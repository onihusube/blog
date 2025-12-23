# C++26 Contracts

C++26では契約プログラミング機能が使用可能になります。この記事はその機能の解説を行うものです。なお、契約プログラミングそのものやその意義などについてはここでは解説しませんので、各自で調べてください。

[:contents]

### 構文

C++26 Contracts機能によって、契約プログラミング（契約による設計）の主要概念である事前条件と事後条件に対応するアサーションとその他のアサーションを専用の構文によってコード中に配置し、関数契約をC++コードの一部として記述できるようになります。このアサーションのことを**契約アサーション（contract assertions）**と呼びます。

契約アサーションには前述の事前条件・事後条件・その他アサーションにして3種類のアサーションがあります。

- `pre()` : 事前条件アサーション
- `post()` : 事後条件アサーション
- `contract_assert()` : アサーション文

3種類のアサーションは基本的には同じ使用法になり、`()`の中には契約条件を表す式を指定します

```cpp
int f(const int x)
  pre (x != 1)  // 事前条件アサーション
  post(r : r == x && r != 2) // 事後条件アサーション
{
  contract_assert(x != 3); // アサーション文

  return x;
}
```

事前条件と事後条件アサーションは関数の宣言の直後（`requires`節が存在する場合、その後）に対して付加し、関数本体の内など他の場所には指定できません。`contract_assert()`は逆に`pre()/post()`の場所には配置できず、文（*statement*）の一種として関数本体ブロック内などの分が配置できる場所に配置することができます。

関数ヘッドの直後（`requires`節が存在する場合、その後）、（定義がある場合は）本体ブロックの直前、が事前条件と事後条件アサーションを配置する専用の構文スペースになります。ここでは、`pre()`と`post()`を空白区切りで任意の個数配置することができます。`pre()`と`post()`の出現順は任意であり、両方あってもどちらか片方だけしかなくてもokです。一方で、他のものはここには配置できません。

```cpp
int f1(int x) pre(x != 1) pre(x != 2) pre(x != 3) ... pre(x != 1000) ...  // ok
{
  ...
}

int f2(const int x) post(x != 1) post(x < 0) pre(x == 0) post(r: r != x)  // ok
{
  ...
}

void f3(int x) contract_assert(x != 0)  // ng、ここに配置できるのはpre()とpost()のみ
{
  ...
}

template<typename T>
void f(T& x) requires std::integral<T> pre(x != 0) post(0 < x)  // ok
{
  ...
}
```

関数に対する事前・事後条件アサーションの指定はフリー関数に限定されたものではなく、メンバ関数でも使用可能です。

```cpp
template<typename T>
struct S {
  T t;

  int f1(int x) pre(x == 0) post(r: x != 0) // ok
  {
    ...
  }

  auto f2() const & noexcept [[attribute]] -> T requires std::integral<T> pre(t != 0) post(r: r < T(0));  // ok

  int f3(this S& self) pre(self.t == 0) post(r: r < 0); // ok
};
```

事後条件アサーションだけは関数の戻り値をキャプチャするための専用の構文スペースが用意されており、`post(ret: expr)`の様に条件式`expr`の前の`ret`の部分に戻り値を指すように任意の名前を指定できます。戻り値を表すこの名前は続く`expr`内で使用することができ、値としてはその関数の戻り値が取得できます。

戻り値の無い（`void`戻り値型の）関数の事後条件アサーションにおける結果名の使用はコンパイルエラーとなります。

```cpp
void f()
  post(r: ...)  // ng、戻り値の無い関数での結果名の指定はコンパイルエラー
{
  ...
}
```

事後条件アサーションにおけるこの結果名は、事後条件アサーションが関連付けられている関数の戻り値のオブジェクト/参照を表す束縛（*result binding*）であり、言語参照（`T&`）とは異なる形の参照の様な名前になります（これは構造化束縛において導入される各束縛の名前と同じ扱いのものです）。そして、結果名の式としての値カテゴリ（`decltype(r)`）は`const`左辺値（`const T&`、`T`は戻り値型）となります。

戻り値への参照ではなく束縛としていることによって、`return`文における暗黙ムーブやRVOの影響をうけなくなっており、結果名はそれらの適用された関数戻り値を直接示しています。

なお、`pre`/`post`は`override`等と同じ文脈依存キーワードであり、`contract_assert`はキーワードとして新規追加されています。そのため、`pre`/`post`は他の名前として使用できる一方、`contract_assert`は使用できません。

