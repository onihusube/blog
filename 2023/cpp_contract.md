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

事前・事後条件および中間のアサーションのためにはこのような属性様構文によって注釈を行い、これがチェックされるかどうかはビルドレベルによって制御します。

ビルドレベルは全ての契約条件がチェックされるモード、一部だけがチェックされるモード、全てがチェックされないモードの3つがありコンパイルオプションで指定します。

契約条件がチェックされている場合に契約条件が破られる（`false`となる）と、違反ハンドラと呼ばれる関数が呼ばれてプログラムは終了します。違反ハンドラはユーザーがカスタマイズできるものではなくその内容については実装定義でした。また、契約が破られた場合に実行を継続するモードも用意されており、これもコンパイルオプションで指定します。

基本的な機能は抑えておりこれでも実際に使用できるようになれば有用だったのでしょうが、色々議論が紛糾した結果、2019年7月の全体会議においてC++20から削除することが決定され削除されてしまいました。

### 問題点とMVP

C++20 Contractsは一旦はドラフト入りしたものの、1年後の2019年7月に削除することが合意されC++20から削除されてしまいました。

- [P1823R0 Remove Contracts from C++20](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1823r0.pdf)
- [2019-07 Cologne ISO C++ Committee Trip Report — 🚀 The C++20 Eagle has Landed 🚀 (C++20 Committee Draft shipped; Contracts Moved From C++20 to a Study Group; `std::format` in C++20; C++20 Synchronization Library) : r/cpp](https://www.reddit.com/r/cpp/comments/cfk9de/201907_cologne_iso_c_committee_trip_report_the/)
- [Trip report: Summer ISO C++ standards meeting (Cologne) – Sutter’s Mill](https://herbsutter.com/2019/07/20/trip-report-summer-iso-c-standards-meeting-cologne/)

直接の提案（P1823R0）や標準化会議参加者のレポ等を要約すると、ドラフトへのマージ後に設計変更が相次ぎ、しかもそれに統一的な合意を得ることができず、実装経験不足を含めた問題が提起され、それによって現在の設計が出荷に値するものではないことが分かったため、のようです。

例えば、2019年に提出されたContracts関連の提案はリビジョン改定含めて47本に及び（[2019年の提案一覧](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/)をcontractというワードでページ検索）、そのほぼ全てが2019年7月ごろまでの間に提出されています。なお、前年は19本、翌年は8本でした。

なんとなく納得はできますがあまり具体的ではありません。具体的に何が問題だったのでしょうか？47本の提案のタイトルを眺めていると議論が紛糾している様はわかりますが個別に見ていくのは辛いものがあります。幸いなことに、後に争点をまとめた文書があります。

- [P2076R0 Previous disagreements on Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2076r0.html)

これによると

- 契約違反後の継続
    - 契約違反後に継続できるべきかどうか
    - 継続できるようにするとして、それはグローバルなスイッチ（コンパイラオプション）とローカルなスイッチ（個別の契約条件ごとの指定）のどちらによって制御されるべきか？
- ビルドレベル
    - 全ての契約注釈のセマンティクスはビルドレベルによって一律に制御されるが、それは可能なのか？
    - また、ある契約注釈がチェックされるかどうかを決定するのがグローバルなビルドレベルだけであるべきか？
    - よりきめ細かい制御の方法を望む向きがあり、それらを並立させた場合にデフォルトはなんであるべきか、あるいは契約注釈のセマンティクスを制御できる方法が複数提供されないほうが良いか？
- グローバルスイッチの存在
    - 全ての契約注釈のセマンティクス及び有効/無効は全てグローバル制御になっているが、ローカルな制御を望む向きもあった
    - グローバルな契約機能の有効化/無効化は全ての契約注釈に影響を与えるのか、一部の注釈だけがそのグローバル設定を上書きできるのか
    - どのレベルで契約注釈の制御が行われるか、あるいはどのレベルでそれを制御できるかはContractsがどのように使用されるかに大きな影響を与えうる
- ソース内コントロール
    - それぞれの契約注釈ごとにそのセマンティクスを設定し、それがグローバル設定の影響を受けないようにする提案があった
    - そのようなアイデアは十分に成熟しているか？
    - 契約注釈のセマンティクスの制御をどの程度細かく行うべきか？
- コードの仮定に使用すること
    - チェックされていない契約条件をコードの仮定とすることが許可されていたが、これが当初の設計意図に合致しているかどうか？
        - すなわち、契約注釈が[`[[assume(expr)]]`](https://cpprefjp.github.io/lang/cpp23/portable_assumptions.html)の機能を含むことは妥当なのか？
    - チェックされない契約条件をコードの仮定とすることが合理的かどうか、またその制御とデフォルトはどうあるべきか？

これらの（相互に絡み合う）問題について合意を得ることができず、またその見通しも立たなかったためにC++20 Contractsは一旦取り下げられたわけです。最後のものはチェックされないはずの契約が破られた場合にプログラムが未定義動作に陥るため、特に紛糾したポイントだったようです。残りの上4つはよく似た事を言っており、これらの問題はざっと2つにまとめられます

1. C++ Contractsの単純さと応用可能性の問題
2. C++ Contractsの安全性の問題

この2つの問題はどちらかが相対的に影響が小さいものではなく、それぞれ単独でC++20のContractsを行き詰まらせるだけの影響があったようです。

とはいえこのような議論の紛糾はContractsそのものに対する反対ではなくその設計に反対するもので、Contractsそのものの有用性は認められていたため、Contractsの再設計を行う専門のStudy Group（SG21）を設立し、将来機能として引き続き議論していくことになりました。

SG21では上記のP2076も含めてC++ Contractsの機能や設計についての再調査を行い、C++23に向けたC++ Contractsとして上記のような紛糾した点の影響を受けない最小の範囲の機能をC++ ContractsのMVP(*Minimum Viable Product*)としてまとめ、まずこのMVPを最初のC++ Contractsとして導入することを目指すことにしました。上記の紛糾ポイントを含めた意見の相違がある機能や設計については時間をかけて議論してた上で将来的に導入していくことを目指します。

- [P1995R0 Contracts — Use Cases](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1995r0.html)
- [P2114R0 Minimal Contract Use Cases](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2114r0.html)
- [P2182R1 Contract Support: Defining the Minimum Viable Feature Set](https://wg21.link/p2182r1)

このMVPの考え方と方針は現在のC++ Contractsに関連する作業や議論の基礎となっています。

ただ、P2182R1の部分でさえもSG21での合意に至ることはできなかったようで、さらに機能を絞り込んだものが最初のMVPとして確立されました。

- [P2388R4 Abort-only contract support](https://wg21.link/p2388r4)

P2388の最初のMVPは主に次のようなものです

1. 事前条件 : `[[pre: condition]]`
2. 事後条件 : `[[post: condition]]`
3. アサーション : `[[assert: condition]]`
4. 2つのビルドモード
   - *No_eval* : コンパイラは契約の式の有効性だけを検証し、実行時に影響を与えない
   - *Eval_and_abort* : 全ての契約を実行時にチェックする。違反した場合契約違反ハンドラが呼び出され、その後`std::abort()`する
   - これらを翻訳単位ごとに切り替える実装が許可される
5. カスタマイズ不可能で`std::abort()`を呼ぶだけの違反ハンドラ

提案文書より、サンプルコード。

```cpp
int select(int i, int j)   // 最初の宣言
  [[pre: i >= 0]]
  [[pre: j >= 0]]
  [[post r: r >= 0]];
  
int select(int i, int j);  // 再宣言では、同じ契約を指定するか、何も指定しない
                          
int select(int i, int j)   // 定義
{
  [[assert: _state >= 0]];
  
  if (_state == 0) {
    return i;
  } else {
    return j;
  }
} 
```

ここではビルドモードは契約条件をチェックするかしないかの2つしかなく（継続モードはなく）、それはビルドモードによってグローバルにのみ制御可能で、チェックされない契約条件をプログラムの仮定として最適化に利用することは明示的に禁止されています。この段階では前述の争点を何も解決していませんが、後からそれを拡張することを意図しており、それが可能なようになっています。

逆にいうと、C++20のContracts仕様からこのP2388によるMVPを引いた部分が議論が紛糾したポイントであるといえます。P2388は本当に最小のもので、3種類の契約注釈の指定方法とそれがチェックされるかされないかのグローバルフラグのみからなります。

### C++26に向けたロードマップ

MVPに対する改善や設計検討はC++23サイクル中も行われていましたが、あまり活発ではありませんでした。そのためC++ ContractsはC++23には間に合いませんでした。

2022年11月、SG21よりC++26に向けたContracts MVP仕様の標準への導入のロードマップが示されました。

- [P2695R1 A proposed plan for contracts in C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2695r1.pdf)

これによると、次のようなスケジュールになっていました

|タイムライン|マイルストーン|やるべきこと|
|---|---|---|
|2022年11月（Kona）||契約注釈の副作用に関する議論|
|2023年2月（Issaquah）|C++26サイクルの開始|契約注釈の副作用に関する設計の決定|
|2023年6月（Varna）||違反ハンドラに関する設計の決定|
|2023年11月（Kona）||契約構文に関する設計の決定|
|2024年3月（Tokyo）||残った問題への対処。MVPを完成させEWGおよびLEWGへ転送する|
|2024年6月（St. Louis）||EWGにおけるMVPのレビュー|
|2024年11月?|C++26のための最後のEWGレビュー|MVPをEWGでの合意の下でCWGへ転送する|
|2025年2月?|C++26のための最後のCWGレビュー|CWGにおけるレビューを完了し、C++26WPヘマージ|
|2025年6月?|C++26 CD完了|未解決の設計/文言の問題解決|
|2025年11月?||NBコメントへの対応|
|2026年2月?|C++26 DIS完了|NBコメントへの対応|

このロードマップはSG21で合意され（僅かながら反対票がありましたが）、SG21はこのロードマップに沿ってC++26 Contractsの作業を進めていくことになりました。

そして、これを受けて2023年は非常に活発にContractsに関する議論が行われており、2023年中の関連提案がリビジョン改訂含めて74本も提出されています。これはC++20サイクルの終盤で議論が紛糾していた時よりもさらに多いです。

### MVPの改善

#### 非`const`引数の事後条件からの参照

### CCAのセマンティクス

- [P2570R0 On side effects in contract annotations](https://onihusube.hatenablog.com/entry/2022/07/09/160343)
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
- [P1995R0 Contracts — Use Cases](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1995r0.html)
- [P2695R1 A proposed plan for contracts in C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2695r1.pdf)
- [標準化会議 - C++ の歩き方 | cppmap](https://cppmap.github.io/standardization/meetings/)
