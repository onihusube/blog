# ［C++］Deprecating volatile を見つめて

※この記事は[C++20を相談しながら調べる会 #3](https://cpp20survey.connpass.com/event/147002/)の成果として書かれました。

C++20より、一部の`volatile`の用法が非推奨化されます。提案文書は「[Deprecating volatile](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1152r4.html)」という壮大なタイトルなのでvolatileそのものが無くなるのかと思ってしまいますがそうではありません。  
この提案文書をもとに何が何故無くなるのかを調べてみます・・・

[:contents]

### そもそもvolatileってなんだろう・・・

長くなったので別記事に分離しました。以下でお読みください。


[https://onihusube.hatenablog.com/entry/2019/10/09/184906:embed:cite]


C++における`volatile`の意味とは

- `volatile`指定されたメモリ領域はプログラム外部で利用されうるという事をコンパイラに通知
    - 特に、そのような領域は外部から書き換えられうる
- そして、実装は必ずしもそれを検知・観測できない
- `volatile`領域への1回のアクセスは正確に1回だけ行われる必要がある
    - 0回にも2回以上にもなってはならない

そして、`volatile`の効果は

- シングルスレッド実行上において
- `volatile`オブジェクトへのアクセス（読み/書き）の順序を保証し
- `volatile`オブジェクトへのアクセスに関してはコンパイラの最適化対象外となる

となります。

そして、マルチスレッドにおいての同期用に使用すると未定義動作の世界に突入します。マルチスレッド時のための仕組みにはなっていません。

### volatileの正しい用法

- 共有メモリ（not スレッド間）
    - 共有相手はGPU等の外部デバイスや別プロセス、OSカーネルなど
    - 特に、time-of-check time-of-use (ToCToU)を回避する正しい方法の一つ
- シグナルハンドラ
    - シグナルハンドラ内で行えることは多くなく、共有メモリにシグナルが発生したことを書きこみ速やかに処理を終えることくらい
    - そのような共有メモリに`volatile static`変数を利用できる
- `setjmp`/`longjmp`
    - `setjmp`の2回の呼び出しの間で（つまり、`longjmp`によって戻ってきた後でも）、変数が変更されないようにするのに使用する
- プログラム外部で変更されうるメモリ領域
    - メモリマップドI/Oにおける外部I/Oデバイスのレジスタなど
    - コンパイラはこのようなメモリ領域がプログラム内でしか使われていない事を仮定できない
- 無限ループにおいて副作用を示す
    - 無限ループが削除されてしまわないように`volatile`オブジェクトを使用する
    - これは`std::atomic`や標準ライブラリのI/O操作によっても代替可能
- `volatile`の効果を得るためのポインタキャスト
    - `volatile`なのはデータではなくコードである、という哲学の下で一般に利用されている
    - `volatile`へのキャストが有効なのはポインタ間のみであり、オブジェクト間で非`volatile`から`volatile`付の型にキャストしても`volatile`の効果は得られない
- [*Control dependencies*](https://en.wikipedia.org/wiki/Dependence_analysis#Control_dependencies)を保護する
    - コンパイラの最適化によってこのような依存関係が削除されないようにする
- `memory_order_consume`のいくつかの実装の保護
    - コンパイラの最適化によってデータ依存の順序が崩されないようにする？

この様な正しい用途の中には、`volatile`の代替となる方法がインラインアセンブリを使う（コンパイラへの指示 or 機械語命令の直接出力）しか無いものがあります。  
そのような方法には移植性がありません・・・

なおここには含まれていない正しい用例があるかもしれませんが、そこにマルチスレッド間共有メモリが入ることは決してありません。

### この提案（P1152R4）の目的

この提案の目的は、C++標準内で間違っている`volatile`の利用を正すことにあります。  
`volatile`が意味がないから非推奨とか、マルチスレッド利用について混乱の下だから非推奨とか言う事ではありません。

そのため、`volatile`の正しい用法のための文言には一切手を付けていません。たとえそこにいくつかの問題がある事が分かっていても、この提案ではその修正さえもしていません。

また、そのような間違った`volatile`の用法はC++20に対してはとりあえず非推奨としていますが、将来的にそれらを削除することを目指しています。

### C++20から非推奨となるコア言語の`volatile`

ここから、この提案によって非推奨とされる`volatile`の用法を見て行きましょう。その際重要な事は、`volatile`メモリへのアクセスは読み込みと書き込み、およびその順序に意味があるという事です。

#### 複合代入演算子、インクリメント演算子

復号代入演算子とは`+= -= *= /=`のような演算子の事です。

インクリメント演算子（`++ --`）と合わせて、これらの演算子は「読み出し - 更新 - 書き込み」という3つの操作を1文で行います。  
すなわち、復号代入演算子の左辺オペランドが`volatile`だった場合に、そのメモリ領域には少なくとも2回のアクセスが発生します。

```cpp
volatile int a = 0;
int b = 10;

a += b;
//これは以下と等価
//int tmp = a; 
//a = tmp + b;

++a;
//int tmp = a;
//a = tmp + 1;

a--;
//int tmp = a;
//a = tmp - 1;
```

実際にはこの様な展開はアセンブラコードとしてのものであり、`tmp`はレジスタ上のどこかです。

ですが、復号代入演算子及びインクリメント演算子はこの場合の`a`に一回しかアクセス（最後の書き込みのみ）しかしないと思われがちです。また、このような一連の操作がアトミックに行われるとも勘違いされがちです。  
`std::atomic`でさえも、このような操作には「読み出し - 更新 - 書き込み」という3つの操作が必要です。

`volatile`に対するこのような複合操作は明示的に「読み出し - 更新 - 書き込み」を分けて書くか、`volatile`なatomic操作を利用すべきです。

従って、`volatile`オブジェクトに対するこれらの演算子はバグの元であり、その使用は適切ではないため、非推奨とされます。  
ただし、非推奨となるのは算術型・ポインタ型に対する組み込みの演算子のみです。

##### 連鎖した代入演算子

類似の問題として`a = b = c`のように連なった代入演算子の用法があります。

```cpp
volatile int a, b, c;

a = b = c = 10;
//これは
//c = 10;
//b = 10;
//a = 10;
//それとも
//c = 10;
//b = c;
//a = b;
//もしくは
//c = 10;
//b = c;
//a = c;
//どうなの！？
```

実際は2番目の形になる様子ですが、この場合の`b c`にどのような順番で何回の読み書きが発生するのかが不明瞭です。  
そのため、この場合の`b, c`が`volatile`である場合に限ってこの様な代入演算子の使用は非推奨となります。

```cpp
volatile int a, b, c;

a = b = c = 10; //ng

int e;

a = e = 10;     //ok

a = e = c = 10; //ng

c = 10;
a = c;          //ok

a = e = c;      //ok
```
代入演算子が2つ以上連なる場合に、両端にある変数を除いて`volatile`修飾された変数が現れてはいけません。ただし、これは非クラス型の場合のみ非推奨です。

#### 関数引数の`volatile`、戻り値型の`volatile`

関数の引数がポインタや参照ではないのに`volatile`修飾されている場合、`const`修飾でも同様ですが関数の内部では明確な意味を持ちます。

しかし、呼び出し側から見ると引数型のトップレベルのCV修飾の有無は無視され、呼び出し規約もC++コード上では無視されるため、その意味は非`volatile`引数をとる関数と全く同様になります。 
また、わずかとはいえ関数実装詳細が漏洩してしまいます。

```cpp
//以下関数は全て同じ関数と見なされ、オーバーロード出来ない
void f(volatile int n);
void __fastcall f(const int n);
void __stdcall f(int n);

volatile int g(volatile int n);

int n = 10;
int r = g(n);  //非volatileな変数をコピーして渡し、volatileな戻り値を非volatileな変数にコピーして受ける
```

仮に引数を`volatile`として扱いたい場合、非`volatile`引数を`volatile`なローカル変数にコピーする方が良いでしょう。処理系によっては、この場合のコピーは省略されます。

同様に、ポインタや参照でない`volatile`な戻り値型には意味がありません。GCCやclangでは効果が無いとして警告を出します。

これらの事は`volatile`の正しい効果を考えると自明です。この様に、引数及び戻り値型に対する`volatile`修飾は無意味であるので非推奨とされます。  
これはトップレベルの`volatile`修飾がある場合のみ非推奨とされます。従って、`volatile`修飾されたポインタや参照型の引数・戻り値は以前使用可能です。

```cpp
void f1(volatile int);  //ng
void f2(volatile int*); //ok
void f3(int volatile*); //ok、f2と同じ引数型
void f4(int* volatile); //ng
void f5(volatile int&); //ok
void f6(int volatile&); //ok、f5と同じ引数型

volatile int  g1(); //ng
volatile int* g2(); //ok
int volatile* g3(); //ok、g2と同じ戻り値型
int* volatile g4(); //ng
volatile int& g5(); //ok
int volatile& g6(); //ok、g5と同じ戻り値型
```

また、この提案では、`const`修飾も同様であるとしてまとめて非推奨とする提案を行っていましたが、それは承認されなかったようです。


#### 構造化束縛宣言の`volatile`

構造化束縛宣言にもCV修飾を指定できますが、実際の所そのCV修飾は構造化束縛宣言に指定した変数名に直接作用しているわけではありません。  
構造化束縛宣言の右辺にある式の暗黙の結果オブジェクトに対してCV修飾がなされます。

構造化束縛宣言の動作の詳細については以下をお読みください。
[https://onihusube.hatenablog.com/entry/2019/10/04/122001:embed:cite]

その結果オブジェクトが`std::tuple`の場合、`std::get`を用いて要素の参照が行われるため、そこでエラーになります（`std::get()`は`volatile std::tuple<...>`を受け取るオーバーロードを持たないため）。これは`std::pair`でも同様です。  
ただ、配列や構造体の場合は意図通りになります。

```cpp
auto f() -> std::tuple<int, int, double>;

volatile auto [a, b, c] = f();   //コンパイルエラー！！
//ここでは以下の様な事が行われている
//volatile auto tmp = f();
//std::tuple_element_t<0, decltype(tmp)>& a = std::get<0>(tmp);

int array[3]{};

volatile auto [a, b, c] = array; //ok
//ここでは以下の様な事が行われている
//volatile int tmp[] = {array[0], array[1], array[2]};
//volatile int a = tmp[0];

static_assert(std::is_volatile_v<decltype(a)>); //ok
```

この様な非一貫的な挙動及び、前項の関数の戻り値型の`volatile`と同様の無意味さがあることから、構造化束縛宣言に対する`volatile`修飾は非推奨とされます。  
もし構造化束縛に`volatile`修飾したい場合は、分解元の型の要素・メンバに対して`volatile`修飾しておくべきであり、`volatile`の用途としてはおそらくそれが適切でしょう（構造化束縛の名前自体は変数名ではないので・・・）。

```cpp
auto f() -> std::tuple<int, int, double>;

volatile auto [a, b, c] = f();  //ng

auto g() -> std::tuple<volatile int,volatile int,volatile double>;
auto [a, b, c] = g();  //ok

static_assert(std::is_volatile_v<decltype(a)>); //ok
static_assert(std::is_volatile_v<decltype(b)>); //ok
static_assert(std::is_volatile_v<decltype(c)>); //ok
```

### C++20より非推奨となる標準ライブラリ内の`volatile`

当初の提案は標準ライブラリ内にある`volatile`に関する所も非推奨とする提案を含んでいましたが、のちにそれは別の提案（[P1831R0 Deprecating volatile: library](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1831r0.html)）として分離されました。  
まだ採択されていませんが、合意は取れているようなのでC++20に入ることは確実でしょう。その場合、DR（Defect Report : 欠陥報告）としてC++20に追加される可能性があります。

#### 標準ライブラリ内テンプレートの`volatile`なオーバーロード

標準ライブラリ内で提供されているクラステンプレートには`volatile`用にオーバーロード（部分特殊化）が明示的に提供されているものがあります。

- `numeric_limits`
- `tuple_size`
- `tuple_element`
- `variant_size`
- `variant_alternative`
- `std::atomic`関連

このうち`numeric_limits`は有用性があるという事でそのままとのことです。また、`std::atomic`関連は次の項で説明します。

`tuple`と`variant`はその実装がどうなっているのか規定されておらず、その実装にどのように`volatile`アクセスするのかが不明瞭です。  
また、標準ライブラリのその他のクラステンプレートは特に`volatile`修飾を意識して書かれておらず、一貫していません。

従って、`std::atomic`関連と`numeric_limits`を除くこれらのクラステンプレートの`volatile`に対する部分特殊化は非推奨とされます。

#### `std::atomic`の`volatile`メンバ関数

`volatile`オブジェクトの操作はアトミックではなく、その順序も変更される可能性がります（非`volatile`オブジェクトとの間の相対順序やCPUのアウトオブオーダー実行時）。しかし、そのようなアクセスは確実に実行され、`volatile`な領域の各バイトに対して正確に1度だけアクセスし、コンパイラによる最適化の対象とはなりません。

`std::atomic`オブジェクトへの操作は分割されることは無く、完全なメモリモデルを持ち、それらは最適化の対象となります。

`volatile std::atomic`はこれらを合わせた性質を持つことが期待されますが、現在の実装はそうなってはいません。

提案文書によれば、ロックフリーではないアトミック操作（の実装）は`volatile`オブジェクトに対して行われたときに、その原子性が失われることがある（アクセス順序や回数の変更ができないことから？）。とされています。

さらに、複合代入のような「読み出し - 更新 - 書き込み」操作の実装は特に指定されておらず、実装としては、再試行ループ、ロック命令、トランザクショナルメモリ、メモリコントローラの操作等の実装方法がありますが、`volatile`領域に正確に1度だけアクセスするという事を達成できるのはメモリコントローラの操作という実装だけです。  
`volatile`の効果を適切に再現するためにはこうした実装を指定する必要がありますが、この様なハードウェアでの実装を指定することはC++標準の範囲から逸脱しています。

このように、現状の`volatile`と`std::atomic`の同時利用は必ずしも両方の特性を合わせたものにはなっておらず、場合によってはどちらかの性質が失われていることがあります。

この様な理由から、`std::atomic`の全てのメンバ関数の`volatile`修飾版及び、フリー関数の`std::atomic_init`の`volatile`オーバーロードが、`std::atomic<T>::is_always_lock_free == false`となる特殊化に対してのみ非推奨とされます。


### 検討されていた他の候補

#### メンバ関数のvolatile修飾

`volatile`修飾メンバ関数は特殊な場合を除いて通常使用されません。これはSTLのクラスが`const`メンバ関数を用意していても`volatile`メンバ関数を用意していない事からも伺うことができます。  
それに対応しようとすると、あるメンバ関数を定義するのにその記述量が倍になってしまう（CV無し+C有+V有+CV有）割にその恩恵が不明瞭で使用頻度も低い為だと思われます。

クラスは`const`でもそうでなくても利用でき、その`const`修飾の有無でメンバ関数の挙動を変えることができます。この有用性は誰もが認めることだと思われます。しかし`volatile`はどうでしょうか？

クラスが`volatile`修飾されているとき、そのオブジェクトは外部から変更されうる領域に置かれていることになります。しかし果たして、そのようなクラスが`volatile`としてもそうでない場合も使えるように設計される必要は本当にあるのでしょうか？そしてその場合、`volatile`修飾されたメンバ関数とそうでない関数の違いとは一体何でしょうか・・・・

また、あるオブジェクトに対する`const`修飾の効果が表れるのは、そのオブジェクトの最派生コンストラクタの呼び出しが完了したときであり、コンストラクタ内ではそのメンバに対するアクセスでも`const`性はありません（これはデストラクタも同様）。  
これは`volatile`でも同様ですが、`volatile`の場合はその領域は外部から変更されうる場所であり、その領域へのアクセス順序や回数には意味があるはずです。その時、`volatile`性なしでオブジェクトの構築・破棄を行う事は適切ではありません。

このように、`volatile`修飾メンバ関数は実質的に無意味であるため、非推奨とする事が提案されていました。

ただし、上記の事を踏まえても、集成体（*aggregate*）は`volatile`で適切に使用されている可能性があります。その場合`volatile`修飾メンバ関数が非推奨となると、そのような集成体の全てのメンバを再帰的に`volatile`修飾して回ることになってしまいます。  
そのため、この文書では3つのアプローチを提案していました。

1. 全てのメンバ関数が`volatile`修飾相当である、又は全くそうではない、という事を規定する
2. 例えば`struct volatile`のように、`volatile`で使用される集成体の宣言を追加する
3. 集成体では`volatile`を禁止する（PODクラスとフリー関数を使用するようにする）

いずれの場合でも、メンバ変数の`volatile`修飾を禁止しません。  
提案文書の著者は3番目の方法を押している雰囲気でした。

他にも共用体やビットフィールドの扱いなど考慮すべきところはあったようですが、結局これはC++20では見送られました。  
`std::atomic`の`volatile`メンバ関数の意味合いについて検討する必要があったためのようです。ただ、`volatile`メンバ関数の非推奨については合意を得られていたようなので将来的には非推奨とされる可能性があります。

### `volatile_load<T>` / `volatile_store<T>`

正確に言えばこの提案には含まれていませんでしたが、この提案から派生した提案として、`volatile`な値の読み書きを行う特別な関数の提案が出されています。

```cpp
namespace std {
  template<typename T>
  constexpr T volatile_load(const T* p);

  template<typename T>
  constexpr void volatile_store(T* p, T v);
}
```

この`std::volatile_load<T>`と`std::volatile_store<T>`は引数として渡されたメモリ領域から値を読み込み、また書き込みます。  
そこでは引数が`volatile`かどうかに関わらず、`volatile`セマンティクスが適用されます。すなわち、1回のアクセスは正確に1回だけ`p`の指すメモリ領域へアクセスし、この関数は最適化対象外となりその順序の入れ替えも行われません。  
また、単なる`volatile`オブジェクトへのアクセス以上の保証を与えているようです（可能な限りアクセスを分割しない等）。

これは、`volatile`なのはデータ（変数）ではなくコードであるという考え方を体現したものといえ、Linuxカーネルで使用される`READ_ONCE()/WRITE_ONCE()`マクロや、D言語の`peek()/poke()`、Rustの`std::ptr::read_volatile()/std::ptr::write_volatile()`と同様のアプローチです。

ここまで見てきた（そしてこの後紹介する）ような、`volatile`修飾の間違った用例を見ると、このアプローチの方が正しいのでは？という気もしてきます・・・

合意は取れているようなので将来的にC++に入ることは間違い無いと思われますが、C++20に入るかは不透明です。

### 不適切と思われる`volatile`の用例

最後に、提案文書にある不適切な`volatile`の使用例を~~コピペ~~紹介しておきます。上記の事の理解の一助になるかと思われます。

```cpp
struct foo {
  int a : 4;
  int b : 2;
};
volatile foo f;

//どんな命令が生成されるでしょう？また、領域に何回アクセスするでしょう？？
f.a = 3;
```

```cpp
struct foo {
  volatile int a : 4;
  int b : 2;
};
foo f;

f.b = 1; // aの領域へアクセスする？
```

```cpp
union foo {
  char c;
  int i;
};
volatile foo f;

//これはsizeof(int) [byte]の領域へアクセスする？それとも、sizeof(char) [byte]だけ？？
f.c = 42;
```

```cpp
volatile int i;

//それぞれ何回領域アクセスが発生するでしょう？
i += 42;
++i;
```

```cpp
volatile int i, j, k;

//iへの代入時にjの値を再読み込みしますか？
i = j = k;
```

```cpp
struct big { int arr[32]; };
volatile _Atomic struct big ba;
struct big b2;

//この操作はatomicに行われる？
ba = b2;
```

```cpp
int what(volatile std::atomic<int> *atom) {
    int expected = 42;

    //ここでは*atomの領域に何回のアクセスが起こるでしょう？
    atom->compare_exchange_strong(expected, 0xdead);
    
    return expected;
}
```

```cpp
void what_does_the_caller_care(volatile int);
```

```cpp
volatile int nonsense(void);
```

```cpp
struct retme { int i, j; };
volatile struct retme silly(void);
```

```cpp
struct device {
  unsigned reg;
  device() : reg(0xc0ffee) {}
  ~device() { reg = 0xdeadbeef; }
};
volatile device dev; //初期化（コンストラクタ内）、破棄（デストラクタ内）はともにvolatileではない
```

### 参考文献
- [P1152R0 : Deprecating volatile](https://wg21.link/p1152r0)
- [P1152R1 : Deprecating volatile](https://wg21.link/p1152r1)
- [P1152R2 : Deprecating volatile](https://wg21.link/p1152r2)
- [P1152R4 : Deprecating volatile](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1152r4.html)
- [P1831R0 : Deprecating volatile: library](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1831r0.html)
- [P1382R0 : volatile_load<T> and volatile_store<T>](https://wg21.link/p1382r0)
- [Time of check to time of use - Wikipedia](https://ja.wikipedia.org/wiki/Time_of_check_to_time_of_use)
- [setjmp - cppreference.com](https://ja.cppreference.com/w/cpp/utility/program/setjmp)
- [Memory corruption due to word sharing. - Linus Torvalds. GCC mailing list](https://gcc.gnu.org/ml/gcc/2012-02/msg00027.html)
- [C++0xのメモリバリアをより深く解説してみる - yamasaのネタ帳](https://yamasa.hatenablog.jp/entry/20090929/1254237835)
- [C++20 を相談しながら調べる会 #3 共有ドキュメント](https://docs.google.com/document/d/163DDT73-ccWJY8khoX2wOS6tiYYsJ2mvPdkLlIZXywk/edit)

### 謝辞
この記事の7割は以下の方々によるご指摘によって成り立っています。

- [@kariya_mitsuruさん](https://twitter.com/kariya_mitsuru/status/1183334836989120512)
- [@mokamukurugaさん](https://twitter.com/mokamukuruga/status/1183340276733005825)
- [@mokamukurugaさん](https://twitter.com/mokamukuruga/status/1183380975335559169)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20191014_deprecated_volatile.md)