```cpp
int pre(const int x)
  pre(x != 1)           // ok
  post(post: post == x) // ok
{
  int contract_assert;  // ng、これはダメ

  ...
}
```

以下、この記事では事前条件アサーションと事後条件アサーションの事を単に事前条件と事後条件と呼びます。

#### 契約アサーションの述語（契約条件式）

アサーションの種類によらず、契約アサーションには何かしら契約条件を表現する条件式を指定する必要があります。この条件式の事を述語（*predicate*）と呼びます。この述語というのはアルゴリズムの文脈などで使用される言葉と同じ意味です。

述語は文脈的に`bool`変換が可能（contextually converted to `bool`）な式である必要がある他は任意のC++式を記述することができます。すなわち、`if`や条件演算子の条件式として使用できるものが使用できます。ただし、後述する`const`化の違いがあります。

```cpp
void f1(int* ptr) pre(ptr)  // ok、ptr != nullptr と等価
{}

void f2(std::optional<int> opt) pre(opt)  // ok、opt.has_value() と等価
{}
```

以下、この記事ではこの述語の事を**契約条件式**と呼ぶことにします。

#### `const`化

3種類いずれの契約アサーションにおいても、その契約条件式内から参照可能な外部の変数はすべて、暗黙的に`const`化されます。

この`const`化は契約条件式の振る舞いがC++の他の部分とかなり異なる点です。これは、契約条件式の評価に伴う副作用の発生を防止するための措置の一つです。

契約条件式には文脈的に`bool`変換が可能であれば任意の式を記述することができます。（`const`化を除いて）それ以外に特に制限は無いため、その条件式を起点として任意のC++コードを実行することができます。プログラムの任意時点の状態をチェックするための契約アサーションからプログラムの状態を変更することは通常間違った行いであるため、これをなるべく防止するためにこの`const`化の措置が取られています。

```cpp
void f() {
  std::vector<bool> vec{true, false};

  contract_assert(vec.emplace_back(true) == true);  // ng、vecはconst
}  
```

この`const`化は契約条件式の外部の変数の使用すべてに対して作用します。関数引数、ローカル変数、グローバル/名前空間スコープの変数、`static`/`thread_local`変数、NTTPや構造化束縛、そして`this`および`*this`まで、あらゆる外部の変数は`const`化されます。事後条件における結果名の値カテゴリが`const`左辺値なのも`const`化の一部です。

```cpp
int n = 0;
struct X { bool m(); };

struct Y {
  int z = 0;

  void f(int i, int* p, int& r, X x, X* px)
    pre (++n)     // ng、const左辺値を変更しようとしている（グローバル変数
    pre (++i)     // ng、const左辺値を変更しようとしている
    pre (++(*p))  // ok、ポインタの参照先には伝播しない
    pre (++r)     // ng、const左辺値を変更しようとしている
    pre (x.m())   // ng、非constメンバ関数呼び出し
    pre (px->m()) // ok、ポインタの参照先には伝播しない 
    pre ([=, &i, *this] mutable {
      ++n;        // ng、const左辺値を変更しようとしている
      ++i;        // ng、const左辺値を変更しようとしている
      ++p;        // ok、コピーキャプチャされたクロージャ型のメンバの変更（ポインタ
      ++r;        // ok、コピーキャプチャされたクロージャ型のメンバの変更（非参照
      ++this->z;  // ok、コピーキャプチャされた*thisの変更
      ++z;        // ok、コピーキャプチャされた*thisの変更
      int j = 17;

      [&]{
        int k = 34;
        ++i; // ng、const左辺値を変更しようとしている
        ++j; // ok
        ++k; // ok
      }();

      return true;
    }());

  template <int N, int& R, int* P>
  void g()
    pre(++N)      // ng、prvalueを変更しようとしている
    pre(++R)      // ng、const左辺値を変更しようとしている
    pre(++(*P));  // ok、ポインタの参照先には伝播しない

  int h()
    post(r : ++r) // ng、const左辺値を変更しようとしている
    post(r: [=] mutable {
      ++r;  // ok、コピーキャプチャされたクロージャ型のメンバの変更
      return true;
    }());

  int& k()
    post(r : ++r); // ng、const左辺値を変更しようとしている
};
```

契約条件式には任意の式を使用できるため、当然ラムダ式が使用できます。契約条件式内ラムダ式内部で宣言された変数（コピーキャプチャも含めて）にはこの`const`化は適用されません。

