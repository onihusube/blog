# ［C++］`owning_view`によるパイプライン安全性の確保

### `owning_view`

ちょうど別に書いたので以下をご参照ください。

- [[C++］ <ranges>のviewを見る19 - owning_view] - Zenn](https://zenn.dev/onihusube/articles/fd07528b68ae0c)

`owning_view`は右辺値の範囲から構築され、それを所有することで右辺値範囲の寿命を延長するものです。定義は簡単なのでコピペしておくと次のようになっています

```cpp
namespace std::ranges {
  template<range R>
    requires movable<R> && (!is-initializer-list<R>) // see [range.refinements]
  class owning_view : public view_interface<owning_view<R>> {
  private:
    R r_ = R(); // exposition only
  public:
    owning_view() requires default_initializable<R> = default;

    // 専ら使用するコンストラクタ
    constexpr owning_view(R&& t) : r_(std​::​move(t)) {}

    owning_view(owning_view&&) = default;
    owning_view& operator=(owning_view&&) = default;

    constexpr R& base() & noexcept { return r_; }
    constexpr const R& base() const& noexcept { return r_; }
    constexpr R&& base() && noexcept { return std::move(r_); }
    constexpr const R&& base() const&& noexcept { return std::move(r_); }

    // Rのイテレータをそのまま使用
    constexpr iterator_t<R> begin() { return ranges::begin(r_); }
    constexpr sentinel_t<R> end() { return ranges::end(r_); }

    // Rがconst-iterableならそうなる
    constexpr auto begin() const requires range<const R>
    { return ranges::begin(r_); }
    constexpr auto end() const requires range<const R>
    { return ranges::end(r_); }

    constexpr bool empty() requires requires { ranges::empty(r_); }
    { return ranges::empty(r_); }
    constexpr bool empty() const requires requires { ranges::empty(r_); }
    { return ranges::empty(r_); }

    // Rがsized_rangeならそうなる
    constexpr auto size() requires sized_range<R>
    { return ranges::size(r_); }
    constexpr auto size() const requires sized_range<const R>
    { return ranges::size(r_); }

    // Rがcontiguous_rangeならそうなる
    constexpr auto data() requires contiguous_range<R>
    { return ranges::data(r_); }
    constexpr auto data() const requires contiguous_range<const R>
    { return ranges::data(r_); }
  };
}
```

ムーブコンストラクタを除くとコンストラクタは一つしかなく、そこでは`R`（`range`かつ`movable`）の右辺値（これはフォワーディングリファレンスではありません）を受け取り、それをメンバ変数`r_`にムーブして保持します。このようにして入力の右辺値範囲の寿命を延長しており、それ以外の部分は見てわかるようにその`R`の薄いラッパです。

### `views::all`と`views::all_t`

`owning_view`を生成するためのRangeアダプタとして`views::all`が用意されていますが、`views::all`は`owning_view`だけでなく`ref_view`も返します。

型`R`のオブジェクト`r`に対して、`views::all(r)`のように呼ばれた時の効果は

1. `R`が[`view`](https://cpprefjp.github.io/reference/ranges/view.html)のモデルであるなら、`r`をdecay-copyして返す
      - decay-copyは`r`をコピーorムーブしてその型の新しいオブジェクトを作ってそれを返すこと 
2. `r`が左辺値なら`ref_view(r)`
3. `r`が右辺値なら`owning_view(std::move(r))`

このように、`views::all`は`range`を入力として`view`を返すもので、別の言い方をすると`range`を`view`に変換するものです。`views::all`を主体としてみれば、`ref_view`とか`owning_view`の区別は重要ではないため、この2つをまとめて（あるいは、`views::all`による`view`を）*All view*と呼びます。

`<ranges>`のRangeアダプタと呼ばれる`view`は、任意の`view`を入力として何か操作を適用した`view`を返すものです。そのため、Rangeアダプタ（の実態の`view`型）に`range`を渡すためには一度`view`に変換する必要があり、`views::all`はその変換を担うRangeアダプタとして標準に追加されています。とはいえ、ユーザーがRangeアダプタを使用する際に一々`views::all`を使用しなければならないのかといえばそうではなく、この適用は*All view*を除く全てのRangeアダプタにおいて自動で行われます。そのため通常は、ユーザーが`views::all`および`ref_view`や`owning_view`を直接使う機会は稀なはずです。

`views::all`の自動適用は推論補助をうまく利用して行われています。簡易な実装を書いてみると

```cpp
using namespace std::ranges;

// 任意のviewとする
template<view V>
class xxx_view {
  V base_;

public:
  // viewを受け取るコンストラクタ
  xxx_view(V v) : base_(std::move(v)) {}

};

// この推論補助がミソ！
template<range R>
xxx_view(R&&) -> xxx_view<views::all_t<R>>;
```

`views::all_t`は`views::all`の戻り値型を求めるもので、次のように定義されます。

```cpp
namespace std::ranges::views {

  template<viewable_range R>
  using all_t = decltype(all(declval<R>()));
}
```

先ほどの`xxx_view`を`xxx_view{r}`のように使用した時、クラステンプレートの実引数推定が起こることによって1つだけ定義されている推論補助が使用され、`r`の型`R`を`views::all_t<R>`のように通して、`views::all(r)`の戻り値型を`xxx_view`のテンプレートパラメータ`V`として取得します。`views::all`の戻り値型は、`R`が`view`ならその`view`型（*prvalue*としての素の型）、`R`が左辺値なら`ref_view{r}`、`r`が右辺値なら`owning_view{r}`を返します。つまり、`views::all_t<R>`は常に`R`を変換した`view`のCV修飾なし参照なしの素の型（*prvalue*）を得ます。

そうして得られた型を`V`とすると、`xxx_view{r}`は`xxx_view<V>{r}`のような初期化式になります。`xxx_view`（および標準Rangeアダプタ）の`view`を受け取るコンストラクタは`explicit`がなく、テンプレートパラメータに指定された`view`型（`V`、これは実引数`r`の型`R`に対して`views::all_t<R>`の型）を直接受けるものであるため、そのコンストラクタ引数では`R -> V`の暗黙変換によって`views::all(r)`を通したのと同じことが起こり、ここでようやく`views::all`の自動適用が行われます。

これと同じことが、*All view*を除く全てのRangeアダプタの`view`型で実装されており、これによって、Rangeアダプタは`views::all`を自動適用して`view`を受け取っています。これは`xxx_view`に対して`views::xxx`の名前のRangeアダプタを使用した時でも同様です（その効果では結局、何かしらの`view`型を適用することになるため）。

```cpp
#include <ranges>
#include <vector>

auto f() -> std::vector<int>&;
auto g() -> std::vector<int>;

using namespace std::ranges;

int main() {
  auto tv = take_view{f(), 5};
  // decltype(tv) == take_view<ref_view<std::vector<int>>>

  auto dv = drop_view{g()}, 2;
  // decltype(dv) == drop_view<owning_view<std::vector<int>>>

  auto dtv = drop_view{tv, 2};
  // decltype(dtv) == drop_view<take_view<ref_view<std::vector<int>>>>

  auto ddv = dv | views::drop(2);
  // decltype(ddv) == drop_view<drop_view<owning_view<std::vector<int>>>>

  auto ddv2 = drop_view{dv, 2};
  // decltype(ddv2) == drop_view<drop_view<owning_view<std::vector<int>>>>
}
```

### パイプラインで起こること

個別の`view`型で起こることはわかったかもしれませんが、実際に起こることはイメージしづらいものがあります。

```cpp
#include <ranges>
#include <vector>

auto f() -> std::vector<int>;

using namespace std::views;

int main() {
  // pipesの型は？構造は？？
  auto pipes = f() | drop(2)
                   | filter([](int n) { return 0 < n; })
                   | transform([](int n) { return n * n; })
                   | take(5);

  // 安全、f()の戻り値はowning_viewによって寿命延長されている
  for (int m : pipes) {
    std::cout << n << ',';
  }
}
```

例えばこのようなRangeアダプタによるパイプラインの結果として得られた`pipes`は、どんな型を持ちどんな構造になっているのでしょうか？また、`f()`の結果（右辺値）は`owning_view`によって安全に取り回されているはずですが、`pipes`のどこにそれは保持されているのでしょうか？

### 参考文献

- [P2415R2 What is a view?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2415r2.html)
- [What is `std::views::all` introduced for in C++20?](https://stackoverflow.com/questions/67335254/what-is-stdviewsall-introduced-for-in-c20)
- [`<ranges>` - cpprefjp](https://cpprefjp.github.io/reference/ranges.html)