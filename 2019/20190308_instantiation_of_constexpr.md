# ［C++］ constexpr関数がインスタンス化されるとき

「[P0859R0 評価されない文脈でconstexpr関数が定数式評価されることを規定](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)」を理解するためのメモです。

constexpr関数についてのインスタンス化という言葉はテンプレートにおけるインスタンス化と同じ意味、すなわちconstexpr関数の定義の評価が発生するという意味合いで使用しています。

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
ある式がunevaluated operandでなくその一部分でもないとき、その式はpotentially evaluatedと言われます。評価される（evaluated）のでその式に関わる関数や型には定義が必要になる可能性があります。

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

#### potential results（予想される結果）
ある式がpotentially evaluatedであるとき、その結果として想定される式の集まりをpotential resultsといいます。

ある式のpotential resultsは必ずしも単一の式ではなく、その式に含まれる式のpotential resultsも含まれます。特に、
- 配列の添え字演算子の場合は、添え字として指定される式（`a[b+c]`の`b+c`）
- クラスメンバアクセス（`., ->`）、pointer-to-memberアクセス（`.*, ->*`演算子）の場合は、その左辺の式（`(a+b).c, (a+b)->b`の`a+b`）
- 条件演算子（三項演算子）の場合は、真偽それぞれの結果となる二つの式（`a?b:c;`の`b`と`c`）
- カンマ演算子の場合は、右側の式（`a,b,c`の`c`）

がそれぞれ含まれます。

また、それらの式に関数呼び出しが含まれる場合、その引数の式はpotential resultsに含まれません。
```cpp
struct S { 
  static const int x = 0; 
};

const int& f(const int &r);

int n = b ? (1, S::x)  // S​::​x is not odr-used here
          : f(S::x);   // S​::​x is odr-used here, so a definition is required
```
この例で、`n`の初期化式のpotential resultsには最初の`S::x`及び`f(S::x)`が含まれますが、`f(S::x)`の引数の式`S::x`は含まれません。

potential resultsに含まれる式は、必ずしもpotentially evaluatedではありません。

#### odr-used

大さっぱに言えば、potentially evaluatedな式に含まれている変数や関数はodr-usedであると言います。  
つまり定義が必要となるような使われ方の事で、odr-usedであれば定義が必要になります。

以下、少し詳しめの考察。

##### 変数

potentially evaluatedな式`ex`に含まれている変数`x`は、以下の両方を満たさない場合に（`ex`によって）odr-usedされると言います。
1. `x`に左辺値→右辺値変換を適用すると、non-trivialな特殊メンバ関数を呼び出さない定数式とならない。
2. `x`がオブジェクトならば、`ex`は外側の式`e`のpotential resultsの一つ。
    - そのような`e`はdiscarded-value expressionであるか、左辺値→右辺値変換が適用されている式。


左辺値→右辺値変換（lvalue-to-rvalue conversion）とは以下のように暗黙的に右辺値へのコピーが発生することです。
```cpp
int f(int n) {
  return n;  //引数nは左辺値から右辺値へ変換され、返却される
}

int n = 10;
int&& m = int(n);  //変数nは左辺値から右辺値へ変換され、右辺値参照で束縛される
```

discarded-value expressionとは、ある式の結果を得る過程で実行する必要のある式のことで、potential resultsに含まれますが、最終的にはその式の結果は廃棄される形になります。
- 配列の添え字演算子の場合は、添え字として指定される式（`a[b+c]`の`b+c`）
- クラスメンバアクセス（`., ->`）、pointer-to-memberアクセス（`.*, ->*`演算子）の場合は、その左辺の式（`(a+b).c, (a+b)->b`の`a+b`）
- 条件演算子（三項演算子）の場合は、真偽それぞれの結果となる二つの式（`a?b:c;`の`b`と`c`）
- カンマ演算子の場合は、右側の式（`a,b,c`の`c`）

potential resultsの項のリストと同じ内容になりますが主にこれらの式です。逆に言うと、discarded-value expressionはpotential resultsに含まれる、と言えます。

以上のことを踏まえて考えてみると
1. `x`に左辺値→右辺値変換を適用すると、non-trivialな特殊メンバ関数を呼び出さない定数式とならない。

まず、特殊メンバ関数とはデフォルト・コピー・ムーブコンストラクタ、デストラクタ、コピー・ムーブ代入演算子の事で、non-trivial・trivialとはユーザー定義してるかどうかということです。

non-trivialな特殊メンバ関数を呼び出さない定数式とならない、とはつまり、trivialな特殊メンバ関数を呼び出す定数式とならない、ということです。  
これは主に組み込み型のための要件だと思われます。組み込み型であればその特殊メンバ関数は定義が無くても使用可能です。そして、定数式であればその場で値を確定させられるので定義を見に行く必要もありません。  
逆に、trivialな特殊関数でなければその定義が必要ですし、定数式でないならその変数の実体（定義）を待たねばなりません。

`x`に左辺値→右辺値変換を適用すると、なので実際に適用されている必要があるわけではありません。odr-usedであるかどうか確認するために適用するわけです。

2. `x`がオブジェクトならば、`ex`は外側の式`e`のpotential resultsの一つ。
    - そのような`e`はdiscarded-value expressionであるか、左辺値→右辺値変換が適用されている式。




##### 関数


#### 特殊メンバ関数が実装されるとき
ユーザー定義されていない特殊メンバ関数はコンパイラによって暗黙の宣言が行われ、odr-usedされたときに初めて暗黙に定義されます。

実は、常に定義されているわけではないのです。

odr-usedされたとき、なので`sizeof`等の未評価オペランド内では宣言のみで定義がないことになります。

### 問題
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
コメントを外す : [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/uMlwuCST5e0QM8g7)


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


```cpp
template<int N>
struct U {};

int g(int);

template<typename T>
constexpr int h(T) { return T::error; }

template<typename T>
auto f(T t) -> U<g(T()) + h(T())> {}

int f(...);

int k = f(0);
```

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

### 解決のための変更

#### namedとodr-used

#### potentially constant evaluated

#### needed for constant evaluation


### 参考文献
- [5.2 未評価オペランド（unevaluated operand） - C++11の文法と機能(C++11: Syntax and Feature)](http://ezoeryou.github.io/cpp-book/C++11-Syntax-and-Feature.xhtml#unevaluated_operand)
- [リンク時に関連するルールの話 - ここは匣](http://fimbul.hateblo.jp/entry/2014/12/11/000123)
- [mainとodr-usedとpotentially evaluatedの関係 - Qita](https://qiita.com/yohhoy/items/e06227ab0a5c1f579e35)
- [Clause 15 [special] - N4659](https://timsong-cpp.github.io/cppwp/n4659/special)
- [P1065R0 : constexpr INVOKE](https://wg21.link/p1065)
- [P0859R0 : Core Issue 1581: When are constexpr member functions defined?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)
- [1581. When are constexpr member functions defined? - C++ Standard Core Language Active Issues, Revision 100](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html#1581)