また、この`const`化は浅いもので、深く伝播することはありません、例えば、外部のポインタを使用しているときそのポインタそのものは`const`化されていますが（`T* const`）、ポインタの参照先（`*ptr`/`ptr->~`）までは伝播しません。

仮に`const`化を解除したい場合は、`const_cast`を使用します。

```cpp
struct S {
  int m_resource;
  std::mutex m_mtx;

  // 非constのステータスチェック
  bool cond() {
    std::lock_guard _{m_mtx};

    return m_resource != 0;
  }

  int f()
    pre(this->cond())                 // ng、非constメンバ関数呼び出し
    pre(const_cast<S*>(this)->cond()) // ok
  {}
}
```

#### 事後条件における関数引数の使用

事後条件から関数引数を使用することは良くありそうですが、その場合に使用する引数は参照であるか、そうでないなら`const`宣言されていなければなりません。非参照の場合、これは暗黙`const`化とは関係なく明示的に`const`と宣言されている必要があります。

```cpp
void f(int a1, const int a2, int& a3)
  post(a1 == 0) // ng。事後条件からの非参照非const引数の使用
  post(a2 == 0) // ok、const引数
  post(a3 == 0) // ok、参照引数
```

これは、事後条件から使用される非参照非`const`関数引数について、どの時点の値をキャプチャすべきか？という問題を回避するためのものです。

例えば次のようなライブラリ関数があるとします

```cpp
// ユーザーが見る宣言
int generate(int lo, int hi)
  pre (lo <= h)
  post(r: lo <= r && r <= hi);
```

この宣言からは、事後条件によって引数`lo, hi`に対して戻り値が`[lo, hi]`の範囲内に収まっていることが明確に読み取れます。しかしこの関数の実装が次のようになっていたとしたらどうでしょうか

```cpp
// 開発者が見る定義
int generate(int lo, int hi)
  pre (lo <= h)
  post(r: lo <= r && r <= hi) // 事後条件からの引数使用に制限がないとする
{
  int result = lo;

  while (++lo <= hi) // loが更新される
  {
    if (further())
      ++result;      // loよりもゆっくりとインクリメントされる
  }
  return result;
}
```

この関数は値渡しで引数を変更しています。これにより、この定義から見る事後条件の意味は全く違ったものになっています。

関数の非参照引数を変更するというのは正気ならやらないとは思われますが、言語が暗黙的にこれを行う場合があります。

```cpp
std::string g(std::string p)
  post (r: starts_with(p))  // 事後条件からの引数使用に制限がないとする
{
  return p; // 引数の暗黙ムーブ
}
```

関数引数は暗黙ムーブの対象であるため、事後条件でそのような関数引数を使用すると意図通りに動作しなくなります。

このように、関数定義内で引数が変更されていると、関数宣言の契約アサーション（特に事後条件）のみから戻り値に対する推論を行うことができなくなります。このことは事前条件では問題にならず（変更前であるため）、事後条件でのみ問題になります。また、引数が参照である（変更されるものであるため）か`const`である場合（変更できないため）も問題になりません。

これを防止するために、事後条件から使用できる関数引数は参照もしくは非参照の`const`なものに限定されています。

#### 宣言と定義が分かれている場合

C++の関数はその宣言と定義を分けて記述することができるほか、宣言だけなら何度も再宣言することができます。この場合にも契約アサーション（事前条件と事後条件アサーション）を指定することはできますが、少し注意が必要です。

関数に対して事前条件と事後条件アサーションを指定する場合、翻訳単位におけるその関数の最初の宣言に対して指定しておかなければなりません。そして、同じ翻訳単位内で続く再宣言は事前条件と事後条件アサーションの指定について次のどちらかを順守する必要があります

- 事前条件と事後条件アサーションを一切指定しない
- 最初の宣言と全く同一の事前条件と事後条件アサーションを指定する

一つの翻訳単位内でこれが満たされない場合、コンパイルエラーとなります。

```cpp
// 最初の宣言
int f(const int x)
  pre (x != 1)
  post(r : r == x && r != 2);

// 有効な再宣言: 事前/事後条件アサーションを持たない
int f(const int x);

// 有効な再宣言: 事前/事後条件アサーションを持つ
int f(const int x)
  pre (x != 1)
  post(r : r == x && r != 2);

// 有効な再宣言（定義）: 事前/事後条件アサーションを持たない
int f(const int x)
{
  contract_assert(x != 3);  // contract_assertは関係ない

  return x;
}

// 不正な再宣言: 異なる事前/事後条件アサーションを持つ
int f(const int x)
  pre (x != 1);     // ng

// 不正な再宣言: 異なる事前/事後条件アサーションを持つ
int f(const int x)
  pre (0 < x)
  post(r: r == 0);  // ng
```

