# ［C++］ autoによるキャスト

C++23から`auto(x)`の形式のキャストが可能になります。

```cpp
template<std::copy_constructible T>
void f(T x) {
  T p = auto(x);  // ok、C++23から
}
```

これに関連する仕様等のメモです。

[:contents]

### prvalue値へのキャスト

`auto(x)`の形式のキャストは`x`をその型を`decay`した型の値としてキャストするものです。

型の`decay`とはその型からCV/参照修飾を取り除き、配列/関数はそのポインタに変換するものです。配列/関数以外の場合、`auto`によるキャストは`x`をその型の*prvalue*へキャストします。

そして、`auto(x)`のキャストは単なる型変換ではなく、キャスト結果の*prvalue*は`x`の値をコピーしたものになります。したがって、その結果は`x`とは異なるオブジェクトとして得られ、`x`の状態を変更しません（コピーコンストラクタが変なことしない限り）。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // auto(x)式の値カテゴリはprvalue
  static_assert(std::same_as<decltype(auto(x)), T>);

  // pとxは異なるオブジェクト（コピーされる）
  T p = auto(x);

  // auto(x)後もxの利用は安全
  x.use();

  // pに変更を加えてもxには波及しない
  p.mutate();

  // auto(x)は同じオブジェクトに対して何度も行える
  T p2 = auto(x);
}
```

```cpp
auto f(int) -> std::size_t;

int main() {
  int a[5]{};

  // 配列型、関数型の場合は対応するポインタ型のprvalueへキャスト
  auto* p1 = auto(a);
  auto* p2 = auto(f);
}
```

コピーを行うため、`T`は`copy_constructible`である必要があります。`move_constructible`でしかない場合はキャストは失敗しコンパイルエラーとなります。

```cpp
struct no_copy {
  no_copy() = default;
  no_copy(const no_copy&) = delete;
};

int main() {
  non_copy nc{};

  non_copy cp = auto(nc); // ng
}
```

また、`auto(x)`だけでなく`auto{x}`も有効であり、どちらも同じ効果になります。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // どちらも同じprvalueへのキャスト
  T p1 = auto(x);
  T p2 = auto{x};
}
```

### 細かい仕様の話

`auto(x)`の形式のキャストは明示的型変換（関数スタイルキャスト）の一種であり、型名の代わりに`auto`を使用するものです。この場合に使用可能なのは丁度`auto`のみで、`decltype`や`auto&`、`const auto&`だとかは使用できません。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // すべてコンパイルエラー
  decltype(x);
  decltype(auto)(x);
  auto&(x);
  auto&&(x);
  const auto&(x);
}
```

`auto(x)`の形式のキャストにおいては`auto`は他の所と同じくプレースホルダ型として扱われており、その型は`x`の型が推論された後で置き換えられます。その推論においては通常の`auto`の推論と同様に、単一のテンプレートパラメータをもちそのテンプレートパラメータ型の引数を1つだけ受ける関数テンプレートに対して`x`を渡した時にそのテンプレートパラメータに推論される型が取得されます。

```cpp
// これらのautoに推論される型は
auto c = x;
auto(x);
auto f() { return x; }

// このような関数テンプレートに対して
template<typename T>
void hf(T);

// xをそのまま渡した時のTに推論される型として取得される
hf(x);
```

この場合の推論時に行われる`x`の型から修飾を取り除いたりポインタ型に変換したりといった調整を型に対する`decay`と呼び、結果の型は`std::decay_t<decltype((x))>`で得られる型と一致します。これは、配列型・関数型以外の場合は元の型に対して*prvalue*になります。

こうして取得された型を`T`とすると、`auto(x)`のプレースホルダ`auto`はこの型`T`で置き換えられ、`T(x)`として通常の関数スタイルキャストとして処理されます。この式は`x`をコピーして`T`の新しいオブジェクトを構築する式となります。これは`auto{x}`においても同様です。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // この4つは実は同じ意味
  auto(x);
  T(x);
  auto{x};
  T{x};
}
```

`auto`を用いたキャストにおいては、`{}`の中の初期化式は1つだけでないとその型が推論できないため渡せる式は1つに限定され、`()`の場合はカンマ区切りの式とみなされやはり渡せる式は1つだけになります。また、推論の仕様上取得される型は`x`と修飾だけが異なる同じ型となるため、大きな型変換は起こりません。したがって、`()`と`{}`の違い（式の評価順序や縮小変換の禁止など）はここでは顕在化せず両方は真に同じ意味を持ちます。

