# ［C++］`owning_view`によるパイプライン安全性の確保

この記事は[C++ Advent Calendar 2021](https://qiita.com/advent-calendar/2021/cxx)の21日目の記事です。

### ExecutorとNetworking TS

#### Executor

Executorライブラリは、非同期並行処理の制御のための基盤となる機能を提供しようとするものです。

標準インターフェースを介して様々なハードウェアリソースへアクセスする方法と非同期処理のグラフを表現する方法を提供し、処理がいつどこで行われるのかをプログラマが制御可能とするためのライブラリです。

- [P2300R2 `std::execution`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2300r2.html)
- [［翻訳］P0443R13 A Unified Executors Proposal for C++ - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/05/24/205222)

#### Networking TS

Networking TSは、標準ライブラリに基礎的なソケット通信の機能を追加しようとするものです。

Networking TSはBoost.Asioをベースとして設計されており、一部変更されている部分はあるもののBoost.Asioほぼそのままの形で利用することができるようになっています。

Networking TS（Boost.Asio）は、非同期I/O操作のために非同期処理のサポート機構、すなわちExecutorに相当するものを内包しています。そのため、ExecutorライブラリはNetworking TSの一部であり、ベースとなるものとされます。

現在のC++標準化委員会では、Executorを導入してからNetworking TSをそれをベースとするように修正し導入する、といった感じで作業が進められています（した）。

- [N4771 Working Draft, C++ Extensions for Networking](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/n4771.pdf)
- [ネットワーク - TCP - boostjp](https://boostjp.github.io/tips/network/tcp.html)

### Executorの道程

#### AsioにおけるExecutorの発見

AsioにおけるExecutorは開発の早い段階で見出され、2006年ごろには`asio_handler_dispatch()`（後に`asio_handler_invoke()`）と言う名前のADLカスタマイズポイントとして実装されました。

```cpp
namespace mine {
  template <typename Handler>
  class counting_handler {
    void operator()(...) {
      // invoke handler
    }

    Handler handler_;
  };

  // counting_handlerに対するカスタマイズasio_handler_invoke
  template <typename Function>
  void asio_handler_invoke(Function function, counting_handler* context) {
    // increment counter
    // invoke function
  }
}


int main() {
  // ...

  mine::counting_handler handler(&handle_read);

  // 非同期Read
  boost::asio::async_read(socket, buffer, handler);
}
```

- [When to use `asio_handler_invoke`? - stackoverflow](https://stackoverflow.com/questions/32857101/when-to-use-asio-handler-invoke)

Asioの実装内で、`asio_handler_invoke`は利用されます。

```cpp
namespace boost::asio {

  // デフォルトのasio_handler_invoke()
  template <class Function>
  void asio_handler_invoke(Function& function, ...) {
    function(); // デフォルトは現在のスレッド
  }
  
  // async_readの実装とする
  auto async_read(const Socket& socket, Buffer& buffer, Handler handler) {
    // I/O操作・・・

    // ADLによるasio_handler_invokeを介したhandlerの呼び出し
    using asio_handler_invoke;
    asio_handler_invoke(handler, ...);
  }
}
```

（細部を端折っている雑な例であることをお許しください）  
これによって、Asioの提供する非同期操作に与える完了ハンドラによって、そのハンドラが呼び出される場所（実行コンテキスト）とその方法を制御することが可能となります。これは例えば、非同期処理の完了ハンドラでさらに非同期処理をネストさせて呼び出すときに全てのハンドラを1つのスレッドで実行させたい場合などに使用できます。

これはC++11にムーブセマンティクスが導入された際にムーブオンリーなハンドラに対応できない問題が発覚し（この詳細はよくわかんないです・・・）、それに対処するために`associated_executor`に変更され、その際にカスタマイズポイント自体（`associated_executor`）から実行コンテキストの表現（上記例の`context`）が分離されました（これはどうやら、Networking TSに移植する際に変更されたようです）。

- [Networking TS の Boost.Asio からの変更点 - その 4: Associated Executor - あめだまふぁくとりー](https://amedama1x1.hatenablog.com/entry/2017/12/09/102405)

```cpp
namespace boost::asio {

  // 完了ハンドラからexecutorを取得するためのtraitsクラス
  template<class T, class Executor = system_executor>
  struct associated_executor {
    using type = T::executor_type;
    // T::executor_typeがなければ
    using type = Executor;

    static type get(const T& t, const Executor& e = Executor()) noexcept {
      return t.get_executor();
      // T::executor_typeがなければ
      return e;
    }
  };

  // async_readの実装とする
  auto async_read(const Socket& socket, Buffer& buffer, Handler&& handler) {
    // I/O操作・・・

    // 完了ハンドラに関連づけられたexecutorを取得する
    auto ex = associated_executor<Handler>::get(handler);
    // exの場所でexによって指定された方法で完了ハンドラを実行
    dispatch(ex, std::forward<Handler>(handler), ...);
  }
}
```

ここで出てくる`ex`こそが今日Executorと呼ばれているものです。`associated_executor`は非同期操作の完了ハンドラ型に対して部分特殊化しておくことでカスタムすることができ、その`::get()`から得られるExecutorによって完了ハンドラが実行される場所を指定します。何もカスタムしなければ、デフォルトの`system_executor`が使用され、デフォルトは現在のスレッド（`ex.dispatch()`の呼び出された場所）でそのまま実行されます。

#### WG21 SG1におけるUnified Executorの追求

Asioでの動きを受けてかそれとは別かはわかりませんが、2012〜2015にかけていくつかの異なるExecutorの提案がSG1（Study Group1 : Concurrency Study Group）に提出されました。

これを受けてSG1では、これらのニーズとユースケースを満たしつつそれぞれの提案の問題点を解決するような統一的なExecutorモデルを模索され、2016年10月に最初のUnified Executorである[P0443R0 A Unified Executors Proposal for C++](https://wg21.link/P0443R0)が提案されました。

P0443R0はかなりNetworking TSのExecutorの影響が見られるものでしたが、その後議論を経て洗練されていきコンセプトとCPOベースの非常にジェネリックなライブラリとして進化していきました。

- [［翻訳］P0443R13 A Unified Executors Proposal for C++ - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/05/24/205222)

2019年7月のSG1の全体投票においてP0443の設計をExecutorライブラリとして承認し、C++20標準への導入を目指してLEWGでのレビューに移行しました。

C++標準化において、ライブラリ提案は各SG->LEWG->LWGの3段階のレビュープロセスを踏みます。また、各SGでは方向性やコンセプトの決定と最初の設計を行い、LEWGでは設計を集中的にレビューし、LWGでは標準に提案する文書についてのレビューを行います。

なかなか巨大なこともあってC++20には間に合わず、その後COVID-19パンデミックが直撃したこともありレビューは遅れ、2020年夏頃からLEWGのリソースを全力投入する形で、P0443をいくつかの部分に分割して個別のグループによってレビューされました。提案が巨大で歴史のあるものであったこともありレビューは困難を極めたようで、Executorの設計とその歴史についてLEWGのメンバに周知を図る必要性が提起されました。とはいえレビューは為され、[そこそこの数の問題が報告](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2219r0.pdf)されました。

その後2020年12月のLEWGのレビューで、P0443からいくつかの部分が別の提案に分離されることが決定された他はほぼ設計が固まったように見え、一部の人から実装経験について心配する声が上がっていましたが、C++23に向けて作業されていました。

#### P2300

### P0443

### Networking TS


### P2300 vs Networking TS

### 参考文献

- [A Unified Executors Proposal for C++ | P0443R14](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r14.html)
- [P2033R0 - History of Executor Properties](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2033r0.pdf)
- [P2300R2 `std::execution`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2300r2.html)
- [P2444R0 The Asio asynchronous model](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2444r0.pdf)
- [P2470R0 Slides for presentation of P2300R2: `std::execution` (`sender/receiver`)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2470r0.pdf)
- [P2463R0 Slides for P2444r0 The Asio asynchronous model](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2463r0.pdf)
- [P2464R0 Ruminations on networking and executors](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2464r0.html)
- [P2469R0 Response to P2464: The Networking TS is baked, P2300 Sender/Receiver is not.](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2469r0.pdf)
- [P2479R0 Slides for P2464](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2479r0.pdf)
- [P2471R1 NetTS, ASIO and Sender Library Design Comparison](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2471r1.pdf)
- [P2480R0 Response to P2471: "NetTS, Asio, and Sender library design comparison" - corrected and expanded](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2480r0.pdf)
- [P0443 A Unified Executors Proposal for C++ - cplusplus/papers](https://github.com/cplusplus/papers/issues/102)
- [P2300 `std::execution` - cplusplus/papers](https://github.com/cplusplus/papers/issues/1054)
- [Networking TS の Boost.Asio からの変更点 - その 3: Executor - あめだまふぁくとりー](https://amedama1x1.hatenablog.com/entry/2016/08/20/222326)
- [Networking TS の Boost.Asio からの変更点 - その 4: Associated Executor - あめだまふぁくとりー](https://amedama1x1.hatenablog.com/entry/2017/12/09/102405)