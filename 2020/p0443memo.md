# P0443R13 A Unified Executors Proposal for C++ メモ

- [A Unified Executors Proposal for C++ | P0443R13](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html  )

## 1 Design Document

### 1.1 Motivation

C++プログラムの未来を想像する時我々は、小さなスマートフォンから大きなスーパーコンピュータまで多様なハードウェアによってアクセラレートされエレガントにネットワーク化された非同期並列処理を思い描く。今、ハードウェアの多様性はかつてないほどに増しているが、C++プログラマには彼らが満足する並行プログラミングのためのツールがない。産業用の強力な並行処理プリミティブのようなものは強力だが危険であり、よく知られる問題に苦しめられている。また、C++標準のアルゴリズムライブラリは並列化対応されているが柔軟性に欠け、その他の並行処理機能（`std::thread, std::atomic. std::async, std::future`など）と組み合わせたり連携することができない。

これらの現在抱える課題に対処し思い描いた未来を築くためには、C++にプログラムの実行を制御するための基礎機能を整備しなければならない。まず、C++はある処理がいつどこで実行されるのかを制御するための柔軟な機能を提供する必要がある。本稿では、それらの機能の設計を提案する。SG1は[多くの議論と協力](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#appendix-executors-bibilography)の果てに2019年ケルン会議でこの設計を全員の合意の下で採択した。

### 1.2 Usage Example

この提案では実行のための2つの主要なコンポーネント（処理実行インターフェースと処理の表現）と、それらの間の相互関係についての要件を定義する。それぞれ、*executors*、*senders*、*receivers*と呼ばれる。

```cpp
// この提案のAPIはstd::execution名前空間の下に定義される
using namespace std::execution;

// 任意の場所（たとえばスレッドプール）で処理を実行するexecutorを取得する
std::static_thread_pool pool(16);
executor auto ex = pool.executor(); // この記法はコンセプトによる変数の制約

// 高レベルのライブラリによる処理がどこで実行されるかを記述するためにexecutorを使用する
perform_business_logic(ex);

// あるいは、この提案によるよりプリミティブなAPIを直接使用することもできる

// スレッドプールに処理を投げ、すぐ実行する
execute(ex, []{ std::cout << "Hello world from the thread pool!"; });

// スレッドプールに処理を投げすぐ実行し、完了まで現在のスレッドをブロックする
execute(std::require(ex, blocking.always), foo);

// 依存性のある一連の処理を記述し、後で実行する
sender auto begin    = schedule(ex);
sender auto hi_again = then(begin, []{ std::cout << "Hi again! Have an int."; return 13; });
sender auto work     = then(hi_again, [](int arg) { return arg + 42; });

// 処理の最終結果を標準出力へ出力する
receiver auto print_result = as_receiver([](int arg) { std::cout << "Received " << std::endl; });

// 先ほど定義したworkによる処理をreceiverと組み合わせてスレッドプールで実行する
submit(work, print_result);
```

### 1.3 Executors Execute Work

軽量なハンドルとして、*executor*に実行コンテキストへの統一されたアクセスを課する。

*executor*は処理が物理的に実行されるハードウェアを抽象化することで、処理を作成するための統一的なインターフェースを提供する。先ほどのサンプルコードでの実行リソースはスレッドプールだった。そのほかには、SIMDユニットやGPU、単純な現在のスレッド、などが含まれる。そのような実行リソース一般を指して **実行コンテキスト（*execution context*）** と呼ぶ。

そのような実行リソースへの軽量なハンドルとして、*executor*には実行コンテキストへの統一されたアクセスを課する。統一性があることで、ライブラリインターフェースの背後で間接的に実行される場合でも（そこに*executor*を受け渡すことで）、処理が実行される場所を制御することができる。

基本的な*executor*インターフェースは、利用者が処理を実行するための`execute`関数である。

```cpp
// 何かしらのexecutorを取得する
executor auto ex = ...

// 処理を引き数なしで呼び出し可能として定義する
invocable auto work = []{ cout << "My work" << endl; };

// 定義した処理workをexecuteカスタマイゼーションポイントを介して実行する
execute(ex, work);
```

`execute()`それ自体は基本的な*fire-and-forget*スタイルのインターフェースで、引き数なしで呼び出し可能な1つの呼び出し可能オブジェクトを受け入れ、作成した作業を識別・操作するための戻り値を返さない。このようにして、普遍性と利便性をトレードオフにしている。結果として、ほとんどのプログラマはより便利な高レベルのライブラリを介して*executor*を利用することになるだろう。我々が想定している非同期STLはそのようなライブラリの一例である。

`std::async`を*executor*と相互運用可能なように拡張し、ユーザーが実行を制御できるようにする方法を考えてみる。

```cpp
template<class Executor, class F, class Args...>
future<invoke_result_t<F,Args...>> async(const Executor& ex, F&& f, Args&&... args) {
  // 処理とその引数をパッケージングする
  packaged_task work(forward<F>(f), forward<Args>(args)...);

  // futureオブジェクトを取得
  auto result = work.get_future();

  // 与えられたexecutorで処理を実行
  execution::execute(ex, move(work));

  return result;
}
```

このように拡張することの利点は、ユーザーが複数のスレッドプールの中から１つを選択して、対応する*executor*を`std::async`に与えるだけでどのプールを使用するかを正確にコントロールでき、処理のパッケージングや処理のプールへの送出などの不便な部分はライブラリの仕事になる点にある。

#### Authoring executors

プログラマは`execute()`関数とともに型を定義することで、カスタム*executor*を定義することができる。

ユーザーの処理をその内部で実行する`execute()`関数を持つ*executor*実装を考えてみる。

```cpp
struct inline_executor {
  // define execute
  template<class F>
  void execute(F&& f) const noexcept {
    std::invoke(std::forward<F>(f));
  }

  // enable comparisons
  auto operator<=>(const inline_executor&) const = default;
};
```

`<=>`による比較は、2つの*executor*が同じ実行リソースを参照しており、同じ意味論の下で処理が実行されるかを判断するものである。`executor/executor_of`コンセプトはこれらを要約したもので、前者は個別の*executor*を検証し、後者は*executor*と処理の両方が利用可能な場合に検証する。

#### Executor customization

*executor*をカスタマイズし、実行をアクセラレートしたり新しい振舞を追加することができる。先ほどのサンプルコードは新しい*executor*型を定義するものだったが、より細かい/粗い粒度でのカスタマイズも可能である。それぞれ **エグゼキュータープロパティ（*executor propertie*）**、**制御構造（*control structure*）** と呼ばれる。

#### Executor properties

*executor propertie*は`execute()`の最小の契約を超えてオプショナルな動作要件を実装に伝達する。本提案でもいくつかを規定する。エキスパートな実装者によってより高いレベルの抽象下の下でこれらの要件が課されることを想定している。 

原則として、オプションの動的データメンバや関数引数はこれらの要件を伝達することができるが、C++にはコンパイル時にカスタマイズする機能が必要である。また、そのようなオプションのパラメータは[組み合わせることによって多くの関数の変種を生み出してしまう](https://wg21.link/P2033)。

代わりに、statically-actionableなプロパティはそれらの要件を考慮し、エグゼキューターAPIの組み合わせ爆発を抑止する。例えば、ブロッキングを伴う処理の優先度付き実行のための要件を考えてみる。スケーラブルではない設計では、それぞれの要件を個別の関数に乗算することでオプションを`execute()`のインターフェースに埋め込むことができるかもしれない（`execute, blocking_execute, execute_with_priority, blocking_execute_with_priority, ...etc`）。

本稿における*executor*では、`require/prefer`に基づく[P1393](https://wg21.link/P1393)のプロパティ設計を採用することによってこのような組み合わせ爆発を回避する。

```cpp
// 何かしらのexecutorを取得する
executor auto ex = ...;

// 実行にはブロッキング操作が必要という要求（require
executor auto blocking_ex = std::require(ex, execution::blocking.always);

// 特定の優先度pで実行することが好ましい（prefer
executor auto blocking_ex_with_priority = std::prefer(blocking_ex, execution::priority(p));

// ブロッキングしながら実行、可能ならば指定の優先度で実行
execution::execute(blocking_ex_with_priority, work);
```

それぞれの`require/prefer`は*executor*を要求されたプロパティを持つものに変換する。この例では、もしブロッキングエグゼキューターに変換できない場合は`require`の呼び出しはコンパイルエラーとなる。`prefer`はヒントを伝達するための弱い要求であり、その要求は無視される可能性があるため、コンパイルは常に成功する。

呼び出し元を決してブロックしないバージョンの`std::async`を考えてみる。

```cpp
template<executor E, class F, class... Args>
auto really_async(const E& ex, F&& f, Args&&... args) {
  using namespace execution;

  // 処理とその引数をパッケージングする
  packaged_task work(forward<F>(f), forward<Args>(args)...);

  // futureオブジェクトを取得
  auto result = work.get_future();

  // 指定されたexecutorでブロッキング無しで処理を実行
  execute(require(ex, blocking.never), move(work));

  return result;
}
```

このような拡張によって、よく知られた`std::async`の危険性に対処できる。

```cpp
// 戻り値のfutureは破棄されたためasyncの呼び出しはブロックする
std::async(foo);

// こちらは決してブロックしない
// futureがデストラクタで処理の完了を待機するのはstd::asyncが返したもののみであるため
really_async(foo);
```

#### Control structures

*control structure*は*executor*がそれらをフックできるようにすることでより高い抽象化レベルでのカスタマイズを可能にし、特定の実行コンテキストにおいてより効率的な実装が可能な場合に有用である。本提案が最初に定義する*control structure*は単一の操作で関数呼び出しのグループを作成する`bulk_execute`である。このパターンは広範囲の効率的な実装を可能にし、C++と標準ライブラリにとって極めて重要なものである。

デフォルトの`bulk_execute`は繰り返し`execute`を呼び出すだけであるが、個々の処理を繰り返し実行するのはスケールせず効率が悪い。そのため、多くのプラットフォームはそのようなバルク処理を明示的かつ効率的に実行するAPIを備えている。そのような場合、カスタムの`bulk_execute`はそれらの高速化されたバルクAPIに直接アクセスすることで非効率的なプラットフォームとのやりとりを回避しスカラーAPIの使用を最適化することができる。

`bulk_execute`は呼び出し可能オブジェクトと呼び出し回数を受け取る。可能な実装を考えてみる。

```cpp
struct simd_executor : inline_executor { // 初めに、executor要件を満足するために、inline_executorを継承する

  template<class F>
  simd_sender bulk_execute(F f, size_t n) const {
    #pragma simd
    for(size_t i = 0; i != n; ++i) {
      std::invoke(f, i);
    }

    return {};
  }
};
```

`bulk_execute`を高速化するために、`simd_executor`はSIMDループを使用する。

`bulk_execute`は一度に複数の処理が必要な場合に使用する。

```cpp
template<class Executor, class F, class Range>
void my_for_each(const Executor& ex, F f, Range rng) {
  // バルク実行を要求し、senerを取得する
  sender auto s = execution::bulk_execute(ex, [=](size_t i) {
    f(rng[i]);
  }, std::ranges::size(rng));

  // 実行を開始し処理の完了を待機
  execution::sync_wait(s);
}
```

先程の例の`simd_executor`による`bulk_execute`実装は熱心（即座）に実行されるが、`bulk_execute`の意味論はそれを要求しない。上記`my_for_each`が示すように、`execute`とは異なり`bulk_execute`はオプションで実行を延期可能な遅延操作の一例である。`bulk_execute`が返すトークン（上記コード中の`s`）はユーザーが処理を開始したり、実行対象の処理と対話するための使用することができる*sender*の一例である。例えば、*sender*を渡して`sync_wait()`を呼び出せば、呼び出し元の処理が継続される前にバルク処理が完了する事を保証する。*sender*と*receiver*は次のセクションの主題である。

### 1.4 Senders and Receivers Represent Work

