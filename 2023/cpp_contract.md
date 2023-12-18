# ［C++］契約のこれまで、これから

[:contents]

### C++ Contracts

ContractとはContract programmingの略称で、C++ ContractsとはC++における契約プログラミング機能を指す言葉です（sは付いたり付かなかったりします）。

C++ Contractsとは、契約プログラミングという考え方に基づいた設計（契約による設計）をより自然に行えるようにするための言語機能です。契約プログラミングについてはあまり深入りしないので各自ググってください。

- [契約プログラミング - Wikipedia](https://ja.wikipedia.org/wiki/契約プログラミング)

契約による設計の中心概念には、関数の事前条件・事後条件とクラスの不変条件という3つのものがあります。C++ Contractsがまず導入しようとしているのは、前者の関数の事前条件・事後条件をコードとして記述しそれを実行時にチェックできるようにする機能です。

C++ Contractsは単に契約プログラミングの実現のためだけのものという訳ではなく、それを含めてさまざまなものが想定されています。例えば

- 契約プログラミング（契約による設計）を言語機能によって実現する
- 現在ドキュメントに記載されている関数に対する契約（事前条件・事後条件）をコードで記述する
    - そして、デバッグ時にそれを検査することができる
- より高機能な実行時検査のための言語機能
    - 特に、関数呼び出しの境界においての実行時検査方法の提供
    - デバッグ時はもちろんとして、リリースバイナリにおいても有用な実行時検査方法の提供
- 実行時検査の違反時のより効果的なハンドリング
    - より高度なログ出力や安全なシャットダウンなどを可能にする
- ユニットテストのための基盤機能としての利用
- ツールが契約アノテーションを読み取ることで、静的解析に役立てる
    - 静的解析ツールの能力向上
    - 形式検証を可能にするようなアノテーション拡張（将来？）

などです。もちろん、ここに記載されていないものや、実際に利用可能になってから開けるユースケースもあるでしょう。いずれにせよ、C++ ContractsはC++コードをさらに安全に記述する事に確実に貢献する機能です。

これらのユースケースの実現には単に事前条件・事後条件を記述できるようにするだけでは足りず、その周辺の諸機能が必要となることが想像できると思います。それらを含めたC++ Contractsは単純な言語機能ではなく、実装され実使用される場合の事を考慮して設計されなければなりません。そのため、その議論はかなり難しく時間を要するものになっています。

### C++20 Contracts

C++ ContractsはC++20に対してP0542で提案され、2018年6月に一旦C++20ドラフトにマージされました。

- [P0542R5 Support for contract based programming in C++](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0542r5.html)

この提案自体もどうやら2013年頃から継続された議論の一つの集大成であったようです。あまり踏み込まないので詳しくは当時書かれた別の記事をご覧ください

- [契約に基づくプログラミング - cpprefjp](https://cpprefjp.github.io/lang/future/contract-based_programming.html)
- [C++20 Contract #C++ - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)

cpprefjpのサンプルコードを拝借すると、構文的には次のようなものでした

```cpp
#include <iostream>
#include <cmath>

double sqrt_checked(double x)
  [[expects: x > 0]]   // 引数に対する事前条件
  [[ensures r: r > 0]] // 戻り値に対する事後条件
{
  return std::sqrt(x);
}

int main()
{
  double x;
  std::cin >> x;

  [[assert: x > 0]]; // アサーション

  double y = sqrt_checked(x);

  std::cout << y << '\n';
}
```

事前・事後条件および中間のアサーションのためにはこのような属性様構文を使用しており、これがチェックされるかどうかはビルドレベルによって制御します。

ビルドレベルは全ての契約条件がチェックされるモード、一部だけがチェックされるモード、全てがチェックされないモードの3つがありコンパイルオプションで指定します。

契約条件がチェックされている場合に契約条件が破られる（`false`となる）と、違反ハンドラと呼ばれる関数が呼ばれてプログラムは終了します。違反ハンドラはユーザーがカスタマイズできるものではなくその内容については実装定義でした。また、契約が破られた場合に実行を継続するモードも用意されており、これもコンパイルオプションで指定します。

基本的な機能は抑えておりこれでも実際に使用できるようになれば有用だったのでしょうが、色々議論が紛糾した結果、2019年7月の全体会議においてC++20から削除することが決定され削除されてしまいました。

### 問題点とMVP

C++20 Contractsは一旦はドラフト入りしたものの、1年後の2019年7月に削除することが合意されC++20から削除されてしまいました。

- [P1823R0 Remove Contracts from C++20](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1823r0.pdf)
- [2019-07 Cologne ISO C++ Committee Trip Report — 🚀 The C++20 Eagle has Landed 🚀 (C++20 Committee Draft shipped; Contracts Moved From C++20 to a Study Group; `std::format` in C++20; C++20 Synchronization Library) : r/cpp](https://www.reddit.com/r/cpp/comments/cfk9de/201907_cologne_iso_c_committee_trip_report_the/)
- [Trip report: Summer ISO C++ standards meeting (Cologne) – Sutter’s Mill](https://herbsutter.com/2019/07/20/trip-report-summer-iso-c-standards-meeting-cologne/)

直接の提案（P1823R0）や標準化会議参加者のレポ等を要約すると、ドラフトへのマージ後に設計変更が相次ぎ、しかもそれに統一的な合意を得ることができず、実装経験不足を含めた問題が提起され、それによって現在の設計が出荷に値するものではないことが分かったため、とのことです。

例えば、2019年に提出されたContracts関連の提案はリビジョン改定含めて47本に及び（[2019年の提案一覧](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/)をcontractというワードでページ検索）、そのほぼ全てが2019年7月ごろまでの間に提出されています。なお、前年は19本、翌年は8本でした。

なんとなく納得はできますがあまり具体的ではありません。具体的に何が問題だったのでしょうか？47本の提案のタイトルを眺めていると議論が紛糾している様はわかりますが個別に見ていくのは辛いものがあります。幸いなことに、後に争点をまとめた文書があります。

- [P2076R0 Previous disagreements on Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2076r0.html)

これによると

- 契約違反後の継続
    - 契約違反後に継続できるべきかどうか
    - 継続できるようにするとして、それはグローバルなスイッチ（コンパイラオプション）とローカルなスイッチ（個別の契約条件ごとの指定）のどちらによって制御されるべきか？
- ビルドレベル
    - 上記も含めた、制御がグローバルであること
- 継続するかしないか、ビルドレベルなどがソースコードの外（おそらくコンパイラオプション）で設定されること
- Literal semantics（in-source controls）
    - 個々の契約に対して個別にチェックするか否かを指定したり、それがグローバルフラグの影響を受けないようにしていた
- Assumption
    - （上記の事によって）axiomではないのにチェックされていない契約条件の存在が想定される

これらの（相互に絡み合う）問題について合意を得ることができず、またその見通しも立たなかったためにC++20 Contractsは一旦取り下げられたわけです。

とはいえこのような議論の紛糾はContractsそのものに対する反対ではなくその設計に反対するもので、Contractsそのものの有用性は認められていたため、Contractsの再設計を行う専門のStudy Group（SG21）を設立し、将来機能として引き続き議論していくことになりました。

- [P2182R0 Contract Support: Defining the Minimum Viable Feature Set](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2182r0.html)



### C++26に向けたロードマップ

### MVPの改善

### CCAのセマンティクス

- [P2834R1 Semantic Stability Across Contract-Checking Build Modes](https://wg21.link/P2834R1)
- [P2877R0 Contract Build Modes and Semantics](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2877r0.pdf)
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
- [標準化会議 - C++ の歩き方 | cppmap](https://cppmap.github.io/standardization/meetings/)
