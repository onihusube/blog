# ［C++］`owning_view`によるパイプライン安全性の確保

この記事は[C++ Advent Calendar 2021](https://qiita.com/advent-calendar/2021/cxx)の21日目の記事です。

### ExecutorとNetworking TS

#### Executor

Executorライブラリは、非同期並行処理の制御のための基盤となる機能を提供しようとするものです。

標準インターフェースを介して様々なハードウェアリソースへアクセスする方法と非同期処理のグラフを表現する方法を提供し、処理がいつどこで行われるのかをプログラマが制御可能とするためのライブラリです。

- [P2300R2 `std::execution`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2300r2.html)
- [P2470R0 Slides for presentation of P2300R2: `std::execution` (`sender/receiver`)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2470r0.pdf)
- [［翻訳］P0443R13 A Unified Executors Proposal for C++ - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/05/24/205222)

#### Networking TS

Networking TSは、標準ライブラリに基礎的なソケット通信の機能を追加しようとするものです。

Networking TSはBoost.Asioをベースとして設計されており、一部変更されている部分はあるもののBoost.Asioほぼそのままの形で利用することができるようになっています。

Networking TS（Boost.Asio）は、非同期I/O操作のために非同期処理のサポート機構、すなわちExecutorに相当するものを内包しています。そのため、ExecutorライブラリはNetworking TSの一部であり、ベースとなるものとされます。

現在のC++標準化委員会では、Executorを導入してからNetworking TSをそれをベースとするように修正し導入する、といった感じで作業が進められています（した）。

- [N4771 Working Draft, C++ Extensions for Networking](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/n4771.pdf)
- [ネットワーク - TCP - boostjp](https://boostjp.github.io/tips/network/tcp.html)


ExecutorもNetworkingも、C++20策定時点ではC++23に導入される見込みであるとされており、実際設計も固まっていたのでほぼ内定だろうと思われていました・・・

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

1つはgoogleからのもの

```cpp
class executor {
public:
  virtual void add(function<void()> closure) = 0;

  virtual void add_at(time_point abs_time,
                      function<void()> closure) = 0;

  virtual void add_after(duration rel_time,
                         function<void()> closure) = 0;
  ...
};

class thread_pool : public executor { ... };
```

1つはAsioからのもの

```cpp
class my_executor {
public:
  template<class Function, class Allocator>
  void dispatch(Function&& f, const Allocator& alloc);
  
  template<class Function, class Allocator>
  void post(Function&& f, const Allocator& alloc);

  template<class Function, class Allocator>
  void defer(Function&& f, const Allocator& alloc);

  execution_context& context() noexcept;
  
  ...
};
```

1つはNVIDIAからのもの

```cpp
template<class Executor>
struct executor_traits {
  template<class Function>
  static future<auto> async_execute(Executor& ex, Function f);

  template<class Function>
  static future<auto> async_execute(Executor& ex, Function f, shape_type shape);
  
  template<class Function>
  static auto execute(Executor& ex, Function f);
 
  template<class Function>
  static auto execute(Executor& ex, Function f, shape_type shape);
  ...
};
```

AsioはExecutorとExecution Contextが分かれていたり、NVIDIAはおそらくGPUでの実行を意識してバルク実行インターフェースを備えていたりと、それぞれが必要とするユースケースによって提案されたExecutorの設計は微妙に異なっていました。

これを受けてSG1では、これらのニーズとユースケースを満たしつつそれぞれの提案の問題点を解決するような統一的なExecutorモデルが模索され、2016年10月に最初のUnified Executorである[P0443R0 A Unified Executors Proposal for C++](https://wg21.link/P0443R0)が提案されました。

P0443R0はかなりNetworking TSのExecutorの影響が見られるものでしたが、その後議論を経て洗練されていきコンセプトとCPOベースの非常にジェネリックなライブラリとして進化していきました。

- [［翻訳］P0443R13 A Unified Executors Proposal for C++ - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/05/24/205222)

2019年7月のSG1の全体投票においてP0443の設計をExecutorライブラリとして承認し、C++20標準への導入を目指してLEWGでのレビューに移行しました。また、先立つ2019年5月には、SG1の投票において将来的にP0443が標準化された時に、Networking TSをP0443ベースに書き換えることに全会一致で合意が取れていました。

C++標準化において、ライブラリ提案は各SG->LEWG->LWGの3段階のレビュープロセスを踏みます。また、各SGでは方向性やコンセプトの決定と最初の設計を行い、LEWGでは設計を集中的にレビューし、LWGでは標準に提案する文書についてのレビューを主に行います。

なかなか巨大なこともあってC++20には間に合わず、その後COVID-19パンデミックが直撃したこともありレビューは遅れ、2020年夏頃からLEWGのリソースを全力投入する形で、P0443をいくつかの部分に分割して個別のグループによってレビューされました。提案が巨大で歴史のあるものであったこともありレビューは困難を極めたようで、Executorの設計とその歴史についてLEWGのメンバに周知を図る必要性が提起されましたがレビューは為され、[そこそこの数の問題が報告](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2219r0.pdf)されました。

2020年8月ごろには、AsioはP0443のExecutorを実装してリリースされました。これはP0443の実装経験を得るためでもあるようです。

- [Boost 1.74.0リリースノート - boostjp](https://boostjp.github.io/document/version/1_74_0.html#asio)

その後2020年12月のLEWGのレビューで、P0443からいくつかの部分が別の提案に分離されることが決定された他はほぼ設計が固まったように見え、一部の人から実装経験について心配する声が上がっていましたが、C++23に向けて作業されていました。

2021年5月ごろには[P0958R3](https://wg21.link/p0958r3)（Networking TSをP0443ベースに書き換える提案）と[P1322R3](https://wg21.link/p1322r3)（Networking TSの各APIが任意のExecutorを受け取れるようにする提案）がSG4（Networking Study Group）を全会一致で通過し、LEWGに転送されました。この2つの提案はNetworking TSをP0443に対応させるためのものです。

#### P2300 `std::execution`

P0443そのものは半年ほどは目立った（外部から観測できる）動きはなかったのですが、2021年6月、P0443を置き換える新しいExecutorライブラリである[P2300R0 `std::execution`](https://wg21.link/p2300r0)が提案されました。P2300はP0443をベースとしていくつかの問題を解決した上で、分離して提案されていた非同期アルゴリズムライブラリを含むさらに大きなライブラリで、C++における非同期処理に関する大統一モデルの構築を目指しているようです。

R1に改稿されLEWGで議論を重ねていたのですが、2021年7月ごろのレビューでP2300の`sender/reciever`による非同期モデルとNetworking TS(Asio)の非同期モデルが異なっていることが指摘されました。P2300を大統一非同期モデルとして追求していくなら、Networking TSのExecutor部分に対して大きな変更が必要となります。一部の人は、P2300によるそのような大統一モデルの必要性と有効性に疑問を呈すとともに、Networking TSをP2300から分離すべきだと主張し始めたようです。

2021年8月初旬のLEWGレビューにおける方向性を探る投票においては、大統一非同期モデルの必要性についてはコンセンサスが得られなかったものの、C++標準ライブラリのstructured concurrency保証のソリューションとしてP0443の代わりにP2300を追求する方向性には強いコンセンサスが得られました。

2021年8月中旬のLEWGレビューではP2300の第一ピリオドとして次の改稿のためのまとめが行われ、P2300のモデルを説明するための例の充実やコルーチンとの関係性や既存の標準並列アルゴリズムとどう統合されるかなど、主に説明や解説を追記していくことが指示されました。一方で、大統一非同期モデルについては単一のモデルでカバーするには領域が広すぎるという意見や、P2300はstructured concurrencyと並行性という狭いスコープに焦点を当てて標準化し、標準ライブラリの他の部分（Networking TSなど）は別の非同期モデルを選択できるようにした方が良いのではないかという意見があったようです。

この時点で、Executorの議論は完全にP2300に移り、P0443と関連する提案の追求はストップされました。

2021年9月の1回目のLEWGレビューにおいて、7月ごろに指摘されたNetworking TSとの間の問題について、LEWGのメンバに向けて解説が行われたようです（[P2444R0](https://wg21.link/P2444R0)、[P2463R0](https://wg21.link/P2463R0)）。これらの提案・スライドの作成および説明は、Asioの作者自らによって行われています。これを受けて方向性を探る投票が行われ、Networking TSを今のまま（P2300に対応せず）C++23に導入するコンセンサスは得られませんでしたが、P2300をC++23に導入するコンセンサスも得られませんでした。これは方個性を決定する投票ではないためP2300とNetworking TSがこれで終わるわけではありませんが、ExecutorとNetworkingのC++23入りについて暗雲が立ち込めてきました・・・

2021年9月の2回目のLEWGレビューではNetworking TSとP2300をどう進めていくかについて本格的に議論されることになり、Networking TSとP2300を切り離した場合に後からP2300とNetworking TSを相互運用可能なようにラッパーを書くことができるか、あるいは（Asioが必要とする）プロパティ指定方法なしでP2300をC++23に導入した場合に後でそれを追加できるか？などが議論されたようです。  
ここでも方向性を探るための投票が行われ、大統一非同期モデルの必要性についてはコンセンサスが得られず、Networking TSとP2300のC++23入りについても前回同様の結果となりました。

2021年10月公開の提案文書では、このP2300とNetworkingTSの問題に関連する提案（報告書）がいくつも提出されました。

- [P2464R0 Ruminations on networking and executors](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2464r0.html)
    - Networking TSをP0443ベースで標準化すべきではない
    - P2300の開発に専念し、完成後にそれにフィットするネットワークライブラリを標準化したほうがいい
- [P2469R0 Response to P2464: The Networking TS is baked, P2300 Sender/Receiver is not.](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2469r0.pdf)
    - ↑に反論する文書
    - P2300は非同期モデルを提案するものではなく非同期DSLを提案するものにすぎない
    - ASIOは実装経験に裏打ちされた非同期モデルをもっており、P2300の実質スーパーセットである
- [P2479R0 Slides for P2464](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2479r0.pdf)
    - P2464を紹介するスライドだが、↑に対する批判を含む
    - P2469はP2300が提供する共通化されたAPIとモデルによる非同期処理の構成を可能とするAPIを持たない
- [P2471R1 NetTS, ASIO and Sender Library Design Comparison](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2471r1.pdf)
    - Networking TSとAsioとP2300を比較するもの
- [P2480R0 Response to P2471: "NetTS, Asio, and Sender library design comparison" - corrected and expanded](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2480r0.pdf)
    - ↑に対して間違いを指摘する提案

これを受けて、10月のLEWGレビューでもP2464とP2469について議論されたようです。両方の支持者は、互いが互いの上に構築できる（P2300の上にNetworking TSを構築できるし、Networking TSの上にP2300を構築できる）と主張していて、議論の主題はエラー処理に関することでした。Networking TSのExecutorモデル（およびP0443の`exeecutor`）はエラー通知に関するチャネルを持たず、特に処理が実行コンテキストに投入されてから実行されるまでの間に起きるエラーをハンドルする方法を提供しないことが懸念されたようです。もう一つの論点はパフォーマンスに関することで、P2300のモデルでは`sender/reciever`オブジェクトの構築に伴う受け入れがたいオーバーヘッドが発生すると考えている人が多いようです。

これらの問題についてP2300/Networking TSをどう進めていくかを判断するために、LEWGおよびSG1のメンバで次の項目について投票を行いました

1. Networking TS/Asioの非同期モデルは、ネットワーキング・並列処理・GPUなどのほとんどの非同期ユースケースの優れた基盤である
      - 弱い否決
2. P2300の非同期モデルは、ネットワーキング・並列処理・GPUなどのほとんどの非同期ユースケースの優れた基盤である
      - コンセンサス
3. C++の標準ネットワークライブラリとして、Networking TSを追求するのをやめる
      - 否決
4. C++標準ネットワークライブラリは、P2300をベースとすべき
      - 弱いコンセンサス
5. C++標準ネットワークライブラリを、TLS/DTLSサポートなしで出荷することを容認する
      - 否決

2番目の投票は反対9に対して賛成40と大差がついています。3番目の投票は反対16に対して賛成26でしたが、賛成票を投じた人の多くはNetworking TSを白紙に戻したいのではなく、P2300の上に構築したいという意図のようです。

これによって、LEWG/SG1およびSG4の方向性は

1. Networking TS/Asioの非同期モデルをベースとしてP2300を構築しない
2. Networking TS/Asioの非同期モデルはネットワーキングのためのモデルとして追及したほうがいい（するなら
3. LEWGはC++23に向けてP2300の作業を続行する
4. Networking TSは死んでいない
5. Networking TSを標準に導入するためには、非同期モデルとセキュリティについての作業が必要となる
      - この作業は重く、C++23に間に合う可能性は低い
6. Networking TSがP2300ではない非同期モデルを採用するなら、説得力のある提案が必要となる

一応はこれで決着を見たはずです、火種は残ってる気がしますが・・・

この結果に従って、12月まではP2300がLEWGにて引き続きレビューされていますがLWGに進めてはいません。今のところ、Networking TS絡みで大きな問題はないようです。

#### C++23 Feature Complete

まだ2023年までは時間がありますが、あらかじめ決められているスケジュール（[P1000R4](https://isocpp.org/files/papers/P1000R4.pdf)）として、C++23に導入する機能の設計は2022年2月7日までに完了していることが求められています。

LEWGの予定表（[P2489R0](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2489r0.html)）によれば、P2300のLEWGにおけるレビューの機会はあと一回（2022年1月11日）で、LWGへ進めるための投票の機会もあと一度（2022年1月14日～）です。

前述のように、Networking TSは実質的に作業がストップしており、非同期モデルとセキュリティという2つの重い課題を抱えているので、C++23には間に合わないでしょう。Executorが間に合うかは来年2週目のLEWGのテレコンレビューで設計を完了できるかで決まります。

### Executor?

#### P0443

#### P2300

#### Networking TS


### P2300 vs Networking TS

### 参考文献

- [A Unified Executors Proposal for C++ | P0443R14](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r14.html)
- [P2033R0 - History of Executor Properties](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2033r0.pdf)
- [P2300R2 `std::execution`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2300r2.html)
- [P2430R0 Slides: Partial success scenarios with P2300](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2430r0.pdf)
- [P2431R0 Presentation: Plans for P2300 Revision 2](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2431r0.pdf)
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
- [P1322 Networking TS enhancement to enable custom I/O executors - cplusplus/papers](https://github.com/cplusplus/papers/issues/361)
- [P0958 Networking TS changes to support proposed Executors TS - cplusplus/papers](https://github.com/cplusplus/papers/issues/339)
- [Networking TS の Boost.Asio からの変更点 - その 3: Executor - あめだまふぁくとりー](https://amedama1x1.hatenablog.com/entry/2016/08/20/222326)
- [Networking TS の Boost.Asio からの変更点 - その 4: Associated Executor - あめだまふぁくとりー](https://amedama1x1.hatenablog.com/entry/2017/12/09/102405)