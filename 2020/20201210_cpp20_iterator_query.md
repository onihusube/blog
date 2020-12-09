# ［C++］ C++20からのイテレータ情報のクエリ

これは[C++ Advent Calendar 2020](https://qiita.com/advent-calendar/2020/cxx)のn日めの記事です。

これまで`iterator_traits`を介して取得していたイテレータ情報は、C++20からはより簡易な手段を介して取得できるようになります。

特に、C++20以降は`iterator_traits`を使わずにこれらのものを利用することが推奨されます。

### `difference_type`

`difference_type`はイテレータの距離を表す型で、イテレータの差分操作（`operator-`）の戻り値型でもあります。

従来は`std::iterator_traits<I>::difference_type`から取得していましたが、C++20からは[`std::iter_difference_t<I>`](https://cpprefjp.github.io/reference/iterator/iter_difference_t.html)を用いる事で同じものを取得できます。

```cpp
#include <iterator>
#include <vector>
#include <ranges>

int main() {
  using iota_view_iter = std::ranges::iterator_t<std::ranges::iota_view<int>>;

  static_assert(std::same_as<std::iter_difference_t<std::vector<int>::iterator>, std::ptrdiff_t>);
  static_assert(std::same_as<std::iter_difference_t<int*>, std::ptrdiff_t>);
  static_assert(std::same_as<std::iter_difference_t<iota_view_iter>, std::ptrdiff_t>);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xtIHjsWxax7VyeGK)

#### `std::incrementable_traits`

`std::iter_difference_t<I>`は基本的にはC++20で追加された[`std::incrementable_traits`](https://cpprefjp.github.io/reference/iterator/incrementable_traits.html)を用いて`difference_type`を取得し、`std::incrementable_traits`はいくつかの経路を使って`difference_type`を探してくれます。

イテレータ型を`I`として

- `I::difference_type`
- `I`の`oeprator-`（2項演算）の戻り値型
- `std::incrementable_traits<I>`の明示的/部分特殊化

C++20からのイテレータ型は上記いずれかで取得できるようにしておけばいいわけです。

なお、`difference_type`は意外に多くの場所でイテレータ判定に使用されているので必ず定義しておいたほうがいいでしょう。おそらくの多くの場合は入れ子の`difference_type`を定義するのが簡単でしょう（つまり今まで通り）。

### `value_type`

`value_type`はイテレータの指す要素の型を表す型です。大抵はイテレータの間接参照の戻り値型から参照を除去した型でしょう。

従来は`std::iterator_traits<I>::value_type`から取得していましたが、C++20からは[`std::iter_value_t<I>`](https://cpprefjp.github.io/reference/iterator/iter_value_t.html)を用いる事で同じものを取得できます。

```cpp
#include <iterator>
#include <vector>
#include <ranges>

int main() {
  using iota_view_iter = std::ranges::iterator_t<std::ranges::iota_view<unsigned int>>;

  static_assert(std::same_as<std::iter_value_t<std::vector<int>::iterator>, int>);
  static_assert(std::same_as<std::iter_value_t<double*>, double>);
  static_assert(std::same_as<std::iter_value_t<iota_view_iter>, unsigned int>);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gJTguyhn3eP7rsx4)

#### `std::indirectly_readable_traits`

`std::iter_value_t<I>`は基本的にはC++20で追加された[`std::indirectly_readable_traits`](https://cpprefjp.github.io/reference/iterator/indirectly_readable_traits.html)を用いて`value_type`を取得し、`std::indirectly_readable_traits`はいくつかの経路を使って`value_type`を探してくれます。

イテレータ型を`I`として

- `I::value_type`
- `I::element_type`
- `std::incrementable_traits<I>`の明示的/部分特殊化

C++20からのイテレータ型は上記いずれかで取得できるようにしておけばいいわけです。

この`value_type`も他の場所で使用されていることがあるので必ず定義しておいたほうがいいでしょう。おそらく入れ子の`value_type`を定義するのが簡単でしょう（これも今まで通り）。

### `reference`

`reference`はイテレータの指す要素を参照する参照型で、これはイテレータの間接参照の戻り値型です。

従来は`std::iterator_traits<I>::reference`から取得していましたが、C++20からは[`std::iter_reference_t<I>`](https://cpprefjp.github.io/reference/iterator/iter_reference_t.html)を用いる事で同じものを取得できます。

```cpp
#include <iterator>
#include <vector>
#include <ranges>

int main() {
  using iota_view_iter = std::ranges::iterator_t<std::ranges::iota_view<unsigned int>>;

  static_assert(std::same_as<std::iter_reference_t<std::vector<int>::iterator>, int&>);
  static_assert(std::same_as<std::iter_reference_t<double*>, double&>);
  static_assert(std::same_as<std::iter_reference_t<iota_view_iter>, unsigned int>);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gJTguyhn3eP7rsx4)

`reference`というのは歴史的経緯から来る名前で、イテレータの間接参照の戻り値型は必ずしも参照型でなくてもいいのです。

`std::iter_reference_t`は次のように定義されています。

```cpp
namespace std {
  template<dereferenceable I>
  using iter_reference_t = decltype(*declval<I&>());
}
```

そのまま間接参照の戻り値型ですね、つまり我々は何もする必要がありません。普通のイテレータ型なら常にこれを利用できます。

#### `std::iter_rvalue_reference_t`

[`std::iter_rvalue_reference_t`](https://cpprefjp.github.io/reference/iterator/iter_rvalue_reference_t.html)は`iterator_traits`にはなかったもので、イテレータの要素を指す右辺値参照型を表すものです。

```cpp
#include <iterator>
#include <vector>
#include <ranges>

int main() {
  using iota_view_iter = std::ranges::iterator_t<std::ranges::iota_view<unsigned int>>;
  
  static_assert(std::same_as<std::iter_rvalue_reference_t<std::vector<int>::iterator>, int&&>);
  static_assert(std::same_as<std::iter_rvalue_reference_t<double*>, double&&>);
  static_assert(std::same_as<std::iter_rvalue_reference_t<iota_view_iter>, unsigned int>);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/YMbZwtsjKG1soh2m)

イテレータがprvalueを返す場合はこれも素の方を示します。

これは少し複雑な定義をされていますが、大抵の場合は`decltype(std::move(*i))`の型を取得することになります。つまりこれも我々は何もしなくても使用できます。

#### `std::iter_common_reference_t`

[`std::iter_common_reference_t`](https://cpprefjp.github.io/reference/iterator/iter_common_reference_t.html)も`iterator_traits`にはなかったもので、`std::iter_value_t<I>&`と`std::iter_reference_t<I>`の両方を束縛することのできるような共通の参照型を表すものです。

```cpp
#include <iterator>
#include <vector>
#include <ranges>

int main() {
  using iota_view_iter = std::ranges::iterator_t<std::ranges::iota_view<unsigned int>>;

  static_assert(std::same_as<std::iter_common_reference_t<std::vector<int>::iterator>, int&>);
  static_assert(std::same_as<std::iter_common_reference_t<double*>, double&>);
  static_assert(std::same_as<std::iter_common_reference_t<iota_view_iter>, unsigned int>);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/qJGj2X32S9CAVeNx)

これも`reference`といいつつ、必ずしも参照型であるとは限りません。

`std::iter_common_reference_t`は次のように定義されています。

```cpp
namespace std {
  template<indirectly_readable I>
  using iter_common_reference_t = common_reference_t<iter_reference_t<I>, iter_value_t<I>&>;
}
```

要は[`std::common_reference`](https://cpprefjp.github.io/reference/type_traits/common_reference.html)に投げているのですが、これは組み込み型であれば何もしなくても取得できます。ユーザー定義型では[`std::basic_common_reference`](https://cpprefjp.github.io/reference/type_traits/basic_common_reference.html)を通して*common reference*を定義してやる必要があります。

### `pointer`

その要素のポインタ型を取得する口は用意されていません。おそらく`value_type*`で十分という事でしょう。

### `iterator_category`

C++20以降、イテレータカテゴリの判定に各イテレータのタグ型を調べてどうこうするのは完全にナンセンスです。コンセプトを使いましょう。

`<iterator>`ヘッダにあらかじめいくつかのイテレータコンセプトが用意されています。特に、基本的な*input iterator*とか*forward iterator*といったものにはそのままの名前でコンセプトが定義されています。

```cpp
// forward_iteratorコンセプトの定義の例
namespace std {
  template<class I>
  concept forward_iterator =
    input_iterator<I> &&
    derived_from<ITER_CONCEPT(I), forward_iterator_tag> &&
    incrementable<I> &&
    sentinel_for<I, I>;
}
```

これらのコンセプトの間にはその性質の関係に応じた包含関係があり、コンセプトの半順序上でもそれに応じた順序付けがなされます。

```cpp
#include <iostream>
#include <iterator>
#include <ranges>
#include <vector>
#include <list>
#include <forward_list>

template<std::forward_iterator I>
void iter_print(I) {
  std::cout << "forward iterator!" << std::endl;
}

template<typename I>
  requires std::bidirectional_iterator<I>
void iter_print(I) {
  std::cout << "bidirectional iterator!!" << std::endl;
}

void iter_print(std::random_access_iterator auto) {
  std::cout << "random access iterator!!" << std::endl;
}


int main() {
  iter_print(std::forward_list<int>::iterator{});
  iter_print(std::list<int>::iterator{});
  iter_print(std::vector<int>::iterator{});
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/KlRShyfWSQ05R9rA)

#### `iterator_concept`

イテレータを定義する時は従来通り`iterator_category`を用意する必要がありますが、C++20からはそこに`iterator_concept`を利用することができます。

`iterator_concept`が用意されたのはC++17以前との互換性を取るためで、特にポインタ型のカテゴリが`contiguous_iterator`に変更された事に対処する面が大きいと思われます。  
詳しくは次節で説明しますが、C++20以降でしか利用できないイテレータを定義する場合は、常に`iterator_concept`でイテレータカテゴリを宣言し`iterator_category`は定義しないようにしておきます。

```cpp
// C++20以降しか考慮しないイテレータ
struct newer_iterator {
  using iterator_concept = std::forward_iterator_tag;
  // 他のメンバは省略
};

// C++17以前との互換性を確保するC++20仕様イテレータ
struct cpp17_compatible_iterator {
  using iterator_concept = std::random_access_iterator_tag; // C++20コードから使用したときのイテレータカテゴリ
  using iterator_category = std::input_iterator_tag;        // C++17コードから使用したときのイテレータカテゴリ
  // 他のメンバは省略
};
```

### `C::iterator`


### 参考文献

- [`<iterator>` - cpprefjp](https://cpprefjp.github.io/reference/iterator.html)