# ［C++］契約のこれまで、これから

[:contents]

### C++ Contracts

ContractとはContract programmingの略称で、C++ ContractsとはC++における契約プログラミング機能を指す言葉です（sは付いたり付かなかったりします）。

C++ Contractsとは、契約プログラミングという考え方に基づいた設計（契約による設計）をより自然に行えるようにするための言語機能です。契約プログラミングについてはあまり深入りしないので各自ググってください。

- [契約プログラミング - Wikipedia](https://ja.wikipedia.org/wiki/契約プログラミング)

契約による設計の中心概念には、関数の事前条件・事後条件とクラスの不変条件という3つのものがあります。C++ Contractsがまず導入しようとしているのは、前者の関数の事前条件・事後条件をコードとして記述しそれを実行時にチェックできるようにする機能です。

C++ Contractsのユースケースは単に契約プログラミングの実現のためという訳ではなく、それを含めてさまざまなものが想定されています

- 契約プログラミング（契約による設計）を言語機能によって実現する
- 現在ドキュメントに記載されている関数に対する契約（事前条件・事後条件）をコードで記述する
- より高機能な実行時検査のための言語機能
    - 特に、関数呼び出しの境界において
- 実行時検査時の契約違反ハンドラによる検査結果のより効果的なハンドリング
    - ログ出力
    - 安全なシャットダウン
- ユニットテストのための利用
- ツールが契約アノテーションを読み取ることで、静的解析に役立てる
    - 静的解析ツールの能力向上
    - 形式検証を可能にする拡張（将来）

など。

- [P2755R0 A Bold Plan for a Complete Contracts Facility](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2755r0.pdf)

### C++20 Contracts

C++ Contractsは一旦はC++20

- [契約に基づくプログラミング - cpprefjp](https://cpprefjp.github.io/lang/future/contract-based_programming.html)
- [C++20 Contract #C++ - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)
### 問題点とMVP

### C++26に向けたロードマップ

### MVPの改善

### CCAのセマンティクス

- [P2834R1 Semantic Stability Across Contract-Checking Build Modes](https://wg21.link/P2834R1)
- [P2877R0 Contract Build Modes, Semantics, and Implementation Strategies](https://wg21.link/P2877R0)

### 違反ハンドラ

- [P2811R7 Contract-Violation Handlers](https://wg21.link/P2811R7)

### 構文

- [P2961R0 A natural syntax for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2961r0.pdf)

### C++26に向けて、残りの問題

- [P2932R0 A Principled Approach to Open Design Questions for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2932r0.pdf)

### 参考文献

- [C++20 Contract - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)
- [契約に基づくプログラミング - cpprefjp](https://cpprefjp.github.io/lang/future/contract-based_programming.html)
- [C++20 Contract #C++ - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)
- [P0542R5 Support for contract based programming in C++](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0542r5.html)
- [2019-07 Cologne ISO C++ Committee Trip Report - reddit](https://www.reddit.com/r/cpp/comments/cfk9de/201907_cologne_iso_c_committee_trip_report_the/)
- [P1823R0 Remove Contracts from C++20](https://www.reddit.com/r/cpp/comments/cfk9de/201907_cologne_iso_c_committee_trip_report_the/)
- [P2755R0 A Bold Plan for a Complete Contracts Facility](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2755r0.pdf)
- [P2932R0 A Principled Approach to Open Design Questions for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2932r0.pdf)
- [P2961R0 A natural syntax for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2961r0.pdf)
