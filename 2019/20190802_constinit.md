# ［C++］constinit？🤔

[:contents]

### `constinit`指定子

`constinit`指定子はC++20より変数に付けることができるようになるもので、`constexpr`変数がコンパイル時に初期化される事を保証するように、`constinit`変数が静的初期化、特に __定数初期化__ されている事を保証します。

しかし、`constexpr`とどう違うのか、なにが嬉しいのか、などは中々理解しづらいものがあります。

提案文書より、サンプルコード。
```cpp
const char *g() { return "dynamic initialization"; }
constexpr const char *f(bool p) { return p ? "constant initializer" : g(); }
  
constinit const char *c = f(true);  // OK.
constinit const char *d = f(false); // ill-formed
```

一見すれば、初期化式が定数式で実行可能ではない時にエラーを起こしているように見えます。とするとやはり、`constexpr`指定との差がよくわかりません・・・

### 静的変数の初期化

グローバル（名前空間スコープの）変数やクラスの静的メンバ変数、関数ローカルの`static`変数など静的ストレージにあるものはプログラムの開始前に、スレッドローカルストレージにあるものはスレッドの開始前に、それぞれ初期化が完了しています。

それらの変数はまずコンパイル時に __静的初期化__ され、実行時（プログラムロード時、スレッド起動時）に __動的初期化__ されます。結果として、プログラム開始時もしくはスレッド開始時には初期化が完了しているように見えているわけです（正確には実装は変数が使用される直前まで初期化を遅延させることが許可されています）。

動的初期化はその初期化式が定数式で実行できない場合に実行時に行われるものです。ここでは重要では無いので深掘りしません。

静的初期化はコンパイル完了時までになんらかの値で初期化しておくもので、 __定数初期化__ と __ゼロ初期化__ の2段階で行われます。

静的初期化においてはまず、定数初期化が可能であるならば変数は定数初期化されます。これによってその変数の初期値は確定し、以降の初期化はスキップされます。  
次に、定数初期化できなかった残り全ての変数をゼロ初期化します。ゼロ初期化は変数をゼロに相当する値によって初期化するものです（例えば、浮動小数点型の`0.0`、ポインタ型の`nullptr`等）。この時、クラス型のコンストラクタは無視され、その型を構成する全ての型が再帰的にゼロ初期化されます。  
これにより、静的ストレージ・スレッドローカルストレージにある変数は全てとりあえずはなんらかの値で初期化されている状態でコンパイルが終了します。

静的初期化された値はプログラムイメージ（実行ファイルバイナリ、アセンブリ）の一部としてプログラム内のどこかに埋め込まれています。

動的初期化はこのように初期化されている変数に対して、実行時に実際の初期化式によって初期化を行います。

### 定数初期化（constant initialization）

定数初期化は静的初期化の中で、他のあらゆる初期化に先行して行われます。そして、定数初期化が完了すればその変数の初期化はそこで完了しており、その後一切の初期化処理は行われません。

定数初期化を行うためには、変数が静的ストレージかスレッドローカルストレージにあり、その初期化式が定数式でなくてはなりません。  
それを満たせば全ての変数は定数初期化できます。`constexpr`が付いていなくてもいいですし、`const`がなくても大丈夫です。初期化式が`constexpr/consteval`関数を呼び出していても、初期化に当たって一時オブジェクトを生成しても構いません。

ただし、定数初期化されている`const`な整数型と列挙型だけが他の定数式で利用でき、その他の種類の変数は定数初期化されただけでは定数式で使えません。

#### 定数初期化コンストラクタ

