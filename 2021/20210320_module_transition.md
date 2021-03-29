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



```cpp
/// foo.h
#ifndef FOO_H
#define FOO_H
typedef struct { /*...*/ } X;
#endif
```
```cpp
module;
#include "foo.h"
export module A;
X x;
```
```cpp
export module B;
import A;
```
```cpp
/// main.cpp
import B;
#include "foo.h"
```

翻訳単位`main.cpp`では`X`の定義は到達可能ではないため、`X`の定義を含めることは許可されます。しかし、この時でもコンパイラがモジュール`A`の`X`の定義を知っている場合、`X`の定義をマージする作業が必要となります。

この提案では、リンケージを与えるための`typedef`の対象となる構造体は次のものを含むことができないようにします。

- 非静的データメンバ・メンバ列挙型・メンバ型（入れ子クラス）を除くすべてのメンバ
- 基底クラス
- データメンバに対するデフォルト初期化子
- ラムダ式

この提案によって、リンケージを与えるための`typedef`はC言語互換のためだけの機能であることが明確となり、その対象となる構造体はC互換の構造体に限定されるようになります。

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
  STR(foo);  // error: can’t export empty-declaration ';'
  STR(bar);  // error: can’t export empty-declaration ';'
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

この提案では、異なる翻訳単位の同じ名前空間スコープの2つの宣言が、同じ関数引数に異なるデフォルト引数を、同じテンプレート引数に異なるデフォルトテンプレート引数を指定することをそれぞれ禁止します。ただし、異なるデフォルト引数を持つ複数の宣言が同時に到達可能とならない限り、コンパイルエラーとならない可能性があります。

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

そのために、__C++の__ 標準ヘッダは全てヘッダユニットとしてインポート可能であると規定し、標準ライブラリへのアクセス手段としての標準ヘッダのインポートを明確に規定します。なお、C互換の標準ヘッダ（`<cmath>, <cassert>`などの`<c~~~>`系のヘッダ）はインポート可能ではありません（これらのヘッダは事前のマクロ定義に大きく影響を受けますが、ヘッダユニットも含めたモジュールは外で定義されたマクロが内部に影響を及ぼしません）。

また同時に、`std`から始まる全てのモジュール名を将来の標準ライブラリモジュールのために予約します。

### Issueの解決1

- [GB022 04.01Allow "import" for accessing standard library names](https://github.com/cplusplus/nbballot/issues/22)
    - [[intro.compliance] The standard library also offers header units. - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/3356)
- [FR039 06.05.2.4 Non-exported functions should not be visible via ADL after importing](https://github.com/cplusplus/nbballot/issues/38)
    - [[basic.lookup.argdep] Inline the definition of 'interface'. - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/3390)
- [GB 078 10.01 Harmonize "digits" referring to reserved namespace/module names](https://github.com/cplusplus/nbballot/issues/77)
    - [[namespace.future,diff.cpp14.library] Properly refer to grammar 'digit'](https://github.com/cplusplus/draft/pull/3345)
- [P1971R0 : Core Language Changes for NB Comments at the November, 2019 (Belfast) meeting](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1971r0.html)
    - [GB079 10.01 Add example for private-module-fragment](https://github.com/cplusplus/nbballot/issues/78)
    - [US087 10.03 p9 Header unit imports cannot be cyclic, either](https://github.com/cplusplus/nbballot/issues/86)
    - [US132 15.03 Macros from the command-line not exported by header units](https://github.com/cplusplus/nbballot/issues/131)
    - [US367 6-15 Instead of header inclusion, also permit header unit import](https://github.com/cplusplus/nbballot/issues/363)
- [P1979R0 : Resolution to US086](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1979r0.html)
    - [US086 10.03 Treatment of non-exported imports](https://github.com/cplusplus/nbballot/issues/85)
- [US088 10.04 [module.global] Harmonize labels referring to the global module fragment](https://github.com/cplusplus/nbballot/issues/87)
    - [[module.global,cpp.glob.frag] Rename labels to ...global.frag.](https://github.com/cplusplus/draft/pull/3351)
- [GB089 10.06 [module.reach] Mark translation unit boundaries in example](https://github.com/cplusplus/nbballot/issues/88)
  - [[module.reach] Clearly separate translation units in example.](https://github.com/cplusplus/draft/pull/3331)

### Dynamic Initialization Order of Non-Local Variables in Modules
- [P1874R1 Dynamic Initialization Order of Non-Local Variables in Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1874r1.html)
    - [US082 10.03 [module.import] Define order of initialization for globals in modules P1874](https://github.com/cplusplus/nbballot/issues/81)

### Issueの解決2

- [P2103R0 Core Language Changes for NB Comments at the February, 2020 (Prague) meeting](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2103r0.html)
    - [NB US 033: Allow import inside linkage-specifications](https://github.com/cplusplus/nbballot/issues/32)

### ABI isolation for member functions

- [P1779R3: ABI isolation for member functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1779r3.html)

### Modules Dependency Discovery
- [P1857R3 Modules Dependency Discovery](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1857r3.html)

### Issueの解決3
- [P2109R0: US084: Disallow "export import foo" outside of module interface](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2109r0.html)

- [P2115R0: US069: Merging of multiple definitions for unnamed unscoped enumerations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2115r0.html)

### Translation-unit-local entities

- [P1815R2: Translation-unit-local entities](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1815r2.html)
