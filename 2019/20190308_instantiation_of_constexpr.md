# ［C++］ constexpr関数がインスタンス化されるとき

「[P0859R0 評価されない文脈でconstexpr関数が定数式評価されることを規定](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)」を理解するためのメモです。

以下の文章内でのconstexpr関数についてのインスタンス化という言葉はテンプレートにおけるインスタンス化と同じ意味、すなわちconstexpr関数の定義の評価が発生するという意味合いで使用しています。

[:contents]

### 必要な知識

#### unevaluated operand（未評価オペランド）
unevaluated operandsとは、`sizeof`、`decltype`、`noexcept`、`typeid`のオペランド（引数）として指定されるもの（式）の事で、その名の通りそのオペランドは評価されません。

評価されないとは、そのオペランドに含まれるいかなる計算や関数呼び出しも実行されないということで、そこで参照される関数やクラス等の宣言のみを考慮する（定義が必要ない）ことを意味します。

```cpp
struct S;

template<typename T>
int f();

int main()
{
  //評価されないのでSとfには定義が必要ない
  decltype(f<S>()) n = sizeof(f<S>()); //int n = sizeof(int);と等価
  std::cout << n;
}
```
ただし、`noexcept`以外は型名を指定することができ、その場合の型名オペランドはunevaluated operandではありません。

#### potentially evaluated（おそらく評価される）
ある式がunevaluated operandでなくその部分式（subexpression）でもないとき、その式はpotentially evaluatedと言われます。評価される（evaluated）のでその式に関わる関数や型には定義が必要になる可能性があります。

```cpp
template<typename T>
int f();

int main()
{
  //f<int>()はpotentially evaluated、fの定義が必要
  auto n = f(0);
  std::cout << n;
}
```
つまりは、`sizeof`、`decltype`、`noexcept`、`typeid`、いずれのオペランドでもない式の事だと思っていいでしょう。

potentiallyというのは、例えば以下のようなとき
```cpp
if(true) {
  f(0);
} else {
  f(1);
}
```
この場合、`f(0)`も`f(1)`も評価される可能性のある文脈に現れていますが、`f(1)`の方は絶対に評価されません。しかし、この場合でもコンパイラは両方のコードをコンパイルします。この様に、評価されるとは思うけど本当にされるかどうかはわからない、という意味合いでpotentially evaluatedなのだと思われます。

#### odr-used

大さっぱに言えば、potentially evaluatedな式に含まれている変数や関数はほぼodr-usedとなります。つまりは、定義が必要となる使われ方の事で、odr-usedであれば定義が必要になります。

potentially evaluatedであってodr-usedとならない例は、純粋仮想関数の呼び出しやメンバポインタの形で現れるとき、static constなメンバ変数を定数式でrvalueに変換する場合、最終的に結果が捨てられる形（discarded-value expression）になる場合などです。

```cpp
struct S;

S* ps{};  //ポインタは不完全型でも宣言可能、odr-usedではない

struct S { 
  static const int x = 0; 
};

decltype(&S::x) p{};  //unevaluated operandなので、odr-usedではない

int f() {
  S::x;  //discarded-value expression、odr-usedではない
  return S::x;  //lvalue -> rvalue変換が定数式で可能、odr-usedではない
}

```

##### 関数

後ほど重要になってくるので関数だけはもう少し詳しく掘り下げておきます。

>関数名がpotentially evaluatedな式に現れるとき、以下の場合にodr-usedされます。
>
>- 関数は名前探索のただ一つの結果、であるか
>- オーバーロード候補の一つである
>
>ただし、以下を満たしていること
>
>- その関数が純粋仮想関数ならば、明示的な修飾名で呼び出されている
>- 式の結果がメンバポインタとならない
>
>クラスのコピー・ムーブコンストラクタは、それが最適化などの結果によって省略されたとしても、odr-usedされています。
>
>また、純粋仮想関数ではない仮想関数は常にodr-usedされます。

明示的な修飾名で呼び出されている純粋仮想関数とは、以下のような呼び出しの事です。
```cpp
struct base {
  virtual int f() = 0;
};

int base::f() {
  return 0;
}

struct derived : base {
  int f() override {
    return 10;
  }
};

base* b = new derived{};

auto n = b->f();        //通常の仮想関数呼び出し、odr-usedでない
auto m = b->base::f();  //明示的な修飾名での呼び出し、odr-used
//n == 10, m == 0
```
つまり、明示的な修飾名での呼び出しはもはや仮想関数呼び出しではなく、通常の純粋仮想関数の呼び出しはodr-usedではありません。