定数初期化はもちろん任意のクラス型に対しても行えます。  
そのクラスが[リテラル型](http://boleros.hateblo.jp/entry/20130718/1374155184)でなかったとしても、`constexpr`コンストラクタを持ち、そのコンストラクタからメンバ変数を全て定数式で初期化できれば、そのクラスのオブジェクトは定数初期化できます。

これを利用しているクラスはSTLにも存在しており、`std::mutex`のデフォルトコンストラクタ、`std::unique_ptr`のデフォルトおよび`nullptr`を受けるコンストラクタなどが定数初期化コンストラクタを持っています（`std::unique_ptr`のこれらのコンストラクタになぜ`constexpr`が付いているのか不思議に思った人は多いのではと思います、こういう事です）。

上でも述べていますが、定数初期化（静的初期化）は静的ストレージかスレッドローカルストレージにあるものが対象で、ローカル変数に対しては適用されません。

```cpp
#include <mutex>
#include <memory>
#include <thread>

struct C {
  C() = default;

  C(int n) : m(n) {}

  operator int() const noexcept {
    return m;
  }

private:
  int m;
};

//全て定数初期化される
std::mutex m{};
std::unique_ptr<int> p1; 
std::unique_ptr<int> p2 = nullptr;
C c1{};

//これは動的初期化になる（切り替えられるかもしれない）
C c2{10};

int main() {
  std::lock_guard lock{m};

  int n = c1;
  int m = c2;

  //ローカル変数の初期化はまた別の話・・・
  std::unique_ptr<int> p3;
}
```
[出力アセンブリ例 - Compiler Explorer](https://godbolt.org/z/ZevUtd)

コンパイル結果を見ても静的初期化されてるのか動的初期化されてるのかはよくわからないですね・・・。gccの方は`__static_initialization_and_destruction_0(int, int):`なるセクションに突っ込まれているのはわかりますが・・・


### 動的初期化の静的初期化への切り替え

静的初期化（定数 or ゼロ初期化）は必ず行われた上でコンパイルが完了しています。  
そして追加で、コンパイラは次の条件を満たす場合に動的初期化を静的初期化に切り替えることが許されています。

- 動的初期化で実行される予定の初期化式は副作用を持たない
- 静的初期化に切り替えても、動的初期化した場合と全く同じ値で初期化できることが保証できる
  - 他の静的変数の初期化式に依存している・されている場合でも結果が同じにならなくてはならない
  - すなわち、プログラム全体として初期化後の結果は切り替え前と全く同一でなければならない

すなわち、通常の初期化順序に沿って動的初期化を行った結果と（プログラム全体として）全く同じ結果になることがコンパイル時に分かる場合に、動的初期化を静的初期化に切り替えることが許されます。

動的初期化から切り替えてゼロ初期化するというケースは無いと思うので、実質的に定数初期化されることになります。  
この初期化タイミングの切り替えは可能であっても必ず行われるとは限りません。コンパイラによります。

### `constinit`の効能

変数を静的初期化、特に定数初期化しておくことのメリットは、その変数の初期化に関してデータ競合などを考える必要がないことです。

動的初期化では初期化処理はプログラム実行時（スレッド起動時）の一番最初に起こり、その初期化の順序及び初期値に依存するようなコードではデータ競合によって思わぬバグを仕込むことになる可能性があります。  
翻訳単位を超えて動的初期化される変数を使っている場合などはその初期化順およびそれに起因するバグを理解することは非常に困難になるでしょう・・・

静的初期化では初期化処理はコンパイル時に完了しており、そこでは翻訳単位毎に宣言順で初期化されるためデータ競合は発生しません。プログラム開始時、動的初期化開始前にはその初期値は確定しており静的初期化された変数の初期値に依存するような処理を少しだけ安全に書くことができます。

通常の静的初期化は少なくともゼロ初期化が行われている事は間違い無いのですが、定数初期化が行なわれたかどうか、つまり変数が動的初期化されるのかどうかをコンパイル後に知る事は困難です。  
前項の動的初期化からの切り替えも必ず行われるとは限りませんし、思わぬ変更から定数初期化しているつもりの初期化式が動的初期化になってしまっている事もありえます。本当に定数初期化されたかを見るのはアセンブリを確認するしかありません・・・

これは`consteval`関数が導入された理由の一つと同じ問題です。つまり、`constexpr`変数の初期化以外の所で`constexpr`関数が本当にコンパイル時に実行されたかどうかは容易には分からなかったのです。

`constexpr`変数・`consteval`関数と似たように、`constinit`変数は変数が動的初期化される場合にコンパイルエラーを起こします。別の言い方をすると、`constinit`指定子は`constinit`変数が動的初期化されないことを保証します。  
そして、`constinit`変数は確実に静的初期化によってコンパイル時に初期化が完了します。

### 利用例

前述のように、`constinit`指定は静的・スレッドローカルストレージにある変数に指定でき、その初期化式が定数式でなければなりません。  
初期化式が無い場合、静的・スレッドローカルストレージにある変数はゼロ初期化され、実行すべき初期化式が無いために動的初期化されません。したがって、`constinit`変数に初期化式がない場合はゼロ初期化が保証されます。

静的初期化されるかどうかはリンケージ指定（`static, extern`）とは無関係ですが、別の翻訳単位で定義されている変数の`extern`宣言に対しての`constinit`指定は未定義動作を引き起こすので注意が必要です（おそらくエラーにはなりません）。

```cpp
#include <mutex>
#include <memory>
#include <random>

constinit const int N = 1;    //ok
constinit unsigned int M = N; //ok、constな整数型は定数式で利用可能

constinit thread_local static int Counter = 0; //ok

constinit const double PI = 3.1415; //ok
constinit double PI2 = PI + PI;     //ng、変数PIは定数式で利用不可

constinit static int L; //ok、ゼロ初期化される
constinit int Array[3]; //ok、ゼロ初期化される

constinit std::mutex m{};           //ok、定数初期化コンストラクタ呼び出し
constinit std::unique_ptr<int> p1;  //ok、定数初期化コンストラクタ呼び出し

constinit extern int def = 10;  //ok
constinit extern int ext;       //ng、おそらくエラーにはならないが未定義動作（診断不要）


struct S {
  constinit static const int x;
  static const int y;
  static constexpr int z = 56;
};

const int S::x = 12;            //ok、constinit変数の初期化
constinit const int S::y = 34;  //ok
constinit constexpr int S::z;   //エラーにはならないと思われるが意味がなく、インライン変数に対する多重定義

int main() {
  constinit static std::unique_ptr<int> ptr = nullptr;                //ok、静的ローカル変数
  constinit thread_local std::mt19937 engine(std::random_device{}()); //ng、定数式で初期化できない

  constinit int local = 0;  //ng、ローカル変数
}
```

`constinit`指定は変数宣言に指定でき、その効果はその変数の初期化宣言に対して適用されます。`extern`変数や静的メンバ変数のように宣言と定義が別れる場合、初期化宣言から`constinit`宣言が到達不可能となると未定義動作（診断不要）です。

### `const`一族

||`const`|`constexpr`|`consteval`|`constinit`|
|:---|:---:|:---:|:---:|:---:|
|誕生時期|神代の頃|C++11|C++20|C++20|
|変数に付加|○|○|×|△|
|関数に付加|△|○|○|×|
|変数への効果|immutable化|定数式でも使用可能<br/>実行時に`const`化|コンパイルエラー|静的初期化保証|
|関数への効果|`const`変数からのみ呼出可能|定数式でも使用可能|定数式でのみ使用可能|コンパイルエラー|

### 参考文献
- [P1143R2 Adding the `constinit` keyword](https://wg21.link/P1143)
- [6.6.2 Static initialization [basic.start.static] - ISO/IEC 14882:2017 N4659](https://timsong-cpp.github.io/cppwp/n4659/basic.start.static)
- [初期化 - cppreference.com](https://ja.cppreference.com/w/cpp/language/initialization#Non-local_variables)
- [定数初期化 - cppreference.com](https://ja.cppreference.com/w/cpp/language/constant_initialization)
- [Constant initialization - Andrzej's C++ blog ](https://akrzemi1.wordpress.com/2012/05/27/constant-initialization/)
- [mutexのconstexprコンストラクタ - yohhoyの日記](http://d.hatena.ne.jp/yohhoy/20120621/p1)
- [`[[clang::require_constant_initialization]]` - Clang 10 documentation](https://clang.llvm.org/docs/AttributeReference.html#require-constant-initialization)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190802_constinit.md)