文法上`auto(x), auto{x}`の`x`には任意の式を渡すことができ、意味論的にも制限がないため、`auto`によるキャストは必ずしも変数名のみに対して作用するわけではありません。とは言え、何が渡されたとしてもやることは変わらず、与えられる式の結果をその型の*prvalue*値へキャストすることです。

```cpp
auto f() -> std::string;
auto g() -> const std::string&;

int main() {
  std::vector vec = {1, 2, 3, 4};

  auto v1 = auto(vec);  // ok、コピー
  auto v2 = auto(std::move(vec)); // ok、ムーブ
  auto s1 = auto(f());  // ok、コピー省略
  auto s2 = auto(g());  // ok、コピー
}
```

`auto(x)`の`x`が右辺値の場合はコピーではなくムーブされて結果が生成されます。さらに、`x`が*prvalue*の場合はコピー省略によって`auto(x)`ではコピーもムーブも発生しません（受けている変数が非参照ならば、そこに直接構築される）。

### 利点や用途

前述のように、`auto(x)`は`x`の素の型`T`に対して`T(x)`と同じ意味になります。さらに、`auto(x)`によるコピーは`auto var = x;`のような変数宣言でも同じことを達成できます。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // この4つは実は同じ意味
  auto(x);
  T(x);
  auto{x};
  T{x};

  // 次の3つの宣言は同じことを行う
  auto v1 = auto(x);
  auto v2 = x;
  T v3 = x;
}
```

とすると、`auto(x)`のキャストは冗長で無価値なものにしか見えなくなります。

`auto`キャストが有用なのは、上記のように`T`が素直に得られず、一時変数を作る必要がない場合においてです。

例えばコンテナをテンプレートで受け取って、その先頭要素と同じ値をコンテナから削除したい場合を考えます。

```cpp
// front()が呼べるコンテナコンセプト
template<typename C>
concept container = 
  std::ranges::forward_range<C> and
  requires(C& c) {
    {c.front()} -> std::same_as<std::ranges::range_reference_t<C>>;
  };

// コンテナから先頭要素と同じ要素を削除する
void pop_front_alike(container auto& x) {

  // 先頭要素が削除された後、3番目の引数はダングリング参照となる
  std::erase(x.begin(), x.end(), x.front());

  // 予め先頭要素をコピーしておいて、それを使う
  auto tmp = x.front();
  std::erase(x.begin(), x.end(), tmp);

  // 1行で書こうとすると面倒・・・
  using T = std::decay_t<decltype(x.front())>;
  std::erase(x.begin(), x.end(), T(x.front()));
}
```

`.front()`は要素への参照を返し、`std::erase()`の第3引数は要素型の`const`参照を受け取ります。そのため、`std::erase()`の第3引数に`x.front()`を直接渡すと先頭要素が削除された後（つまり処理が開始されてすぐ）にその参照はダングリング参照となり、UBです。それを回避するためには、先頭要素を予めコピーしてから`std::erase()`に渡すことが必要となります。

ここでは、コピーしてる変数`tmp`はその後使うことはないため一時変数は導入しない方が望ましく、要素型`T`は直接的に見えていないため取得が面倒になります。

そこで、`auto(x)`を使用すると、それらの懸念を解消しつつ同じことをよりシンプルに記述できます。

```cpp
// コンテナから先頭要素と同じ要素を削除する
void pop_front_alike(container auto& x) {
  // auto(x)を使う
  std::erase(x.begin(), x.end(), auto(x.front()));
}
```

前述のように、`auto(x.front())`は`x.front()`の結果をdecayしてコピーした新しいオブジェクトの*prvalue*を返します。`std::erase()`の実行によってコピー元音オブジェクトが削除されても、`auto(x.front())`でコピーされたオブジェクトには何の影響もありません。なお、`auto(x.front())`で渡したオブジェクトは`std::erase()`の呼び出しが終わるまで有効であり、この場合に生存期間の問題は発生しません。

また、`T`の名前が5文字以上の場合（おそらく多くの場合はそうなるでしょう）なら文字数のアドバンテージを得ることができます。さらに言えば、目が慣れれば`T(x)`よりも`auto(x)`の方が一貫性が高くその意図が明確になるでしょう。

```cpp
class very_long_name_my_class {
  ...
};

auto f(const auto&) {
  ...
}

int main() {
  very_long_name_my_class v{};
  int n = 10;
  long double l = 1.0;

  // vをコピーしてfに渡したい場合
  f(very_long_name_my_class(v));
  f(int(n));
  f(long double(l));  // ng

  f(auto(v));
  f(auto(n));
  f(auto(l)); // ok
}
```

```cpp
struct my_class {
  my_class(const my_class&) noexcept(...) {
    ...
  }

