# ［C++］さらに出来るようになったconstexpr（C++20）

※この内容はC++20から利用可能になる予定の情報であり、一部の変更がC++23以降に先延ばしになるなど、内容が変更される可能性があります。

C++11でconstexprが導入されて以降、あらゆる処理をconstexprで行うことを目指すかのように（おそらく実際そう）constexprは着実に強化されてきました。
C++20ではC++14以来の大幅な強化が行われ、constexprの世界はさらに広がることになります。

[:contents]

### constexprな仮想関数
ついに仮想関数をconstexprの文脈で呼び出せるようになります。初っ端から意味わからないですね・・・。

仮想関数呼び出しというと`new`がちらつきますが、ポインタや参照を介してさえいれば`new`によって確保されたオブジェクトでなくても動的ポリモーフィズムを行うことができます。  
そのような場合であれば不正なキャストなどのチェックを静的に行うことができ、その動的型（dynamic type）を静的に追跡すれば仮想関数呼び出しすら静的に解決することが可能です。

そのため、constexprの文脈で仮想関数呼び出しを禁止している制限は不要であるとして撤廃されました。

```cpp
struct base {
  virtual int f() const = 0;
};

struct derived1 : public base {
  constexpr int f() const override {
    return 10;
  }
};

struct derived2 : public base {
  constexpr int f() const override {
    return 20;
  }
};

constexpr derived1 d1{};
constexpr derived2 d2{};
  
constexpr base const& b1 = d1;
constexpr base const* b2 = &d2;
  
constexpr int n1 = b1.f();   //n1 == 10
constexpr int n2 = b2->f();  //n2 == 20
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/mWChtjk8RYRkMukD)  
この様なコードが動くようになります。

このコードのように、非constexprな仮想関数をconstexprな仮想関数でオーバーライドすることができますし、その逆（constexpr仮想関数を非constexpr仮想関数でオーバーライド）も可能です。  
また、const修飾はしておかないと実行時に呼び出すことができなくなります（constexprに初期化された変数は実行時にはconstになっているため）。

ただし、constexprなポインタ・参照はstatic変数やグローバル変数のように、staticストレージと呼ばれるところにあるものしか参照できません。  
なので、ローカルconstexpr変数をポインタ・参照に入れることは出来ません。  
（[@mokamukurugaさん、ご教授ありがとうございました！](https://twitter.com/mokamukuruga/status/1109410491158269952)）

しかし、constexpr関数の内部で利用する分にはその制約は受けず、そのconstexpr関数が定数実行されれば目的を達せます。  
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/CUE6S95SDCyTWOOx)  
この例でもは引数に渡してますが、完全にconstexpr関数内で生成から仮想関数呼び出しまでを完結させても問題ありません。

最基底で定義された仮想関数はそのconstexprの有無に関わらず派生クラスにおいてconstexprの有る無し両方でオーバーライドできます。その際、途中のオーバーライドが非constexprであっても、最終的に呼び出される最派生（most derived）のオーバーライドがconstexprであれば定数実行可能です。

```cpp
struct base {
  virtual int f() const = 0;

  constexpr virtual int g() const {
    return 0;
  }
};

struct derived1 : public base {
  int f() const override {
    return 0;
  }
  
  constexpr int g() const override {
    return 10;
  }
};

struct derived2 : public derived1 {
  constexpr int f() const override {
    return 10;
  }
  
  int g() const override {
    return 20;
  }
};

constexpr derived2 d2{};
constexpr base const& b = d2;

//ok
constexpr int a = b.f();  //a == 10
//compile error! derived2::g() is not constexpr function.
constexpr int b = b.g();
```

[ちなみに、純粋仮想関数の定義もconstexprにできます。](https://wandbox.org/permlink/2x1gP9U0enF6m8qn)

### dynamic_castとtype_id
前項の内容の延長です。constexprな仮想関数が許可されたのと同様の理由により`dynamic_cast`や多態的な型のオブジェクトに対する`type_id`も静的に解決することができます。なのでそれが可能になりました。  
また、この変更に伴って`std::type_info`の`operator==`と`operator!=`がconstexpr指定され定数式で使用可能になります。

```cpp
struct base {
  virtual int f() const = 0;
};

struct derived1 : public base {
  constexpr int f() const override {
    return 10;
  }
};

struct derived2 : public base {
  constexpr int f() const override {
    return 20;
  }
};

//組み込み型に対するtypeid
{
  constexpr auto&& int_t  = typeid(int);
  constexpr auto&& char_t = typeid(char);
  //ここまではC++11以降なら可能

  constexpr bool is_same = int_t == char_t;  //constexprな同値比較はC++20より
  static_assert(is_same == false);
}