後の宣言で事前条件と事後条件アサーションが指定されていない場合、暗黙的に最初の宣言の事前条件と事後条件アサーションと同一のものが指定されているものとして扱われます。

最初の宣言に事前条件と事後条件アサーションが指定されていない場合、あとの宣言で追加することはできません。

```cpp
// 契約アサーションを持たない関数宣言
int f(const int x);

// 不正な再宣言:  事前/事後条件アサーションが追加された
int f(const int x)
  pre (x != 1)
  post(r : r == x && r != 2); // ng
{
  contract_assert(x != 3);

  return x;
}
```

翻訳単位が複数ある場合、ある関数に対応する最初の宣言は翻訳単位毎に1つづつ存在しえます（このような状況はヘッダファイルに契約アサーションを持つ関数の宣言を記述して、そのヘッダを複数のソースファイルでインクルードした時に起こります）。ある関数に対応するそのような複数の最初の宣言の間で同一の事前条件と事後条件アサーションが指定されていない場合、診断不要のill-formed（IFNDR）となります。

```cpp
/// 翻訳単位1におけるf()の宣言
int f(const int x)
  pre (x != 1)
  post(r : r == x && r != 2);

/// 翻訳単位2におけるf()の宣言
int f(const int x)
  pre (x != 1)
  post(r : r == x && r != 2); // ok

/// 翻訳単位3におけるf()の宣言
int f(const int x); // IFNDR、契約アサーションの指定がない
```

IFNDRは診断されない、すなわちコンパイルエラーとなることを要求されていないため、未定義動作となります。これはODR違反が起きているのとほぼ同じことです。ここでの翻訳単位には共有ライブラリの様なものも当然含まれます。

これらのルールを理解したうえで問題となるのは、事前条件と事後条件アサーションの同一性の定義です。契約アサーションは何をもって同一と言えるのでしょうか？

ある2つの事前/事後条件アサーションのシーケンスは次の場合に同一とみなされます

1. 同一の契約アサーション指定（1つの`pre(...)`/`post(...)`）が
2. 同じ順序で指定されている

この一つの契約アサーション指定の同一性は、ODRの意味での同一です。これは、関数宣言`d1`と`d2`がありそれぞれ契約アサーション指定`c1`と`c2`（この`c1. c2`は単一の`pre(...)`/`post(...)`）を持っているとき、その述語`p1`と`p2`は、宣言`d1`と`d2`に対応する仮想的な関数本体に配置されコンパイルされたときにODRに違反しない、場合にODRの意味で同一となります。すなわち、この時に仮想的な`d1, d2`の定義が異なっていない状態の場合に、契約アサーション指定`c1`と`c2`は同一となります。

このODRの同一性をより具体的に言えば、この仮想的な`d1, d2`がビット単位で全く同じ機械語コードにコンパイルされる場合、がODRの意味で同一と言えます（最適化の事は考えないでください）。したがって、異なる翻訳単位にある時でも、同じ関数に指定された事前/事後条件アサーションが参照する変数や関数等は同じものにならなければなりません。

一方で、関数引数の名前やテンプレートパラメータ名、事後条件における結果名、などはODR同一性においては考慮されないため、異なっていても問題ありません（これは通常の関数のODRよりも緩いルールです。通常の`inline`関数や関数テンプレートでは、字句的に同一であることが求められます）。

```cpp
/// 翻訳単位1におけるf()の宣言
int f(const int x)
  pre (x != 1)
  post(r : r == x && r != 2);
  
/// 翻訳単位2におけるf()の宣言
int f(const int y)
  pre (y != 1)
  post(b : b == y && b != 2); // ok
  
/// 翻訳単位3
static int x = 0;

/// 翻訳単位3におけるf()の宣言
int f(const int a)
  pre (x != 1)
  post(r : r == x && r != 2); // IFNDR、翻訳単位1と2の契約アサーションと同一ではない
  
/// 翻訳単位4におけるf()の宣言
int f(const int y)
  post(b : b == y && b != 2)
  pre (y != 1);               // IFNDR、順番が異なる
```

この同一性の違反は翻訳単位が同じであればチェックされてコンパイルエラーとなります。

