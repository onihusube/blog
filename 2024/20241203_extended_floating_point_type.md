# ［C++］ 拡張浮動小数点数型の変換ランクに関する規定のある一文について

この記事は[C++ Advent Calendar 2024](https://qiita.com/advent-calendar/2024/cxx)の3日目の記事です。

拡張浮動小数点数型についてはあまり詳しく説明しないので他のページを参照してください。

- [`<stdfloat>` - cpprefjp](https://cpprefjp.github.io/reference/stdfloat.html)
- [Standard library header <stdfloat> (C++23) - cppreference](https://en.cppreference.com/w/cpp/header/stdfloat)

なんか書いてみたら自明な感じがしてきましたが、一応備忘録です。

[:contents]

## 拡張浮動小数点数型の変換ランク

C++23において拡張浮動小数点数型という新しい浮動小数点数型のサポートが（必須ではないものの）追加されています。規格では、拡張浮動小数点数型を含む浮動小数点数型の変換やオーバーロード解決について、浮動小数点数型の変換ランクというものを用いて説明されています。

この変換ランクは浮動小数点数型に対応する浮動小数点数表現が表現可能な値の集合の包含関係によって定義されており、より表現可能な値の集合が大きい型（より幅の広い浮動小数点数型）の変換ランクが上位に来るようになっています。とはいえ、float16とbfloat16のように互いに包含関係が成立しない型が存在するので、この順序は半順序になります。

[N4950 [conv.rank]/2](https://timsong-cpp.github.io/cppwp/n4950/conv.rank#2)にそれは規定されており、概ねそのようなことが書かれています。

> 全ての浮動小数点数型は、次のように定義される浮動小数点数変換ランクを持つ  
> 1. 浮動小数点数型`T`のランクは、その値の集合が`T`の値の集合の真部分集合となる浮動小数点数型のランクよりも大きくなる  
> 2. `long double`のランクは`double`よりも大きく、`double`のランクは`float`よりも大きい  
> 3. 同じ値の集合を持つ2つの拡張浮動小数点数型のランクは同じ  
> 4. （CV修飾を無視して）標準浮動小数点数型のうちのちょうど1つと同じ値の集合を持つ拡張浮動小数点数型のランクは、その標準浮動小数点数型と同じ  
> 5. （CV修飾を無視して）標準浮動小数点数型のうちの2つ以上と同じ値の集合を持つ拡張浮動小数点数型のランクは、`double`と同じ

翻訳が気になる場合は原文を参照してください。

3に該当する拡張浮動小数点数型のペアはC++23時点では存在していない気がするのですが、ここで気になるのはそこではなく5の規定です。`double`と`float`がIEEE754の倍精度と単精度の表現を持つものとすると、4によって`std::float64_t`と`std::float32_t`はそれぞれ`double`と`float`と同じ変換ランクになります。じゃあ5は一体何を言っているのでしょうか？あるいは、何を想定しているのか・・・？

## `long double`

標準浮動小数点数型にはもう一つ`long double`という奴がいます。これは少なくとも`double`と同じ精度を持つということくらいしか指定されていない自由人なのですが、この実体が実装によって実にバラエティ豊かになっています。そしてとくに、`long double`が`double`と同じ表現を持つ場合が普通にあります。

例えばMSVCのWindows環境がそうですが、他にもARMの32ビット環境などもそうなるようです。`double`がIEEE754の倍精度表現になっているとすると、この場合拡張浮動小数点数型`std::float64_t`に対して同じ表現を持つ標準浮動小数点数型が2つ存在していることになります。

先程の変換ランクの規定5はまさにこのような場合の事を想定し、指定しています。

ある拡張浮動小数点数と他の浮動小数点数型間の変換において、変換ランクの低い型から高い型への変換はロスレス変換として暗黙的に行える一方で、変換ランクを下る方向の変換は縮小変換であり暗黙的には行えません。規定2によって`long double > double`となるため、この場合に`std::float64_t`はどちらかと同じ変換ランクになる必要があり、それは`double`と同じになることを規定4は指定しています。

この場合にもし`long double`と同じ変換ランクになるとすると、`long double`と`std::float64_t`は同じ変換ランクなので相互に暗黙変換可能なのに対して、`std::float64_t`と`double`では変換ランクが異なるため`double`からの変換は暗黙的に行えるものの、`double`への変換は明示的変換が必要となります。

```cpp
// long doubleとstd::float64_tが同じ変換ランクだったとすると
const long double ld = 1.0;
const double d = 1.0;
const std::float64_t fp64 = 1.0f64;

// long doubleとstd::float64_tは相互変換可能
long double ld2 = fp64;     // ✅
std::float64_t fp64_2 = ld; // ✅

// doubleとstd::float64_tは一方通行
std::float64_t fp64_3 = d;  // ✅
double d2 = fp64;           // ❌
```

この挙動はおそらく便利なものではありません。どう考えても`double`の使用機会の方が多いでしょう。従って実際の仕様ではこのような場合の拡張浮動小数点数型の変換ランクは`double`と同じになり、少なくとも`double`とのやり取りをスムーズにしています。

```cpp
// 実際のC++23では
const long double ld = 1.0;
const double d = 1.0;
const std::float64_t fp64 = 1.0f64;

// long doubleとstd::float64_tは一方通行
long double ld2 = fp64;     // ✅
std::float64_t fp64_2 = ld; // ❌

// doubleとstd::float64_tは相互変換可能
std::float64_t fp64_3 = d;  // ✅
double d2 = fp64;           // ✅
```

非Windowsのx86-64環境では`long double`の表現は80ビットの拡張倍精度になっていることが多いですが、この動作はオプション（`-mlong-double-64`）で変更することができるのでこの挙動を実際に確かめることができます。

- https://wandbox.org/permlink/fEmXHB5GuAPlEU8M

余談ですが、AVRマイコンの環境でGCC9までは`double`も`long double`も`float`と同じ32ビット幅の表現になっていたようで、gcc10以降もオプションで変更可能とのことです。このような環境では、（もし実装されれば）`std::float32_t`に対して同じ表現を持つ標準浮動小数点数型が3つ存在することになります・・・

### 参考文献

- [P1467R9 Extended floating-point types and standard names](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p1467r9.html)
- [`<stdfloat>` - cpprefjp](https://cpprefjp.github.io/reference/stdfloat.html)
- [long doubleの話 - Qiita](https://qiita.com/mod_poppo/items/8860505f38e2997cd021)
- [Fundamental types - cppreference](https://en.cppreference.com/w/cpp/language/types)
- [avr-gcc - GCC Wiki](https://gcc.gnu.org/wiki/avr-gcc)
    - [@mod_poppoさんより](https://x.com/mod_poppo/status/1862488254035239400)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2024/20241203_extended_floating_point_type.md)
