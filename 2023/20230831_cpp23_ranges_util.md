#  ［C++］C++23<ranges>のユーティリティ

C++23で追加された`<ranges>`関連の小さめのユーティリティをまとめておきます。ここには新しいファクトリ/アダプタや`ranges::to`は含まれていません。ここで紹介するものは基本的に`std::ranges`名前空間にありますが、名前空間指定を省略しています。

[:contents]

### `const_iterator_t`/`const_sentinel_t`

`const_iterator_t`は`range`型からその定数イテレータ（*const iterator*）の型を取得するエイリアステンプレートです。`const_sentinel_t`はそれに対応する番兵型を取得するもので、どちらも`std::ranges`名前空間にあります。これらは、`iterator_t`/`sentinel_t`の亜種です。

```cpp
namespace std::ranges {
  template<range R>
  using const_iterator_t = const_iterator<iterator_t<R>>;

  template<range R>
  using const_sentinel_t = const_sentinel<sentinel_t<R>>;
}
```

定数イテレータはその要素が変更できないイテレータのことで、ほぼ間接参照結果が`const`参照になっていると思って差し支えありません。`const_sentinel_t`で取得できる番兵型も意味合いは同様なのですが、通常番兵を間接参照することはほぼないのでこれは`const_iterator_t`と対になるように用意されている側面が強いものです。

定義で使用されている`const_iterator`/`const_sentinel`はイテレータ（番兵）型を受けてそれを定数イテレータ（番兵）型に変換するエイリアステンプレートで、この変換に際しては入力イテレータ型の間接参照結果が既に`const`ではない場合にのみ`std::basic_const_iterator`でラップしてイテレータを確実に定数化します。

`const_iterator_t`/`const_sentinel_t`で得られるイテレータ型は、C++23以降の`std::ranges::cbegin`/`std::ranges::cend`で取得できるイテレータの型と一致します。

```cpp
#include <ranges>
using namespace std::ranges;

template<range R>
void f(R& rng) {
  const_iterator_t<R> cit = cbegin(rng);  // Rに関わらずok
  const_sentinel_t<R> cse = cend(rng);    // Rに関わらずok

  *cit = ...; // ng（ほとんどの場合）
}
```

ただし例外として、間接参照結果が*prvalue*（すなわち非参照）であるようなイテレータ型（`range`型）に対する`const_iterator`/`const_iterator_t`の結果のイテレータ型は、間接参照結果が`const`参照ではなく*prvalue*のままとなります（`const`修飾がある場合は外されます）。これは、間接参照結果の*prvalue*をどう変更したとしても元の`range`の要素を変更してはいないためと、*prvalue*の結果を`const`参照化するとダングリング参照になるためです。

```cpp
#include <ranges>
using namespace std::ranges;

// iota_viewの間接参照結果型は要素型のprvalue
void f(iota_view<int> vi) {
  const_iterator_t<iota_view<int>> cit = cbegin(vi);
  const_sentinel_t<iota_view<int>> cse = cend(vi);

  *cit = 10;  // 要素型が組み込み型の場合はng、クラス型の場合は通る可能性がある

  static_assert(std::same_as<decltype(*cit), int>); // パスする
}

// 間接参照結果がstringのprvalueの場合
template<range R>
  requires std::same_as<range_reference_t<R>, std::string>
void g(R& rng) {
  const_iterator_t<R> cit = cbegin(vi);
  const_sentinel_t<R> cse = cend(vi);

  *cit = "str"; // ok、ただしこの変更は観測されない
}
```

他の特殊な場合として、`views::zip`のような特殊なイテレータ型（値型と参照型の関係が複雑なイテレータ型）の場合は、`const_iterator`/`const_iterator_t`を通した後の間接参照結果型は単純に`const`を付加しただけでも*prvalue*のままにもなりません（参照型`std::tuple<T1&, T2&, ...>`に対して、`std::tuple<const T1&, const T2&, ...>`のようになる）。

これらのエイリアステンプレートによる定数イテレータの参照型の決定は最終的に`std::iter_const_reference_t`によって行われます。これについては以前の記事を参照ください

- [［C++］`iter_const_reference_t`の型の決定について - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2023/04/30/181514)

