# ［C++］C++20モジュールの変遷 - Module TSからC++20DISまで

C++20のモジュールは確かにある一つの提案がベースになっているのですが、その後C++20策定完了までの間に複数の提案やIssue報告によってそこそこ大きく変化しています。その結果、C++20のモジュールはその全体像を把握するためにどれか一つの提案を読めばわかるものではなく、関連する提案を追うのもC++20のDIS（N4861）を読み解くのも辛いものがあり、ただでさえ難解な仕様を余計に分かりづらくしています。

この記事は、C++20の最初のモジュールの一歩手前から時系列に沿って、モジュールがどのように変化していったのかを眺めるものです。

[:contents]

### Working Draft, Extensions to C++ for Modules (Module TS)

- [N4720 Working Draft, Extensions to C++ for Modules](http://wg21.link/n4720)

Module TSと呼ばれているもので、最終的なC++20の仕様のベースとなっているものです。

意味論の細かい差異はあれど、現在書くことのできる基本的なモジュールの構文や仕様はここで決定されました。

### Another take on Modules (ATOM Proposal)

- [P0947R1 Another Take On Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0947r1.html)

この提案は、モジュールシステムを別の観点から見つめ直し、モジュールTSにあったいくつかの問題を修正しようとするものです。

TSからの変更点としては

- `export/module`の非キーワード化
- `module`宣言は翻訳単位の先頭になければならない
- モジュールパーティションの導入
- `private/public`な`import`
- マクロの`export`
- ヘッダユニット（*Legacy header units*と呼ばれていた）
    - ヘッダの`import`
    - `#include`の`import`への置換
- インスタンス化経路（*path of instantiation*）

これはあくまでモジュールTSをベースとしており、対案と言うよりはモジュールTSを補間し修正しようとする提案です。他の提案からは、ATOM Proposalと呼ばれます。

### Merging Modules (最初期のC++20モジュール)

- [P1103R3 Merging Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1103r3.pdf)

この提案はC++20に最初に導入されたモジュール仕様です。モジュールTS（N4720）にATOM提案（P0947R1）をマージする形でモジュールは導入されました。

ここで、新たに次のものが追加されました

- グローバルモジュールフラグメントの導入
    - 正確には、グローバルモジュールフラグメントは明示的に導入するものとなった（TSでは`#include`によるヘッダインクルードが実質的にグローバルモジュールフラグメントを導入していた）
- プライベートモジュールフラグメントの導入
- *semantic boundaries rule*の導入
    - 「（定義を持つものは）以前の定義が到達可能なところで再定義されてはならない」と言うルール
- ヘッダユニットからのマクロの定義位置
    - `import`宣言の直後と規定

また、次のものは導入されませんでした

- モジュールTS
    - *Proclaimed ownership declaration*
- ATOM提案
    - `export/module`の非キーワード化
    - `private/public`な`import`
    - マクロの`export`

#### 参考資料

- [C++20 モジュールの概要 / Introduction to C++ modules (part 1)](https://www.slideshare.net/TetsuroMatsumura/c20-152189285)
- [C++ ModulesのHeader units - Qita](https://qiita.com/tetsurom/items/e25b2683cb7e7c0fa91c)

### Relaxing redefinition restrictions for re-exportation robustness

- [P1811R0 : Relaxing redefinition restrictions for re-exportation robustness](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1811r0.html)


当初のモジュールでは、従来の`#include`は可能ならすべてヘッダユニットの`import`に置き換えられていました。そして、ヘッダユニットの宣言はグローバルモジュールに属する宣言として扱われます。

またODR要件が緩和されており、以前の定義が到達可能でなければ定義は複数あってもいい、とされていました。ある場所から定義が到達可能というのは、その場所で直接見えている`import`宣言をたどっていった先で定義が見つかることで、この到達可能な定義の集合に同じ宣言に対する定義が複数含まれているとエラーとなります。

C++17以前と同様に、グローバルモジュール（非モジュール内）においては、その宣言が同一であれば異なる翻訳単位で定義が重複しても良い、というルールがあります。ただし、それらの定義がモジュールのインポートによって到達可能となってしまう場合は定義の重複は許されません。

```cpp
module;
#include "a.h" // struct A {};
export module M;

// b.hはインポート可能なヘッダ
export import "b.h"; // struct B {};

export A f();
```
```cpp
import M;
// AとBはともにこの場所から到達可能

#include "a.h" // error, Aの再定義
#include "b.h" // OK, b.hのインクルードはimportに変換され、Bの定義は再定義とならない
```

この時、`b.h`が次のようになっていると多重定義エラーが発生する可能性があります。 

```cpp
/// b-impl.h （インポート可能なヘッダではない
#ifndef B_IMPL_H
#define B_IMPL_H
struct B {};
#endif
```
```cpp
/// b.h （インポート可能なヘッダ
#include "b-impl.h"
```
```cpp
import M;
#include "b-impl.h" // error, Bの再定義
```

インポート可能なヘッダというのは実装定義であり、このようなエラーはコンパイラによって発生したりしなかったりするかもしれません。また、従来の`#include`であれば、このようなケースはODRの例外規定によって特別扱いされていたはずです。

このようなグローバルモジュールに属するエンティティの再エクスポート時の不可思議な振る舞いを避けるために、この提案によって次のように仕様が調整されました。

- グローバルモジュールに属するエンティティの定義は、定義が到達可能かどうかに関係なく、各翻訳単位で最大1つの定義の存在を許可する。
- 名前付きモジュールに属するエンティティに対するODRの例外規定の削除。
    - ODRの例外規定とは、定義が同一であれば複数の翻訳単位に現れてもいい、というルール。
    - テンプレートをヘッダに書いてコンパイルする際に実装を容易にするための特殊なルールだったが、モジュールの`import`は宣言をコピペしないのでモジュールでは不要。
- インポート可能なヘッダの`#include`は、`import`に置き換えても __よい__ という表現に変更
    - そもそも、インポート可能なヘッダを常に`import`していたのは、先程の`b.h`の最初の例のようなケースで再定義エラーが起こらないようにするため。この提案の変更によって前提となる問題が解決された。

```cpp
// この提案適用後では
import M;
#include "b-impl.h" // OK, Bの定義は到達可能だが、この翻訳単位では最初の定義
```

この提案によってグローバルモジュールにおけるODR周りの事はC++17までとほとんど同様となり、名前付きモジュール内でだけODR要件が厳しくなります。

- グローバルモジュール : 宣言に対する定義は各翻訳単位で唯一つであり、全ての定義は同一でなければならない
- 名前付きモジュール : 宣言に対する定義はプログラム内で唯一つでなければならない

どちらの場合でも、同じ翻訳単位内での多重定義はコンパイルエラーとなりますが、翻訳単位が分かれている場合にこのルールに違反していると必ずしもコンパイルエラーとはならず、未定義動作となります。

#### 参考資料

- [テンプレートの実体化の実装方法とODR違反について - 本の虫](https://cpplover.blogspot.com/2013/12/odr.html)

### Mitigating minor modules maladies

- [P1766R1 : Mitigating minor modules maladies](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1766r1.html)


この提案はモジュールによって問題となる、3つの特殊なケースのバグを修正するものです。

#### 1. `using/typedef`

※この問題はコンパイラの実装に大きくかかわる物で、今一よくわかりませんでしたので、結論のみを書いておきます・・・

この提案では、リンケージを与えるための`typedef`の対象となる構造体は次のものを含むことができないようにします。

- 非静的データメンバ・メンバ列挙型・メンバ型（入れ子クラス）を除くすべてのメンバ
- 基底クラス
- データメンバに対するデフォルト初期化子
- ラムダ式

この提案によって、リンケージを与えるための`typedef`はC言語互換のためだけの機能であることが明確となり、その対象となる構造体はC互換の構造体に限定されるようになります。また、`typedef/using`によって名前のリンケージを変更できないことが明確となります。

これはモジュールの内外を問わず適用されるため、破壊的変更となります。

#### 2. エクスポートブロック内での`static_assert`

モジュールにおける`export`宣言では、名前を導入しないタイプの宣言を`export`することができません。

```cpp
export static_assert(true); // error、エクスポートできない

export {
  struct Foo { /*...*/ };
  static_assert(std::is_trivially_copyable_v<Foo>); // error、エクスポートできない

  struct Bar { /*...*/ };

  template<typename T>
  struct X { T t; };

  template<typename T>
  X(T) -> X<T>;  // error、エクスポートできない

  // ...

#define STR(x) constexpr char x[] = #x;
  // セミコロン（;）が余計に一つ付くが、エクスポートできないのでエラー
  STR(foo);
  STR(bar);
#undef X
}
```

この提案では、このようなエクスポートブロックの内部でのみ、宣言が少なくとも1つの名前を導入しなければならない、というルールを削除します。

ただし、ブロックではない通常の`export`宣言においては名前を導入しない宣言をエクスポートできないのは変わりません。

#### 3. デフォルト引数の不一致

`inline`ではない関数では、デフォルト引数を翻訳単位ごとに異なるものとすることができます。また、テンプレートのデフォルトテンプレート引数も翻訳単位ごとに異なるものとすることができます。

```cpp
/// a.h
int f(int a = 123);
```
```cpp
/// b.h
int f(int a = 45);
```
```cpp
import A;     // a.hを間接的にインクルードしているが、エクスポートはしていない
import "b.h";

int n = f();  // ??
```

同じ宣言に対して異なるデフォルト引数が与えられた複数の宣言が同じ翻訳単位内で出現する場合はコンパイルエラーとなりますが、モジュールにおいては一方のみが名前探索で可視であるが、両方の宣言に到達可能となる場合があります。当初の仕様ではこの場合にどう振舞うかは未規定でした。

この提案では、異なる翻訳単位の同じ名前空間スコープの2つの宣言が、同じ関数引数に異なるデフォルト引数を、あるいは同じテンプレート引数に異なるデフォルトテンプレート引数を指定することをそれぞれ禁止します。ただし、異なるデフォルト引数を持つ複数の宣言が同時に到達可能とならない限り、コンパイルエラーとならない可能性があります。

この変更は、その宣言がモジュールにあるかどうかにかかわらず適用されます。つまり、これは破壊的変更となります。

### Recognizing Header Unit Imports Requires Full Preprocessing

- [P1703R1 : Recognizing Header Unit Imports Requires Full Preprocessing](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1703r1.html)

この提案は、依存関係スキャンを簡易化・高速化するために、ヘッダユニットのインポートを`#include`とほとんど同等に扱えるようにするものです。

当初のモジュールでは、`import`宣言はほとんどC++のコードとして解釈され、プリプロセス時にはヘッダユニットのインポートに対してマクロのエクスポートを行う以外のことをしていませんでした。そのため、ヘッダユニットのインポートを識別するには翻訳フェーズ4（プリプロセスの実行）を完了する必要がありました。

すなわち、`import`宣言はほとんどどこにでも現れる可能性があり、マクロ展開を完了しなければ`import`宣言を抽出することができません。

これは従来`#include`に対して行われていた依存関係スキャンに対して、実装が困難になるだけではなく、速度の面でも明らかに劣ることになります。例えば、`#include`に対する依存関係スキャンでは、プリプロセッシングディレクティブ以外の行は何もせず無視することができ、`#include`は1行で書く必要があるため行をまたぐような複雑なマクロ展開をしなくても良くなります。

この提案では、`(export) import`によって開始される行をプリプロセッシングディレクティブとして扱うようにします。それによって、`(export) import`をマクロ展開によって導入する事ができなくなり、`(export) import`は空白を除いて行の先頭に来ていなければならず、`import`宣言は1行で書かなければならなくなります。

プリプロセスの最初の段階ではモジュールのインポートもヘッダユニットのインポートもまとめて扱われ、その後ヘッダユニットのインポートに対してエクスポートされたマクロのインポートを行います。最後に、`import`トークンを実装定義の`import-keyword`に置き換えて、`import`ディレクティブのプリプロセスは終了します。

翻訳フェーズ5以降、つまりC++コードのコンパイル時には、このように導入された`import-keyword`によるものだけが`import`宣言として扱われるようになります。

なお、`(export) import`のトークンおよび`import`ディレクティブを終了する`;`と改行だけがマクロで導入できないだけで、`import`対象のヘッダ・モジュール名はマクロによって導入することができます。

この提案によって可能な記述は制限される事になります。



<table>
<tr>
<th>Before</th>
<th>After</th>
</tr>
<tr>
<td valign="top">

```cpp
int x; import <map>; int y;
```
</td>
<td valign="top">

```cpp
// importディレクティブは1行で独立
int x;
import <map>;
int y;
```
</pre>
</td>
</tr>
</table>
<table>
<tr>
<th>Before</th>
<th>After</th>
</tr>
<tr>
<td valign="top">

```cpp
import <map>; import <set>;
```
</td>
<td valign="top">

```cpp
// それぞれ1行づつ書く
import <map>;
import <set>;
```

</pre>
</td>
</tr>
</table>
<table>
<tr>
<th>Before</th>
<th>After</th>
</tr>
<tr>
<td valign="top">

```cpp
export
import
<map>;
```
</td>
<td valign="top">

```cpp
// importディレクティブは1行で完結する
export import <map>;
```

</pre>
</td>
</tr>
</table>
<table>
<tr>
<th>Before</th>
<th>After</th>
</tr>
<tr>
<td valign="top">

```cpp
#ifdef MAYBE_EXPORT
export
#endif
import <map>;
```

</td>
<td valign="top">

```cpp
// importディレクティブの一部だけを#ifで変更できない
#ifdef MAYBE_EXPORT
export import <map>;
#else
import <map>;
#endif
```

</pre>
</td>
</tr>
</table>
<table>
<tr>
<th>Before</th>
<th>After</th>
</tr>
<tr>
<td valign="top">

```cpp
#define MAYBE_EXPORT export
MAYBE_EXPORT import <map>;
```

</td>
<td valign="top">

```cpp
// (export) importはマクロによって導入できない
#define MAYBE_EXPORT
#ifdef MAYBE_EXPORT
export import <map>;
#else
import <map>;
#endif
```

</pre>
</td>
</tr>
</table>


この提案の内容はのちにP1857R3によって大幅に（より制限する方向に）拡張されることになります。

#### 参考資料

- [［C++］モジュールとプリプロセス - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/05/15/201112)

### Standard library header units for C++20

- [P1502R1 : Standard library header units for C++20](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1502r1.html)

この提案は、少なくとも標準ライブラリのヘッダはヘッダユニットとしてインポート可能であることを規定するものです。

C++20にモジュールが導入されるのは確定的で、そうなると標準ライブラリをモジュールとして提供する（できる）必要が生じます。この提案の時点ではその作業が間に合うかは不透明であり（実際間に合わなかった）、間に合わなかった場合は、それぞれのベンダーがそれぞれの（互換性のない）方法でモジュール化された標準ライブラリが提供され、C++エコシステムに分断をもたらす事になりかねません。

この提案では、既存の標準ライブラリをモジュールとして提供するための最低限のメカニズムを提供しつつ、将来的な標準ライブラリの完全なモジュール化を妨げる事が無いようにするものです。

そのために、__C++の__ 標準ヘッダは全てヘッダユニットとしてインポート可能であると規定し、標準ライブラリへのアクセス手段としての標準ヘッダのインポートを規定します。そして、モジュール単位（名前付きモジュール）の中での標準ライブラリヘッダの`#include`はグローバルモジュールフラグメントの中でのみ行える事が規定されました（診断は不要とあるので、これに従わなくてもコンパイルエラーとはならない可能性があります）。

なお、C互換の標準ヘッダ（`<cmath>, <cassert>`などの`<c~~~>`系のヘッダ）はインポート可能ではありません。これらのヘッダは事前のマクロ定義に大きく影響を受けますが、ヘッダユニットも含めたモジュールは外で定義されたマクロが内部に影響を及ぼさないため、インポータブルでは無いためです。

また同時に、`std`から始まる全てのモジュール名を将来の標準ライブラリモジュールのために予約します。

### NBコメントへの対応1

- [GB022 04.01Allow "import" for accessing standard library names](https://github.com/cplusplus/nbballot/issues/22)
    - [[intro.compliance] The standard library also offers header units. - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/3356)

このIssueは、規格文書中で標準ライブラリのエンティティ名にアクセスする手段を記述している所にヘッダユニットの`import`を加えるものです。P1502R1の内容を補強するもので、P1502R1ではおそらく見落とされていたものです。

- [FR039 06.05.2.4 Non-exported functions should not be visible via ADL after importing](https://github.com/cplusplus/nbballot/issues/38)
    - [[basic.lookup.argdep] Inline the definition of 'interface'. - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/3390)

このIssueは、モジュールのインターフェースという言葉を使用していたために、エクスポートしていない関数名がADLを介して表示されるかのように読めてしまっていた部分の表現を修正するものです。

意味するところはこの前後で変わらず、モジュールの内部にあるエクスポートされた宣言はテンプレートのインスタンス化経路上で可視となりますが、エクスポートされていない宣言はいかなる場合にも可視になりません。

- [GB 078 10.01 Harmonize "digits" referring to reserved namespace/module names](https://github.com/cplusplus/nbballot/issues/77)
    - [[namespace.future,diff.cpp14.library] Properly refer to grammar 'digit'](https://github.com/cplusplus/draft/pull/3345)

このIssueは、予約するモジュール名について名前空間の予約と記述を一貫させるものです。

意味するところは変わらず、`std`に数字が続く名前空間名、`std`から始まるモジュール名は全て予約されます。

- [US088 10.04 [module.global] Harmonize labels referring to the global module fragment](https://github.com/cplusplus/nbballot/issues/87)
    - [[module.global,cpp.glob.frag] Rename labels to ...global.frag.](https://github.com/cplusplus/draft/pull/3351)

このIssueは、グローバルモジュールフラグメントに関する箇所の規格参照用のラベルが[module.global]だったり[cpp.glob.frag]だったりしていたのを、[xxx.global.frag]に一貫させるものです。

- [GB089 10.06 [module.reach] Mark translation unit boundaries in example](https://github.com/cplusplus/nbballot/issues/88)
  - [[module.reach] Clearly separate translation units in example.](https://github.com/cplusplus/draft/pull/3331)

このIssueは、モジュールに関するサンプルコードで翻訳単位の境界が曖昧だった所を明確にするものです。

### Core Language Changes for NB Comments at the November, 2019 (Belfast) meeting

- [P1971R0 : Core Language Changes for NB Comments at the November, 2019 (Belfast) meeting](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1971r0.html)

この提案は2019年11月のベルファストの会議において採択されたコア言語のIssue解決（NBコメントについて）をまとめたものです。モジュールに関連するものは4件あります。

- [GB079 10.01 Add example for private-module-fragment](https://github.com/cplusplus/nbballot/issues/78)

これは、それまで規格としての記述のみで利用法が不明瞭だったプライベートモジュールフラグメントについて、サンプルコードを追加するものです。

- [US087 10.03 p9 Header unit imports cannot be cyclic, either](https://github.com/cplusplus/nbballot/issues/86)

これは、ヘッダユニットのインポートが再起して巡回する事が無いことを明確に記述するものです。

それまで、モジュールのインポートはインターフェース依存関係という言葉を用いて巡回インポートが禁止されていましたが、ヘッダユニットについては特に規定がありませんでした。

ここでは、インターフェース依存関係の対象にヘッダユニットを含めることで、モジュールと同様に巡回インポートを禁止します。あらゆる巡回インポートはコンパイラによって検出され、コンパイルエラーとなります。

- [US132 15.03 Macros from the command-line not exported by header units](https://github.com/cplusplus/nbballot/issues/131)

これは、コマンドラインオプション（`-D`など）によって定義されたマクロ名がヘッダユニットからエクスポートされないことを規定するものです。

これによって、そのようなマクロ名が重複したり、それがコンパイラによって異なったりする事が防止されます。ただ、これはどうやら文面として強制するものでは無いようです・・・

- [US367 6-15 Instead of header inclusion, also permit header unit import](https://github.com/cplusplus/nbballot/issues/363)

これは、グローバル`new/delete`を使うための`<new>`や`<=>`の戻り値型を使用するための`<compare>`など、言語機能の利用のために標準ライブラリヘッダのインクルードの必要が規定されているものについて、ヘッダユニットの`import`も認めるようにするものです。

### Resolution to US086

- [P1979R0 : Resolution to US086](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1979r0.html)
    - [US086 10.03 Treatment of non-exported imports](https://github.com/cplusplus/nbballot/issues/85)

この提案によって解決されるIssueは、あるモジュール単位`I`を同じモジュール内の他のモジュール単位`M`がインポートする時に、`I`のグローバルモジュールフラグメントにあるインポート宣言を暗黙的にインポートしないようにするものです。

同じモジュール内にあるモジュール単位をインポートするとき、インポートするモジュール単位内でインポートされているすべての翻訳単位をインポートします。2つのモジュール単位が別々のモジュールに属する場合のインポートは再エクスポート（`export imprt`）されている翻訳単位のみをインポートしますが、同じモジュール内でだけはインポート宣言がより多くの翻訳単位をインポートすることになります。

グローバルモジュールフラグメントは`#include`をモジュール内で安全に行うための宣言領域であり、そこにあるインポート宣言は`#include`の`import`への置換によって導入されたものでしょう。それらはグローバルモジュールに属するものであり`I`の一部ではなく、`I`からエクスポートされ`M`から到達可能となるのは不適切です。

`export`宣言はグローバルモジュールフラグメントに直接的にも間接的（`#include`やマクロ展開）にも書くことはできないので、グローバルモジュールフラグメントで`import`されている翻訳単位をインポートしてしまう可能性があるのは同じモジュール内でのモジュール単位のインポート時だけです。

当初の仕様ではその考慮は抜けており（モジュールTSでは考慮されていましたが、ATOMとのマージ時にグローバルモジュールフラグメントが導入されたことで見落とされていた様子）、グローバルモジュールフラグメントのインポート宣言がモジュールのインターフェースの一部となってしまっていたため、この提案では明示的にそうならないことを規定しています。

```cpp
/// uses_vector.h
import <vector>; // #includeからの置換である可能性がある
```
```cpp
/// partition.cpp
module;
#include "uses_vector.h" // import <vector>; と展開される
module A:partition;

// この中でstd::vector<int>を使っているとする。
```
```cpp
/// interface.cpp
module A;
import :partition;

// 必ずコンパイルエラーになるようになる
// ここでは<vector>はインポートもインクルードもされていない
std::vector<int> x; 
```

以前の仕様では、最後の`std::vector`の仕様がwell-definedとなってしまっていました。

### Dynamic Initialization Order of Non-Local Variables in Modules
- [P1874R1 Dynamic Initialization Order of Non-Local Variables in Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1874r1.html)
    - [US082 10.03 [module.import] Define order of initialization for globals in modules P1874](https://github.com/cplusplus/nbballot/issues/81)

当初の仕様では、モジュールとそれをインポートする翻訳単位の間で静的記憶域期間を持つオブジェクト（すなわちグローバル変数）の動的初期化順序が規定されていなかったために、`std::cout`の利用すら未定義動作を引き起こす可能性が潜んでいました。

```cpp
import <iostream>;  // <iostream>ヘッダユニットのインポート

struct G {
  G() {
    std::cout << "Constructing\n";
  }
};

G g{};  // Undefined Behaior!?
```

このような場合でも安全に利用できるようにするために、モジュールを含めた翻訳単位間での静的オブジェクトの動的初期化に一定の順序付けを規定するようにします。

ある翻訳単位がヘッダユニットも含めてモジュールをインポートする時、そのモジュールに対してインターフェース依存関係が発生します。インポートが絡む場合の動的初期化順序はこのインターフェース依存関係を1つの順序として初期化順序を規定します。ただし、この初期化順序は半順序となります（すなわち、順序が規定されない場合があります）。

同じ翻訳単位内での動的初期化順序はその宣言順で変わりありません。これは、別の翻訳単位をインポートしたときに、インポート先にある静的変数とインポート元の静的変数との間の動的初期化順序を最低限規定するものです。

#### 参考資料

- [［C++］モジュールインポート時の動的初期化順序 - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/02/07/205039)

### Core Language Changes for NB Comments at the February, 2020 (Prague) meeting

- [P2103R0 Core Language Changes for NB Comments at the February, 2020 (Prague) meeting](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2103r0.html)
    - [NB US 033: Allow import inside linkage-specifications](https://github.com/cplusplus/nbballot/issues/32)

これは、言語リンケージ指定を伴うブロック内での`import`宣言を許可するものです。

例えば`extern "C"`なブロック内でCのヘッダを`#include`している場合にも、そのファイルがC++としてコンパイルされていればそのヘッダを`import`に置換することができるはずです。しかし以前の仕様では`import`のリンケージ指定もリンケージブロック内での`import`も許可されていなかった（`import`宣言はグローバル名前空間スコープにのみ現れることができた）ため、その場合は常に`#include`するしかありませんでした。

このIssueの解決では、直接的に書くことができないのは従来通りですが、`#include`変換の結果としてヘッダユニットの`import`が現れるのが許可されるようになります。ただし、`C++`言語リンケージ指定以外に現れる`import`宣言は実装定義の意味論で条件付きのサポートとなります。

```cpp
extern "C" import "importable_header.h" // NG、直接書けない

extern "C" {
  #include "importable_header.h"  // OK、ヘッダユニットのインポートに変換可能
                                  // ただし、実装依存のサポート

  import "importable_header.h"    // NG、直接書けない
}

extern "C++" {
  #include "importable_header.h"  // OK、ヘッダユニットのインポートに変換可能
  
  import "importable_header.h"    // NG、直接書けない
}
```

このことは、構文定義を変更してインポート宣言をおよそ宣言が書ける場所にどこでも書けるようにしたうえで、文書でインポート宣言を書ける場所をグローバル名前空間スコープに限定しておき、リンケージ指定ブロック内で（`#include`置換の結果として）インポート宣言が間接的に現れることを許可する形で表現されており、少しややこしいです。


### Translation-unit-local entities

- [P1815R2: Translation-unit-local entities](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1815r2.html)
  - [US035 06.05 Referring to internal-linkage entities from certain exported ones should be ill-formed P1815](https://github.com/cplusplus/nbballot/issues/34)
  - [US133 15.03 Header units containing internal-linkage entities P2003 P1815](https://github.com/cplusplus/nbballot/issues/132)
  - [US134 15.03 Header units containing external-linkage entities P2003 P1815](https://github.com/cplusplus/nbballot/issues/133)

これは名前付きモジュールのインターフェースにある内部リンケージ名がそのモジュールの外部へ露出する事を禁止するものです。

これは特に、モジュール外部でインライン展開されうる関数にて問題になっていました。

```cpp
/// mymodule.cpp
module;
#include <iostream>
export module mymodule;

// 内部リンケージ
static void internal_f(int n) {
  std::cout << n << std::endl;
}

namespace {
  // 内部リンケージ
  int internal_g() {
    return 10;
  }
}

// エクスポートされている、外部リンケージ
export inline int external_f(int n) {
  // この関数がインライン展開されると・・・
  internal_f(n);
  return n + internal_g();
}
```

名前付きモジュールにおける`inline`関数が`export`される場合、その定義はそのモジュールのインターフェースに無ければなりません。そのため、`export`された`inline`関数は`inline`指定の本来の効果（関数のインライン展開の指示）の適用対象となります。

インライン展開される関数の本体から内部リンケージ名を参照していると、本来翻訳単位を超えて参照できないはずの内部リンケージ名がインライン展開によって翻訳単位の外側から参照されてしまう事になります。内部リンケージ名の翻訳単位外への暴露は望ましい動作では無いため、この提案によって禁止されました。

名前付きモジュールのインターフェースに存在する外部への露出が禁止されるもののことを、翻訳単位ローカルのエンティティ（*TU-local Entities*）と呼びます。TU-localエンティティの正確な定義は複雑ですが、ほぼ内部リンケージ名を持つ関数・変数・型のことを指します。

それらTU-localエンティティが`inline`関数などによって翻訳単位の外に曝露する可能性のある時、コンパイルエラーとなります。注意なのは、TU-localエンティティが曝露された時ではなく、その可能性がある段階でコンパイルエラーとなる事です。

```cpp
export module M;

// 内部リンケージの関数
static constexpr int f() { return 0; }

static int f_internal() { return f(); } // 内部リンケージ、OK
       int f_module()   { return f(); } // モジュールリンケージ、OK
export int f_exported() { return f(); } // 外部リンケージ、OK

// 外部orモジュールリンケージを持つinline関数は内部リンケージ名を参照できない
static inline int f_internal_inline() { return f(); } // OK
       inline int f_module_inline()   { return f(); } // NG
export inline int f_exported_inline() { return f(); } // NG
```

もう一つ、`inline`関数では無いけれどほぼ同じ振る舞いをするものにテンプレートがあります。テンプレートの厄介なところは、インスタンス化されるまで何を参照しているかが確定しない事にあります。そのため、テンプレートでは、インスタンス化された時に内部リンケージ名を参照する可能性がある場合にコンパイルエラーとなります。

```cpp
/// mymodule.cpp
export module mymodule;

export struct S1 {};

// 内部リンケージ
static void f(S1);  // (1)

export template<typename T>
void f(T t);  // (2)

// インスタンス化前はエラーにならない
export template<typename T>
void external_f(T t) {
  f(t);
}
```
```cpp
/// main,cpp
import mymodule;

struct S2{};

void f(S2);  // (3)

int main() {
  S1 s1{};
  S2 s2{};

  external_f(10);  // OK、(2)を呼ぶ
  external_f(s2);  // OK、(3)を呼ぶ
  external_f(s1);  // NG、(1)を呼ぶ
}
```

内部リンケージ名を参照する可能性がある場合というのは、直接的に現れていなかったとしても、関数オーバーロードの候補集合に内部リンケージな関数が含まれている場合です。その場合使用する関数の決定を待たずにコンパイルエラーとなります。

テンプレートに関しては例外があり、内部リンケージ名を外部から参照しエラーとなる宣言であっても、モジュールのインターフェース内で予め特殊化されインスタンス化済みである時はエラーとなりません（`inline`指定が無ければ）。

```cpp
/// mymodule.cpp
export module mymodule;

export struct S1 {};

static void f(S1 s);  // (1)

// 宣言はOK
export template<typename T>
void external_f(T t) {
  f(t);
}

// S1に対するexternal_f()の明示的インスタンス化
template void external_f<S1>(S1); // (2)
```
```cpp
/// main,cpp
import mymodule;

int main() {
  S1 s1{};

  external_f(s1);  // OK、(2)でインスタンス化済
}
```

この場合、モジュールは予めコンパイルされているはずなので、インスタンス化済のテンプレートのインスタンス化を省略し、通常の関数と同様にシグネチャのみで参照することができます。テンプレートは`inline`指定がなければインライン展開されるとは限らず、その必要がありません。


このようにこの提案の後では、名前付きモジュールにおける関数に対する`inline`指定はインライン展開の対象であることをコンパイラに伝えるマーカーとしての本来の役割のみを担うようになります。

#### 参考資料

- [［C++］TU-local Entityをexposureするのこと（禁止） - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2021/04/30/230638)

### ABI isolation for member functions

- [P1779R3: ABI isolation for member functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1779r3.html)

これは、名前付きモジュール内で定義されたクラスについて、その定義内で定義されているメンバ関数の暗黙`inline`をしなくするものです。

先ほどのP1815R2の変更によって、モジュールのインターフェース内の`inline`関数内での内部リンケージ名の使用がコンパイルエラーとなるようになります。これによって大きな影響を受けるのは、クラスの定義内で定義されているメンバ関数です。

クラス定義内で定義されているメンバ関数は暗黙`inline`であり、P1815R2の影響を強く受けることになります。

```cpp
export module M;

// 内部リンケージの関数
static constexpr int f() { return 0; }

// エクスポートされ外部リンケージを持つクラス定義
export struct c_exported {
  int mf_exported();
  int mf_exported_inline() { return f(); } // NG、暗黙inline
};

int c_exported::mf_exported() { return f(); } // OK、暗黙inlineではない
```

これを避けようとすると、メンバ関数は全てクラス外で定義することになってしまい、冗長な記述が増え、非メンバ関数との一貫性がなくなります。この辺りの使用は複雑なので、このことはユーザーにとって意味がわからないエラーとなるかもしれません。

クラス定義内で定義されたメンバ関数が暗黙`inline`なのは、ヘッダに定義を書いて複数の翻訳単位でインクルードした時に多重定義エラーを起こさないためなので、モジュールの利用においてはほとんど必要ありません。

そのため、この提案では名前付きモジュール内に限って、クラス定義内で定義されたメンバ関数に対する暗黙`inline`を行わないようにします。これによって、モジュールにおけるクラスの定義は今まで通りに行う事ができ、複雑なことをきにする必要は無くなります。

```cpp
export module M;

...

export struct c_exported {
  int mf_exported();
  int mf_exported_inline() { return f(); } // OK、暗黙inlineではない
};
```

ただし、このことはモジュールの外側（グローバルモジュール）においては従来通りです。モジュールではないところで定義されたクラスのクラス定義内で定義されたメンバ関数は相変わらず暗黙`inline`です。

### Modules Dependency Discovery

- [P1857R3 Modules Dependency Discovery](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1857r3.html)

これは、`module`と`import`を書くことのできる場所や形式を制限するものです。

P1703R1も同様の目的の変更でしたが、`module`はなんら制限されておらず、`import`を使用する既存のコードへの影響が小さくありませんでした。この提案はP1703R1のアプローチをさらに進めて、`module`を用いる構文についても書き方や書ける場所を制限し、かつ`import`と`module`を使用している既存のコードへの影響を減らそうとするものです。

この提案では、次の条件を満たすもので始まる行は、`inport`ディレクティブと`module`ディレクティブとして扱われるようになります。

- `import` : 以下のいずれかが同じ行で後に続くもの
    - `<`
    - 識別子（*identifier*）
    - 文字列リテラル
    - `:`（`::`とは区別される）
- `module` : 以下のいずれかが同じ行で後に続くもの
    - 識別子
    - `:`（`::`とは区別される）
    - `;`
- `export` : 上記2つの形式のどちらかの前に現れるもの

これらは新しいプリプロセッシングディレクティブとして扱われますが、プリプロセッシングディレクティブの扱いは従来通りであるため、ここでの`import, module, export`はマクロによって置換されたり導入されたりせず、ディレクティブは1行で書く必要があります。

```cpp
// これらは各行がプリプロセッシングディレクティブとみなされる
#                     
module ;              
export module leftpad;
import <string>;      
export import "squee";
import rightpad;      
import :part;

// これらの行はプリプロセッシングディレクティブではない
module            
;                     
export                
import                
foo;                  
export                
import foo;           
import ::             
import ->             
```

これによってまず、インポート宣言、モジュール宣言、グローバルモジュールフラグメント、プライベートモジュールフラグメントの構文は、マクロによって導入されず、1行で書かなければなりません。ただし、インポート対象の名前やモジュール名はマクロによって導入することができます。

なお、通常の`export`宣言はこれらの処理の対象ではありません。`export`から始まるプリプロセッシングディレクティブはあくまで、すぐ後に`import/module`が現れるものです。

これらのディレクティブに含まれる`import, module, export`はプリプロセッサによって`import-keyword, module-keyword, export-keyword`に置き換えられ、この`*-keyword`によるものがC++コードとしてのインポート宣言やモジュール宣言として扱われるようになります。

例えば次のようなコードは

```cpp
module; // グローバルモジュールフラグメント
#include <iosream>
export module sample_module;  // モジュール宣言

// インポート宣言
import <vector>;
export import <type_traits>;

// エクスポート宣言
export int f();

// プライベートモジュールフラグメント
module : private;

int f() {
  return 20;
}
```

プリプロセス後（翻訳フェーズ4の後）に、おおよそ次のようになります。

```cpp
__module_keyword;
#include <iosream>
__export_keyword __module_keyword sample_module;

__import_keyword <vector>;
__export_keyword __import_keyword <type_traits>;

// export宣言はプリプロセッシングディレクティブでは無い
export int f();

__module_keyword : private;

int f() {
  return 20;
}
```

`__import_keyword`などは実装定義なので実際にどう書き換えられるかは分からず、それを直接書くための構文は用意されていません。

そしてもう一つの大きな変更は、プリプロセスの一番最初の段階でソースファイルがモジュールファイルなのか通常のファイルなのかを判定し、モジュール宣言、グローバルモジュールフラグメントとプライベートモジュールフラグメントはモジュールファイルだけに現れることが出来るように規定されている事です。

この判定は、ファイルの一番最初に現れる非空白文字が`module`あるいは`export module`で始まっているかどうかをチェックすることで行われ、それがある場合にのみモジュールディレクティブに対応するディレクティブ（の処理方法）が定義されます。

通常のファイルとして処理された場合でもインポートディレクティブを処理することはできますが、モジュールディレクティブは対応するディレクティブが定義されないため、コンパイルエラーとなります。

この事は、`#ifdef`などによってあるファイルがモジュールであるかヘッダファイルであるかを切り替える、ような事ができないことを意味しています。

これらの事はCプリプロセッサのEBNFによる構文定義の中で表現されており、少し複雑です。



#### 参考資料

- [［C++］モジュールとプリプロセス - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/05/15/201112)

### Issueの解決3
- [P2109R0: US084: Disallow "export import foo" outside of module interface](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2109r0.html)

- [P2115R0: US069: Merging of multiple definitions for unnamed unscoped enumerations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2115r0.html)