//polymorphicな型に対するtypeid
{
  constexpr derived1 d1{};
  constexpr derived2 d2{};
  
  constexpr base const* b1 = &d1;
  constexpr base const* b2 = &d2;
  
  constexpr auto&& b1_t = typeid(*b1);
  constexpr auto&& b2_t = typeid(*b2);

  constexpr bool is_same = b1_t == b2_t;
  static_assert(is_same == false);
}


struct base2 {
  virtual int g() const = 0;
};

struct derived3 : public base, public base2 {
  constexpr int f() const override {
    return 20;
  }
  
  constexpr int g() const override {
    return 30;
  }
};

//dynamic_cast
{
  constexpr derived3 d{};
  constexpr base const* b1 = &d;
  //side cast
  constexpr base2 const* b2 = dynamic_cast<base2 const*>(b1);
}

```
多分このように書けるようになります（普段あまり使わないのと確認できないのとで自信がないですが・・・）。

このような定数実行の中で例外を投げるような適用が行われた場合は定数実行されません。例外を投げるような適用とは、dynamic_castなら参照の変換での失敗時、typeidはnullptrを参照するポインタを受けたとき、です。
```cpp
constexpr base* nullp = nullptr;
constexpr auto&& t = typeid(*nullp);  //compile error! 例外を投げるため定数実行不可


constexpr derived1 d1{};
//b1のmost derived typeはderived1
constexpr base const& b1 = d1;

//down cast
constexpr derived2 const& d2 = dynamic_cast<derived2 const&>(b1);  //compile error! 例外を投げるため定数実行不可

```
### コンパイル時メモリアロケーション
※この項は複雑で長くなるのでページ分けしました  
[［C++］ constexprなメモリの確保と解放のために（C++20）](https://onihusube.hatenablog.com/entry/2019/03/03/113722)

ざっとまとめると以下が可能になります

- constexpr デストラクタ
- new式/delete式のコンパイル時実行（operator newではない）
- `std::allocator<T>`及び`std::allocator_traits<std::allocator<T>>`のコンパイル時実行
- ~~コンパイル時に確保され解放されなかったメモリは静的記憶域に移行され実行時に参照可能~~

### unionのアクティブメンバの切り替え
共用体（union）のアクティブメンバとは、ある時点の共用体のオブジェクトにおいて最後に初期化されたメンバの事です。共用体の初期化自体はconstexprに行うことが可能ですが、あるメンバの初期化後に別のメンバを初期化した場合にアクティブメンバの切り替えが発生します。アクティブメンバの切り替えはC++17までコンパイル時に行えません。

前項の変更によってコンパイル時にメモリ確保すら可能になるため、STLの多くのクラスをconstexpr対応させることができるようになります。しかし、`std::string`や`std::optional`、`std::variant`はその実装において共用体が使われています（`std::string`はsmall-string optimization : ssoと呼ばれる最適化のために）。

それらのクラスでは共用体のアクティブメンバの切り替えが発生する可能性があり、その場合にconstexprの文脈で使用できなくなります。そのようなクラスをconstexprにさらに対応させるため、この制限は撤廃されることになりました。

```cpp
union U {
  int n;
  float f;
};

//U::fを読み出しアクティブメンバをU::nに切り替える
constexpr float change() {
  //fをアクティブメンバとして初期化 (Designated Initialization!)
  U u = { .f = 3.1415f };

  float f = u.f;  //u.nがアクティブメンバの場合はここは定数実行不可
  u.n = 10;  //u.nへアクティブメンバを切り替え、C++17までは定数実行不可

  return f;
}

int main()
{
  constexpr auto f = change();
  static_assert(f == 3.1415f);
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/KhZmpwNfPAQ0X4Nu)

ただし、非アクティブなメンバへのアクセス（そこへの参照からの間接アクセスも含む）は未定義動作であり、定数式で現れてはいけません。つまりは定数式の文脈でそのようなアクセスを行った時点でコンパイル時実行不可能になります（`std::string`のsso実装がこれに当てはまってしまっています）。


### try-catch
constexpr関数内にはこれまでtry-catchブロックを書くことは出来ませんでした。書いてあった場合はコンパイル時実行不可能です。しかし、それを書くことができるようになります。

と言っても、書くことができるようになるだけです。相変わらずthrow式が現れてはいけませんし、コンパイル時実行中に例外が投げられればその時点で実行不可です。  
つまりは、コンパイル時実行時のtry-catchブロックは無視されます。

この変更は、std::vectorをconstexpr対応させる際に問題となったために為されました。将来的にconstexprをさらに拡大させていく際にも地味な障害となるので早めに取り除いておく方が良いと考えられたのでしょう。

