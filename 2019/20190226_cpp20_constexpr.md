# ［C++］さらに出来るようになったconstexpr（C++20）

※この内容はC++20から利用可能な情報であり、一部の変更はC++23以降に先延ばしになるなど、内容が変更される可能性があります。

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
この様なコードが動くようになるはずです（おそらく）。

このコードのように、非constexprな仮想関数をconstexprな仮想関数でオーバーライドすることができますし、その逆（constexpr仮想関数を非constexpr仮想関数でオーバーライド）も可能です。  
また、const修飾はしておかないと実行時に呼び出すことができなくなります（constexprに初期化された変数は実行時にはconstになっているため）。

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

### dynamic_castとtype_id
前項の内容の延長です。constexprな仮想関数が許可されたのと同様の理由により`dynamic_cast`や`type_id`も静的に解決することができます。なのでそれが可能になりました。  
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

  constexpr bool is_same = int_t == char_t;  //is_same == false
}

//polymorphicな型に対するtypeid
{
  constexpr derived1 d1{};
  constexpr derived2 d2{};
  
  constexpr base const* b1 = &d1;
  constexpr base const* b2 = &d2;
  
  constexpr auto&& b1_t = typeid(b1);
  constexpr auto&& b2_t = typeid(b2);

  constexpr bool is_same = b1_t == b2_t;  //is_same == false
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
constexpr int* nullp = nullptr;
constexpr auto&& t = typeid(nullp);  //compile error! 例外を投げるため定数実行不可

constexpr derived1 d1{};
//b1のmost derived typeはderived1
constexpr base const& b1 = d1;
//down cast
constexpr derived2 const& d2 = dynamic_cast<derived2 const&>(b1);  //compile error! 例外を投げるため定数実行不可

```
### STLコンテナのconstexpr化のために
※この項は複雑で長くなるのでページ分けして後程追記します。

ざっとまとめると以下が可能になります

- constexpr デストラクタ
- new式/delete式のコンパイル時実行（operator newではない）
- `std::allocator<T>`及び`std::allocator_traits<std::allocator<T>>`のコンパイル時実行
- コンパイル時に確保され解放されなかったメモリは静的記憶域に移行され実行時に参照可能


### unionのアクティブメンバの切り替え
共用体（union）のアクティブメンバとは、ある時点の共用体のオブジェクトにおいて最後に初期化されたメンバの事です。共用体の初期化自体はconstexprに行うことが可能ですが、あるメンバの初期化後に別のメンバを初期化した場合にアクティブメンバの切り替えが発生します。アクティブメンバの切り替えはC++17までコンパイル時に行えません。

前項の変更によってコンパイル時にメモリ確保すら可能になるため、STLの多くのクラスをconstexpr対応させることができるようになります。しかし、`std::string`や`std::optional`はその実装において共用体が使われています（`std::string`はsmall-string optimization : ssoと呼ばれる最適化のために）。

それらのクラスでは共用体のアクティブメンバの切り替えが発生する可能性があり、その場合にconstexprの文脈で使用できなくなります。そのようなクラスをconstexprにさらに対応させるため、この制限は撤廃されることになりました。

```cpp
union U {
  int n;
  float f;
};

//U::fを読み出しアクティブメンバをU::nに切り替える
constexpr float change(U& u) {
  float f = u.f;  //u.nがアクティブメンバの場合はここが定数実行不可
  u.n = 0;  //u.nへアクティブメンバを切り替え、C++17までは定数実行不可
  return f;
}

//fをアクティブメンバとして初期化 (Designated Initialization!)
U u = { .f = 1.0f };
constexpr auto f = change(u);
```

ただし、非アクティブなメンバへのアクセス（そこへの参照からの間接アクセスも含む）は未定義動作であり、定数式で現れてはいけません。つまりは定数式の文脈でそのようなアクセスを行った時点でコンパイルエラーを引き起こします（`std::string`のsso実装がこれに当てはまるようです）。


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

また、通常の`if`を使うという事は`true`及び`false`となる両方のステートメントがコンパイル出来なければなりません。同時に、実行時に選択される方のステートメントでもconstexpr関数で現れてはいけない構文が現れてはいけません（例えば、`throw`や`goto`、`reinterpret_cast`）。


### consteval（immediate function : 即時関数）
constexprを指定した関数は定数実行可能であり、定数式の文脈でコンパイル時に実行可能であることを表明します。  
しかし、文脈によっては定数実行されたかどうかを確かめることが困難であったり、定数実行中に実行不可となるようなエラーが発生した場合は暗黙的に実行時まで処理が先延ばしされたりします（単なるconstな変数の初期化試行時等）。

そこで、必ずコンパイル時に定数を生成しそれができなければコンパイルエラーとなる関数が欲しい場合があります。そのような需要に応えるためにconsteval指定子が導入されました。

constevalは関数の頭（constexprと同じ位置）に付け、その関数が必ずコンパイル時実行されることを示します。そして、そのような関数は即時関数と呼ばれます。  
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
一方、`sqr`はconstexprではなく別の非constexprな変数`x`を介していることもあり、constexpr実行不可能なのでその時点でコンパイルエラーを発生させます。  
また、consteval関数内に定数実行不可能な処理がある場合もコンパイルエラーです。

consteval関数はほかのどの関数よりも早く実行されます。すなわち、constexpr関数の実行時点にはconsteval関数の実行は終わっていなければなりません。  
ただし、consteval関数の中でconsteval関数が呼び出されている場合はそうではなく、そのように囲んでいるconsteval関数が最終的に定数評価されればエラーにはなりません。

```cpp
consteval int sqrsqr(int n) {
  return sqr(sqr(n)); //この時点では定数評価されてないが、エラーにはならない
}

constexpr int dblsqr(int n) {
  return 2*sqr(n); // compile error! 囲む関数はconstevalではない
}
```

コンパイル時には全て終わっているという性質のため、consteval関数のアドレスを取ることは出来ません。そのような行為を働いた時点でコンパイルエラーとなります。  
また、コンストラクタに付けることは出来ますがデストラクタには付けることはできません。コンストラクタに付けた場合はconstexpr指定したのとほぼ同じ意味になります。

この即時関数はコンパイラのフロントエンドで処理され、バックエンドはその存在を知りません。すなわち、関数形式マクロ（悪名高いWindows.hのmin,maxマクロのようなプリプロセッサ）の代替として利用することができます。

デメリットとしてはテンプレートメタプログラミングと同じでデバッグが困難であることです。constexpr関数であれば通常の関数としてデバッグ可能ですが、consteval関数は実行時には跡形も残りませんので通常の手段ではデバッグできません。

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

consteval関数はアドレスを取れないことから関数ポインタなどで持ち回れないので、可搬にするのに利用すると良いかもしれません。  
後は通常のローカル関数としての利用でしょうか。

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
  std::vector<double> v = {5, 3, 2, 9, 1, 0, 4};
  v.push_back(11);

  int s{};
  for(auto n : v) {
    s += n;
  }

  return n;
}

constexpr auto sum = test_vector(); //ok. sum == 35
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

#### 全てのメンバ関数のconstexpr化を達成したクラス
- `std::vector`
- `std::array`
- `std::pair`
- `std::tuple`
- `std::back_insert_iterator`
- `std::front_insert_iterator`
- `std::insert_iterator`


#### 追加のconstexpr対応
- `std::complex`（非メンバ関数版も含む）
  - 四則演算の演算子（自己代入系含む）
  - 代入演算子
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
- [P1073 : Immediate functions](https://wg21.link/P1073)
- [P1004R1 : Making std::vector constexpr](https://wg21.link/P1004)
[constexpr for `<cmath>` and `<cstdlib>`
](https://wg21.link/P0533)
- [P0202R3 : Add Constexpr Modifiers to Functions in `<algorithm>` and `<utility>` Headers](https://wg21.link/P0202)
- [P0415R1 : Constexpr for std::complex](https://wg21.link/P0415)
[P1006R1 : Constexpr in std::pointer_traits](https://wg21.link/P1006)
- [C++20 - cpprefjp](https://cpprefjp.github.io/lang/cpp20.html)