とはいえそのような特殊なイテレータ型の場合は`common_reference`のカスタマイズなどを通して適切に`const`対応が取られているはずなので、結果的には、`const_iterator`/`const_iterator_t`を通したイテレータ型では常にその要素は変更されない（できない）と見なすことができます。よって、これと一致する`std::ranges::cbegin`/`std::ranges::cend`で得られるイテレータも常に定数イテレータになるようになります（C++20時点では、必ずしも定数イテレータを得られない場合がありました）。

### `range_const_reference_t`

`range_const_reference_t`は`range`型`R`から、その間接参照結果を`const`化した型を取得するエイリアステンプレートです。

```cpp
namespace std::ranges {
  template<range R>
  using range_const_reference_t = iter_const_reference_t<iterator_t<R>>;
}
```

この型は、先程の`const_iterator_t`で得られる定数イテレータの間接参照結果の型となります。

```cpp
#include <ranges>
using namespace std::ranges;

template<range R>
void f(R& rng) {
  const_iterator_t<R> cit = cbegin(vi);

  range_const_reference_t<R> cr = *cit;  // ok
}
```

ただし、前述のように*prvalue*を`const`化した型はそのまま*prvalue*となるほか、`viws::zip`など要素型が特殊な場合もあるため、`range_const_reference_t`によって得られる型は参照型ではない場合があり、常に`const`であるわけでもありません。それでも、`const_iterator_t`が必ず定数イテレータを取得するように、`range_const_reference_t`もまたそれを通して元の範囲の要素を変更できない型を示します。

### `costant_range`

`costant_range`はその要素を変更できない`range`を表すコンセプトです。

```cpp
namespace std::ranges {
  template<class T>
  concept constant_range = input_range<T> && constant-iterator<iterator_t<T>>;
}
```

定義は`input_range`かつそのイテレータが`constant-iterator`であることを要求し、[`constant-iterator`](https://cpprefjp.github.io/reference/iterator/constant-iterator.html)はイテレータが定数イテレータであることを表す説明専用のコンセプトです。

このコンセプトは主に、`range`を受ける場所で受け取った`range`の要素を変更しない場合に使用すると良いでしょう。

```cpp
#include <ranges>
using namespace std::ranges;

// constant_rangeコンセプトで制約することで、受け取ったrangeの要素を変更しないことを表明
void f(constant_range auto&& rng) {
  // constant_rangeを満たしているため、内部では要素を変更しようとしてもできない
  auto it = begin(vi);
  *it = ...; // ngもしくは無意味

  ...
}

int main() {
  std::vector<int> vec = {1, 2, 3, 4, 5};
  const auto& rv = vec;

  f(vec); // ng
  f(rv);  // ok
}
```

`costant_range`コンセプトは構文的にイテレータを介して要素が変更不可能であることを要求しているため、関数の実装側も`costant_range`として受け取った範囲の要素を変更しようとしても変更できません。

手持ちの範囲を手軽に`costant_range`化するには、`views::as_const`を使用します。

```cpp
#include <ranges>
using namespace std::ranges;

void f(constant_range auto&& R) {
  ...
}

int main() {
  std::vector<int> vec = {1, 2, 3, 4, 5};

  f(vec); // ng
  f(vec | views::as_const); // ok
}
```

`views::as_const`は、入力`range`を単に`const`化したり、そのイテレータを`std::basic_const_iterator`でラップするなどして、入力`range`を`constant_range`へ変換します。

### `range_adaptor_closure`

### 参考文献

- [P2278R4 `cbegin` should always return a constant iterator](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2278r4.html)
- [`const_iterator_t` - cpprefjp](https://cpprefjp.github.io/reference/ranges/const_iterator_t.html)
- [`const_sentinel_t` - cpprefjp](https://cpprefjp.github.io/reference/ranges/const_sentinel_t.html)
- [`std::ranges::range_const_reference_t` - cpprefjp](https://cpprefjp.github.io/reference/ranges/range_const_reference_t.html)
- [`std::ranges::constant_range` - cpprefjp](https://cpprefjp.github.io/reference/ranges/constant_range.html)
- [`std::basic_const_iterator` - cpprefjp](https://cpprefjp.github.io/reference/iterator/basic_const_iterator.html)
- [［C++］`iter_const_reference_t`の型の決定について - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2023/04/30/181514)
- [C++23 <ranges>のviewを見る3 - As const view](https://zenn.dev/onihusube/articles/04120c20e1339b)
- [［C++］ rangesのパイプにアダプトするには - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2022/04/24/010041)