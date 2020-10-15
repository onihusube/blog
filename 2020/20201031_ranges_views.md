# ［C++］ `<range>`の*View*

## 前準備

### コンセプトによる定義

#### `range<T>`

```cpp
template<class T>
concept range =
  requires(T& t) {
    ranges::begin(t);
    ranges::end(t);
  };
```

#### `borrowed_range<T>`

```cpp
template<class T>
concept borrowed_­range =
  range<T> &&
  (is_lvalue_reference_v<T> || enable_borrowed_range<remove_cvref_t<T>>);

template<class>
inline constexpr bool enable_borrowed_range = false;
```

#### `sized_range<T>`

```cpp
template<class T>
concept sized_­range =
  range<T> &&
  requires(T& t) { ranges::size(t); };
```

#### `views<T>`

```cpp
template<class T>
concept view =
  range<T> && movable<T> && default_­initializable<T> && enable_view<T>;

template<class T>
inline constexpr bool enable_view = derived_from<T, view_base>;
```

#### *range*のカテゴリ

#### `common_range<T>`

```cpp
template<class T>
concept common_­range =
  range<T> && same_­as<iterator_t<T>, sentinel_t<T>>;
```
#### `viewable_range<T>`

```cpp
template<class T>
concept viewable_­range =
  range<T> && (borrowed_range<T> || view<remove_cvref_t<T>>);
```


### `view_interface`

### `subrange`

## *View*について

*range*ライブラリにおける*View*とは、他の所（言語、ライブラリ、概念・・・）での任意のシーケンスに対する*View*と呼ばれるものと同じ意味です。元のシーケンスに対して何か操作を適用した結果得られ、元のシーケンスをコピーせず参照し、かつ遅延評価によってシーケンスに操作を適用するものです。  
さらに、*View*自身もシーケンスなので*View*に対してさらに他の処理を適用していくことができるようになっています。

*range*ライブラリにおける*View*はコンセプトによって構文・意味論の両方向から次のように定義されます。

```cpp
template<class T>
concept view =
  range<T> &&                 // begin()/end()によってイテレータペアを取得可能
  movable<T> &&               // ムーブ可能
  default_­initializable<T> && // デフォルト構築可能
  enable_view<T>;             // viewコンセプトを有効化する変数テンプレート
```

- ムーブ構築/代入は定数時間
- デストラクトは定数時間
- コピー不可もしくは、コピー構築/代入は定数時間

この定義に沿う型が*range*ライブラリにおける*View*として扱われます。

分かりづらいかもしれませんが意味するところはすなわち、任意のシーケンスを所有せずに参照し、*View*自身の構築・コピー・ムーブ・破棄は参照する範囲とは無関係であるということです。

実際の実装はほぼ間違いなくイテレータペア（*range*）を保持するクラス型となり、*View*にまつわる操作は`begin()`の呼び出し時、あるいはそのイテレータに対する`++, *`等の操作のタイミングで実行されることによって遅延評価されることになるでしょう。

標準ライブラリにある*View*であるクラス型にはたとえば`std::string_view`があります。`std::string_view`は自身も*range*であり、ムーブやデフォルト構築が可能で、単に文字列の先頭ポインタと長さを保持するものなので、構文的にも意味論的にもこの定義に沿っています。  
ただし、`std::ranges::enable_view<std::string_view>`（上記コンセプト定義の一番最後の条件）が`false`となるので`std::string_view`は`view`コンセプトを満たしません。`enable_view`は`view`コンセプトを有効化するための最後の一押しです。

### `view_interface`

`<ranges>`にある*View*となるクラスは共通部分の実装を簡略化するために`view_interface`というクラスを継承しています。`view_interface`はCRTPによって派生クラス型を受け取り、派生している*View*に対してコンテナインターフェースを備えるためのものです。  
これによって、`empty()/data()/size()/front()/back()/operator[]`と言った要素を参照する操作が利用可能となります（ただし、*View*の参照する*range*の種類（すなわち、イテレータカテゴリ）によります）。

```cpp
template<class D>
  requires is_class_v<D> && same_as<D, remove_cv_t<D>>
class view_interface : public view_base {
  // 略
};
```

`view_base`というのは単なるタグ型で、*View*となるクラスを識別するためのものです。*View*の型`D`に求めらているのはクラス型でありCV修飾されていない事だけです。自分で*View*を定義する時もこれを利用すると良いでしょう。ちなみに、これを継承しておくと`std::ranges::enable_view<T>`が自動的に`true`となるようになっています。

### *View*の命名規則と操作

