# ［C++］契約プログラミング機能の違反ハンドラ

Contracts提案がC++26に向けて採択され、C++26では契約プログラミング機能を言語サポートの下で実践できるようになります。契約プログラミング機能の一部として導入されている違反ハンドラというものについてのお話です。

[:contents]

### 契約プログラミング機能における違反ハンドラの概要

C++26の契約プログラミング機能は、関数の事前条件と事後条件（と中間の条件）を契約注釈（契約アサーション）として記述できるようにするとともに、それを実行時にチェックできるようにするものです。実行時チェックについては契約注釈の評価のセマンティクスによってその動作が規定されており、4種類のセマンティクスが定義されています。

4つのセマンティクス（ignore, observe, enforce, quick_enforce）のうち、observeとenforceセマンティクスでは契約が破られた（条件式が`false`に評価された）時に、違反ハンドラと呼ばれる言語組み込みのコールバック関数が呼ばれます。

違反ハンドラは契約違反が起きた場合の処理を担うもので、実装によってデフォルトのハンドラが用意されており、通常契約違反時にはそれが呼び出されます。デフォルトの違反ハンドラの動作については実装定義ですが、契約違反に関する診断メッセージを出力することが推奨されてはいます。

```cpp
// 違反ハンドラのシグネチャ（グローバル名前空間で定義）
void handle_contract_violation(const std::contracts::contract_violation&) noexcept(/*実装定義*/);
```

なお、違反ハンドラの呼び出しはシグナルハンドラのようなものでも、異なるスレッドで処理されるようなものでもなく、通常の制御フローに従った呼出しになります。あるスレッドで契約注釈が評価されて違反ハンドラが呼ばれた場合、そのスレッドの実行は違反ハンドラ内に移り、observeセマンティクスの場合は違反ハンドラが正常にリターンすると違反が起きた契約注釈の直後から元のプログラムの処理が再開されます。

契約注釈の評価と違反ハンドラ呼出しは通常のC++を用いた疑似コードで記述することができます

```cpp
// セマンティクスの取得
evaluation_semantic _semantic = __current_semantic();

if (evaluation_semantic::ignore == _semantic) {
  // ignoreセマンティクスの場合
  // なにもしない
} else if (evaluation_semantic::observe == _semantic
        || evaluation_semantic::enforce == _semantic
        || evaluation_semantic::quick_enforce == _semantic)
{
  // 契約チェックを行うセマンティクスの場合

  if consteval {
    // 定数式における契約チェック
    // See Section 3.5.12.
  } else {
    // exposition−only variables for control flow
    bool _violation;
    // Violation handler should be invoked.
    bool _handled = false; // Violation handler has been invoked.

    // Check the predicate and invoke the violation handler if needed.
    try {
      // 契約条件の評価
      _violation = __check_predicate(X);
    } catch (...) {
      // 契約条件式の評価が例外を送出した場合
      if (evaluation_semantic::quick_enforce == _semantic) {
        // quick_enforceセマンティクスの終了処理
        std::terminate(); // implementation−defined program termination
      } else {
        // Handle the violation within the exception handler.
        _violation = true;

        // 契約違反ハンドラの呼び出し
        __handle_contract_violation(_semantic, detection_mode::evaluation_exception);

        _handled = true;
      }
    }

    if (_violation && evaluation_semantic::quick_enforce == _semantic) {
      // quick_enforceセマンティクスの終了処理
      __builtin_trap(); // implementation−defined program termination
    }
    if (_violation && !_handled) {
      // 契約違反ハンドラの呼び出し
      __handle_contract_violation(_semantic, detection_mode::predicate_false);
    }
    if (_violation && evaluation_semantic::enforce == _semantic) {
      // enforceセマンティクスの終了処理
      abort(); // implementation−defined program termination
    }
  }
} else {
  // 実装定義のセマンティクスの処理
}
```

実際に契約注釈毎にこのようなコードが挿入されるわけではありませんが、契約注釈の評価に伴って何が起こるかはこのような疑似コードから理解することができます。

この疑似コードからも分かりますが、契約注釈の評価中に例外が送出された場合も違反ハンドラが呼び出されます。このケースは引数の`contract_violation`オブジェクトを通して得られる情報から判別可能です。

#### ユーザー定義違反ハンドラ

デフォルトの、と言っていることからわかるように、この違反ハンドラはユーザーが置き換えてカスタマイズすることを想定されています（ただしそのサポートは実装定義とされてはいますが）。違反ハンドラの置き換えのメカニズムはグローバルの`operatro new/operator delete`と同様であり、上記のシグネチャに合致するように関数を定義することでユーザーが違反ハンドラを定義できます。