#### クラスの特殊メンバ関数が実装されるとき
クラスの特殊メンバ関数とは、デフォルト・コピー・ムーブコンストラクタ、コピー・ムーブ代入演算子、デストラクタ、の事です。

ユーザー定義されていないクラスの特殊メンバ関数はコンパイラによって暗黙の宣言が行われ、odr-usedされたときに初めて暗黙に定義されます。  
仮に最適化等によってそのodr-usedが最終的に消え去ったとしても、その時点で定義されます。

実は、常に定義されているわけではないのです。

odr-usedされたとき、なので`sizeof`等の未評価オペランド内では宣言のみで定義がないことになります。

#### constexpr関数の実行と評価のタイミング
constexpr関数は定数式から呼び出されたときにインスタンス化され、実行されます。  
定数式となるには定数式で現れてはいけない構文が現れなければ定数式となり、コンパイル時に実行可能になります。

これを説明しだすと止まらないので、詳しくは以下をご参照ください。  
[5.22 定数式（Constant expressions） - C++11の文法と機能(C++11: Syntax and Feature)](http://ezoeryou.github.io/cpp-book/C++11-Syntax-and-Feature.xhtml#expr.const)

しかし、定数実行を行うコンテキストについては規定がありません。そのためコンパイラは可能な限り定数式を処理し、コンパイル時に値を確定させようとします。それが未評価オペランドであっても例外ではありません・・・

### 問題となるコード例
以下は[P0859R0](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)によって欠陥修正されていない世界のお話です。
この変更は欠陥の修正なので過去のバージョンにさかのぼって適用されています。なので、clangやgccでは一部の問題が早い段階から修正されているようです。  
そのために問題が確認できるコンパイラが古いものであることがあります。Wandbox様々です。

#### その1
[Core Issue 1581](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html#1581)より

```cpp
struct duration {
  constexpr duration() {}
  constexpr operator int() const { return 0; }
};

int main()
{
  //duration d = duration();
  int n = sizeof(short{duration(duration())});
  std::cout << n;
}
```
コンパイルエラー : [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NeVfflG6R807YydL) 

一見コンパイルの通りそうなこのコードは、C++17までの規格に則るとエラーとなります。なぜでしょう？

`int n = sizeof(short{duration(duration())});`

ここの行に注目すると、`sizeof`オペランド中の`duration(duration())`は`duration`クラスのコピー/ムーブコンストラクタを要求しています。`duration`クラスはそれらを宣言すらしていないので、コンパイラによって暗黙に宣言されています。

しかし`sizeof`のオペランドは未評価オペランドであり、odr-usedではないため`duration`のコピー/ムーブコンストラクタは暗黙定義されません。従って、未定義の関数を呼び出す形になるため定数式では無くなります。ただし、宣言はあるのでコンパイルエラーにはなりません。  
残るのは、`duration -> short`の変換です。これには`duration::operator int()`が使われて`int -> short`の変換となり、これは縮小変換になるためリスト初期化（波かっこ初期化）において許可されないのでコンパイルエラーになります。

なるほど、一つづつ見ていくと納得の動作ですね。  
では次に、その上の行にあるコメントを外してみましょう！

コメントを外すと : [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/uMlwuCST5e0QM8g7)

コンパイル通りました。なぜでしょうか・・・

`duration d = duration();`

この行では`duration`クラスの変数宣言とデフォルト構築を行っています。最終的にはデフォルトコンストラクタのみになるとはいえ、形式的には左辺でデフォルト構築した一時オブジェクトを右辺`d`にムーブして構築する形になります。つまり、ここで`duration`のムーブコンストラクタはodr-usedされるので、暗黙に定義されます。

そして次の行に行くわけですが、`duration`のムーブコンストラクタは既に定義されており、それは暗黙定義のものであり、メンバや基底も特に無いためconstexprになります。その結果`duration`の構築から`int`のリテラル0の変換までが定数式で実行可能になります。  
そこから`short`への変換ですが、定数式であれば縮小変換であっても、変換元の定数値が変換先の型で表現可能でありさえすれば定数実行可能になります。  
この結果、`sizeof`のオペランドはすべて定数実行可能であり、`short`の定数値0になります。`sizeof`は結果として`short`のサイズを恙なく出力し、何のエラーも起こりません。

何とも奇妙な振舞です。  
これらの奇妙な振舞の根本は特殊メンバ関数（この場合ムーブコンストラクタ）の暗黙定義のタイミングと定数実行が行われるコンテキストが曖昧であることにあります。

#### その2
[P1065r0](www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1065r0.html
)および、[llvm bug 23135](https://bugs.llvm.org/show_bug.cgi?id=23135)より

```cpp
template<typename T>
int f(T x)
{
    return x.get();
}

template<typename T>
constexpr int g(T x)
{
    return x.get();
}

int main() {

  // O.K. The body of `f' is not required.
  decltype(f(0)) a;

  // Seems to instantiate the body of `g'
  // and results in an error.
  decltype(g(0)) b;

  return 0;
}
```
 [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xkl1Uxt4xH9Zkc7U)

一つ目の`decltype(f(0)) a;`は`int a;`と同じ意味であり、`f(0)`はconstexprでもないので何の問題もなくコンパイル可能です。

`decltype(g(0)) b;`も同じであるはずです。しかし、`g(0)`は定数実行可能でありコンパイラが貪欲に定数化しようとした結果、未評価オペランドのはずなのに`g<int>(int)`がインスタンス化（定義が評価）されてしまい、`int`はメンバ関数`get`を持たないことからコンパイルエラーを引き起こします。

これは明らかにバグですが、根本原因は定数実行が行われるコンテキストが曖昧であることにあります。

#### その3
[Core Issue 1581](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html#1581)より
```cpp
template<int N>
struct U {};

int g(int);

template<typename T>
constexpr int h(T) { return T::error; }

template<typename T>
auto f(T t) -> U<g(T()) + h(T())> {}

int f(...) { return 0;}

int k = f(0);
```
失敗例： [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/cca8pP5XNo3GIkxE)   
成功例： [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/F2hGCM3qZYmwgFDW)

これは少し複雑ですが、最終的に`k = f(0);`によって呼ばれる`f`は引数がellipsisである方が想定されます。

`template<typename T> auto f(T t) -> U<g(T()) + h(T())> {}`

問題となるのはここの関数定義です。特に変数後置部`U<g(T()) + h(T())>`の`operator+`の評価順によって分岐します。  

その左辺`g(T())`を先に評価する場合、`g(int)`はconstexprでなく定義もないので定数実行できません。そのため、定数式ではないことが分かります。そのため、`U`の非型テンプレートパラメータは確定できず、その時点で以降の式を評価する必要がないことが分かるため`h(T())`は評価されず、SFINAEによってもう一つの`f()`を見に行きます。

右辺`h(T())`が先に評価される場合は必ずコンパイルエラーを引き起こします。  
`h<int>(int)`単体はconstexpr指定されており、定数実行可能である可能性があります。そのためコンパイラは定義を見に行きます。結果、`int`はメンバ変数`error`を持たないためエラーになりますが、このエラーが引き起こされるところはSFINAEによって継続される文脈ではないのでコンパイルエラーを引き起こしてしまいます。

この場合の問題は、プログラマから見てconstexpr関数のインスタンス化が必要かどうかが不明瞭であることです。つまりは、constexpr関数がインスタンス化されるコンテキストが不明瞭であることが原因です。  
エラーになるのかならないのか、はっきりしてほしい所です。

#### その4
[Core Issue 1581](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html#1581)より

```cpp
#include <type_traits>

template <class T>
constexpr T f(T t) { return +t; }

struct A { };

template <class T>
decltype(std::is_scalar<T>::value ? T::fail : f(T()))
  g() { }

template <class T>
void g(...);

int main()
{
  g<A>();
}
```
失敗例： [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/33m59K6TZlMrbsQO)   
成功例： [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/TIZZX0jZo5AoGjxg)

この例はより深淵に踏み込みます。

一つ目の`g()`の戻り値型`decltype(std::is_scalar<T>::value ? T::fail : f(T()))`の評価タイミングが問題です。

constexpr関数がいつインスタンス化するのか？すなわち、構文解析時にここが評価されたとき、`f(T())`がインスタンス化されるかどうかで結果が変わります。

構文解析時にconstexpr関数がインスタンス化される場合、`f(T())`がインスタンス化され、型`A`には単項`+`演算子のオーバーロードはないのでインスタンス化に失敗しエラーとなります。エラー発生個所はSFINAEによって置き換えられる文脈ではないのでコンパイルエラーとなります。

（構文解析の後の）定数評価時にconstexpr関数がインスタンス化される、すなわち構文解析時にconstexpr関数インスタンス化が行われない場合、`g()`の戻り値を決めようとすると`A`に入れ子型`T::fail`がないことからエラーとなり、SFINAEによってもう一つの`g()`が選ばれます。よってコンパイルは恙なく完了します。

この問題も、constexpr関数のインスタンス化がいつ行われるのか？が曖昧であることが原因で、つまりは定数実行されるコンテキストが明確ではないことが原因です。


### 解決のための変更

上記の問題に共通することは、定数式が実行されるコンテキストが曖昧であるために、constexpr関数がインスタンス化されるタイミングも不明解になってしまっている、という事です。

では、P0859はこれらをどのように解決するのでしょうか？

#### named by（指名される）

まず、関数のodr-usedについてが以下のように変更されます。

>ある関数が、式もしくは何らかの変換の中でnamed byである（指名される）とは
>
>- 関数は名前探索のただ一つの結果、であるか
>- その式・変換に際し必要となる関数呼び出しについてのオーバーロード候補の一つである
>
>ただし、以下を満たしていること
>
>- その関数が純粋仮想関数ならば、明示的な修飾名で呼び出されていること
>- 式の結果がメンバポインタとならない
>
>純粋仮想関数ではない仮想関数は常にodr-usedされ、そうでない関数はpotentially-evaluatedな式・変換から指名された（named by）ときにodr-usedされる。

named byという言葉が間に入っただけで実質あまり変わっていません。named byという言葉は後で使います。

#### potentially constant evaluated（おそらく定数評価される）

>ある式がpotentially constant evaluatedであるとは、以下の時です
>
> - manifestly constant-evaluatedな（間違いなく定数評価される）式
>   - 定数式
>   - constexpr if文の条件式
>   - consteval関数の呼び出し
>   - 制約式（コンセプト）
>   - 定数初期化（constant initialization）できる変数の初期化式
>   - 定数式で使用可能な変数の初期化式
>     - constexpr変数
>     - 参照型
>     - const修飾された整数型
>     - enum型
>- potentially evaluatedな式
>- リスト初期化子の直接の部分式
>- テンプレートパラメータに依存する変数名に対するアドレス取得
>- 上記いずれかの部分式が、ネストした未評価オペランドの部分式ではない

このルールは定数式が実行されうるコンテキストを定めたものと言えます。これらのコンテキストでは定数式が実行されるかもしれません。

manifestly constant-evaluatedな式とは、`std::is_constant_evaluated() == true`となる式の事でもあります。

ネストした未評価オペランドの部分式とは、`sizeof`の中に`sizeof`があるような場合です。
```cpp
constexpr int a = 0, b = 1;

auto s = sizeof(sizeof(a + b));   //この場合、`sizeof(size_t)`であることが明らかなので
                                  //定数式`a+b`はpotentially constant evaluatedではない
```

#### needed for constant evaluation（定数評価に必要）

ある関数がpotentially constant evaluatedな式から指名（named by）される時、needed for constant evaluationであると言われます。

また、ある変数の名前がpotentially constant evaluatedな式に現れる時、needed for constant evaluationであると言われます。  
ただし、そのような変数はconstexpr変数、参照型、const修飾された整数型のいずれかであるときに限ります。

#### クラスの特殊メンバ関数が実装されるタイミング
ユーザー定義されていないクラスの特殊メンバ関数はコンパイラによって暗黙の宣言が行われ、odr-usedされたときに初めて暗黙に定義される、というのが今までの動作でした。

C++20ではそこに加えて、needed for constant evaluationであるときにも暗黙に定義されるようになります。  
これにより、未評価オペランドの定数式内であっても暗黙に定義されるようになります。

#### （関数）テンプレートのインスタンス化
合わせて、テンプレートが暗黙的にインスタンス化されるときも若干変更が入ります。  
主に、existence of the definition affects the semantics of the program（定義の存在がプログラムのセマンティクスに影響を与えるとき）という条件が追加されます。

>クラステンプレートおよびメンバーテンプレートのメンバー関数・変数が明示的特殊化も明示的インスタンス化もされていないとき、以下のどちらかの場合に暗黙的にインスタンス化されます。
>
> - そのメンバー定義が必要になるコンテキストで参照されたとき（odr-usedされたとき）
> - メンバー定義の存在がプログラムのセマンティクスに影響を与えるとき
>
>明示的特殊化も明示的インスタンス化もされていない関数テンプレートの特殊化、またはfrinde関数テンプレートの定義から生成された宣言は、以下のどちらかの場合に暗黙的にインスタンス化されます。
>
> - その関数定義が必要となるコンテキストで参照されたとき（odr-usedされたとき）
> - 定義の存在がプログラムのセマンティクスに影響を与えるとき

frinde関数テンプレートの定義から生成された宣言とは、クラス内でfrinde関数の定義を行った場合にその外部名前空間になされる暗黙の関数宣言の事です（この宣言は明示的に行われない限りADLによってのみ参照可能です）。

変数テンプレートに関してはここでは重要でなく、上記二つとほぼ同じ文言なので省略します。

ではこの、「定義の存在がプログラムのセマンティクスに影響を与えるとき」、という何ともあいまいな条件は一体どんな時でしょうか？

>テンプレート変数・関数がある式においてneeded for constant evaluationであるとき、「定義の存在がプログラムのセマンティクスに影響を与える」とみなされます。これには以下の場合も含みます。
>
> - 式を定数評価する必要がないとき
> - 定数式の評価の際に定義が使われないとき

横文字用語が再帰しまくってよく分からなくなってきました・・・

ある関数がneeded for constant evaluationとは、定数評価されうる式からその関数が参照される事です。  
そしてそのような式が定数評価の必要がないか（未評価オペランド等）、定数式の評価の際に定義が使われない場合（条件演算子の絶対に評価されない方、等）でも、その関数の定義が評価されます。

すなわち、テンプレート関数はpotentially constant evaluatedな式に出現する場合に確実にインスタンス化される、ということです。

これらの追加された条件は主に定数式内の関数・変数テンプレートがインスタンス化されるタイミングを定めたものであることが分かります。

一緒に書いてあるサンプルコードを見てみましょう。

```cpp
template<typename T>
constexpr int f() { return T::value; }

template<bool B, typename T>
void g(decltype(B ? f<T>() : 0));

template<bool B, typename T>
void g(...);

template<bool B, typename T>
void h(decltype(int{B ? f<T>() : 0}));

template<bool B, typename T>
void h(...);

void x() {
  g<false, int>(0);  //OK
  h<false, int>(0);  //compile error!
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ZkTVDmSer65m41Pr) 

`x()`内1行目、`g<false, int>(0);`はまず`g()`の1つ目の宣言を見に行きます。そこの引数宣言を見ると`decltype(B ? f<T>() : 0)`となっています（`B = false`）。decltype内の式は未評価オペランドなので`B ? f<T>() : 0`はpotentially constant evaluatedではありません（ので、needed for constant evaluationでもありません）。  
そのため、`f<T>()`はインスタンス化されずdecltypeの結果は両方の式に共通する`int`となり、コンパイルは恙なく完了します。

`x()`内2行目、`h<false, int>(0);`はまず`h()`の1つ目の宣言を見に行きます。その引数宣言は`decltype(int{B ? f<T>() : 0})`となっています（`B = false`）。decltype内の式は未評価オペランドですが、`int{B ? f<T>() : 0}`にはリスト初期化があります。この内側の式はpotentially constant evaluatedになります（ので、needed for constant evaluationでもあります）。  
すると、`f<T>()`の定義が「プログラムのセマンティクスに影響を与える」ので`f<T>()`はインスタンス化されます。しかし、`int`は入れ子型`T::value`を持たないのでインスタンス化は失敗し、コンパイルエラーとなります。

#### 結局
この様なややこしい規則と用語の導入によって、定数式が評価されるコンテキストと、constexpr関数及び関数テンプレートがインスタンス化される場所・タイミングが明確に定められました。

それによって先の4つの問題も一定の解決が図られます。

1つ目の問題
```cpp
  //duration d = duration();
  int n = sizeof(short{duration(duration())});
```
これは`duration`クラスのムーブコンストラクタが定義されるタイミングが問題でした。

このコードの`sizeof`内は未評価オペランドではありますがリスト初期化があるので、その内側の式はpotentially constant evaluatedになります。
`duration`クラスのムーブコンストラクタはそこから指名（named by）されているので（すなわちneeded for constant evaluation）暗黙の定義がなされます。  
結果全ての定数式の実行及び`sizeof`の評価は恙なく完了し、上の行のコメントを解除しなくてもこのコードはコンパイルが通るようになります。

2つ目の問題
```cpp
template<typename T>
constexpr int g(T x)
{
    return x.get();
}

decltype(g(0)) b;
```
このコードでは貪欲な定数実行の結果`g(0)`のインスタンス化が発生してしまうことが原因でした。

しかし、decltypeの内部は未評価オペランドであり、そこの式（`g(0)`）はpotentially constant evaluatedな式の条件に当てはまっておらず、これは定数式ではありません。そのため、「定義の存在がプログラムのセマンティクスに影響を与える」とはみなされません。  
よって、`g(0)`のインスタンス化は発生せず、`decltype(g(0))`は`int`となりコンパイルが完了します。

3つ目の問題
```cpp
template<int N>
struct U {};

int g(int);

template<typename T>
constexpr int h(T) { return T::error; }

template<typename T>
auto f(T t) -> U<g(T()) + h(T())> {}

int f(...) { return 0;}

int k = f(0);
```
このコードは、関数`f`の戻り値型計算の過程で、`+`のオペランドをどちらから評価するかでエラーになるかならないか決まる物でした。

`U<g(T()) + h(T())>`の内部ですが、これは非型テンプレートパラメータの初期化式です。未評価オペランドはありませんので、potentially evaluatedな式であり、定数式である筈です。  
したがって、`g(T())`はodr-usedされており、`h(T())`は「定義の存在がプログラムのセマンティクスに影響を与える」とみなされることから、両方の関数のインスタンス化が発生します。これはどちらのオペランドから評価をしたとしても、両方のインスタンス化が必要になります。  
結果、`h(T())`のインスタンス化は`int::error`となる型は存在せず失敗し、SFINAEによる継続が可能な文脈でもないため、このコードは必ずコンパイルエラーになります。

4つ目の問題
```cpp
template <class T>
constexpr T f(T t) { return +t; }

struct A { };

template <class T>
decltype(std::is_scalar<T>::value ? T::fail : f(T()))
  g() { }

template <class T>
void g(...){}

g<A>();
```
このコードは、構文解析時と定数式実行時のどちらでconstexpr関数のインスタンス化が発生するかでエラーになるかが決まる物でした。

問題となるのは`g()`の戻り値型計算部分ですが、decltypeの内部は未評価オペランドとなるのでpotentially evaluatedではありません。したがってconstexpr関数のインスタンス化は一切発生しません。  
結果、`g()`の戻り値を決めようとすると`A`に`T::fail`という静的メンバがないことからエラーとなり、SFINAEによってもう一つの`g()`が選ばれます。よってコンパイルは恙なく完了します。  
構文解析時と定数実行のタイミングが異なるとかは関係なく、ここでは定数実行もインスタンス化も必要無くなったのです。
<br>

この様に、定数式実行のコンテキストとconstexpr（テンプレート）関数のインスタンス化タイミングを明確にすることで、C++標準仕様とは無関係なコンパイラの実装によってエラーとなるかが決まるような奇妙な振る舞いが取り除かれ、エラーとなるケースとそうでないケースが明快かつコンパイラ非依存に決定されるようになりました。


### 参考文献
- [5.2 未評価オペランド（unevaluated operand） - C++11の文法と機能(C++11: Syntax and Feature)](http://ezoeryou.github.io/cpp-book/C++11-Syntax-and-Feature.xhtml#unevaluated_operand)
- [リンク時に関連するルールの話 - ここは匣](http://fimbul.hateblo.jp/entry/2014/12/11/000123)
- [mainとodr-usedとpotentially evaluatedの関係 - Qita](https://qiita.com/yohhoy/items/e06227ab0a5c1f579e35)
- [15 Special member functions - N4659](https://timsong-cpp.github.io/cppwp/n4659/special)
- [15.8.1 Copy/move constructors - N4659](https://timsong-cpp.github.io/cppwp/n4659/class.copy#ctor-12)
- [8.20 Constant expressions - N4659](https://timsong-cpp.github.io/cppwp/n4659/expr.const)
- [P1065R0 : constexpr INVOKE](https://wg21.link/p1065)
- [P0859R0 : Core Issue 1581: When are constexpr member functions defined?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)
- [1581. When are constexpr member functions defined? - C++ Standard Core Language Active Issues, Revision 100](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html#1581)
- [Should decltype(foo(1)) instantiate the constexpr function template foo? - stackoverflow](https://stackoverflow.com/questions/40593515/should-decltypefoo1-instantiate-the-constexpr-function-template-foo)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190308_instantiation_of_constexpr.md)