また、C++20では単に無視することにしただけで、将来的にコンパイル時に例外処理が行えるようになる可能性が閉ざされた訳ではありません。


### std::is_constant_evaluated()
`std::is_constant_evaluated()`はコンパイル時には`true`を、実行時には`false`を返す関数です。これにより、コンパイル時と実行時でそれぞれ効率的な処理を選択することが可能になります。

おそらくconstexprで数学関数を実装しようと思った方が通るであろう、コンパイル時にはコンパイル時実行可能なアルゴリズムで、実行時にはcmathの対応する関数で実行してほしい！ということがついに可能になります。

```cpp
#include <type_traits>  //←必須
#include <cmath>
#include <iostream>

template<typename T>
constexpr auto my_sin(T theta) {
  if (std::is_constant_evaluated()) {
    //コンパイル時
    auto fabs = [](T v) -> T { return (v < T(0.0))?(-v):(v); };
    T x_sq = -(theta * theta);
    T series = theta;
    T tmp = theta;
    T fact = T(2.0);
    
    //マクローリン級数の計算
    do {
      tmp *= x_sq / (fact * (fact+T(1.0)));
      series += tmp;
      fact += T(2.0);
    } while(fabs(tmp) >= std::numeric_limits<T>::epsilon());
    
    return series;
  } else {
    //実行時
    return std::sin(theta);
  }
}

int main()
{
  constexpr double pi = 3.1415926535897932384626433832795;
  
  std::cout << std::setprecision(16);
  
  //sin(60°)を求める
  constexpr auto sin_static = my_sin(pi/3.0); //コンパイル時計算
  auto sin_dynamic = my_sin(pi/3.0);  //実行時計算
  
  std::cout << sin_static << std::endl;
  std::cout << sin_dynamic << std::endl;
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/AlkWGowaOGevamtw)

`if constexpr`や`static_assert`でこの関数を利用すると必ず`true`として処理されます。なので、コンパイル時と実行時で処理を分けるような目的で利用する場合は通常の`if`で分岐する必要があります。しかし、実行時まで`if`文が残る事は無いでしょう。

また、通常の`if`を使うという事は`true`及び`false`となる両方のステートメントがコンパイル出来なければなりません。  
しかし、`false`となる方のステートメントにconstexpr実行不可能なもの（`throw`や`memcopy`等）が現れることは問題ありません。

#### `true`と評価されるところ
`std::is_constant_evaluated()`は、manifestly constant-evaluated（間違いなく定数評価される）という式の中で`true`となります。

manifestly constant-evaluatedな式とは以下のようなものです。

- 定数式
- constexpr if文の条件式
- consteval関数の呼び出し（consteval関数の中身）
- 制約式（コンセプト）
- 定数初期化（constant initialization）できる変数の初期化式
- 定数式で使用可能な変数の初期化式
  - constexpr変数
  - 参照型
  - const修飾された整数型
  - enum型

難しく書いてありますが、要するにコンパイル時計算中に`true`となるという事です。  
サンプルコードを見てみましょう（ドラフト規格文書より）

```cpp
//(1)
template<bool>
struct X {};
X<std::is_constant_evaluated()> x; // type X<true>

//(2)
int y;
const int a = std::is_constant_evaluated() ? y : 1; // dynamic initialization to 1
double z[a];  // ill-formed: "a" is not "usable in constant expressions"

//(3)
const int b = std::is_constant_evaluated() ? 2 : y; // static initialization to 2 

//(4)
int c = y + (std::is_constant_evaluated() ? 2 : y); // dynamic initialization to y+y

//(5)
constexpr int f() {
  const int n = std::is_constant_evaluated() ? 13 : 17; // n == 13
  int m = std::is_constant_evaluated() ? 13 : 17; // m might be 13 or 17 (see below)
  char arr[n] = {}; // char[13]
  return m + sizeof(arr);
}