そのようなユーザー定義違反ハンドラ内ではほぼ自由な処理を実行することができます。一応ユースケースとしては、診断メッセージのカスタマイズ、診断メッセージの出力先の変更、Graceful Shutdownを可能にする、enforceセマンティクスにおいて例外を投げることでプログラム終了を回避する、無限ループに陥るようにしておくことで失敗した特定スレッドの実行を停止する、などが想定されています。

#### `std::contracts::contract_violation`

違反ハンドラ引数の`std::contracts::contract_violation`型は契約違反に関する情報を持つ型で、次のようなインターフェースを持っています

```cpp
namespace std::contracts {

  class contract_violation {
    // ユーザーがアクセス可能なコンストラクタや代入演算子はない
    // コピーもムーブもできない
  public:

    // 違反を起こした契約注釈のテキスト表現を取得する
    const char* comment() const noexcept;

    // 違反ハンドラの呼び出された理由を取得する
    contracts::detection_mode detection_mode() const noexcept;

    // 契約注釈の評価中に例外が送出されている場合、その例外オブジェクトを取得する
    exception_ptr evaluation_exception() const noexcept;

    // 現在の評価セマンティクスがプログラムの終了を伴うかどうかを取得する
    // trueの場合、違反ハンドラが正常にリターンするとプログラムは終了する
    bool is_terminating() const noexcept;

    // 契約違反を起こした契約注釈の種別（`pre, post, contract_assertion`）
    assertion_kind kind() const noexcept;

    // 契約違反を起こした契約注釈のソースコード上の場所を取得する
    source_location location() const noexcept;

    // 契約違反を起こした契約注釈の評価セマンティクスを取得する
    evaluation_semantic semantic() const noexcept;
  };
}
```

`.kind()`、`.semantic()`、`.detection_mode()`の戻り値は列挙型の値であり、次のように定義されます

```cpp
namespace std::contracts {

  // 契約注釈の種別
  enum class assertion_kind : unspecified {
    pre = 1,
    post = 2,
    assert = 3,

    // 実装定義の値、もしくは将来の拡張で追加されうる
    // 実装定義の値の最小値は1000である必要がある
  };

  // 契約注釈の評価セマンティクス種別
  enum class evaluation_semantic : unspecified {
    ignore = 1,
    observe = 2,
    enforce = 3,
    quick_enforce = 4,

    // 実装定義の値、もしくは将来の拡張で追加されうる
    // 実装定義の値の最小値は1000である必要がある
  };
  
  // 違反ハンドラの呼出し理由
  enum class detection_mode : unspecified {
    predicate_false = 1,        // 契約違反
    evaluation_exception = 2,   // 条件式評価中の例外送出

    // 実装定義の値、もしくは将来の拡張で追加されうる
    // 実装定義の値の最小値は1000である必要がある
  };
}
```

これらのものは`<contracts>`ヘッダに配置されていますが、単に契約注釈を記述するだけならこのヘッダをインクルードする必要はありません。

#### より一般的な利用

この契約違反ハンドラは契約違反のハンドリングをより柔軟に行いつつ、セマンティクスの動作の一部を担う（以前にあったビルドモードの役割を置き換える）ことを目的としており、現在の仕様は契約違反のハンドリングで使用するために必要な最小限なものになっています。

しかし、Contractsの議論の中ではこの違反ハンドラがより広く一般的に使用できる可能性があることが認識されており、それを考慮して細部のインターフェースは調整されています。この記事の残りの部分ではその想定されるユースケースを紹介します。

### 外部ツールの共通コールバック機構として

違反ハンドラは契約違反が起きた場合、すなわちプログラム中で何らかの想定外の状態が検出された場合のコールバック処理を担うものです。そのようなプログラム実行時の想定外の状態とは必ずしも契約チェックでのみ検出されるわけではなく、それを検出する外部のツールが現在すでに存在しています。

そのような外部のツールが検出したエラー状態をプログラムに通知するための方法として、違反ハンドラが活用できる可能性があります。

そのようなツールの具体的なものとして頻繁に挙げられているのは、サニタイザーです。アドレスサニタイザーをはじめとする各種サニタイザーはプログラムと同居する形で内部的にエラー状態を検出し、通常エラーが検出されるとプログラムの実行は中断されます。

契約違反時と同様に、そのようなエラーが起きた場合に行いたいことはプログラムの要求によって異なるため、一部のサニタイザー実装ではコールバックを登録してそれをハンドルできるようにしたり、終了の方法をカスタマイズしたりできるようになっています。すなわち、サニタイザーにおけるエラー状態の検出後にどうするかということに関しては、契約違反が起きた場合とほとんど同じ問題であり、共通したソリューションを取ることができます。

また、サニタイザーにおけるコールバックの共通したAPIセットのようなものやその在り方についてのコンセンサスは現在存在しておらず、違反ハンドラを利用することでより中立的かつ一般的にその共通機構となることができます。

