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

// 処理を引数なしで呼び出し可能として定義する
invocable auto work = []{ cout << "My work" << endl; };

// 定義した処理workをexecuteカスタマイゼーションポイントを介して実行する
execute(ex, work);
```

`execute()`それ自体は基本的な*fire-and-forget*スタイルのインターフェースで、引数なしで呼び出し可能な1つの呼び出し可能オブジェクトを受け入れ、作成した作業を識別・操作するための戻り値を返さない。このようにして、普遍性と利便性をトレードオフにしている。結果として、ほとんどのプログラマはより便利な高レベルのライブラリを介して*executor*を利用することになるだろう。我々が想定している非同期STLはそのようなライブラリの一例である。

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

`executor`コンセプトは指定された実行コンテキストで単一の操作を実行するという基本的なニーズに対応しているが、`executor`コンセプトの表現力は限られている。`execute`はスケジュールされた処理へのハンドルを返すのではなく`void`を返し、*executor*抽象は操作をチェーンしてその結果の値やエラー、キャンセルシグナルを下流の処理に伝播させる一般的な方法を提供しない。また、処理の投入から実行までの間に発生しうるスケジューリングエラーを処理する方法がなく、一連の操作に関連する状態オブジェクトのアロケーションとライフタイムを制御する便利な方法も提供されていない。


そのような制御方法を提供しないままでは、（Stepanovの意味で）一般的な非同期アルゴリズムの効率的で機能的なデフォルト実装を定義することはできない。このギャップを埋めるために、本稿では関連する2つの抽象*sender*と*receiver*を提案する。具体的な動機を以下に述べる。

#### 1.4.1 Generic async algorithm example: `retry`

`retry`は*sender*と*receiver*が可能にする汎用アルゴリズムの一種であり、それはとても単純な意味論を持つ。実行コンテキストで処理をスケジュールし、恙なく成功した場合とユーザーがキャンセルした場合にその処理は完了したとみなし、それ以外、例えばスケジューリングエラーが発生した場合などには処理の実行を再試行する。

```cpp
template<invocable Fn>
void retry(executor_of<Fn> auto ex, Fn fn) {
  // ???
}
```

*executor*だけではスケジューリングエラーをキャッチして対処するポータブルな方法がないため、このようなアルゴリズムの一般的な実装を妨げている。後程、*sender*と*receiver*によってこれがどのように実装されるのかを示す。

#### 1.4.2 Goal: an asynchronous STL

`retry`のような汎用非同期アルゴリズムの定義を後押しする適切に選択されたコンセプトは、効率的な非同期処理グラフの作成を簡素化する。ここに、我々の思い描いている非同期プログラムについて少しのサンプルコードを紹介する（[P1897](http://wg21.link/P1897)から借用している）。

```cpp
sender auto s = just(3) |                                  // 即座に`3`を生成
                via(scheduler1) |                          // コンテキストを遷移
                then([](int a){return a+1;}) |             // 継続処理をチェーン
                then([](int a){return a*2;}) |             // さらにもう一つ継続処理をチェーン
                via(scheduler2) |                          // コンテキストを遷移
                handle_error([](auto e){return just(3);}); // エラーハンドル、デフォルト値を返すようにする