int p = f();     // m == 13; initialized to 26
int q = p + f(); // m == 17 for this call; initialized to 56
```

さて、これらの場合に`std::is_constant_evaluated()`はどちらに評価されるのでしょうか？順に考えていきましょう。

(1)はクラスXのテンプレートパラメータ指定時に呼ばれています。  
Xのテンプレート引数は`bool`の非型テンプレートパラメータなので、その初期化式は定数式です。結果は`true`になります。

(2)は`const int`な変数`a`の初期化式で呼ばれています。  
これは定数式ですので（上記「定数初期化（constant initialization）できる変数の初期化式」に当たります）まず結果は`true`になります。しかしその場合は非constexprで未初期化の変数`y`を用いて初期化することになり、これは定数実行不可なので定数式では初期化されません。  
そのため、`a`の初期化はコンパイル時ではなく実行時に行われ、その場合の結果（と我々から見た結果）は`false`になります。  
これにより変数`a`は実行時に`1`で初期化されることになり、整数定数を要求する配列のサイズ指定に用いることは出来ず、配列`z`の宣言も失敗します。  
つまりこの場合の結果は、`true`と`false`両方となります。

(3)は`const int`な変数`b`の初期化式で呼ばれています。
この結果は先ほどと逆になる事が分かるでしょう。  
つまり、結果が`true`となる方のリテラル`2`での初期化が常に定数式で可能なため、この場合の結果は必ず`true`となります。

(4)は普通の`int`の変数`c`の初期化で呼ばれます。  
初期化式にはいきなり非定数の未初期化変数`y`がでてきます。この時点で定数式ではないので、この場合の結果は必ず`false`です。

(5)は少し複雑です。
まずは`int p = f();`で、`f()`の中で呼ばれます。  
`f()`はconstexpr関数であり`int`は定数初期化が可能ですのでこの場合の初期化式は定数式になります（上記「定数初期化（constant initialization）できる変数の初期化式」に当たります）。  
そのため`f()`はコンパイル時に実行され、中の`is_constant_evaluated()`は全て`true`になります。
結果、コンパイル時の`f()`は`26`を返し、`int p`は`26`で定数初期化されます。

次に、`int q = p + f();`ですが、`p`は定数初期化されているだけで定数ではありません。なので、これは定数式ではありません。  
そのため`f()`は実行時に実行されます。その時の`f()`内では、`int m`の初期化式の`is_constant_evaluated()`だけが`false`になります（`const int n`の初期化式は常に定数実行、つまり`true`になります）。  
結果`m`は`17`になるので、実行時の`f()`は`30`を返します。`p`は`26`で定数初期化されているので、`q`は実行時に`56`で初期化されます。

### 定数式内で、trivially default constructibleな型をデフォルト初期化する

これまで、以下のように基本型の変数宣言に初期化子が無い場合は未定義動作となり、constexpr関数では未定義動作が現れてはならないことからコンパイルエラーとなってしまっていました。

```cpp
constexpr int ng() {
  int n;  //undefined behavior!初期化子が必要
  ++n;

  return n;
}

constexpr int ok() {
  int n{};  //ok、デフォルト初期化（0）される
  ++n;

  return n;
}
```

こんなとても簡単なコードならば初期化子を書けばよいのですが、問題となるのはテンプレートにしたときです。

```cpp
template <typename T>
constexpr T copy(const T& other) {
  T t;  //デフォルト初期化（してほしい）
  t = other;

  return t;
}

struct trivial {
  int n;
};

struct non_trivial {
  int n = 100;
};

int main() {
  {
    //全てok
    auto cp1 = copy(10);
    auto cp2 = copy(trivial{});
    auto cp3 = copy(non_trivial{});
  }

  {
    constexpr auto cp1 = copy(10);            //ng
    constexpr auto cp2 = copy(trivial{});     //ng
    constexpr auto cp3 = copy(non_trivial{}); //ok
  }
}
```

`int`に代表される基本型は初期化子が無いとその変数の状態は未定義となりますが、それはテンプレートにおいても同様です。そして、それが定数式で現れてしまうとコンパイルエラーを引きおこします。

また、この例の`trivial`型のように集成体でありデフォルトメンバ初期化によってメンバが初期化されていない型も基本型と同様に初期化に際して初期化子が必要になります。  

これらの型のように、デフォルトコンストラクタ（に相当するもの）が全くユーザーによって定義されていないとき（メンバも何ら初期化していない時）、その型はtrivially default constructibleといいます。

trivially default constructibleな型はデフォルト初期化されると、その値は（ユーザー定義型の場合そのメンバが）`0`に相当する値によって初期化されます。  
ただし、初期化子が無い場合の初期化状態は未定義になります。

C++20からはこのようなtrivially default constructibleな型は定数式に限って初期化子が無くてもデフォルト初期化されるようになります。  
従って、先ほどのコードは全てのケースでコンパイルできるようになります。

```cpp
template <typename T>
consteval T copy(const T& other) {
  T t;  //デフォルト初期化される
  t = other;

  return t;
}

struct trivial {
  int n;
};

struct non_trivial {
  int n = 100;
};

