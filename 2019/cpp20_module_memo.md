
# P1103R3メモ書き

## まえがき

※読み進めながら書いてるので記法に一貫性がないです。  
※翻訳には多分に間違いが含まれています、怪しい記述を信用しないでください。

Wroding Changeの項では変更点のみを翻訳するのではなく関連する記述をまとめて翻訳し、P1103R3以降の変更も反映しています（N4861ベースにするための作業中）

関連する文書等の一覧
- [P1103R3 : Merging Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1103r3.pdf)
- [[module.interface] Use 'namespace-definition', #2916 - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/2916)
- [Typo fixes for sample code comments related to modules. #2951 - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/2951)
- [[basic.lookup.argdep]/5 Added export to `apply(T t, U u)` #2973 - C++ Standard Draft Sources](https://github.com/cplusplus/draft/pull/2973)
- [P1811R0 : Relaxing redefinition restrictions for re-exportation robustness](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1811r0.html)
- [P1766R1 : Mitigating minor modules maladies](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1766r1.html)
- [P1703R1 : Recognizing Header Unit Imports Requires Full Preprocessing](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1703r1.html)
- [P1502R1 : Standard library header units for C++20](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1502r1.html)
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
      - `new`とか`<=>`とか対応するヘッダのインクルードが必要なものについて、`import`を明示的に許可する。以下では省略
- [P1979R0 : Resolution to US086](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1979r0.html)
    - [US086 10.03 Treatment of non-exported imports](https://github.com/cplusplus/nbballot/issues/85)
- [US088 10.04 [module.global] Harmonize labels referring to the global module fragment](https://github.com/cplusplus/nbballot/issues/87)
    - [[module.global,cpp.glob.frag] Rename labels to ...global.frag.](https://github.com/cplusplus/draft/pull/3351)
- [GB089 10.06 [module.reach] Mark translation unit boundaries in example](https://github.com/cplusplus/nbballot/issues/88)
  - [[module.reach] Clearly separate translation units in example.](https://github.com/cplusplus/draft/pull/3331)
- [P1874R1 Dynamic Initialization Order of Non-Local Variables in Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1874r1.html)
    - [US082 10.03 [module.import] Define order of initialization for globals in modules P1874](https://github.com/cplusplus/nbballot/issues/81)
- [P2103R0 Core Language Changes for NB Comments at the February, 2020 (Prague) meeting](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2103r0.html)
    - [NB US 033: Allow import inside linkage-specifications](https://github.com/cplusplus/nbballot/issues/32)

### 未追記

- [P1779R3: ABI isolation for member functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1779r3.html)
- [P1857R3 Modules Dependency Discovery](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1857r3.html)
- [P2109R0: US084: Disallow "export import foo" outside of module interface](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2109r0.html)
- [P2115R0: US069: Merging of multiple definitions for unnamed unscoped enumerations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2115r0.html)
- [P1815R2: Translation-unit-local entities](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1815r2.html)

## 以下本文

- module unit : モジュール単位  
モジュールを構成する翻訳単位  
ファイル先頭のモジュール宣言によりモジュール単位は開始される  
その後にimport宣言が続く（なくてもよい

モジュール宣言
```cpp
module foo;  //ファイル先頭で行う
```

- module interface unit : モジュールインターフェース単位  
module unitであり、モジュール宣言にexportを伴うもの

モジュールインターフェース宣言
```cpp
export module foo;  //ファイル先頭で行う
```

モジュールのインターフェースを定義する  
インターフェース：シグネチャ、宣言みたいな

モジュールは少なくとも一つがモジュールインターフェース単位である必要がある

- primary module interface unit : プライマリモジュールインターフェース単位  
モジュール名と同じモジュールインターフェース宣言を含むモジュール単位  
モジュールfooなら`export module foo;`

- module interface partitions : モジュールインタフェースパーティション  
プライマリではないすべてのモジュールインターフェース単位

## visible と reachable

- visible : 可視  
名前探索によって宣言が見つかれば、そのコンテキストでその宣言は可視である

- reachable : 到達可能  
名前の意味論的効果が使用可能である場合、そのコンテキストでその宣言は到達可能である  
例えば、あるコンテキストでクラスが完全型であるならば、そのクラスの定義は到達可能である

宣言は可視 -> 到達可能 : true  
到達可能 -> 宣言は可視 : false（必ずしも成り立たない）

importはどの名前空間スコープの名前が可視になるか
および、どの宣言が意味論的に（semantically）到達可能か
だけをコントロールする。

あるエンティティの振る舞いは、そのエンティティの到達可能な宣言の集合によって決まる（エンティティ = 名前・定義？）
例えば、クラス・列挙体のメンバはその定義が到達可能であるとき、名前探索で可視である

## export
宣言は`export`を用いてモジュールインターフェース単位内でエクスポートできる

内部リンケージを持つものを除いて、エクスポートされていない宣言はそのモジュール単位をインポートする同じモジュール内の名前探索で可視である

推移的にインポート（not 再エクスポート）されたモジュール単位内のすべての宣言は、エクスポートされているかにかかわらず到達可能（可視になるとは言ってない）

モジュール単位は対応するモジュールインタフェース単位を暗黙にインポートする

名前空間内の宣言（名前空間を伴う宣言）がエクスポートされると、その名前空間も暗黙的にエクスポートされる。
名前空間をエクスポートすると、名前空間内の宣言は（暗黙的に）エクスポートされる。

## module partitions : モジュールパーティション

一つのモジュールは単一のファイルでも複数のファイルでも定義できる。  
例えば、宣言（モジュールインターフェースユニット）と定義（実装）をファイルで分割することができる。

モジュールパーティションは、そのようなインターフェースと実装を分割することを可能にする

- module interface partitions : モジュールインターフェースパーティション

モジュールインターフェースは必要に応じて複数のファイルに分割することができる。
それらのファイルをモジュールインターフェースパーティションと呼ぶ。
以下のようなモジュールインターフェースパーティション宣言を（その他のモジュール宣言の代わりに）含む翻訳単位のこと。

モジュールインターフェースパーティション宣言
```cpp
export module foo::part;
```

モジュールインターフェースパーティションに含まれるエンティティの所有権は属しているモジュールと共有される。  
それ以外は、モジュールインターフェースパーティションは単一のモジュールと同じ振る舞いをする。  

そのため、エンティティの宣言と定義を別々のパーティションで行うことができる  
これは、モジュール内部で発生しうる循環参照（依存関係のループ）を解決するために必要  
これはまた、ABIを変えることなくモジュール内でコードを移動することができる

プライマリモジュールインターフェース単位は、モジュール内のすべてのインターフェースパーティションの推移的インポートと再エクスポートをしなければならない。

- module implementation partitions : モジュール実装パーティション

モジュール内で実装が複数のファイルに分割されており、モジュール内で他のモジュールインターフェースパーティションで定義されたものを使用している場合、実装の詳細（定義）に依存することを避けるために、宣言をモジュールインターフェース単位に含めずに実装単位間で共有することが望ましいことがある  
そうすることで、定義が変更されたときにモジュールインターフェースとその依存関係を再構築する必要がなくなる  
それを可能にするのが モジュール実装パーティションである。

モジュール実装パーティション宣言
```cpp
module foo:part;
```
これは、モジュールインターフェース単位の一部ではないモジュールパーティションとなる

モジュール実装パーティションはエクスポートされた宣言を含めることができない
代わりに、モジュール実装パーティションをインポートすることで、そのモジュール実装パーティションのすべての宣言は同じモジュール内の他の翻訳単位から可視となる

`export`はモジュール外部への名前と宣言の可視性にのみ影響を与える。

- module partitions : モジュールパーティション  
モジュールインタフェースパーティションとモジュール実装パーティションはまとめて、モジュールパーティションと呼ぶ

モジュールパーティションはモジュールの実装の詳細であり、その名前をモジュール外部から参照することはできない。
そのため、モジュールパーティションを指名する`import`宣言はモジュール名を指定できず、パーティション名のみを指定することができる


```cpp
module foo;    //モジュール宣言
import :part;  //モジュールパーティションのインポート

//モジュール名の指定はコンパイルエラー
import bar:part;  //ng
import foo:part;  //ng
```

## 非モジュールコードとの相互運用

### グローバルモジュールフラグメント

以下のように、モジュール（インターフェース）単位で旧来のヘッダをインクルードした場合、そのモジュール内のすべての翻訳単位でインクルードしたのと同じことになってしまう（同じモジュール内の他のファイルでもインクルードしたヘッダの中身が見える）。

```cpp
export module mymodule;

#include <iostream>
```

グローバルモジュールフラグメントは、モジュール内部で他のモジュールパーティションから見えないように旧来のヘッダファイルを#includeするための仕組み

```cpp
module;  //グローバルモジュールフラグメントの（開始）宣言

#include <iostream>

//グローバルモジュールフラグメントの終了
export module mymodule;  //モジュールインターフェース宣言
```

グローバルモジュールフラグメント内の宣言はモジュールによって所有されない

グローバルモジュールフラグメントに含まれる宣言によってモジュールが肥大化することを防ぐため、モジュール単位で参照されていないグローバルモジュールフラグメント内の宣言は破棄される  
そのような宣言は、モジュール単位をインポートするほかの翻訳単位からは到達不可能であり 
モジュール単位の外での2段階目のテンプレートのインスタンス化（two phase name lookup）の際に見つからない

すなわち、グローバルモジュールフラグメント内の宣言は
- グローバルモジュールフラグメント終了後のそのモジュール単位内で名前が現れるか
- そのように参照されている宣言で名前が現れる

場合にその宣言が参照されているとみなされる。

```cpp
module;

#include <tuple>

export module mymodule;

export using int_tuple = std::tuple<int, int, int>;

export auto f() -> std::tuple<char, short, double>;

//これ以外のstd::tuple特殊化および、すべての関数の宣言は使用されていないので破棄される
//破棄された宣言はモジュールに含まれず、コンパイルもされない
//そして、このモジュールをimportした先で参照することもできない
```

### ヘッダーユニット

```cpp
export module foo;  //モジュールインターフェース宣言

//ヘッダーユニットのインポート宣言
import "some-header.h";
import <version>; 
```

`import`に指定されたヘッダファイルはソースファイルのように処理され、ヘッダー内のインターフェースが抽出され`import`した翻訳単位で使用可能になる。  
また、ヘッダー内でプリプロセス時に定義されたマクロも保存され、`import`した翻訳単位で使用可能になる。

ヘッダーユニット内の宣言及びコードはどのモジュールにも所有されない。  
同じエンティティを別のヘッダーユニットもしくは非モジュールコードにおいて再宣言できる。

ヘッダーユニットは通常の再エクスポート宣言と同じように再エクスポートできる。

```cpp
export module foo;
export import "some-header.h";  //ヘッダーユニット”some-header.h”の再エクスポート
```

ただし、マクロをインポートできるのはヘッダーユニット構文だけであり、再エクスポートではマクロはエクスポートされない。

### 非モジュールコード内宣言の到達可能性
グローバルモジュールフラグメント及びヘッダーユニット内の宣言は可視であるときに到達可能である。

そのような宣言が可視ではないが、推移的にインポートされている文脈でも到達可能かどうかは未規定。  
理想的にはそのような（推移的にインポートされた）宣言は到達可能であるべきではないが、そのように規定すると実装によっては実装コストが大きくなってしまうため、標準はその扱いについて規定しない。  
このルールが適用される範囲は実装に任せている。

グローバルモジュールフラグメントにおいて破棄された宣言は、モジュールの外側で可視ではなく、到達可能でもない。


### 非モジュールコードでのモジュールの利用
モジュールとヘッダーユニットは非モジュールコードにインポートすることができる。そのような`import`宣言はプリアンブルに限定されず、どこでも行うことができる。  
これによって、ボトムアップなモジュール化が可能になり、ライブラリはモジュールによるインターフェースのみを提供し、かつモジュールによるインターフェースによってヘッダーインターフェースを定義する事を切り替えることができる。

非モジュールコードには、モジュール単位を除いた翻訳単位（インポートされたヘッダーユニットを含む）及び、モジュール単位内のグローバルモジュールフラグメントが含まれる。

非モジュールコードに#includeがあり、そこで指名されているヘッダファイルがヘッダーユニット化可能である場合、実装はその#includeをヘッダーユニットのインポートに置き換える。

このような置き換えが可能な#includeを見つける方法は実装定義である。  
実装方法は様々考えられ、研究が進むことを期待してのこと。
（ヘッダーユニットを明示的にビルドしてその後のコンパイル時に利用する、ヘッダーユニットの構成を記述するファイルを導入する、など）

実装は、マッピングメカニズムを提供せずに各ヘッダーユニットを個別に処理してもいい

## 以前のバージョンからの変更

### R2からの変更

偶然到達可能なエンティティが他の定義をill-formedにしてしまうバグを修正
```cpp
// a.h 
#ifndef A_H 
#define A_H 
class X {}; 
#endif

// b.cc
module;
#include "a.h" 
export module B; 
X x;

// c.cc 
export module C; 
import B; // not exported

// d.cc 
import C; 
#include "a.h" //"semantic boundaries rule"によって、Xの定義が見えたとしても問題ない
```
グローバルモジュールフラグメント内のクラスXの宣言はモジュール`B`の外で可視でも到達可能でもない。
しかし、`d.cc`では（`#include "a.h"`によって）Xの宣言が可視であり到達可能である（定義が見える）。ここはグローバルモジュールなので（以前の提案とODRの下では）ODR違反を引き起こす。
これは”semantic boundaries rule”によって許可される。  
（semantic boundaries rule：以前の定義が到達可能なところで再定義されてはならない。）

モジュールリンケージを持つエンティティが複数のモジュール単位で定義を持つことを許可

### R1からの変更

#### P1299R2: Module preamble is unnecessarily fragile
この提案以前は、ヘッダーユニットからインポートされたマクロがモジュール内でインポートされている物に影響を与えることは禁止されていた。

この規則によってユーザーと実装の両方で複雑さが増してしまい、依存関係の抽出をしたい実装側にとって期待した利益では正当化されないため  
この規則は削除された

この提案によると、ヘッダーユニットからインポートされたマクロはインポート直後に利用可能になる。そのようなマクロはモジュール単位のプリアンブルの後、ほかのインポート宣言の前に展開される。

#### P1242R1: Single-ﬁle modules
この提案は モジュールTSにあった”attendant entities”ルールを削除する。

このルールはモジュールの機能に空白を残していた。
モジュールの実装詳細をモジュール外部で利用できないままで、モジュールを単一ファイルで定義する方法はもはやなかった。

この提案では`module :private;`というマーカーを利用してインターフェースから実装を分離し、インターフェースと実装を備えた完全なモジュールを単一ファイルで定義できる。

### R0からの変更

#### 名前空間のエクスポート

R0およびモジュールTSでは、モジュールインターフェース単位で宣言されている全ての名前空間（無名名前空間とその中身を除く）は外部リンケージを持ち、暗黙的にエクスポートされる。

しかし、明示的に`export`した名前空間か、エクスポートされた宣言に含まれている名前空間のみがエクスポートされるように変更された。

これによって、モジュール実装詳細で使用されてる名前空間をモジュールインターフェース単位で宣言しても、モジュールインターフェースから隠す（分離する）ことができる。

#### テンプレートのインスタンス化における到達可能性

P0947R1のルールに基づいて、テンプレートインスタンス化内の宣言の可視性と到達可能性を解決するために、インスタンス化経路（path of instantiation）ルールを使用する。

テンプレートインスタンス化時に利用される宣言が、たとえテンプレートの定義されたところでもインスタンス化されるところでも可視でも到達可能でもなかったとしても  
このルールの下では、テンプレートのインスタンス化の経路の各点で可視または到達可能であれば、それら全ての宣言を利用することが許可される。

```cpp
//moduleA.cpp
export module A;

export template<typename T, typename U> void f(T t, U u) { t.f(); }


//moduleB.cpp
module;

//グローバルモジュールフラグメント内宣言、モジュールBからのみ可視
struct S { 
  void f();
};

export module B;

import A;  //モジュールAのインポート（not エクスポート）

export template<typename U> void g(U u) { S s; f(s, u); }


//moduleC.cpp
export module C;

import B;  //モジュールBのインポート（not エクスポート）

export template<typename U> void h(const U &u) { g(u); }


//main.cpp
import C;

int main() { 
  h(0);
}
```
構造体`S`の定義およびそのメンバ関数`S::f()`の宣言は、インスタンス化地点（`f<S, int>()`）からもそのテンプレート定義からも到達可能ではない。  
しかし、`S`はインスタンス化経路上のモジュールBにおいて到達可能であるので、このコードは有効である。

宣言がインスタンス化経路上でさえも到達可能でなかったとしても、インスタンス化したところにおいてそれら宣言が推移的にインポートされているのならば、実装はそれらを到達可能な追加宣言として扱うことが許されている。

```cpp
module M;

struct S;

import C; // unspeciﬁed whether a deﬁnition of S is reachable here or in the instantiation of h<S>

void q(const S &s) { h(s); } 
```
この例ではモジュールMにおいて`S`の定義は到達可能ではないが、インポートしているモジュールCを通して推移的にインポートされているモジュールBに定義がある。  
この時、`import C;`の点およびそのあとの`h<S>`のインスタンス化地点で`S`の定義が到達可能であるかは未規定（実装は到達可能であるとしてもよい）。

この、インスタンス化経路（path of instantiation）というルールはADLにも適用される。
インスタンス化経路で可視である名前はADLでも可視になる。

さらに、関連する型が属しているモジュールでエクスポートされた宣言もADLで可視となる。

ただし、グローバルモジュール内の内部リンケージ宣言は無視される。

#### プリアンブルの終端の検出

R0ではプリプロセッサはプリアンブルの終端を見つけたうえで、その場所でヘッダーユニットからインポートされたマクロを可視にするという負担を負っていた。  
実装者にとっては実装が難しく、ユーザーにとっては書いたコードの想定異なる振舞を行い、プリアンブルのインポートと非モジュールコードでのインポートとで意味が異なることになる
など、問題があった。

そのため、この提案ではよりシンプルなルールを導入する。
ヘッダーユニットからインポートされたマクロは、そのヘッダーユニットのインポート宣言の直後に可視になる。

### モジュール TSからの変更

グローバルモジュールフラグメントの前に、`module;`という導入宣言が必要になった。

モジュールによって所有されているがエクスポートされていないエンティティが、モジュールインターフェースのエクスポート宣言によって参照されている場合  
モジュール TSはそのエクスポートの時点で、エクスポートしているエンティティに関連する意味論的プロパティ（semantic properties）をエクスポートする。
もし、そのような複数のエクスポートがエンティティに異なる意味を与える場合はill-formed

```cpp
export module M;

struct S;
export S f(); // S incomplete here

struct S {};
export S g(); // S complete here, error 
```

Atom提案では、そのようなエンティティの意味は、モジュールインターフェース単位の最後にその特性から決定される。

この提案では、モジュールによって所有される全てのエンティティの意味は、モジュールインターフェース単位の終わりにその特性から決定される（エクスポートされているかに関わらず）。

モジュールインターフェースに宣言どの順番で表れるかは、どの特性による意味がエクスポートされるかとは無関係。  
（あるエンティティのどの特性が意味としてエクスポートされるかは、宣言順に依存しない）

モジュール TSにあった、付随するエンティティ（attendant entities）ルールは、適用できるケースが無くなったため削除された。

モジュール内で`extern "C"`、`extern "C++"`で宣言されたエンティティはモジュールによって所有されなくなった。  
（モジュールTSの意図からの変更であるかは不明）

この提案では、名前空間名はあまり頻繁にエクスポートされなくなった。

### P0947R0 (“Another Take On Modules”)からの変更

この提案では、グローバルモジュールフラグメントをサポートするが、Atom提案のプリアンブルをコンパイラ以外に識別させるという目標を妨げている。
しかし、その目標から得られる利点はグローバルモジュールフラグメントを利用しない場合には有効である。

Atom提案では`export`と`module`は文脈依存キーワードとされていたが、この提案ではそれぞれキーワードとして扱われる。  
これは、[P0924R0](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0924r0.pdf)における議論からのEWGの指示に従っている。


## Wording Change

### 4.1 Implementation compliance [intro.compliance]

#### 5

標準ライブラリで定義される名前は名前空間スコープを持つ。C++翻訳単位は、適切な標準ライブラリのヘッダファイルの`#include`か、適切な標準ライブラリのヘッダーユニットの`import`によって、これらの名前へのアクセスを取得する。

### 5.4 Preprocessing tokens [lex.pptoken]
- preprocessing-token:
	- header-name
	- import-keyword
	- module-keyword
	- export-keyword
	- identifier
  - pp-number
  - character-literal
  - user-defined-character-literal
  - string-literal
  - user-defined-string-literal
  - preprocessing-op-or-punc
  - 上記のいずれにも当てはまらない空白文字

#### 3
入力ストリーム（ソースコード）が次に示す特定の文字までにプリプロセッシングトークンにパースされた場合、それぞれ次のように処理される。
1. 次の文字が`R"`のような生文字列リテラルの可能性のある文字列で始まる場合
    - 次のプリプロセッシングトークンは生文字列リテラルである
    - 生文字列中の最初と最後のダブルクオートの間の文字列に対して翻訳フェーズ1,2で実行された処理は元に戻される
      - この変換はd-char,r-charおよび区切りかっこが識別される前に適用される
    - 生文字列リテラルは次のパターンに一致する最短の文字列として定義される
    - encoding-prefix (opt) `R` raw-string
    - encoding-prefixは`u8 u U L`のこと
2. そうではなく、次の三文字が`<​::​`であり後続の文字が`: >`のどちらでも無い場合
    - `<`は代替トークン`<:`の最初の文字としてではなく、単体でプリプロセッシングトークンとして扱われる
3. 上記いずれも当てはまらない場合
    -  次のプリプロセッシングトークンはプリプロセッシングトークンを構成できる最長の文字列（たとえ字句解析が失敗したとしても）
    - ただし、header-nameは以下のいずれかの場合にのみ形成される
      - `#include`ディレクティブまたは`import`ディレクティブの後
      - has-include-expressionの内部
      - ~~これまでに処理された一連のプリプロセッシングトークンが翻訳フェーズ4までコンパイル可能であり、結果として`import`宣言になる場合、プリプロセッシングディレクティブの外側では翻訳フェーズ4を適用する。~~

#### 4
import-keywordは`import`ディレクティブをプリプロセスすることで生成され、module-keywordは`module`ディレクティブをプリプロセスすることで生成され、export-keywordはその2つのディレクティブをプリプロセスする事で生成される。

この他に、記述するための文法は無い。

### 5.11 Keywords [lex.key]

- Keywords:
	- 表5に記載のある識別子
	- import-keyword
	- module-keyword
	- export-keyword

### 6.3 One-deﬁnition rule [basic.def.odr]

#### 1  
1つの翻訳単位には、変数、関数、クラス型、列挙型、テンプレート、特定のスコープ内関数のデフォルト引数、デフォルトテンプレート引数、これらの定義を複数含めることはできない。

#### 11

定義領域（*definition domain*）は次のどちらか。
- プライベートモジュールフラグメント（private-module-fragment）
- プライベートモジュールフラグメントを除いた、翻訳単位の残りの部分
    - プライベートモジュールフラグメントがない場合は、翻訳単位の全域

inline関数/変数の定義は、*discarded statement*の外側でodr-usedされているすべての定義領域の終端から到達可能でなければならない。

#### 12

クラスの定義は、そのクラスが完全型であることを要求して使用されるすべての文脈で到達可能でなければならない

#### 13 
あるエンティティに対する定義が複数の翻訳単位に現れている時、それらの定義が以下の要件を満たす場合、次のものはプログラム内に複数の定義を持つことがある。  
（ただし、名前付きモジュールに属するエンティティは複数の定義を持ってはならない。その場合、後の定義が現れるときに前の定義が到達可能でなければ、診断は不要である。）

- クラス・列挙型
- 外部リンケージを持つinline関数・変数
- テンプレート化されたエンティティ
    - テンプレート
      - クラステンプレート
        - 静的メンバ変数
        - メンバ関数
      - 非static関数テンプレート
      - コンセプト
      - テンプレートの部分特殊化
    - テンプレート化されたエンティティ内で作成・定義されたエンティティ
    - テンプレート化されたエンティティのメンバ
    - テンプレート化されたエンティティである列挙型の列挙子
    - テンプレート化されたエンティティの宣言内で現れるラムダ式のクロージャ型
- 特定のスコープ内関数のデフォルト引数
- デフォルトテンプレート引数

（ここから、以下の要件、and条件）  
`D`という名前のエンティティが複数の翻訳単位で定義されているとして

- それぞれの`D`の定義は全て、名前付きモジュールに属していない
- それぞれの`D`の定義は全て、同じトークン列で構成されている（全く同じ文字列である）
- `D`の各定義において、名前探索の結果の対応する名前は、`D`の定義内で定義されたエンティティを指すか、オーバーロード解決とテンプレートの部分特殊化のマッチング後に同じエンティティを指すものとする。ただしその名前は次のものを指す事ができることを除く
  - 内部リンケージを持つ非`volatile const`かリンケージを持たない、次を満たすオブジェクト、であるか
    - `D`のすべての定義は同じリテラル型を持つ
    - 定数式で初期化されている
    - どの`D`の定義もodr-usedされていない
    - すべての`D`の定義は同じ値を持つ
  - すべての`D`の定義で同じ実態を参照するように定数式で初期化された、内部リンケージかリンケージを持たない参照
- `D`の各定義において、対応するエンティティは同じ言語リンケージを持つ
- `D`の各定義において、参照されるオーバーロードされた演算子関数（暗黙変換演算子/コンストラクタ、`new/delete`を含む）は、同じ関数を指すか、`D`の定義内で定義された関数を指す
- `D`の各定義において、（あらゆる形の）関数呼び出しによって使用されるデフォルト引数、及びあらゆる形で使用されるテンプレートのデフォルトテンプレート引数は、そのトークン列が`D`の定義内にあるかのように扱われる。  
つまり、デフォルト引数はここで示されている（複数定義を持ちうる）要件に従う。そのデフォルト引数が再帰的にデフォルト引数を持つ呼び出しを行う場合、これらの要件も再帰的に適用される。
- `D`が事前条件を持つ関数呼び出しを行うか、アサーションもしくは契約条件を持つ関数である場合
`D`のすべての定義が同じビルドレベルと違反継続モードを用いてコンパイルされる条件は処理系定義（これらアサーションや契約条件は、C++20より導入のContractの事）
- `D`が暗黙的に宣言されたコンストラクタを持つクラス型の場合、そのコンストラクタがodr-usedされているすべての翻訳単位で暗黙的に定義されているかのように振る舞う。そのコンストラクタの暗黙定義は、`D`のサブオブジェクトに対して同じコンストラクタを呼び出さなければならない。
```cpp
// translation unit 1:
struct X {
  X(int, int);
  X(int, int, int);
};
X::X(int, int = 0) { }

class D {
  X x = 0;
};
D d1;                           // X(int, int) called by D()

// translation unit 2:
struct X {
  X(int, int);
  X(int, int, int);
};
X::X(int, int = 0, int = 0) { }

class D {
  X x = 0;
};
D d2;                           // X(int, int, int) called by D();
                                // D()の暗黙定義はODR違反！
```

`D`がテンプレートであり複数の翻訳単位で定義されている場合、以上の要件は、テンプレートの定義で使用されているそれを囲むスコープからの名前と、インスタンス化地点の依存名、の両方に適用される。

`D`の定義がこれらの要件を満たす場合、プログラムは`D`の定義は一つだけであるかのように動作する。そうでない場合（`D`の定義が要件を満たさない場合）、動作は未定義。  
（1つ目の要件以外は、すべての定義の持つ意味が同じになる事！を言っている。ただし、2つ目の条件の入れ子の要件に該当するものはその限りではない。）

#### 15

`D`の定義がこれらの要件を満たしていない場合、プログラムはill-formed。ただし、診断が必要となるのはエンティティが名前付きモジュールに属していて、あとの定義が現れた時点で前の定義に到達可能となる場合のみ。

### 6.4.5 Namespace scope [basic.scope.namespace] 

翻訳単位`Q`が別の翻訳単位`R`にインポートされている時、`Q`の名前空間スコープで宣言された名前`X`の潜在的なスコープは、  
次の全てを満たす場合に`Q`を（直接または間接的に）インポートする`R`の、最初のmodule-import-declarationかmodule-declarationに続く、`R`の対応する名前空間スコープを含むように拡張される。

- `X`は内部リンケージを持たない
- `X`が`Q`内のmodule-declarationの後に宣言されている（もしあれば）
- `X`はエクスポートされているか、`Q`と`R`は同じモジュールの一部

[module-import-declarationは指定された翻訳単位と、その中でexported module-import-declarationによって指定された全てのモジュールの両方を再帰的にエクスポートする]

### 6.5 Name lookup [basic.lookup]
（ある名前の）名前探索、関数オーバーロード解決、アクセスチェック、が成功した後で初めて、その名前の宣言及び到達可能な再宣言によって導入された意味論的特性（*semantic properties*）が式の処理（評価）に使用される。

### 6.5.4 Argument-dependent name lookup [basic.lookup.argdep]

#### 4

関連名前空間`N`を探索するとき、次の点を除いて`N`が修飾子として使用されるときに実行される探索と同じことが行われる。

- N内のusingディレクティブはすべて無視される
- 関数と関数テンプレート（オーバーロードされているかもしれない）、以外の名前はすべて無視される
- 関連エンティティの集合の中で 到達可能な定義を持つ クラス内で宣言されたフレンド関数（テンプレート）は、たとえそれらが通常の名前探索で可視でなかったとしてもそれぞれの名前空間内で可視である
- 名前付きモジュール`M`本文の、名前空間`N`の内側にあるエクスポートされた宣言`D`は、`D`を囲む最も内側の非inline名前空間内に、`M`に属する関連エンティティがある場合にすべて可視となる
- 探索が依存名に対するものである場合、`N`内の宣言`D`がインスタンス化コンテキスト内の任意の点における修飾名探索で可視であるとき、次の場合を除いて`N`内の宣言`D`はすべて可視である。
  - 宣言`D`は別の翻訳単位でグローバルモジュールに属して宣言されており、かつ
    - 破棄されている、もしくは
    - 内部リンケージを持つ

```cpp
/// 翻訳単位1
export module M;

namespace R {
  export struct X {};
  export void f(X);
}
namespace S {
  export void f(R::X, R::X);
}
```
```cpp
/// 翻訳単位2
export module N;
import M;

export R::X make();

namespace R {
  static int g(X);
}

export template<typename T, typename U> void apply(T t, U u) {
  f(t, u);
  g(t);
}
```
```cpp
/// 翻訳単位3
module Q;
import N;

namespace S {
  struct Z { template<typename T> operator T(); };
}

void test() {
  auto x = make();  // OK, decltype(x)はR​::​Xでmodule Mにあり、可視ではないが名前を参照していない
  R::f(x);          // error: RとR​::​fは可視ではない
  f(x);             // OK, R​::​f()をモジュールMからADLで呼び出し
  f(x, S::Z());     // error: 名前空間Sは関連名前空間に含まれるが
                    // モジュールMのS::fはADLの候補ではない（第二引数の推定に失敗する）

  apply(x, S::Z()); // error: S​::​fインスタンス化コンテキストで可視
                    // しかし、R::gは内部リンケージであり、翻訳単位の外からは呼べない
}
```

### 6.5.5.3 Namespace members [namespace.qual] 
名前空間`X`と名前`m`があるとき、名前空間修飾探索集合`S(X, m)`は次のように定義される
- `X`内のすべての`m`の宣言及び、`X`内のinline名前空間の集合を`S'(X, m)`とする
  - その潜在的なスコープには、`m`が宣言されている場所のnested-name-speciﬁerの名前空間が含まれる
- `S'(X, m)`が空でない場合、`S'(X, m) = S(X, m)`
- そうでない場合は`S(X, m)`は`S(Ni, m)`のiについての和集合、`Ni`は`X`内にあるすべてのusingディレクティブとinline名前空間の集合の元

### 6.6 Program and linkage [basic.link]
プログラムは互いにリンクされた1つ以上の翻訳単位から成る。

翻訳単位は宣言の列から成る。

- translation-unit
  - declaration-seq (opt)
  - global-module-fragment (opt) module-declaration declaration-seq (opt) private-module-fragment (opt)

#### 3  
ある名前が、別のスコープの宣言によって導入された名前と同じ、オブジェクト、参照、関数、型、テンプレート、名前空間、値、を指し示す場合、その名前は __リンケージ__ （*linkage*）を持つ。

名前が外部リンケージを持つ場合、 その名前が指し示すエンティティは次の名前から参照することができる（参照されうる、逆もしかり）。
- 他の翻訳単位内のスコープにある名前
- 同じ翻訳単位内の他のスコープにある名前

名前がモジュールリンケージを持つ場合、その名前が指し示すエンティティは次の名前から参照することができる。
- 同じモジュール単位内の他のスコープにある名前
- 同じモジュール内の他のモジュール単位のスコープにある名前

名前が内部リンケージを持つ場合、 その名前が指し示すエンティティは次の名前から参照することができる。
- 同じ翻訳単位内の他のスコープにある名前

名前がリンケージを持たない場合、 その名前が指し示すエンティティは他のスコープの名前から参照することができない。

#### 4
名前空間スコープをもつ名前のうち、非テンプレートの`volatile`ではない`const`変数は、次のいずれでもない場合に内部リンケージを持つ。
- 明示的に`extern`と宣言されている
- `inline`変数
- エクスポートされている
- その変数名は以前に宣言されていて、その宣言が内部リンケージを持たない

[Note: const修飾された型のインスタンス化された変数テンプレートは、`extern`と宣言されていなくても、外部リンケージまたはモジュールリンケージを持つ]

#### 5
無名名前空間、または無名名前空間で直接または間接的に宣言された名前空間は内部リンケージを持つ。  
そうでない名前空間は外部リンケージを持つ。  
上記の内部リンケージを持たない名前空間を持ち、次のいずれかのものの名前
- 変数
- 関数
- 名前付きクラス
- `typedef`された名前を持つ、`typedef`で宣言された名前のないクラス
- 名前付き列挙型
- `typedef`された名前を持つ、`typedef`で宣言された名前のない列挙型
- テンプレート

である場合のリンケージは次のように決定される。
- 囲む名前空間が内部リンケージを持つ場合、その名前も内部リンケージを持つ。
- そうでなく、名前の宣言は名前付きモジュールに属しており、エクスポートされてない場合、その名前はモジュールリンケージを持つ。
- それ以外の場合、その名前は外部リンケージを持つ。

#### 7
ブロックスコープで宣言された関数名と、extern付きの変数名はリンケージを持つ。  
そのような宣言が名前付きのモジュールに属している場合、プログラムはill-formed。

#### 10
2つの名前が同じであり異なるスコープで宣言されているとき、次の全てを満たす場合に同じ変数・関数型、テンプレート、名前空間、を表す。
- 2つの名前が外部リンケージかモジュールリンケージを持っており、同じモジュールに属した宣言によって宣言されている、もしくは、2つの名前が内部リンケージを持ち同じ翻訳単位で宣言されている
- 2つの名前は同じ名前空間、もしくは継承されていないクラスのメンバーを参照する
- 両方の名前が関数名であるとき、その引数型が同一である
- 両方の名前がテンプレート関数名であるとき、そのシグネチャが一致している

（関数名でなければ、上の二つを満たしていれば二つの名前は同じものを指している）

外部リンケージを持つ同じ名前の複数の宣言が、異なるモジュールに属していること以外は同じエンティティを宣言している場合、プログラムはill-formdであり、診断は不要。

#### 11
宣言が、別のモジュールに属した到達可能な宣言を再宣言する場合、プログラムはill-formd

```cpp
///ヘッダファイル "decls.h":
int f();            // #1, グローバルモジュールに属している
int g();            // #2, グローバルモジュールに属している


///Module interface of M:
module;
#include "decls.h"
export module M;
export using ::f;   // OK: エンティティを宣言していない、#1をエクスポートする
int g();            // error: #2と同じエンティティの再宣言、Mに属する宣言になるためエラー
export int h();     // #3
export int k();     // #4


///Other translation unit:
import M;
static int h();     // error: #3と同じエンティティの再宣言、同じモジュールに属していない
int k();            // error: #4と同じエンティティの再宣言、同じモジュールに属していない
```

この規則によって、エンティティのすべての宣言は同じモジュールに所属していなければならない、という帰結が得られる。
そのようなエンティティはモジュールに ***属している（attached）*** と言われる


#### 13

宣言`D`は次のいずれかの場合、エンティティ`E`を __指名する（*names*）__

1. `D`はラムダ式を含んでおり、そのクロージャ型が`E`
2. `E`は関数でも関数テンプレートでもなく、`D`には`E`を示す次のいずれかのものが含まれている
    - *id-expression*
    - *type-specifier*
    - *nested-name-specifier*
    - *template-name*
    - *concept-name*
3. `E`は関数か関数テンプレートであり、`D`には`E`を指定する式、または`E`を含むオーバーロードの集合を参照する*id-expression*が含まれている。

[Note: インスタンス化された宣言内の非依存名は、オーバーロードの集合を参照しない。]

#### 14

宣言は次のいずれかの場合に、__曝露（*exposure*）__ している
1. 次の場合を無視して、TU-localエンティティ（次で定義する）を指名（*names*）する
      - 非`inline`関数または関数テンプレートの本体
         - ただし、プレースホルダ型を戻り値型として宣言された関数の、（インスタンス化された可能性のある）定義の推定された戻り値型ではない
      - 変数または変数テンプレートの初期化子
      - クラス定義内フレンド宣言
      - 非`volatile`な`const`オブジェクトへの参照、またはodr-useされておらず定数式で初期化された内部リンケージかリンケージ名の無い参照
2. TU-local値（次で定義する）で初期化された`constexpr`変数を定義する

[Note: `inline`関数テンプレートは、その明示的特殊化が他の翻訳単位で使用可能な場合でも、曝露（*exposure*）している可能性がある。]

#### 15

エンティティは次のいずれかの場合に**TU-local**である

1. 型、関数、変数、テンプレートであって
   1. 内部リンケージ名をもつ、か
   2. TU-localエンティティの定義内で、ラムダ式によって導入または宣言され、リンケージ名を持たないもの
2. クラスの宣言・定義、関数本体、初期化子、の外側で定義されている名前のない型
3. TU-localエンティティを宣言するためだけに使用される、名前のない型
4. TU-localテンプレートの特殊化
5. TU-localテンプレートを実引数として与えられたテンプレートの特殊化
6. その宣言が曝露されているテンプレートの特殊化
      - [Note: 特殊化は、暗黙的あるいは明示的なインスタンス化によって生成できる]

#### 16

値もしくはオブジェクトは次のいずれかの場合に**TU-local**である

1. それがTU-local関数またはTU-local変数に関連付けられているオブジェクトであるか、そのポインタ型である
2. クラスか配列型のオブジェクトであり、そのサブオブジェクトのいずれか、もしくは参照型の非静的データメンバが参照するオブジェクトまたは関数のいずれかがTU-localであり、定数式で使用可能（*usable in constant expression*）である

#### 17

モジュールインターフェース単位（プライベートモジュールフラグメントが存在する場合はその外側）またはモジュールパーティション内の、（インスタンス化されている可能性のある）非TU-localエンティティの宣言またはその推論補助が、曝露（*exposure*）しているとき、プログラムはill-formed。

他のコンテキストでのこのような宣言は、非推奨である。

#### 18

ある翻訳単位に現れる宣言が、ヘッダユニットではない別の翻訳単位で宣言されたTU-localエンティティを指名する場合、プログラムはill-formed。

テンプレートの特殊化によってインスタンス化された宣言は、その特殊化のインスタンス化地点（*instantiation point*）に現れる。

#### 19

```cpp
/// 翻訳単位1（プライマリインターフェース単位）
export module A;

static void f() {}

inline void it() { f(); }           // error: fを曝露している
static inline void its() { f(); }   // OK

template<int>
void g() { its(); }   // OK
template void g<0>();

decltype(f) *fp;                    // error: fはTU-local（fの型ではない）
auto &fr = f;                       // OK
constexpr auto &fr2 = fr;           // error: fを曝露している（fのアドレスはTU-localな値）
constexpr static auto fp2 = fr;     // OK

struct S { void (&ref)(); } s{f};               // OK, 値（fのアドレス）はTU-local
constexpr extern struct W { S &s; } wrap{s};    // OK, 値（sのアドレス）はTU-localではない

static auto x = []{f();};           // OK
auto x2 = x;                        // error: クロージャ型はTU-local
int y = ([]{f();}(),0);             // error: クロージャ型はTU-localではない
int y2 = (x,0);                     // OK

namespace N {
  struct A {};
  void adl(A);
  static void adl(int);
}
void adl(double);

inline void h(auto x) { adl(x); }   // OK, ただしその特殊化はN::adl(int)を曝露しうる
```
```cpp
/// 翻訳単位2（実装単位）
module A;
void other() {
  g<0>();                   // OK, 特殊化は明示的にインスタンス化されている
  g<1>();                   // error: 特殊化の実体は、TU-localなits()を使用している
  h(N::A{});                // error: オーバーロード候補集合はTU-localなN​::​adl(int)を含んでいる
  h(0);                     // OK, adl(double)を呼ぶ
  adl(N::A{});              // OK; N​::​adl(N​::​A)を呼び、N​::​adl(int)は見つからない
  fr();                     // OK, f()を呼ぶ
  constexpr auto ptr = fr;  // error: frは定数式で使用可能ではない
}
```

### 6.9.3.1 main function [basic.start.main]

#### 1
プログラムはグローバルモジュールに属している`main`という名前のグローバル関数を含む。

#### 2
以下のプログラムは全てill-formdである。
- グローバルスコープで`main`という名前の変数を宣言している
- 名前付きのモジュールに属しているグローバルスコープで`main`という名前の関数を宣言している
- Cリンケージを使用して`main`という名前の関数を宣言している

### 6.9.3.3 Dynamic initialization of non-local variables [basic.start.dynamic]

#### 1

静的記憶域期間を持つ非ローカル変数の動的初期化順序が順序付けされるかは、その変数に応じて次のように規定される。

- （暗黙・明示的に）インスタンス化されたテンプレートの特殊化
    - 順序付けされない（*unordered*）
- （暗黙・明示的に）インスタンス化されたテンプレートの特殊化、ではない`inline`変数
    - 半順序が規定される（*partially-ordered*）
- その他の場合（上記2つのいずれでもないその他全ての変数）
    - 順序が規定される（*ordered*）

[Note: 明示的に特殊化された、非`inline`静的データメンバまたは変数テンプレートの特殊化の初期化は、順序が規定される、]

#### 2

次のどちらかの場合、宣言`D`は宣言`E`の前に、 __出現順通りに順序付け（*appearance-ordered*）__ される

- `D`は`E`と同じ翻訳単位に現れる
- `E`を含む翻訳単位は`D`を含む翻訳単位にインターフェース依存関係を持つ

いずれの場合も`E`の出現より前にそうなっている。

#### 3

静的記憶域期間を持つ非ローカル変数`V, W`の動的初期化は、次の順序で行われる

1. `V`と`W`の初期化は順序が規定されており、`V`の定義は`W`の定義の前に __出現順通りに順序付け__ されているか、
2. `V`の初期化は半順序が規定されていて（すなわち、非テンプレートの`inline`変数）かつ、`W`の初期化は何らかの順序が規定されており、`W`の全ての定義`E`に対して __出現順通りに順序付け__ される`V`の定義`D`が存在する場合、次のどちらか
      1. プログラムがメインスレッド以外のスレッドを開始しないか、`V`と`W`の初期化は順序が規定されており同じ翻訳単位で定義されている場合
         - `V`の初期化は`W`の初期化の前に順序付けられる（*sequenced before*）
      2. それ以外の場合
         - `V`の初期化は`W`の初期化の前に強く発生する（*strongly happens before*）
3. そうではなく、`V`か`W`（どちらか）の初期化前にプログラムがメインスレッド以外のスレッドを開始する場合
      - `V`と`W`の初期化がどのスレッドで発生するかは未規定、かつ
      - `V`と`W`の初期化が同じスレッドで発生した場合の初期化順序も未規定
4. それ以外の場合、`V`と`W`の初期化順序は不定

[Note: この定義によって、順序付けられた変数シーケンスを別のシーケンスの初期化と同時に（並行して）行うことができる]

## 7.7 Constant expressions [expr.const]

### 3

変数は、`constexpr`変数であるか、参照であるか、`const`修飾された整数型/列挙型である場合、潜在的に定数（*potentially-constant*）である。

### 4

定数で初期化された*potentially-constant*な変数`V`は、`V`の初期化宣言`D`が点`P`から到達可能であり、かつ次のいずれかの場合に、点`P`において定数式で使用可能（*usable in constant expression*）である

1. `V`は`constexpr`変数
2. `V`はTU-local値で初期化されていない、もしくは
3. `P`は`D`と同じ翻訳単位にある

（以下、追加の定数式で使用可能（*usable in constant expression*）なオブジェクトor参照の定義が続く。定数式で使用可能はそのままの意味で、`constexpr`の文脈で使用可能な変数という意味。）

### 9.2.3 The typedef specifier [dcl.typedef]

#### 10
リンケージ目的で`typedef`名を持つ無名クラスは次のものを含んではならない。

- 非静的データメンバ、メンバ列挙型、メンバ型（入れ子クラス）以外のメンバ
- 基底クラス
- データメンバに対するデフォルト初期化子
- ラムダ式

そして、この規則はそのメンバとなっているクラスにも再帰的に適用される。

```cpp
typedef struct {
  int f() {}
} X;  //error: リンケージのためにtypedef名を持つクラスがメンバ関数を持っている
```

### 9.2.7 The inline specifier [dcl.inline]

#### 2

（中略）  
[Note: `inline`は関数のリンケージには影響しない。場合によっては、`inline`関数は内部リンケージ名を使用できない。]

#### 4 (削除)

~~クラス定義内で定義された関数は`inline`関数である。~~

#### 5

関数・変数の定義が、最初のinline宣言の時点で到達可能である場合、プログラムはill-formed。

外部リンケージまたはモジュールリンケージをもつ関数・変数が1つの定義領域（*definition domain*）内で`inline`宣言されている場合、その`inline`宣言は、それが宣言されている全ての定義領域の終端から到達可能でなければならない。ただし、この診断は不要。

[Note: `inline`関数の呼び出し、`inline`変数の使用は、その定義が翻訳単位で到達可能となる前に発生する可能性がある。]

#### 6

[Note: 外部リンケージまたはモジュールリンケージを持つ`inline`関数・変数は、複数の翻訳単位で定義することができるが、1つのアドレスを持つ1つのエンティティである。従って、それらの関数内で定義された型または`static`変数は単一のエンティティである]

#### 7

名前付きモジュールに属している`inline`関数/変数がある定義領域（*definition domain*）で宣言されている場合、その領域で定義されなければならない。

[Note: `constexpr`関数は暗黙`inline`である。グローバルモジュールでは、クラス定義内で定義された関数は暗黙`inline`である。]

### 9.2.8.5 Placeholder type specifiers [dcl.spec.auto]

#### 10
プレースホルダ型（`auto, decltype(auto)`とそれのコンセプト付き）を戻り値型に使用する宣言を持つエクスポートされた関数は、そのエクスポートされた宣言を含む翻訳単位内で、かつ（存在している場合は）プライベートモジュールフラグメントの外側で定義されなければならない。  
[Note: 推論される戻り値型は、内部リンケージ名を持つことはできない。]

### 9.3.3.6 Default arguments [dcl.fct.default]

テンプレートでない関数は、同じスコープの後の宣言でデフォルト引数を追加できる。  
異なるスコープの宣言には完全に異なるデフォルト引数の集合がある。つまり、より内側のスコープの宣言はそれより外側のスコープの宣言からデフォルト引数を取得しない、その逆も同様。

特定の関数宣言では、デフォルト引数を持つ引数の後の各引数には以前の宣言、もしくはその宣言で導入されたデフォルト引数が指定されていなければならない。  
ただし、そのような（デフォルト引数の後の）引数がパラメータパックから展開された場合、もしくは関数パラメータパックである場合を除く。

[Note: デフォルト引数はたとえ同じ値であっても後の宣言で再定義することはできない。]

[Example省略]

異なる翻訳単位で定義された特定の`inline`関数では、それぞれの翻訳単位の終端での累積となるデフォルト引数の集合は同一でなければならない。ただし、この診断は不要。

`friend`宣言でデフォルト引数式が指定されている場合、その宣言は定義であり、かつその翻訳単位における唯一の関数・関数テンプレートの宣言でなければならない。

### 9.5.2 Explicitly-defaulted functions [dcl.fct.def.default]

#### 3

削除済みとして定義されていない、明示的に`default`指定された関数は、*constexpr-compatible*であるときに`constexpr/consteval`宣言できる。最初の宣言でで明示的に`default`指定された関数は、暗黙`inline`であり、*constexpr-compatible*であるときに暗黙`constexpr`となる。

### 9.8 Namespaces [basic.namespace]

#### 1
名前空間は名前付き（無くても良い）の宣言領域である。  
名前空間の名前を利用して、名前空間内に宣言されたエンティティにアクセスできる。すなわち、そのようなエンティティは名前空間のメンバである。  
他の宣言領域とは異なり、名前空間の定義は1つ以上の翻訳単位に分割でき、さらにその中で複数の部分に分割できる。

#### 2
名前空間の定義のうちの1つがエクスポートされる場合、または名前空間がエクスポートされた宣言を含む場合、外部リンケージを持つ名前空間がエクスポートされる。  
名前空間はモジュールに属すことはなく、エクスポートされなかったとしてもモジュールリンケージを持つことはない。

### 9.11 Linkage specifications[dcl.link]

#### 4

モジュールインポート宣言はリンケージ指定（*linkage-specification*）に直接含まれてはならない。C++言語リンケージ以外のリンケージ指定に現れているモジュールインポート宣言は、実装定義の意味論で条件付きでサポートされる。  
（*linkage-specification*とは`extern "C"`のこと。直接というのは`extern "C++" import M;`のような形式、ブロックで囲う形式のなかに現れているときは、C++言語リンケージだけサポート）

### 10.1 Module units and purviews [module.unit]

- module-declaration:
  - export-keyword(opt) module-keyword module-name module-partition(opt) attribute-speciﬁer-seq(opt);
- module-name:
  - module-name-qualifier(opt) identifier
- module-partition:
  - : module-name-qualifier(opt) identifier
- module-name-qualifier:
  - identifier `.`
  - module-name-qualifier identifier `.`

#### 1
__モジュール単位__（*module unit*）とは __モジュール宣言__（module-declaration）を含む翻訳単位。  
__名前付きモジュール__（*named module*）とは同じ __モジュール名__（module-name）を持つモジュールの集まり。  
`module`と`import`の識別子は、モジュール名もしくは __モジュールパーティション__（module-partition）の識別子として表れることはない。

`std`（+0個以上の数字列）から始まるモジュール名、及び予約語を含むモジュール名は全てC++標準によって予約されているため、モジュール名として使用してはならない。ただし、この診断は不要。  
そのように予約されたモジュール名のうち、その名前が予約語であるものはC++実装（処理系）のため、それ以外のものは将来のC++標準のため、それぞれ予約されている。

（オプショナルである）attribute-speciﬁerseqはモジュール宣言に作用する（attribute-speciﬁerseqは0個以上の属性指定のこと）。

#### 2
__モジュールインターフェース単位__（*module interface unit*）はそのモジュール宣言に`export`が含まれているモジュール単位。  
それ以外のモジュール単位は全て __モジュール実装単位__（*module implementation unit*）。  
名前付きモジュールは、プライマリーモジュールインターフェース単位（*primary module interface unit*）と呼ばれるモジュールパーティションを持たないモジュールインターフェース単位を、ただ1つだけ含んでいなければならない。ただし、この診断は不要。

#### 3
__モジュールパーティション__（*module partition*）はそのモジュール宣言にmodule-partition（上の構文ルールの中の句）が含まれるモジュール単位。  
名前付きモジュールは同じmodule-partitionをもつ複数のモジュールパーティションを含んではならない。   
あるモジュールのモジュールインターフェース単位でもある全てのモジュールパーティションは、プライマリーモジュールインターフェース単位によって、直接的・間接的にエクスポートされなければならない。ただし、これに違反したとしても診断は不要。  
[Note: モジュールパーティションは同じモジュール内の他のモジュール単位によってのみインポートできる。モジュールのモジュール単位への分割は外側からは可視ではない。]

#### 4
```cpp
//翻訳単位#1（プライマリーモジュールインターフェース単位）

export module A;  //プライマリーモジュールインターフェース宣言
export import :Foo;  //モジュールパーティションA:Fooをimportしつつexport
export int baz();  //関数baz()のエクスポート

//翻訳単位#2（モジュールインターフェースパーティションA:Foo）

export module A:Foo;  //モジュールインターフェースパーティション宣言
import :Internals;  //モジュールパーティションA:Internalsのインポート
export int foo() {   //関数foo()のエクスポート
  return 2 * (bar() + 1);
}

//翻訳単位#3（モジュールパーティションA:Inetrnal）

module A:Internals; //モジュールパーティション宣言
int bar();  //関数宣言（エクスポートしてない）

//翻訳単位#4（モジュール実装単位）

module A;  //モジュール宣言
import :Internals;  //モジュールパーティションA:Internalsのインポート

//bar()とbaz()両関数の定義、bazのみがエクスポートされている
int bar() {
  return baz() - 10;
}
int baz() {
  return 30;
}

```
モジュール`A`は4つの翻訳単位を含んでいる。
- プライマリーモジュールインターフェース単位（翻訳単位#1）
- モジュールパーティション`A:Foo`（翻訳単位#2）、これはモジュール`A`のインターフェースの一部となるモジュールインターフェース単位。
- モジュールパーティション`A:Internals`（翻訳単位#3）、これはモジュール`A`の外向きのインターフェースには寄与しない
- 関数`baz`と`bar`の定義を提供しているモジュール実装単位（翻訳単位#4）、パーティション名が無いためインポート不可

#### 5
__モジュール単位の本文__（*module unit purview*）とは、モジュール宣言から始まりその翻訳単位の終わりまでのトークン列。  
名前付きモジュール`M`の本文は、`M`のモジュール単位のそれぞれの本文の集合である。

#### 6

__グローバルモジュール__（*global module*）とは、全てのグローバルモジュールフラグメントと全てのモジュール単位ではない翻訳単位、の集まりである。  
そのようなコンテキストで現れる宣言は、グローバルモジュールの本文内にあると言われる。  
[Note: グローバルモジュールは、名前が無く、モジュールインターフェース単位も持たず、いかなるモジュール宣言によっても導入されない]

#### 7
__モジュール__（*module*）は名前付きモジュールかグローバルモジュールのいずれか。

ある宣言はそれぞれ以下のように、モジュールに __属している__（*attached*）
- 次のいずれかの場合、宣言はグローバルモジュールに __属している__
  - 宣言は置換可能なグローバル確保・解放関数（`new/delete`）
  - 宣言は外部リンケージを持つ名前空間定義
  - 宣言はリンケージ指定内に現れている
- それ以外の場合、宣言はそれが現れるところを本文とするモジュールに __属している__

#### 8
`export`もモジュールパーティションも含まないモジュール宣言は、module-import-declarationによるかのように、そのモジュールのプライマリーモジュールインターフェース単位を暗黙的に`import`する。

```cpp
// TU 1
module B:Y; // モジュールパーティション宣言、モジュールBを暗黙的にインポートしない
int y();

// TU 2
export module B;  //Bのプライマリーモジュールインターフェース単位の宣言
import :Y; // OK, does not create interface dependency cycle
int n = y();

// TU 3
module B:X1; //モジュールパーティション宣言、モジュールBを暗黙的にインポートしない
int &a = n;  //error: n はここでは可視ではない

// TU 4
module B:X2; //モジュールパーティション宣言、モジュールBを暗黙的にインポートしない
import B;    //明示的なBのインポート
int &b = n;  //OK、n は可視

// TU 5
module B; //exportがなくパーティションでもないモジュール宣言、モジュールBを暗黙的にインポート
int &c = n; // OK、n は可視
```

### 10.2 Export declaration [module.interface]

- export-declaration:
  - `export` declaration
  - `export` { declaration-seq (opt) }
  - export-keyword module-import-declaration

#### 1
`export`宣言（export-declaration）は、モジュールインターフェース単位の本文内にある名前空間スコープでのみ現れる。  
`export`宣言は、無名名前空間又はプライベートモジュールフラグメント内に直接的にも間接的にも現れてはならない。  
`export`宣言は、その宣言（存在する場合は、declaration-seq）の宣言的効果を持つ。  
`export`宣言は、スコープを導入することはなく、その宣言又はdeclaration-seqは再帰的に`export`宣言を含んではならない。

#### 2
宣言は以下のいずれかに該当する場合に __エクスポート__（*exported*）される。
- `export`宣言内で宣言された名前空間スコープ
- `export`を伴うモジュールの`import`宣言
- エクスポートされた宣言を含む名前空間定義
- 少なくとも1つの名前を導入するヘッダーユニット内の宣言

モジュール`M`の __インターフェース__（*interface*）はその本文内でエクスポートされたすべての宣言の集合

```cpp
export module M;  //プライマリーモジュールインターフェース単位の宣言

namespace A {                   // exported
  export int f();               // exported
  int g();                      // not exported
}
```
このモジュール`M`のインターフェースは、名前空間`A`と関数`A::f()`からなる。

#### 3
エクスポートされた宣言は少なくとも1つの名前を宣言しなければならない。そのような宣言がヘッダーユニット内に無い場合、内部リンケージで名前を宣言してはならない。

```cpp
//a.h
export int x;

//翻訳単位 #1
module;
#include "a.h"  // error: xのexport宣言がモジュールインターフェース単位ではない所に来ている

export module M;
export namespace {}             // error: 名前を宣言していない
export namespace {
  int a1;                       // error: 内部リンケージを持つ名前のエクスポート（間接的に無名名前空間内でexportしている）
}
namespace {
  export int a2;                // error: 内部リンケージを持つ名前のエクスポート
}
export static int b;            // error: static指定は内部リンケージを与える
export int f();                 // OK
export namespace N { }          // OK
export using namespace N;       // error: 名前を宣言していない
```

#### 5
（エクスポートされている）宣言が`using`宣言であってヘッダーユニット内にない場合、全てのusing-declaratorsが最終的に参照する全てのエンティティは外部リンケージを持つ名前で導入されていなければならない。

```cpp
//Source file "b.h":
int f();

//Importable header "c.h":
int g();

//Translation unit #1:
export module X;
export int h();

//Translation unit #2:
module;

#include "b.h"

export module M;

import "c.h";
import X;
export using ::f, ::g, ::h;     // OK
struct S;
export using ::S;               // error: Sは外部リンケージではなくモジュールリンケージを持つ
namespace N {
  export int h();
  static int h(int);            // static指定は内部リンケージを与える
}
export using N::h;              // error: N::h(int)が内部リンケージを持ってしまっている
```

ただし、この制約は`typedef/using`による型エイリアスの名前には適用されない。

```cpp
export module M;

struct S;

export using T = S;             // OK, 型Sのエイリアスとなる名前Tをエクスポートする
```

#### 6
エンティティのエクスポートされた宣言の再宣言は暗黙的にエクスポートされる。
以前の宣言がエクスポートされておらず、再宣言がエクスポート宣言となる場合、プログラムはill-formd。

```cpp
export module M;

struct S { int n; };
typedef S S;

export typedef S S;             // OK, エンティティの再宣言をしない
export struct S;                // error: 以前にエクスポートされていないクラスSの再宣言
```

#### 7
ある名前がモジュールの本文内のエクスポートされた宣言によって導入or再宣言されている場合、その名前はモジュールによって __エクスポートされている__ （*exported*）。  
[Note: 
エクスポートされた名前は外部リンケージを持つか、リンケージを持たない。  
モジュールによってエクスポートされた名前空間スコープの名前は、そのモジュールをインポートしている翻訳単位の名前探索において可視となる。  
クラス・列挙型のメンバの名前は、その型の定義が到達可能なコンテキストにおいて、名前探索で可視となる。]

```cpp
//モジュールMのプライマリモジュールインターフェース単位
export module M;

export struct X {
  static void f();
  struct Y { };
};

namespace {
  struct S { };
}

export void f(S);               // OK

struct T { };
export T id(T);                 // OK

export struct A;                // A は不完全型としてエクスポート

export auto rootFinder(double a) {
  return [=](double x) { return (x + a/x)/2; };
}

export const int n = 5;         // OK, nは外部リンケージを持つ

//モジュールMの実装単位
module M;

struct A {
  int value;
};

//Main program:
import M;

int main() {
  X::f();                       // OK, Xはエクスポートされており、その定義は到達可能
  X::Y y;                       // OK, X​::​Yはエクスポートされており、完全型
  auto f = rootFinder(2);       // OK
  return A{45}.value;           // error: Aは不完全型（Aの定義はエクスポートされておらず、到達可能でない）
}
```

#### 8
エクスポート宣言（export-declaration）内で名前を再宣言しても、その名前のリンケージを変更できない（されない）。

```cpp
//モジュールMのプライマリモジュールインターフェース単位
export module M;

static int f();                 // #1 static指定は内部リンケージを与える
export int f();                 // error: #1は内部リンケージをもつためエクスポートできない
struct S;                       // #2 名前空間に包まれていないので、モジュールリンケージを持つ
export struct S;                // error: #2はモジュールリンケージを持つためエクスポートできない
namespace {
  namespace N {
    extern int x;               // #3 無名名前空間内、内部リンケージ
  }
}
export int N::x;                // error: #3は内部リンケージをもつためエクスポートできない
```

#### 9
エクスポートされた名前空間定義または、エクスポートされたリンケージ指定（linkage-specification）内部の宣言はエクスポートされ、エクスポートされた宣言のルールに従う。

```cpp
export module M;

export namespace N {
  int x;                  //ok
  static_assert(1 == 1);  //error: 名前を宣言していない
}
```

### 10.3 Import declaration [module.import]

- module-import-declaration:
  - import-keyword module-name attribute-specifier-seq(opt);
  - import-keyword module-partition attribute-specifier-seq(opt);
  - import-keyword header-name attribute-specifier-seq(opt);

#### 1
モジュールインポート宣言（*module-import-declaration*）はグローバル名前空間スコープにのみ現れる。  
モジュール単位におけるすべてのモジュールインポート宣言（*module-import-declaration*）およびモジュールインポート宣言をエクスポートするエクスポート宣言（*export-declaration*）は、その翻訳単位及び（存在する場合は）プライベートモジュールフラグメントにおける*declaration-seq*内にあり、かつそこに含まれる他の全て宣言よりも前に宣言されなければならない。  
モジュールインポート宣言に対する属性指定（*attribute-specifier-seq*）はモジュールインポート宣言に作用する。

#### 2
モジュールインポート宣言（`module-import-declaration`）は以下のように決定された翻訳単位の集合を __インポート__（*imports*）する。  
[Note: インポートされた翻訳単位からエクスポートされている名前空間スコープ名はインポートする翻訳単位で可視となり、インポートされた翻訳単位内の宣言はインポート宣言の後、インポートする翻訳単位で到達可能になる。]

1. モジュール`M`の名前を指定するインポート宣言（`import M;`）は、`M`の全てのモジュールインターフェース単位をインポートする。
2. モジュールパーティションを指定するインポート宣言は、あるモジュール`M`のモジュール単位におけるモジュール宣言の後にのみ現れることができる。  
そのような宣言は`M`のモジュールパーティションをインポートする。
3. ヘッダー名`H`を指定するインポート宣言は、`H`で指定されたヘッダーもしくはソースファイルを翻訳フェーズ7までコンパイルすることで生成された翻訳単位である __ヘッダーユニット__（*header unit*）をインポートする。ヘッダーユニットにはモジュール宣言は含まれない。  
[Note: ヘッダーユニット内のすべての宣言は暗黙的にエクスポートされ、グローバルモジュールに属する。]  
__インポート可能なヘッダー__（*importable header*）は全てのインポート可能なC++ライブラリヘッダを含んだ実装定義のヘッダーの集合であり、`H`はインポート可能なヘッダーを識別する。そのような2つのインポート宣言があるとすると
    1. それら2つのインポート宣言のヘッダ名が異なるヘッダやソースファイルを識別している場合、それらは個別のヘッダーユニットをインポートする。
    2. そうではなく（ヘッダ名が同じで）、それら2つのインポート宣言が同じ翻訳単位にある場合、それらは同じヘッダーユニットをインポートする。
    3. それ以外の場合、同じヘッダーユニットをインポートするかどうかは未規定。[Note: これによって、インポート可能なヘッダで内部リンケージを持つエンティティの複数のコピーが存在しうる。]  
[Note: ヘッダ名を指定するモジュールインポート宣言（ヘッダーユニットのインポート宣言）もプリプロセッサによって認識され、（[cpp.import]で説明されているように）そのヘッダーユニットの翻訳フェーズ4の終了時点で定義されていたマクロが可視になる。]
4. ヘッダユニットのすべての宣言は暗黙にエクスポートされるが、内部リンケージを持つ名前の宣言は許可される。[Note: 複数の翻訳単位に現れる定義は、一般にそのような名前を参照できない]  
ヘッダーユニットは外部リンケージを持つ非`inline`の関数/変数定義を含んではならない。
5. インポート宣言がある翻訳単位`T`をインポートするとき、`T`でエクスポートされたインポート宣言（再エクスポート：`export import T2;`）によってインポートされているすべての翻訳単位もインポートされる。それらの翻訳単位は`T`によってエクスポートされている。  
さらに、あるモジュール`M`のあるモジュール単位内のインポート宣言が、`M`の別のモジュール単位`U`をインポートすると、`U`の本文内でエクスポートされないインポート宣言（普通のインポート宣言）によってインポートされたすべての翻訳単位をインポートする。  
（これらの規則により、１つのインポート宣言からさらに多くの翻訳単位がインポートされる可能性がある）
    - 2つ目の規定における`U`の本文内とは、`U`のグローバルモジュールフラグメントを含まない。すなわち、グローバルモジュールフラグメント内の`import`宣言（とそこからインポートされるもの）はその翻訳単位外から観測可能（到達可能）ではない。

#### 8
モジュール実装単位はエクスポートできない。  

```cpp
//Translation unit #1:
module M:Part;

//Translation unit #2:
export module M;
export import :Part;    // error: 再エクスポートしようとしてる:Part は実装単位（モジュール実装パーティション）
```

#### 9
モジュール`M`のモジュールパーティションではないモジュール実装単位は`M`（自分自身）を指定するインポート宣言を含んではならない。  
```cpp
module M;
import M;               // error: Mをそれ自身のモジュール単位でインポートできない
```

#### 10
次のいずれかの場合に、ある翻訳単位はある翻訳単位`U`に __インターフェース依存関係__（*interface dependency*）を持つ。  
ただし、翻訳単位は自分自身に対してインターフェース依存関係を持たない。
  1. `U`を暗黙的にインポートするモジュール宣言、又は`U`をインポートするモジュールインポート宣言が含まれている場合
  2. `U`にインターフェース依存関係を持つ翻訳単位にインターフェース依存関係を持つ場合

```cpp
//Interface unit of M1:
export module M1;
import M2;

//Interface unit of M2:
export module M2;
import M3;

//Interface unit of M3:
export module M3;
import M1;              // error: 循環的なインターフェース依存関係 M3→M1→M2→M3
```

### 10.4 Global module fragment [module.global.frag]
- global-module-fragment:
	- module-keyword `;` declaration-seq(opt)

[Note:翻訳フェーズ4より前では、ここのdeclaration-seqにはプリプロセッサディレクティブのみが現れる  
（すなわち、グローバルモジュールフラグメントにはプリプロセッサディレクティブしか現れてはならない）]

#### 2
global-module-fragmentは、モジュール単位の __グローバルモジュールフラグメント__（*global module fragment*）の内容を指定する。  
グローバルモジュールフラグメントを使用して、グローバルモジュールに属し（そのモジュールに属さず）、モジュール単位で使用可能な宣言を提供できる。

#### 3
次のいずれかの場合、宣言`D`は同じ翻訳単位内の宣言`S`から __宣言的に到達可能__（*decl-reachable*）である。
1. `D`は関数・関数テンプレートを宣言せず、`S`はid-expression、名前空間名、型名、テンプレート名、コンセプト名、のいずれかの命名`D`を含む。
2. `D`は`S`に現れる式によって指名されている関数・関数テンプレートを宣言している。
3. `S`が`postfix-expression( expression-list(opt) )`という形式の`E`を含むとき  
その`postfix-expression`が依存名を表すか、演算子が依存名を表す演算子式の場合、  
それぞれの型に依存する引数やオペランドを名前空間やエンティティに関連付けられていないプレースホルダ型の値に置き換えることで`E`から合成された式の中で、  
対応する名前を名前探索することによって`D`は`S`から見つかる。
    - `postfix-expression( expression-list(opt) )`とは、関数形式キャストや`static_cast`等のキャストや`typeid`式及び、それらの結果に対する演算子（`++,->`等）の適用
4. `S`にはターゲット型が依存するオーバーロードされた関数のアドレスを取る式が含まれており、そのオーバーロードの集合には`D`が含まれている。
5. `M`が`S`から宣言的に到達可能であり、次のいずれかに該当する名前空間定義ではない宣言`M`が存在する。
    - `D`は`M`から宣言的に到達可能である
    - `D`は`M`によって宣言されたエンティティを再宣言するか、`M`は`D`によって宣言されたエンティティを再宣言しており、かつ`D`はフレンド宣言でもブロックスコープ宣言でもない。
    - `D`は名前空間`N`を宣言しており、`M`は`N`のメンバーである
    - `M`と`D`のどちらか一方はクラステンプレート`C`を宣言しており、もう一方は`C`のメンバーまたはフレンドを宣言している
    - `M`と`D`のどちらか一方は列挙型`E`を宣言しており、もう一方は`E`のメンバである列挙子を宣言している
    - `D`は関数・変数を宣言し、`M`は`D`内部で宣言されている（この場合の宣言は変数の初期化子内のラムダ式内部に現れることができる）
    - `M`と`D`のどちらか一方はテンプレートを宣言しており、もう一方はそのテンプレートの部分特殊化・明示的特殊化・明示的インスタンス化・暗黙インスタンス化のいずれかを宣言している
    - `M`と`D`のどちらか一方はクラス・列挙型を宣言しており、もう一方はその型の`typedef`名を導入している（リンケージを目的として）

ただし、上記決定は以下のことを指示するものではない  
1. エイリアス宣言、`typedef`宣言、`using`宣言、名前空間エイリアス宣言、への参照が上記決定の前に指定した宣言に置き換えられるかどうか
2. 依存型を示さず、そのテンプレート名がエイリアンテンプレートを指定するsimple-template-idが、上記決定の前に指定した型に置き換えられるかどうか
3. 依存型を示さない`decltype`指定が、上記決定の前にその示す型に置き換えられるかどうか
4. 値に依存しない定数式が、上記決定の前にその定数評価の結果に置き換えられるかどうか

（これら4つの事は、4つのいずれかに該当するものを`E`とすると、`E`が最終的な結果に評価（置換）されるのと、`E`が*decl-reachable*であると決定されるのと、どちらが先に行われるかを実装定義とするということを意味する。  
後で例として出てくる、配列の添え字に指定された定数式が*decl-reachable*であるかは未規定というのはここの記述4による。）

#### 4

グローバルモジュールフラグメント内の宣言`D`は、その翻訳単位内のどの宣言からも宣言的に到達可能ではないとき、__破棄される__（*discarded*）。  
[Note: 破棄された宣言は、たとえインスタンス化地点がモジュール単位の外側にあるテンプレートのインスタンス化時にモジュール単位がそのインスタンス化コンテキストに含まれていたとしても（インスタンス化経路上にあったとしても）、モジュール単位の外側で到達可能でも可視でもない。]

#### 5

```cpp
const int size = 2;
int ary1[size];                 // sizeがary1から宣言的に到達可能かどうかは未規定
constexpr int identity(int x) { return x; }
int ary2[identity(2)];          // identityがary2から宣言的に到達可能かどうかは未規定

template<typename> struct S;
template<typename, int> struct S2;
constexpr int g(int);

template<typename T, int N>
S<S2<T, g(N)>> f();             // S, S2, g, ​::は全てf()から宣言的に到達可能

template<int N>
void h() noexcept(g(N) == N);   // g, ​::​ はh()から宣言的に到達可能
```

#### 6

```cpp
//Source file "foo.h":
namespace N {
  struct X {};
  int d();
  int e();
  inline int f(X, int = d()) { return e(); }
  int g(X);
  int h(X);
}
//Module M interface:
module;
#include "foo.h"  //グローバルモジュールフラグメント

export module M;
template<typename T> int use_f() {
  N::X x;                       // N​::​X, N, ​::​ はuse_­fから宣言的に到達可能
  return f(x, 123);             // N​::​f はuse_­fから宣言的に到達可能,
                                // N​::​e はuse_­fから間接的に宣言的に到達可能
                                // なぜなら、N::eはN::fから宣言的に到達可能なため
                                // N​::​d はuse_­fから宣言的に到達可能
                                // なぜなら、N::dもまた N​::​fから宣言的に到達可能なため
                                // ただし、N::dの呼び出しは使用されていない
}
template<typename T> int use_g() {
  N::X x;                       // N​::​X, N, ​::​ はuse_­gから宣言的に到達可能
  return g((T(), x));           // N​::​g はuse_­gから宣言的に到達可能ではない
                                //引数がTの依存名になってしまっているため、Tが確定しないと宣言的に到達可能にならない
}
template<typename T> int use_h() {
  N::X x;                       // N​::​X, N, ​::​ はuse_­hから宣言的に到達可能
  return h((T(), x));           // N​::​h はuse_­hから宣言的に到達可能ではない（use_gと同様）
                                // しかし、N​::​h はuse_­h<int>からなら到達可能（テンプレート引数Tが確定するため）
}
int k = use_h<int>();
  // use_­h<int> はkの宣言から宣言的に到達可能
  // すなわち、kの宣言からならばN​::​hは宣言的に到達可能
Module M implementation:
module M;
int a = use_f<int>();           // OK
int b = use_g<int>();           // error: 呼び出し可能なg()はみつからない。
                                // g()はモジュールMのインターフェース単位の本文内でどの宣言からも宣言的に到達可能ではないため
                                // module Mのインターフェース単位の終了とともに、g()の宣言は破棄された
                                //そのため、use_gは使用不可能
int c = use_h<int>();           // OK、use_h<int>()はモジュールMのインターフェース単位内でインスタンス化済
```

### 10.5 Private module fragment [module.private.frag]

- private-module-fragment:
  - `module : private;` top-level-declaration-seq (opt)
  
#### 1

プライベートモジュールフラグメント（private-module-fragment）はプライマリモジュールインターフェース単位にだけ表れる。 
private-module-fragmentを持つモジュール単位は、そのモジュールで唯一のモジュール単位となる。その診断は不要。

#### 2
[Note: プライベートモジュールフラグメントは、他の翻訳単位に影響を及ぼす可能性のある部分のモジュールインターフェース単位を終了する。プライベートモジュールフラグメントを使用すると、モジュールの全ての中身を`import`した翻訳単位から到達可能にすることなく（モジュールの必要な一部分だけを到達可能としながら）単一の翻訳単位としてモジュールを構成できる。

プライベートモジュールフラグメントの存在は次のものに影響を及ぼす

1. エクスポートされた`inline`関数の定義が必要とされるポイント
2. エクスポートされたプレイスホルダー戻り値型（後置されない`auto, decltype(auto)`）を持つ関数の定義が必要とされるポイント
3. 宣言が曝露していない事が求められるかどうか
4. `inline`関数やテンプレートの定義が現れるべき場所
5. 以前にプライベートモジュールフラグメントでインスタンス化されたテンプレートのインスタンス化コンテキスト
6. プライベートモジュールフラグメント内部の宣言の到達可能性

]

#### 3

プライベートモジュールフラグメントのサンプルコード

```cpp
export module A;
export inline void fn_e();      // error: エクスポートされたinline関数fn_e()は、プライベートモジュールフラグメントの開始前に定義されていない
inline void fn_m();             // OK, module-linkage inline function
static void fn_s();
export struct X;
export void g(X *x) {
  fn_s();                       // OK, 同じ翻訳単位のstatic関数の呼び出し
  fn_m();                       // OK, モジュールリンケージを持つinline関数の呼び出し
}
export X *factory();            // OK

module :private;
struct X {};                    // このモジュールAをインポートした側からは、このXの定義に到達可能ではない
X *factory() {
  return new X ();
}
void fn_e() {}
void fn_m() {}
void fn_s() {}
```


### 10.6 Instantiation context [module.context]
#### 1
__インスタンス化コンテキスト__（*instantiation context*）とは、ADLによってどの名前が可視となるか、および特定の宣言又はテンプレートのインスタンス化のコンテキストでどの宣言が到達可能となるか、を決定するプログラム内のある __地点__（*point*）の集合のこと（一箇所ではないことがある）。

#### 2
default指定されたクラスの特殊メンバ関数が暗黙的に定義されるとき、それにまつわるインスタンス化コンテキストは、クラス定義からのインスタンス化コンテキストと、特殊メンバ関数の暗黙定義のきっかけとなったプログラムの構文のインスタンス化コンテキストの和集合となる。

#### 3
あるテンプレートのインスタンス化地点がそれを囲んでいる別のテンプレートの特殊化の中にあり、その（囲まれている）テンプレートがそこで暗黙的にインスタンス化される時のインスタンス化コンテキストは、囲んでいるテンプレートの特殊化のインスタンス化コンテキストと（もしあれば）次の点との和集合。

テンプレートがモジュール`M`のインターフェース単位で定義され、インスタンス化地点が`M`のインターフェース単位内にない場合、そのインスタンス化地点は、`M`のプライマリーモジュールインターフェース単位のdeclaration-seqの最後の点（すなわち翻訳単位終端）（存在する場合、プライベートモジュールフラグメントの前）である。

#### 4
default指定された特殊メンバ関数の暗黙の定義中で参照されているために、暗黙にインスタンス化されているテンプレートのインスタンス化コンテキストは、そのdefault指定された特殊メンバ関数のインスタンス化コンテキストである（すなわち上記2）。

#### 5
（上記3, 4に当てはまらない）その他のテンプレート特殊化がインスタンス化される際のインスタンス化コンテキストは、そのテンプレートのインスタンス化地点を含む。

#### 6
（上記のいずれにも当てはまらない）その他のケースの場合の、プログラム内のある地点におけるインスタンス化コンテキストはその地点を含む。

#### 7
```cpp
//Translation unit #1:
export module stuff;

export template<typename T, typename U> void foo(T, U u) { auto v = u; }
export template<typename T, typename U> void bar(T, U u) { auto v = *u; }

//Translation unit #2:
export module M1;
import "defn.h";        // struct X {};の宣言と定義がある
import stuff;

export template<typename T> void f(T t) {
  X x;
  foo(t, x);
}

//Translation unit #3:
export module M2;
import "decl.h";        // struct X;の宣言のみがある
import stuff;

export template<typename T> void g(T t) {
  X *x;
  bar(t, x);
}

//Translation unit #4:
import M1;
import M2;

void test() {
  f(0);
  g(0);
}
```

`f(0)`の呼び出しは有効。`foo<int, X>`のインスタンス化コンテキストは次の地点を含んでいる。
- 翻訳単位#1の終端
- 翻訳単位#2の終端
- `f(0)`の呼び出し地点（翻訳単位#4の`test()`内）

このとき、クラス`X`の定義は到達可能である。

`g(0)`の呼び出しが有効かどうかは未規定。`bar<int, X*>`のインスタンス化コンテキストは次の地点を含んでいる。
- 翻訳単位#1の終端
- 翻訳単位#3の終端
- `g(0)`の呼び出し地点（翻訳単位#4の`test()`内）

このとき、クラス`X`の定義が到達可能である必要はない（翻訳単位#2の`import "defn.h";`によってインポートされた宣言は、推移的にインポートされた翻訳単位#4において到達可能となるかが未規定なため）。

### 10.6 Reachability [module.reach]
#### 1

次のどちらかの場合、ある翻訳単位`U`はある点`P`から __必ず到達可能__（*necessarily reachable*）である。

- `P`を含む翻訳単位が`P`より前にモジュールインターフェース単位`U`にインターフェース依存関係を持つ
- `P`を含む翻訳単位が`P`より前に`U`をインポートする

モジュールインタフェース単位はエクスポートされないインポート宣言を介して推移的にインポートされた時でも到達可能だが、そのようなモジュールインターフェース単位からの名前空間スコープ名は名前探索において可視ではない。

（エクスポートされないインポート宣言とは、普通のインポート宣言のこと。  
それを介した推移的なインポートとは、あるモジュール`M`で別のモジュール`N`をエクスポートせずインポートした状態で、また別の翻訳単位`U`で`M`をインポートしたときのこと。  
その時、`U`からは`M`のインポート宣言を介して`N`のインターフェースに到達可能となる、しかし可視ではない。）

#### 2
必ず到達可能なすべての翻訳単位は __到達可能__（*reachable*）である。  
プログラム内のある点でインターフェース依存関係を持つ追加の翻訳単位が到達可能とみなされるかどうか、およびどのような状態にあるかは未規定。  
（従って、実装はコンパイルに含まれる追加の翻訳単位の意味論的効果が観測されるのを防ぐ必要はない。）

[Note:移植性を持たせたいプログラムにおいては、追加の翻訳単位の到達可能性に依存するのは避けるべき。]

（ここでの追加の翻訳単位とは、インターフェース依存関係を持つが必ず到達可能ではない翻訳単位のこと。それはすなわち、推移的にインポートされている翻訳単位のこと。推移的にインポートされた翻訳単位はインターフェース依存関係が発生するが、必ず到達可能ではない。  
モジュールインターフェース単位は推移的にインポートにおいても到達可能となるとすぐ上で規定されている。しかしそうではない翻訳単位、すなわちヘッダーユニットとグローバルモジュールフラグメントは到達可能となるかは未規定）

#### 3
宣言`D`は次のそれぞれの場合に、インスタンス化コンテキスト内の任意の点`P`から到達可能となる
- `D`は同じ翻訳単位内にあり、`P`より前に現れる
- `D`は破棄されておらず、`P`から到達可能な翻訳単位に現れており、プライベートモジュールフラグメントに現れていないか、`P`を含むモジュールのプライベートモジュールフラグメントに現れている。

[Note: 宣言がエクスポートされているかは到達可能かどうかとは関係ない]

#### 4
あるエンティティのあるコンテキスト内で到達可能な全ての宣言の累積となるプロパティは、そのコンテキスト内におけるそのエンティティの振る舞いを決定する。

[Note: そのような到達可能な意味論的プロパティには、型の完全性、型定義、初期化子、関数・テンプレート宣言のデフォルト引数、属性、通常の名前探索におけるクラス・列挙型のメンバの可視性、などが含まれる。  
デフォルト引数は（その関数やテンプレートを）呼び出した式のコンテキストで評価されるため、対応する引数型の到達可能な意味論的プロパティがそのコンテキストにおいて適用される。]

```cpp
//ranslation unit #1:
export module M:A;  //モジュールインタフェースパーティションM:A
export struct B;

//Translation unit #2:
module M:B; //モジュールパーティションM:B

struct B {
  operator int();
};

//Translation unit #3:
module M:C; //モジュール実装パーティションM:C
import :A;  //モジュールインタフェースパーティションM:Aをインポート

B b1;                           // error: クラスBの定義は到達可能ではない
                                // M:AではBの宣言がエクスポートされているが、定義はM:Bにある
                                // モジュールパーティション間では暗黙的にインポートされないため翻訳単位#2にあるBの定義は到達不可能

//Translation unit #4:
export module M;    //モジュールMのプライマリーモジュールインターフェース単位
export import :A;
import :B;

B b2;               //ok. M:AもM:BもインポートしているのでBの定義は可視（到達可能）
export void f(B b = B());

//Translation unit #5:
module X;
import M;

B b3;                           // error: クラスBの定義は到達可能ではない
void g() { f(); }               // error: クラスBの定義は到達可能ではない
                                // クラスBの定義はM内部の実装パーティションにあり、エクスポートされているインターフェース（パーティション）単位にはない
                                // よって、Bの定義は到達不可能
```

#### 5
エンティティは名前探索で可視でなくても、到達可能な宣言を持つことができる。

```cpp
//Translation unit #1:モジュールA
export module A;

struct X {};
export using Y = X;

//Translation unit #2:モジュールB
module B;
import A;

Y y;                // OK, Xの定義は到達可能
X x;                // ill-formed: Xは被修飾名探索において可視ではない
```

### 11.3.9 Bit-fields [class.bit]

ビットフィールドは整数型または列挙型を持つものとし、ビットフィールドの意味論的プロパティはクラスメンバの型の一部ではない。

（ビットフィールド宣言・定義のもつ意味論的な効果は、その指定されているメンバ型とは無関係、ということ？）

### 11.4.1 Member functions [class.mfct]

#### 1

メンバ関数はそのクラス定義内で定義することができる。その場合、グローバルモジュールに属していれば`inline`メンバ関数となり、既に宣言されているがクラス定義内で定義されていなければ、クラス定義の外側で定義することができる。

[Note: メンバ関数は`inline/constexpr/consteval`と宣言されている場合も`inline`メンバ関数となる。]

### 11.9.3 Friends [class.friend]

#### 6

クラスの`friend`宣言で関数を定義出来るのは、そのクラスが非ローカルクラスであり、関数名が修飾されておらず、その関数が名前空間スコープを持つ場合のみ。

```cpp
class M {
  friend void f() { } // Mのfriendであるグローバルf()の定義であって、メンバ関数の定義ではない
};
```

#### 7

その様な関数は、グローバルモジュールに属していれば暗黙`inline`となる。クラス定義内で定義された`friend`関数は、それが定義されているクラスの（*lexical*）スコープ内にある。クラス定義の外側で定義された`friend`関数はそうではない。

### 12.5.8 User-defined literals [over.literal]
意訳：ユーザー定義リテラルはモジュールリンケージを持つことができる！

# 13 Templates [temp]
- template-declaration:
	- template-head declaration
	- template-head concept-definition
- template-head:
	- template < template-parameter-list > requires-clause(opt)


テンプレート宣言（template-declaration）は名前空間スコープ・クラススコープにおける宣言として現れることができる。  
その宣言（template-headに続くdeclaration）は、エクスポート宣言（export-declaration）であってはならない。

（`export template<typename T> ...`というのができないと言っているのではなく、`template<typename T> export ...`という宣言ができないと言っている）

## 13.1 Preamble [temp.pre]

関数テンプレート、クラステンプレートのメンバ関数、変数テンプレート、クラステンプレートの静的メンバ変数、の定義は、対応する特殊化がある翻訳単位で明示的インスタンス化されていない限り、暗黙的にインスタンス化されている全ての定義領域（*definition domain*）の終端から到達可能でなければならない。この診断は不要。

### 13.8.3.4 Value-dependent expressions [temp.dep.constexpr]

#### 2

*id-expression*は次のいずれかの場合に、値に依存している（*value-dependent*）

- 略
- 現在のインスタンス化の依存メンバである静的メンバ関数を指名（*names*）する場合
- 略

### 13.8.4.1 Point of instantiation [temp.point]
#### Delete paragraph 12.7.4.1/7:
インスタンス化コンテキスト（instantiation context）の定義がモジュールの項に移り、内容も変更されたため削除。

#### 1
関数テンプレート・メンバ関数テンプレートの特殊化、クラステンプレートのメンバ関数もしくは静的メンバ変数の特殊化（1つ目）が、別のテンプレートの特殊化（2つ目）から参照されているために暗黙的にインスタンス化されており、その特殊化（1つ目）が参照されるコンテキストがテンプレートパラメータに依存しているとき、（1つ目の）特殊化のインスタンス化地点はそれを囲む特殊化（2つ目）のインスタンス化地点である。

そうでない場合、そのような特殊化（1つ目）のインスタンス化地点は、その特殊化（1つ目）を参照する名前空間の宣言・定義の直後の地点。

（例えば、1つ目の特殊化がある非テンプレート関数内で参照されたとき、その関数を囲む名前空間の終わりの地点がインスタンス化地点になる。また、テンプレートな関数内でも、その1つ目の特殊化がインスタンス化される際にその関数のテンプレート引数に非依存ならば同様。  
テンプレート引数に依存している場合は、その関数テンプレートのインスタンス化地点が1つ目の特殊化のインスタンス化地点となる。）

#### 2
クラステンプレートのメンバ関数もしくはメンバ関数テンプレートが、それら関数のデフォルト引数の定義を使用する形で呼び出されたとき、そのデフォルト引数のインスタンス化地点は、そのようなメンバ関数もしくはメンバ関数テンプレートのインスタンス化地点。

（デフォルト引数とはおそらく、テンプレートのデフォルト引数も含む。定義を使用する形で呼び出された時というのは、デフォルト引数をodr-usedする形で使用して呼ばれたときという事。  
ただし、不完全型のポインタのように呼び出しに際してその定義を使用しない場合もあり得る。）

#### 3
関数テンプレートの特殊化、クラステンプレートのメンバ関数の特殊化に指定された`noexcept`指定子は、その`noexcept`指定子が別のテンプレートの特殊化で必要とされ、そのコンテキストがテンプレートパラメータに依存するために暗黙的にインスタンス化される場合、その`noexcept`指定子のインスタンス化地点はそれを必要とした特殊化（2つ目）のインスタンス化地点。

そうでない場合、そのような`noexcept`指定子のインスタンス化地点は、その`noexcept`指定子を必要とする名前空間の宣言・定義の直後の地点。

（おそらく、`noexcept(cond)`の形のものの事を言っていると思う。`cond`に指定された式のインスタンス化地点が上記のように決まる、）

#### 4
クラステンプレートの特殊化、クラスのメンバテンプレートの特殊化、またはクラステンプレートの内部クラスの特殊化（1つ目）が、別のテンプレートの特殊化（2つ目）から参照されているために暗黙的にインスタンス化されるとき、特殊化（1つ目）が参照されるコンテキストがテンプレートパラメータに依存し、かつ囲むテンプレートのインスタンス化前に特殊化（1つ目）がインスタンス化されていない場合、特殊化（1つ目）のインスタンス化地点はそれを囲むテンプレートのインスタンス化地点の直前。

そうでない場合、そのような特殊化（1つ目）のインスタンス化地点は、その特殊化（1つ目）を参照する名前空間スコープの宣言・定義の直前の地点。

#### 5
仮想関数が暗黙的にインスタンス化される場合、そのインスタンス化地点はそれを囲む（その仮想関数が属する）クラステンプレートの特殊化のインスタンス化地点の直後。

#### 6
明示的インスタンス化の定義は、明示的インスタンス化によって指定されたテンプレートの特殊化、又は（そこに含まれる特殊化も含めた）複数の特殊化、のためのインスタンス化地点でもある。

#### 7
関数テンプレート、メンバ関数テンプレート、クラステンプレートのメンバ関数もしくは静的メンバ変数は、上記のインスタンス化地点に加えて、翻訳単位内に複数のインスタンス化地点を持つことができる。
- それらの特殊化が、翻訳単位のdeclaration-seq内（存在する場合はプライベートモジュールフラグメントの前）にインスタンス化地点を持つ場合、そのdeclaration-seqの後の点（終端の次）もそのインスタンス化地点とみなされる。
  - （翻訳単位のdeclaration-seq内にインスタンス化地点を持つということは、実質プライベートモジュールフラグメントの外側にインスタンス化地点を持つということ。その場合プライベートモジュールフラグメント直前か、なければ翻訳単位の終端にインスタンス化地点を持つ。ということ）
- それらの特殊化が、プライベートモジュールフラグメント内部にインスタンス化地点を持つ場合、その翻訳単位の終端もインスタンス化地点とみなされる。

クラステンプレートの特殊化は、翻訳単位内に最大1つのインスタンス化地点を持つ。  
任意のテンプレートの特殊化は、複数の翻訳単位にインスタンス化地点を持つことがある。  
テンプレートの特殊化の、2つの異なるインスタンス化地点がODRに従って、その特殊化に異なる意味を与える場合、プログラムはill-formd。しかし、診断は不要。

### 13.7.4.2 Candidate functions [temp.dep.candidate]
`postfix-expression`が依存名である関数呼び出しの場合、候補関数はテンプレート定義コンテキストから通常の名前探索を用いて探索される。  
[Note:関連する名前空間を用いた探索（ADL）のパートについては、ADLの項で説明されているように、テンプレートのインスタンス化コンテキストにある関数宣言がADLによって探索される。]  
（そのような呼び出し時の）ADLにおいて、テンプレート定義およびインスタンス化コンテキストで見つかった宣言だけでなく、すべての翻訳単位の名前空間に導入された外部リンケージをもつすべての関数宣言が考慮され、呼び出しがill-formedであるか、より良い一致が見つかった場合、プラグラムは未定義動作。

#### 2

```cpp
//Source file "X.h":
namespace Q {
  struct X { };
}

//Source file "G.h":
namespace Q {
  void g_impl(X, X);
}

//Module interface unit of M1:
module;  //グローバルモジュールフラグメント

#include "X.h"  //Q::Xの定義
#include "G.h"  //Q::g_implの宣言

export module M1;

export template<typename T>
void g(T t) {
  g_impl(t, Q::X{ });   //ここの定義コンテキストにおいてADLによってQ​::​g_­implが見つかる
                        //Q​::​g_­impl、Q::Xは破棄されない
}

//Module interface unit of M2:
module;

#include "X.h"

export module M2;
import M1;

void h(Q::X x) {
   g(x);                // OK
}
```

#### 3

```cpp
//Module interface unit of Std:
export module Std;

export template<typename Iter>
void indirect_swap(Iter lhs, Iter rhs)
{
  swap(*lhs, *rhs);     // このswapは被修飾名探索では見つからない、見つかるとしたらADLでのみ
}

//Module interface unit of M:
export module M;
import Std;

struct S { /* ...*/ };
void swap(S&, S&);      // #1

void f(S* p, S* q)
{
  indirect_swap(p, q);  // インスタンス化コンテキストを探索するADLを介して、 #1が見つかる
                        //indirect_swapはインスタンス化コンテキストにこの点とモジュール内の定義点を含む
                        //ここの点においてSに対するswapは可視であるのでindirect_swap内からのADLにおいても可視
}
```

#### 4

```cpp
//Source file "X.h":
struct X { /* ... */ };
X operator+(X, X);

//Module interface unit of F:
export module F;

export template<typename T>
void f(T t) {
  t + t;
}

//Module interface unit of M:
module;

#include "X.h"  //クラスXの定義とXに対する2項+の宣言

export module M;
import F;

void g(X x) {
  f(x);             // OK: モジュールFのf()がインスタンス化される
                    // Xのoperator+はインスタンス化コンテキストで可視である
                    // この場合はここのf(x)と呼びだしている点で可視
}
```

#### 5

```cpp
//Module interface unit of A:
export module A;

export template<typename T>
void f(T t) {
  cat(t, t);         // #1
  dog(t, t);         // #2
}

//Module interface unit of B:
export module B;
import A;

export template<typename T, typename U>
void g(T t, U u) {
  f(t);
}

//Source file "foo.h", インポート可能なヘッダではない:
struct foo {
  friend int cat(foo, foo);
};
int dog(foo, foo);

//Module interface unit of C1:
module;

#include "foo.h" // dog()は参照されないため破棄される

export module C1;
import B;

export template<typename T>
void h(T t) {
  g(foo{ }, t);  // g()の呼び出しはテンプレートパラメータTに依存している
                 // そのため、g()の呼び出しに際してのdog()の呼び出し（catも？）は参照されているとみなされない
}

//Translation unit:
import C1;

void i() {
  h(0);       // error: #2のdog()が見つからない
              // モジュールC1内でdog()は参照されなかったため、宣言は破棄された
}

//インポート可能なヘッダ "bar.h":
struct bar {
  friend int cat(bar, bar);
};

int dog(bar, bar);

//Module interface unit of C2:
module;

#include "bar.h" // "bar.h"をヘッダーユニットとしてインポート

export module C2;
import B;

export template<typename T>
void j(T t) {
  g(bar{ }, t);
}

//Translation unit:
import C2;

void k() {
   j(0);        // OK, dog()はインスタンス化コンテキスト内で見つかる:
                // C2のモジュールインターフェース単位の終端において、dog()の宣言は可視
}
```

### 13.9.2 Implicit instantiation [temp.inst]

#### 1

テンプレートの特殊化`E`は、`E`に対して到達可能な明示的インスタンス化の定義、明示的特殊化の宣言があるか、`E`に対して到達可能な明示的インスタンス化の宣言が存在し次のいずれでも無い場合、宣言された特殊化（*declared specialization*）である。

1. `inline`関数
2. 初期化しまたは戻り値から推定される型
3. 潜在的に定数（*potentially-constant*）の値
4. クラステンプレートの特殊化

[Note:インポートした側での暗黙的インスタンス化では、インポートされた側の内部リンケージ名を使用できない。]

#### 2

クラステンプレートの特殊化が宣言された特殊化（*declared specialization*）では無い限り、完全型のオブジェクトを必要とする文脈で特殊化が参照される場合や、クラス型の完全性がプログラムのセマンティクスに影響を与える場合、クラステンプレートの特殊化は暗黙的にインスタンス化される。

#### 4

クラステンプレートのメンバが宣言された特殊化（*declared specialization*）では無い限り、メンバの定義の存在が必要となる文脈で参照された時、またはメンバの定義の存在がプログラムのセマンティクスに影響を与える場合、メンバの特殊化は暗黙的にインスタンス化される。

特に、静的データメンバの初期化（および関連する副作用）は、静的データメンバの定義の存在を必要とする方法で静的データメンバが使用されない限りは発生しない。

#### 5

関数テンプレートの特殊化が宣言された特殊化（*declared specialization*）では無い限り、その特殊化が関数定義の存在を必要とする文脈で使用される場合、またはその定義の存在がプログラムのセマンティクスに影響を与える場合、関数テンプレートの特殊化は暗黙的にインスタンス化される。

フレンド関数定義から宣言がインスタンス化された関数は、関数定義の存在を必要とする文脈で使用される場合、またはその定義の存在がプログラムのセマンティクスに影響を与える場合、暗黙的にインスタンス化される。

明示的特殊化された関数、および明示的特殊化されたクラステンプレートのメンバ関数の呼び出しを除いて、関数テンプレートやクラステンプレートのメンバ関数のデフォルト引数は、デフォルト引数の値を必要とする文脈で関数が呼び出された時に暗黙的にインスタンス化される。

[Note:明示的インスタンス化されている`inline`関数は宣言された特殊化（*declared specialization*）では無い。その意図は、odr-usedされた時にも暗黙的にインスタンス化され関数本体のインライン化が考慮されるが、そのout-of-lineコピーは翻訳単位では生成されない、ということ。]

#### 7

変数テンプレートの特殊化が宣言された特殊化（*declared specialization*）では無い限り、その特殊化が変数定義の存在を必要とする文脈で参照される場合、またはその定義の存在がプログラムのセマンティクスに影響を与える場合、変数テンプレートは暗黙的にインスタンス化される。

変数テンプレートのデフォルトテンプレート引数は、変数テンプレートがデフォルト引数の値を必要とする文脈で参照されると、暗黙的にインスタンス化される。

### 13.9.3 Explicit instantiation [temp.explicit]

#### 10（削除）

~~`inline`関数・変数、初期化子や戻り値から型を推論する宣言、リテラル型の`const`変数、参照型の変数、およびクラステンプレートの特殊化を除いて、明示的インスタンス化の宣言は参照先のエンティティの暗黙的インスタンス化を抑制する効果がある。~~

~~[Note:この意図は、明示的インスタンス化されている`inline`関数はodr-usedされた時にも暗黙的にインスタンス化され関数本体のインライン化が考慮されるが、そのout-of-lineコピーは翻訳単位では生成されない、ということ。]~~

# 15 Preprocessing directives [cpp]

- preprocessing-file:
  - group (opt)
  - module-file
- module-file:
  - pp-global-module-fragment (opt) pp-module group (opt) pp-private-module-fragment (opt)
- pp-global-module-fragment:
  - `module ;` new-line group (opt)
- pp-private-module-fragment:
  - `module : private ;` new-line group (opt)
- group:  
  - group-part  
  - group group-part
- group-part:
  - control-line
  - if-section
  - text-line
  - `#` conditionally-supported-directive
- control-line:
	- `# include` pp-tokens new-line
	- pp-import
  - （以下略）

#### 1

__プリプロセッシングディレクティブ__（*preprocessing directive*）は次の制約を満たすプリプロセッシングトークンのシーケンスで構成される。

翻訳フェーズ4開始の時点で、シーケンスの最初のトークン（ディレクティブ導入トークン）は、ソースファイルの最初の文字として（改行文字を含まない任意個のホワイトスペースがあっても可）、または少なくとも1つの改行文字（new-line）を含むホワイトスペースに続いて現れており、かつ

1. `#`プリプロセッシングトークン
2. `import`プリプロセッシングトークン、同じ論理行の直後にheader-name、`<`、識別子、string-literal、`:`のいずれかのプリプロセッシングトークンが続くもの
3. `moudle`プリプロセッシングトークン、同じ論理行の直後に識別子、`:`、`;`のいずれかのプリプロセッシングトークンが続くもの
4. `export`プリプロセッシングトークン、同じ論理行の直後に2, 3のどちらかの形式のディレクティブが続くもの

シーケンスの最後のトークンは、（次の）シーケンスの最初のトークンであり、その直後には改行を含む空白文字が続く。  
（そのため、プリプロセッシングディレクティブは一般に「行」とよばれる。プリプロセス中の特定処理を除いて、全てのホワイトスペースは同等であるため、これらの「行」には他の構文上の意味はない）

[Note: 改行文字（new-line）は、意図せずに関数形式マクロ等の呼び出しの中に現われたとしても、プリプロセッシングディレクティブを終了させる]

```cpp
#                       // preprocessing directive
module ;                // preprocessing directive
export module leftpad;  // preprocessing directive
import <string>;        // preprocessing directive
export import "squee";  // preprocessing directive
import rightpad;        // preprocessing directive
import :part;           // preprocessing directive

module                  // not a preprocessing directive
;                       // not a preprocessing directive

export                  // not a preprocessing directive
import                  // not a preprocessing directive
foo;                    // not a preprocessing directive

export                  // not a preprocessing directive
import foo;             // preprocessing directive (ill-formed at phase 7)

import ::               // not a preprocessing directive
import ->               // not a preprocessing directive
```

#### 2

プリプロセッシングトークンのシーケンスは、ディレクティブ導入トークンで始まらない限り、text-lineにすぎない。

プリプロセッシングトークンのシーケンスは、上記構文定義の`#`の後に現れるディレクティブ名のいずれでも始まらない場合にのみ、conditionally-supported-directiveとなる。

#### 3

翻訳フェーズ4の開始時に、pp-global-module-fragmentのgroupにはtext-lineもpp-importも含まれてはならない。

#### 5
プリプロセッシングディレクティブ内（ディレクティブ導入トークンの直後から終端改行文字の直前までの間）のプリプロセッシングトークン間に現れる空白文字は、半角スペースと水平タブのみである。

（ディレクティブ導入トークンは1に書かれている3つのもののうちどれか）

#### 6
実装は、ソースファイルのセクションを条件付きで処理・スキップしたり、他のソースファイルをincludeしたり、ヘッダーユニットからマクロをインポートしたり、マクロを置換したりできる。  
これらの（プリプロセッサで）出来ることは、概念的には翻訳単位の翻訳（コンパイル処理）前に行われるため、__プリプロセッシング__（前処理 : *preprocessing*）と呼ばれる。

### 15.1 Conditional inclusion [cpp.cond]

- header-name-tokens:
	- string-literal
	- < h-pp-tokens >
- has-include-expression:
	- _­_­has_­include ( header-name )
	- _­_­has_­include ( header-name-tokens )

（string-literalは`#include "ヘッダ名"`の形式（`L, R`等の接頭辞を使用可能）、h-pp-tokensは各種リテラルを使用できるヘッダ名、`#include <iostream>`の形式）

#### 2
defined-macro-expressionは識別子がその時点でマクロとして定義されている場合に`1`（つまり、定義済みの場合、またはアクティブなマクロ定義（active macro definitions）がある場合。例えば、同じ識別子名を指定された`#undef`ディレクティブが介在していない`#define`ディレクティブに指定された識別子名であった場合など）、そうでない場合は`0`に評価される。

（defined-macro-expressionは、`defined マクロ名`、`defined(マクロ名)`のこと）

#### 3
has-include-expressionの2番目の形式は、最初の形式が一致しない場合にのみ考慮される。その場合、プリプロセッシングトークンは通常のテキストと同じように処理される。

### 15.2 Source file inclusion [cpp.include]

#### 7
header-nameで識別されるヘッダーがインポート可能なヘッダであるとき、そのプリプロセッサディレクティブが次の形式の`import`ディレクティブで置き換えられるかは実装定義。
- `import` header-name ; new-line

（header-nameとは""か<>で囲まれた文字列の事、ここでのプリプロセッサディレクティブは`#include header-name`を指す。すなわち、`#include`を`import`に置き換えることを意味する。この置換は実装定義）

### 15.4 Module directive [cpp.module]

- pp-module:
  - `export`(opt) `module` pp-tokens (opt) `;` new-line

#### 1

pp-moduleは、`module`または`export`（pp-moduleの最初のトークンである場合のみ）がオブジェクトマクロとして定義された識別子である文脈で現れてはならない。

#### 2

`module`ディレクティブ内の`module`プリプロセッシングトークンの後にあるプリプロセッシングトークンは、通常のテキストと同様に処理される。

[Note: そこでマクロ名として定義されている各識別子は、プリプロセッシングトークンの置換リストに置き換えられる]

#### 3

`module`と`export`（存在する場合）プリプロセッシングトークンは、それぞれmodule-keywordとexport-keywordに置き換えられる。

[Note: これにより、その行はプリプロセッシングディレクティブではなくなるため、翻訳フェーズ4の終了時に削除されない。]

### 15.3 Header unit importation [cpp.import]

- pp-import:
	- `export`(opt) `import` header-name pp-tokens(opt)`;` new-line
	- `export`(opt) `import` header-name-tokens pp-tokens(opt)`;` new-line
	- `export`(opt) `import` pp-tokens `;` new-line

#### 1

pp-importは、`import`または`export`（pp-importの最初のトークンである場合のみ）がオブジェクトマクロとして定義された識別子である文脈で現れてはならない。

#### 2

`import` control-lineの`import`プリプロセッシングトークンの後のプリプロセッシングトークンは通常のテキストと同様に処理される（つまり、その時点でマクロ名として定義されている各識別子は、プリプロセッシングトークンの置換リストによって置換される）。

[Note: pp-importの最初の2つの形式にマッチする`import`ディレクティブは、header-nameで指定されるヘッダーユニットからマクロをインポートするように、プリプロセッサーに指示する。]

pp-importによってインポートされるマクロのインポート点は、pp-importの最初の2つの形式ではそのpp-importを終了する改行（new-line）の直後の点。

pp-importの最後の形式は、最初の2つの形式がマッチしなかった時にのみ考慮され、マクロのインポート点を持たない。  
（この形式には、名前付きモジュールの`import`宣言がマッチする。それは次の規則によってimport-keywordに置換され、`import`宣言としてプリプロセス後に処理される。）

#### 3

module-fileのgroup処理中に、ソースファイルのインクルード（`#include`がインポート可能なヘッダを指定する時に行われる書き換えも含めて）によってpp-importが生成される場合、プログラムはill-formed。

#### 4

pp-importの3つの形式全てで、`import`と`export`（存在する場合）プリプロセッシングトークンは、それぞれimport-keywordとexport-keywordに置き換えられる。（これにより、モジュールとしての処理はプリプロセス後にヘッダーユニット等の区別なく実行される。）

[Note: これにより、その行はプリプロセッシングディレクティブではなくなるため、翻訳フェーズ4の終了時に削除されない。]

さらに、pp-importの2つ目の形式では、header-name-tokensが`#include`ディレクティブのpp-tokensであるかのように、header-nameトークンが生成される。  
そして、header-name-tokensは（生成された）header-nameトークンに置き換えられる。  
[Note:これにより、インポートはプリプロセッサ及びその後の翻訳フェーズで（１つ目の形式として）一貫して処理される。]

#### 5

プログラムの各翻訳単位のプリプロセス時に現れた`#define`ディレクティブは、それぞれ個別の __マクロ定義__（*macro definition*）である。

[Note: 事前定義されるマクロ名は`#define`ディレクティブで導入されない。追加で任意のマクロを事前定義する方法（コマンドライン引数など）を提供する処理系は、それらを`#define`で導入されたものとして扱わない事が推奨される。（すなわち、ヘッダーユニットからのマクロのエクスポートにおいて、それらの事前定義マクロはエクスポートされない。もしくはしない事が推奨される）]

ヘッダーユニットからマクロをインポートすると、その翻訳単位（その翻訳単位におけるヘッダーユニット）からのマクロ定義が、他の（インポートした）翻訳単位において可視となる（使えるようになる）。

それぞれのマクロ定義は、次のように各翻訳単位において最大1つの定義点及び未定義点をもつ。
- ある翻訳単位内においてのマクロ定義の __定義点__（*point of definition*）は次のどちらか。
  - その`#define`ディレクティブが現れる点（`#define`ディレクティブを含む翻訳単位内）
  - マクロ名がキーワード・`module`・`import`と字句的に同一でない場合、マクロ定義の定義点があればそれを含む翻訳単位の最初のマクロのインポート地点（ヘッダーユニットをインポートした他の翻訳単位内）。
- ある翻訳単位内においてのマクロ定義の __未定義点__（*point of undefinition*）は次のどちらか。
  - その定義点の後にマクロを命名する`#undef`ディレクティブが現れる最初の点
  - マクロ定義の未定義点がある場合、先に現われた未定義点を含む翻訳単位の最初のマクロのインポート地点。

（どちらのケースも、1つ目の条件はマクロを直接`define・undef`する翻訳単位においての点の事を言っており、2つ目の条件はマクロを記述したヘッダーユニットをインポートする翻訳単位においての点の事を言っている。  
定義点の2番目の条件の冒頭は、マクロ名がキーワード及び`module import`と同じではならないという事と思われる）

#### 4
マクロディレクティブがソースのある場所で __アクティブ__（*active*）となるのは、その場所より前にその翻訳単位における（そのマクロディレクティブの）定義点があり、かつ同様に未定義点が無い場合。

#### 5
マクロは置換されるか再定義され、そのマクロ名に対して複数のマクロ定義がアクティブとなっているとき、アクティブなマクロ定義は全て同じマクロの有効な再宣言でなければならない。  
[Note: pp-import間の相対的な順序は、特定のマクロ定義がアクティブかどうかとは関係ない。]

#### 6

```cpp
//インポート可能なヘッダ "a.h":
#define X 123   // #1
#define Y 45    // #2
#define Z a     // #3
#undef X        // a.hにおける#1の未定義点

//インポート可能なヘッダ "b.h":
import "a.h";   // b.hにおける、#1,#2,#3の定義点、#1の未定義点（正確にはセミコロンの後ろ）

#define X 456   // OK, #1はアクティブでないため、新しいマクロXの定義が可能
#define Y 6     // error: #2はアクティブなため、定義をするなら同じ内容にならなければならない

//インポート可能なヘッダ "c.h":
#define Y 45    // #4
#define Z c     // #5

//インポート可能なヘッダ "d.h":
import "a.h";   // d.hにおける、#1,#2,#3の定義点、#1の未定義点
import "c.h";   // d.hにおける、#4,#5の定義点

int a = Y;      // OK, アクティブなマクロ定義#2と#4、#4はYの有効な再定義
int c = Z;      // error: クティブなマクロ定義#3と#5、#5はZの有効な再定義ではない
```

### 16.5.1.2 Headers [headers]
#### 4
表19にリストアップされているヘッダ（フリースタンディング処理系の場合は実装によって提供されるそれらの一部となるヘッダ）は、まとめて __インポート可能なC++ライブラリヘッダ__（*importable C++ library headers*）と呼ばれる。

```cpp
import <vector>;      // <vector>ヘッダーユニットをインポート

std::vector<int> vi;  // OK
```

### 16.5.2.2 Headers [using.headers]
（ここでは、C++プログラムがC++標準ライブラリの機能にアクセスする方法を説明している）

#### 1
C++標準ライブラリのエンティティはヘッダで定義されており、適切な`#include`プリプロセッシングディレクティブ又は`import`宣言がなされていれば、その翻訳単位で使用できる。

#### 3
翻訳単位は、宣言又は定義の外側にのみヘッダを含め（モジュール単位の場合はグローバルモジュールフラグメント内にのみヘッダを含め）、それらのヘッダ内エンティティのその翻訳単位での最初の参照の前に、ヘッダをインクルードするか、対応するヘッダーユニットをインポートする。その診断は不要である。

### 16.5.4.2.3 Namespaces for future standardization  [namespace.future]

名前空間名が`std`とそれに続く1つ以上の数字で構成される最上位の名前空間は、将来の標準化のために予約されている。

[Example: 最上位の名前空間`std2`はこの国際標準の将来の改訂版で使用されるために予約されている。]

## Annex C (informative) Compatibility [diff]

### C.4.7 [library]: library introduction [diff.cpp14.library]

#### 2
Affected subclause: [namespace.future]  
Change: 新たな予約済み名前空間  
Rationale: これを用いなければ既存のプログラムと互換性がない可能性のある標準ライブラリの将来のリビジョンのために名前空間を予約する  
Effect on original feature: グローバルな名前空間`std`とそれに続く1つ以上の数字列は、将来の標準化のために予約される。これに該当するような最上位の名前空間（例えば、`std2`）を使用するC++14で有効なコードは、この国際規格（C++20）では無効になる場合がある。

### C.5.1 [lex]: lexical conventions [diff.cpp17.lex]

Affected subclause: [lex.header]   
Change: header-nameトークンはより多くのコンテキストで生成される  
Rationale: 新機能に必要  
Effect on original feature: 識別子`import`の後に`<`が続くと、header-nameトークンが形成されることがある。
```cpp
template<typename>
class import {};

import<int> f();                // ill-formed;（ヘッダーユニットのインポート宣言として解釈され、エラー） 以前は有効だった
::import<int> g();              // OK
```

### C.1.2 [lex]: lexical conventions [diff.cpp17.lex]

Affected subclauses: [lex.pptoken], [module.unit], [module.import], [cpp.pre], [cpp.module], and [cpp.import]  
Change: 特別な意味を持つ新しい識別子  
Rationale: 新機能に必要  
Effect on original feature: `module`または`import`で始まる論理行は、この国際規格（C++20）では解釈が異なることがある。
```cpp
class module {};
module m1;        // 以前は変数宣言、現在はモジュール宣言
module *m2;       // OK

class import {};
import j1;          // 以前は変数宣言、現在はインポート宣言
::import j2;        // 変数宣言
```

### C.5.4 [dcl.dcl]: declarations[diff.cpp17.dcl.dcl]
#### 1
Affected subclause: [dcl.typedef]  
Change: リンケージ目的で`typedef`名を持つ無名クラスには、C互換の構成のみを含めることができる。  
Rationale: 実装可能性のために必要  
Effect on original feature: C++17では有効だったコードが、この国際標準（C++20）では正しくない場合がある。

```cpp
typedef struct {
  void f() {} // ill-formed; 以前はwell-formed
} S;
```

#### 2
Affected subclause: [dcl.fct.default]  
Change: 関数は異なる翻訳単位で異なるデフォルト引数を持つことができない。
Rationale: モジュールサポートのために必要  
Effect on original feature: C++17では有効だったコードが、この国際標準（C++20）では正しくない場合があり、それについての診断は不要。

```cpp
// 翻訳単位1
int f(int a = 42);
int g() { return f(); }

// 翻訳単位2
int f(int a = 76) { return a; } // ill-formed (診断は不要); 以前はwell-formed
int g();

int main() {
  return g(); // 42を返すために使用
}
```

## Annex D (normative) Compatibility features [depr]

### D.8 Non-local use of TU-local entities [depr.local]

曝露（*exposure*）している非TU-localエンティティの宣言は非推奨。

[Note: そのような宣言は、インポート可能なモジュール単位ではill-formed。]

```cpp
namespace {
  struct A {
    void f() {}
  };
}

A h();                      // 非推奨 : h()は内部リンケージでは無い
inline void g() {A().f();}  // 非推奨 : g()はinlineかつ内部リンケージでは無い
```