  my_class& operator=(my_class&&) noexcept {
    ...
  }

  my_class& operator=(const my_class& other) noexcept(std::is_nothrow_copy_constructible_v<my_class>) {
    if (this == &other) {
      return *this;
    }

    // コピーしてムーブ代入することで実装する
    auto copy = other;
    *this = std::move(copy);

    // あるいは
    *this = my_class(other);

    // auto(x)
    *this = auto(other);

    
    return *this;
  }
}
```

### decay-copyとの違い

`auto(x)`の行うようなコピーは規格書中では`decay-copy`という用語でよく知られており、対応する説明専用のライブラリ関数も用意されています。

```cpp
// 実際の名前はdecay-copy
template<class T>
constexpr decay_t<T> decay_copy(T&& v) noexcept(is_nothrow_convertible_v<T, decay_t<T>>)
{
  return std::forward<T>(v);
}
```

```cpp
template<std::copy_constructible T>
void f(T x) {
  auto v1 = auto(x);
  auto v2 = decay_copy(x);  // これではダメなの？
}
```

`auto(x)`のような構文を新たに導入せずとも、この関数を標準化すれば同じことは達成できるように思えます。そうしないのは、`auto(x)`と`decay_copy(x)`では前者がキャスト式となり後者は関数呼び出し式となることから、その振る舞いに違いがあるためです。

まず1つ目の違いは、`decay_copy(x)`は`x`が*prvalue*である場合にその引数で*prvalue*が実体化されてしまいコピー省略を妨げる点です。`auto(x)`の場合はこれ自体が*prvalue*の式であるため`x`が*prvalue*である場合はコピー省略によって一切のコンストラクタ呼び出しを伴いません（というか何もしません）。

```cpp
auto f() -> std::string;

int main() {
  std::string s1 = auto(f());       // コピー省略によって、s1はf()のreturn文の式から直接構築される
  std::string s2 = decay_copy(f()); // s2はf()の戻り値からムーブコンストラクタによって構築される
}
```

2つ目の違いは、クラス型のプライベートへのアクセスが可能なコンテキストで`decay_copy()`はそのコンテキストを引き継げない点です。

```cpp
class A {
  int x;

public:
  A();

  auto run() {
    f(A(*this));           // ok
    f(auto(*this));        // ok
    f(decay_copy(*this));  // ng
  }

protected:
  A(const A&);
};
```

この場合の`decay_copy(*this)`で実際に`A`のコピーコンストラクタが呼ばれるのは、`decay_copy()`の定義内の`return`文においてであり、`decay_copy()`は`A`の`friend`ではないためそこからは`protected`である`A`のコピーコンストラクタにアクセスできません。

`auto(*this)`は単なる式であるため、コピーが発生するのはその直接のコンテキストである`A::run()`の定義内であり、そこからは問題なく`A`のコピーコンストラクタにアクセスできます。

この例は直接的ですが、`friend`を介すると別のクラスのコンテキストにおいても同様の違いが観測されます。

```cpp
class S;

class A {
public:
  A() = default;

private:
  A(const A&);

  friend S;
};

class S {
public:
  S() = default;

  void f(A& a) {
    auto ca1 = auto(a);       // ok
    auto ca2 = decay_copy(a); // ng
  }
};
```

### 規格書における置き換え

前述のように、規格書においては以前から`auto(x)`とほぼ同等の意味合いで`decay-copy`という用語が使用され、また説明専用の関数が使用されていました。この機能のもう一つの目的としてはそれらを置き換えることで規格書の記述をシンプルにすることも含まれています。

ただし、単に`decay-copy`と書かれていてもその意図が微妙に異なっているらしく、`auto(x)`とは異なり`x`が*prvalue*の場合でもコピーを行うこと（*prvalue*を実体化させること）を意図した場合があるようです。そのため、機械的な置き換えではなく、その微妙な意図を汲み取った上で`auto(x)`と同じ意味で`decay-copy`が使用されている場所についてのみ置き換えを行なっています。次の表はその大まかな分類と方針をまとめたものです

|規格表現|C++20の例|C++23からの例|
|---|---|---|
|特定の式を指定した`decay-copy`|`decay-copy(begin(t))`|`auto(begin(t))`|
|特定の式を指定しない`decay-copy`|`decay-copy(E)`|変更なし|
|`decay-copy`の評価結果についての説明|`decay-copy`の呼び出しはコンストラクタを呼び出したスレッドで評価される|`auto`によって生成された値はコンストラクタを呼び出したスレッドで実体化される|

表中の規格文章は一例で、それぞれ`ranges::begin`、`std::thread`のコンストラクタにおけるものです。

正直こんなニュアンスわかるはずもありませんが、今後は`auto(x)`が使用されている場所は*prvalue*の実体化を意味しないコピーであり、引き続き`decay-copy`が使用されている場所はそうではない、と思うことができます。

### コンセプト定義における利用例

少し変わった使用法になりますが、この機能はコンセプトの戻り値型制約において役立つ場合があります。

例えば、コンセプトにおいて何か呼び出し可能な型をチェックする際に、その戻り値型を特定の1つの型に指定したい場合を考えます。

```cpp
// Fは引数なしで呼び出し可能であり、bool型を返してほしい
template<typename F>
concept returning_bool = 
  std::invocable<F> and
  requires(F& f) {
    {f()} -> std::convertible_to<bool>; // bool型を返すという意味になっていない
  };