int r = sync_wait(s);                                      // 一連の処理の結果を待機
```

`just(3)`は、その戻り値の型が正しくコンセプトを満たしいてる非同期APIの呼び出しに置き換えても、このプログラムの正しさを維持することがことが可能であるべきである。`when_all`や`when_any`のような汎用アルゴリズムによってユーザーは、DAGを用いて並行処理の分岐/結合を表現することが可能になる。STLのイテレータ抽象と同様にコンセプト的な要件を満たすコストは、広く再利用と連携が可能なライブラリのアルゴリズムの表現力によって相殺される。

#### 1.4.3 Current techniques

依存関係のある非同期実行のチェーンを作成するテクニックはいくつも存在している。普通のコールバックはC++でもそれ以外の場所でも長年にわたり成功を収めてきた。現代のコードベースは継続をサポートする`future`抽象のバリエーションに切り替わっている（例えば`std::experimental::future::then`、他の所ではJavascriptのPromiseチェーンなど）。C++20以降はコルーチンがより標準的になり、非同期操作を起動すると`awaitable`オブジェクトが返されるようになることだろう。これらのアプローチにはそれぞれ長所と短所がある。

##### Futures

`future`はこれまで実現されているように、共有状態とその同期のためにメモリの動的確保と管理を必要とし、典型的には処理と継続の型消去も必要とする。これらのコストの多くの部分はすでにスケジューリング済みの実行操作のハンドルとしての`future`の性質に固有のもので、これらの費用は多くの用途で将来の抽象化を排除しており、一般的なメカニズムとしては不適切な選択である。

##### Coroutines

**コルーチンは** 多くの問題を`future`と共有するが、依存関係のある処理をチェーンさせる際に通常はサスペンドを開始するため、同期化を回避できる。多くの場合、コルーチンフレーム（コルーチンに関連するものを格納しておくメモリ領域）は動的確保が不可避である。そのため、組み込み環境やヘテロジニアスな環境では、その詳細に細心の注意を払う必要がある。協調動作しているコルーチンを素早く安全に終了させるためには満足のいかない解決策が必要となるため、コルーチンもまた非同期処理をキャンセル可能な候補とはならない。一方で、例外は非効率的であるため多くの環境で許可されず、また、`co_yield`がステータスコードを返すような扱いにくいアドホックメカニズムは正しさの妨げになっている。これらの事は[P1662](http://wg21.link/P1662)で全容の解説がなされている。

##### Callbacks

コールバックは処理のチェーンを作成するための最も単純で強力かつ効率的なメカニズムであるが、それ自体に問題がある。コールバックは処理結果の値かエラーのどちらかを伝搬する必要があり、このシンプルな要件がいくつものインターフェースの可能性をもたらしている。しかし、それらインターフェースの標準的なものがないことが一般的な設計を妨げている。さらに、それらのインターフェースの可能性の中には、上流の処理を停止してクリーンアップするよう要求した場合にキャンセル信号に対応しているものは殆どない。

### 1.5 Receiver, sender, and scheduler

前述の動機付けのように、結果値、エラー、キャンセル伝播の存在する場合の汎用非同期プログラミングの必要性に対応するためのプリミティブを導入する。

#### 1.5.1 Receiver

*receiver*は特定のインターフェースと意味論を持つコールバックである。関数呼び出し構文と単一のシグネチャで成功とエラーの両方を処理するが、*receiver*には結果値、エラー、完了（あるいはキャンセル）の3つのチャンネルがある。

これらのチャンネルはカスタマイゼーションポイントとして指定され、`receiver_of<R,Ts...>`のモデルとなる型`R`はそれらをサポートする。

```cpp
std::execution::set_value(r, ts...); // 成功を通知するがset_value自体が失敗する可能性はある
std::execution::set_error(r, ep);    // 失敗を通知（epはstd::exception_ptr）、これは失敗しない
std::execution::set_done(r);         // 停止を通知、失敗しない
```

これら3つの関数のうちのどれか一つだけが、*receiver*が破棄される前にその*receiver*によって呼び出されなければならない。これらの各インターフェースは処理の「終端」とみなされる。つまり、特定の*receiver*は3つのうちのどれか1つが呼ばれた場合は残りの2つが呼ばれることはないと仮定することができる。唯一の例外は`set_value`が例外を送出して終了した場合で、その時*receiver*はまだ完了していない。従って、破棄する前に別の関数を呼び出す必要がある。`set_value`の呼び出しが失敗した場合に正確性を保つには、続いて`set_err/set_done`のどちらかの呼び出しが必要である。*receiver*は`set_value`の2回目の呼び出しがwell-formedであることを保証する必要はない。これらの要件を総称して*receiver contract*と呼ぶ。

*receiver*のインターフェースは一見真新しく見えるかもしれないが、単なるコールバックであることに変わりはない。さらに、`std::promise`の`set_value/set_exception`が本質的に同じインターレースを提供していることを考えれば、そのような真新しさは消えるだろう。このようなインターフェースと意味論の選択は、*sender*とともに`retry`のような多くの有用な非同期アルゴリズムの汎用実装を可能にする。

#### 1.5.2 Sender

*sender*は実行のスケジュールがまだされていない処理を表し、継続（*receiver*）を追加してからローンチするか、実行のためにキューに入れる必要がある。接続された*receiver*に対する*sender*の義務は、3つの*receiver*関数のうちのどれか一つが正常に完了することを保証することで、*receiver contract*を履行することである。

この提案の以前のバージョンではこれらの2つの作業（継続のアタッチと実行のためのローンチ）を1つの操作`submit`に集約していた。本稿ではその`submit`を、`connect`ステップ（*sender*と*receiver*を1つの*operation state*にパッケージングする）と`start`ステップ（論理的に操作を開始し、操作が完了したときに呼ばれる*receiver*の完了通知関数のスケジューリング）の2つの操作に分割することを提案する。

```cpp
// P0443R12（以前のバージョン
std::execution::submit(snd, rec);