`<ranges>`にある*View*は`操作名_view`という名前でクラスとして`std::ranges`名前空間に定義されており、*range*オブジェクトを渡して構築することでその操作を行う*View*オブジェクトを得ることができます。そして、その操作に対応する`view`を作成するための関数オブジェクト（時々変数テンプレート）が`std::ranges::views`名前空間に`操作名_view`に対して`操作名`で定義されています。こちらを用いると*View*を得る操作を簡潔に書くことができます。

名前空間名は真面目に書くと長いですが`std::views`という名前空間エイリアスが用意されており、そちらを用いると少し短く書けます。

この様な関数オブジェクトには、*range factories*と*range adaptor objects*の2種類があります。

## `empty_view`

`empty_view<T>`は型`T`の空のシーケンスを表す*View*です。

```cpp
#include <ranges>

int main() {
  std::ranges::empty_view<int> ev{};

  for (int n : ev) {
    assert(false);  // 呼ばれない
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/eJq2oHSPjhPhaDZS)

これは次のように定義されます。

```cpp
namespace std::ranges {
  template<class T>
    requires is_object_v<T>
  class empty_view : public view_interface<empty_view<T>> {
  public:
    static constexpr T* begin() noexcept { return nullptr; }
    static constexpr T* end() noexcept { return nullptr; }
    static constexpr T* data() noexcept { return nullptr; }
    static constexpr size_t size() noexcept { return 0; }
    static constexpr bool empty() noexcept { return true; }
  };

  namespace views {
    // 変数テンプレート
    template<class T>
    inline constexpr empty_view<T> empty{};
  }
}
```

使いどころはすぐには思いつきませんが、*range*を取るアルゴリズムに対してあえて空の*range*を渡したい場合に利用することができるでしょうか。そのような場合、型`T`を与えるだけで空の*range*を得ることができるのでお手軽です。

この定義からわかるように、`empty_view`の*range*は*contiguous range*（イテレータが*contiguous iterator*の範囲）です。

### range factories

`std::views`（`std::ranges::views`）名前空間にある変数テンプレートを用いると空の*View*を取得するという操作を若干簡潔に書くことができます。

```cpp
#include <ranges>