このような需要はP2900の比較的早い段階で認識されており、C++26 Contractsの違反ハンドラはサニタイザーにおける利用を考慮して設計されています。ただし、C++26時点ではこれの実現可能性やサニタイザーのコールバックの仕様不全などからそれを完全にサポートする形にはなっていません。

### 実行時エラーハンドリングのコールバック機能として（P3290R2）

実行時のエラー状態の検出は契約チェックでも外部ツールでもなく、ユーザーコードによって行われるのが現在より一般的です。それはCアサートをはじめとするアサーションであったり、`if`による明示的なものであったりします。しかしここでもやはり、検出した後にどうすべきか？という問題があります。

アサーション（マクロ）に関しては契約プログラミングにも共通する考え方のもとで現在も広く使用されており、特にCアサートがC++26 Contractsとはほぼ非互換であることはContractsの議論の過程で問題になりました。

P2900の最終仕様の違反ハンドラはユーザーが自由に呼べるものにはなっていませんが（特に`contract_violation`オブジェクトを構築する方法が無い）、P3290(R2)で既存アサーション機構をC++ Contractsに接続するための拡張提案が議論されています。

P3290では違反ハンドラをユーザーが任意のタイミングで呼び出せるようにするAPIと、契約セマンティクスがサポートするプログラム終了方法をユーザーが実行できるようにするAPIを提案しています。この拡張がなされた場合、ユーザーが記述するエラー検出コードにおいて検出されたエラーのハンドリングのために違反ハンドラを利用できるようになります。

```cpp
void f(int* ptr) {
  if (ptr == nullptr) {
    // enforceセマンティクスに基づく違反ハンドラの呼出し
    std::contracts::handle_enforced_contract_violation("ptr == nullptr", std::source_location::current());
  }
}
```

違反ハンドラは言語機能であり、ライブラリや実装とは独立した仕様を持っており、プログラム中のどこから呼ばれたとしても同じハンドラが呼び出され、エラーハンドリングを一元的に担うことができます。違反ハンドラのユーザー呼出しのサポートによって、Contractsの持つ利点の一部をユーザーでも利用できるようになります。

### プロファイル機能の実行時検査におけるコールバックとして（P3081R0）

プロファイル機能は、現在C++29に向けて検討中のC++コードの安全性を高めるために、プロファイルによって指定される特定の保証（型安全やリソース安全性など）をオプトインで要求するためのシステムです。プロファイルによる保証はコンパイル時の制限と実行時チェックによって提供されます。

この実行時チェックによって危険性が検出された場合にどうするのかについてはあまり具体的に指定されてはいないのですが、これもやはり違反ハンドラのモチベーションと共通するものがあるため、Contractsの違反ハンドラのメカニズムを使用することが検討されています。

### 未定義動作の実行時ハンドリング機能として（P3100R0）

ここまでのユースケース例において、何らかのエラー状態を検出した時の共通ハンドリング機構としてのContracts違反ハンドラの側面が見えていますが、そのエラー状態のとして契約違反だけではなく未定義動作及びエラー性動作（erroneous behavior）を含めて、C++ Contractsのフレームワークによってよって統一的にそのハンドリングを行おうとする構想があります。

そのアイデアは、実行時に未定義動作もしくはエラー性動作に陥る可能性のある操作（言語機能）が暗黙的に契約注釈を持つように扱うことで、UB/EBをC++ Contractsのフレームワークの内部に捉えてしまおうとするものです。そして、この実行時コールバックのために違反ハンドラが使用されます。

これはP3100R0で提案されているもので、解説は以前の記事を参照してください

- [P3100R0 Undefined and erroneous behaviour are contract violations - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P3100R0-Undefined-and-erroneous-behaviour-are-contract-violations)

これがどうなるかはまだまだ分かりませんが、これらの例に見えるように、契約プログラミング機能における違反ハンドラはさらなる発展の可能性を秘めている陰の主役ともいえる機能です。

### 参考文献

- [P2900R14 Contracts for C++](https://open-std.org/jtc1/sc22/wg21/docs/papers/2025/p2900r14.pdf)
- [P3073R0 Remove evaluation_undefined_behavior and will_continue from the Contracts MVP](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3073r0.pdf)
- [P3081R0 Core safety Profiles: Specification, adoptability, and impact](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3081r0.pdf)
- [P3100R0 Undefined and erroneous behaviour are contract violations](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3100r0.pdf)
- [P3205R0 Throwing from a `noexcept` function should be a contract violation.](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3205r0.pdf)
- [P3229R1 Making erroneous behaviour compatible with Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p3229r1.pdf)
- [P3290R2 Integrating Existing Assertions With Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3290r2.pdf)
- [P3227R0 Contracts for C++: Fixing the contract violation handling API](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3227r0.pdf)
- [P3386R0 Static Analysis of Contracts with P2900](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3386r0.pdf)