// P0443R13（このバージョン
auto state = std::execution::connect(snd, rec);
// ... 後からスタート
std::execution::start(state);
```

この分割は最適化のための興味深い機会を提供し、[*sender*とコルーチンを調和させる](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#appendix-a-note-on-coroutines)。

`sender`コンセプトそれ自身は*sender*の処理が実行される実行コンテキストに対して何ら要件を課さない。その代わり、`sender`コンセプトのモデルとなる特定の*sender*は、*receiver*の3つの関数が呼び出されるコンテキストについてより強い保証を提供することができる（`sender`コンセプトの意味論的な要求として要求されうる）。これは特に、*scheduler*によって作成された*sender*に当てはまる。

#### 1.5.3 Scheduler

多くの汎用非同期アルゴリズムは、同じ実行コンテキストに対して複数の実行エージェントを作成する。したがって、既知の実行コンテキストで完了するsingle-shot *sender*を用いてそれらのアルゴリズムをパラメータ化するだけでは不十分である。むしろ、これらのアルゴリズムの方をsingle-shot *sender*のファクトリに渡す方が理にかなっている。そのようなファクトリを*scheduler*と呼び、`schedule`という単一の基本操作を持つ。

```cpp
sender auto s = std::execution::schedule(sched);
// OK、sはschedの示す実行コンテキストで完了する何も返さないsingle-shot sender
```

*executor*と同様に*scheduler*も実行コンテキストへのハンドルとして機能する一方、*executor*と事なり*scheduler*は実行を遅延して実行コンテキストへ送信する。ただし、ある単一の型が`executor`コンセプトと`scheduler`コンセプトの両方のモデルとなる場合がある。`scheduler`コンセプトの包摂（する実装）によって、一定期間が経過するまで実行を延期したり、キャンセルしたりする機能が追加されることを想定している。

### 1.6 Senders, receivers, and generic algorithms

有用なコンセプトは汎用アルゴリズムを制約する一歩で、それらコンセプトの基本操作によるデフォルト実装を許可する。以下に、これら`sender`と`receiver`が一般的な非同期アルゴリズムの効率的な実装を提供する方法を示す。殆どの汎用的な非同期アルゴリズムは、*sender*を受け取りそれによる`connect`の呼び出しが、アルゴリズムのロジックを実装するアダプタをラップした*receiver*を返すように実装されていることを想定している。次の`then`アルゴリズムは、*sender*で継続関数をチェーンする簡単なデモである。

#### 1.6.1 Algorithm `then`

次のコードは`std::experimental::future::then`のように、非同期処理の結果が利用可能な場合にその結果に適用される関数をスケジュールする`then`アルゴリズムを実装したものである。このコードはアルゴリズムがどのようにして*receiver*にアダプトし、アルゴリズムのロジックをコード化できるかを示している。

```cpp
template<receiver R, class F>
struct _then_receiver : R { // 説明のために、Rからset_errorとset_doneを継承する
  F f_;

  // 呼び出し可能オブジェクトf_を呼び出し、その結果を基底クラスに渡すことでset_valueをカスタマイズする
  template<class... As>
    requires receiver_of<R, invoke_result_t<F, As...>>
  void set_value(Args&&... args) && noexcept(/*...*/) {
      ::set_value((R&&) *this, invoke((F&&) f_, (As&&) as...));
  }

  // f_の戻り値型がvoidの場合の対応など、省略
};

template<sender S, class F>
struct _then_sender : _sender_base {
  S s_; // sender
  F f_; // callble

  template<receiver R>
    requires sender_to<S, _then_receiver<R, F>>
  state_t<S, _then_receiver<R, F>> connect(R r) && {
      return ::connect((S&&)s_, _then_receiver<R, F>{(R&&)r, (F&&)f_});
  }
};

