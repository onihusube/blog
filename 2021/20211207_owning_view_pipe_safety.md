# ［C++］`owning_view`によるパイプライン安全性の確保

この記事は[C++ Advent Calendar 2021](https://qiita.com/advent-calendar/2021/cxx)の7日目の記事です。

### `owning_view`

`owning_view`については、ちょうど別に書いたので以下もご参照ください。

- [`<ranges>`の`view`を見る19 - `owning_view` - Zenn](https://zenn.dev/onihusube/articles/fd07528b68ae0c)

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

    // ムーブコンストラクタ/代入演算子
    owning_view(owning_view&&) = default;
    owning_view& operator=(owning_view&&) = default;

    // 保持するRのオブジェクトを取得する
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

ムーブコンストラクタを除くとコンストラクタは一つしかなく、そこでは`R`（`range`かつ`movable`）の右辺値（これはフォワーディングリファレンスではありません）を受け取り、それをメンバ変数`r_`にムーブして保持します。このようにして入力の右辺値範囲の寿命を延長しており、それ以外の部分は見てわかるように元の`R`の薄いラッパです。

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

// 任意のview
template<view V>
class xxx_view {
  V base_;

public:
  // 入力viewを受け取るコンストラクタ
  xxx_view(V v) : base_(std::move(v)) {}

};

// この推論補助が重要！
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

この`xxx_view`を`xxx_view{r}`のように使用した時、クラステンプレートの実引数推定が起こることによって1つだけ定義されている推論補助が使用され、`r`の型`R`を`views::all_t<R>`のように通して、`views::all(r)`の戻り値型を`xxx_view`のテンプレートパラメータ`V`として取得します。`views::all`の戻り値型は、`r`が`view`ならその`view`型（*prvalue*としての素の型）、`r`が左辺値なら`ref_view{r}`、`r`が右辺値なら`owning_view{r}`を返します。つまり、`views::all_t<R>`は常に`R`を変換した`view`のCV修飾なし参照なしの素の型（*prvalue*）を得ます。

そうして得られた型を`V`とすると、`xxx_view{r}`は`xxx_view<V>{r}`のような初期化式になります。`xxx_view`（および標準Rangeアダプタの`view`）の`view`を受け取るコンストラクタは`explicit`がなく、テンプレートパラメータに指定された`view`型（`V`、これは実引数`r`の型`R`に対して`views::all_t<R>`の型）を値として受けるものであるため、そのコンストラクタ引数では`R -> V`の暗黙変換によって`views::all(r)`を通したのと同じことが起こり、ここで`views::all`の自動適用が行われます。

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

個別の`view`型で起こることはわかったかもしれませんが、実際に使用した時に起こることはイメージしづらいものがあります。

```cpp
#include <ranges>
#include <vector>

auto f() -> std::vector<int>;

auto even = [](int n) { return 0 < n; };
auto sq = [](int n) { return n * n; };

using namespace std::views;

int main() {
  // pipesの型は？構造は？？
  auto pipes = f() | drop(2)
                   | filter(even)
                   | transform(sq)
                   | take(5);

  // 安全、f()の戻り値はowning_viewによって寿命延長されている
  for (int m : pipes) {
    std::cout << n << ',';
  }
}
```

例えばこのようなRangeアダプタによるパイプラインの結果として得られた`pipes`は、どんな型を持ちどんな構造になっているのでしょうか？また、`f()`の結果（右辺値）は`owning_view`によって安全に取り回されているはずですが、`pipes`のどこにそれは保持されているのでしょうか？

先程の`views::all/views::all_t`の標準Rangeアダプタでの使われ方を思い出すと、`pipes`の型はわかりそうです。

1行目の`f() | drop(2)`では[`drop_view`](https://cpprefjp.github.io/reference/ranges/drop_view.html)（`views::drop(2)`による）の構築が行われ、`f()`の戻り値を`r`とすると`drop_view{r, 2}`が構築されます。前述の通り、そこでは`views::all`が自動適用され、`r`は右辺値`std::vector<int>`なのでその結果は`owning_view{r}`が帰ります。したがって、この行で生成されるオブジェクトの型は`drop_view<owning_view<std::vector<int>>>`となります。

その結果を`v1`として、次の行`v1 | filter(even)`では[`filter_view`](https://cpprefjp.github.io/reference/ranges/filter_view.html)が、`filter_view{v1, even}`のように構築されます。ここでも`views::all`が自動適用されていますが、`views::all(v1)`は`v1`が既に`view`であるため、それがそのまま（decay-copyされて）帰ります。したがって、この行で生成されるオブジェクトの型は`filter_view<drop_view<owning_view<std::vector<int>>>, even_t>`となります（述語`even`のクロージャ型を`even_t`としています）。

パイプラインの2段目以降では`views::all`の適用はほぼ恒等変換となるため、`views::all_t`の型を気にする必要があるのはパイプラインの一番最初だけです。後の行およびその他のRangeアダプタの適用時に起きることも同じようになるため、この2行目で起きている事がわかれば後は簡単です。ただし、Rangeアダプタオブジェクトの返す型に注意が必要ではあります。

```cpp
auto pipes = f() | drop(2)        // V1 = drop_view<owning_view<std::vector<int>>>
                 | filter(even)   // V2 = filter_view<V1, even_t>
                 | transform(sq)  // V3 = transform_view<V2, sq_t>
                 | take(5);       // V4 = take_view<V3>
```

略さずに書くと`decltype(pipes) == take_view<transform_view<filter_view<drop_view<owning_view<std::vector<int>>>, even_t>, sq_t>>`となります。標準`view`型は入力の`view`をテンプレートの1つ目の引数として取るので、パイプライン前段の`view`型が、次の段の`view`型の第一テンプレート引数としてはまっていきます。

型がわかれば、そのオブジェクト構造がなんとなく見えてきます。しかし、標準`view`型の個々のクラス構造がわからないとこのパイプライン全体の構造も推し量る事ができません。

標準`view`型（主にRangeアダプタ）の型としての構造（第一テンプレート引数に入力`view`をとる、推論補助によって`views::all_t`を自動適用する）がある程度一貫していたように、そのクラス構造もまたある程度の一貫性があります。そこでは、入力の`view`オブジェクトをコンストラクタで値として受け取って、メンバ変数にムーブして保持しています。

```cpp
using namespace std::ranges;

// 任意のview
template<view V, ...>
class xxx_view {
  // 入力viewをメンバとして保持
  V base_ = V();

public:
  // 入力view（と追加の引数）を受け取るコンストラクタ
  xxx_view(V v, ...) : base_(std::move(v)) {}

};
```

[`view`コンセプト](https://cpprefjp.github.io/reference/ranges/view.html)の定義する`view`とは、ムーブ構築が`O(1)`で行えて、ムーブされた回数`N`と要素数`M`から（ムーブ後`view`を含む）`N`個のオブジェクトの破棄が`O(N+M)`で行えて、ムーブ代入の計算量は構築と破棄を超えない程度、であるような型です。`owning_view`のような例外を除けば、これは範囲を所有せずに`range`となるような型を指定しており、ムーブ構築のコストは範囲の要素数と無関係に行える事を示しています（ここでは`view`のコピーについては触れないことにします）。  
`owning_view`は範囲を所有しますが、ムーブオンリーであるため`view`コンセプトの要件を満たすことができる、少し特殊な`view`型です。

`views::all_t<R>`は`R`が`view`である時に`R`の素の型（*prvalue*としての型）を返します。それは右辺値`R&&`と左辺値`R&`および`const R`に対して、`R`となる型です。このようなCV修飾なし参照なしの型が`view`型の入力`V`となるため、`V`のオブジェクト`rv`（これはパイプライン内では右辺値）はコンストラクタ引数`v`に対してまずムーブされ、メンバ`base_`として保持するためにもう一度ムーブされます。`V`が`ref_view`をはじめとする範囲を所有しないタイプの`view`である時、その参照を含む`view`オブジェクトごとムーブ（コピー）されメンバとして保存されます。`V`が`owning_view`のように範囲を所有する`view`の場合、その所有権ごと`view`オブジェクトをムーブしてメンバとして保存します。その後、そうして構築された`view`オブジェクトは、パイプラインの次の段で同様に次の`view`オブジェクト内部にムーブして保持されます。

パイプラインの格段でこのような一時`view`オブジェクトのムーブが起きているため、最初に構築された`ref_view or owning_view`オブジェクトは最後まで捨てられることなく、パイプラインの一番最後に作成されたオブジェクト内に保持されます。そして、パイプラインの段が重なるごとに、それを包むようにRangeアダプタの`view`の層が積み重なっていきます。

イメージとしてはマトリョーシカとか玉ねぎとかそんな感じで、一番中心にパイプラインの起点となった入力`range`を参照or所有する`view`オブジェクトが居て、それは通常`ref_view`か`owning_view`のどちらかとなります。

```cpp
#include <ranges>
#include <vector>

auto f() -> std::vector<int>;

auto even = [](int n) { return 0 < n; };
auto sq = [](int n) { return n * n; };

using namespace std::views;

int main() {
  // f()の戻り値はpipesの奥深くにしまわれている・・・
  auto pipes = f() | drop(2)
                   | filter(even)
                   | transform(sq)
                   | take(5);

  // 安全、f()の戻り値は生存期間内
  for (int m : pipes) {
    std::cout << n << ',';
  }
}
```

構造を簡単に書いてみると次のようになっています

- `pipes : take_view`
    - `base_ : transform_view`
      - `base_ : filter_view`
        - `base_ : drop_view`
          - `base_ : owning_view`
            - `r_ : std::vector<int>`
        - `pred_ : even_t`
      - `fun_ : sq_t`

（変数名は規格書のものを参考にしていますが、この名前で存在するわけではありません）

このようにして、`f()`の戻り値である右辺値の`std::vector`オブジェクトの寿命は、パイプラインを通しても延長されています。`views::filter`が受け取る述語オブジェクトなども対応する層（`view`オブジェクト内部）に保存されており、同様に安全に取り回し、使用する事ができます。

#### `ref_view`の場合

先ほどの例の`f()`が左辺値を返している場合、パイプライン最初の`drop_view`構築時の`views::all`適用時には、`ref_view`が適用されます。

```cpp
#include <ranges>
#include <vector>

auto f() -> std::vector<int>&;

auto even = [](int n) { return 0 < n; };
auto sq = [](int n) { return n * n; };

using namespace std::views;

int main() {
  // f()の戻り値は参照されている
  auto pipes = f() | drop(2)
                   | filter(even)
                   | transform(sq)
                   | take(5);

  // f()で返されるvectorの元が生きていれば安全
  for (int m : pipes) {
    std::cout << n << ',';
  }
}
```

この時の`pipes`の型は先ほど`owning_view<std::vector<int>>`だったところが`ref_view<std::vector<int>>`に代わるだけで、他起こることは同じです。

`ref_view`は次のように定義されています。

```cpp
namespace std::ranges {
  // コンストラクタ制約の説明専用の関数
  void FUN(R&);
  void FUN(R&&) = delete;

  template<range R>
    requires is_object_v<R>
  class ref_view : public view_interface<ref_view<R>> {
  private:
    // 参照はポインタで保持する
    R* r_;  // exposition only

  public:

    // 左辺値を受け取るコンストラクタ
    template<different-from<ref_view> T>
      requires convertible_to<T, R&> &&         // T(右辺値or左辺値参照)がR&(左辺値参照)へ変換可能であること
               requires { FUN(declval<T>()); }  // tが右辺値ならFUN(R&&)が選択され制約を満たさない
    constexpr ref_view(T&& t)
      : r_(addressof(static_cast<R&>(std​::​forward<T>(t))))
    {}

    constexpr R& base() const { return *r_; }

    constexpr iterator_t<R> begin() const { return ranges::begin(*r_); }
    constexpr sentinel_t<R> end() const { return ranges::end(*r_); }

    constexpr bool empty() const
      requires requires { ranges::empty(*r_); }
    { return ranges::empty(*r_); }

    constexpr auto size() const requires sized_range<R>
    { return ranges::size(*r_); }

    constexpr auto data() const requires contiguous_range<R>
    { return ranges::data(*r_); }
  };

  // 推論補助、左辺値参照からしか推論できない
  template<class R>
  ref_view(R&) -> ref_view<R>;
}
```

コンストラクタはかなりややこしいですが、推論補助と組み合わさって、確実に左辺値のオブジェクトだけを受け取るようになっています。そして、`ref_view`は参照する範囲へのポインタを保持してラップすることで`range`型`R`を`view`へと変換します。また、あえて定義されてはいませんが、`ref_view`のコピー/ムーブ・コンストラクタ/代入演算子は暗黙定義されています。

パイプラインへの入力が左辺値である場合、パイプラインによって生成されたマトリョーシカの中心には`ref_view`がおり、そこからは元の範囲をポインタによって参照しているわけです。

`ref_view`はデフォルト構築不可能であるので、メンバのポインタ`r_`が`nullptr`となることを考慮する必要はないですが、参照先の`range`オブジェクトが先に寿命を迎えれば容易にダングリングとなります。また、ポインタの関節参照のコストも（おそらく最適化で除去可能であるとはいえ）かかることになります。`owning_view`が好まれたのは、これらの問題と無縁であることも理由の一つです。

### 参考文献

- [P2415R2 What is a view?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2415r2.html)
- [What is `std::views::all` introduced for in C++20?](https://stackoverflow.com/questions/67335254/what-is-stdviewsall-introduced-for-in-c20)
- [`<ranges>` - cpprefjp](https://cpprefjp.github.io/reference/ranges.html)


[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2021/20211207_owning_view_pipe_safety.md)
