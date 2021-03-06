# ［C++］モジュールとプリプロセス

C++20より使用可能になるはずのモジュールは3つの新しいキーワードを用いて記述されますが、それらのキーワードは必ずしも予約語ではなく、コンパイラによる涙ぐましい努力によって特殊な扱われ方をしています。

[:contents]

たとえば、全部入りを書くと次のようになります。

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

これはプリプロセス後（翻訳フェーズ4の後）に、おおよそ次のようになります。

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

これは実際には実装定義なのでどう置き換えられるのかは不明ですが、これら置換されている`module, import, export`トークンの現れていた所とその行は実はプリプロセッシングディレクティブとして処理され、その結果としてこのような謎のトークンが生成されます。そして、C++のコードとしてはこれらの謎のトークンによるものをモジュール宣言やインポート宣言などとして扱います。

逆に、これらのプリプロセッシングディレクティブによって導入されるトークン置換後の宣言のみが、モジュール宣言やインポート宣言などとして扱われ、それ以外にそれらを直接記述する方法はありません。

何でこんなことをしているのかというと、ひとえに依存関係の探索を高速にするためです。

当初のモジュール宣言やインポート宣言はプリプロセス後にC++のコードとしての意味論の下で認識され、そこでようやくそのファイルがモジュールであるのか、またその依存関係を把握することができます。つまり、依存関係をスキャンしようとすればC++コードをある程度コンパイルせねばなりません。

対して、現在のC++における依存関係スキャンは相手にするのが`#include`だけなのでプリプロセスさえ行えば依存関係を把握可能です。C++コンパイラは必要なく、プリプロセッシングディレクティブ以外の行は無視することができます。当然、こちらの方が圧倒的に高速かつ簡単です。

依存関係の把握はモジュールのビルドに関わってくる重要な問題であり、依存関係スキャンを高速に行えればプログラム全体のビルド時間を短縮できます。また、`#include`に対して不利な点が増えればユーザーのモジュールへの移行を妨げてしまう事にもなりかねません。

そのため、モジュール宣言やインポート宣言をプリプロセッシングディレクティブによってのみ導入することでプリプロセスの段階でそれらの宣言を識別可能にし、`#include`と同様にプリプロセスさえ行えば依存関係スキャンが可能かつ、プリプロセッシングディレクティブ以外の行を考慮しなくてもよくなるように変更されました。

また、両方ともマクロ展開よりも前に処理されるためマクロによって導入することができません（その名前は導入可能）。また、モジュール宣言は`#if`系ディレクティブよりも前に処理されるため、あるファイルがモジュールであるかどうかをマクロによって切り替えることもできません。これらのことによって結果的に、完全なプリプロセスを必要とせずにソースファイルの依存関係をスキャンすることができるようになっています。

ちなみに、VS2019 update5でMSVCはこれらのことを実装しているようです。

### ディレクティブ導入トークン

ディレクティブ導入トークンはプリプロセッシングディレクティブを導入するトークン（文字列）です。従来のプリプロセッシングディレクティブでは、ある行の最初の非空白文字が`#`で始まる行がディレクティブ導入トークンとして扱われていました。そこに次の3つが追加され、新しいプリプロセッシングディレクティブとして扱われるようになります。

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

このディレクティブ導入トークンに該当するトークンで始まる行はプリプロセッシングディレクティブとして扱われ、対応する形式のプリプロセッシングディレクティブがあれば処理されます。もし対応するディレクティブが存在しない場合はコンパイルエラーとなります。

このディレクティブ導入トークンとしてみなされなかった`module, import, export`トークンは通常の識別子として処理されます。このため、`module, import`はクラス名や変数名に使用できます（注意は必要ですが）。`export`は元々予約語のため使用できません。

### モジュールディレクティブ

モジュールディレクティブはモジュール宣言を導入するためのプリプロセッシングディレクティブです。EBNFは次のような形式です。

```ebnf
export(opt) module pp-tokens(opt) ; new-line
```

スペースの空いているところは任意個数の空白文字を含む事ができますが改行は含まれまず、`(opt)`とあるのはあってもなくても良いやつです。改行が入って良いいのは行末（`new-line`）だけなので、モジュールディレクティブはセミコロンまで含めて1行で書く必要があります。

`pp-tokens`はマクロによって置換される必要のあるトークン列を表していて、モジュール名が来る筈です。すなわち、モジュール名はマクロによって導入できます。また、`(opt)`とはありますが名前が無い場合はプリプロセスの後、C++構文解析時にコンパイルエラーになります。

このディレクティブの効果は、ディレクティブ中の`export`と`module`トークンを実装定義の`export-keyword`と`module-keyword`に置換します。これによってこの行はプリプロセッシングディレクティブではなくなるため翻訳フェーズ4の終わりに削除されず、あとでモジュール宣言として処理されます。

```cpp
// OKな例
export module module_name;

module module_name;

module module:part:partition_name;  // モジュールパーティションの宣言

export   module /*コメントは1つの空白と見なされるので間に入っても良い*/ module_name;

// NG例
export module;  // プリプロセスよりあとでコンパイルエラー

module 1module; // 通常の識別子同様、数字で始まってはならない

export
module
module_name;  // 1行で書く

module module_name
;
```

#### フラグメント導入ディレクティブ

`module`トークンはさらにグローバルモジュールフラグメントとプライベートモジュールフラグメントの2つの領域を導入します。それぞれEBNFは次のように定義されています。

```ebnf
// グローバルモジュールフラグメント
module ; new-line group(opt)

// プライベートモジュールフラグメント
module : private ; new-line group(opt)
```

