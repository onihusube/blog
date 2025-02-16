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

### [P1030R7 `std::filesystem::path_view`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p1030r7.pdf)

パス文字列を所有せず参照する`std::filesystem::path_view`の提案。

以前の記事を参照

- [P1030R4 `std::filesystem::path_view` - WG21月次提案文書を眺める（2020年12月）](https://onihusube.hatenablog.com/entry/2021/01/17/005823#P1030R4-stdfilesystempath_view)
- [P1030R5 `std::filesystem::path_view` - WG21月次提案文書を眺める（2022年09月）](https://onihusube.hatenablog.com/entry/2022/10/09/021557#P1030R5-stdfilesystempath_view)
- [P1030R6 `std::filesystem::path_view` - WG21月次提案文書を眺める（2023年07月）](https://onihusube.hatenablog.com/entry/2023/09/23/203644#P1030R6-stdfilesystempath_view)

このリビジョンでの変更は

- 最新のWDにリベース
- `render_*()`メンバ関数が`const`修飾されていなかったのを修正
- `c_str()`の要件はnull終端のみとなり、その他の事前条件は不要になった
- `[[nodiscard]]`を削除
- `<filesystem>`から分離され、`<path_view>`ヘッダを新設し移動
- `path-view-like`によって、ソースコードの変更なしに既存のコードがこの提案で追加された新しいフリー関数を呼び出すことは無いことの証明を追記
- `path_view`に対して将来的にABIを破損することなく新しいエンコーディングを追加できることの証明を追記
- `filesystem::path`のフォーマッタを複製する形でフォーマッタを追加
- エラーコード引数を持つフリー関数の多くが`noexcept`である理由についての文言を追加
- `path_view`の使用例を追加
- `path_view`の比較演算子を追加
- `<=>`演算子と削除定義されている演算子の相互作用に関するテストを実施
- `filesystem::path`をとるiosteream関数についての文言を調整

などです。

- [P1030 進行状況](https://github.com/cplusplus/papers/issues/406)

### [P1061R9 Structured Bindings can introduce a Pack](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p1061r9.html)

構造化束縛可能なオブジェクトをパラメータパックに変換可能にする提案。

以前の記事を参照

- [P1061R2 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2022年04月）](https://onihusube.hatenablog.com/entry/2022/05/08/195618#P1061R2-Structured-Bindings-can-introduce-a-Pack)
- [P1061R3 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2022年10月）](https://onihusube.hatenablog.com/entry/2022/11/13/233529#P1061R3-Structured-Bindings-can-introduce-a-Pack)
- [P1061R4 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2023年02月）](https://onihusube.hatenablog.com/entry/2023/03/19/184146#P1061R4-Structured-Bindings-can-introduce-a-Pack)
- [P1061R5 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P1061R5-Structured-Bindings-can-introduce-a-Pack)
- [P1061R6 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2023年12月）](https://onihusube.hatenablog.com/entry/2024/02/29/191439#P1061R6-Structured-Bindings-can-introduce-a-Pack)
- [P1061R7 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P1061R7-Structured-Bindings-can-introduce-a-Pack)
- [P1061R8 Structured Bindings can introduce a Pack - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P1061R8-Structured-Bindings-can-introduce-a-Pack)

このリビジョンでの変更は、提案する文言の調整と実装経験セクションを更新したことです。

この提案はこの次のリビジョンが2024年11月の全体会議で採択されています。

- [P1061R2 進行状況](https://github.com/cplusplus/papers/issues/294)

### [P2019R7 Thread attributes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2019r7.pdf)

`std::thread/std::jthread`において、そのスレッドのスタックサイズとスレッド名を実行開始前に設定できるようにする提案。

- [P2019R1 Usability improvements for `std::thread` - ［C++］WG21月次提案文書を眺める（2022年08月）](https://onihusube.hatenablog.com/entry/2022/09/04/141015#P2019R1-Usability-improvements-for-stdthread)
- [P2019R2 Usability improvements for `std::thread` - ［C++］WG21月次提案文書を眺める（2022年10月）](https://onihusube.hatenablog.com/entry/2022/11/13/233529#P2019R2-Usability-improvements-for-stdthread)
- [P2019R3 Thread attributes - ［C++］WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P2019R3-Thread-attributes)
- [P2019R4 Thread attributes - ［C++］WG21月次提案文書を眺める（2023年10月）](https://onihusube.hatenablog.com/entry/2024/01/08/203712#P2019R4-Thread-attributes)
- [P2019R5 Thread attributes - ［C++］WG21月次提案文書を眺める（2024年01月）](https://onihusube.hatenablog.com/entry/2024/03/10/170322#P2019R5-Thread-attributes)
- [P2019R6 Thread attributes - ［C++］WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P2019R6-Thread-attributes)

このリビジョンでの変更は

- `char8_t`サポートを削除
    - スレッド名の指定`char8_t`文字列を指定できていたが禁止化
    - `wchar_t/char16_t/char32_t`のサポートは意味がないとしてされていませんでしたが`char8_t`はされていた
    - ただし、これは議論不足のための措置であり、将来に追加する事にして別の提案で議論するようです
    - ABI互換性確保のために、名前を受け取るAPIでは`basic_string_view<T>`を取るようにすることにしています

などです。

- [P2019 進行状況](https://github.com/cplusplus/papers/issues/817)

### [P2287R3 Designated-initializers for base classes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2287r3.html)

基底クラスに対して指示付初期化できるようにする提案。

以前の記事を参照

- [P2287R0 Designated-initializers for base classes - ［C++］WG21月次提案文書を眺める（2021年1月）](https://onihusube.hatenablog.com/entry/2021/02/11/153333#P2287R0-Designated-initializers-for-base-classes)
- [P2287R1 Designated-initializers for base classes - ［C++］WG21月次提案文書を眺める（2021年2月）](https://onihusube.hatenablog.com/entry/2021/03/12/225547#P2287R1-Designated-initializers-for-base-classes)
- [P2287R2 Designated-initializers for base classes - ［C++］WG21月次提案文書を眺める（2023年4月）](https://onihusube.hatenablog.com/entry/2023/04/23/192236#P2287R2-Designated-initializers-for-base-classes)

このリビジョンでの変更は

- 指示子（designator）なしで基底クラスのサブオブジェクトを直接初期化する構文の追加
- 実装経験の追記

このリビジョンでは、R2で可能だった

```cpp
struct A {
  int a;
};

struct B : A {
  int b;
};

int main() {
  // R0で提案されていた構文、R2で削除（このリビジョンでも不可
  B b1{:A = {.a = 1}, b = 2};
  B b2{:A{.a = 1}, b = 2};
  B b3{:A{1}, .b{2}};

  // R1で追加され、R2でも可能な構文
  B b4{.a = 1, .b = 2};
  B b5{.a{1}, .b{2}};

  // このリビジョンで追加された構文
  B b6{ A{1}, .b = 2};
}
```

特に、派生クラスと基底クラス（どちらも集成体型とする）で同じメンバ変数名を持つ場合に区別して初期化することができるようになります

```cpp
struct D { int x; };
struct E : D { int x; };

int main() {
  auto e1 = E{.x=1};         // E::xを1で初期化、D::xではない
  auto e2 = E{{.x=1}, .x=2}; // D::xを1で、E::xを2で初期化
  auto e3 = E{D{1}, .x=2};   // 同上
}
```

また、この形式によって非集成体の基底クラスが含まれている場合にそのクラスだけ非指示付き初期化によって初期化することができるようになります

```cpp
struct C : std::string { int c; };

// どちらも同じ意味、ok
auto c1 = C{"hello", .c=3};
auto c2 = C{{"hello"}, .c=3};
```

ただし、指示付き初期化によって初期化できるのは集成体型のみです。

```cpp
struct A { int a; };
struct B : A { int b; };
struct C : A { C(); int c; };
struct D : C { int d; };

A{.a=1};       // C++20からok
B{.a=1, .b=2}; // 提案、'a' は集成体型の直接のメンバであり、Aは基底クラス
C{.c=1};       // error: Cは集成体型ではない
D{.a=1};       // error: 'a' は集成体型の直接のメンバだが、中間の基底クラスCは集成体型ではない
```

この提案では、現在の指示付き初期化時の識別子に対する制約を拡張して、指示付き初期化しようとしている型`T`の直接の非静的メンバ変数に加えて、全ての間接メンバ（集成体型基底クラスの非静的メンバ変数名）もその対象に加えています。

この提案では、指示付き初期化において基底クラス名を指定して初期化する方法を考え出すことをやめており、メンバを指定する間接的な初期化方法をサポートすることを目指しています（ただし、それは直交した問題であり後からでも可能としています）。

- [P2285 進行状況](https://github.com/cplusplus/papers/issues/978)

### [P2319R1 Prevent path presentation problems](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2319r1.html)

`filesystem::path`の`.string()`メンバ関数を非推奨にする提案。

以前の記事を参照

- [P2319R0 Prevent path presentation problems - WG21月次提案文書を眺める（2024年07月）](https://onihusube.hatenablog.com/entry/2025/01/13/204945#P2319R0-Prevent-path-presentation-problems)

このリビジョンでの変更は、`.string()`メンバ関数の非推奨化のみに主眼を置いて、代替関数の追加をやめたことです。

- [P2319 進行状況](https://github.com/cplusplus/papers/issues/1987)

### [P2688R2 Pattern Matching: `match` Expression](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2688r2.html)

C++へのパターンマッチング導入に向けて、別提案との基本構造の違いに焦点を当てた議論。

以前の記事を参照

- [P2688R0 Pattern Matching Discussion for Kona 2022 - WG21月次提案文書を眺める（2022年10月）](https://onihusube.hatenablog.com/entry/2022/11/13/233529#P2688R0-Pattern-Matching-Discussion-for-Kona-2022)
- [P2688R1 Pattern Matching: `match` Expression - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P2688R1-Pattern-Matching-match-Expression)

このリビジョンでの変更は

- 実装経験の追加
- 提案する文言を追加
- `match`演算子の優先順位を定義
- リフレクションベースのtuple-like/variant-likeなプロトコルを提案してないことを決定

などです。

- [P2688 進行状況](https://github.com/cplusplus/papers/issues/1353)

### [P2786R7 Trivial Relocatability For C++26](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2786r7.pdf)

*trivially relocatable*をサポートするための提案。

以前の記事を参照

- [P2786R0 Trivial relocatability options - WG21月次提案文書を眺める（2023年02月）](https://onihusube.hatenablog.com/entry/2023/03/19/184146#P2786R0-Trivial-relocatability-options)
- [P2786R1 Trivial relocatability options - WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P2786R1-Trivial-relocatability-options)
- [P2786R2 Trivial relocatability options - WG21月次提案文書を眺める（2023年07月）](https://onihusube.hatenablog.com/entry/2023/09/23/203644#P2786R2-Trivial-relocatability-options)
- [P2786R3 Trivial relocatability options - WG21月次提案文書を眺める（2023年10月）](https://onihusube.hatenablog.com/entry/2024/01/08/203712#P2786R3-Trivial-Relocatability-For-C26)
- [P2786R4 Trivial relocatability options - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P2786R4-Trivial-Relocatability-For-C26)
- [P2786R5 Trivial relocatability options - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P2786R5-Trivial-Relocatability-For-C26)
- [P2786R6 Trivial relocatability options - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P2786R6-Trivial-Relocatability-For-C26)

このリビジョンでの変更は

- EWG/LEWGでの懸念の提起に対処するために大幅に書き直し
- trivial relocatabilityの提示と議論を簡素化
- swapに関する議論を統合（P3239R0から
- 動作の変更
  - ユーザー定義のムーブ代入演算子によって、型が暗黙的にtrivial relocatableにならないようになった
  - コンテキスト依存キーワード
      - 改訂されたセマンティクスを適切に表現するために、`memberwise_trivially_relocatable`という新しい名前が付けられた
      - オプトインのみ
      - 基底クラスとメンバのrelocatabilityを推定する
  - コンテキスト依存キーワードの後に述語が続かないため、オプトアウトの方法はない
  - 新しい`relocate()`関数は非トリビアルな型と定数評価をサポートする
- P3239R0からの動作の変更
  - trivial swappabilityは置換可能であることとtrivially relocatableに基づいている
  - `memberwise_replaceable`（コンテキスト依存キーワード）の追加
  - `swap_value_representations()`関数と新しいプロパティにより、`std::swap`を最適化する

などです。

- [P2786 進行状況](https://github.com/cplusplus/papers/issues/1463)

### [P2835R5 Expose std::atomic_ref's object address](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2835r5.html)

↓

### [P2835R6 Expose std::atomic_ref's object address](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2835r6.html)

`std::atomic_ref`が参照しているオブジェクトのアドレスを取得できるようにする提案。

以前の記事を参照

- [P2835R0 Expose `std::atomic_ref`'s object address - WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P2835R0-Expose-stdatomic_refs-object-address)
- [P2835R1 Expose `std::atomic_ref`'s object address - WG21月次提案文書を眺める（2023年07月）](https://onihusube.hatenablog.com/entry/2023/09/23/203644#P2835R1-Expose-stdatomic_refs-object-address)
- [P2835R2 Expose `std::atomic_ref`'s object address - WG21月次提案文書を眺める（2024年01月）](https://onihusube.hatenablog.com/entry/2023/09/23/203644#P2835R1-Expose-stdatomic_refs-object-address)
- [P2835R3 Expose `std::atomic_ref`'s object address - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P2835R3-Expose-stdatomic_refs-object-address)
- [P2835R4 Expose `std::atomic_ref`'s object address - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P2835R4-Expose-stdatomic_refs-object-address)

R5での変更は

- P3309とP3323を考慮して更新
- 戻り値型を`T*`に戻す
    - `constexpr`をサポートする唯一の設計であるため
- 既存のポインタを返すAPIを参考に名前を変更

このリビジョンでの変更は

- LEWGは戻り値型として`T*`を確認
- LEWGは名前として`address()`を選択

などです。

- [P2835 進行状況](https://github.com/cplusplus/papers/issues/1545)

### [P2841R4 Concept and variable-template template-parameters](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2841r4.pdf)

コンセプトを受け取るためのテンプレートテンプレートパラメータ構文の提案。

以前の記事を参照

- [P2841R0 Concept Template Parameters - WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P2841R0-Concept-Template-Parameters)
- [P2841R1 Concept Template Parameters - WG21月次提案文書を眺める（2023年10月）](https://onihusube.hatenablog.com/entry/2024/01/08/203712#P2841R1-Concept-Template-Parameters)
- [P2841R2 Concept Template Parameters - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P2841R2-Concept-and-variable-template-template-parameters)
- [P2841R3 Concept Template Parameters - WG21月次提案文書を眺める（2024年05月）](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2841r3.pdf)

このリビジョンでの変更は

- テンプレートコンセプトパラメータを参照する関数テンプレートは、包摂の対象外とした
- 制約の正規化のセクションを改善
- 例を改善して追加
- 新しい文法要素の名前を変更
- テンプレートパラメータとそのパックを紹介するセクションを追加
- id式を使用しないようにテンプレート引数の文言を変更
- コンセプト依存制約の導入
- CWGフィードバックへの対応

などです。

- [P2841 進行状況](https://github.com/cplusplus/papers/issues/1546)

### [P2846R3 reserve_hint: Eagerly reserving memory for not-quite-sized lazy ranges](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2846r3.pdf)

遅延評価のため要素数が確定しない range の `ranges::to` を行う際に、推定の要素数をヒントとして知らせる `ranges::reserve_hint` CPO を追加する提案。

以前の記事を参照

- [P2846R0 `size_hint`: Eagerly reserving memory for not-quite-sized lazy ranges - WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P2846R0-size_hint-Eagerly-reserving-memory-for-not-quite-sized-lazy-ranges)
- [P2846R1 `size_hint`: Eagerly reserving memory for not-quite-sized lazy ranges - WG21月次提案文書を眺める（2023年09月）](https://onihusube.hatenablog.com/entry/2023/10/29/180915#P2846R1-size_hint-Eagerly-reserving-memory-for-not-quite-sized-lazy-ranges)
- [P2846R2 `reserve_hint`: Eagerly reserving memory for not-quite-sized lazy ranges - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P2846R2-reserve_hint-Eagerly-reserving-memory-for-not-quite-sized-lazy-ranges)

このリビジョンでの変更は、`reserve_int`を`std::vector`で使用することを義務付ける文言を追加したことです。

- [P2846 進行状況](https://github.com/cplusplus/papers/issues/1549)

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

`<chrono>`の`time_point`型のフォーマット指定を追加する提案。

以前の記事を参照

- [P2945R0 Additional format specifiers for time_point - WG21月次提案文書を眺める（2023年07月）](https://onihusube.hatenablog.com/entry/2023/09/23/203644#P2945R0-Additional-format-specifiers-for-time_point)

このリビジョンでの変更は、既存のコードの意味を変更するオプションをすべて削除したことです。

R0では`%S`オプションの動作の変更（秒を2桁で出力し、ミリ秒未満を出力しないようにする）を提案していましたが、このリビジョンでは削除されたため、この提案は純粋な機能拡張のみとなりました。

- [P2945 進行状況](https://github.com/cplusplus/papers/issues/1609)

### [P2988R7 `std::optional<T&>`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p2988r7.pdf)

`std::optional`が参照を保持することができるようにする提案。

以前の記事を参照

- [P2988R0 `std::optional<T&>` - WG21月次提案文書を眺める（2023年10月）](https://onihusube.hatenablog.com/entry/2024/01/08/203712#P2988R0-stdoptionalT)
- [P2988R1 `std::optional<T&>` - WG21月次提案文書を眺める（2024年01月）](https://onihusube.hatenablog.com/entry/2024/03/10/170322#P2988R1-stdoptionalT)
- [P2988R3 `std::optional<T&>` - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P2988R3-stdoptionalT)
- [P2988R4 `std::optional<T&>` - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P2988R4-stdoptionalT)
- [P2988R5 `std::optional<T&>` - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P2988R5-stdoptionalT)
- [P2988R6 `std::optional<T&>` - WG21月次提案文書を眺める（2024年08月）](https://onihusube.hatenablog.com/entry/2025/01/26/185126#P2988R6-stdoptionalT)

このリビジョンでの変更は

- 右辺値参照型の特殊化（`std::optional<T&&>`）を削除したこと
- 変換代入演算子の追加
- 変換in-placeコンストラクタの追加

などです。

- [P2988 進行状況](https://github.com/cplusplus/papers/issues/1661)

### [P3016R4 Resolve inconsistencies in begin/end for valarray and braced initializer lists](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3016r4.html)

`std::valarray`と初期化子リストに対して`std::begin`と`std::cbegin`を呼んだ場合の他のコンテナ等との一貫しない振る舞いを修正する提案。

以前の記事を参照

- [P3016R0 Resolve inconsistencies in `begin/end` for `valarray` and braced initializer lists - WG21月次提案文書を眺める（2023年10月）](https://onihusube.hatenablog.com/entry/2024/01/08/203712#P3016R0-Resolve-inconsistencies-in-beginend-for-valarray-and-braced-initializer-lists)
- [P3016R1 Resolve inconsistencies in begin/end for valarray and braced initializer lists - WG21月次提案文書を眺める（2023年12月）](https://onihusube.hatenablog.com/entry/2024/02/29/191439#P3016R1-Resolve-inconsistencies-in-beginend-for-valarray-and-braced-initializer-lists)
- [P3016R2 Resolve inconsistencies in begin/end for valarray and braced initializer lists - WG21月次提案文書を眺める（2023年12月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P3016R2-Resolve-inconsistencies-in-beginend-for-valarray-and-braced-initializer-lists)
- [P3016R3 Resolve inconsistencies in begin/end for valarray and braced initializer lists - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P3016R3-Resolve-inconsistencies-in-beginend-for-valarray-and-braced-initializer-lists)

このリビジョンでの変更は

- LWG Issue 4131の変更（Issue解決）の文面を追加
    - 提案はしていない

などです。

- [P3016 進行状況](https://github.com/cplusplus/papers/issues/1678)

### [P3019R9 Vocabulary Types for Composite Class Design](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3019r9.html)

動的メモリ領域に構築されたオブジェクトを扱うためのクラス型の提案。

以前の記事を参照

- [P3019R0 Vocabulary Types for Composite Class Design - WG21月次提案文書を眺める（2023年10月）](https://onihusube.hatenablog.com/entry/2024/01/08/203712#P3019R0-Vocabulary-Types-for-Composite-Class-Design)
- [P3019R3 Vocabulary Types for Composite Class Design - WG21月次提案文書を眺める（2023年12月）](https://onihusube.hatenablog.com/entry/2024/02/29/191439#P3019R3-Vocabulary-Types-for-Composite-Class-Design)
- [P3019R6 Vocabulary Types for Composite Class Design - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P3019R6-Vocabulary-Types-for-Composite-Class-Design)
- [P3019R8 Vocabulary Types for Composite Class Design - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P3019R8-Vocabulary-Types-for-Composite-Class-Design)

このリビジョンでの変更は

- コンストラクタの順序を変更
- `indirect`に変換代入演算子を追加
- `indirect`と`polymorphic`に変換コンストラクタを追加
- `indirect`と`polymorphic`に初期化子リストコンストラクタを追加
-  ‘heap’や‘free-store’等の用語の使用を‘dynamically-allocated storage’に変更

などです。

- [P3019 進行状況](https://github.com/cplusplus/papers/issues/1680)

### [P3037R3 `constexpr std::shared_ptr`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3037r3.pdf)

`std::shared_ptr`を定数式でも使える様にする提案。

以前の記事を参照

- [P3037R0 `constexpr std::shared_ptr` - WG21月次提案文書を眺める（2023年12月）](https://onihusube.hatenablog.com/entry/2024/02/29/191439#P3037R0-constexpr-stdshared_ptr)
- [P3037R1 `constexpr std::shared_ptr` - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P3037R1-constexpr-stdshared_ptr)
- [P3037R2 `constexpr std::shared_ptr` - WG21月次提案文書を眺める（2024年07月）](https://onihusube.hatenablog.com/entry/2025/01/13/204945#P3037R2-constexpr-stdshared_ptr)

このリビジョンでの変更は

- `reinterpret_pointer_cast`から`constexpr`を取り除いた
- 関連提案への参照の追加
- libc++ベースの2つ目の実装経験の追加

などです。

除外されたのは、例外や`reinterpret_cast`などの定数式では実行できない操作を含むものです。

- [P3037 進行状況](https://github.com/cplusplus/papers/issues/1713)

### [P3074R4 trivial unions (was `std::uninitialized<T>`)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3074r4.html)

定数式において、要素の遅延初期化のために共用体を用いるコードを動作するようにする提案。

以前の記事を参照

- [P3074R0 constexpr union lifetime - WG21月次提案文書を眺める（2023年12月）](https://onihusube.hatenablog.com/entry/2024/02/29/191439#P3074R0-constexpr-union-lifetime)
- [P3074R2 `std::uninitialized<T>` - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P3074R2-stduninitializedT)
- [P3074R3 trivial union (was std::uninitialized<T>) - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P3074R3-trivial-union-was-stduninitialized)

このリビジョンでの変更は、以前に提案していた2つのうちの1つ"Just make it work"の提案に絞ったことと、実装経験を追加したことです。

"Just make it work"の提案は前のリビジョンの`trivial union`の機能性を現在の`union`のまま有効化するものです。すなわち

- デフォルトコンストラクタは無条件でトリビアル
    - デフォルトメンバ初期化子がある場合、削除される
- 最初のメンバがimplicit-lifetime typeである場合、デフォルトコンストラクタはそのメンバの生存期間を開始しそれをアクティブメンバとする
    - 初期化はされない
- デフォルトコンストラクタは無条件でトリビアル

の3点が、現在の構文のままで動作が変更されるようになります。

```cpp
// トリビアルデフォルトコンストラクタを持つ (sの生存期間を開始しない、初期化もされていない)
// トリビアルデストラクタを持つ
// (現在: デフォルトコンストラクタとデフォルトデストラクタはどちらも削除される)
union U1 { string s; };

// デフォルトコンストラクタは定義されるもののトリビアルではない
// デストラクタは削除される
// (現在: デストラクタは削除される)
union U2 { string s = "hello"; }

// トリビアルデフォルトコンストラクタを持つ（sの生存期間を開始する
// トリビアルデストラクタを持つ
// (現在: デフォルトコンストラクタとデフォルトデストラクタはどちらも削除される)
union U3 { string s[10]; }
```

この提案でほしかったものは、定数式で使用可能な遅延初期化用ストレージでした。単一メンバの共用体は遅延初期化用ストレージは供給可能なものの定数式で使用可能ではなくコンストラクタ/デストラクタを定義するとトリビアル性が失われるという問題がありましたが、この提案によりメンバ型に関わらずコンストラクタ/デストラクタを定義しなくても`union`としてのトリビアルなそれら（なにもしない）が宣言されるようになるとともに、implicit-lifetime typeである場合に生存期間を開始するようになることで定数式でも使用可能になります。

- [P3074 進行状況](https://github.com/cplusplus/papers/issues/1734)

### [P3096R3 Function Parameter Reflection in Reflection for C++26](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3096r3.pdf)

C++26に向けた静的リフレクションに対して、関数仮引数に対するリフレクションを追加する提案。

以前の記事を参照

- [P3096R0 Function Parameter Reflection in Reflection for C++26 - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P3096R0-Function-Parameter-Reflection-in-Reflection-for-C26)
- [P3096R1 Function Parameter Reflection in Reflection for C++26 - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P3094R2-stdbasic_fixed_string)
- [P3096R2 Function Parameter Reflection in Reflection for C++26 - WG21月次提案文書を眺める（2024年07月）](https://onihusube.hatenablog.com/entry/2025/01/13/204945#P3096R2-Function-Parameter-Reflection-in-Reflection-for-C26)

このリビジョンでの変更は

- 提案する文言の改善
- P2996R5の内容を反映

などです。

- [P3096 進行状況](https://github.com/cplusplus/papers/issues/1764)

### [P3128R1 Graph Library: Algorithms](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3128r1.pdf)

↓

### [P3128R2 Graph Library: Algorithms](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3128r2.pdf)

グラフアルゴリズムとデータ構造のためのライブラリ機能の提案のうち、提案するグラフアルゴリズムについてまとめた文書。

- [P3128R0 Graph Library: Algorithms - WG21月次提案文書を眺める（2024年07月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P3128R0-Graph-Library-Algorithms)

R1での変更は

- Traversalセクションを追加し、幅優先探索アルゴリズムとトポロジカルソートアルゴリズムを移動。また、深さ優先探索アルゴリズムを追加
- ダイクストラ法とベルマン–フォード法のアルゴリズムの改訂
    - visitorパラメータを追加して、アルゴリズムの動作をカスタマイズできるようにした
    - `Compare()`,`Combine()`関数を除外したオーバーロードを追加
    - 複数ソースのオーバーロードを追加
    - 値がアルゴリズムにおいてどう使用されるかを明確にするために、"invalid distance"を"infinite distance"へ変更
- ベルマン–フォード法のアルゴリズムにおいて、負の重みサイクルを検出する機能を追加

このリビジョンでの変更は、コントリビューターを追加したことです。

- [P3127 進行状況](https://github.com/cplusplus/papers/issues/1783)

### [P3210R2 A Postcondition *is* a Pattern Match](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3210r2.pdf)

事後条件の構文をパターンマッチングの構文に親和させる提案。

以前の記事を参照

- [P3210R0 A Postcondition *is* a Pattern Match - WG21月次提案文書を眺める（2024年04月）](https://onihusube.hatenablog.com/entry/2024/08/31/233056#P3210R0-A-Postcondition-is-a-Pattern-Match)
- [P3210R0 A Postcondition *is* a Pattern Match - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P3210R1-A-Postcondition-is-a-Pattern-Match)

このリビジョンでの変更は

- 提案1の内容を、P2737のキーワード構文を採用するものではなく、P2688のバインディング構文に一致させる、に変更
- 他の部分をそれに合わせて変更
- モチベーションの明確化

などです。

参照する提案が変わっただけで、提案の内容そのものは大きく変化していません。

変更後の内容もSG21でのコンセンサスを得られず、リジェクトされています。

- [P3210 進行状況](https://github.com/cplusplus/papers/issues/1861)

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

この提案はこのリビジョンがそのまま2024年11月の全体会議で承認され、C++26WDに適用されています。

- [C++20標準ライブラリ仕様：Constraints／Mandates／Preconditions - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20200605/p1)
- [LWG Issue 4072. std::optional comparisons: constrain harder](https://cplusplus.github.io/LWG/issue4072)
- [P3379 進行状況](https://github.com/cplusplus/papers/issues/2036)

### [P3380R0 Extending support for class types as non-type template parameters](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3380r0.html)

NTTPとして扱えるクラス型の制限を拡張する提案。

この提案のアイデアはP2484R0で以前に提案されたものをベースにして発展させたものです。

クラス型のNTTPを許可する際に最も問題になることは、NTTP値の等価性をどのように判定するかということです。例えば次のようなコードにおいて

```cpp
// NTTPとして使用可能なクラス型とする
struct C { ... };

template<atuo NTTP>
struct X {};

static_assert(std::same_as<X<C{}>, X<C{}>>);  // 常にパスする？
```

最後のアサーションが常に成功することが重要です。これらはコード上から見た時に同じ型であり、これが同じ型とならない場合は余計なインスタンス化が行われていることになり、関数のインターフェースに現れる場合に一見同じな二つの宣言が異なるオーバーロードになってしまうなど、ODRの問題を引き起こすためです。これは実装的にはマングル名の問題であり、NTTP値をマングリングする時は同じ値は同じ文字列にマングルされる必要があります。

C++20でNTTPとして使用可能な構造的型 (structural type) という型の分類は、この問題が起こらないと思われる要件をまとめたものです。しかし、全てのメンバが`public`である必要があるために多くのクラス型（特に型の構造以上の意味論を持つクラス型）はNTTPとして使用することができません。

`private`メンバを持つクラス型は単にそのサブオブジェクトに分割して等価性を判断するということが必ずしも正しくなく、その型の持つ意味論を考慮する必要がある場合があります。

この提案では、シリアル化（Serialization）・正規化（Normalization）・逆シリアル化（Deserialization）の3ステップによってNTTP値を構築することによって、NTTPの等価性判定に意味論も反映する仕組みを提案するとともに、それをクラス型で宣言するための構文を提案するものです。

1つ目のステップであるシリアル化とは、（NTTPとして使用する）値`V`を受け取り、それを構造的型のタプルへ分解する過程です。結果の型はそれ自体も構造的型である必要があるため、この分解破砕機的に行われます（スカラ型か左辺値参照型に行きつくと終了）。

これはつまりC++20時点の仕様と実装がやっていることであり、クラス型は0個以上スカラ型によって構成されているものとして扱って、そのスカラ型の等価性によってクラス型の等価性を定義しようとするものです。

ただし`private`メンバを持つ型などでは、そのクラス型の等価性判定のためにどのようにシリアライズを行えば良いのか（どのような型に分解するのが適切なのか）をコンパイラに伝える必要があります。

その手段さえ用意すれば、`std::tuple`や`std::string_view`などの型ではこのシリアル化だけでNTTPの等価性問題をクリアできます。ただし、これだけでは不十分な型もあります。

例えば次のような小さな文字列型があって

```cpp
class SmallString {
  char data[32];
  int length = 0; // always <= 32

public:
  // the usual string API here, including
  SmallString() = default;

  constexpr auto data() const -> char const* {
    return data;
  }

  constexpr auto push_back(char c) -> void {
    assert(length < 31);
    data[length] = c;
    ++length;
  }

  constexpr auto pop_back() -> void {
    assert(length > 0);
    --length;
  }
};
```

この型がNTTPとして使用可能であるとして、次のような関数がある時

```cpp
// SmallStringをNTTPで受ける型
template <SmallString S>
struct C { };

constexpr auto f() -> SmallString {
  auto s = SmallString();
  s.push_back('x');
  return s;
}

constexpr auto g() -> SmallString {
  auto s = f();
  s.push_back('y');
  s.pop_back(); // yは配列上に残ったままになる
  return s;
}
```

`SmallString`クラスの意味論的には、`f()`と`g()`の返す文字列型は同じ値を持ちます（`x`1文字からなる文字列）。しかし、そのデータ配列の内容は異なり、最初にゼロクリアされているとしても`g()`の配列には`y`が記録されたままになっています。このため、単にシリアル化の結果のみから等価性を判定（C++20のデフォルト、サブオブジェクト列の等価性によって判定）すると、`C<f()>`と`C<g()>`は異なる型になります。

ここではその意味論を反映する必要がありそうで、シリアル化をカスタムすることで`data[0]`から`data[length - 1]`までの文字のみを等価性判定に参加させた方がいいような気がします。ただしこの方法はまた別の問題を孕んでいます

```cpp
template <SmallString S>
constexpr auto bad() -> int {
  if constexpr (S.data()[1] == 'y') {
    return 0;
  } else {
    return 1;
  }
}
```

この関数を用いた、`bad<f()>()`と`bad<g()>()`は`0`と`1`のどちらの値を返すでしょうか？あるいは両方でしょうか？今はカスタムのシリアル化によって`C<f()>`と`C<g()>`は同一であるようにしているため、これはODR違反になります。

つまり、デフォルトのシリアル化を選ぶと等しさが正しくなくなり（意味を反映できず）、カスタムのシリアル化を選ぶとODR違反が発生します。

この問題を回避するためのステップが正規化です。ここでの正規化は他のところで使用される場合と同じ意味で、本質的に同じであるものを同じになるようにする作業です。例えばこの場合、カスタムのシリアル化を行った後で、`data[]`全体をゼロクリアしてから`length`個の要素をコピーしてその値により等価性判定を行うようにすることで、`C<f()>`と`C<g()>`は同一になりかつ`bad<f()>()`と`bad<g()>()`はどちらも1を返すようになります。

この正規化の実際の作業は型ごとに必要性や方法が異なりえます。

ただし、これを経てもなおまだ十分ではない型が存在します。その代表例は`std::vector`をはじめとする可変長コンテナです。

`std::vector`の実装はとても単純には次のようになっています

```cpp
template <typename T>
class vector {
  T* begin_;
  size_t size_;
  size_t capacity_;
};
```

ポインタのNTTP等価性判定はそのポインタの値によって行われ、ポインタ値が等しい時に等価であるとされますが、`std::vector`の場合はその要素によって判定を行う必要があります（ポインタ値が異なる場合でも`std::vector`的には等価な場合がありうる）。`std::vector`をはじめとするコンテナのシリアル化と正規化においては、可変長の要素列を取り扱う必要があります。

ここまでなら前の`SmallString`と話は変わらないのですが、`std::vector`の場合はキャパシティというプロパティがあります。2つの`std::vector`の全要素が完全に同一だったとしても、キャパシティの値は異なる可能性があります。しかし単にキャパシティの値を等価性判定に参加させただけでは不十分です。なぜなら、キャパシティの値は実態に合っている必要があるためで、すなわち確保されている配列の全体が等価性判定に参加してしまい、先ほどと同じ問題が起こります。

逆シリアル化はこれを上手く取り扱うためのステップで、（カスタム/デフォルトの）シリアル化を行った結果をデシリアライズして実際のNTTP値を構成することによってこの問題を解決します。逆シリアル化は再構築をおこなうことによって正規化を暗黙に実行しており、これによって正規化の方法を慎重に指定する負担を軽減する事もできます。

また、コンパイラは次のようなチェックを実行してこれらの3ステップの過程が健全であることを確認することもできます

```cpp
serialize(deserialize(serialize(v))) === serialize(v)
```

ユーザーがコード内で見るNTTP値は、元の値はをシリアルライズしてデシリアライズ（シリアル化結果をクラスに渡して再構築）した値であり、この結果得られる値はNTTP値として等価であるとみなされる元の型のすべての値に対して信頼できる単一のテンプレート引数となります（同値類の代表元みたいなものになる）。

P2484R0では、このカスタムのシリアル化と逆シリアル化を含むNTTP仕様の設計を提案するものではありましたが、可変長コンテナをサポートできていないなどの問題がありました。この提案ではそれを考慮して正規化というステップを入れることによってこれを解消しています。

残った問題は、このシリアル化と逆シリアル化をどのように行うか、中間表現をどうするか、という点です。`std::vector`や`std::tuple`をシリアル化するには新しい`std::vector`や`std::tuple`が必要になり、表現型についても設計しなければなりません。

この提案では、これに静的リフレクションを活用することを提案しています。すなわち、シリアル化の表現は`std::meta::info`で行い、シリアル化の結果は`std::meta::info`の配列になります。逆シリアル化はこれを受け取るコンストラクタによって行います。

`SmallString`の場合、カスタムのシリアル化（`length`個分の要素だけをシリアル化）は次のようになります

```cpp
class SmallString {
  char data[32];
  int length;

  // 自身をstd::meta::infoの配列に分解
  consteval auto operator template() const -> std::vector<std::meta::info> {
    std::vector<std::meta::info> repr;

    // lengthこの範囲の要素だけをシリアライズする
    for (int i = 0; i < length; ++i) {
      repr.push_back(std::meta::reflect_value(data[i]));  // meta::infoに値を保持する
    }
    
    return repr;
  }
};
```

そして、逆シリアル化（+正規化）は次のように実装されます

```cpp
class SmallString {

  ...

  // オーバーロード解決を容易にするためにタグ付きコンストラクタにする
  consteval SmallString(std::meta::from_template_t, std::vector<std::meta::info> repr)
    : data{} // 配列をまずゼロクリアしておく（正規化）
    , length(repr.size())
  {
    // 各要素を復帰する
    for (int i = 0; i < length; ++i) {
      data[i] = extract<char>(repr[i]);
    }
  }
};
```

`std::vector`の場合もこれと同様に実装できます

```cpp
template <typename T>
class vector {
  T* begin_;
  size_t size_;
  size_t capacity_;

  // vectorのシリアライズ表現型
  struct Repr {
    std::unique_ptr<std::meta::info const[]> p;
    size_t n;

    consteval auto data() const -> std::meta::info const* {
      return p.get();
    }

    consteval auto size() const -> size_t {
      return n;
    }
  };

  // シリアライズ処理
  consteval auto operator template() const -> Repr {
    auto data = std::make_unique<std::meta::info const[]>(size_);

    // 要素の値を保持しておく
    for (size_t i = 0; i < size_; ++i) {
      data[i] = std::meta::reflect_value(begin_[i]);
    }

    // サイズと一緒に保存
    return Repr{
      .p=std::move(data),
      .n=size_,
    };
  }

  // デシリアライズ処理
  consteval vector(std::meta::from_template_t, Repr r) {
    // キャパシティの値はサイズと同一になる
    begin_ = std::allocator<T>::allocate(r.size());
    size_ = capacity_ = r.size();

    // 要素を復帰
    for (size_t i = 0; i < size_; ++i) {
      ::new (begin_ + i) T(extract<T>(r.p[i]));
    }
  }
};
```

ここでは、シリアル化の結果として`Repr`という型を返しています。シリアル化の結果は`meta::info`の配列として扱えればよく`std::vector`である必要はありません（というか`std::vector`は`std::vector`のためには使用できない）。求められているのは、`.data()`が`const std::meta::info*`に変換可能であり、`.size()`でその要素数が取得できることです。

このアプローチは非常に強力である一方で、一部の型に対しては目的は達せられるものの最適とは言えない部分があります。例えば`optional`であり

```cpp
template <typename T>
class Optional {
  union { T value; };
  bool engaged;

  // null reflectionを用いることで長さ0 or 1の配列を表現できる（vector<info>は必要ない
  struct Repr {
    std::meta::info r;

    explicit operator bool() const {
      return r != std::meta::info();
    }

    consteval auto data() const -> std::meta::info const* {
      return *this ? &r : nullptr;
    }
    consteval auto size() const -> size_t {
      return *this ? 1 : 0;
    }
  };

  consteval auto operator template() -> Repr {
    if (engaged) {
      return Repr{.r=meta::reflect_value(value)};
    } else {
      return Repr{.r=meta::info()};
    }
  }

  consteval Optional(meta::from_template_t, Repr repr)
    : engaged(repr)
  {
    if (engaged) {
      ::new (&value) T(extract<T>(repr.r));
    }
  }
};
```

`tuple`もそうです

```cpp
template <typename... Ts>
class Tuple {
  // let's assume this syntax works (because the details are not important here)
  Ts... elems;

  // Note that here we're returning an array instead of a vector
  // just to demonstrate that we can
  consteval auto operator template() -> array<meta::info, sizeof...(Ts)> {
    array<meta::info, sizeof...(Ts)> repr;
    size_t idx = 0;
    template for (constexpr auto mem : nonstatic_data_members_of(^Tuple) {
      // references and pointers have different rules for
      // template-argument-equivalence, and thus we need to
      // capture those differences... differently
      if (type_is_reference(type_of(mem))) {
          repr[idx++] = reflect_object(this->[:mem:]);
      } else {
          repr[idx++] = reflect_value(this->[:mem:]);
      }
    }
    return repr;
  }

  consteval Tuple(meta::from_template_t tag,
                  array<meta::info, sizeof...(Ts)> repr)
      : Tuple(tag, std::make_index_sequence<sizeof...(Ts)>(), repr)
  { }

  template <size_t... Is>
  consteval Tuple(meta::from_template_t,
                  index_sequence<Is...>,
                  array<meta::info, sizeof...(Ts)> repr)
      : elems(extract<Ts>(repr[Is]))...
  { }
}
```

これらの型の場合はいずれも、メンバ毎の等価性によって自身の等価性を表現しているにすぎません。すなわち、（C++20とは異なるが）その動作はデフォルトです（シリアライズのみで十分）。したがって、この場合はデフォルト実装が利用可能であるはずです。

```cpp
template <typename... Ts>
class Tuple {
  Ts... elems;

  consteval auto operator template() = default;
  consteval Tuple(meta::from_template_t, auto repr) = default;
}
```

ただしこれはまだ微妙（1つの操作に2つの宣言がいる、正規化を行う必要がある型で役に立たないなど）な部分があります。この提案では`operator template`の戻り値型`void`であるかどうかによって、その意味を変えるようにしています。

`operator template`の戻り値型`void`である場合、正規化を行う必要があるものの、そのシリアル化および逆シリアル化はデフォルト（メンバ毎のもの）であり、カスタムの逆シリアル化が必要ないことを表します。

```cpp
template <typename T>
class Optional {
  union { T value; };
  bool engaged;

  consteval auto operator template() -> void { }
};

template <typename... Ts>
class Tuple {
  Ts... elems;

  consteval auto operator template() -> void { }
}
```

この戻り値型`void`の`operator template`は、C++20に欠けていた、メンバ毎の等価性によって等価性が判定可能だが`private`なメンバを持ってしまっているクラスに対するオプトイン構文になります。

`SmallString`の場合も実装は単純になります

```cpp
class SmallString {
  char data[32];
  int length;

  consteval auto operator template() -> void {
    // 正規化方法のみを書く（シリアル化と逆シリアル化はデフォルトで良い
    std::fill(this->data + this->length, this->data + 32, '\0');
  }
};
```

この提案では最終的に

- コア言語
    - テンプレート表現関数 (`operator template`)の導入: クラス型`T`は次の2つの形式のいずれかで`consteval`な`operator template`を提供できる
        1. `void`を返す: すべての基底クラスと非静的データメンバは構造型でなければならず、`mutable`であってはならない
        2. `R`を返す:
            - `R.data()`は`std::meta::info const*`に変換可能で、`R.size()`は`size_t`に変換可能である必要がある
            - `T(std::meta::from_template, R)`が有効な式である必要がある
    - テンプレート引数の正規化の概念の導入
        - 構造型`T`の値`v`は、以下のようにテンプレート引数として正規化されます
            1. `T`がスカラー型または左辺値参照型の場合、何も行わない
            2. `T`が配列型の場合、配列のすべての要素がテンプレート引数として正規化される
            3. `T`がクラス型の場合
                - `T`が`void`を返すテンプレート表現関数を提供する場合、その関数が`v`上で呼び出され、`v`のすべてのサブオブジェクトがテンプレート引数として正規化される
                - `T`が`std::meta::info`の範囲を返すテンプレート表現関数を提供する場合、新しい値`T(std::meta::from_template, v.operator template())`が`v`の代わりに使用される
                - `T`がテンプレート表現関数を提供しない場合、`v`のすべてのサブオブジェクトがテンプレート引数として正規化される
    - P2996の`std::meta::reflect_value`の意味を、引数に対してテンプレート引数の正規化を実行するように変更
    - 構造的型の定義の拡張
        - 構造的型は、スカラー型、左辺値参照型、または要素型が構造的型である配列型
        - または、以下のプロパティを持つリテラルクラス型
            - クラスが資格のあるテンプレート表現関数を持つ
            - あるいは
              - すべての基底クラスと非静的データメンバが`public`かつ非`mutable`であり
              - すべての基底クラスと非静的データメンバの型が構造的型である
    - テンプレート引数として等価（template-argument-equivalent）の定義の拡張
        - 2つの値がテンプレート引数として等価であるのは、それらが同じ型であり、次の場合
            - [...]
            - どちらもクラス型`T`であり
              - `T`が非`void`を返す資格のあるテンプレート表現関数を持つクラス型である場合、2つの値に対してテンプレート表現関数を呼び出した結果である`r1`と`r2`について、`r1.size() == r2.size()`であり、`0 <= i < r1.size()`の各`i`について、`r1.data()[i] == r2.data()[i]`である
              - それ以外の場合、対応する直接のサブオブジェクトと参照メンバがテンプレート引数として等価である
    - クラス型の非型テンプレートパラメータを初期化する際に、テンプレート引数の正規化を実行するようにする
- ライブラリ
    - 新しいタグ型`std::meta::from_template_t`と、その値`std::meta::from_template`を追加
    - 新しい型特性`std::is_structural`を追加
    - 次のライブラリ型すべてに、制約付きの`consteval void operator template() { }`（つまり、正規化なしのデフォルトのサブオブジェクトごとのシリアル化）を追加
        - `std::tuple<Ts...>`
        - `std::optional<T>`
        - `std::expected<T, E>`
        - `std::variant<Ts...>`
        - `std::basic_string_view<CharT, Traits>`
        - `std::span<T, Extent>`
        - `std::chrono::duration<Rep, Period>`
        - `std::chrono::time_point<Clock, Duration>`

を提案しています。

`std::meta::info`の配列を返す`operator template`はリフレクション提案に依存していますが、`void`を返す方には依存はありません。前者はあらゆる型をサポートするために（特に可変長コンテナ型のために）必要なソリューションであり、後者は前者の略記であるものの多くの一般的な型をカバーしています。そのため、リフレクションの進行とは関係なく、`void`を返す形式は検討しておくことができます。

- [C++20 非型テンプレートパラメータとしてクラス型を許可する [P0732R2] - cpprefjp](https://cpprefjp.github.io/lang/cpp20/class_types_in_non-type_template_parameters.html)
- [P2484R0 Extending class types as non-type template parameters - WG21月次提案文書を眺める（2021年11月）](https://onihusube.hatenablog.com/entry/2021/12/11/220126#P2484R0-Extending-class-types-as-non-type-template-parameters)
- [P3380 進行状況](https://github.com/cplusplus/papers/issues/2037)

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

### [P3383R0 `mdspan.at()`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3383r0.html)

`std::mdspan`に`.at()`メンバ関数を追加する提案。

`std::mdspan`の添え字アクセスは境界チェックが行われないアクセスであり、境界チェックを行う場合ユーザーが明示的に行わなければなりません。一方で、添え字アクセス可能な標準のコンテナは全て`.at()`メンバ関数を備えています（`std::span`も含めて）。

この提案は、安全性と一貫性のために、`std::mdspan`にも`.at()`メンバ関数を追加しようとするものです。

```cpp
namespace std {
  
  template<
    class ElementType,
    class Extents,
    class LayoutPolicy = layout_right,
    class AccessorPolicy = default_accessor<ElementType>>
  class mdspan {

    ...

    // 提案されているat()の宣言例
    template<class... OtherIndexTypes>
      constexpr reference at(OtherIndexTypes... indices) const;
    
    template<class OtherIndexType>
      constexpr reference at(span<OtherIndexType, rank()> indices) const;

    template<class OtherIndexType>
      constexpr reference at(const array<OtherIndexType, rank()>& indices) const;

    ...
  };
}
```

この意味論は他のコンテナの`.at()`とほとんど同じです。

この提案の内容はすでに`dmspan`の参照実装であるkokkos/mdspanにて実装されています。

- [Add element access via `at()` to `std::mdspan` by stephanlachnit · Pull Request #302 · kokkos/mdspan](https://github.com/kokkos/mdspan/pull/302)
- [P3383 進行状況](https://github.com/cplusplus/papers/issues/2040)

### [P3384R0 `__COUNTER__`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3384r0.html)

`__COUNTER__`マクロを標準化する提案。

`__COUNTER__`マクロは、翻訳単位ごとに0から始まり展開され度にインクリメントされる、整数リテラルへと展開されるマクロです。これは、プリプロセッサメタプログラミングで使用され、ユニークな名前やインデックスを生成するのに使用されます。

このマクロは多くのCおよびC++コンパイラで拡張として使用可能ではあるもののCでもC++でも標準化されてはいません。これにより、そのセマンティクスや移植性には何ら保証がありません。そのため、移植性が重要なコードベースにおいてはマクロによって使用可能かどうか検出して使用するか、使用しないように注意されています。

それでもCおよびC++のコードベースの両方で広く使用されているため、移植性とセマンティクスの保証を提供するために既存の実装を取り込む形で`__COUNTER__`マクロを標準化しようとする提案です。

```cpp
int main() {
  int a = __COUNTER__ ; // 0
  int b = __COUNTER__ ; // 1
  int c = __COUNTER__  + __COUNTER__; // 5
}
```

`__COUNTER__ `マクロの展開結果は整数リテラルになるため厳密にはマクロの結果そのものに型は無いのですが、この提案では少なくとも`2^32 - 1`の値を表現できるように実装することを推奨しており、その実装定義の最大値に達したらコンパイルエラーにするようにしています。

この手のマクロにありがちで問題になるのは、巧妙に使用するとODR違反コードを生成できてしまうことです。

```cpp
// foo.hpp
#define CONCAT_IMPL(x, y) x##y
#define CONCAT(x, y) CONCAT_IMPL(x, y)
#define NEW_VAR(name) CONCAT(name, __COUNTER__)

inline void foo() {
  int NEW_VAR(x) = 2; // __COUNTER__マクロの値次第で、変数名が異なる
}

// a.cpp
#include "foo.hpp"

// b.cpp
int x = __COUNTER__;
#include "foo.hpp"  // a.cppのインクルード内容と異なるfoo()が定義されてしまう
```

既存の実装ではこのような問題に対して特別に検出して警告を発するなどの事は行っておらず、この提案でも特にケアをしていません。解決のためにはモジュールを使用する（`__COUNTER__`マクロはモジュールローカルであるため）か、ODRフレンドリー名前`_`（同じスコープで何度も再使用できる）を使用する事を推奨しています。

これ以外の部分でも、既存の実装の動作やセマンティクスに準じた機能になっています。

- [P3384 進行状況](https://github.com/cplusplus/papers/issues/2041)

### [P3385R0 Attributes reflection](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3385r0.html)

リフレクションにおいて、エンティティに指定されている属性の情報を取得・付加できるようにする提案。

P2996で提案中の静的リフレクション機能には、属性に関するリフレクション（付加されている属性の情報を取得する or 属性情報のリフレクションを用いて属性を付加する）の機能が欠けています。標準属性は現在でも広く使用されており、今後も増加していくことが予想されるため、その重要性は時間とともに増していきます。

この提案は、P2996の静的リフレクションをベースとして、そこに属性に関するリフレクションの機能を追加することを提案するものです。

次のサンプルコードは提案のモチベーションを端的に示したものです

```cpp
enum class Result {
  success,
  warn,
  fail,
};

struct [[nodiscard]] StrictNormalize {
  static constexpr bool operator() (Result status) {
    return status == Result::success;
  }
};

template <class F> 
[[ [: ^F :] ]] // [[ nodiscard ]] に展開される
auto transform(auto... args) {
  return F()(args...);
};

int main() {
  transform<StrictNormalize>(Result::success); // "nodiscard"による警告が表示される
  bool isOk = transform<StrictNormalize>(Result::success); // OK、警告なし
}
```

`transform`の定義においては、呼び出し可能な型`F`に付加されている属性を取得して自身にも付加します。この例では、`StrictNormalize`に付加されている`[[nodiscard]]`を復元しています。

このような属性のイントロスペクションはP2237で提案されているようなコードインジェクション機能の利用時に特に重要になることが予想されます。例えば、`[[deprecated]]`メンバを選択的にスキップするなどです

```cpp
struct User {
  [[deprecated]] std::string name;
  std::string uuidv5;

  [[deprecated]] std::string country;
  std::string countryIsoCode;
};

template<class T>
constexpr std::vector<std::meta::info> liveMembers(const T& user) {
  std::vector<std::meta::info> liveMembers;
  
  // [[deprecated]]属性のリフレクションを取得しておく
  auto deprecatedAttribute = std::meta::attributes_of(^[[deprecated]])[0];

  auto keepLive = [&] <auto r> {
    // [[deprecated]]指定されているメンバを無視する
    if (!std::ranges::any_of(
      attributes_of(^T),
      [deprecatedAttribute] (auto meta) { meta == deprecatedAttributes; }
    )) {
      liveMembers.push_back(r);
    }
  };

  // T の[[deprecated]]ではないメンバのリフレクションだけをliveMembersに入れていく
  template for (auto member : std::meta::members_of(^T)) {
    keepLive(member);
  }

  return os;
}

// Migratedのユーザーはdeprecatedなメンバをサポートしない
struct MigratedUser;
std::meta::define_class(^MigratedUser, liveMembers(currentUser));
```

このために、ここでは次の変更を提案しています

- `std::meta::info`
    - 属性をリフレクション可能なプロパティとしてサポートする
    - これにより、`std::meta::info` 型の値で属性を表現できるようになる
- リフレクション演算子 `^`
    - 属性に対するリフレクションをサポートする。
      - `^[[deprecated]]`を有効にする
    - 結果の値は、属性エンティティの関連情報が埋め込まれたリフレクション値（`std::meta::info`型の値）
    - 標準属性でない場合、この式はill-formed
- スプライサー `[[ [: r :] ]]`
    - 属性が許可されているコンテキストで、`r`（属性のリフレクション）に映されている属性に対応する属性リストを生成できるようにする
    - 例えば、`[[ [: ^ErrorCode :] ]]` のように記述することで、`ErrorCode`型の属性を別の型に付与できる
    - 文法として参照している`attribute-list`は`alignas`をカバーしていないが、これは別の提案で議論する予定
- メタ関数
    - `attributes_of(info) -> std::vector<info>`: 指定されたリフレクション値に付随する各属性を表す`std::meta::info` のシーケンスを返す
    - `is_attribute(info) -> bool`: 指定されたリフレクション値が属性を指している場合に `true` を返す
    - 属性名の取得: 属性のリフレクションから、属性トークンに対応する文字列や、属性を識別するのに役立つテキストを返す
      - `name_of(info) -> string_view`
      - `u8name_of(info) -> u8string_view`
      - `qualified_name_of(info) -> string_view`
      - `u8qualified_name_of(info) -> u8string_view`
      - `display_name_of(info) -> string_view`
      - `u8display_name_of(info) -> u8string_view`
    - `data_member_spec()`と`define_class()`
      - 属性をサポートできるように`data_member_options_t`を拡張する

属性のリフレクションというと、標準属性と非標準属性（特に、ユーザー定義属性）の2種類の話がありますが、この提案では標準属性のサポートに主眼を置きそれのみを提案しています。ただ、標準属性へこれらのサポートを拡大することを念頭に置いて機能は設計されているようです。

- [P3385 進行状況](https://github.com/cplusplus/papers/issues/2042)

### [P3388R0 When Do You Know connect Doesn't Throw?](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3388r0.pdf)

`execution::conect`による操作が例外を送出するかどうかを早期に判定できるようにする提案。

`std::execution`において、非同期操作を表現する`sender`は`receiver`と`connect`して`operation_state`を取得し、それに対して`start`することによってそれが表す非同期操作を開始することができます。現在の仕様では`connect`の操作は例外を送出しうる一方で、`start`の操作が例外を送出するのは禁止されています。

`std::execution`を利用する際にやることは簡単に次の3ステップに分割できます

1. `sender`と`receiver`の選択
2. 1で選択した`sender`と`receiver`の接続（`connect`）
3. 2の結果の`operation_state`を`start`する

このうち、1と2のフェーズは例外を送出する可能性がありますが、3は例外を送出しません。`start`時に送出される例外は`operation_state`の（`connect`されている）`receiver`のエラーチャネルを通じて伝播される必要があります。

さらに、このステップはループしてネストする可能性があります。すなわち、3で開始された非同期操作の内部でさらにこのステップが実行され、その非同期コンテキスト内から非同期操作を開始する、といったことができます。この場合、ネストした1と2および3で生じる例外は全て、`execution::set_error`によって`receiver`のエラーチャネルで伝播される必要があります。

通常の同期関数が例外を送出するかどうかは`noexcept`によって宣言し、取得することができます。同様に、`sender`も例外を送出する場合としない場合があり、送出する場合は`execution::completion_signatures_of_t`を介して照会できる完了シグネチャ（`sender`の返す値の型。3チャネル分ある）のリスト内に`std::set_error_t(std::exception_ptr)`が含まれているかどうかによって宣言し、取得することができます。

そして、`sender`による非同期操作が例外を投げないことが分かる場合、後続の`sender`ではその完了シグネチャに`std::set_error_t(std::exception_ptr)`を含まない事によって自身も例外を送出しないことを選択でき、これは例外をハンドリングするコードの削減等の最適化に繋がります。

すなわち、ネストして非同期操作が構成され開始される場合に、そこからの例外を`execution::set_error`によって伝達する必要があるのかどうかをより早期に判断できれば、その外側の`sender`も例外を伝播する必要があるかどうかをコンパイル時に決定可能になります。そして、現在はそのようにはなっていません。

ステップ1は`sender`と`receiver`の構築時の例外であるためこれは制限できませんが、ステップ2の場合は制限を少し強めることでこれが可能になります。この提案はそれを検討し、提案しています。

この提案では次の2つの事を提案しています

1. `receiver`コンセプトの一部として、`receiver`が例外を投げずにムーブ可能であることを要求する
2. 次のいずれかによって、特定の環境を持つ`receiver`に対して、`sender`の`connect`メンバ関数が例外を送出しないことを判断する仕組みを導入する
    - ある`sender`型のオブジェクトをある`receiver`型（`R1`）のオブジェクトに`connect`しても例外を送出しない場合、その`sender`型のオブジェクトを、`R1`と同じ関連環境型を持つ別の`receiver`型のオブジェクトに接続しても例外を送出しない。という意味論要件を追加
    - 上記に加えて、別の環境型が全く同じクエリをサポートし、全く同じ型を生成すると仮定して、異なる関連環境型を提供できるように要件を強化
    - `sender`型に対して、特定の関連環境型を持つ`receiver`型がその型に対して、例外を送出せずに`connect`可能かをクエリできる`sender`版クエリ関数を導入する

の2つの事を提案しています。

`sender`が例外を送出するかを判定するのに使用可能な`execution::completion_signatures_of_t`は、`sender`そのものか（`receiver`の）環境（*Environment*）に対して照会を行うものです。`connect`操作の実態は`sender`型のメンバ関数として実装されるものなので、これは`connect`内部で接続されようとしている`receiver`の環境を取得してクエリを行います。この時、`sender`型の操作は接続されようとしている`receiver`型の型そのものにはアクセスしません。これはコンパイル時の型情報の相互循環参照を回避するための仕様です。

すなわち、`sender`から見た`receiver`の重要かつ唯一のプロパティはこの環境そのものです。そして、環境とはコンパイル時のKey-Valueストアであり、サポートしているクエリの種類とクエリの返す結果によって特徴づけられ、ある`sender`から見た時にそれらの性質が同じ環境は（型や`receiver`が異なったとしても）同じであるとみなすことができます。

ただ、`connect`操作では`sender`型のメンバ関数内で引数として`receiver`を受け取って、自身及びその（接続されようとしている）`receiver`をコピーないしムーブして`operation_state`を生成する必要があります。つまり、`connect`操作で例外を送出する場合とは、基本的にはこの時に呼ばれるコピー/ムーブコンストラクタが例外を送出する場合です。

自身のムーブ/コピーコンストラクタが例外を送出するどうかについては自身の性質なのですぐにわかりますが、`receiver`型がどうかどうかはその型の性質を参照しないと分かりません。しかし、前述のように直接参照することができず、この性質は環境からも取得できないため、`sender`から見た時の`receiver`の具体的な型の唯一の重要な性質となります。

コピーについては`connect`メンバ関数の引数型を値で受けるようにすることで、`connect`操作の呼び出し側の責任にすることができます。したがって、問題となるのはムーブコンストラクタの例外送出に関する性質のみです。

この時、`receiver`コンセプトの要件の一部として、`receiver`型のムーブコンストラクタからの例外送出が禁止されていれば、この問題は解消し、`sender`から見た`receiver`の唯一の性質は環境のみであるという状態が復元されます。

提案している2つのことはこれらのような理由によります。提案2の3つの選択肢は、その制限の強さと確実性の度合いによるものです。

- [P3388 進行状況](https://github.com/cplusplus/papers/issues/2043)

### [P3389R0 Of Operation States and Their Lifetimes (LEWG Presentation 2024-09-10)](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3389r0.pdf)
### [P3390R0 Safe C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3390r0.html)

```cpp
// safety関連の機能をonにする
#feature on safety

// 安全な標準ライブラリをインクルード
#include <std2.h>

// safe指定子付きmain()
// UBにつながる操作を禁止する
int main() safe {
  std2::vector<int> vec { 11, 15, 20 };

  for(int x : vec) {
    // Ill-formed. mutate of vec invalidates iterator in ranged-for.
    if(x % 2) {
      // safetyコンテキストでは、左辺値はデフォルトでimmutable
      mut vec.push_back(x);
    }

    std2::println(x);
  }
}
```

### [P3391R0 `constexpr std::format`](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3391r0.html)

`std::format()`を`constexpr`化する提案。

P2741R3の採択によって、`static_assert()`のエラーメッセージとして`std::string`を渡せるようになりました。ただし、ここに渡す`std::string`を生成するために便利な`std::format()`は定数式では使用できません。

`std::format()`は内部的に型消去を用いてフォーマット対象引数を扱っていた（`const T*`から`const void*`へのキャストが必要だった）ために定数式で使用可能にすることはできませんでしたが、これはP2738R1の採択によって可能になっており、さらにはそれを`placement new`を用いて構築することもできるようになっています（P2747R2）。

これにより、`std::format()`を`constexpr`化する事を妨げるものは無くなっているため、ここではそれを提案しています。

ただ、そのまま`constexpr`を付加するだけで終わるほど簡単ではなく、定数式で使用可能な型のうち2種類の型ではそれが困難なことが分かっています。

1つは浮動小数点数型です。`std::format()`においては整数型と浮動小数点数型の文字列化に`std::to_chars()`を使用しています（実装は直接使用していないかもしれませんが、やっていることは同じです）。しかし、`std::to_chars()`のオーバーロードのうち定数式で使用可能なのは整数型のもののみで浮動小数点数型のオーバーロードは使用可能ではありません。

これは`std::to_chars()`が文字列化のアルゴリズムを明示的に指定していないことや、そのようなアルゴリズムが定数式で実行可能ではないことなどの事情があり、整数型が`constexpr`指定された時点（P2291R3）でも現在でも浮動小数点数型のオーバーロードを`constexpr`にすることはできないようです。

もう1つは`<chrono>`の型で、こちらは`std::basic_ostringstream<char>`を介してストリーミングされるのと同様にフォーマットされるように規定されており、当然iostreamの型（および内部のフォーマット実装）には`constexpr`を付加できません。

これを動作させるには`<chrono>`型のフォーマットの動作を変更する必要があると思われます。

この提案では、どちらの型に対しても更なる議論を行わずに、これらの型と定数式で使用可能ではない型（`stacktrace_entry`や`filesystem::path`など）を除いた、既存の標準のフォーマット可能な型についてのみ、コンパイル時のフォーマットを有効化することを提案しています。

{fmt}ライブラリでは`<chrono>`型を除いて`constexpr`な`format()`がすでにサポートされているほか、libstdc++の実装においても関数に`constexpr`を付加するほかは2か所の変更のみでこの提案の内容を実装可能だったようです。

- [P3391 進行状況](https://github.com/cplusplus/papers/issues/2046)

### [P3392R0 Do not promise support for function syntax of operators](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3392r0.pdf)

標準ライブラリの演算子オーバーロードは関数構文での呼び出しをサポートしていないことを明確化する提案。

オーバーロードされた演算子`@`は`a @ b`や`@a`等のように演算子として使用する他に、関数構文（`a.operator@(b)` or `operator@(a, b)`）によっても呼び出すことができます。標準ライブラリの演算子についても同様ではありますが、この提案はそれをサポートしていない（演算子としての使用のみが可能である）事を明確化しようとするものです。

その意図は、標準ライブラリが演算子の実装方法（メンバ/非メンバオーバーロード）を変更する権利を持つことを留保する事にあります。そして、ユーザーの期待にそぐわない将来/未来の動作に依存したコードにおける問題の発生を防止するために、このことを明確化しようとしています。

ただし、`operator->`と`new/delete`演算子（配列版含む）はこの例外とされます。`operator->`は再起的に呼び出して結果を取得するためにメンバ構文（`a.operator->()`）による呼び出しが許可されており、`new/delete`演算子は直接呼び出すことでメモリの確保・解放のみを行うことができるためです。

- [P3391 進行状況](https://github.com/cplusplus/papers/issues/2046)

### [P3396R0 `std::execution` wording fixes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3396r0.html)

`std::execution`に関する規格文言の問題修正をまとめた提案。

これは、`std::execution`提案（P2300）に関するGithubのIssueトラッカー（https://github.com/cplusplus/）において、残ったままになっていた問題（LWG Issue相当）について、効率的な処理のために1つの提案にまとめたものです。

ここでは次の10件の問題とその解決案が提案されています

1. The preconditions on `run_loop::run()` are too strict
2. `noexcept` clause of basic-state constructor is incomplete
3. Definition of an async operation’s environment’s ownership seems incorrect
4. scheduler semantic requirements imply swapability but concept does not require it
5. `operation-state-task` exposition-only type does not need a move constructor
6. [exec.general] Wording for AS-EXCEPT-PTR should use 'Precondition:' instead of 'Mandates:' for runtime properties
7. [exec.schedule.from] Potential access to destroyed state in `impls-for::complete`
8. scheduler concept should require that move-constructor does not exit with an exception
9. [exec.bulk] wording should indicate that f is called with i = [0, …, shape-1]
10. The use of JOIN-ENV leads to inefficient implementations of composed environments

それぞれの詳細は提案を参照してください。

- [P3391 進行状況](https://github.com/cplusplus/papers/issues/2048)

### [P3397R0 Clarify requirements on extended floating point types](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3397r0.pdf)

拡張浮動小数点数型の算術演算について、ISO/IEC 60559に準拠すべきかどうかを明確にする提案。

C++23では`std::float32_t`などの拡張浮動小数点数型が導入されました。`std::bfloat16_t`を除いて、これらの型はISO/IEC 60559(IEEE 754)の定める交換形式と対応する表現を持つように指定されています。

ただ、ISO/IEC 60559では浮動小数点数型の表現やフォーマットだけでなく、算術演算の再現性についても指定しています。そこでは、浮動小数点数型に対する算術演算が実行されたハードウェアやソフトウェアによらず、それらをどう組み合わされて実行された時でも同じ計算について同じ結果を生成することを要求するほか、丸めも正しく行うことを要求しています。良く知られているように、C++の標準浮動小数点数型はこの要件を全く満たしていません。

この提案が問題にしているのは、拡張浮動小数点数型についても同じことがいえるのか？という点です。`std::float32_t`等の型が定義される場合、その性質はISO/IEC 60559で指定される、というように規定していますが、これがフォーマット（表現）のみなのか、算術演算についてもなのかが不透明です。

委員会の中でもこの解釈は割れているようで、ある小グループではこの規定は表現にのみ適用されるという合意がされている一方で、SG6は逆に演算にも適用されるという投票を行ったことがあります。

もし仮に、表現に加えて演算についてもISO/IEC 60559に準拠する場合、その実装は既存の標準浮動小数点数型とは全く異なる実装が必要になり、`<cmath>`の関数群も同様に厳格な実装が求められます。そしてその実装では最適化は著しく制限され、拡張浮動小数点数型は標準浮動小数点数型と比較するとパフォーマンスで劣るようになるでしょう。特に、一部のハードウェアではサポートされていない場合もあるため、ソフトウェアによる実装になる場合もあります。これは、拡張浮動小数点数型が導入されたきっかけが機械学習におけるパフォーマンス目的であるという明らかな文脈にはそぐわない解釈です。

しかし、それでもなお現在の規格の文面は拡張浮動小数点数型のISO/IEC 60559への準拠が「表現のみ」なのか「演算も」なのかが曖昧であるため、これを明確化する必要があります。この提案ではそれについて文言を修正することを提案しています。

方向性について合意が取れたものではないですが、拡張浮動小数点数型の経緯などから、現在のリビジョンでは「表現のみ」の解釈を明確化する方向で文面を調整する提案を行っています。

- [`<stdfloat>` - cpprefjp](https://cpprefjp.github.io/reference/stdfloat.html)
- [P3397 進行状況](https://github.com/cplusplus/papers/issues/2049)

### [P3398R0 User specified type decay](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3398r0.pdf)

あるクラス型について、推論される型を指定するための`decays_to(T)`の提案。

この提案のモチベーションは、未発表の文字列補完提案（`f`リテラル）におけるパフォーマンス低下やダングリングの問題を回避する事にあります。`f`リテラルはその使用が`std::format()`の呼び出しになる事を要求するリテラルで、`f""`の形の文字列リテラル内の`{}`内を置換フィールドとしてその内部の文字列については識別子名としてそのコンテキストから拾ってくるものです。

```cpp
// fリテラルによって構築される型
template<...>
struct formatted_string decays_to(std::string) {
  ...
};

std::string x = "x";
auto s = f"value {x + "y"}";  // ok "xy"
// sは"xy"という文字列を保持するstd::string型、ダングリングの心配はない

// std::printの新しいオーバーロード
extern void std::print(const formatted_string& s);

std::print(f"value {x + "y"}"); // パフォーマンスの劣化が無い（std::stringの生成をしない）
```

`f`リテラルの生成結果が`std::string`である場合、`std::cout << std::format(...)`と同じパフォーマンスの問題が発生します。それを回避するために、`f`リテラルの結果はフォーマットに必要な情報（`format_args`と`format_string`）を保持している独自の型（例の`formatted_string`）となっています。ただし、この場合は`f`リテラルの結果を`auto`で受けたりするとダングリング参照を生成してしまいます。

この場合に、`f`リテラルの結果を`auto`で受けるような場合にのみ、その結果を`std::string`に変換してしまうための仕組みがこの提案です。

型の定義時に`decays_to(T)`と指定（`final`等と同じ）しておくことで、`auto`やテンプレートパラメータの推論時にこの指定した型`T`に推論されるように指定します。

上記の例だと、`formatted_string`型に`decays_to(std::string)`と指定されていることで、`auto s = f"value {x + "y"}"`で推論される`s`の型は`std::string`になり、`formatted_string`型が`std::string`に暗黙変換可能であることによって`f`リテラルの結果はダングリング化する前に`std::string`に変換され、以降安全に使用可能になります。

`std::print`には`formatted_string`型を直接受け取るオーバーロードが用意されることで、`formatted_string`型を直接受け取ることができるため、`f`リテラルの出力のために`std::string`が逐一生成されることはありません。

この提案の内容はまた、式テンプレートにおけるよく知られた問題に対処することもできるようになります。式テンプレートは、型に式の構造を埋め込んでしまうことで式の構造を保存して、結果が必要になった時に初めて実際の計算を行うようにします。これにより、複雑な計算を実行する際の中間変数やコピーを削減することができます。

例えばC++の行列演算ライブラリの実装においては式テンプレートを用いて行列演算の実行を遅延評価することが行われますが、式テンプレートという技法を知らない場合に、式テンプレートが適用されている演算の結果を`auto`で受けたりテンプレートパラメータとして推論されるところににそのまま渡してしまったりすると、計算結果ではなく式テンプレートの中間構造型が得られてしまいます。この型は本来欲しかった結果型と同じように扱うことができなかったり、そのまま結果取得をしようと何度もアクセスすると、アクセスの旅に再計算が走ってしまうなどの問題があります。

```cpp
template<typename L, typename R, typename Op>
class Binop<L, R, Op> decays_to(Matrix) {
public:
  Binop(explicit const& L lhs, explicit const& R rhs) :
    lhs(lhs), rhs(rhs)
  {}

  operator Matrix() {
    Matrix ret;
    for (int r = 0; r < lhs.height(); r++)
    for (int c = 0; c < lhs.width(); c++)
    ret[r, c] = operator[](r, c);
    return ret;
  }

  double operator[](size_t r, size_t c) const { return op(lhs[r, c], rhs[r, c]); }
  size_t width() const { return lhs.width(); }
  size_t height() const { return lhs.height(); }

private:
  L lhs;
  R rhs;
  OP op;
};

template<typename LHS, typename RHS>
explicit auto operator+(LHS&& lhs, RHS&& rhs) {
  return Binop<LHS, RHS, std::plus<>>(lhs, rhs);
}

Matrix a, b, c;

Matrix d = a + b + c;     // 両方の加算は要素ごとにまとめて行われる（遅延評価が効いている）
auto e = a + b + c;       // eはMatrix型
explicit auto p = a + b;  // decayを無効化する（Binop型が得られる
auto f = p + c;           // fはMatrix型であり、この計算のパフォーマンスはd,eと同じ
```

式テンプレートにおける計算の中間型にこの提案の`decays_to`によって結果となる行列型を指定しておくことで、`auto`で受けられた時に中間型ではなく結果の行列型として取得させることができます。

この提案では`explicit`を提案する`decays_to`の抑制指示に使用しており、この例の`operator+`は戻り値型推論時にdecayすることなく中間の`Binop`型をそのまま返し、変数宣言において`explicit auto`とすることで`decays_to`の指示する型ではなく本来の型に推論させることができます。

あるクラス型`C`に対して`decays_to(T)`と指定している時に`auto`推論などで`C`オブジェクトの型が`T`に推論される場合、あくまで結果型が`T`に推論されるようにするところまでがこの提案で、`C -> T`への変換については従来通りの扱いとなり、変換が可能ではない場合はコンパイルエラーとなります。

また、`decltype(auto)`の場合は`decays_to(T)`に対して`T`が推論されますが、それ以外の場合（`const auto&`や`const T`等の推論時）はプレイスホルダ型もしくはテンプレートパラメータに付加されているCV・参照修飾が`T`に対して適用されます。

`decays_to(T)`によって`T`に推論されるのは、型推論が実行されるすべてのコンテキストで行われます（関数戻り値型推論や、構造化束縛などを含む）。

同様に、型推論が行われるすべてのコンテキストにおいて、推論対象の型を表すもの（テンプレートパラメータやプレイスホルダ型）に対して`explicit`を付加しておくことで、この機能による推論を無効化して本来の型を得ることができます。

```cpp
template<typename T>
void f(explicit const T& x);


f<std::string>(f"Not deduced {"and not decayed"}"; // Call f<std::string>
```

最後に、この機能に関する型特性として`std::decay`を更新し、`std::decay`が`decays_to(T)`指定されている型に対しては`T`を帰す様に更新し、ある型に`decays_to(T)`が指定されているかどうかを取得する型特性`std::has_decays_to<T>`の追加を提案しています。

この提案はEWGiのレビューにおいてさらに時間をかけて議論する合意を得られませんでした。

- [P3398 進行状況](https://github.com/cplusplus/papers/issues/2050)

### [P3401R0 Enrich Creation Functions for the Pointer-Semantics-Based Polymorphism Library - Proxy](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3401r0.pdf)

Proxyを構築するユーティリティ関数の提案。

Proxyとは、P3086で提案されている仮想関数と継承を利用しないで動的なポリモルフィズムを実現しようとするライブラリです。この提案はそこから構築に関するユーティリティを分離したものです。

提案されているの次の3つです

- `make_proxy()`: 指定された値によって`proxy`オブジェクトを構築する際に、SBOを有効化して構築する
- `allocate_proxy()`: カスタムアロケータを用いて`proxy`オブジェクトを構築する。`std::allocate_shared`と同じ使用感
- `make_proxy_inplace`: std::optionalと同様に、与えられた値を自身のストレージ内に保存するSBOポインタを提供します。inplace proxiable targetというコンセプトを満たす型に対して使用できます.

`proxy`クラスは通常ヒープを用いてその値を保持しますが、内部バッファに収まる場合はSBO(small buffer optimization)によってメモリ確保を回避することができます。ただしそれが可能な型のサイズなどは実装詳細でありユーザーが気にするべきことではなく、自動的に判定してほしいものがあります。ところが、`proxy`のコンストラクタは保持する型`T`のポインタを受け入れるようになっているため、`proxy`に渡された時点で動的メモリ確保は完了しています。

例えば`year`というクラスの値を`proxy`で保持するためには次のように書きます

```cpp
struct year {
  static constexpr proxiable_ptr_constraints constraints{
    .max_size = sizeof(void*[2]),
    .max_align = alignof(void*[2]),
    .copyability = constraint_level::none,
    .relocatability = constraint_level::nothrow,
    .destructibility = constraint_level::nothrow
  };
  // other members to meet the facade name-requirement.
};

std::proxy<year> CreateYear() {
  return std::make_unique<int>(2024); // std::proxy<year>へ暗黙変換
}
```

`int`の値などは明らかにSBOの対象ですが、ユーザーが指定したポインタを受け取る以上`proxy`の型内部でSBOを自動適用することができません。そこで、この提案のファクトリ関数`make_proxy()`でそれを行うようにします。

```cpp
std::proxy<year> CreateYear() {
  return std::make_proxy<year>(2024); // 動的メモリ確保されない
}
```

`make_proxy()`は内部で渡された値がSBO可能かどうかによってSBOを適用するしないを自動で判定したうえで`proxy`オブジェクトを構築するものです。SBOが適用されない場合、ヒープ領域に確保されたうえで、所有権管理が行われます（おそらく`unique_ptr`によって）。

`proxy`は通常所有権を引き取らないため渡すポインタのリソースの管理はユーザーの責任ですが、`make_proxy()`を使うと`proxy`にそれを委ねることができます。この場合にメモリの確保をカスタマイズしようとすると再び手動でリソース管理を行わなければならなくなるため、アロケータも一緒に渡すようにするのが`allocate_proxy()`です。

```cpp
auto CreateHugeYear(){
  // sizeof(std::array<int, 1000>) is usually greater than the max size defined in facade,
  // calling allocate proxy has no limitation to the size and alignment of the target
  using HugeYearData = std::array<int, 1000>;

  return std::allocate_proxy<year, HugeYearData>(std::allocator<HugeYearData>{});
}
```

この関数はちょうど`std::allocate_shared()`とよく似た使用感になります。

`make_proxy_inplace()`はinplace構築を行う`make_proxy`です。これは`std::optional`のinplaceコンストラクタに対応する`std::make_optional()`と同じような役割のものです。

先ほどの`make_proxy()`の例に対して

```cpp
auto CreateYear() {
  return std::make_proxy_inplace<year, int>(2024);
}
```

この提案の内容はP3086で提案されているライブラリ機能をベースとして、その構築を便利にするためのユーティリティだけを分離して提案しているものです。

- [P3086R0 Proxy: A Pointer-Semantics-Based Polymorphism Library - WG21月次提案文書を眺める（2024年01月）](https://onihusube.hatenablog.com/entry/2024/03/10/170322#P3086R0-Proxy-A-Pointer-Semantics-Based-Polymorphism-Library)
- [P3401 進行状況](https://github.com/cplusplus/papers/issues/2051)

### [P3402R0 A Safety Profile Verifying Class Initialization](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3402r0.html)

クラスのすべてのサブオブジェクトが初期化されていることを保証するプロファイルの提案。

この提案はP3274で提案されているプロファイル機能の1つとして、クラスを構築した後でそのクラスのすべてのサブオブジェクト（メンバ変数と基底クラス）が何かしら初期化済みであることを強制し保証するプロファイルを提案するものです。

提案するのは`[[Profiles::enable(initialization)]]`というプロファイル属性で、クラスの定義に対して付加します。

```cpp
struct [[Profiles::enable(initialization)]] parent1 {
  int i;
  parent1() = default; // iが初期化されていないためプロファイルに準拠していない（parent1は未検証）
};

struct [[Profiles::enable(initialization)]] child1 : public parent {
  int j;
  child1() : parent1(), j(42) {} // child1自体はプロファイル準拠している
}

// 検証済みのクラスではない
// プロファイルが指定されれば準拠できる
struct parent2 {
  int i = 0;
  parent2() = default;
};

struct [[Profiles::enable(initialization)]] child2 : public parent2 {
  int j;
  child2() : parent2(), j(42) {} // parent2が検証済みではないため、child2も未検証
}
```

スカラ型もしくはこのプロファイルが指定されているクラス型は検証済みのクラスと呼びます。検証済みのクラスのすべてのコンストラクタは次のプロパティを満たす必要があります

- 全ての基底クラスは検証済み
- 全ての基底クラスは、その非静的メンバ変数が読み取られる前に初期化されている
- 全ての検証済みメンバ変数は、その非静的メンバ変数が読み取られる前に初期化されている
- 全ての検証済みメンバ変数は、全てのパスで初期化されている
- 明示的に除外されているメンバ変数やそのメンバ変数は読み取れない
- 全ての非静的メンバ変数が初期化されるまで、オブジェクト引数（`this` or 明示的オブジェクト引数）の使用は制限される
    - 制限されている場合、オブジェクト引数は非静的メンバ変数へのアクセスにのみ使用できる（初期化のため）
- 全ての非静的メンバ変数が初期化されるまで、コンストラクタは検証済みのクラスのコンストラクタのみを呼び出すことができる
    - それまでは、他の関数の呼び出しは禁止される
- 関数呼び出しの戻り値は、直接的にも間接的にもメンバ変数に代入することはできない
- 検証においては、デフォルト初期化は何かを初期化しているとはみなされない

任意の関数内において非静的メンバ変数が参照されている場合、次の場合を除いてそれは読み取られたとみなされます

- 評価されないオペランドで使用されている
- 破棄された文の一部である
- 代入式の左オペランドである
- コンストラクタ呼び出しの受け取りオブジェクトである

提案文書より、サンプルコード

```cpp
struct [[Profiles::enable(initialization)]] clazz1 {
  int i;
  int j;
  int z = 0;

  clazz1() {
    i = 123;

    if (nondet) {
      j = 456;
    }
    // 非準拠: jは全てのパスで初期化されていない
  }
};
```
```cpp
struct [[Profiles::enable(initialization)]] clazz2 {
  int i;
  int j;

  clazz2() : i(j), j(42) {} // 非準拠: jが初期化される前に読み取られる
};
```
```cpp
struct [[Profiles::enable(initialization)]] clazz3 {
  int i;
  int j;

  // 準拠できているものの、良くない形
  clazz3() {
    this->i = 0;
    this->j = 42;
  }
};
```
```cpp
struct pod {
  int i;
  int j;
};

struct [[Profiles::enable(initialization)]] clazz4 {
  pod p;
  clazz4() = default; // pはデフォルト初期化のため、非準拠
};

struct [[Profiles::enable(initialization)]] clazz5 {
  pod p{};
  clazz5() = default; // pは値初期化されており、準拠している
}


struct [[Profiles::enable(initialization)]] clazz6 {
  pod podFactory() {
    pod p;    // pはデフォルト初期化されている
    return p;
  }

  clazz6() : p(podFactory()) {} ; // 非準拠、pは関数戻り値で初期化されている
}
```
```cpp
struct [[Profiles::enable(initialization)]] clazz7 {
  int i;
  int j;

  clazz7(int i) : i(i), j() {}; // jは値初期化されており、準拠している
};
```

クラステンプレートの場合は、インスタンス化にあたって検証作業が行われます

```cpp
class NotAnnotated{/**/};
class [[Profiles::enable(initialization)]] Annotated {/**/};

template<typename T>
class [[Profiles::enable(initialization)]] AnnotatedTemplate {
  T field = T();
};


void foo() {
  AnnotatedTemplate<NotAnnotated> nat {}; // 非準拠、検証されていないクラスのコンストラクタを呼び出している
  AnnotatedTemplate<Annotated>     at {}; // 準拠している
}
```

このプロファイルに準拠しているクラス型は、そのコンストラクタ呼び出しの後で全てのメンバ変数と基底クラスが初期化済みであることが保証され、その観点からは安全に使用することができます（明確ではないですが、検証に失敗するとコンパイルエラーになるはずです）。

また、提案するプロファイルの下で特定のデータメンバを検証から除外するためには、`[[indeterminate]]`属性を利用することを提案しています（この属性自体はC++23で追加されたもの）。

- [P3274R0 A framework for Profiles development - WG21月次提案文書を眺める（2024年05月）](https://onihusube.hatenablog.com/entry/2024/11/24/155428#P3274R0-A-framework-for-Profiles-development)
- [P3402 進行状況](https://github.com/cplusplus/papers/issues/2052)
