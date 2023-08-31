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

`range_adaptor_closure`は、レンジアダプタを自作する際に標準のアダプタと`|`で接続できるようにするためのクラス型です。CRTPによって継承して利用します。

まず、これを使用せず何も考えずに自作のレンジアダプタを作成すると、標準のアダプタなら可能なパイプライン演算子（`|`）を使用した入力や合成ができません。

```cpp
#include <ranges>
using namespace std::ranges;

// 自作のレンジアダプタ型
// 特にパイプのための実装をしていないとする
class my_original_adaptor {
  ...
};

inline constexpr my_original_adaptor my_adaptor{};

int main() {
  std::vector vec = {...};

  // パイプでviewを入力できない
  view auto v1 = vec | my_adaptor; // ng
  view auto v2 = vec | views::take(2) | my_adaptor;  // ng

  // レンジアダプタの合成もできない
  auto raco1 = views::take(2) | my_adaptor;  // ng
  auto raco2 = my_adaptor | views::take(2);  // ng
}
```

これを可能とするには標準ライブラリ実装が用いているのと同様の方法によってパイプライン演算子を有効化しなければなりませんが、それは実装詳細であり公開されているものではありません。そこで、`range_adaptor_closure`を使用すると統一的かつ実装詳細を気にしない方法でパイプライン演算子を有効化することができます。

```cpp
#include <ranges>
using namespace std::ranges;

// 自作のレンジアダプタ型
// CRTPによってrange_adaptor_closureを継承する
class my_original_adaptor : range_adaptor_closure<my_original_adaptor> {
  ...
};

inline constexpr my_original_adaptor my_adaptor{};

int main() {
  std::vector vec = {...};

  // パイプでviewを入力できるようになる
  view auto v1 = vec | my_adaptor; // ok
  view auto v2 = vec | views::take(2) | my_adaptor;  // ok

  // レンジアダプタの合成も有効化される
  auto raco1 = views::take(2) | my_adaptor;  // ok
  auto raco2 = my_adaptor | views::take(2);  // ok
}
```

ここでは自作のレンジアダプタ`my_original_adaptor`の実装詳細を省略していますが、当然それはパイプライン演算子対応以外の部分はきちんとレンジアダプタとして実装されている必要があります。

`range_adaptor_closure`はこのように、本来とても複雑なパイプライン演算子対応を自動化してくれるものです。レンジアダプタを自作することは稀だと思われるためあまり使用機会はないかもしれませんが、レンジアダプタを自作する場合は非常に有用なものとなるでしょう。

ただ、`range_adaptor_closure`はその名の通りレンジアダプタクロージャオブジェクト型に対してパイプライン演算子を有効化することしかしません。追加の引数が必要なレンジアダプタオブジェクト型において、入力`range`以外の引数を予め受けておいてレンジアダプタクロージャオブジェクトを生成する部分については`range_adaptor_closure`はもちろん、特にサポートがありません。

```cpp
#include <ranges>
using namespace std::ranges;

int main() {
  std::vector vec = {...};
  
  // views::commonはレンジアダプタクロージャオブジェクト
  view auto v1 = vec | views::common;

  // 追加の引数が必要なものはレンジアダプタオブジェクト
  view auto v2 = vec | views::take(5);
  view auto v3 = vec | views::filter([](auto v) { ... });
  view auto v4 = vec | views::transform([](auto v) { ... });

  // レンジアダプタオブジェクトに追加の引数を予め充填したものはレンジアダプタクロージャオブジェクト
  auto raco1 = views::take(5);
  auto raco2 = views::filter([](auto v) { ... });
  auto raco3 = views::transform([](auto v) { ... });

  // パイプライン演算子はレンジアダプタクロージャオブジェクトに対して作用する
  view auto v5 = vec | raco1; // v2と同じ意味
  view auto v6 = vec | raco2; // v3と同じ意味
  view auto v7 = vec | raco3; // v4と同じ意味
  auto raco4 = raco1 | raco2 | raco3;
}
```

レンジアダプタを自作する場合、必ずしもレンジアダプタクロージャとして実装できない場合が容易に考えられ、その場合は追加の引数を保存してレンジアダプタクロージャオブジェクトを生成するという部分を実装しなければなりません。

幸いなことに、C++23から追加された`std::bind_back()`（`std::bind_front()`の逆順版）を使用すると、追加の引数の順番を保った保存の部分を委任することができます。

```cpp
#include <ranges>
using namespace std::ranges;

// 自作のレンジアダプタクロージャ型
template<typename F>
struct my_closure_adaptor : range_adaptor_closure<my_original_adaptor> {
  F f;

  view auto operator()(viewable_range auto&& input) const {
    return f(input);  // bind_back()でラッピングされたcallbleに引数のrangeを入力しレンジアダプタを実行する
  }
};

// 自作のレンジアダプタ型（not クロージャ）
class my_original_adaptor :  {

  ...
  
  // 追加の引数を受けてレンジアダプタクロージャオブジェクトを返す
  template<typename... Args>
  auto operator()(Args&&... args) const {
    // bind_back()で自身と追加の引数をラッピングし、レンジアダプタクロージャオブジェクトを作成
    return my_closure_adaptor{ .f = std::bind_back(*this, std::forward<Args>(args)...)};
  }
};

inline constexpr my_original_adaptor my_adaptor{};

int main() {
  std::vector vec = {...};

  // my_original_adaptorが追加の引数として整数を1つ受け取るとすると
  view auto v1 = vec | my_adaptor(1); // ok
  view auto v2 = vec | views::take(2) | my_adaptor(2);  // ok
  auto raco = my_adaptor(1);  // ok
  view auto v3 = vec | raco;  // ok、v1と同じ意味
}
```

`my_original_adaptor`はここでも実装を省略していますが、そこについては適切に実装されている必要があります（何かいい例があればいいのですが・・・）。

おそらく、この`my_closure_adaptor`（汎用的なレンジアダプタクロージャオブジェクト型）のようなものは自作のレンジアダプタとは別で作成できて、かつこの例のような典型的な実装になるはずです。そのため、自作のレンジアダプタ毎にこのようなものを作る必要は無いでしょう。この部分がC++23で追加されなかったのは、この部分の最適な実装

宣伝ですが、これらレンジアダプタ（クロージャ）オブジェクトを簡易に作成できるC++20/C++23のライブラリを作っていました。`range_adaptor_closure`や`std::bind_back`相当のものをC++20で使用できるほか、`my_closure_adaptor`相当のものも用意しており、より簡易にレンジアダプタを作成できるようになります。

- [onihusube/rivet - github](https://github.com/onihusube/rivet)

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