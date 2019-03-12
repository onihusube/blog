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

#### odr-used


##### 変数
potentially evaluatedな式に含まれている変数`x`は、以下を満たす場合にodr-usedであると言います。
- `x`を左辺値→右辺値へ変換する際、non-trivialな特殊メンバ関数を呼び出さない。
- `x`はオブジェクトではない（参照）か、`x`がオブジェクトならより大きな式のpotential resultsの一つ

##### 関数


#### 特殊メンバ関数が実装されるとき
ユーザー定義されていない特殊メンバ関数（デフォルト・コピー・ムーブコンストラクタ、デストラクタ、コピー・ムーブ代入演算子）はコンパイラによって暗黙の宣言が行われ、odr-usedされたときに初めて暗黙に定義されます。

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