int main() {

  constexpr auto cp1 = copy(10);            //ok
  constexpr auto cp2 = copy(trivial{});     //ok
  constexpr auto cp3 = copy(non_trivial{}); //ok
}
```

ただし、その値を読み出すことは相変わらず未定義とされます。  
あくまで、実行時とコンパイル時でコンパイル出来たりできなかったりする一貫しない挙動の修正が目的です（例えば、読み取りを出来るようにすると変数領域を確実に初期化するオーバーヘッドが入ってしまう）。

```cpp
consteval int ng() {
  int n;  //デフォルト初期化されるけど・・・

  return n; //undefined behavior!コンパイルエラーとなる
}
```

### constexpr関数内でasm宣言が書けるように

なるのですが、書けるだけです。

`std::is_constant_evaluated()`の導入によって`constexpr`関数内で`if`文によって実行時とコンパイル時の処理を分けることができます。その場合、実行時の処理はコンパイル時に実行されることはなく逆も然りです。

そのため、実行時のブロックではコンパイル時に現われてはいけないものが現れていたとしても問題はないはずです。  
例えば、`asm`宣言はC++17までは定数式に現われることができず書いてあるだけでコンパイルエラーになります。

しかし、C++20からは`constexpr`関数内で`asm`宣言を書くことができるようになります。ただし、実行は出来ないため定数式で`asm`宣言に到達しないようにしなければなりません。つまり`std::is_constant_evaluated()`とセットで用いる必要があります。

提案文書のサンプルコードを基にした例

```cpp
#include <iostream>
#include <type_traits>

constexpr double fma(double a, double b, double c) {
  if (std::is_constant_evaluated()) {
    return a*b+c;
  } else {
    //GCC拡張のインラインアセンブラ構文なのでVC++では動かないかも・・・
    asm volatile ("vfmadd213sd %0,%1,%2" : "+x"(a) : "x"(b),"x"(c));
    return a;
  }
}

int main()
{
  constexpr double fma1 = fma(2.0, 8.0, 1.0);
  double fma2 = fma(2.0, 9.0, 2.0);
  
  std::cout << fma1 << "\n" << fma2 << std::endl;
}
```
`vfmadd213sd`はFMA命令でIntelのCPUではHaswell以降のものしか対応していません（そのためWandboxで試せません・・・）

動くサンプル、二次元ベクトルの内積計算。

```cpp
#include <iostream>
#include <iomanip>
#include <type_traits>

constexpr double inner_product_v2(const double (&v1)[2], const double (&v2)[2]) {
  double dp{};

  if (std::is_constant_evaluated()) {
    for (int i = 0; i < 2; ++i) dp += v1[i]*v2[i];
  } else {
    constexpr int imm8 = 0b110001;
    asm volatile (
      "movlpd %%xmm0, %1;"
      "movhpd %%xmm0, %2;"
      "movlpd %%xmm1, %3;"
      "movhpd %%xmm1, %4;"
      "dppd %%xmm0, %%xmm1, %5;"
      "movlpd %0, %%xmm0"
      : "=m"(dp)
      : "m"(v1[0]), "m"(v1[1]), "m"(v2[0]), "m"(v2[1]), "N"(imm8)
    );
  }

  return dp;
}


int main()
{
  {
    constexpr double v1[2] = { 2.0, 2.0 }; 
    constexpr double v2[2] = { 2.0, -2.0 };
  
    constexpr double dp1 = inner_product_v2(v1, v2);
    double  dp2 = inner_product_v2(v1, v2);

    std::cout << std::setprecision(16);
    std::cout << dp1 << "\n" << dp2 << std::endl;
  }
  {
    constexpr double v1[2] = { 0.0, 1.0 }; 
    constexpr double v2[2] = { 1.0, 1.4142135623730950488016887242097 };
  
    constexpr double dp1 = inner_product_v2(v1, v2);
    double  dp2 = inner_product_v2(v1, v2);

    std::cout << dp1 << "\n" << dp2 << std::endl;
  }
}

/*
出力
0
0
1.414213562373095
1.414213562373095
*/
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LIIfCl56mxIPUW6K)


### consteval（immediate function : 即時関数）
constexprを指定した関数は定数実行可能であり、定数式の文脈でコンパイル時に実行可能であることを表明します。  
しかし、文脈によっては定数実行されたかどうかを確かめることが困難であったり、定数実行中に実行不可となるようなエラーが発生した場合は暗黙的に実行時まで処理が先延ばしされたりします（単なるconstな変数の初期化試行時等）。

そこで、必ずコンパイル時に定数を生成しそれができなければコンパイルエラーとなる関数が欲しい場合があります。そのような需要に応えるためにconsteval指定子が導入されました。

constevalは関数の頭（constexprと同じ位置）に付け、その関数が必ずコンパイル時実行されることを示します。そして、そのような関数は即時関数（immediate function）と呼ばれます。  
基本的には、consteval関数内でできる事/出来ない事等の性質はconstexpr関数と同じです。