template<sender S, class F>
sender auto then(S s, F f) {
  return _then_sender{{}, (S&&)s, (F&&)f};
}
```

非同期*sender*を返すAPI、`async_foo`が与えられた場合、`then`のユーザーはその非同期処理の結果が利用可能になったときに任意のコードを実行することができる。

```cpp
sender auto s = then(async_foo(args...), [](auto result) {/* stuff... */});
```

これによって合成された非同期操作が構築される。ユーザーがこの操作の実行をスケジュールしたい場合、*receiver*を`connect`し得られる*operation state*オブジェクトを用いて`start`を呼び出す。

`then`を使用して実行コンテキストでの処理の実行スケジュールを設定することもできる。`scheduler`コンセプトを満たす`static_thread_pool`のオブジェクト`pool`が与えられれば、ユーザーは次のようにすることができる。

```cpp
sender auto s = then(
    std::execution::schedule( pool ),
    []{ std::printf("hello world"); } );
```

これにより、実行されるとスレッドプール内のスレッドから`printf`を呼び出す*sender*を作成できる。

任意のコードを実行することができないようなヘテロジニアスコンピューティング環境が存在しており、その場合上記の様な`then`の実装は機能しないか（その環境にとって）未知のコードを実行するためにホストへの遷移コストが発生する。従って、`then`自体とそのほかのいくつかの基本的なアルゴリズムプリミティブは実行コンテキスト毎にカスタマイズ可能である必要がある。

`then`の動作例：https://godbolt.org/z/dafqM-

#### 1.6.2 Algorithm `retry`

前述したように、`retry`のアイデアは非同期操作の失敗時に再試行し、成功やキャンセル時は再試行をしない。`retry`の正しい汎用実装の鍵はエラーが起きた場合とキャンセルされた場合を区別できることにある。`then`アルゴリズムと同様に、`retry`アルゴリズムはアルゴリズムのロジックを`retry`される*sender*が`connect`されているカスタム*receiver*に配置する。このカスタム*receiver*にはシグナルを変更せずに渡すだけの`set_value/set_done`メンバ関数が定義されている。一方、`set_error`メンバ関数は元の*sender*とカスタム*receiver*の新しいオブジェクトを用いて再度`connect`することで、その場で*operation state*を再構築する。そして、その新しい*operation state*が再び`start`され、実質的に元の*sender*が再実行される。

[付録](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#appendix-the-retry-algorithm)に`retry`アルゴリズムのソースコードが掲載されている。`retry`アルゴリズムのシグネチャは単純だ

```cpp
sender auto retry(sender auto s);
```

操作を再実行する実行コンテキストはパラメータ化されていない。これは、指定された実行コンテキストで*sender*を実行するようにスケジュールする関数の存在を仮定できるためである。

```cpp
sender auto on(sender auto s, scheduler auto sched);

retry(on(s, sched));  // schedの実行コンテキストで再実行してもらう
```

これら2つの関数があれば、ユーザーは`retry(on(s, sched))`とすることで指定した実行コンテキストで処理を再実行することができる。

#### 1.6.3 Toward an asynchronous STL

"then"と"retry"の2つは、*sender*と*receiver*によって表現可能な多くの汎用非同期アルゴリズムのたった2つにすぎない。他の重要なアルゴリズムには`on`と`via`の2つがある。前者は指定した*scheduler*で実行されるように*sender*をスケジュールし、後者は指定した*scheduler*上で*sender*に`connect`されている継続を実行させる。このようにして、ある実行コンテキストから別の実行コンテキストへ遷移する非同期処理のチェーンを作成することができる。

そのほかの重要なアルゴリズムには、fork/joinセマンティクスをカプセル化する`when_all/when_any`がある。これらのアルゴリズムやその他の仕組みを使用すれば、非同期処理全体のDAGを作成し実行できる。`when_any`は汎用タイムアウトアルゴリズムを実装するために使用でき、一定時間スリープしてから「完了」シグナルを通知する*sender*実装とともに使用することでそのようなアルゴリズムを構成することができる。要するに、*sender/receiver*は汎用非同期アルゴリズムの豊富なセットをSTLにある既存のStepanovによるシーケンスアルゴリズムと同時に使用することができる。*sender*を返す非同期APIはこれらの汎用アルゴリズムで使用でき、再利用性が向上する。[P1897](http://wg21.link/P1897)ではそれらのアルゴリズムの初期セットが提案されている。

### Summary

我々は、C++プログラマがエレガントな標準インターフェースを介して多様なハードウェアリソース上での非同期並行処理を表現できる未来を想像している。この提案は柔軟な実行基盤を提供し、その目標の実現に向けた最初の一歩である。*executor*は処理を実行するハードウェアをリソースを表現する。*sender*と*receiver*は遅延構築された非同期処理のDAGを表現する。これらのプリミティブは、処理がいつどこで行われるのかをプログラマが制御できるようにする。

## 2 Proposed Wording

あまりに長いので各ヘッダのsynopsisだけコピペして後は省略。

- [2 Proposed Wording](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#proposed-wording)

#### 2.1.2 Header <execution> synopsis

```cpp
namespace std {
namespace execution {