##### 事前条件と事後条件アサーションにおけるラムダ式の使用

ラムダ式がリンケージを必要とする場所（関数宣言付近）に現れる場合、そのクロージャ型は必ず固有のものになるというルールがあります。これと契約アサーション指定の同一性のルールによって、事前条件と事後条件アサーションでラムダ式が使用されている場合は同じ翻訳単位内で全く同じ文字列によって再宣言していたとしても（仮に契約アサーション指定を省略したとしても）、同一性を満たすことができません

```cpp
// 同じ翻訳単位内にあっても
void f() pre([]{ return true; }()); // ok、最初の宣言
void f() pre([]{ return true; }()); // ng、最初の宣言の契約アサーションと同一ではない
void f();                           // ng、最初の宣言の契約アサーションと同一ではない
```

このような場合でも再宣言をしなければ事前条件と事後条件アサーションでラムダ式を使用することに問題はありません。

ラムダ式のこのような性質についてはC++20 P0351R4のこの解説を参照してください

- [C++20 評価されない文脈でのラムダ式 [P0315R4] - cpprefjp](https://cpprefjp.github.io/lang/cpp20/wording_for_lambdas_in_unevaluated_contexts.html)

##### 事後条件での関数引数の使用

事後条件で関数引数を使用するにはその引数が非参照なら`const`である必要があるというのはもう説明したことです。これは単に事後条件が存在する場合のみ`const`にしておけばいいのではなく、すべての宣言において`const`でなければなりません。通常の関数宣言では、値引数の`const`有無は関数宣言のマッチングにおいて考慮されないため、少し注意が必要です。

```cpp
void f1(int n);
void f1(const int n); // ok、f1()の再宣言

void f1(const int n) post(r: r == n);
void f1(int n);   // ng、事後条件で使用している引数が（非参照）非const
```

再宣言において事前条件と事後条件アサーションが省略された場合、最初の宣言と同一の契約アサーション指定がなされているとみなされるため、後の宣言でも事後条件で使用している引数に`const`が必要です。

これはここまでで懇々と説明してきたODR同一性とは少し関係がないことですが、契約アサーション付き関数の再宣言においては注意すべきことです。

### 評価セマンティクス

#### 4つのセマンティクス

#### 評価の順序

戻り値の構築 -> 関数引数の破棄

事後条件の評価 -> 関数引数の破棄

#### 条件式の評価回数

#### 例外

#### 定数式

#### Not Part of the Immediate Context

### 違反ハンドラ

違反ハンドラそのものにもpre/postを指定できる

#### `<contracts>`

### 特殊な関数等に対する契約アサーションの扱い

#### 仮想関数

#### ラムダ式

#### コンストラクタ/デストラクタ

> if the unqualified function call appears in a precondition assertion of a constructor or
> a postcondition assertion of a destructor and overload resolution selects a non-static
> member function, the call is ill-formed;

#### コルーチン

```
When a function is defined to be a coroutine, its parameters may be modified even if they are
declared const by the user on all declarations of the function. The reason is that the coroutine
initializes copies of the parameters in the coroutine frame with modifiable xvalues referring to the
original parameters, ignoring any const qualification on those original parameters,8 which means
that such parameters may be moved from. Therefore, if a function parameter is odr-used by a
postcondition-assertion predicate and that function is defined to be a coroutine, the program is
ill-formed, even if that parameter is declared const on all declarations written by the user.
```

コルーチン事後条件からの関数引数使用は禁止。

#### 関数ポインタ

#### `main()`

`main()`関数にも事前条件と事後条件を指定することができます。

```cpp
int main(int argc, char *argv[])
  pre(2 < argc)
  post(r: r != 0)
{
  ...

  return 10;
}
```

評価等のルールにも特別なところはなく、通常の関数と同じように扱われます。

この例のようにプログラム引数に対して使用する以外にも、`main()`呼び出し前（あるいは終了前）のプログラムのより大域的な状態を検査するのにも使用できます。

### その他

#### 未定義動作とObservable Checkpoints

#### Contractsと例外

#### `assert`マクロとの関係

### C++29以降の展望

### 反対意見について

### 参考文献

- [P2900R14 Contracts for C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p2900r14.pdf)
- [P2899R1 Contracts for C++ - Rationale](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2025/p2899r1.pdf)
- [P3819R0 Remove `evaluation_exception()` from contract-violation handling for C++26](https://open-std.org/jtc1/sc22/wg21/docs/papers/2025/p3819r0.pdf)