```cpp
consteval int square(int n) {
  return n*n;
}

constexpr int sqc = square(10);   //ok. executed at compile time.
int x = 10;
int sqr = square(x);   //compile error! can't executed at compile time.
```
変数`sqc`の初期化はconstexprが付加されていることもあり定数式で実行可能ですので、`square(10)`はコンパイル時に実行され、`sqc == 100`になります。  
一方`sqr`の初期化では、`square`即時関数の引数が非constexprな変数`x`になっているために即時実行不可なのでその時点でコンパイルエラーを発生させます。  
また、consteval関数内に定数実行不可能な処理がある場合もコンパイルエラーです。

consteval関数はほかのどの関数よりも早く実行され、consteval関数が出現したらほぼその場で実行されます。つまり、constexpr関数実行時点ではその内部のconsteval関数実行は終了しています。  
ただし、consteval関数の中でconsteval関数が呼び出されている場合はそうではなく、そのように囲んでいるconsteval関数が最終的に定数評価されればエラーにはなりません。

```cpp
consteval int sqrsqr(int n) {
  return square(square(n)); //この時点では定数評価されていないが、エラーにはならない
}

constexpr int dblsqr(int n) {
  return 2*square(n); // compile error! 囲む関数はconstevalではない
}
```
つまりはconsteval関数呼び出しが実行時まで残っている可能性のある場合にエラーとなり、実行時には必ず結果となる定数値に置き換えられていなければなりません。

また、consteval関数内にconstexpr関数呼び出しがあっても良いようです。

そのように、コンパイル時には全て終わっているという性質のためconsteval関数のアドレスを取ることは出来ません。そのような行為を働いた時点でコンパイルエラーとなります。  
ただし、consteval関数内で扱われている限りはconsteval関数のアドレスを扱うことができます。

```cpp
consteval int f() { return 42; }
consteval auto g() { return f; } //ok
consteval int h(int (*p)() = g()) { return p(); } //ok

constexpr int r = h();  //ok
constexpr auto e = g(); //compile error! consteval関数のアドレスは定数式として許可されない
```

このような性質から、即時関数はコンパイラのフロントエンドで処理され、バックエンドはその存在を知りません。すなわち、関数形式マクロ（悪名高いWindows.hのmin,maxマクロのようなプリプロセッサ）の代替として利用することができます。

デメリットとしてはテンプレートメタプログラミングと同じでデバッグが困難であることです。constexpr関数であれば通常の関数としてデバッグ可能ですが、consteval関数は実行時には跡形も残りませんので通常の手段ではデバッグできません。

#### constevalコンストラクタ

consteval指定はコンストラクタに行うこともできます。そのようなコンストラクタもまた即時関数となり、そのコンストラクタを通じた初期化は他のconsteval関数と同じタイミング（constexprコンストラクタよりも早い）で行われます。  
コンストラクタに付ける場合に（そのクラスに）必要な要件・制限はconstexpr指定したのとほぼ同じです。

constevalコンストラクタの挙動は通常のconsteval関数と同じです。  
すなわち、その初期化は定数かリテラル型を通して行われなければならず、constexpr関数内で使用される場合はその関数が実行される時点で既に初期化が終了していなければなりません。  
そして、実行時にはそのコンストラクタは残らないため、実行時にconstevalコンストラクタは使用不可能になります。アドレスも取得不可です。

つまりは、constevalコンストラクタのみを持つようなクラスは（consteval関数以外から見ると）定数として振舞い、実行時に生成することができなくなります。

```cpp
struct immediate {
  consteval immediate(int m, double d)
    : n{m}
    , f{d}
  {}

  consteval operator int() const {
    return n;
  }

  consteval operator double() const {
    return f;
  }

private:
  int n;
  double f;
};

consteval auto make_immediate(int m, double d) -> immediate {
  return immediate{m, d};
}

constexpr auto make_immediate2(int m, double d) -> immediate {
  return immediate{m, d};  //ng、この関数はconstevalではない
}

int main() {
  constexpr immediate im1{10, 3.141};  //ok
  constexpr auto im2 = make_immediate(20, 2.718);  //ok

  int n{};
  double d{};
  immediate im3{n, d};  //ng
  auto im4 = make_immediate(n, d);  //ng

  immediate im5 = immediate{30, 1.618};  //ok?、即時生成した一時オブジェクトをムーブする?

  constexpr auto m = int(im1)    + int(im2);     //ok, m == 30
  constexpr auto e = double(im1) + double(im2);  //ok, e == 5.859
  
  std::cout << int(im1)    << ", " << int(im2)    << std::endl;  //ok
  std::cout << double(im1) << ", " << double(im2) << std::endl;  //ok
}
```
この様な`immediate`クラスはもはや実行時にオブジェクトを生成することはできません。ただし、その特殊メンバ関数はconstexprに暗黙定義されており、コピーやムーブは実行時でも可能なはずです（現状では、暗黙定義される特殊メンバ関数はconsteval関数にはなりません）。

