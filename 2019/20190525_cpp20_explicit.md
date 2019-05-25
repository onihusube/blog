# ［C++］explicit(bool)の使いどころ

※この内容はC++20から利用可能になる予定の情報であり、一部の内容が変更される可能性があります。

### `explicit(bool)`指定子

従来コンストラクタと変換関数に付けることのできていた`explicit`指定子は
、C++20より`explicit(expr)`という形のものに置き換えられます。  
かっこの中の`expr`に指定出来るのは`bool`に変換可能な定数式です。

そして、その`expr`が`true`となる場合はそのコンストラクタ（変換関数）はexplictコンストラクタになり、`false`となる場合は通常の非explicitコンストラクタとして扱われます。

また、従来の式を指定しない`explicit`指定は`explicit(true)`として扱われるようになります。

### データメンバ型のexplicit性継承

ではこの`explicit(bool)`指定子、一体何が嬉しいのでしょうか？  

それを知るために、以下のようにテンプレートによって任意の型を保持するようなクラスを考えてみます。

```cpp
template<typename T>
struct unit {

  //Tに変換可能なUから構築
  template<typename U=T>
  constexpr unit(U&& other)
    : value(std::forward<U>(other))
  {}

  T value;
};
```

とりあえず最小限のコンストラクタをそろえておきます。  
最小限であるとはいえこれで目的を達することができ、特に問題は無いように思えます。

そこで、この`unit`型に`explicit`コンストラクタを持つ型を入れてみましょう。

```cpp
struct has_explicit_ctor {
  explicit has_explicit_ctor(int) {}
};

int main() {
  has_explicit_ctor s1{1};     //ok、直接初期化（明示的コンストラクタ呼び出し）
  has_explicit_ctor s2 = {2};  //ng、コピーリスト初期化（暗黙変換）
  has_explicit_ctor s3 = 3;    //ng、コピー初期化（暗黙変換）

  unit<has_explicit_ctor> s4 = {10};  //ok
  unit<has_explicit_ctor> s5 = 10;    //ok
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Lkma2eESKBWV3lZ1)

ご覧のように、包む`unit`型のコンストラクタを通すことによって、要素型`has_explicit_ctor`のexplicitコンストラクタのexplicit性が失われてしまっています。  
その結果、初期化時に暗黙変換が行われるようになってしまっています・・・

暗黙変換されたくないのでコンストラクタにexplicitを付けているはずで、この様に別の型に包まれたとしても同じようになってくれなければ困ってしまいます。

では、`unit`のコンストラクタに`explicit`を付加してやりましょう。そうすれば解決ですね。

```cpp
template<typename T>
struct unit {

  //Tに変換可能なUから構築
  template<typename U=T>
  explicit constexpr unit(U&& other)
    : value(std::forward<U>(other))
  {}

  T value;
};

int main() {
  unit<has_explicit_ctor> u1 = {10};  //ng
  unit<has_explicit_ctor> u2 = 10;    //ng
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BbCFh5Q11TCv3LxZ)

しかしこれにも問題があります。

```cpp
auto f() -> unit<int> {
  return {128};  //compile error!
}

int main() {
  unit<int> u1 = {10};  //ng
  unit<int> u2 = 10;    //ng
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LqMfuxX9w8XDsCHF)

はい、今度は非explicitコンストラクタを持つ型を入れた時に意図しないコンパイルエラーが多発します。すべて`unit`型のコンストラクタがexplicitであるためです。  
（これがまさに、C++17において[N4387](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4387)で解決された`std::tuple`、`std::pair`のコンストラクタの問題です。）

これを解決する一つの策が、型引数`T`のコンストラクタのexplicit性を継承するPerfect Initializationと呼ばれるイディオムです。

```cpp
template<typename Cond>
using enabler = std::enable_if_t<Cond::value, std::nullptr_t>;

template<typename Cond>
using disabler = std::enable_if_t<!Cond::value, std::nullptr_t>;

template<typename T>
struct unit {

  //Tに暗黙変換可能なUから構築
  template<typename U=T, enabler<std::is_convertible<U, T>> = nullptr>
  constexpr unit(U&& other)
    : value(std::forward<U>(other))
  {}
  