int main() {
  for (int n : std::views::empty<int>) {
    assert(false);  // 呼ばれない
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/RgtkTNZWIszHh5NW)


`std::views`名前空間にあるこの様な*View*クラスに対応する操作を表す関数オブジェクト（時々変数テンプレート）の事を、*range factory*と呼びます。

## `single_view`

`single_view<T>`は型`T`の要素を1つだけ持つシーケンスを作成する*View*です。

```cpp
#include <ranges>

int main() {
  std::ranges::single_view<int> sv{20};

  for (int n : sv) {
    std::cout << n; // 1度だけ呼ばれる
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/DOiFMbDf8ZTY2gLL)

これもまた*range*を取るアルゴリズムに対してあえて1要素の*range*を入れたい場合など、1要素シーケンスが欲しい時に活用できるでしょう。

これは次のように定義されます。

```cpp
namespace std::ranges {
  template<copy_constructible T>
    requires is_object_v<T>
  class single_view : public view_interface<single_view<T>> {
  private:
    semiregular-box<T> value_;  // 説明専用メンバ変数
  public:
    single_view() = default;
    constexpr explicit single_view(const T& t);
    constexpr explicit single_view(T&& t);
    template<class... Args>
      requires constructible_from<T, Args...>
    constexpr single_view(in_place_t, Args&&... args);

    constexpr T* begin() noexcept;
    constexpr const T* begin() const noexcept;
    constexpr T* end() noexcept;
    constexpr const T* end() const noexcept;
    static constexpr size_t size() noexcept;
    constexpr T* data() noexcept;
    constexpr const T* data() const noexcept;
  };
}
```

`single_view`もまた、*contiguous range*（イテレータが*contiguous iterator*の範囲）です。

4つ目のコンストラクタは`T`のオブジェクトを内部で*in place*構築するためのものです。`args...`にコンストラクタ引数を渡す事で、直接コンストラクタを呼んで構築することができます。

```cpp
int main() {
  
  // std::stringのコンストラクタを呼び出してもらう
  std::ranges::single_view<std::string> sv(std::in_place, "in place construct", 8);

  for (auto& str : sv) {
    std::cout << str; // in place
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Q7Ouic65XAJA9Tju)

### range factories

`single_view`にも*range factory*となる関数オブジェクトが用意されています。これを用いると幾分か記述を省略できます。

```cpp
int main() {
  for (auto& str : std::views::single(std::string{"in place construct", 8})) {
    std::cout << str;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/qYMOXBqAcVHLWGN6)

この`std::view::single`はカスタマイゼーションポイントオブジェクトであり、`std::view::single(arg)`のように呼び出すと`std::ranges::single_view{arg}`を構築して返してくれます（無論、引数は完全転送されます）。  
ただし、このCPOは1引数しか受け付けないため、*in place*コンストラクタを呼び出すことはできません。

## `iota_view`

`iota_view`は渡された2つの値をそれぞれ始点と終点として、単調増加するシーケンスを作成する*View*です。  
整数型に限定するならば、`init, bound`の2つの値を渡すと[init, bound)の範囲で1づつ増加していく数列を生成します。

```cpp
#include <ranges>

int main() {
  std::ranges::iota_view iv{1, 10};

  for (int n : iv) {
    std::cout << n; // 123456789
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/1ITXZXmU2yOpSJYE)

また、引数1つだけで構築した場合は終端のない無限列を生成します。

```cpp
#include <ranges>

int main() {
  std::ranges::iota_view iv{1};

  for (int n : iv) {
    std::cout << n;     // 1234567891011121314151617181920
    if (n == 20) break; // 何かしら終わらせる条件がないと無限ループ
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/niHMzCrLfiHNcA76)

このような無限列は、*range adaptor*と呼ばれる*View*と組み合わせる事で有効活用することができます（後の方で紹介予定）。

基本的には整数列を生成するために使用すれば良いのですが、この実体はインクリメント可能であり距離を定義できさえすればどんな型の単調増加シーケンスでも作成可能です。これは[`std::weakly_incrementable`](https://cpprefjp.github.io/reference/iterator/weakly_incrementable.html)コンセプトによって制約されます。  
例えば、ポインタ型やイテレータ型のシーケンスを作成可能です。


```cpp
int main() {
  
  int array[] = {2, 4, 6, 8, 10};
  
  // ポインタのインクリメントシーケンス
  std::ranges::iota_view iva{std::ranges::begin(array), std::ranges::end(array)};

  for (int* p : iva) {
    std::cout << *p;  // 246810
  }
  
  std::cout << '\n';
  
  std::list list = {1, 3, 5, 7, 9}; 
  
  // listイテレータのインクリメントシーケンス
  std::ranges::iota_view ivl{std::ranges::begin(list), std::ranges::end(list)};

  for (auto it : ivl) {
    std::cout << *it; // 13579
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/3jbhn5RgULKqGeiy)

正直このジェネリックな振る舞いは使いどころがあるのか分かりません。頭の片隅に置いておくと役立つこともあるでしょうか・・・？  
なお、`<ranges>`の*View*はおおよそ全てがこの様になるべく~~無駄に~~ジェネリックに動作可能なように設計されています。

なお、浮動小数点数型は`std::weakly_incrementable`を満たさないので`iota_view`では使用できません。距離を整数値で定義できないのが原因のようです。

### 遅延評価

`iota_view`によって生成されるシーケンスは`iota_view`オブジェクトを構築した時点では生成されておらず、その生成は遅延評価されます。

具体的には、`iota_view`オブジェクトから得られるイテレータのインクリメント（`++i/i++`）のタイミングで1つづつシーケンスの要素が計算されます。

```cpp
int main() {
  std::ranges::iota_view iv{1, 10}; // この段階ではまだ何もしてない

  auto it = std::ranges::begin(iv); // この段階ではまだ何もしてない

  int n1 = *it; // 初項（1）が得られる
  ++it;         // ここで次の項（2）が計算される
  it++;         // ここで次の項（3）が計算される
  int n2 = *it; // 3番目の項（3）が得られる  
}
```

### *range*カテゴリ

`iota_view`の表す*range*はその要素型によって*range*カテゴリが変化します。整数型で使用する分には常に*random access range*ですが、そのほかの型の場合は可能な操作によって弱くなる可能性があります。例えば、`std::list`のイテレータによる`iota_view`オブジェクトは*bidirectional range*になります。

*random access range*となる`iota_view`のシーケンスは、そのイテレータに対して`--, +=, -=`等でシーケンス上をほぼ自由に移動でき、*bidirectional range*となる場合は`++, --`によって前後方向への移動が可能になります。

### range factories

`iota_view`にも*range factory*となる関数オブジェクトが用意されています。


```cpp
#include <ranges>

int main() {
  for (int n : std::views::iota(1, 10)) {
    std::cout << n;   // 123456789
  }
  
  std::cout << '\n';

  for (int n : std::views::iota(1)) {
    std::cout << n;   // 1234567891011121314151617181920
    if (n == 20) break;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/niHMzCrLfiHNcA76)

この`std::views::iota`はカスタマイゼーションポイントオブジェクトで、1つか2つの引数を受け取りその引数をそのまま転送して`iota_view`オブジェクトを生成し返します。

## `basic_istream_view`

