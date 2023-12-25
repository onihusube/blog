# ［C++］契約のこれまで、これから

[:contents]

### C++ Contracts

ContractとはContract programmingの略称で、C++ ContractsとはC++における契約プログラミング機能を指す言葉です（sは付いたり付かなかったりします）。

C++ Contractsとは、契約プログラミングという考え方に基づいた設計（契約による設計）をより自然に行えるようにするための言語機能です。契約プログラミングについてはあまり深入りしないので各自ググってください。

- [契約プログラミング - Wikipedia](https://ja.wikipedia.org/wiki/契約プログラミング)

契約による設計の中心概念には、関数の事前条件・事後条件とクラスの不変条件という3つのものがあります。C++ Contractsがまず導入しようとしているのは、前者の関数の事前条件・事後条件をコードとして記述しそれを実行時にチェックできるようにする機能です。

C++ Contractsは単に契約プログラミングの実現のためだけのものという訳ではなく、それを含めてさまざまなものが想定されています。例えば

- 契約プログラミング（契約による設計）を言語機能によって実現する
- 現在ドキュメントあるいはコメントに記載するしかない関数に対する契約の一部（事前条件・事後条件）をコードで記述する
    - そして、実行時にそれを検査することができる
- より高機能な実行時検査のための言語機能
    - 特に、関数呼び出しの境界においての実行時検査方法の提供
    - デバッグ時はもちろんとして、リリースバイナリにおいても有用な実行時検査方法の提供
- 実行時検査の違反時のより効果的なハンドリング
    - 実行時のプログラム状態チェックが失敗した場合に、より高度なログ出力や安全なシャットダウンなどを可能にする
- ユニットテストのための基盤機能としての利用
- ツールに対するプログラマの知識の伝達手段
    - IDE（入力支援など）が契約注釈に基づいたコード補完やサジェストを行う
    - 静的解析ツールが契約注釈を読み取り解析に役立てる
    - サニタイザーが契約注釈を読み取り実行時検査に使用する
    - 形式検証を可能にするようなアノテーション拡張（将来？）

などです。もちろん、ここに記載されていないものや、実際に利用可能になってから開けるユースケースもあるでしょう。いずれにせよ、C++ ContractsはC++コードをさらに安全に記述する事に確実に貢献する機能です。

これらのユースケースの実現には単に事前条件・事後条件を記述できるようにするだけでは足りず、その周辺の諸機能が必要となることが想像できると思います。それらを含めたC++ Contractsは単純な言語機能ではなく、実装され実使用される場合の事を考慮して設計されなければなりません。そのため、その議論はかなり難しく時間を要するものになっています。

### C++20 Contracts

C++ ContractsはC++20に対してP0542で提案され、2018年6月に一旦C++20ドラフトにマージされました。

- [P0542R5 Support for contract based programming in C++](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0542r5.html)

この提案自体もどうやら2013年頃から継続された議論の一つの集大成であったようです。あまり踏み込まないので詳しくは当時書かれた別の記事をご覧ください

- [C++20 Contract #C++ - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)
- [契約に基づくプログラミング - cpprefjp](https://cpprefjp.github.io/lang/future/contract-based_programming.html)

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

### 問題点とMVP(Minimum Viable Product)

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

- [P2388R4 Minimum Contract Support: either No_eval or Eval_and_abort](https://wg21.link/p2388r4)

P2388による最初のMVPは主に次のようなものです

1. 事前条件 : `[[pre: condition]]`
2. 事後条件 : `[[post: condition]]`
3. アサーション : `[[assert: condition]]`
4. 2つのビルドモード
   - *No eval* : コンパイラは契約の式の有効性だけを検証し、実行時に影響を与えない
   - *Eval and abort* : 全ての契約を実行時にチェックする。違反した場合契約違反ハンドラが呼び出され、その後`std::abort()`する
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

### 最初のMVP仕様

P2388がMVPとしての地位を確立した後、P2521で改めてMVPの仕様がまとめられました。

- [P2521R3 Contract support -- Record of SG21 consensus](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2521r3.html)

このMVPの仕様においては契約注釈の構文は未決定なためプレースホルダの構文を使用しています。ただし、この記事では以降属性構文を基本として使用することにします。

このMVP仕様に対しては、ロードマップ策定の前後までの間にいくつかの未解決の問題の解決が図られています。その中でも大き目なものをいくつかピックアップします。

#### 関数の再宣言と契約注釈

C++における関数宣言は定義が一つだけである必要があるものの、単なる宣言は何度でも行うことができます。その際問題となるのは、宣言ごとに契約注釈が異なっている場合にどの契約注釈が最終的なその関数に対する契約注釈となるのか？という事です。

```cpp
/// header.hpp

int select(int i, int j)  // 最初の宣言
  [[pre: i >= 0]];

/// implemetation.cpp

int select(int i, int j)  // 再宣言であり定義
  [[pre: j >= 0]]
  [[post r: r >= 0]]; 
```

変な例を考えれば、いくつも再宣言を行いそれぞれに異なる契約注釈を与えるような例なども容易に想像ができます。

MVP仕様においては、契約注釈は関数の最初の宣言にのみ行うことができ、再宣言に対してなされている場合はill-formed（コンパイルエラー）とされています。

```cpp
/// header.hpp

int select(int i, int j)    // ok、最初の宣言
  [[pre: i >= 0]];


int select2(int i, int j);  // ok、最初の宣言

/// implemetation.cpp

int select(int i, int j)  // ng、再宣言に契約注釈を行えない
  [[pre: j >= 0]]
  [[post r: r >= 0]];

int select2(int i, int j)   // ng、再宣言に契約注釈を行えない
  [[pre: i >= 0]]
  [[pre: j >= 0]]
  [[post r: r >= 0]];
```

正しい記述は次のようになります

```cpp
/// header.hpp

int select(int i, int j)  // ok、最初の宣言
  [[pre: i >= 0]]
  [[pre: j >= 0]]
  [[post r: r >= 0]];

/// implemetation.cpp

int select(int i, int j); // ok、再宣言であり定義
```

これは、ヘッダファイルに関数の宣言だけを記述し別のソースファイルでその定義を提供するプログラムやライブラリでの使用時に最も自然な形になります。すなわち、関数契約をコード化した契約注釈は常に利用者側に公開されなければならないということを反映しています。

#### 非`const`引数の事後条件からの参照

事後条件においては関数の戻り値だけではなく関数引数を参照することができます。その際、関数引数のどの時点の状態を取得するかによって条件の意味が変わってしまう場合があります。

```cpp
// ユーザーが見る宣言
int generate(int lo, int hi)
  [[pre lo <= hi]]
  [[post r: lo <= r && r <= hi]];

// 開発者が見る定義
int generate(int lo, int hi) {
  int result = lo;
  while (++lo <= hi) // loが更新される
  {
    if (further())
      ++result;      // loよりもゆっくりとインクリメントされる
  }
  return result;
}
```

この`generate()`関数では、事後条件として`lo <= r`（`r`は戻り値）であることが表示されています。しかしその定義を見てみると、`lo`は関数中でその値が変更されています。このため、確かに`generate()`の戻り値の値は`generate()`を呼び出した時点の`lo`以上になるのですが、一方で関数終了時点の`lo`よりは小さくなります。

このように、関数引数がその実装内部で変更できることによってユーザーが見る条件と実装者が見る条件の解釈が異なる場合がいあり得てしまいます。

また、暗黙ムーブによって事後条件がムーブ後オブジェクトを参照する可能性もあります。

```cpp
// ユーザーが見る宣言
string forward(string str)
  [[post r: r == str]];

// 開発者が見る定義
string forward(string str) {
  // ...
  return str; // 暗黙ムーブが行われる
}             // UB、事後条件はムーブ後オブジェクトを読み取る
```

契約注釈は実装者からユーザーに向けての関数契約をコードであらわしたものであり、それを読み取るのはユーザーです。ユーザーは関数宣言の契約注釈を見た場合、そこで使用されている仮引数名の値は自分が渡した値に一致すると思って見るのが一般的な見方だと思われます。そしておそらく、契約注釈を読み取るツールも同様の見方をするでしょう。そのため契約注釈の条件の意味はユーザー目線で自然であることがあるべき姿です。

また、これらの問題は関数の引数が非参照（参照型変数は変更されうることが明確かつ暗黙ムーブ対象外）かつ非`const`（`const`引数であれば変更されないことが明確）の場合にのみ問題となります。そのため、MVPでは事後条件で関数引数を使用する場合、その引数が参照型であるか`const`でなければならず、そうでない場合はill-formed（コンパイルエラー）としています。

```cpp
// これはダメ
int generate(int lo, int hi)
  [[pre lo <= hi]]
  [[post r: lo <= r && r <= hi]]; // ng、loもhiもconstでも参照でもない

// こう書く
int generate(const int lo, const int hi)
  [[pre lo <= hi]]
  [[post r: lo <= r && r <= hi]]; // ok、loもhiもconst
```

#### 契約条件式の副作用

C++のほとんどの式はあらゆる副作用を含む可能性があり、それは契約注釈の条件式も例外ではありません。また、関数が副作用を含んでいるかどうかを判定することは困難であるため、副作用を含む関数の排除を徹底することもできません。

C++ Contractsは安全なコードの記述を促進するための機能であるため、契約条件式からの副作用というものは望ましいものではありません。そのため、当初の論調では契約注釈内の副作用は禁止する雰囲気でしたが、それは困難なため何とか制限しようと試みられていました。

- [P2388R4 Minimum Contract Support: either No_eval or Eval_and_abort](https://wg21.link/p2388r4)
    - 契約条件式の副作用を部分的に削除することを許可 
- [P2570R0 On side effects in contract annotations](https://onihusube.hatenablog.com/entry/2022/07/09/160343#P2570R0-On-side-effects-in-contract-annotations)
    - 副作用が無いことが分かる関数のみ使用可能とする
    - ビルドモードによって副作用の評価が異なるモデルを採用する
    - 条件式を複数回評価する
- [P2680R1 Contracts for C++: Prioritizing Safety](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2680r1.pdf)
    - 定数式における`constexpr`関数のように。その評価の内側に収まる限り副作用を許可する
- [P2712R0 Classification of Contract-Checking Predicates](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2712r0.pdf)
    - 契約条件式内専用の言語サブセットを作成しないことを推奨
    - 副作用は許容するがそのような条件式を書かないように教育する
- [P2756R0 Proposal of Simple Contract Side Effect Semantics](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2756r0.pdf)
    - 契約条件式の扱いを他のC++コードと全く同じにする

MVP仕様では、契約条件式の副作用を禁止していません。ただし、契約条件式はビルドモード等によって0回以上評価される可能性がある（評価回数が不定）とすることで、プログラマが契約条件式の副作用に依存することを回避しようとしています。


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

このロードマップはSG21で合意され（僅かながら反対票がありましたが）、SG21はこのロードマップに沿ってC++26 Contractsの作業を進めていくことになりました。この作業にあたっては、P2521（当時はR2~R3）でまとめられていたMVP仕様が作業ベースとなります。

そして、これを受けて2023年は非常に活発にContractsに関する議論が行われており、2023年中の関連提案がリビジョン改訂含めて74本も提出されています。これはC++20サイクルの終盤で議論が紛糾していた時よりもさらに多いです。

### 契約注釈のセマンティクス

契約注釈のセマンティクスとは契約注釈のC++コード上で持つ意味のことで、特に契約条件がどう評価されるのか、評価された時何が起こるのかなどを指定するものです。条件式の副作用の扱いもセマンティクスの一部であり、MVPにおける契約注釈のセマンティクスのほとんどの部分はビルドモードによって一律的に制御されていました。

とはいえ細かいところまですべてが決まっていたわけではなく、例えば契約条件の評価に伴って例外がスローされたときにどうなるのか、あるいは未定義動作が発生したらどうなるのか、などが未決定でした。

そのためまず、ビルドモードによって大まかに指定される契約注釈のセマンティクスの細かい部分についてP2751が提案するセマンティクスが採用されました

- [P2751R1 Evaluation of Checked Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2751r1.pdf)

これは次のようなものです

1. 契約条件式は文脈的に`bool`変換可能な式であり、評価する際は式の評価に関するC++の通常のルールに従う
2. 契約条件式の評価が完了し、その結果が`true`では無い時、契約違反が発生している
    1. 契約条件式の評価結果が`true`となる場合は契約違反を意味せず、それ以上のアクションは発生しない
    2. 契約条件式の評価結果が`false`となる場合は契約違反が発生している
    3. 契約条件式の評価時に例外が投げられる場合は契約違反が発生している
        - 契約条件式評価時に例外が伝播することを許可すると、`noexcept`が付加されている関数が契約注釈をもつ場合、その関数評価を含むような式を渡した`noexcept`演算子は何を返すべきか？
    4. 契約条件式がUBを含む場合、欠陥が発生する
        - UBによるタイムトラベル（制御フローパスの破棄）が契約条件内で発生する場合、違反ハンドラの呼び出しに置き換えることを意図している
    5. 正常に評価されないその他の契約条件式は通常通りに動作する
        - `[[noreturn]]`関数からの`return`や`longjmp`等、病的と思われるものであっても式の評価に関するC++の通常のルールに従う
3. 契約条件が評価される回数は未規定。違反の検出のために0回以上、違反の処理のために1回以上評価されうる
    1. 契約条件を1回だけ評価することは許可される
    2. 契約条件を0回だけ評価することは許可される
        - 条件式に副作用がない場合、その評価をスキップすることが許可される
        - コンパイラが同じ違反を検出する同等の式を識別できる場合、その代替式の評価で条件式を置き換えることができる（as-ifルールに基づく）
    3. 契約条件を複数回評価することは許可される
    4. 複数の契約条件が連続して評価される場合、それらは相互に並べ替えて評価される可能性がある
        - 並べ替えられた契約条件の評価は、0ではない回数評価される可能性がある

当初のMVP同様に、契約条件式内での副作用を許容しつつ（副作用を禁止するようなサブセットを生み出さず）条件式の評価回数を不定とすることで副作用に依存できないようにしています。この提案で特に明確にされたのは2つ目の契約条件式が評価された場合の振る舞いについてです。

ただしこのセマンティクスにも未決定な部分があり、それは2-3の条件式から例外が送出される場合についてです。この契約注釈からの例外送出に関してはセマンティクスのより根本の部分にかかわる問題があり、契約違反発生時に例外を送出するモードの必要性が望まれたことでその議論が本格化しました。

- [P2698R0 Unconditional termination is a serious problem](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2698r0.pdf)
    - 契約違反時に例外を投げる*Eval and throw*ビルドモードの提案
- [P2780R0 Caller-side precondition checking, and Eval_and_throw](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2780r0.html)
    - 契約条件（事前条件）のチェックが関数内部ではなく関数呼び出し側で行われるという動作モデルの提案
- [P2858R0 Noexcept vs contract violations](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2858r0.html)
    - *Eval and throw*モードの必要性に疑義を投げかける提案

問題というのはまず、`noexcept(true)`指定がなされている関数に対して契約注釈を行われているとき、その関数の`noexcept`性がどうなるのかについてです。

```cpp
// noexceptだが、事前条件違反が起こる
void fun() noexcept [[pre: false]];

constexpr bool mystery = noexcept(fun());  // この値は何になる？

using nothrow_callback_t = void(*)() noexcept;
nothrow_callback_t p = fun;                // コンパイルが通る？

void overload(void(*)());                  // #1
void overload(void(*)() noexcept);         // #2

overload(&fun);                            // どちらのオーバーロードが呼ばれる？
```

*Eval and throw*モードでは契約違反に伴って例外が送出されるため、その関数の呼び出し時のプログラム状態次第で`noexcept`関数から例外が送出されることになります。とすると、ビルドモードが*Eval and throw*の場合は契約注釈が行われている関数は全て例外が送出されうるため。そのような関数の`noexcept`演算子の結果は`false`となるべきでしょうか？

*Eval and throw*モードでなくとも、契約条件式にはC++の任意の式が指定可能であるため任意の例外が送出される可能性があります。それを考慮すると、契約注釈が行われている全ての関数について契約条件がチェックされる場合に同様の問題があります。

```cpp
void my_func(int i) [[pre: i >= 0]];
void your_func(int i) noexcept [[pre: i >= 0]];

int x; // Value is not used.
static_assert( false == noexcept(my_func(x)) );   // 常に成り立つ
static_assert( true == noexcept(your_func(x)) );  // 常に成り立つ？
```

この例の`your_func()`は、呼び出し側から見ると契約条件が評価される場合は常に例外を投げる可能性があります。従って、`noexcept`演算子は契約条件が評価されるビルドモードにおいて契約注釈が行われている関数に対して常に`false`を返さなければなりません。

```cpp
static_assert( true == noexcept(your_func(x)) );  // 契約条件をチェックしないビルドモードでは成り立つ
static_assert( false == noexcept(your_func(x)) ); // 契約条件をチェックするビルドモードでは成り立つ
```

`noexcept`演算子の振る舞いは契約のビルドモードによって変化してしまうわけです。しかし、これは現在`noexcept`演算子によってその動作を切り替えているコード（`std::vector`のムーブコンストラクタのようなコード）の動作をそのビルドモードに応じて静かに変更させることになりますが、それはおそらくバグというべき振る舞いでしょう。

これらの問題について、その解決や整理を試みる提案がいくつか提出され、C++26 Contractsに向けては次の提案によるセマンティクスが採用されました。

- [P2834R1 Semantic Stability Across Contract-Checking Build Modes](https://wg21.link/P2834R1)
- [P2877R0 Contract Build Modes and Semantics](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2877r0.pdf)
- [P2861R0 The Lakos Rule: Narrow Contracts And `noexcept` Are Inherently Incompatible](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2861r0.pdf)

これらによる契約注釈のセマンティクス変更は次のようになります

1. 契約注釈が評価される場合、その評価は*ignore*、*observe*、*enforce*のいずれかのセマンティクスを持つ
    - *ignore* : 契約注釈は各契約条件を評価しないため、契約違反を起こさない
        - 無視される契約注釈のオーバーヘッドはゼロであり、*ignore*セマンティクスを持つ契約注釈はODRを除いてコメントアウトされたのと同等になる
    - *observe* : 契約注釈は各契約条件を評価し、そのいずれかが`true`を返さない場合は契約違反処理プロセスが発生する
    - *enforce* : 契約注釈は各契約条件を評価し、そのいずれかが`true`を返さない場合は契約違反処理プロセスが発生する。契約違反処理プロセスの終了後、プログラムは実装定義の方法で終了する
2. 契約注釈の個々の評価において、それがどのようなセマンティクスを持つかは実装定義とする
    - プログラム内の全ての注釈が同じセマンティクスを持つように強制される場合がある
      - MVPの2つのビルドモードに対応する
    - 異なる評価で異なるセマンティクスを持つことにより、同じ関数の異なるインライン版で異なるセマンティクスをコンパイル時に選択することができ、それはODR違反ではなくなる
    - 実装は、その選択をどのように行うかを指定する仕組みがユーザーに公開されていれば、契約注釈のセマンティクスをコンパイル時・リンク時・実行時のいずれかのタイミングで選択できる
3. `noexcept`演算子をはじめとするコンパイル時のクエリについて、契約注釈以外のC++のコンパイル時セマンティクスが契約のビルドモードによって変化することはない
    - 契約がなされている関数においてその契約条件がコンパイルされwell-formedだったならば、`noexcept`演算子は全てのビルドモードで（すなわち契約が評価されるかどうかに関わらず）同じ動作をする

このセマンティクスの指定は契約機能全体のC++言語機能内での直交性を向上させており、ビルドモードが元々備えていたセマンティクスに*observe*を1つ追加するとともに、契約注釈の評価のセマンティクスを契約注釈全体からその個々のプロパティとすることで、契約注釈を持つ関数のコンパイル時プロパティが契約注釈のセマンティクスに依存しない（できない）ようにしています。

これによって、契約注釈がビルドモードに関わらず他の言語機能に影響を与えないようになり、翻訳単位間で契約注釈のセマンティクスが混合していることも許可されます。すなわち、関数の`noexcept`指定は契約注釈とは無関係に今まで通りの振る舞いとなり、契約注釈のセマンティクスは翻訳単位で異なっていることも、翻訳単位内の関数呼び出しごとに異なっていることも許可されます。ビルドモードはあくまで実装によって提供される契約注釈のセマンティクスを一律的に制御する方法（コンパイルオプション）にすぎなくなり、ビルドモードはこの3種類のセマンティクスの上に構築されるものであるため、あるビルドモードの性質が後から追加される別のビルドモードの性質に影響を与えないようになります。

P2877の提案単体では、実装はMVPの2つのビルドモードだけをサポートすることを選択でき、また、コンパイラはリンク時やコンパイル時、実行時で契約注釈のセマンティクスを選択できるようなビルドオプションを提供することもできるようにすることを意図していましたが、これに関しては違反ハンドラの役割の変更に伴ってさらに更新されます（後述）。

このセマンティクスの下では、`noexcept`指定されている関数の呼び出し時に、*Eval and throw*モードにおいて契約が破られるか単に契約条件から例外がスローされた場合の振る舞いは、従来の`noexcept`指定された関数から例外が送出された場合と同じになり、`std::terminate()`によってプログラムが終了されます。これは仕様の矛盾ではなく、Lakos Ruleに背いて契約がなされてしまっていることにより発生する結果です。

- [P2861R0 The Lakos Rule](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2861r0.pdf)
- [広い契約(Wide Contracts)とnoexcept指定 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20180127/p1)

Lakos Ruleに基づけば

- `noexcept`指定された関数の例外仕様と狭い契約は、本質的に互換性がなく、矛盾している
- つまり、何かしらの契約がなされている関数は狭い契約を持つ（引数等プログラム状態に関して事前条件を持つ）ため、`noexcept`指定されるべきではない

となり、`noexcept`指定された関数の契約注釈からの例外送出を特別扱いする必要は無いことが分かります。ただし、これを言語機能として強制すること（`noexcept`指定された関数への契約注釈はコンパイルエラーとすること）は、有効なユースケース（ネガティブテストやプログラマの仮定に基づく`noexcept`指定など）があるため回避されています。

結局例外仕様と契約注釈に関しては、`noexcept`指定されている関数に契約を付与することができ、`noexcept`関数ではその契約は評価及び破られた時にも例外を投げないとみなされます。もしその仮定が裏切られ、その契約が評価中に例外を投げるか、契約が満たされなかった時に例外を投げた場合、現在の`noexcept`関数から例外を投げた時と同様に`std::terminate()`を呼び出してプログラムを終了させます。

### 違反ハンドラ

C++ Contractsの方向性としては、契約違反時の振る舞いを違反ハンドラ（*violation handler*）によってユーザーがカスタマイズできるようにすることを最終的な方向性としています。しかし、C++20でもMVPでも、違反ハンドラは実装が定義する固定的なものでその動作は最小限なものでした（C++20では厳密には実装定義の方法で可能とされていたようです）。

違反ハンドラの想定されるユースケースは次のようなものでした

- 契約違反時の報告方法や形式のカスタマイズ
- 契約違反時のセマンティクス管理
    - 即終了する、例外を投げる、longjmpによる終了、無視して継続、など

カスタム違反ハンドラは特に、2つ目の契約違反時のセマンティクス制御をビルドモードとは無関係に行う方法でもあります。

MVPの違反ハンドラはシステムデフォルトのものから置き換えることはできず、その動作も特にログ出力などはせずにプログラムを終了させるだけです。とはいえこれは違反ハンドラのデフォルトの動作を最小限にすることで将来的なカスタマイズなどを妨げないようにするものであり、C++20でも議論の的になった部分について何かを規定することを避けるものです。

しかし、MVPの契約違反時の動作は終了するか契約条件を全くチェックしないかの2つしかなく、最低限のログ出力や*Eval and throw*モードの動機のように安全なシャットダウン等のために違反後の継続を行いたい需要がやはり存在しており、それを可能にしようとする議論が行われました。

- [P2784R0 Not halting the program after detected contract violation](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2784r0.html)
    - 標準ライブラリ関数によってC++プログラム中にコンポーネントと呼ばれる文脈を作り出し、契約違反時はそのコンポーネントのみを終了させることでプログラムを継続させる
- [P2811R7 Contract-Violation Handlers](https://wg21.link/P2811R7)
    - 契約違反ハンドラのカスタマイズを許可し、違反ハンドラによって契約違反時セマンティクスを制御する
- [P2838R0 Unconditional contract violation handling of any kind is a serious problem](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2838r0.html)
    - 違反ハンドラのカスタマイズによってビルドモードの動作を実現する
- [P2852R0 Contract violation handling semantics for the contracts MVP](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2852r0.html)
    - P2811の下で、違反ハンドラのデフォルト動作と違反時セマンティクスを指定する
- [P2853R0 Proposal of std::contract_violation](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2853r0.pdf)
    - P2811を修正する形の違反ハンドラの提案

議論の結果、C++26 Contractsに対してはP2811（とP2838）を採用する形で違反ハンドラのユーザーによるカスタマイズを許可することになりました。

- [2023-06 Varna ISO C++ Committee Trip Report — First Official C++26 meeting! : r/cpp](https://www.reddit.com/r/cpp/comments/14h4ono/202306_varna_iso_c_committee_trip_report_first/?rdt=63459)

採用されたP2811の違反ハンドラ周りは次のように標準ライブラリの一部として指定されます

```cpp
// <contract> ヘッダで定義
namespace std::contracts {

  enum class detection_mode : int {
    predicate_false = 1,
    evaluation_exception  = 2,
    evaluation_undefined_behavior = 3
    // 将来の標準によって追加されうる
    // また、実装定義の値を許可する。実装定義の値は1000以上
  };

  enum class contract_semantic : /int {
    enforce = 1
    // 将来の標準によって追加されうる、例えば以下のもの
    // observe = 2,
    // assume = 3,
    // ignore = 4
    // また、実装定義の値を許可する。実装定義の値は1000以上
  };

  enum class contract_kind : int {
    pre = 1,
    post = 2,
    assert = 3
  };

  class contract_violation {
  public:
    // 仮想関数かどうかは実装定義
    /*virtual*/ ~contract_violation();

    // コピー（及びムーブ）禁止
    contract_violation(const contract_violation&) = delete;
    contract_violation& operator=(const contract_violation&) = delete;

    // 破られた契約の条件式のテキスト表現 
    const char* comment() const noexcept;

    // 契約違反の起こり方
    detection_mode detection_mode() const noexcept;

    // 違反ハンドラが正常にリターンした時、その直後の評価を継続することが期待されているかを返す
    // 現在はfalseを返す（違反後継続モードはまだ組み込まれていない）
    bool will_continue() const noexcept;

    // 破られた契約の種別
    contract_kind kind() const noexcept;

    // 違反を起こした場所の情報
    source_location location() const noexcept;

    // ビルドモードに関する情報
    contract_semantic semantic() const noexcept;
  };

  // デフォルトの違反ハンドラ
  // 受け取ったcontract_violationオブジェクトのプロパティを出力する
  void invoke_default_contract_violation_handler(const contract_violation&);
}

// 置換可能、noxeceptや[[noreturn]]であってもいい
void handle_contract_violation(const std::contracts::contract_violation&);
```

そして、契約条件式のチェックに伴って例外がスローされた場合の振る舞いを次のように変更します

- 事前条件/事後条件の評価中に発生した例外は関数本体内で発生したものとして扱われる
- 契約条件式の評価から送出される例外は契約違反ハンドラを呼び出す
    - この例外を呼び出し元に伝播したい場合、それを行うカスタムハンドラを定義できる
- 例外は、契約違反ハンドラの呼び出し中にスローされる可能性がある
    - このような例外はすべて、対応する契約条件式の評価中にスローされる例外と同じようにスタック巻き戻しを実行する

すなわち、関数に対する契約注釈は全て、その関数が呼び出す他の関数の評価に伴うものと同様に、現在のC++の例外伝播と`noexcept`ルールに従います。これは、無条件`noexcept`指定を行う関数に対する基準であるLakos Ruleに従うものでもあります。

契約注釈のセマンティクスは実装定義かつ契約注釈ごとに異なる可能性があり、契約違反が発生した場合のセマンティクスは違反ハンドラによって指定されます。したがって、契約違反時にどういう振る舞いをするのかについては違反ハンドラのカスタマイズによって制御されるため、それを指定するビルドモードは不要になり、契約条件式を一切チェックしないビルドモードも標準として区別する必要はなくなります（契約注釈が*ignore*セマンティクスを持つかどうかは実装定義であるため）。

結果、前節のセマンティクスの変更と合わせて標準としてはビルドモードという概念が不必要となったため、MVP仕様からはビルドモードという概念は削除されました。ただし、ユーザー目線でビルドモードというものが無くなったわけではなく、おそらくそれはコンパイラオプションという形で現れることになるでしょう。

たとえば、*Eval and abort*モードは次のように実装でき

```cpp
[[noreturn]]
void ::handle_contract_violation(const std::contracts::contract_violation&) {
  std::abort();
}
```

*Eval and throw*モードの実装はたとえば次のようになります

```cpp
[[noreturn]]
void ::handle_contract_violation(const std::contracts::contract_violation& violation) noexcept(false) {
  if (violation.detection_mode() == detection_mode::evaluation_exception) {
    throw; // 例外を伝播させる
  } else {
    throw std::runtime_error{"error message"};
  }
}
```

*No eval*モードに関しては違反ハンドラのカスタマイズでエミュレーションはできても*ignore*セマンティクスを達成できないため、実装定義の方法（コンパイルオプション）によって一律的に契約注釈のセマンティクスを*ignore*に設定することで行われるはずです。

そして、契約注釈のセマンティクスは実装定義かつ実行時に指定可能となり、違反ハンドラはリンク時に差し替えるものとなったため、契約注釈のセマンティクスの殆どの部分は必ずしもビルド時点で固定されなくなりました。これによって、ビルド済バイナリによるライブラリ配布時などに、そのライブラリ内部の契約注釈に関してセマンティクスの指定や違反ハンドラのカスタマイズなどが利用者側で事後的に行えるようになります。

### 構文

C++20 Contractsでは契約注釈のための構文として属性（っぽい）構文を採用していました。C++20で議論が紛糾したポイントにこの構文は含まれていなかったのですが、MVP仕様では構文に関しても未決定としてプレースホルダなものを当てていました。しかし、C++20以降のContracts関連の提案では主として属性構文が使用されていました。

- [P2935R4 An Attribute-Like Syntax for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2935r4.pdf)

```cpp
// 属性like構文の例
int select(int i, int j)
  [[pre: i >= 0]]
  [[pre: j >= 0]]
  [[post r: r >= 0]]
{
  [[assert: _state >= 0]];

  if (_state == 0)
    return i;
  else
    return j;
}

int pre;    // ok
int assert; // ok
int post;   // ok
```

MVPに対する構文の提案としては属性構文の他にも、ラムダ式のような構文を提案するもの

- [P2461R1 Closure-based Syntax for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2461r1.pdf)

```cpp
// ラムダ式like構文の例
int select(int i, int j)
  pre{i >= 0}
  pre{j >= 0}
  post(r){r >= 0}
{
  assert{_state >= 0};

  if (_state == 0)
    return i;
  else
    return j;
}

int pre;    // ok
int assert; // ???
int post;   // ok
```

新しいキーワードとともに専用の領域を導入する条件中心と呼ばれるもの

- [P2737R0 Proposal of Condition-centric Contracts Syntax](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2737r0.pdf)

```cpp
// 条件中心構文の例
int select(int i, int j)
  precond(i >= 0)
  precond(j >= 0)
  postcond(result >= 0)
{
  incond(_state >= 0);

  if (_state == 0)
    return i;
  else
    return j;
}

int precond;  // ng
int incond;   // ng
int postcond; // ng
```

文脈依存のキーワードによる専用の領域を導入する自然な構文と呼ばれるもの

- [P2961R2 A natural syntax for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2961r2.pdf)

```cpp
// 自然な構文の例
int select(int i, int j)
  pre(i >= 0)
  pre(j >= 0)
  post(result : result >= 0)
{
  contract_assert(_state >= 0);

  if (_state == 0)
    return i;
  else
    return j;
}

int pre;  // ok
int post;  // ok
int contract_assert; // ng
```

の4つの構文候補が提案されていました。

ロードマップに従って2023年11月の全体会議で構文を決定することになりましたが、その時点でP2737の条件中心構文は新しいキーワードの導入などが忌避されかつ更新が無く、P2461のラムダlike構文はP2961の自然な構文をその後継として認めていたため取り下げられており、実質的に当初の属性構文と自然な構文との二者択一となりました。

構文選択のためにP2885R3にて契約注釈のための構文に求められる要件がまとめれその比較基準が示されました

- [P2885R3 Requirements for a Contracts syntax](https://wg21.link/p2885r3)

より正確には、P2961の自然な構文は最後発の構文であり、属性構文の欠点を解消しラムダlikeと条件中心構文の利点を取り入れたうえで、この要件をなるべく満たすように考慮して設計され提案された構文案でした。

P2885に基づいて2つの構文が比較検討された結果、2023年11月のKona会議においてC++ Contractsの構文としてはP2961の自然な構文が採用されました。

- [2023-11 Kona ISO C++ Committee Trip Report — Second C++26 meeting!🌴 : r/cpp](https://www.reddit.com/r/cpp/comments/17vnfqq/202311_kona_iso_c_committee_trip_report_second/)
- [P3028R0 An Overview of Syntax Choices for Contracts](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p3028r0.pdf)

議論の過程などは公開されていないためどういう判断基準で決定されたかはわかりませんが、2つの構文の詳細な比較検討はP3028に見ることができます。

P2961では属性構文の欠点として次のような点が挙げられていました

1. 契約注釈の区切りのトークン`[[ ... ]]`が構文として重い
    - 一部のユーザーからは醜いと認識されている
2. 契約構文は属性と同様の記法を利用するが属性ではないため、混乱が生じる
    - 契約構文は違反ハンドラを通じるなどして、関数から新しいコードパスを作成できるが、標準属性はこのようなことを行うように設計されていない
3. 契約注釈を置ける構文上の位置は関数宣言の自然な読み取り順序に反している
    - 属性の置ける位置を再利用するため、後置戻り値の前（`override`や`requires`節の前）に事前条件と事後条件がくる
4. `assert`は式ではないため、Cの`assert`の完全な代替となり得ない
5. 3と4を属性構文のまま解決しようとすると、属性構文の利点が失われる
    - 現在それらが可能なように標準属性はできていない、そのため実装経験もない
6. 属性構文では、その内部の述語の前に`:`がくる場合に、それより前の内容に区切りを導入しない
    - 視覚的な情報の区別（契約種別や戻り値の名前、ラベルなどの見分け）が難しくなり、将来的に構文解析の曖昧さを生じさせる
7. 契約注釈自体に属性を付加する場合、属性内の属性という文法を導入させなければならない

そして、P2961は既存の構文が満たしていない部分を満足することを設計ゴールとし、次のような目標を掲げていました

- 構文は既存のC++に自然に馴染む。
    - 契約機能に慣れていないユーザーでも混乱を招くことなく直感的に理解できるものである必要がある
- 契約注釈構文は、属性やラムダ式など既存のC++の構成要素に似ていてはならない
    - ぱっと見で認識可能な独自の設計空間に置かれているべき
- 構文はエレガントかつ軽量である
    - 必要以上にトークンや文字を使用するべきではない
- 読みやすくするために、一次情報とニ次情報を構文的に分離する
    - 一次情報（条件種別、契約条件式、戻り値名、キャプチャなど）をそれ以外のニ次情報（ラベルなど）よりも視覚的に強調する

P3028R0より、P2961の自然な構文による契約注釈の例

```cpp
// フリー関数に対する契約注釈
template <typename T>
auto f() noexcept -> int requires something<T> pre( true );

// 配列ポインタを返す関数に対する契約注釈
int (*g(char i))[17] pre( true );

// 事後条件における戻り値参照と戻り値型
auto f() -> int post( r : r > 0 );

// 事後条件と属性
auto f()
  [[ function_type_attribute1 ]]
  [[ function_type_attribute2 ]]
  -> int
  [[ return_type_attribute1 ]]
  pre( 1 || true )
  pre( 2 || true )


// メンバ関数に対する契約注釈
struct S {

  // デフォルト宣言への注釈（C++29以降）
  bool operator=(const S&) pre( true ) = default;

  template <typename T>
  auto f() const&& -> int requires something<T>
    pre( true )
    post( r : true )
  {
    return 17; 
  }
};

// メンバ初期化子でのアサーション
struct S {
  int d_x;
  
  S : d_x( contract_assert( true ) , 17 ) {}
};

// ラムダ式
auto x = [] (int a) -> int pre( true ) { return 17; };
auto y = [] -> int pre( true ) { return 17; };

// ラムダ式 + requires節
auto x = [](auto a) requires something<decltype(a)>
  pre( true ) { ... };
```

### C++26に向けて、残りの問題

契約注釈のセマンティクスに契約構文というとても大きな問題がP2695R1のロードマップ通りのスケジュールで解決を見たことで、C++26 ContractsのSG21における作業完了は俄然現実味を帯びてきました。

とはいえまだC++26に間に合わせるにあたってのすべての問題が解決したわけではありません。細かいながらも決定を必要とする問題がいくつか残っています。

- [P2896R0 Outstanding design questions for the Contracts MVP](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2896r0.pdf)

P2896でまとめて提示されている残りの設計上の問題は次のものです

1. 異なる翻訳単位の最初の宣言における契約について
    - 現在のMVPでは、`f`が異なる翻訳単位で宣言されている場合、その契約は同一（*identical*）でなけれならない（そうでない場合診断不用のill-formed）とされているが、同一（*identical*）の意味が定義されていない。この定義が必要
    - 選択肢
      1. 同一（*identical*）の意味を定義し、これが実装可能であることを確認する
      2. 異なる翻訳単位の同じ関数の2つの宣言について、両方に契約がなされている場合をill-formed（診断不用）として問題を回避する。ただしこれは実用的ではない
2. オーバーライドする関数とされる関数の契約について
    - 現在のMVPでは、オーバーライドする関数はされる関数の契約を継承し、追加の契約を行えない。これについて異論があり、どうするかを選択する必要がある。
    - 選択肢
      1. なにもしない（現在のMVPのまま）
      2. MVPの制限を強め、オーバーライドする関数もされる関数も契約を行えないようにする
      3. 継承された契約をオーバーライドする機能などの仮想関数に対するより柔軟なソリューションを考案し、MVPを緩和する
3. ラムダ式に対する契約と暗黙キャプチャについて
    - 契約機能はラムダ式においても機能しなければならない。その際、ラムダの本体で使用されていないが契約指定で使用されている名前はキャプチャされるかどうか（契約に表れている名前がODR-usedであるかどうか）が未解決
    - 選択肢
      1. ラムダにおける契約は他の所と同じルールに従う。すなわち、契約条件式でのみ使用されている名前はキャプチャされる
          - P2890R0が提案している
      2. ill-formedとする。ラムダにおける契約条件式は、他の方法でキャプチャされない名前をキャプチャできない
          - P2834R1が提案している
      3. ラムダ式における契約機能を無効にする
4. コルーチンにおける契約
    - コルーチンに対する契約は通常の関数と同様に動作するのかが未解決
    - 選択肢
      1. コルーチンで事前・事後条件とアサーションを許可し、事前条件と事後条件のセマンティクスを指定する
          - P2957R0が提案し、セマンティクスについても提供している
      2. コルーチンではアサーションのみ許可する
      3. コルーチンでは契約機能は無効とする
5. 定数式における契約について
    - 定数評価中に契約条件は評価されるのか、どういうセマンティクスを持つのかが未解決。特に、契約条件式はコア定数式ではない場合と、契約条件式はコア定数式だが`false`に評価された場合にどうなるのかが問題。
    - 選択肢（2つの場合のどちらについても）
      1. ill-formed
      2. ill-formed、ただし診断不要
      3. 契約条件式は無視される（定数評価中のみ）
      4. 契約条件式は無視するが、警告を発することを推奨する
      5. いずれの場合も定数式における契約注釈のセマンティクスは実装定義とする
6. トリビアルな特殊メンバ関数に対する契約について
    - トリビアルな関数に契約がなされている場合、そのトリビアル性に影響するかどうかが未解決
    - 選択肢
      1. 契約が指定されていてもトリビアルのまま
      2. 契約が指定されていてもトリビアルのままだが、その結果として事前・事後条件がチェックされない可能性がある
          - P2834R1が提案している

これら問題に対する設計についてはそれぞれ既に提案が提出されています。

- [P2932R2 A Principled Approach to Open Design Questions for Contracts](https://wg21.link/p2932r2)
    - P2896で提示されている問題すべてに対する解決策を提案
- [P3066R0 Allow repeating contract annotations on non-first declarations](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p3066r0.pdf)
    - 1の問題に対する提案
    - 同じリストを持つ限り後の宣言での契約注釈を許可する
    - 契約注釈の同じリストの定義を提案している
- [P2954R0 Contracts and virtual functions for the Contracts MVP](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2954r0.html)
    - 2の問題に対する提案
    - 次のようにすることを提案
      - 関数をオーバーライドする仮想関数には契約指定を行えず、オーバーライドされる関数の契約指定を継承する
      - 関数が複数の関数をオーバーライドする場合、オーバーライドされる関数は契約指定を持ってはならない
- [P2890R2 Contracts on lambdas](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2890r2.pdf)
    - 3の問題に対する提案
    - 契約注釈で使用された名前は暗黙的にキャプチャされる
- [P2834R1 Semantic Stability Across Contract-Checking Build Modes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2834r1.pdf)
    - 3と6の問題に対する提案を含む
    - 契約注釈で使用された名前は暗黙的にキャプチャされない
    - トリビアルな関数の契約注釈は関数のトリビアル性に影響を与えない
      - そのような契約注釈は評価されない（*ignore*セマンティクスを持つ）可能性がある
- [P2957R0 Contracts and coroutines](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2957r0.html)
    - 4の問題に対する提案
    - コルーチンでも契約注釈を使用可能にするためのセマンティクスを提案
- [P2894R1 Constant evaluation of Contracts](https://wg21.link/p2894r1)
    - 5の問題に対する提案
    - 定数式における契約チェックを許可し、そのセマンティクスは実装定義とする

ただし、このうち一部のものについては2023年11月の会議で解決が採択されています。

- [2023-11 Kona ISO C++ Committee Trip Report — Second C++26 meeting!🌴 : r/cpp](https://www.reddit.com/r/cpp/comments/17vnfqq/202311_kona_iso_c_committee_trip_report_second/)

4と6についてはC++26に向けた設計が決定されており、それぞれ次のようになりました

- コルーチンにおける契約
    - コルーチンに対しては事前条件と事後条件を指定できない（コンパイルエラー）
    - アサーション（`contract_assert`）は使用可能
- トリビアルな特殊メンバ関数に対する契約について
    - 最初の宣言で`default`指定されている関数には契約注釈（事前条件/事後条件）を行えない（コンパイルエラー）

これらはどちらも契約注釈の存在をコンパイルエラーとしており、これが最終的に確定した仕様というわけではありません。MVPの当初の理念に基づいて、この問題の詳細な設計の確定は将来のバージョンで行い、C++26 Contractsに向けてはエラーとしておくことで将来の拡張を妨げないようにしています。

残りの問題については、来春3月末の東京における会議でその設計が決定される予定です。

### 2023年末時点でのMVP

これらの議論をすべて反映した現時点でのMVP仕様、すなわちC++26 Contracts仕様候補はP2900にまとめられています。この記事を執筆している時点ではR3が最新版です。

- [P2900R3 Contracts for C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2900r3.pdf)

順当にいけば、この提案がC++26 Contractsの提案文書としてC++26のワーキングドラフトにマージされることになるでしょう。ロードマップ通りならそれは2025年2月ごろになるはずで、来年の今頃にはC++26 Contracts仕様がほぼ固まりEWGのレビューを終えているはずです。

ただ1つ不安な点があるとすれば、契約注釈からの例外送出に伴うセマンティクスの問題で、`noexcept(contract_assert(...))`の結果がどうなるべきか？など一筋縄ではいきそうにない問題が提起されていることです。

- [P2969R0 Contract annotations are potentially-throwing](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2969r0.pdf)

この問題はどう決定しても禍根を残しそうで、このあたりの問題に関してはまた変更があるかもしれません。

### 参考文献

- [P1995R0 Contracts — Use Cases](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1995r0.html)
- [P2466R0 The notes on contract annotations](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2466r0.html)
- [P0542R5 Support for contract based programming in C++](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0542r5.html)
- [C++20 Contract - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)
- [契約に基づくプログラミング - cpprefjp](https://cpprefjp.github.io/lang/future/contract-based_programming.html)
- [C++20 Contract #C++ - Qiita](https://qiita.com/niina/items/440a44cd74ec4588cd15)
- [標準化会議 - C++ の歩き方 | cppmap](https://cppmap.github.io/standardization/meetings/)
- [2019-07 Cologne ISO C++ Committee Trip Report - reddit](https://www.reddit.com/r/cpp/comments/cfk9de/201907_cologne_iso_c_committee_trip_report_the/)
- [P1823R0 Remove Contracts from C++20](https://www.reddit.com/r/cpp/comments/cfk9de/201907_cologne_iso_c_committee_trip_report_the/)
- [P2755R0 A Bold Plan for a Complete Contracts Facility](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2755r0.pdf)
- [P2695R1 A proposed plan for contracts in C++](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2695r1.pdf)
- [P2817R0 The idea behind the contracts MVP](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2817r0.html)
- [P2829R0 Proposal of Contracts Supporting Const-On-Definition Style](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2829r0.pdf)
- [P2861R0 The Lakos Rule](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2861r0.pdf)
- [P2969R0 Contract annotations are potentially-throwing](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2969r0.pdf)
- [2023-06 Varna ISO C++ Committee Trip Report — First Official C++26 meeting! : r/cpp](https://www.reddit.com/r/cpp/comments/14h4ono/202306_varna_iso_c_committee_trip_report_first/?rdt=63459)
- [2023-11 Kona ISO C++ Committee Trip Report — Second C++26 meeting!🌴 : r/cpp](https://www.reddit.com/r/cpp/comments/17vnfqq/202311_kona_iso_c_committee_trip_report_second/)