```

この場合に要求したいことが、「`f()`の戻り値型が`bool`型そのものであってほしいが別に修飾（`&`や`&&`）はついていても構わない。ただし`bool`以外の型は遠慮してほしい」だった場合、`std::convertible_to<bool>`ではその要求を表現できていません。なぜなら、`std::convertible_to<bool>`だと`bool`に変換可能な型であればOKという意味になってしまっているからです。例えば、ポインタ型を返す引数なしの関数は全てこの制約をパスしますが、それは明らかに意図するところではないでしょう・・・

`std::same_as`を使うとちょうど`bool`型のみという制約になりますが、これだと今度は少し厳しくなります。

```cpp
template<typename F>
concept returning_bool = 
  std::invocable<F> and
  requires(F& f) {
    {f()} -> std::same_as<bool>; // bool&などが弾かれる
  };
```

この戻り値型制約（および他のところでコンセプトの第一引数の自動補完が働く場所）においては、コンセプトの第一引数には`decltype((expr))`が充てられます。例えば上記の場合、`std::convertible_to<decltype((f())), bool>`という制約がチェックされますが、`decltype((expr))`で取得していることによって`expr`の値カテゴリの情報が含まれることになります。

この場合にその修飾情報を無視した素の型をチェックするのは意外に難しく（`decay_t`したり`remove_cvref_t`したりする必要がある）、戻り値型制約の利用は諦めざるを得なくなります

```cpp
template<typename F>
concept returning_bool = 
  std::invocable<F> and
  std::same_as<std::remove_cvref_t<std::invoke_result_t<F>>, bool>; // ようやくほぼ意図通りになる
```

これは目を凝らさないと何してるのかわからないものがあり、戻り値型制約と比べると可読性に劣り、書くのもの大変面倒です。

このような場合に`auto(x)`を使用すると、型の`decay`（`std::remove_cvref_t`）を式としてスマートに記述することができます。

```cpp
template<typename F>
concept returning_bool = 
  std::invocable<F> and
  requires(F& f) {
    {auto(f())} -> std::same_as<bool>; // 修飾を無視して戻り値型がboolであること！
  };
```

もちろん、`auto(x)`によって戻り値のコピーが入る場合があるので若干制約の意味は異なることになるのでその点に注意が必要ではありますが、`invoke_result_t`を`remove_cvref_t`してのような謎の呪文を書かなくても、同じことを戻り値型制約の構文の範囲内で表現可能になります。

このことは、上記`f()`のような関数呼び出し式だけでなく任意の式においても有用となるでしょう。個人的には、本来の用途よりもこちらの用法の方がよく使いそうな気がしています。

### 参考文献

- [P0849R8 `auto(x)`: decay-copy in the language](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p0849r8.html)
- [`std::decay` - cpprefjp](https://cpprefjp.github.io/reference/type_traits/decay.html)
- [`decay-copy` - cpprefjp](https://cpprefjp.github.io/reference/exposition-only/decay-copy.html)
- [C++20 コンセプトで、特定の戻り値の型を持つメンバ関数を持つことを要求するにはどのようにすべきですか？ - スタック・オーバーフロー](https://ja.stackoverflow.com/questions/74200/c20-コンセプトで-特定の戻り値の型を持つメンバ関数を持つことを要求するにはどのようにすべきですか)
- [複合要件とsame_as/convertible_toコンセプト - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20200825/p1)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2023/20230922_cpp23_auto_decay_copy.md)