その他のメンバ関数にもconstevalをつけることができますが、デストラクタに付けることはできません。

#### constevalラムダ
consteval指定はラムダ式に対しても行えます。その場合、ラムダ式によって生成される暗黙の関数オブジェクトの関数呼び出し演算子がconsteval関数になります。  
付ける位置はmuttableやconstexprと同じ位置です。

```cpp

auto sq = [](auto n) consteval { return n*n; };

constexpr int sqc = sq(10);
//sqc == 100

```
そのほかの性質はconsteval関数に準じます。

consteval指定されるのはあくまで関数呼び出し演算子なので、このラムダ式を受けている変数自体は即時評価される必要はありません。あくまで関数呼び出しが即時評価されます。  
ただし、キャプチャをする場合の変数は定数、もしくはconsteval関数によって初期化されるリテラル型である必要があり、その場合はラムダ式を受けている変数にconstexprが必須になるかもしれません（ラムダ式の生成する関数オブジェクトの初期化がconstevalコンストラクタを通して行われるため）。

consteval関数を持ち回るのに利用すると良いかもしれません。後は通常のローカル関数としての利用でしょうか。

#### consteval仮想関数
仮想関数がconstexpr指定できるようになったので、当然のように？consteval指定することもできます。ただし、constexprが非constexpr仮想関数をオーバーライドしたり出来るのに対して、constevalはconsteval同士の間でしかオーバーライドしたり/されたりしてはいけません。

```cpp
struct polymorphic_base {
  virtual int f() const = 0;
  consteval virtual int g() const { return 0; };
  consteval virtual int h() const { return 1; };
};

struct delived : polymorphic_base {
  //compile error! polymorphic_base::f() is not consteval function.
  consteval int f() const override {
    return 10;
  }

  //ok
  consteval int g() const override {
    return 20;
  }

  //compile error! missing consteval.
  int h() const override {
    return 30;
  }
};
```
オーバーライド前とオーバーライド後でconsteval指定の有無が一致している必要があります。

consteval関数は実行時には跡形もなく消え去るため、consteval仮想関数のみが定義されているようなクラスは実行時には多態的な振舞を行えなくなります。しかし、それでも仮想関数テーブル等の動的ポリモーフィズムのための準備が省かれるわけではありません。

### STLのconstexpr追加対応

#### vector
上記の様々な変更の結果、`std::vector<T>`およびその特殊化`std::vector<bool>`のすべてのメンバ関数にconstexprが付加され、完全にコンパイル時利用が可能になります。ただし当然ながら、要素型はリテラル型である必要があります。

```cpp
constexpr int test_vector() {
  std::vector<int> v = {5, 3, 2, 9, 1, 0, 4};
  v.push_back(11);

  int s{};
  for(auto n : v) {
    s += n;
  }

  return s;
}

constexpr auto sum = test_vector(); //ok. sum == 35
```

#### string
そしてさらに、`std::string`（`char, char8_t char16_t, char32_t`に対して）の全てのメンバも`constexpr`対応を果たし、コンパイル時利用が可能になります。

```cpp
constexpr std::string is_cpp_file(const std::string& filename) {
  return filename.end_with(".cpp") || filename.end_with(".hpp");
}

constexpr std::string is_cpp_file(const std::u8string& filename) {
  return filename.end_with(u8".cpp") || filename.end_with(u8".hpp");
}


constexpr std::string src_name{"main.cpp"};          //ok
constexpr std::u8string header_name{u8"header.cpp"}; //ok

static_assert(is_cpp_file(src_name));     //ok、エラーにならない
static_assert(is_cpp_file(header_name));  //ok、エラーにならない
```

