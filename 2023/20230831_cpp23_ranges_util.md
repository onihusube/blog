#  ［C++］C++23<ranges>のユーティリティ

C++23で追加された`<ranges>`関連の小さめのユーティリティをまとめておきます。ここには新しいファクトリ/アダプタや`ranges::to`は含まれていません。

[:contents]

### `const_iterator_t`/`const_sentinel_t`

`const_iterator_t`は`range`型からその定数イテレータ（*const iterator*）の型を取得するエイリアステンプレートです。`iterator_t`の亜種で、どちらも`std::ranges`名前空間にあります。`const_sentinel_t`はそれに対応する番兵型を取得するもので、`sentinel_t`の亜種です。

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

ただし例外として、間接参照結果が*prvalue*（すなわち非参照）であるようなイテレータ型（`range`型）に対する`const_iterator`/`const_iterator_t`の結果のイテレータ型は、間接参照結果が`const`参照ではなく*prvalue*のままとなります（`const`参照は外されます）。これは、間接参照結果の*prvalue*をどう変更したとしても元の`range`の要素を変更してはいないためと、*prvalue*の結果を`const`参照化するとダングリング参照になるためです。

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
```

他の特殊な場合として、`views::zip`のような特殊なイテレータ型（値型と参照型の関係が複雑なイテレータ型）の場合は、`const_iterator`/`const_iterator_t`を通した後の間接参照結果型は単純に`const`を付加しただけでも*prvalue*のままにもなりません（``）

とはいえそのような特殊なイテレータ型の場合は`common_reference`のカスタマイズなどを通して適切に`const`対応が取られているはずなので、結果的には、`const_iterator`/`const_iterator_t`を通したイテレータ型では常にその要素は変更されない（できない）と見なすことができます。

### `range_const_referece_t`
### `costant_range`
### `range_adaptor_closure`

### 参考文献

- [P2278R4 `cbegin` should always return a constant iterator](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2278r4.html)
- [`const_iterator_t` - cpprefjp](https://cpprefjp.github.io/reference/ranges/const_iterator_t.html)
- [`const_sentinel_t` - cpprefjp](https://cpprefjp.github.io/reference/ranges/const_sentinel_t.html)
- [［C++］ rangesのパイプにアダプトするには - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2022/04/24/010041)