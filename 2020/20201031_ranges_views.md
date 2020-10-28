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

## `drop_view`

`drop_view`は元となるシーケンスの先頭から指定された数の要素を取り除いたシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // 先頭から5つの要素を取り除く
  std::ranges::drop_view dv{std::views::iota(1, 10), 5};
  
  for (int n : dv) {
    std::cout << n; // 6789
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/bi9QtwtHlVbO0SZ4)

ちょうど`take_view`と逆の働きをするもので、ループ的に考えるなら先頭から指定個数の要素をスキップしたところから開始するシーケンスを生成します。

### オーバーラン防止と遅延評価

`take_view`がそうであるように`drop_view`もまた元となるシーケンスの長さを超えることの無いようになっています。

`drop_view`によるシーケンスは遅延評価によって生成され、そのイテレータの取得時（`begin()`の呼び出し時）に元となるシーケンスの先頭イテレータを指定した分進めて返します。その際、元のシーケンス上で終端チェックを行いながら進めることでオーバーランしないようになっています。これはC++20から追加された`std::ranges::next(it, end, n)`を使用して行われます。

```cpp
// drop_view構築時にはまだ何もしない
std::ranges::drop_view dv{std::views::iota(1, 10), 5};

// イテレータ取得時にスキップ処理が行われる
// 元のシーケンスの先頭イテレータを指定した長さ進めるだけ
// その際終端チェックを同時に行う
auto it = std::ranges::begin(tv);

// その他の操作は元のシーケンスのイテレータそのまま
++it;
*it;
```

イテレータは元のシーケンスのものを完全に流用するので、`drop_view`の*range*は元のシーケンスの*range*カテゴリと同じになります。

また、この`drop_view`の`begin()`の呼び出しは元のシーケンスが`forward_range`（以上の強さ）であるとき、`begin()`の処理結果はキャッシュされることが規定されています。これによって`drop_view`の`begin()`の計算量は償却定数となります。

### `views::drop`

`drop_view`に対応する*range adaptor object*が`std::views::drop`です。
  
```cpp
#include <ranges>

int main() {
  for (int n : std::views::drop(std::views::iota(1, 10), 5)) {
    std::cout << n;
  }
  
  std::cout << '\n';

  // パイプラインスタイル
  for (int n : std::views::iota(1, 10) | std::views::drop(5)) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/mOGi253qHEodidd2)

`views::drop`はカスタマイゼーションポイントオブジェクトであり、2つの引数を受け取りそれらに応じた*View*を返します。その条件は複雑なので割愛しますが、例えば`random_access_range`かつ`sized_range`である標準ライブラリのもの（`std::span, std::string_view`など）に対しては、与えられた長さと元の長さのより短い方の位置から開始するように構築し直したその型のオブジェクトを返します。

厳密には`drop_view`だけを返すわけではありませんが、結果の型を区別しなければ実質的に`drop_view`と同等の*View*が得られます。

## `drop_while_view`

`drop_while_view`は元となるシーケンスの先頭から条件を満たす連続した要素を取り除いたシーケンスを生成する*View*です。

```cpp
#include <ranges>