`group`には任意のコード列が入ります。`(opt)`とはありますが空になる事はほぼないでしょう。

これらのものもセミコロンまで含めて1行で書く必要があります。ディレクティブとしての効果はモジュールディレクティブと同様に、含まれる`module`トークンを`module-keyword`に置換します。`private`はそのままです。

#### モジュールファイルの識別

翻訳フェーズ4の開始時にプリプロセッシングディレクティブのパースを行う際、コンパイラはまず1行目が上記グローバルモジュールフラグメント導入ディレクティブかモジュールディレクティブのどちらかであるかによって現在のファイルがモジュールファイルであるのか通常のソースファイルであるのかを識別します。

上記モジュールディレクティブとフラグメント導入ディレクティブが処理されるのはモジュールファイルの中だけです。また、それらのディレクティブは正しく一回づつしか現れてはなりません。`#if`等で条件付きで導入することもできません。

通常のファイルとして処理が開始された場合はモジュールディレクティブやフラグメント導入ディレクティブは現れてはならず、現れればコンパイルエラーとなります。

従って、グローバルモジュールフラグメント導入ディレクティブおよびそれが無い場合のモジュールディレクティブはいかなるディレクティブの後にも書く事ができません（ただし、空白列やコメントはあってもokです）。必ずファイルの先頭に来ていなければなりません。

グローバルモジュールフラグメントがある場合でも、`#include`や`#ifdef`等によって後続のモジュールディレクティブが導入されることはありません。これがなされた場合、コンパイルエラーとなります。

これらのことはEBNFとして表現され規定されています。

### インポートディレクティブ

インポートディレクティブはインポート宣言を導入するためのプリプロセッシングディレクティブで、EBNFは次のようになります。

```ebnf
export(opt) import header-name pp-tokens(opt) ; new-line
export(opt) import header-name-tokens pp-tokens(opt) ; new-line
export(opt) import pp-tokens ; new-line
```

インポートディレクティブもセミコロンまで含めて1行で書かなければなりません。最初の2つはヘッダユニットのインポートに対応し、3つ目の形式がモジュールのインポートに対応します。これもまた、インポート対象のモジュール名やヘッダ名をマクロによって導入できます。

このディレクティブの効果はディレクティブ中の`export`と`import`トークンを実装定義の`export-keyword`と`import-keyword`に置換します。その後でインポート宣言として処理されます。  
加えて最初の2つの形式では、指定されたヘッダ名に対応するヘッダユニットからマクロをインポートします。インポートされたマクロはディレクティブの末尾の改行の直後で定義されます。

```cpp
// ok
import <vector>;
export import "mayhaader.hpp";
import module_name;
import module:part:partition;
import :partition;

// ng
export
import
module_name;  // 1行で書く

import <iostream>
;

export
import module_name; // プリプロセスよりあとでコンパイルエラー
```

なお、インポートディレクティブは`import`あるいは`export`がオブジェクトマクロ名として登録されているコンテキストで現れた場合コンパイルエラーになります。

```cpp
import <vector>;  // この時点ではok

#define import export import

import <iostrema>; // error!
```

### サンプルコード

#### OKな例

```cpp
module;
#define m x
#define im anoter:module
export module m;  // モジュール名をマクロ展開するのはok

import im;  // モジュール名やヘッダ名をマクロ展開するのはok
```

```cpp
// これらはプリプロセッシングディレクティブとして扱われない

::import x = {};
::module y = {};

import::inner xi = {};
module::inner yi = {};

void f(Import *import) {
  import->doImport();
}
```

#### ダメな例

```cpp
// このファイルは常に非モジュールファイルとして扱われる
#ifdef INCLUDE_GUARD
#define INCLUDE_GUARD

export module mymodule; // モジュールディレクティブではない、コンパイルエラー

#endif
```

```cpp
module;
#if FOO
export module foo;  // ここではモジュールディレクティブとみなされない、コンパイルエラー
#else
export module bar;  // ここではモジュールディレクティブとみなされない、コンパイルエラー
#endif
```

```cpp
module;
#define EMPTY
EMPTY export module m;  // モジュールディレクティブではない、コンパイルエラー
                        // モジュール名以外の部分はマクロがあってはならない
```

```cpp
export module m;

#ifdef COND_PRIVATE
module : private; // プライベートモジュールフラグメント導入ディレクティブとみなされない、コンパイルエラー
#endif
```

予めコンパイラオプションで`-Dm="export module x;"`などとしていたとして

```cpp
m // モジュールディレクティブではない、マクロ展開後コンパイルエラー
```

```cpp
module y = {};  // ファイル先頭にあるとモジュールディレクティブとしてみなされる
                // プリプロセス後にコンパイルエラー
```

```cpp
namespace N {
  module a; // モジュールディレクティブではないが、プリプロセッシングディレクティブと認識される、コンパイルエラー
  import b; // インポートディレクティブ、プリプロセス後にコンパイルエラー
            // インポート宣言は他のあらゆる宣言の内部に来てはならないため
}
```

### 参考文献

- [P1857R3 Modules Dependency Discovery](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1857r3.html)
- [P1703R1 Recognizing Header Unit Imports Requires Full Preprocessing](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1703r1.html)
- [15 Preprocessing directives [cpp] - N4861](https://timsong-cpp.github.io/cppwp/n4861/cpp)
- [C++ Modules conformance improvements with MSVC in Visual Studio 2019 16.5 - C++ Team Blog](https://devblogs.microsoft.com/cppblog/c-modules-conformance-improvements-with-msvc-in-visual-studio-2019-16-5/)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20200515_module_preprocess.md)
