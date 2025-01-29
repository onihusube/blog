# ［C++］WG21月次提案文書を眺める（2024年09月）

文書の一覧

- [JTC1/SC22/WG21 - Papers 2024 mailing2024-09](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/#mailing2024-09)

全部で51本あります。

もくじ

[:contents]

### [N4990 Business Plan and Convener's Report](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/n4990.pdf)

ビジネスユーザ向けのC++およびWG21の現状報告書。

### [P0472R2 Put `std::monostate` in `<utility>`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p0472r2.pdf)

`std::monostate`を`<utility>`からも利用できるようにする提案。

以前の記事を参照

- [0472R1 Put `std::monostate` in `<utility>` - ［C++］WG21月次提案文書を眺める（2024年07月）](https://onihusube.hatenablog.com/entry/2025/01/13/204945#P0472R1-Put-stdmonostate-in-utility)

このリビジョンでの変更は、`std::nullptr_t`をその代替として使用しない理由の説明と、提案する文言の書き直しなどです。

`std::nullptr_t`をその用途に使わない理由として、`std::monostate`の方が誤用が少ないからと説明しています。`std::nullptr_t`は任意のポインタ型に対してコピー可能で、ストリーム出力（C/C++双方）も動作します。`std::monostate`はどのような代入や変換も不可能であるためこのような誤用の可能性が著しく低く、何もできないことを表す型として適しています（Cのストリームには出力できるようです）。

- [P0472 進行状況](https://github.com/cplusplus/papers/issues/1993)

### [P1030R7 std::filesystem::path_view](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p1030r7.pdf)
### [P1061R9 Structured Bindings can introduce a Pack](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p1061r9.html)
### [P2019R7 Thread attributes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2019r7.pdf)
### [P2287R3 Designated-initializers for base classes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2287r3.html)
### [P2319R1 Prevent path presentation problems](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2319r1.html)
### [P2688R2 Pattern Matching: `match` Expression](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2688r2.html)
### [P2786R7 Trivial Relocatability For C++26](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2786r7.pdf)
### [P2835R5 Expose std::atomic_ref's object address](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2835r5.html)
### [P2835R6 Expose std::atomic_ref's object address](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2835r6.html)
### [P2841R4 Concept and variable-template template-parameters](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2841r4.pdf)
### [P2846R3 reserve_hint: Eagerly reserving memory for not-quite-sized lazy ranges](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2846r3.pdf)
### [P2879R0 Proposal of `std::dump`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2879r0.pdf)

指定された任意個数の引数をスペース区切りで出力する関数である`std::dump()`の提案。

ここで提案されている`std::dump()`は`std::print()`のラッパーであり、`std::dump(arg1, arg2, ..., argn)`は`std::println("{} {} ... {}", arg1, arg2, ..., argn)`と等価になります。

```cpp
std::dump(“Hello, World!”); // output: Hello, World!
std::dump(2 + 2);           // output: 4
std::dump(1, 2, 3, 4, 5);   // output: 1 2 3 4 5

int x = 10, y = 20, z = 30;
std::dump(x, y, z);         // output: 10 20 30
```

モチベーションとしては

- 他のプログラミング言語での既存の慣習とする
    - Pythonの`print(a, b, c)`は`std::dump(a, b, c)`と書ける
- 簡単なテスト、デモ、実験プログラムでの利用
    - 短いプログラムや一時的なコードで、変数の値を手軽に出力するのに便利
- コード例の簡潔化
    -  `std::print({}, {}, {}, ...)`や`std::cout << ... << ...`等のように余計な文字列を省いて例示できる
- デバッグの補助
    - デバッガを使用せずに実行時に変数値を確認するための簡単なコードとして使用可能
    - デバッガが使えない環境や、リアルタイム制約がある環境（一時停止で動作が変わる環境）において、一時的なprintデバッグのために活用できる
- 科学計算での利用
    - 行が改行で区切られ、数値がスペースで区切られた形式は、行列や表の一般的な形式であり、科学計算での利用に適している
      - これは`std::dump()`が生成する形式
- Unixツールとの連携
    - UNIX環境で一般的なトークンベースのCLIツールは`std::dump()`が生成するシンプルな形式で動作する

などが挙げられています。

この提案はLEWGIにおいて時間をかけることに合意が得られませんでした。

- [パラメータパックをprint/formatする - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2024/06/28/230207)
- [P2879 進行状況](https://github.com/cplusplus/papers/issues/2034)

### [P2945R1 Additional format specifiers for time_point](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2945r1.html)
### [P2988R7 std::optional<T&>](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2988r7.pdf)
### [P3016R4 Resolve inconsistencies in begin/end for valarray and braced initializer lists](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3016r4.html)
### [P3019R9 Vocabulary Types for Composite Class Design](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3019r9.html)
### [P3037R3 constexpr std::shared_ptr](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3037r3.pdf)
### [P3074R4 trivial unions (was std::uninitialized<T>)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3074r4.html)
### [P3096R3 Function Parameter Reflection in Reflection for C++26](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3096r3.pdf)
### [P3128R1 Graph Library: Algorithms](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3128r1.pdf)
### [P3128R2 Graph Library: Algorithms](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3128r2.pdf)
### [P3210R2 A Postcondition *is* a Pattern Match](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3210r2.pdf)
### [P3245R2 Allow `[[nodiscard]]` in type alias declarations](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3245r2.html)
### [P3248R2 Require [u]intptr_t](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3248r2.html)
### [P3290R2 Integrating Existing Assertions With Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3290r2.pdf)
### [P3295R1 Freestanding constexpr containers and constexpr exception types](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3295r1.html)
### [P3299R1 Range constructors for std::simd](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3299r1.html)
### [P3309R2 constexpr atomic and atomic_ref](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3309r2.html)
### [P3335R1 Structured Core Options](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3335r1.html)
### [P3371R1 Fix C++26 by making the rank-1, rank-2, rank-k, and rank-2k updates consistent with the BLAS](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3371r1.html)
### [P3372R1 constexpr containers and adapters](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3372r1.html)
### [P3375R0 Reproducible floating-point results](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3375r0.html)

計算結果の再現性の保証された浮動小数点数型の提案。

C++標準では、浮動小数点数の動作（計算）のほとんどの部分は実装定義とされており、同じ計算式が異なるプラットフォームで同じ結果をもたらすとは限りません。

例えば次のようなコードは実装によって異なる結果を生成します。

```cpp
int main() {
	float line_0x(0.f);
	float line_0y(7.f);

	float normal_x(0.57f);
	float normal_y(0.8f);

	float px(10.f);
	float py(0.f);

	float v2p_x = px - line_0x;
	float v2p_y = py - line_0y;

	float distance = v2p_x * normal_x + v2p_y * normal_y;

	float direction_x = normal_x * distance;
	float direction_y = normal_y * distance;

	float proj_vector_x = px - direction_x;
	float proj_vector_y = py - direction_y;

	std::cout << "distance:      " << distance << std::endl;
	std::cout << "proj_vector_y: " << proj_vector_y << std::endl;
}
```

オプションなしでNvidia C++ compiler 24.5でビルドすると

```
distance:  	   0.0999997
proj_vector_y: -0.0799998
```

オプションなしでclang 18.1.0でビルドすると

```
distance:  	   0.0999999
proj_vector_y: -0.0799999
```

`-march=skylake`を指定してclangでビルドすると

```
distance:  	   0.1
proj_vector_y: -0.08
```

のようになります。これは出力が異なっているのではなく、実際にビットレベルで異なった結果となっています。特に、最適化を有効にするとプログラム中で実行される浮動小数点演算の性質・数・順序が実装ごとに異なり、これによって丸め演算の回数や順序が異なってくることから、プラットフォームによって異なった値を生成します。

ISO/IEC 60559:2020（IEEE 754）では浮動小数点演算の再現可能性についても指定しているものの、それを達成するには言語標準・実装・およびユーザーの強力が必要としています。しかし、C++では規格からして再現可能な浮動小数点演算をサポートしていません。

一部のアプリケーションにおいては浮動小数点演算の再現性が重要となる場合があります。例えば、ゲーム開発においては、クロスプラットフォームで展開する場合が多いため、異なるプラットフォーム間で浮動小数点演算結果が一致するようになるとコードの移植性を向上させることができます。あるいは、オンラインマルチプレイが可能なゲームにおいては、より簡単に異なるプラットフォーム間でデータを交換することができます。

科学計算では実装が浮動小数点演算に対して行う最適化（命令の融合や並べ替え）が計算結果に致命的な丸め誤差を導入してしまい、計算結果が不正確なものになる場合があります。これを回避・あるいは制御するためには、計算の順序が厳密に指定されていることが重要になります。

この提案では、再現性のある浮動小数点演算を実現するために、新しいライブラリ実装の浮動小数点数型を追加することを提案しています。

```cpp
namespace std {
  // 丸めモードの指定
  enum class iec_559_rounding_mode : unspecified;                                                                             // freestanding
  inline constexpr iec_559_rounding_mode iec_559_round_ties_to_even = iec_559_rounding_mode::round_ties_to_even;              // freestanding
  inline constexpr iec_559_rounding_mode iec_559_round_toward_positive = iec_559_rounding_mode::round_toward_positive;        // freestanding
  inline constexpr iec_559_rounding_mode iec_559_round_toward_negative = iec_559_rounding_mode::round_toward_negative;        // freestanding
  inline constexpr iec_559_rounding_mode iec_559_round_toward_zero = iec_559_rounding_mode::round_toward_zero;                // freestanding


  // 再現性のある浮動小数点数型
  template<class T, iec_559_rounding_mode R = round_ties_to_even>
  class strict_float {
  public:
    using value_type = T;

    constexpr strict_float(T);
    constexpr strict_float(const strict_float&) = default;
    template<class X, iec_559_rounding_mode Y>
    constexpr explicit strict_float(const strict_float&);

    constexpr operator value_type() const;

    constexpr strict_float& operator= (const T&);
    constexpr strict_float& operator+=(const T&);
    constexpr strict_float& operator-=(const T&);
    constexpr strict_float& operator*=(const T&);
    constexpr strict_float& operator/=(const T&);
  };
}
```

提案されているのは`strict_float<T, R>`というクラステンプレートで、`T`に浮動小数点数型（IEE754交換形式であることが規定される`float16_t, float32_t, float64_t, float128_t`のいずれか）を指定し、`R`に丸めモードの指定（`iec_559_rounding_mode`列挙型の値）を指定します。

この型は浮動小数点数型`T`のごく薄いラッパであり、この型の値に対する操作（計算）は実行時にソースコード上での順序と意味を保持する事（並べ替えや融合が許可されないこと）が要求され、保証されます。すなわち、再現可能性という性質はこの型の暗黙のプロパティとして（ISO/IEC 60559:2020に準拠した形で）指定されます。

計算における丸めモードに関しては`iec_559_rounding_mode`列挙型の値として型に埋め込まれており、演算子オーバーロードによってその丸めを使用する計算が静的に指定されます。

```cpp
namespace std {
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator+(strict_float<T, R>, <T, R>);              // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator+(strict_float<T, R>, T);                   // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator+(T, strict_float<T, R>);                   // freestanding
  
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator-(strict_float<T, R>, <T, R>);              // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator-(strict_float<T, R>, T);                   // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator-(T, strict_float<T, R>);                   // freestanding
  
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator*(strict_float<T, R>, <T, R>);              // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator*(strict_float<T, R>, T);                   // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator*(T, strict_float<T, R>);                   // freestanding
  
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator/(strict_float<T, R>, <T, R>);              // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator/(strict_float<T, R>, T);                   // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator/(T, strict_float<T, R>);                   // freestanding
  
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator+(strict_float<T, R>);                      // freestanding
  template<class T, iec_559_rounding_mode R>
  constexpr strict_float<T, R> operator-(strict_float<T, R>);                      // freestanding
}
```

この提案ではひとまず、四則演算のみをサポートする最小限の演算のみを提案しています。`<cmath>`にある関数などはアルゴリズムや丸めが指定されていないためそのまま利用できず、そのための作業は多大なものになるためです。また同様に、異なる形式の浮動小数点数間の再現可能な変換も将来のサポートとしています。

なお、よく似た提案がP2746R5で提案されていますが、P2746がFenvによる丸めモードの廃止と置換（よく似たクラステンプレートによる）だけを提案するものであるのに対して、この提案はさらに操作の融合や並べ替えを禁止することで計算の再現可能性を達成することを目指すものです。

- [浮動小数点演算の結果が環境依存なのはどんなときか - Zenn](https://zenn.dev/mod_poppo/articles/floating-point-portability)
- [P2746R5 Deprecate and Replace Fenv Rounding Modes - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P2746R5-Deprecate-and-Replace-Fenv-Rounding-Modes)
- [P3375 進行状況](https://github.com/cplusplus/papers/issues/2035)

### [P3379R0 Constrain `std::expected` equality operators](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3379r0.html)

`std::expected`の`==`演算子の制約の指定を変更する提案。

P2944R3（`reference_wrapper`の`==`比較の動作修正提案）ではそのメインの提案とはほとんど関係ない編集上の提案として`pair, tuple, optional, variant`の比較演算子の制約についての指定がMandatesだったのをConstraintsに修正しました。

しかし、その時に`std::expected`が漏れていたため、この提案では同様の変更を提案しています。

`std::optional`については、P2944R3の変更が行われた際に挙動に差が出てしまったようで、それがLWG Issue 4072で修正されています（Mandatesの場合はill-formedになっていて代わりの候補の探索が行われなかった用法が、Constraintsになったことによってオーバーロード候補から外れて代わりの候補が探索されることで有効になってしまう問題）。ここでは、その修正と同じく追加の制約を行うことで同様の問題に対処しています。

- [C++20標準ライブラリ仕様：Constraints／Mandates／Preconditions - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20200605/p1)
- [LWG Issue 4072. std::optional comparisons: constrain harder](https://cplusplus.github.io/LWG/issue4072)
- [P3375 進行状況](https://github.com/cplusplus/papers/issues/2035)

### [P3380R0 Extending support for class types as non-type template parameters](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3380r0.html)
### [P3381R0 Syntax for Reflection](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3381r0.html)

リフレクション構文のための演算子として`^^`を使用する提案。

P2996で提案されているC++26に向けたリフレクション機能においては、任意のエンティティからリフレクション情報を取り出す演算子として`^`を使用しています（`auto info = ^T;`のように使用）。しかし、Objective-C++におけるブロック拡張の構文と衝突していることが指摘されました。

例えば次のような構文は

```cpp
type-id(^ident)();
```

2つの解釈があり得ます

- `type-id`を返し、引数を取らないブロックを保持する`ident`という名前の変数
- `std::meta::info`を`type-id`にキャストして、`operator()`を呼び出す

1つ目がObjective-C++におけるブロック拡張であり、このことはP3294R1のトークンシーケンス構文（`^{ ... }`）が導入されるとさらに影響が大きくなります。

このために、この提案は`^`の代替となる演算子を探索し、提案するものです。

構文候補には次の三種類が考えられます

1. キーワード
2. 1文字（の演算子
3. 複数文字

とはいえ元々、Reflection TSではリフレクション構文として`reflexpr`というキーワードを用いていたものの、これが構文的に重いために`^`に移行した経緯があり、キーワードという選択肢はあり得ません（可能なキーワードは2,3文字では済まないため）。したがって、残るのは1文字以上の演算子です。

入力しやすく、導入の負担が少ない文字（基本文字集号に新しく文字をくわえる必要のない文字、つまりASCII範囲の記号）であり、C++でまだ使用されて居ないものとすると、1文字の候補はかなり限られます。

この文書で検討された**単一文字のリフレクション演算子候補**は以下の通りです。それぞれの候補について、検討結果と採用されなかった理由をまとめました。

| 候補  | 検討結果 | 使えそう？ |
| :---- | :--- | :--: |
| `#e` | Cマクロで既に使用されており、意味の変更ができない | ❌ |
| `$e` | 一部のコンパイラが識別子として `$` を拡張で使用可能にしているため、`$T` が型 `T` のリフレクションと `$` で始まる識別子のどちらにも解釈できてしまう | ❌ |
| `%e` | テンプレート引数で使う場合に`<%` が代替トークン `{` と解釈されるため、`C<%T>` のような構文が使えない。ただし、`()` や空白を使うことで回避可能ではある。 | 😞 |
| `,e`  | 検討の余地なし| ❌ |
| `/e`  | 使用法によっては、コメント開始の `//` や `/*` に見た目が近い | ✅　|
| `:e`  | `C<:T>` が代替トークン `[` と解釈されるため、`C[:T:]` のような構文が使えない | ❌ |
| `=e`  | 代入演算子として一般的に使用されすぎているため、リフレクション演算子としてのオーバーロードは（意味的に）難しい | ❌ |
| `?e`  | 条件演算子との曖昧さは避けられるものの、他の言語での述語との関連性が強い。また、パターンマッチングでの `?` の使用とも競合する。  | 🤷 |
| `@e`  | Objective-Cで拡張機能として既に使用されている（`@property`, `@dynamic` など）。 `@(e)` はボックス式、`@[e]` や `@{e}` はコンテナリテラルとして解釈されてしまうため回避も難しい | ❌ |
| `\e`  | 文字列内での補間と競合する。また、ユニバーサル文字名との衝突もある（`\u0` がUCNとして解釈される） | ❌ |
| `` `e`` | Markdownでのインラインコードブロックで使われるため、エスケープが難しい。また、特に優れた点もない | ❌ |
| `\|e` | 使用可能で、曖昧さもなく、代替トークンの一部でもない。ただし、数学的な背景を持つ人々にとっては、絶対値のように見える可能性がある | ✅ |

結局、一文字の候補で残ったものは次4つです

- `/e`
- `\|e`
- `?e`: パターンマッチングと競合する
- `%e`: 代替トークンとの重複を受け入れるならあり

複数文字の場合は自由度がさらに広がり、候補はほぼいくらでも存在します。筆者の方の一人は[簡単なユーティリティ](https://syntax-tester.haxing.ninja/?op=%5E%5B&sop=%5D)を作成し、見栄えを比較して検討したようです。

- `^^e`: `^`2文字なら衝突はない、1文字増えるだけ
- `^[e]`: オペランドを角かっこで囲む。スプライシングと対照的になるものの、構文が重い
- `${e}` or `$(e)`: トークンシーケンスの構文としてはあまり適していない（内側にさらに波かっこが入るため）
    - `$$(e)`はスプライシングの構文候補の可能性がある
- `/\e`: 大きい`^`、`\e`と同じ問題がある

この提案では結局、`^^`を選択し、これを提案しています。

2文字であればそれほど重くはなく、見た目の問題がある1文字の使用可能な演算子を再検討する必要性を感じるほどコストは高くなく、また`reflexpr`という10文字よりは十分に短い、という理由のようです。

この提案の内容はR0発行の時点ですでにclang/EDGにて実装されているようです。

そして、この提案は大きな反対なくP2996R8にて適用されています。

- [ブロック (C言語拡張) - Wikipedia](https://ja.wikipedia.org/wiki/%E3%83%96%E3%83%AD%E3%83%83%E3%82%AF_(C%E8%A8%80%E8%AA%9E%E6%8B%A1%E5%BC%B5))
- [Alternative operators and tokens - cppreference.com](https://en.cppreference.com/w/c/language/operator_alternative)
- [P3381 進行状況](https://github.com/cplusplus/papers/issues/2038)

### [P3382R0 Coarse clocks and resolutions](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3382r0.html)

より解像度の粗い時計型を追加する提案。

プログラム中でタイムスタンプを取得したい場合というのは比較的よくあり、C++では`<chrono>`の時計型の`Clock::now()`で取得することができます。しかし、これらの時計型は通常マイクロ秒あるいはそれ以上の解像度を持っており、このような高い解像度の時刻取得にはコストがかかります。一部のユースケースにおいてはそのような高い解像度は必要なく、100msから秒の解像度で十分な場合があります。たとえば

- HTTP Dateヘッダの生成: 秒単位で十分
- 定期実行される処理の周期の指定: 周期の単位が秒より大きい場合、秒単位で十分
- 大きめのタイムアウト値: 大規模データベースへのクエリなど、分単位の時間がかかる場合のタイムアウト判定には秒単位以上で十分
- 統計: 応答時間のパーセンタイルや平均をカウントする場合、高い解像度は不要

一部のプラットフォームではこのような需要に応えられる粗いクロックが用意されており、標準ライブラリの時計型よりも70倍以上高速になる場合があります。また、パフォーマンスを重視する一部のプラットフォームでは既に粗いクロックが使用されています。そのような場所では、次のように必要な場合にのみ高い解像度の時刻を取得するようなフォールバックが良く行われています

```cpp
bool is_expired(std::chrono::steady_clock::time_point deadline) {
  // 粗い時刻とその時計の解像度から大雑把に判定
  auto max_time = coarse_steady_clock() + coarse_steady_clock_resolution();
  if (max_time < deadline) {
    return false;
  }

  // 正確な判定にはより高い解像度の時刻を使用
  return deadline < std::chrono::steady_clock::now()
}
```

この提案は、より粗い解像度で時刻を取得できる時計型を標準ライブラリに追加しようとするものです。

提案されているのは`coarse_steady_clock`と`coarse_system_clock`の2種類で、これらは`coarse_`を取り除いた名前の時計型に対応する性質を持つより粗い解像度の時計型です。

```cpp
namespace std::chrono {
  // より粗いsteady_clock
  class coarse_steady_clock {
  public:
    using rep        = steady_clock::rep;
    using period     = steady_clock::period;
    using duration   = steady_clock::duration;
    using time_point = steady_clock::time_point;
    static constexpr bool is_steady = true;

    static time_point now() noexcept;
    static duration resolution() noexcept;
  };
  
  // より粗いsystem_clock
  class coarse_system_clock {
  public:
    using rep        = system_clock::rep;
    using period     = system_clock::period;
    using duration   = system_clock::duration;
    using time_point = system_clock::time_point;
    static constexpr bool is_steady = system_clock::is_steady;

    static time_point now() noexcept;
    static duration resolution() noexcept;

    // mapping to/from C type time_t
    static time_t      to_time_t(const time_point& t) noexcept {
      return system_clock::to_time_t(t);
    }
    static time_point  from_time_t(time_t t) noexcept { 
      return system_clock::from_time_t(t);
    }
  };
}
```

また、`Cpp17TrivialClock`を変更して`.resolution()`メンバからその時計型の解像度を取得することができるようにして、既存の時計型にも`.resolution()`を追加します。

この2つの時計型において、`duration`と`time_point`の型が元の時計型と同じにされているのは、利便性のためです。例えば先ほどのフォールバックのサンプルコードのように、同じ`duration`と`time_point`型を使用しておけば、元の時計型の時刻と簡単に組み合わせて使用できるようになります。

- [P3382 進行状況](https://github.com/cplusplus/papers/issues/2039)

### [P3383R0 mdspan.at()](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3383r0.html)
### [P3384R0 __COUNTER__](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3384r0.html)
### [P3385R0 Attributes reflection](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3385r0.html)
### [P3388R0 When Do You Know connect Doesn't Throw?](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3388r0.pdf)
### [P3389R0 Of Operation States and Their Lifetimes (LEWG Presentation 2024-09-10)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3389r0.pdf)
### [P3390R0 Safe C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3390r0.html)
### [P3391R0 constexpr std::format](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3391r0.html)
### [P3392R0 Do not promise support for function syntax of operators](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3392r0.pdf)
### [P3396R0 std::execution wording fixes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3396r0.html)
### [P3397R0 Clarify requirements on extended floating point types](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3397r0.pdf)
### [P3398R0 User specified type decay](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3398r0.pdf)
### [P3401R0 Enrich Creation Functions for the Pointer-Semantics-Based Polymorphism Library - Proxy](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3401r0.pdf)
### [P3402R0 A Safety Profile Verifying Class Initialization](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3402r0.html)
