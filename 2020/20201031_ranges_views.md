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

## `istream_view`

`istream_view<T>`は任意の`istream`が示す入力ストリーム上にある`T`の値のシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // 標準入力に"1 2 3 4 5 6"のように入力したとする
  for (int n : std::ranges::istream_view<int>(std::cin)) {
    std::cout << n; // 123456
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/2hOyESIGsmHxFtoC)

要は[`std::istream_iterator`](https://cpprefjp.github.io/reference/iterator/istream_iterator.html)を`<range>`における*View*として再設計したものです。

その特性上`istream_view`は常に*input range*となり、一方向性でマルチパス保証がありません。そのため`istream_view`のイテレータはムーブオンリーです。

### `basic_istream_view`

`istream_view<T>`というのは実は*View*クラスではなくて*range factory*に対応する関数です。`istream_view`の実体は`basic_istream_view`というクラスで、`istream_view`は任意の`istream`を引数に受け取り、それを用いて`basic_istream_view`オブジェクトを構築して返します。

この`basic_istream_view`が*View*クラスであり次のように定義されています。

```cpp
namespace std::ranges {

  template<movable Val, class CharT, class Traits>
    requires default_initializable<Val> &&
             stream-extractable<Val, CharT, Traits>
  class basic_istream_view : public view_interface<basic_istream_view<Val, CharT, Traits>> {
  public:
    basic_istream_view() = default;
    constexpr explicit basic_istream_view(basic_istream<CharT, Traits>& stream);

    constexpr auto begin()
    {
      if (stream_) {
        *stream_ >> object_;
      }
      return iterator{*this};
    }

    constexpr default_sentinel_t end() const noexcept;

  private:
    struct iterator;                                    // 説明専用メンバ変数
    basic_istream<CharT, Traits>* stream_ = nullptr;    // 説明専用メンバ変数
    Val object_ = Val();                                // 説明専用メンバ変数
  };
}
```

`basic_istream_view`は3つのテンプレートパラメータ（シーケンスの要素型、ストリームの文字型、文字型の`traits`）を受け取るのですが、最初の要素型`Val`を必ず指定しなければいけないためにテンプレート引数推論を行えず、これを直接使おうとすると3つのテンプレートパラメータ全てを指定しなければなりません。

これは地味に面倒なので利用するときは`std::ranges::istream_view<T>()`を用いるといいでしょう（なお、`std::views::istream_view`はありません）。これは、要素型だけを指定して入力ストリームを渡せば、残り2つのテンプレートパラメータは引数の`istream`の型から取得して補ってくれます。  
なお、この記事では`basic_istream_view`による*View*を指して`istream_view`と呼びます。

### 遅延評価

上記定義を見るとピンとくるかもしれませんが`istream_view`は遅延評価されます。`istream_view`によって生成されるシーケンスは`istream_view`オブジェクトを構築した時点では生成されていません。

まず、`istream_view`オブジェクトから`begin()`によってイテレータを取得した時点で最初の要素が計算（読み取り）されます。そして、インクリメント（`++i/i++`）のタイミングで1つづつ後続の要素が計算されます。

```cpp
int main() {
  // 標準入力に"1 2 3 4 5 6"のように入力したとする

  auto iv = std::ranges::istream_view<int>(std::cin); // この段階ではまだ何もしてない

  auto it = std::ranges::begin(iv); // この段階で最初の要素（1）が読み取られる

  int n1 = *it; // 最初の要素（1）が得られる
  ++it;         // ここで次の要素（2）が読み取られる
  it++;         // ここで次の要素（3）が読み取られる
  int n2 = *it; // 3番目の要素（3）が得られる  
}
```

この事によって、`istream_view`によるシーケンスは通常のシーケンスとは異なりメモリ上に空間的に存在するのではなく、ストリーム上に時間的に存在しています。すなわち、`istream_view`を構築したタイミングで入力データが全て到着している必要はなく、任意のタイミングで到着しても構いません。  
この事は、C#におけるLINQに対するRxの対応と同じです。

シーケンス終端の判定は、ストリーム上にデータが残っているかによって行われます（`std::basic_ios`の[`operator bool`](https://cpprefjp.github.io/reference/ios/basic_ios/op_bool.html)が用いられます）。入力が無い状態でイテレータをインクリメントするとおそらくブロックすることになります。

```cpp
int main() {
  // 標準入力に"1 2"のように入力したとする

  auto iv = std::ranges::istream_view<int>(std::cin);
  auto it = std::ranges::begin(iv); // この段階で最初の要素（1）が読み取られる
  auto fin = std::ranges::end(iv);

  it == fin;  // false
  ++it;       // ここで次の要素（2）が読み取られる、ストリーム上のデータはなくなる

  it == fin;  // true
  ++it;       // 次のデータの到着まで待機する（ストリーム実装によるかもしれない？
}
```

### *range factories -> range adaptors*

ここまでで4つの*View*クラス（`empty_view`, `single_view`, `iota_view`, `istream_view`）を見てきました。これらの*View*はどれもシーケンスを生成するもので、他のシーケンスに対して操作を適用したりするものではありません。その振る舞いから、これらの*View*は*range factories*とカテゴライズされます（`std::views`にある関数オブジェクトの事も同時に指しているようなので、すこしややこしいですが・・・）。

おそらく*range*ライブラリの本命たる、他のシーケンスに対して作用するタイプの*View*は*range adaptors*にカテゴライズされ、次回はついにそこに足を踏み入れていきます。

## *range adaptors*

*range adaptors*は他の*View*を含む任意の*range*に対して作用して、特定の操作を適用した*View*に変換するものです。*range adaptor*は*range*から*range*へ操作を適用しつつ変換するものなので、*range adaptor*の結果にさらに*range adaptor*を適用する形で操作をチェーンさせることができます。そして、その最終的な結果もまた*range*として得られます。

*range factories*はシーケンスを生成するタイプの*View*なので*range adaptors*のように他の*range*に作用することはできませんが、*range adaptors*と比較してみると*range factories*は*range adaptors*によるチェーンの起点となる*View*であることが分かるでしょう。

### *range adaptor objects*

*range factories*の*View*型には`std::views`名前空間にその構築を簡略化するための関数オブジェクトなどが用意されていました。これと同様に、*range adaptors*にもその構築を簡略化し明瞭にするための関数オブジェクトが用意されます。これらのものは*range adaptor objects*と呼ばれます。

*range adaptor objects*は第一引数に*range*を取り、戻り値として対応する*View*を返すカスタマイゼーションポイントオブジェクトとして定義されています。

### パイプライン演算子（`|`）と関数呼び出し

*range adaptor*は関数呼び出しによって使用するほかに、パイプライン演算子（`|`）によっても使用することができます。パイプライン演算子によるスタイルはネストした関数呼び出しをその適用順に分解した形で書くことができ、コードの可読性の向上が期待できます。

同じ*range adaptor*については、パイプラインスタイルと関数呼び出しスタイルはどちらを用いても同じ*View*が得られることが保証されています。

```cpp
// R, R1, R2を任意のrange adaptorとする

// この2つの呼び出しは同じViewを返す
R(std::views::iota(1));
std::views::iota(1) | R ;

// この3つの呼び出しも同じViewを返す、さらにrange adaptorが増えても同様
R2(R1(std::views::iota(1)));
std::views::iota(1) | R1 | R2;
std::views::iota(1) | (R1 | R2);

// range adopterが追加の引数を取るときでも、次の3つは同じViewを生成する
R(std::views::iota(1), args...);
R(std::views::iota(1))(args...);
std::views::iota(1) | R(args...)
```

なお、このパイプライン演算子は新しい演算子ではなくて既存のビット論理和演算子をオーバーロードしたものです。


## `ref_view`

`ref_view`は他の*range*を参照するだけの*View*です。

```cpp
#include <ranges>

int main() {
  std::vector vec = {1, 3, 5, 7, 9, 11};

  for (int n : std::ranges::ref_view(vec)) {
    std::cout << n; // 1357911
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/kw9ARGn9rnF6txaB)

右辺値でさえなければ任意の*range*を受けることができて、その*range*を単に参照するだけの*View*となります。`ref_view`の*range*のカテゴリは参照している*range*のものを受け継ぎます。

ぱっと見ると何に使うのか不明ですが、これは`std::vector`などのコピーが気軽にできない*range*の取り回しを改善するために利用できます。そのような*range*の軽量な参照ラッパとなることで、コピーされるかを気にしなくてよくなるなど可搬性が向上します。役割としては、通常のオブジェクトの参照に対する`std::reference_wrapper`に対応しています。  
例えば、`std::async`の追加の引数として渡すときなどのように*decay copy*されてしまう所に渡す場合に活用できるでしょう。

```cpp
struct check {
  check() = default;
  check(const check&) {
    std::cout << "コピーされたよ！" << std::endl;
  }
};

int main()
{
  std::vector<check> vec{};
  vec.emplace_back();
  
  [[maybe_unused]]
  auto f1 = std::async(std::launch::async, [](auto&&) {}, vec); // vectorがコピーされる
  
  [[maybe_unused]]
  auto f2 = std::async(std::launch::async, [](auto&&) {}, std::ranges::ref_view{vec});  // ref_viewがコピーされる
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/rdrLoR3LjOGs7mu2)

また、C++20のRangeライブラリの元となったRange-V3ライブラリでは`zip_view`を構成するためにも利用されているようです。  
例えば、*View*を作ろうとするとデフォルト構築とムーブ構築/代入が少なくとも求められますが、*range*への参照を持つと代入演算子やデフォルトコンストラクタが定義ができなくなり、ポインタを利用する場合は`nullptr`を気にしなければなりません。`view`コンセプトによる*View*の定義を思い出すと、すべての*View*はデフォルト構築可能でムーブ構築/代入が可能であり、`ref_view`もまたそれに従います。  
このように自分で*View*を作成する時など、他の*range*をクラスメンバに持って参照したいときに直接その*range*の参照を持つ代わりに利用することもできます。

比較的短いので定義も見てみましょう。

```cpp
namespace std::ranges {
  template<range R>
    requires is_object_v<R>
  class ref_view : public view_interface<ref_view<R>> {
  private:
    R* r_ = nullptr;  // 説明専用メンバ変数
  public:
    constexpr ref_view() noexcept = default;

    template<not-same-as<ref_view> T>
      requires /*see below*/
    constexpr ref_view(T&& t);

    constexpr R& base() const { return *r_; }

    constexpr iterator_t<R> begin() const { return ranges::begin(*r_); }
    constexpr sentinel_t<R> end() const { return ranges::end(*r_); }

    constexpr bool empty() const
      requires requires { ranges::empty(*r_); }
    { return ranges::empty(*r_); }

    constexpr auto size() const requires sized_­range<R>
    { return ranges::size(*r_); }

    constexpr auto data() const requires contiguous_­range<R>
    { return ranges::data(*r_); }
  };

  template<class R>
    ref_view(R&) -> ref_view<R>;
}
```

このように、`ref_view`自体は対象の*range*へのポインタを保持し、参照する*range*のイテレータをそのまま利用します。

### `views::all`

`ref_view`に対応する*range adaptor object*が`std::views::all`です。

```cpp
#include <ranges>

int main() {
  std::vector vec = {1, 3, 5, 7, 9, 11};

  for (int n : std::views::all(vec)) {
    std::cout << n;
  }

  std::cout << '\n';

  // パイプラインスタイル
  for (int n : vec | std::views::all) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/jX7bqXs8NDkzKgMm)

`views::all`はカスタマイゼーションポイントオブジェクトであり、1つの引数（`r`）を受け取りそれに応じて次の3つのいずれかの結果を返します。

1. `r`が*View*である（ `std::decay_t<decltype(r)>`が`std::ranges::view`コンセプトを満たす）ならば、`r`を*decay copy*して返す
2. `ref_view{r}`が構築可能ならば、`ref_view{r}`
3. それ以外の場合、`std::ranges::subrange{r}`

厳密には`ref_view`だけを生成するわけではないのですが、結果の型を区別しなければ実質的に`ref_view`相当の*View*を得ることができます。

## `filter_view`

`filter_view`は受け取った述語に従って元となる*range*の要素を選別したシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // 奇数をフィルターする（偶数のみ取り出す）
  std::ranges::filter_view fv{std::views::iota(1, 10), [](int n) { return n % 2 == 0; }};
  
  for (int n : fv) {
    std::cout << n; // 2468
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Cj8dbTWeONREFjri)

名前の通りに、元となるシーケンスの要素をフィルターしたシーケンスを得るものです。

`filter_view`の*range*カテゴリは、元となっている*range*のカテゴリによって*bidirectional range*から*input range*まで変化します。ただ、一番強くても*bidirectional range*になります。

入力となるシーケンスもフィルタ条件も任意であり結果もまたシーケンスとなるので、`filter_view`は色々なところで活躍できそうです。

### 遅延評価

*range adopter*全てがそうなのですが、`filter_view`によるシーケンス生成は遅延評価されます。構築時に最初の要素が計算され、残りの要素はイテレータのインクリメントのタイミングで計算されます。

```cpp
// 構築時に条件を満たす最初の要素が探索され、`filter_view`の1番目の要素が計算される
std::ranges::filter_view fv{std::views::iota(1, 10), [](int n) { return n % 2 == 0; }};

auto it = std::ranges::begin(fv);

// 次に条件を満たす要素が探索され、`filter_view`の2番目の要素が計算される
++it;

int n = *it; // 2番目の要素（4）が得られる
```

この例では`iota_view`もまた遅延評価されているので、一連のシーケンス全体が遅延評価によって生成されています。

この様に、`filter_view`に限らず*range adaptor*による処理チェーンは多くの場合可能な限り遅延評価されます。

### `views::filter`

`filter_view`に対応する*range adaptor object*が`std::views::filter`です。


```cpp
#include <ranges>

int main() {
  for (int n : std::views::filter(std::views::iota(1, 10), [](int n) { return n % 2 == 0; })) {
    std::cout << n;
  }

  std::cout << '\n';

  // パイプラインスタイル
  for (int n : std::views::iota(1, 10) | std::views::filter([](int n) { return n % 2 == 0; })) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gzj8H7ZSPsiuqcYO)

`views::filter`もカスタマイゼーションポインオブジェクトであり、*range*と述語オブジェクトを受け取りそれをそのまま転送して`filter_view`を構築して返します。関数呼び出しによって使う場合あまり恩恵はありませんが、パイプラインスタイルで使用するといい感じに書くことができます。

## `transform_view`

`transform_view`は元となるシーケンスの要素それぞれに対して与えられた変換を適用したシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // 各要素を2倍する
  std::ranges::transform_view tv{std::views::iota(1, 5), [](int n) { return n * 2; }};
  
  for (int n : tv) {
    std::cout << n; // 2468
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BBS3Ium3NFWLWvQR)

型`T`のシーケンスと`T -> U`へ変換する関数を受けて、`U`のシーケンスを返すものです。この例では結果も`int`ですが、型を変換することも当然できます。

`transform_view`の*range*カテゴリは、元となっている*range*のカテゴリをそのまま継承します。ただし、*contiguous range*にはなりません。

`transform_view`は`filter_view`と共に*range*アルゴリズムの基礎となる*View*であり、多くの所で活用できるでしょう。

### 遅延評価

`transform_view`もまた、遅延評価によってシーケンスを生成します。イテレータの`*`による参照のタイミングで要素の読み出しと変換の適用が行われます。

```cpp
// transform_view構築時にはまだ計算されない
std::ranges::transform_view tv{std::views::iota(1, 5), [](int n) { return n * 2; }};

// イテレータ取得時にも計算されない
auto it = std::ranges::begin(tv);

// インクリメント時にも計算されない
++it;

// 間接参照時に要素が読みだされ、変換が適用される
int n1 = *it; // n1 == 2
int n2 = *it; // n2 == 2、再計算している

++it;

int n3 = *it; // n3 == 4
```

少し注意点なのですが、この性質上`*`による間接参照のタイミングで毎回変換が行われます。一度計算した値をキャッシュしたりはしません。なので、変換関数としてあまり重い処理を渡すことは避けた方が良いでしょう。

### `views::transform`

`transform_view`に対応する*range adaptor object*が`std::views::transform`です。

```cpp
#include <ranges>
int main() {
  for (int n : std::views::transform(std::views::iota(1, 5), [](int n) { return n * 2; })) {
    std::cout << n;
  }

  std::cout << '\n';

  // パイプラインスタイル
  for (int n : std::views::iota(1, 5) | std::views::transform([](int n) { return n * 2; })) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BBS3Ium3NFWLWvQR)

`views::transform`もカスタマイゼーションポインオブジェクトであり、操作を適用する*range*と変換関数を受け取りそれをそのまま転送して`transform_view`を構築して返します。

## `take_view`

`take_view`は元となるシーケンスの先頭から指定された数だけ要素を取り出したシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // 先頭から5つの要素だけを取り出す
  std::ranges::take_view tv{std::views::iota(1), 5};
  
  for (int n : tv) {
    std::cout << n; // 12345
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/EYSHSFamhQcywChy)

`iota_view`の生成する無限列のように無限に続くシーケンスから決められた数だけを取り出したり、*range*アルゴリズムにおいて他の操作を適用したシーケンスから（先頭に集められた）最終的な結果を取り出す時などに活用できるでしょう。

### オーバーランの防止

意地悪な人はきっと、`take_view`に元となるシーケンスの長さよりも長い数を指定したらどうなるん？と思うことでしょう。残念ながら？これは対策されています。

`take_view`のイテレータは元となるシーケンス（`r`とします）の種別によって3つのパターンに分岐します。

1. `r`が`sized_range`であるならば、次のいずれか
   1.  `r`が`random_access_range`なら、`r`の先頭イテレータをそのまま利用
   2. それ以外の場合、`std::counted_iterator`に`r`の先頭イテレータと与えられた長さと`r`の長さの短い方を渡して構築
2. それ以外の場合、`std::counted_iterator`に`r`の先頭イテレータと与えられた長さを渡して構築

`sized_range`というのはコンセプトで、距離を定義可能な*range*を表します。 
`std::counted_iterator`はC++20から追加された*iteretor adaptor*で、与えられたイテレータをラップして指定された長さだけイテレート可能なものに変換します。

これによって、距離が事前に求まる場合はその距離を超えてイテレートされることはありません。そして、`sized_range`ではない*range*に対しても`take_view`の提供する*sentinel*によって確実にオーバーランしないようにチェックされています。

```cpp
#include <ranges>

int main() {
  using namespace std::string_view_literals;
  
  // 元の文字列の長さを超えた長さを指定する（上記1.1のケース）
  std::ranges::take_view tv1{"str"sv, 10};
  
  int count = 0;
  
  // 安全、3回しかループしない
  for ([[maybe_unused]] char c : tv1) {
    ++count;
  }
  
  std::cout << "loop : " << count << '\n';  // loop : 3
  
  std::list li = {1, 2, 3, 4, 5};
  
  // 元のリストの長さを超えた長さを指定する（上記1.2のケース）
  std::ranges::take_view tv2{li, 10};
  count = 0;

  // 安全、5回しかループしない
  for ([[maybe_unused]] int n : tv2) {
    ++count;
  }
  
  std::cout << "loop : " << count << '\n';  // loop : 5

  std::forward_list fl = {1, 2, 3, 4, 5};
  
  // 元のリストの長さを超えた長さを指定する（上記2のケース）
  std::ranges::take_view tv3{fl, 10};
  count = 0;

  // 安全、5回しかループしない
  for ([[maybe_unused]] int n : tv3) {
    ++count;
  }
  
  std::cout << "loop : " << count << '\n';  // loop : 5
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xAgRnDzn2Eg1WZ7c)

`std::counted_iterator`は与えられたイテレータの特性を完全に継承するので、`take_view`の*range category*もまた与えられた*range*と同じになります。

なお、`take_view`に負の値を渡すこともできますが、*random access range*の場合以外は未定義動作になります。何かに使えそうな気がしないでもないですが、基本的には避けた方が良いでしょう。

### 遅延評価

`take_view`もまた、遅延評価によってシーケンスを生成します。ただ、`take_view`は元となる*range*の極薄いラッパーなので、ほとんどの操作はベースにあるイテレータの操作をそのまま呼び出すだけで、特別な事は行ないません。

`take_view`が行なっている事はほぼその長さの管理だけです。それは主に`==`による終端チェック時に行われます。また、`std::counted_iterator`が使用される場合はそのためにインクリメントのタイミングで残りの距離の計算（単純なカウンタのデクリメントによる）が行われます。

```cpp
// take_vieww構築時には何もしない
std::ranges::take_view tv{std::views::iota(1), 5};

// イテレータ取得時には元のシーケンスによって最適なイテレータを返す
auto it = std::ranges::begin(tv);

// インクリメントはベースのイテレータをインクリメントする
// counted_iteratorが使用される場合、ここで残りの距離が計算される
++it;

// 間接参照時はベースのイテレータを間接参照するだけ
int n1 = *it; // n1 == 2

// 番兵取得時には元のシーケンスによって最適な番兵を返す
auto fin = std::ranges::end(tv);

// 終端チェック時に与えられた長さと元のシーケンスの長さ、現在の位置に基づいてチェックが行われる
it == fin;
```

### `views::take`

`take_view`に対応する*range adaptor object*が`std::views::take`です。

```cpp
#include <ranges>

int main() {
  
  for (int n : std::views::take(std::views::iota(1), 5)) {
    std::cout << n;
  }
  
  std::cout << '\n';

  // パイプラインスタイル
  for (int n : std::views::iota(1) | std::views::take(5)) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BBS3Ium3NFWLWvQR)

`views::take`はカスタマイゼーションポイントオブジェクトであり、2つの引数を受け取りそれらに応じた*View*を返します。その条件は複雑なので割愛しますが、例えば`random_access_range`かつ`sized_range`である標準ライブラリのもの（`std::span, std::string_view`など）に対しては、与えられた長さと元の長さのより短い方の長さによって構築し直したその型のオブジェクトを返します。

厳密には`take_view`だけを返すわけではありませんが、結果の型を区別しなければ実質的に`take_view`と同等の*View*が得られます。

## `take_while_view`

`take_while_view`は元となるシーケンスから指定された条件を満たす連続要素によるシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // 先頭から7未満の要素だけを取り出す
  std::ranges::take_while_view tv{std::views::iota(1), [](int n) { return n < 7; }};
  
  for (int n : tv) {
    std::cout << n; // 123456
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/A4CXrQoZgcHF2GKy)

元となるシーケンスの先頭から条件を満たさない最初の要素の一つ前までのシーケンスを生成します。

`take_while_view`は元となる*range*の性質をそのまま受け継ぎ（というかイテレータをそのまま利用し）、元となる*range*と同じカテゴリになります。

### 遅延評価

`take_while_view`もまた、遅延評価によってシーケンスを生成します。ただ、`take_while_view`は元となる*range*の極々薄いラッパーなので、ほとんどの操作はベースにあるイテレータの操作をそのまま呼び出すだけで、特別な事は行ないません。

`take_while_view`が行なっている事は終端の管理だけで、`==`による終端チェックのタイミングで現在の要素が条件を満たすか否かをチェックします。また、同時に現在の位置が元のシーケンスの終端に到達しているかもチェックすることでオーバーランを防止します。

```cpp
// take_while_view構築時には何もしない
std::ranges::take_while_view tv{std::views::iota(1), [](int n) { return n < 7; }};

// イテレータ取得時には元のイテレータをそのまま返す
auto it = std::ranges::begin(tv);

// インクリメントは元のイテレータのインクリメント
++it;

// 間接参照も元のイテレータの間接参照
int n1 = *it; // n1 == 2

// 受け取った述語オブジェクトを私て番兵を構築する
auto fin = std::ranges::end(tv);

// 終端チェック時に現在のイテレータの指す要素が与えられた条件を満たしているかをチェック
// 同時に元のシーケンスの終端に到達しているかもチェックする
it == fin;
```

この特性上、`==`による終端チェック時には毎回要素の参照と条件のチェックが行われます。条件判定にはあまり重い処理を渡さないように気を付けましょう。

### `views::take_while`

`take_while_view`に対応する*range adaptor object*が`std::views::take_while`です。

```cpp
#include <ranges>

int main() {
  for (int n : std::views::take_while(std::views::iota(1), [](int n) { return n < 7; })) {
    std::cout << n; // 123456
  }
  
  std::cout << '\n';

  // パイプラインスタイル
  for (int n : std::views::iota(1) | std::views::take_while([](int n) { return n < 7; })) {
    std::cout << n; // 123456
  }
}
```

`views::take_while`はカスタマイゼーションポイントオブジェクトであり、2つの引数を受け取りそれらを転送して`take_while_view`を構築して返します。

### 参考文献

- [Standard Ranges - Eric Niebler](https://ericniebler.com/2018/12/05/standard-ranges/)