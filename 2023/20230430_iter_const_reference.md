# ［C++］iter_const_reference_tの型の決定について

先日zennに投降した、`views::as_const`についての記事を書いているときに調べた、`const_iterator`の要素型（参照型）の決定過程に関するメモです。

- [C++23 <ranges>のviewを見る3 - As const view - zenn](https://zenn.dev/onihusube/articles/04120c20e1339b)

以下、`views::as_const`に関しては知っているものとして説明しません（この記事ないし他の解説をご覧ください）。

また、上記記事及び以降でも、イテレータの間接参照結果の事を指してイテレータの要素だとか要素型だとか言っていますが、それは正しくは要素の参照あるいは参照型（`iter_reference_t`）の事です。本来の意味の要素型（`iter_value_t`）とは異なり、`views::as_const`や`const_iterator`は要素の間接参照結果を`const`化するのであって要素型そのものを`const`化するわけではありません。

[:contents]

### `views::as_const`と`constant_range`

`views::as_const`は入力範囲の要素がすでに`const`になっているかどうかを判定してからそうなっていない場合に何か作業を行います。その判定に関わっているのは`views::as_const`と共にC++23で追加された`std::ranges::constant_range`コンセプトです。

```cpp
// constant_rangeの定義
template<class T>
concept constant_range = 
  input_range<T> && 
  constant-iterator<iterator_t<T>>;
```

`constant_range`の主要な部分を担っているのが`constant-iterator`というコンセプトです。これは説明専用の（規格文書内で規定のために使用される）もので、次のように定義されています。

```cpp
template<class It>
concept constant-iterator =
  input_iterator<It> && 
  same_as<iter_const_reference_t<It>, iter_reference_t<It>>;
```

`constant-iterator`コンセプトの主要な部分は2つ目の制約式で、この制約式は入力のイテレータ型`It`に対して、その`iter_const_reference_t`と`iter_reference_t`が一致することを求めています。[`iter_reference_t`](https://cpprefjp.github.io/reference/iterator/iter_reference_t.html)はイテレータの間接参照（`*`）の直接の結果型のことで、どうやらそれが`const`になっていればこの制約式を満たせるように見えます。

この`iter_const_reference_t`は`views::as_const`と共にC++23で追加されたエイリアステンプレートで、次のように定義されています

```cpp
template<indirectly_readable It>
using iter_const_reference_t =
  common_reference_t<const iter_value_t<It>&&, iter_reference_t<It>>;
```

イテレータ型`It`に対して、その要素型（[`std::iter_value_t`](https://cpprefjp.github.io/reference/iterator/iter_value_t.html)）を`const`参照化したものと参照型の[`common_reference`](https://cpprefjp.github.io/reference/type_traits/common_reference.html)を求めています。

`common_reference`の決定過程は複雑ですが、雰囲気的にはこの結果は常に`const`が付いた型になりそうに見えます。とりあえず今はそれを認めることにして、`iter_const_reference_t<I>`は常に`const`であることを仮定しておきます。

### `std::ranges::cbegin()/cend()`

`views::as_const`の入力範囲が`constant_range`ではない場合、`views::as_const`は次にその型を何とかこねくり回して要素の`const`化が達成できないかを試行します。それが叶わない場合、入力範囲を`as_const_view`に渡して返すことで要素型の`const`変換を行います。

`views::as_const`が`as_const_view`を使用する場合、そのイテレータは`std::ranges::cbegin()`から取得されます。`ranges::cbegin()`はC++23で確実に要素が`const`になっているイテレータを返すように改修されており、型`T`の式`E`とそれの評価結果の左辺値を`t`として`ranges::cbegin(E)`のように呼ばれた時次のようなことを行います

- `enable_borrowed_range<remove_cv_t<T>> == false`ならば、ill-formed
- そうではない場合、式`U`を`ranges​::​begin(possibly-const-range(t))`として、`const_iterator<decltype(U)>(U)`を返す

`possibly-const-range`は説明専用の関数であり、次のように定義されています

```cpp
template<input_range R>
constexpr auto& possibly-const-range(R& r) {
  if constexpr (constant_range<const R> && !constant_range<R>) {
    return const_cast<const R&>(r);
  } else {
    return r;
  }
}
```

ここで行われていることは、入力範囲`R`について入力範囲を単に`const`化すればその要素も`const`化する（`const R`が`constant_range`となる）場合はそうして、そうでない場合、及び`R`が既に`constant_range`である場合は入力をそのまま返す、という事をしています。

`ranges::cbegin()`は、こうして返された範囲オブジェクトから`ranges::begin()`によってイテレータを取得し、それを`std::const_iterator`に通して返します。

`ranges::cend()`はこの手順内の`ranges::begin()`を`ranges::end()`に置き換えたことを行い、最後に`std::const_sentinel`を通して返します。

### `std::const_iterator/const_sentinel`

`std::const_iterator`はエイリアステンプレートであり、入力の型`I`によって次のどちらかの型を返します

- `I`が`constant-iterator`ならば`I`
- そうでないならば、`basic_const_iterator<I>`

ここで出てくる`constant-iterator`コンセプトは、`constant_range`で使用されていたものと同じものを指しています。すなわち、`I`の要素型が`const`ではない場合にのみ`I`を`std::basic_const_iterator`にラップして返します。

`std::const_sentinel`もエイリアステンプレートであり、入力の型`S`によって次のどちらかの型を返します

- `S`が`input_iterator`ならば`const_iterator<S>`
- そうでないならば、`S`

これはどちらも、C++23で`views::as_const`と共に導入されたものです。

### `std::basic_const_iterator`

`std::basic_const_iterator`はC++23で`views::as_const`および`ranges::cbegin()`のために追加されたイテレータラッパであり、入力イテレータの間接参照結果を`const`化する事だけを行います。

前述のように、イテレータ型`I`に対していつも`std::const_iterator<I>`を使用するようにすれば、`std::basic_const_iterator`を`std::basic_const_iterator`でラップするような二重`const`化を回避してイテレータ要素の`const`化を達成できます。

`std::basic_const_iterator`の見どころはほぼその`operator*`のみで、それは内部のイテレータ`it`に対して`return static_cast<reference>(*it)`を返します。`reference`は`std::basic_const_iterator`の入れ子型として説明専用として定義されるもので、次のように定義されています

```cpp
template<input_iterator Iterator>
class basic_const_iterator {
  ...
  
  // 説明専用型referenceの定義
  using reference = iter_const_reference_t<Iterator>;
  
  ...
};
```

結局ここでも、`iter_const_reference_t`が出てきます。

### `std::iter_const_reference_t`

こうして、~~役所もびっくりの~~たらい回しの果てに、`views::as_const`の要素型の決定には`std::iter_const_reference_t`というエイリアステンプレートが深く関与していること分かりました。`views::as_const`の分岐を考えると、これが直接介さない場合でも`views::as_const`の結果の`view`の要素型（参照型）は入力範囲のイテレータ型を`std::iter_const_reference_t`に通して得られた型と同じになるはずです（たぶん）。

従って、`views::as_const`の結果範囲の要素型は`std::iter_const_reference_t`がどう振舞うかを調べればわかることになります。`std::iter_const_reference_t`の定義は次のようになっており

```cpp
template<indirectly_readable It>
using iter_const_reference_t =
  common_reference_t<const iter_value_t<It>&&, iter_reference_t<It>>;
```

その決定には2つの型の`common_reference`が計算されています。

その1つ目の型`const iter_value_t<It>&&`では、`iter_value_t<It>`が参照型ではない場合に結果は必ず`const`になり、かつ常に参照型になります。とはいえ`iter_value_t<It>`は通常修飾なしの型（*prvalue*）であるはずで、[`std::indirectly_readable_traits`](https://cpprefjp.github.io/reference/iterator/indirectly_readable_traits.html)をよく見ると`remove_cv`されるうえに参照型だと`value_type`が定義されないことが分かるため、いつも修飾なしの型であるとします（もう一つ`iterator_traits`の経路だと必ずしもそうではありませんが）。すると、`const iter_value_t<It>&&`とはいつも`const`右辺値参照になります。

2つ目の型`iter_reference_t<It>`はイテレータの関節参照の結果型であり、これは

- 修飾なしの型（*prvalue*）
- 参照型
    - 左辺値参照（`&`）
    - 右辺値参照（`&&`）
- 上2つの`const`修飾

のいずれかであるはずです（`volatile`は無視で・・・）。

それらの型の間の`common_reference`の決定は複雑ですがこれらの仮定を用いるとある程度求めやすくなります。特に、1つ目の型は常に`const`右辺値参照型なので、問題となるのは2つ目の型が参照型かどうかです。`std::common_reference<const T&&, U>`とすると、この結果は次のどちらかになりそうです（あまり自信がない・・・）

- `U`が参照型（`U&`/`U&&`） : `decltype(false ? declval<const T&(&)()>()() : declval<const U&(&)()>()())`
- `U`が*prvalue*（`U`） : `decltype(false ? declval<const T&&(&)()>()() : declval<U(&)()>()())`

とはいえこの型がどうなるかも難しいものがあり（そもそもパースがムズカシイ）、`U`に`const`がついてると少し正しくない部分があるなどやはり難しいものがあります。なので、簡単なテスターを作って実際の振る舞いを確かめてみます。

```cpp
template<typename T>
using test = std::common_reference_t<const std::remove_cvref_t<T>&&, T>;
```

これを使うと、`std::iter_const_reference_t`の型をイテレータ型を介さず直接調べることができます。

```cpp
int main() {
  static_assert(std::same_as<test<int&>, const int&>);
  static_assert(std::same_as<test<int&&>, const int&&>);
  static_assert(std::same_as<test<const int&>, const int&>);
  static_assert(std::same_as<test<int>, int>);
  static_assert(std::same_as<test<const int>, int>);
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/zlMRT9ZphxjcPziL)
- [godbolt](https://godbolt.org/z/6q61deaWs)

イテレータ型`I`の参照型（`iter_reference_t<I>`）を`T`（+修飾）とし、型`T`に対して特に`basic_common_reference`特殊化が行われていないとして、これによると`T`によって`std::iter_const_reference_t<I>`は次のようになります

|`iter_reference_t<I>`|`iter_const_reference_t<I>`|
|---|---|
|`T&`|`const T&`|
|`T&&`|`const T&&`|
|`const T&`|`const T&`|
|`const T&&`|`const T&&`|
|`T`|`T`|
|`const T`|`T`|

`T`が参照型である場合は適切に`const`化されていますが、`T`が*prvalue*である場合はそうなってはいません。それはまあ当然というか、*prvalue*を`const`参照でラップしたらそれはダングリング参照になりますし、*prvalue*に`const`を付加することにはほぼ意味がありません。

これは一般の型`T`に対しての結果ですが、意図的に`common_reference`が（`basic_common_reference`によって）カスタムされている一部の型が標準ライブラリにも存在し、それを使用するような`range`型ではその要素型と参照型の景色が少し異なっていたりします。たとえば

- `std::vector<bool>`
    - `range_value_t` : `bool`
    - `range_reference_t` : `std::vector<bool>::reference`
- `views::zip`とそのファミリ
    - `range_value_t` : `std::tuple<T, U>`
    - `range_reference_t` :  `std::tuple<T&, U&>`
- `views::enumrate`
    - `range_value_t` : `std::tuple<D, T>`
    - `range_reference_t` : `std::tuple<D, T&>`

などがあります。

ここでの`T, U`は`views::zip`や`views::enumarate`の入力範囲の`range_value_t`/`range_reference_t`/`range_difference_t`によって変化するためそのプレースホルダーとします。`T, U`は任意の型の可能性がありますがここでは参照修飾は考えないことにして、`D`は*prvalue*の整数型です。

これらの型の場合は、値型（`range_value_t`）・参照型（`range_reference_t`）・`const`要素型（`range_const_reference_t`）はそれぞれ以下のようになります

|`range`|`range_value_t<I>`|`range_reference_t<I>`|`range_const_reference_t<I>`|
|---|---|---|---|
|`std::vector<bool>`|`bool`|`std::vector<bool>::reference`|`bool`|
|`const std::vector<bool>`|`bool`|`bool`|`bool`|
|`views::zip`|`std::tuple<T, U>`|`std::tuple<T&, U&>`|`std::tuple<const T&, const D&>`|
|`views::enumrate`|`std::tuple<D, T>`|`std::tuple<D, T&>`|`std::tuple<D, const T&>`|

`range_const_reference_t`は`iter_const_reference_t`の`range`版で、`iter_const_reference_t<iterator_t<R>>`として定義されています。

`zip`と`enumrate`の結果をみると想像がつくかもしれませんが、`std::tuple<Ts...>`と`std::tuple<Us...>`の`common_reference`とは、`std::tuple<std::common_reference_t<Ts, Us>...>`のように、`tuple`要素型の対応する型同士の`common_reference`を求める形になります。なので、`std::tuple`の他のケースはその要素型について先程の一般の型に対する結果を参照すると簡単に求められます。また、その場合は`tuple`自身の`const`/参照修飾は無視されます。

`iter_const_reference_t`はこのように、とても巧妙に入力イテレータ型の要素型をそれに応じて適切に`const`化します。しかも、*prvalue*の場合は余計なことをしないなど、本当によくできすぎていることが分かります。

### 参考文献

- [P2278R4 `cbegin` should always return a constant iterator](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2278r4.html)
- [P2321R2 `zip`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2321r2.html)
- [`std::common_reference` - cpprefjp](https://cpprefjp.github.io/reference/type_traits/common_reference.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2023/20230430_iter_const_reference.md)