  // Exception types:

  extern runtime_error const invocation-error; // exposition only
  struct receiver_invocation_error : runtime_error, nested_exception {
    receiver_invocation_error() noexcept
      : runtime_error(invocation-error), nested_exception() {}
  };

  // Invocable archetype

  using invocable_archetype = unspecified;

  // Customization points:

  inline namespace unspecified{
    inline constexpr unspecified set_value = unspecified;

    inline constexpr unspecified set_done = unspecified;

    inline constexpr unspecified set_error = unspecified;

    inline constexpr unspecified execute = unspecified;

    inline constexpr unspecified connect = unspecified;

    inline constexpr unspecified start = unspecified;

    inline constexpr unspecified submit = unspecified;

    inline constexpr unspecified schedule = unspecified;

    inline constexpr unspecified bulk_execute = unspecified;
  }

  template<class S, class R>
    using connect_result_t = invoke_result_t<decltype(connect), S, R>;

  template<class, class> struct as-receiver; // exposition only

  template<class, class> struct as-invocable; // exposition only

  // Concepts:

  template<class T, class E = exception_ptr>
    concept receiver = see-below;

  template<class T, class... An>
    concept receiver_of = see-below;

  template<class R, class... An>
    inline constexpr bool is_nothrow_receiver_of_v =
      receiver_of<R, An...> &&
      is_nothrow_invocable_v<decltype(set_value), R, An...>;

  template<class O>
    concept operation_state = see-below;

  template<class S>
    concept sender = see-below;

  template<class S>
    concept typed_sender = see-below;

  template<class S, class R>
    concept sender_to = see-below;

  template<class S>
    concept scheduler = see-below;

  template<class E>
    concept executor = see-below;

  template<class E, class F>
    concept executor_of = see-below;

  // Sender and receiver utilities type
  namespace unspecified { struct sender_base {}; }
  using unspecified::sender_base;

  template<class S> struct sender_traits;

  // Associated execution context property:

  struct context_t;

  constexpr context_t context;

  // Blocking properties:

  struct blocking_t;

  constexpr blocking_t blocking;

  // Properties to allow adaptation of blocking and directionality:

  struct blocking_adaptation_t;

  constexpr blocking_adaptation_t blocking_adaptation;

  // Properties to indicate if submitted tasks represent continuations:

  struct relationship_t;

  constexpr relationship_t relationship;

  // Properties to indicate likely task submission in the future:

  struct outstanding_work_t;

  constexpr outstanding_work_t outstanding_work;

  // Properties for bulk execution guarantees:

  struct bulk_guarantee_t;

  constexpr bulk_guarantee_t bulk_guarantee;

  // Properties for mapping of execution on to threads:

  struct mapping_t;

  constexpr mapping_t mapping;

  // Memory allocation properties:

  template <typename ProtoAllocator>
  struct allocator_t;

  constexpr allocator_t<void> allocator;

  // Executor type traits:

  template<class Executor> struct executor_shape;
  template<class Executor> struct executor_index;

  template<class Executor> using executor_shape_t = typename executor_shape<Executor>::type;
  template<class Executor> using executor_index_t = typename executor_index<Executor>::type;

  // Polymorphic executor support:

  class bad_executor;

  template <class... SupportableProperties> class any_executor;

  template<class Property> struct prefer_only;

} // namespace execution
} // namespace std
```

#### 2.5.1 Header `<thread_pool>` synopsis

```cpp
namespace std {

  class static_thread_pool;

} // namespace std
```

### 2.6 Changelog

まあいいよね・・・

- [2.6 Changelog](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#changelog)

### 2.7 Appendix: Executors Bibilography

余力があったらそのうち・・・

- [2.7 Appendix: Executors Bibilography](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#appendix-executors-bibilography)

### 2.8 Appendix: A note on coroutines

余力があったらいつか・・・

- [2.8 Appendix: A note on coroutines](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#appendix-a-note-on-coroutines)

### 2.9 Appendix: The retry Algorithm

余力があったらきっと・・・

- [2.9 Appendix: The retry Algorithm](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p0443r13.html#appendix-the-retry-algorithm)