  //Tにexplicitに変換可能なUから構築
  template<typename U=T, disabler<std::is_convertible<U, T>> = nullptr>
  explicit constexpr unit(U&& other)
    : value(std::forward<U>(other))
  {}

  T value;
};

auto f() -> unit<int> {
  return {128};  //ok
}

int main() {
  unit<has_explicit_ctor> s1 = {10};  //ng
  unit<has_explicit_ctor> s2 = 10;    //ng
  
  unit<int> u1 = {10};  //ok
  unit<int> u2 = 10;    //ok
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/L9mnHsl1YFcJW17F)  
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LH9Yoz4X5oJ38i9z)

`std::is_convertible<U, T>`は`U`から`T`に暗黙変換可能かどうかを調べるものです。  
それを用いて、暗黙変換可能かどうかでSFINAEして、同じコンストラクタを型`T`に応じてexplicitかどうかを切り替えます。割と泥臭い・・・  
このようにすることで、この`unit<T>`のような型は内包する型のexplicit性を継承することができます。

しかし、要するに`explicit`の有無の違いだけでなぜ二つも同じコンストラクタを書かなければならないのでしょうか。また、さらに`unit<U>`や`const U&`などから変換するようなコンストラクタを追加すると同じことをしなければなりません。  
これは面倒です、どうにかしたい・・・

そこでようやく`explicit(bool)`の出番です。これを使うと、`unit`型のコンストラクタは簡単になります。

```cpp
template<typename T>
struct unit {

  //Tに変換可能なUから構築
  template<typename U=T>
  explicit(std::is_convertible_v<U, T> == false)
  constexpr unit(U&& other)
    : value(std::forward<U>(other))
  {}
  
  T value;
};
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/3QRFRXN7GCydVjwa)

少し見辛い所はありますが`explicit(bool)`に暗黙変換可能かどうかを判定する式を渡してやることで、一つのコンストラクタの定義だけで先ほどと同じ効果を得られます。  
もはや訳の分からないSFINAEによる分岐は必要ありません。

`explicit(bool)`はおそらくこの問題のためだけに導入されました。ライブラリで複雑な型を書く場合にはありがたみを感じることができるでしょう・・・

ところで、STLにはこのように内部に任意の型のオブジェクトを保持するようなクラスがいくつかあります。`std::tuple`や`std::pair`、`std::optional`がその代表です。  
`std::pair`、`std::optional`のある1つのコンストラクタを見てみます（`std::tuple`は説明するには複雑になるのでスキップ・・・）。

### `std::pair`の場合

同じ問題が起きる[`std::pair`のコンストラクタ](https://cpprefjp.github.io/reference/utility/pair/op_constructor.html)の(5)を見てみます。

このコンストラクタには要件があります。
>(5) : is_constructible<first_type, U&&>::value && is_constructible<second_type, V&&>::valueであること

これを考慮したうえでPerfect Initializationすると、おおよそ以下の様な宣言になります。
```cpp
//与えられた条件全てがtrueの場合に有効化
template<typename... Cond>
using enabler = std::enable_if_t<std::conjunction<Cond...>::value, std::nullptr_t>;

template<typename T1, typename T2>
struct pair {

  template<class U=T1, class V=T2,
    enabler<
        std::is_constructible<T1, U&&>,
        std::is_constructible<T2, V&&>,
        std::is_convertible<U, T1>,
        std::is_convertible<V, T2>
    > = nullptr
  >
  constexpr pair(U&& x, V&& y);
  
  template<class U=T1, class V=T2,
    enabler<
        std::is_constructible<T1, U&&>,
        std::is_constructible<T2, V&&>,
        std::negation<
          std::conjunction<
            std::is_convertible<U, T1>,
            std::is_convertible<V, T2>
          >
        >
    > = nullptr
  >
  explicit constexpr pair(U&& x, V&& y);

};
```

先ほどの`unit`とやってることは同じです。型が二つに増えたので複雑になってしまいました。  
要は`T1,T2`どちらかの型が暗黙変換不可であるとき、コンストラクタに`explicit`を付けます。

`explicit(bool)`を使うと・・・
```cpp
template<typename T1, typename T2>
struct pair {

