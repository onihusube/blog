# ［Meson］Meson for C++の苦闘記

MesonでC++プロジェクトをクロスプラットフォームにビルドできるようにしたときのメモです。C++以外の事は分かりません・・・

### 基本

基本的なビルドスクリプトは以下のようになります。

```meson
# 必ずproject()から始める
project('test_project', 'cpp', default_options : ['warning_level=3', 'werror=true', 'cpp_std=c++17'], meson_version : '>=0.50.0')

# インクルードディレクトリ指定
include_dir = include_directories('include', 'oher/include')

# 実行可能ファイルを出力
executable('test_project', 'test.cpp', include_directories : include_dir)
```

- [Mesonの基本構文](https://mesonbuild.com/Syntax.html)
- [Mesonの関数リファレンス](https://mesonbuild.com/Reference-manual.html)
- [アレはMesonでどうやるの？的なtips](https://mesonbuild.com/howtox.html)

### コンパイラを検出する

- [Use an argument only with a specific compiler](https://mesonbuild.com/howtox.html#use-an-argument-only-with-a-specific-compiler)

`meson.get_compiler('cpp')`でコンパイラオブジェクト？を取得して、そこから`get_id()`でコンパイラ文字列を取得します。  
あとは`if`で分岐するだけです。

```meson
if cppcompiler == 'msvc'
# msvc用の処理
elif cppcompiler == 'gcc'
# gcc用の処理
elif cppcompiler == 'clang'
# clang用の処理
endif
```

ちなみに、コンパイルオプションを主要3コンパイラで分けたいだけならば、`get_argument_syntax()`を使うと便利です。これによって得られる文字列は、オプションの互換性があるコンパイラで同一になります。

```meson
project('test_project', 'cpp', default_options : ['warning_level=3', 'werror=true', 'cpp_std=c++17'], meson_version : '>=0.50.0')
cppcompiler = meson.get_compiler('cpp').get_argument_syntax()

if cppcompiler == 'msvc'
    # MSVC,clang-cl,icc(windows)用
    options = ['/std:c++latest']
elif cppcompiler == 'gcc'
    # gcc,clang,icc(linux)用
    options = ['-std=c++2a']
else
    # その他
    options = []
endif

include_dir = include_directories('include', 'oher/include')

executable('test_project', 'test.cpp', include_directories : include_dir, cpp_args : options)
```

例えばこうしておくと、それぞれのコンパイラで言語バージョンの指定ができます。  
（ただし、デフォルトオプションとして指定している言語バージョンもそのままになってしまうので、MSVC等では警告が出ます・・・）

以下のページにこれらの関数で取得できるコンパイラ文字列の一覧があります。
- [Reference tables](https://mesonbuild.com/Reference-tables.html)
    - `Argument syntax`列は`get_argument_syntax()`によって得られる文字列

### VC++プロジェクトの癖

仕方ないことなのかもしれませんが、Mesonの出力するVC++プロジェクトは少し変わっています・・・

- VS同梱の開発者コマンドプロンプトから`meson build --backend vs`を実行しないといけない
    - 普通のコマンドプロンプトやpowershellではダメ
    - 64bitでビルドしたければ*x64 Native Tools Command Prompt*を使う必要がある
- 出力されたVC++メインのプロジェクトのプロパティはほぼ空（デフォルト）
    - 指定したコンパイルオプション等はビルド時には渡されているが、プロパティからは見えない・・・
        - このため、インテリセンスがC++14準拠になってしまう
- プロジェクトプロパティの変更は、ビルド時に`meson.build`が変更されていてプロジェクト再出力が自動で行われた場合にリセットされる

### VC++プロジェクトにヘッダを含める

出力されるVC++プロジェクトには指定したソースファイルは含まれていますが、インクルードディレクトリ内のヘッダは含まれていません。  
例えばそれらのファイルを編集したくてVS上で開いたとしても、プロジェクト外のファイルに対してはインテリセンスがうまく働きません。  
そのため、プロジェクトにそれらのヘッダを含めたいことがあるでしょう・・・

その場合は、ソースファイルと同じようにヘッダファイルを指定してやれば出力プロジェクトに含めることができます。

```meson
project('test_project', 'cpp', default_options : ['warning_level=3', 'werror=true', 'cpp_std=c++17'], meson_version : '>=0.50.0')
cppcompiler = meson.get_compiler('cpp').get_argument_syntax()

files = ['test.cpp', 'include/header1.hpp', 'include/header2.hpp']

include_dir = include_directories('include', 'oher/include')

executable('test_project', files, include_directories : include_dir, cpp_args : options)
```

残念ながらあるフォルダ内ファイルを列挙する手段はなさそうなので、1つづつ指定するしかなさそうな感じがします・・・。

### 依存ライブラリをダウンロードしてもらう

- [Subprojects](https://mesonbuild.com/Subprojects.html)

依存ライブラリの指定は`subproject()`を使えば出来ます。これはインストール済みCMake（もしくはパッケージマネージャ）を検出して、そこから依存ライブラリ情報を取得してダウンロードして・・・と自動でやってくれる様子です。

でもWindowsだとそんなの入ってないし、githubから引っ張ってきたリポジトリとかでもよろしくやってほしいものです。  
そのままだとこれは出来ない様子ですが、ラップファイルを用意してやることでやってもらえます。

`meson.build`があるフォルダに`subprojects`というフォルダを作り、その中に`ライブラリ名.wrap`というファイルを用意しておきます。

例えば、[doctest](https://github.com/onqtam/doctest)というライブラリを使いたいとしますと。

`subprojects/doctest.wrap`は以下のように書きます。
```
[wrap-git]
directory=doctest
url=https://github.com/onqtam/doctest.git
revision=2.3.4
clone-recursive=true
```
意味はなんとなくわかると思います。`directory=`の所を変えるとダウンロードされるディレクトリ名が変わるようです。`revision=`はダウンロードしてくるものの指定です。`HEAD`とかコミットハッシュが使えるようです。

そして、`meson.build`を以下のようにします。
```meson
project('test_project', 'cpp', default_options : ['warning_level=3', 'werror=true', 'cpp_std=c++17'], meson_version : '>=0.50.0')

#サブプロジェクトの指定
doctest_proj = subproject('doctest')
#依存オブジェクトの取得（名前が決まっている）
doctest_dep = doctest_proj.get_variable('doctest_dep')

files = ['test.cpp', 'include/header1.hpp', 'include/header2.hpp']

include_dir = include_directories('include', 'oher/include', 'subprojects/doctest')

executable('test_project', files, include_directories : include_dir, cpp_args : options, dependencies : doctest_dep)
```

`subproject('プロジェクト名')`で依存ライブラリを指定し（多分ここでダウンロード等がなされる）、その戻り値から`get_variable('ライブラリ名_dep')`で依存オブジェクト？を取得します。  
この依存オブジェクトは、対象ライブラリの持つ`meson.build`に書かれている名前を指定しなければなりません（慣例的に`ライブラリ名_dep`となっているようです）。

最後に、`executable()`に依存オブジェクトを指定してあげます。もし静的ライブラリ等の出力がある場合はここで自動的に取り込まれるようです（対象ライブラリの持つ`meson.build`が適切に書かれていれば）。

ちなみにこれらの時、ダウンロードしてきたプロジェクトのトップに`meson.build`が無いとたぶん上手くいきません・・・。
ただ、ヘッダーオンリーライブラリならインクルードパスの指定だけしてやればいい気がします（`get_variable()`して`executable()`で依存関係指定をしないで、`subproject()`だけしておく）

### CI（Travis AppVeyar）

これはまだ試していないのでどうなるのかわかりませんが、公式サイトにTravisとAppVeyarに対するymlのサンプルがあります。この通りにやれば出来そうです。

- [Continuous Integration - The Meson Build System](https://mesonbuild.com/Continuous-Integration.html)

### 参考文献
- [CMakeの代替 (となってほしい)、Mesonチュートリアル - Qita](https://qiita.com/turenar/items/c727834fbf701beb47ef)
- [Reference manual - The Meson Build System](https://mesonbuild.com/Reference-manual.html)