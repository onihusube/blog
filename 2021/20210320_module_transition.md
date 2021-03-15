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

この提案はC++20に最初に導入されたモジュール仕様です。モジュールTS（N4720）にATOM提案（P0947R1）をマージする形になっています。

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

### Relaxing redefinition restrictions for re-exportation robustness

- [P1811R0 : Relaxing redefinition restrictions for re-exportation robustness](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1811r0.html)

### Mitigating minor modules maladies

- [P1766R1 : Mitigating minor modules maladies](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1766r1.html)

### Recognizing Header Unit Imports Requires Full Preprocessing

- [P1703R1 : Recognizing Header Unit Imports Requires Full Preprocessing](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1703r1.html)

### Standard library header units for C++20

- [P1502R1 : Standard library header units for C++20](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1502r1.html)

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