  template<class U=T1, class V=T2,
    enabler<
        std::is_constructible<T1, U&&>,
        std::is_constructible<T2, V&&>
    > = nullptr
  >
  explicit(!(std::is_convertible_v<U, T1> && std::is_convertible_v<V, T2>))
  constexpr pair(U&& x, V&& y);

};
```

要件を判定しSFINAEする部分と、Perfect Initializationする部分とが分離していくらか見やすくなりました。そして1つのコンストラクタ定義で済むようになります。

### `std::optional`の場合
同じ問題が起きる[`std::optional`のコンストラクタ](https://cpprefjp.github.io/reference/utility/pair/op_constructor.html)の(7)を見てみます。

このコンストラクタには要件があります。
>型Tの選択されたコンストラクタがconstexprであれば、このコンストラクタもconstexprとなる  
>型Uから型Tがムーブ構築可能でなければ、このオーバーロードはオーバーロード解決の候補から除外される  
>型Uから型Tに暗黙的に型変換ができる場合、このオーバーロードは非explicitとなる。  
>型Uから型Tに明示的な型変換ならできる場合、このオーバーロードはexplicitとなる

[§23.6.3.1 Constructors [optional.ctor] - N4659](https://timsong-cpp.github.io/cppwp/n4659/optional.ctor#23)も見るとより詳細が分かります。

これを考慮したうえでPerfect Initializationすると、おおよそ以下の様な宣言になります。

```cpp

//与えられた条件全てがtrueの場合に有効化
template<typename... Cond>
using enabler = std::enable_if_t<std::conjunction<Cond...>::value, std::nullptr_t>;

template<typename T>
class optional {

  template<typename U=T,
    enabler<
      std::is_constructible<T, U&&>,
      std::negation<
        std::is_same<std::decay_t<U>, std::in_place_t>
      >,
      std::negation<
        std::is_same<std::optional<T>, std::decay_t<U>>
      >,
      std::is_convertible<U&&, T>
    > = nullptr
  >
  constexpr optional(U&& rhs);

  template<typename U=T,
    enabler<
      std::is_constructible<T, U&&>,
      std::negation<
        std::is_same<std::decay_t<U>, std::in_place_t>
      >,
      std::negation<
        std::is_same<std::optional<T>, std::decay_t<U>>
      >,
      std::negation<
        std::is_convertible<U&&, T>
      >
    > = nullptr
  >
  explicit constexpr optional(U&& rhs);

};
```
もう見るのも嫌ですね。2つを書かされる差は説明してきたように`explicit`を付けるための`std::is_convertible<U&&, T>`の結果が`true`なのか`false`なのかの所だけです。

では`explicit(bool)`を使ってみれば・・・
```cpp
template<typename T>
optional {

  template<typename U=T,
    enabler<
      std::is_constructible<T, U&&>,
      std::negation<
        std::is_same<std::decay_t<U>, std::in_place_t>
      >,
      std::negation<
        std::is_same<std::optional<T>, std::decay_t<U>>
      >,
    > = nullptr
  >
  explicit(!std::is_convertible_v<U&&, T>)
  constexpr optional(U&& rhs);

};
```
要件を記述するSFINAE部はどうしようもありませんが、記述が一つにまとまり、`explicit`となる条件が分離されて見やすくなっています。


これらのように、`explicit(bool)`があると自分で別の型をラップするような型を作る際にコンストラクタをいくらか簡単に書くことができるようになります。  
特に、`optional`の例のように複雑な要件が絡む場合に強い恩恵を感じることができるかと思います。

### 参考文献
- [P0892R0 : explicit(bool)](http://open-std.org/JTC1/SC22/WG21/docs/papers/2018/p0892r0.html)
- [条件付きexplicit指定子 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20180609/p1)
- [Perfect Initializationイディオム - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20150416/p1)
- [explicit 指定子 - cppreference.com](https://ja.cppreference.com/w/cpp/language/explicit)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190525_cpp20_explicit.md)