#### cmathとcstdlib
一部の数学関数にconstexprが付加されるようになります。とはいえ、std::sin等の特殊関数がconstexpr実行可能になるわけではありません。  
絶対値（`abs`）や丸め（`ceil, floor, round, trunc`）、剰余（`fmod, remainder, remquo`）等の一部の関数がconstexpr指定されるようになります（[一覧](https://wg21.link/P0533)）。

四則演算はすでにconstexprなので、これで基本的な操作はコンパイル時実行できるようになります。おそらく恩恵が強いのは丸め関数系でしょうか。

#### algorithmとutility
std::swap()やstd::sort()等、かなりの関数にconstexprが付加されるようになります（[一覧](https://wg21.link/P0202R3)）。

これによりstd::vectorも含めて、constexprなイテレータを用いたアルゴリズムをコンパイル時実行できるようになります！

```cpp
constexpr std::vector<char> cvec = {`h`, `e`, `l`, `l`, `o`};
constexpr auto& r = cvec.emplace_back(`.`);

constexpr auto it = std::find(std::begin(cvec), std::end(cvec), `e`);
//*it == `e`

constexpr auto no = std::find(std::begin(cvec), std::end(cvec), `w`);
//no == std::end(cvec)
```

#### `std::invoke`とそれを用いるもの

C++17までは`constexpr`関数をどこで実行すべきかが明確に規定されていなかったために、その実行に関しては処理系に一任されていました。  
そのため、処理系によっては貪欲な定数実行の結果、意図しない文脈で`constexpr`関数が実行され、不明確なコンパイルエラーを引き起こしていました。

`std::invoke`はSTL内での呼び出し可能コンセプトの表現や関数呼び出しの`noexcept`指定、戻り値型推論等に広く用いられており、`constexpr`関数の実行コンテキストが明確でないままに`std::invoke`を`constexpr`にしてしまうとそれらの関数利用時に意図しないコンパイルエラーを引き起こす可能性がありました。  
そのため、`std::apply`等`constexpr`関数の定義でも使用されているにも関わらず`std::invoke`は`constexpr`関数ではありませんでした。

C++20より、`constexpr`関数をどこで評価・実行すべきかを明確にしたこと（P0859R0）によってそれらの問題は払拭され、`std::invoke`は`constexpr`指定されました。  
そしてそしてそれに伴い、`std::invoke`を定義に利用するいくつかのSTL関数も`constexpr`指定されます。

[P0859R0 評価されない文脈でconstexpr関数が定数式評価されることを規定](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)について↓
[https://onihusube.hatenablog.com/entry/2019/03/19/011249:embed:cite]

C++20より`constexpr`指定される関連関数

- `std::invoke`
- `std::reference_wrapper<T>`
  - 全メンバ関数
- `std::ref()`
- `std::cref()`
- `std::not_fn()`
- `std::bind_front()`
- `std::bind()`
- `std::mem_fn()`

#### 全てのメンバ関数のconstexpr化を達成したクラス
- `std::vector`
- `std::string`
- `std::allocator<T>`
- `std::array`
- `std::pair`
- `std::tuple`
- `std::back_insert_iterator`
- `std::front_insert_iterator`
- `std::insert_iterator`


#### 追加のconstexpr対応
- `std::complex`（それぞれ非メンバ関数版を含む）
  - 全ての四則演算の演算子（自己代入系含む）
  - 全代入演算子
  - `real(), imag()`
  - `norm(), conj()`
- `std::pointer_traits<T*>`
  - `pointer_to()`
- `std::char_traits`
  - `move()`
  - `copy()`
  - `assign()`

### 参考文献
- [P1064R0 : Allowing Virtual Function Calls in Constant Expressions](https://wg21.link/P1064)
- [P1327R1 : Allowing dynamic_cast, polymorphic typeid in Constant Expressions](https://wg21.link/P1327)
- [P1328R0 : Making std::type_info::operator== constexpr](https://wg21.link/P1328)
- [P0784R2 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r2.html)
- [P0784R5 : More constexpr containers](https://wg21.link/P0784)
- [P1330R0 : Changing the active member of a union inside constexpr
](https://wg21.link/P1330)
- [P1002R1 : Try-catch blocks in constexpr functions
](https://wg21.link/P1002)
- [P0595 : std::is_constant_evaluated()](https://wg21.link/P0595)
- [P1331R1 : Permitting trivial default initialization in constexpr contexts](https://wg21.link/P1331)
- [P1668R1 : Enabling constexpr Intrinsics By Permitting Unevaluated inline-assembly in constexpr Functions](https://wg21.link/P1668)
- [P1073 : Immediate functions](https://wg21.link/P1073)
- [P1004R1 : Making std::vector constexpr](https://wg21.link/P1004)
- [P0980R0 : Making std::string constexpr](https://wg21.link/P0980)
- [P0533R4 : constexpr for `<cmath>` and `<cstdlib>`](https://wg21.link/P0533)
- [P0202R3 : Add Constexpr Modifiers to Functions in `<algorithm>` and `<utility>` Headers](https://wg21.link/P0202)
- [P1065R2 : constexpr INVOKE](https://wg21.link/p1065)
- [P0415R1 : Constexpr for std::complex](https://wg21.link/P0415)
[P1006R1 : Constexpr in std::pointer_traits](https://wg21.link/P1006)
- [C++20 - cpprefjp](https://cpprefjp.github.io/lang/cpp20.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190226_cpp20_constexpr.md)