iint main() {
  // 先頭のホワイトスペースを取り除く
  std::ranges::drop_while_view dv{"     drop while view", [](char c) { return c == ' '; }};
  
  for (char c : dv) {
    std::cout << c;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/G48GYzqNV8citPDG)

`drop_while_view`はかなり`drop_view`と似た振る舞いをします。

### オーバーラン防止と遅延評価

`drop_while_view`も`drop_view`と同様の方法によって遅延評価とオーバーランの防止を行なっています。

すなわち、`drop_while_view`はそのイテレータの取得時（`begin()`の呼び出し時）に元となるシーケンスの先頭イテレータを条件を満たさない最初の要素まで進めて返します。その際、元のシーケンス上で終端チェックを行いながら進めることでオーバーランしないようになっています。これはC++20から追加された[`std::ranges::find_if_not(base_view, pred)`](https://cpprefjp.github.io/reference/algorithm/find_if_not.html)を使用して行われます。

```cpp
// drop_view構築時にはまだ何もしない
std::ranges::drop_while_view dv{"     drop while view", [](char c) { return c == ' '; }};

// イテレータ取得時にスキップ処理が行われる
// 元のシーケンスの先頭イテレータを条件を満たす間進めるだけ
// その際終端チェックを同時に行う
auto it = std::ranges::begin(dv);

// その他の操作は元のシーケンスのイテレータそのまま
++it;
*it;
```

`drop_while_view`は元となるシーケンスのイテレータを完全に流用するので、`drop_while_view`の*range*は元のシーケンスの*range*カテゴリと同じになります。

`drop_while_view`の`begin()`の呼び出しも、元のシーケンスが`forward_range`（以上の強さ）であるときキャッシュされることが規定されています。これによって`drop_while_view`の`begin()`も計算量は償却定数となります。

### `views::drop_while`

`drop_while_view`に対応する*range adaptor object*が`std::views::drop_while`です。
  
```cpp
#include <ranges>

int main() {
  for (char c : std::views::drop_while("     drop while view", [](char c) { return c == ' '; })) {
    std::cout << c;
  }
  
  std::cout << '\n';

  // パイプラインスタイル
  for (char c : "     drop while view" | std::views::drop_while([](char c) { return c == ' '; })) {
    std::cout << c;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/bWXWqx5RSlcA9ed0)

`views::drop_while`はカスタマイゼーションポイントオブジェクトであり、2つの引数を受け取りそれらを転送して`drop_while_view`を構築して返します。

## `join_view`

`join_view`は*View*の*range*となっているシーケンスを平坦化したシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  std::vector<std::vector<int>> vecvec = { {1, 2, 3}, {}, {}, {4}, {5, 6, 7, 8, 9}, {10, 11}, {} };

  std::ranges::join_view jv{vecvec};
  
  for (int n : jv) {
    std::cout << n; // 1234567891011
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/DmH7x7Ntg6XdCRB6)

すなわち、配列の配列を1つの配列に直列化するような事を行うものです。

`join_view`の*range*は通常、元となるシーケンスの外側と内側の*range*が両方とも`bidirectional_range`以上であれば*bidirectional range*となり、`forward_range`以上であれば*forward range*となります。  
それ以外の場合、及び外側の*range*のイテレータの`*`が*prvalue*を返すような場合には常に*input range*になります。

この例では`std::vector`の`std::vector`を利用していますが、別に外側と内側の*range*が同じものである必要はありません。`std::list`の`std::vector`とか、`std::deque`の生配列など、*range*の*range*になっていれば`join_view`は平坦化してくれます。。

```cpp
#include <ranges>

int main() {
  std::vector<std::list<int>> veclist = { {1, 2, 3}, {}, {}, {4}, {5, 6, 7, 8, 9}, {10, 11}, {} };

  std::ranges::join_view jv1{veclist};
  
  for (int n : jv1) {
    std::cout << n; // 1234567891011
  }
  
  std::cout << '\n';
  
  std::deque<int> arrdeq[] = { {1, 2, 3}, {}, {}, {4}, {5, 6, 7, 8, 9}, {10, 11}, {} };

  std::ranges::join_view jv2{arrdeq};
  
  for (int n : jv2) {
    std::cout << n; // 1234567891011
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/svVToBWSPrzPg7DV)

### 遅延評価

`join_view`によるシーケンスもまた遅延評価によって生成されます。`join_view`の仕事の殆どは元となるシーケンスの内側の*range*を接続することにあり、イテレータのインクリメントのタイミングでそれを行います。

`join_view`は元となるシーケンスの内側のシーケンスのイテレータを利用する事で1つの内側*range*のイテレートを行います。そのイテレータが終端に達した時（1つの内側*range*の終端に達した時）、外側*range*のイテレータを一つ進めてそこから次の内側*range*のイテレータを取得します。  
そのままだと内側*range*が空の場合に死ぬので、すぐに内側*range*の終端チェックを行い空でない内側*range*が見つかるまで外側*range*をイテレートします。

```cpp
std::vector<std::vector<int>> vecvec = { {1, 2, 3}, {}, {}, {4}, {5, 6, 7, 8, 9}, {10, 11}, {} };

// 構築とイテレータ取得時には何もしない
std::ranges::join_view jv{vecvec};
auto it = std::ranges::begin(jv);

// インクリメント時に内側イテレータの接続を行う
// 内側イテレータが終端に到達していれば、外側イテレータを進めてそこから内側イテレータを再取得する
// 同時に内側イテレータの終端チェックを行い、空の内側*range*をスキップする
++it;

// デクリメント時はその逆を行う
--it;

// 間接参照は元のシーケンスのイテレータそのまま
int n = *it;
```

1つの内側*range*をイテレートしている間は内側イテレータの終端チェックのみが行われますが、終端に到達した時（2つの内側*range*を接続する時）は少し処理が重くなります。

次の図は、配列の配列になっているシーケンスと`join_view`の様子をそれっぽく書いたものです。

![`join_view`の様子](./20201031_ranges_views/join_view.png)

### `views::join`

`join_view`に対応する*range adaptor object*が`std::views::join`です。

```cpp
int main() {
  std::vector<std::vector<int>> vecvec = { {1, 2, 3}, {}, {}, {4}, {5, 6, 7, 8, 9}, {10, 11}, {} };

  for (int n : std::views::join(vecvec)) {
    std::cout << n;
  }

  std::cout << '\n';

  // パイプラインスタイル
  for (int n : vecvec | std::views::join) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/muoBErBueGCZNb2N)

`views::join`はカスタマイゼーションポイントオブジェクトであり、*range*の*range*となっている*range*オブジェクト1つを受け取りそれを転送して`join_view`を構築して返します。

## `split_view`

`split_view`は元のシーケンスから指定されたデリミタを区切りとして切り出した部分シーケンスのシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  // ホワイトスペースをデリミタとして文字列を切り出す
  std::ranges::split_view sv{"split_view takes a view and a delimiter, and splits the view into subranges on the delimiter.", ' '};
  
  // split_viewは切り出した文字列のシーケンスとなる
  for (auto inner_range : sv) {
    // inner_rangeは分割された文字列1つを表すView
    for (char c : inner_range) {
      std::cout << c;
    }
    std::cout << '\n';
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/YzM0g8aHz94DhuxP)

基本的には文字列の分割に使用することになるでしょう。

`split_view`は切り出した文字列それぞれを要素とするシーケンス（外側*range*）となります。そのため、その要素を参照すると分割後文字列を表す別のシーケンス（内側*range*）が得られます。そこから、内側*range*の要素を参照することで1文字づつ取り出すことができます。なお、この`inner_range`（内側*range*）は`std::string_view`あるいは類するものではなく、単に*forward range*である何かです。

`split_view`の結果はとても複雑で一見非自明です。たとえば`"abc,12,cdef,3"`という文字列を`,`で分割するとき、`split_view`の様子は次のようになっています。

![`join_view`の様子](./20201031_ranges_views/split_view.png)

実際の実装は元のシーケンスのイテレータを可能な限り使いまわすのでもう少し複雑になっていますが、概ねこの図のような関係性の*range*が生成されます。

### 遅延評価

`split_view`もまた遅延評価によって分割処理と*View*の生成を行います。

`split_view`の主たる仕事は元のシーケンス上でデリミタと一致する部分を見つけだし、そこを区切りに内側*range*を生成する事にあります。それは外側*range*のイテレータのインクリメントと内側イテレータの終端チェックのタイミングで行われます。

外側*range*のイテレータ（外側イテレータ）は元のシーケンスのイテレータ（元イテレータ）を持っており、インクリメント時にはそのイテレータから出発して最初に出てくるデリミタ部分を探し出し、そのデリミタ部分の終端位置に元イテレータを更新します。インクリメントと共にこれを行う事で、デリミタ探索範囲を限定しています。

内側*range*における終端検出（すなわち文字列分割そのもの）は、内側*range*のイテレータ（内側イテレータ）の終端チェック（`==`）のタイミングで行われます。内側イテレータは自身を生成した外側イテレータとその親の`split_view`を参照して、外側イテレータの保持する元イテレータの終端チェック→デリミタが空かのチェック→自信の現在位置とデリミタの比較、の順で終端チェックを行います。　

```cpp
// 構築時点では何もしない
std::ranges::split_view sv{"split_view takes a view and a delimiter, and splits the view into subranges on the delimiter.", ' '};

// 外側イテレータの取得、特に何もしない
auto outer_it = std::ranges::begin(sv);

// 外側イテレータのインクリメント時、元のシーケンスから次に出現するデリミタを探す
// 内部rangeは"split_view"->"takes"へ進む
++outer_it;

// 内側rangeの取得、特に何もしない
auto inner_range = *outer_it;

// 内側イテレータの取得、特に何もしない
auto inner_it = std::ranges::begin(inner_range);

// 内側イテレータのインクリメントは、元のシーケンスのイテレータのインクリメントとほぼ等価
++inner_it;

// 元のシーケンスのイテレータのデリファレンスと等価
char c = *inner_it; // a

// 内部rangeの終端チェック
// 元のシーケンスの終端と、デリミタが空かどうか、現在の位置でデリミタが出現しているかどうか、を調べる
bool f = inner_it == std::ranges::end(inner_range); // false
```

`split_view`の結果が複雑となる一因は、この遅延評価を行うことによるところがあります。

### `views::split`

`split_view`に対応する*range adaptor object*が`std::views::split`です。

```cpp
int main() {
  const auto str = std::string_view("split_view takes a view and a delimiter, and splits the view into subranges on the delimiter.");

  for (auto inner_range : std::views::split(str, ' ')) {
    for (char c : inner_range) {
      std::cout << c;
    }
    std::cout << '\n';
  }

  std::cout << "------------" << '\n';

  // パイプラインスタイル
  for (auto inner_range : str | std::views::split(' ')) {
    for (char c : inner_range) {
      std::cout << c;
    }
    std::cout << '\n';
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/VB4JrSSXUTStbG8e)

`views::split`はカスタマイゼーションポイントオブジェクトであり、分割対象の*range*オブジェクトとデリミタを示す*range*オブジェクトを受け取りそれを転送して`split_view`を構築して返します。

### 任意のシーケンスによる任意のシーケンスの分割

実のところ、`split_view`はとてもジェネリックに定義されているため分割対象は文字列に限らず、デリミタもまた文字だけではなく任意の*range*を使用することができます。

たとえば、文字列を文字列で分割することができます。

```cpp
#include <ranges>

int main() {
  const auto str = std::string_view("1, 12434, 5, 0000, 3942");

  // カンマとホワイトスペースで区切りたい
  // そのままだとナル文字\0が入るのでうまくいかない
  for (auto inner_range : str | std::views::split(", ")) {
    for (char c : inner_range) {
      std::cout << c;
    }
    std::cout << '\n';
  }

  std::cout << "------------" << '\n';

  // デリミタ文字列を2文字分のシーケンスにする
  for (auto inner_range : str | std::views::split(std::string_view(", ", 2))) {
    for (char c : inner_range) {
      std::cout << c;
    }
    std::cout << '\n';
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/iaDN7KjAWXyPkehn)

デリミタに任意のシーケンスを使用できるので、`std::vector`を`std::list`で分割することもできます。

```cpp
#include <ranges>

int main() {
  // 3つ1が並んでいるところで分割する
  std::vector<int> vec = {1, 2, 4, 4, 1, 1, 1, 10, 23, 67, 9, 1, 1, 1, 1111, 1, 1, 1, 1, 1, 1, 9, 0};
  std::list<int> delimiter = {1, 1, 1};
  
  for (auto inner_range : vec | std::views::split(delimiter)) {
    for (int n : inner_range) {
      std::cout << n;
    }
    std::cout << '\n';
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/c0IbZh3iU7DTGZXs)

実際このようなジェネリックな分割が必要になる事があるのかはわかりません・・・

ジェネリックな`split_view`の*range*は外側も内側も同じカテゴリとなり、元となるシーケンス（分割対象のシーケンス）が`forward_range`以上であるときにのみ*forward range*となり、それ以外の場合は*input range*となります。

### 文字列への変換

`split_view`はほぼほぼ文字列に対してしか使わないと思われますが、分割結果を文字列で受け取ることができません。

```cpp
#include <ranges>

int main() {
  using namespace std::string_view_literals;
  const auto str = "split_view takes a view and a delimiter, and splits the view into subranges on the delimiter."sv;

  for (auto split_str : str | std::views::split(' ')
                            | std::views::transform([](auto view) {
                              return std::string{view}; // できない
                              return std::string{view.begin(), view.end()}; // ダメ 
                            })
  ) {
    std::cout << split_str << '\n';
  }
}
```

`split_view`の内側*range*は単純な*View*であって、`std::string`への暗黙変換を備えていません。そして、内側*range*は`begin()/end()`のイテレータ型が同じ型を示す`common_range`ではありませんので、C++17以前の設計のイテレータ範囲から構築するコンストラクタからは構築できません。かといって1文字づつ読んで`std::string`に入れる処理を書くのは忍びない・・・

`<ranges>`にはこのような時のために`common_range`ではない*range*を`common_range`に変換する*View*が用意されています（次次回紹介予定）。それを用いれば次のように書くことができます。

```cpp
#include <ranges>

int main() {
  using namespace std::string_view_literals;
  const auto str = "split_view takes a view and a delimiter, and splits the view into subranges on the delimiter."sv;

  for (auto split_str : str | std::views::split(' ')
                            | std::views::transform([](auto view) {
                              // common_viewを通してイテレータ範囲からコピーして構築
                              auto common = std::views::common(view);
                              return std::string{common.begin(), common.end()};
                            })
  ) {
    std::cout << split_str << '\n';
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/AZZWDlEYf6SnrwWU)

`split_view`は*View*であるので元のシーケンスをコピーして処理したりしておらず、その内部イテレータの参照する要素は元のシーケンスの要素そのものです。したがって、文字列の場合は`std::string_view`を用いることができるはずです。

```cpp
#include <ranges>

int main() {
  using namespace std::string_view_literals;
  const auto str = "split_view takes a view and a delimiter, and splits the view into subranges on the delimiter."sv;

  for (auto split_str : str | std::views::split(' ')
                            | std::views::transform([](auto view) {
                                auto common = std::views::common(view);
                                return std::string_view(&*common.begin(), std::ranges::distance(common));
                              })
  ) {
    std::cout << split_str << '\n';
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/MQrlgQ1C8t0ISugP)

ただ、ここで`views::transform`の引数に来ている`view`は内部*range*であり、文字列の場合それは`forward_range`です。そのため、その長さを定数時間で求めることができません。`std::string`で動的確保してコピーしてよりかは低コストだとは思いますが・・・

これらの絶妙な使いづらさは`split_view`が遅延評価を行うことに加えてとてもとてもジェネリックに設計されていることから来ています。このことは標準化委員会の人たちにも認識されていて、`split_view`の主たる用途は文字列の分割なのだから、汎用性を捨てて破壊的変更をしてでも文字列で扱いやすくしよう！という提案（[P2210R0](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2210r0.html)）が提出されています（まだ議論中です）。

## *counted view*

*counted view*は元となるシーケンスの先頭から指定された個数の要素のシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  auto iota = std::views::iota(1);
  
  for (int n : std::views::counted(std::ranges::begin(iota), 5)) {
    std::cout << n; // 12345
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/eXDkHSwysFx0jkfx)

この*counted view*は`std::ranges::couted_view`のようなクラスがあるわけではなく、生成するには`std::views::counted`を使用します。`views::counted`はカスタマイぜーションポイントオブジェクトであり、イテレータと生成する*View*の要素数を受け取ってその種別によって、指定された数の要素を参照する`std::span`か`std::subrange`を返します。  
ただ、`views::counted`は*range adaptor object*ではないのでパイプラインスタイルで使用することはできません。

### `take_view`との差異

*counted view*はまさに`take_view`と同じことをしてくれますが、微妙に違いがあります。

- `take_view`は*View*を受けるが、*counted view*はイテレータを受け取る
- *counted view*はオーバラン防止のためのケアをしない

```cpp
int main() {
  int arr[] = {1, 2, 3};

  // 範囲を飛び越す！
  for (int n : std::views::counted(std::ranges::begin(arr), 5)) {
    std::cout << n;
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/hDUovanRwJ88sJvQ)

*counted view*はイテレータに対して`take_view`相当のものを生成するための入り口であり、イテレータ一つではその範囲の終端は分からないのでオーバーランを防ぐことができないのです。

## `common_view`

`common_view`は元となるシーケンスを、`begin()/end()`によって取得できるイテレータと終端イテレータの型が同じとなるシーケンスに変換する*View*です。

```cpp
int main() {
  auto even_seq = std::views::iota(1)
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::take(10);

  // イテレータ型と終端イテレータ型が合わないためエラー 
  std::vector<int> vec(std::ranges::begin(even_seq), std::ranges::end(even_seq)); // ng
  
  std::ranges::common_view common{even_seq};
  
  std::vector<int> vec(std::ranges::begin(common), std::ranges::end(common)); //ok

  for (int n : vec) {
    std::cout << n; // 2468101214161820
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BRR6DWK4pplhMnPl)

これはC++20以降のイテレータ（*range*ライブラリの*View*などのイテレータ）をC++17以前のイテレータを受け取るものに渡す際に使用します。

標準コンテナのイテレータペアを受け取るコンストラクタや`<algorithm>`の各種アルゴリズム群など、C++17以前のイテレータは`begin()/end()`の型が同一である事を前提としています。しかし、C++20以降のイテレータおよび*range*は異なっていることが前提です。特に、各種*View*クラスの場合は元となる*range*の種別や構築のされ方によって`begin()/end()`の型は細かく変化するので、古いライブラリと組み合わせる際に`common_view`は必須でしょう。

`<algorithm>`のイテレータアルゴリズム関数群は`std::ranges`名前空間の下にある同名の関数を利用すればC++20以降のイテレータに対してもそのまま使用できるようになっていますが、標準コンテナのイテレータペアを取るコンストラクタや`<numeric>`にあるアルゴリズム関数などでは`common_view`を使用する必要があります。

```cpp
int main() {
  auto even_seq = std::views::iota(1)
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::take(10);

  auto common = std::views::common(even_seq);
  
  // 古いやつ
  auto it1 = std::find_if(common.begin(), common.end(), [](int n) { return 10 < n;});
  std::cout << *it1 << '\n';  // 12
  
  // 新しいやつ
  auto it2 = std::ranges::find_if(even_seq.begin(), even_seq.end(), [](int n) { return 10 < n;});
  std::cout << *it2 << '\n';  // 12
  
  // むしろrange直接
  auto it3 = std::ranges::find_if(even_seq, [](int n) { return 10 < n;});
  std::cout << *it3 << '\n';  // 12

  // 古いやつ
  auto sum = std::accumulate(common.begin(), common.end(), 0u);
  std::cout << sum << '\n';   // 110
  
  // まだない・・・
  //auto sum2 = std::ranges::accumulate(even_seq.begin(), even_seq.end(), 0u);
  //auto sum3 = std::ranges::accumulate(even_seq, 0u);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/a7Pd1fFXYtlKZY2T)

`common_view`は元となる*range*が`forward_range`以上であれば*forward range*となり、それ以外の場合は*input range*となります。

### `common_range`

`begin()/end()`の型が同一である*range*は`std::ranges::common_range`コンセプトによって表現され、そのような*range*を*common range*と呼びます。

```cpp
template<class T>
concept common_range =
  range<T> && same_as<iterator_t<T>, sentinel_t<T>>;
```

C++20以降の*range*/イテレータライブラリにおいては、`begin()`から得られるものをイテレータ、`end()`から得られる終端イテレータの事を番兵（*Sentinel*）と呼び分けます。*Sentinel*という言葉は既に*range*ライブラリ周りでは当たり前のように使われています、慣れましょう。

### `views::common`

`common_view`に対応する*range adaptor object*が`std::views::common`です。

```cpp
#include <ranges>

int main() {
  auto even_seq = std::views::iota(1)
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::take(10);

  auto common1 = std::views::common(even_seq);
  
  std::vector<int> vec(std::ranges::begin(common1), std::ranges::end(common1)); //ok


  for (int n : vec) {
    std::cout << n; // 2468101214161820
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/zTm2wNubUBlL6KfY)

```cpp
#include <ranges>

int main() {
  // パイプラインスタイル
  auto even_seq = std::views::iota(1)
    | std::views::filter([](int n) { return n % 2 == 0; })
    | std::views::take(10)
    | std::views::common;

  std::vector<int> vec(std::ranges::begin(even_seq), std::ranges::end(even_seq)); //ok
  
  
  for (int n : vec) {
    std::cout << n; // 2468101214161820
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/8myKZSRy0qXrllbz)

`views::common`はカスタマイゼーションポイントオブジェクトであり、*range*オブジェクト（`r`）を1つ受け取り、それがすでに`common_range`ならば`std::views::all(r)`の結果を、`common_range`でないならば`r`を転送して`common_view`を構築して返します。

結果の型を区別しなければ、あらゆる*range*に対して`common_view`相当のものを得ることができます。特に`common_view`は`common_range`から構築することができないので、`common_view`が欲しい際は常に`views::common`を利用するとよりジェネリックです。

## `reverse_view`

`reverse_view`は元となるシーケンスを逆順にしたシーケンスを生成する*View*です。

```cpp
#include <ranges>

int main() {
  auto seq = std::views::iota(1, 10)
    | std::views::filter([](int n) { return n % 2 == 1; })
    | std::views::transform([](int n) { return n * 10; });
  
  std::ranges::reverse_view rv{seq};
  
  for (int n : rv) {
    std::cout << n; // 9070503010
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/jgP9gz23jT6i11Av)

逆順にするという操作の都合上、入力となる*range*は`bidirectional_range`以上でなければなりません。`reverse_view`そのものは入力*range*と同じカテゴリになります。

### 遅延評価

`reverse_view`は遅延評価によって逆順範囲を生成します。とはいえ、実際の逆順範囲に関しては[`std::reverse_iterator`](https://cpprefjp.github.io/reference/iterator/reverse_iterator.html)に丸投げしているので、`reverse_view`の行うことは`begin()`によってイテレータを取得するタイミングで`std::reverse_iterator`を適切に構築することです。

```cpp
auto seq = std::views::iota(1, 10)
  | std::views::filter([](int n) { return n % 2 == 1; })
  | std::views::transform([](int n) { return n * 10; });

// 構築の時点では何もしない
std::ranges::reverse_view rv{seq};

// イテレータ取得時に元となるシーケンスの終端一つ手前のイテレータからreverse_iteratorを構築して返す
// bidirectional_rangeの場合、時間計算量はO(N)になる
auto it = std::ranges::begin(rv);

// イテレータの操作はreverse_iteratorと同じ
++it;
--it;
int n = *it;

// 元のシーケンスはcommon_rangeでなくてもok
bool fin = it == std::ranges::end(rv);
```

また、この`reverse_view`の`begin()`の処理結果はキャッシュされることが規定されています。これによって`reverse_view`の`begin()`の計算量は償却定数となります。

### `views::reverse`

`reverse_view`に対応する*range adaptor object*が`std::views::reverse`です。

```cpp
#include <ranges>

int main() {
  auto seq = std::views::iota(1, 10)
    | std::views::filter([](int n) { return n % 2 == 1; })
    | std::views::transform([](int n) { return n * 10; });
  
  for (int n : std::views::reverse(seq)) {
    std::cout << n; // 9070503010
  }
  
  std::cout << '\n';
  
  // パイプラインスタイル
  for (int n : seq | std::views::reverse) {
    std::cout << n; // 9070503010
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/HfRLaVvkZMyK3PZc)

`views::reverse`はカスタマイゼーションポイントオブジェクトであり、*range*オブジェクトを1つ受け取りそれを転送して`reverse_view`を構築して返します。ただし、すでに逆順になっているシーケンス（`reverse_view`や`reverse_iterator`の`subrange`）に対してはその元になっている*range*を返す事によって、`reverse_view`を何回も適用する事を回避します。

```cpp
#include <ranges>

int main() {
  std::vector vec = {1, 2, 3, 4, 5, 6, 7, 8, 9};

  for (int n : vec | std::views::reverse  // vector<int> -> reverse_view
                   | std::views::reverse  // reverse_view -> ref_view<vector<int>>
                   | std::views::reverse  // ref_view<vector<int>> -> reverse_view
                   | std::views::reverse  // reverse_view -> ref_view<vector<int>>
      )
  {
    std::cout << n; // 123456789
  }
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/PVL5Ppu7DcpljFUe)

## 参考文献

- [Standard Ranges - Eric Niebler](https://ericniebler.com/2018/12/05/standard-ranges/)