# ［C++］コンソール出力にchar8_t文字列を出力したい・・・

### 非Windows

おそらくほとんどの場合、非Windows環境では`char`のエンコードがUTF-8なのでそのまま出力できるはずです。しかし、C++20では標準出力ストリームに対する`char8_t char16_t char32_t`の`operator<<`が`delete`されているため、そのままではコンパイルエラーになります。でもまあ`char`がUTF-8なのですから、こう、ちょっとひねってやれば、無事出力できます・・・

```cpp
#include <iostream>
#include <string_view>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  std::cout << reinterpret_cast<const char*>(u8str.data()) << std::endl;
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xPs4T0lwjqQaVuzl)

問題なのはWindowsさんです・・・

### Windowsのコンソール出力と標準出力

C言語ではI/Oをファイルとそれに対するデータのストリームとして抽象化しています。ファイルの読み書きによって動作環境との通信（すなわちI/O）を制御し、規定しています。標準出力（`stdout`）や標準入力は（`stdin`）は標準によって予め開くファイルが規定されているストリームで、これらにおいてのファイルとはコンソール（端末）です。

C++もCからこれらのことを継承し、多くのI/O関数はCのものを参照しているため、この辺りの標準I/Oストリームに関することは共通しています。

従って、C/C++の範囲から見た標準出力とはとりあえずは何かのファイルに対する出力として考えることができます。特に、標準出力が受け取った文字列をどう表示するかというところはファイル出力の先の話であり、C/C++が感知するところではありません。

#### 標準IOストリームのモード

C言語においてのファイルストリームには3つのモードがあり、ファイルオープンに使う関数種別`fopen/wfopen`およびその引数で決定されます。

- Text


#### コンソールのコードページ

ここからはWindowsの事情を鑑みなければなりません。

#### スクリーンバッファ

コンソール出力の到達点

### 1. 素直に変換して`std::cout`する

ここからは全てWindowsでの話になります。

一番簡便かつ確実な方法は、UTF-8文字列をANSI(Shift-JIS)文字列へ変換して`std::cout`へ出力することです。

`std::codecvt`はC++17で非推奨化してしまったので変換にはWinAPIを利用することにしますが、`UTF-8 -> Shift-JIS`の変換を実はそのままできません。`MultiByteToWideChar`は`char* -> wchar_t*`へ、`WideCharToMultiByte`は`wchar_t* -> char*`へ変換するので、どうしても型を合わせられないのです・・・

なのでこれらを連続適用して、`UTF-8 -> UTF-16 -> Shift-JIS`という2段階変換することになります。

```cpp
#include <iostream>
#include <string_view>

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  //UTF-8 -> UTF-16
  auto length = ::MultiByteToWideChar(CP_UTF8, 0, 
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    nullptr, 0);
  
  std::wstring temp(length, '\0');

  auto res = ::MultiByteToWideChar(CP_UTF8, 0,
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    temp.data(), temp.length());

  //UTF-16 -> Shift-JIS
  length = ::WideCharToMultiByte(CP_ACP, 0,
    temp.data(), static_cast<int>(temp.length()),
    nullptr, 0,
    nullptr, nullptr);

  std::string result(length, '\0');

  res = ::WideCharToMultiByte(CP_ACP, 0,
    temp.data(), static_cast<int>(temp.length()),
    result.data(), static_cast<int>(result.length()),
    nullptr, nullptr);

  std::cout << result;
}
```


変換の実装を信用すれば、UTF-8 -> UTF-16の変換で文字が落ちることはありませんが、UTF-16 -> Shift-JISの変換では当然Shift-JISでは受けきれないものが出てきます（絵文字とか）。それは`WideCharToMultiByte`がシステムデフォルト値（どうやら`??`）で埋めてくれます。

後面倒なのでしてませんが、コード内`res`で受けてる変換結果が`0`だとエラーが起きてるのでケアした方が良いでしょう。

#### 1.2 UTF-16に変換して`std::wcout`する

しかしとはいえ、二段階変換はさすがに気になりますし、途中でバッファ（`wstring`）を確保しなければいけないのも少し気になります。むしろ、`std::wcout`でUTF-16出力したくなりますよね。しかし、そのままだとなぜかAscii範囲外の文字が出力されません・・・

`std::wcout`と言えども出力先は`std::cout`と一緒です。すなわち、`wchar_t`を内部で`char`に変換してから出力しています。そしてどうやら、`std::wcout`のデフォルトはCロケールになっており、Cロケールでは変換時に非Ascii範囲の文字をスルーしてくれるようです。華麗です・・・

つまりは、明示的にロケールを指定してあげればいいのです。何を指定すればいいのかさっぱりですが、幸いWindowsでは`std::locale("")`とするとその環境のシステムデフォルトのロケールが取得できます。これはWindows限定でポータブルで、外国語環境に行っても適切にその環境のデフォルトロケールを取得することができます。後はこれを`std::wcout`にセットしてやればいいのです。

```cpp
#include <iostream>
#include <string_view>

#define WIN32_LEAN_AND_MEANv
#include <Windows.h>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  //UTF-8 -> UTF-16
  auto length = ::MultiByteToWideChar(CP_UTF8, 0, 
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    nullptr, 0);

  std::wstring result(length, '\0');

  auto res = ::MultiByteToWideChar(CP_UTF8, 0,
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    result.data(), static_cast<int>(result.length()));

  // wcoutにシステムデフォルトのロケールを設定（Cロケールから変更
  std::wcout.imbue(std::locale(""));

  // 出力
  std::wcout << result;
}
```

出力例
```
日本語出力テスト　
```

絵文字は消えましたが日本語出力は出来ているように見えます。しかし、これ以降同じプログラム内で`std::wcout`に何か出力しようとしても何も出てきません。

絵文字が消えているまさにそれが問題で、Shift-JISは絵文字を表現できないので絵文字の変換の際に内部でエラーとなってしまい、それ以降fail状態となり何も出てこなくなるのです。これは[`fail()`](https://cpprefjp.github.io/reference/ios/basic_ios/fail.html)によって検出でき、[`clear()`](https://cpprefjp.github.io/reference/ios/basic_ios/clear.html)によって回復できます。

```cpp
  // wcoutにシステムデフォルトのロケールを設定
  std::wcout.imbue(std::locale(""));

  // 出力
  std::wcout << result;

  // fail状態なら状態を復帰する
  if (std::wcout.fail()) {
    std::wcout.clear();
  }
```

`std::wcout`で出力したとしてもその内部で結局Shift-JISへの変換が走っているうえに、変換エラーによって出力できなくなるというのはこれはこれでイケてないですね・・・

### 2. UTF-16に変換して`WriteConsoleW()`する

Windowsにおいて、あるコンソールに直接出力するためのAPIが`WriteConsoleW()`関数です。この関数はUTF-16文字列を受け取り、コンソールに直接出力します。

```cpp
#include <iostream>
#include <string_view>

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  //UTF-8 -> UTF-16
  auto length = ::MultiByteToWideChar(CP_UTF8, 0, 
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    nullptr, 0);

  std::wstring result(length, '\0');

  auto res = ::MultiByteToWideChar(CP_UTF8, 0,
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    result.data(), static_cast<int>(result.length()));

  // 出力
  ::WriteConsoleW(::GetStdHandle(STD_OUTPUT_HANDLE), result.data(), result.length(), nullptr, nullptr);
}
```

![出力結果](https://raw.githubusercontent.com/onihusube/blog/master/2020/20200403_win_console_char8t/writeconsole.png)

`WriteConsoleW()`関数は指定されたコンソールのスクリーンバッファに対して指定されたUTF-16文字列を直接書き込む関数です。スクリーンバッファはコンソールの出力そのもので、ここに書き込まれているデータがフォントレンダラによって表示されます。

出力結果をコピペしてみると分かるのですが、絵文字列は表示出来ていないだけでコピペ先が表示できるもの（VSCodeとか）ならばちゃんと表示されます。すなわち、文字コードとしては出力までUTF-16で行われています。絵文字が出ないのはおそらくコンソールの表示部分がサロゲートペアを扱えないのに起因していると思われます。

`WriteConsoleW()`関数は名前の通りコンソール出力専用の関数なので、起動したプログラムにコンソールが割り当てられていない場合に失敗します。すなわち、この関数による出力ではリダイレクトができません。


### 3. 標準出力をユニコードモードにする

```cpp
#include <iostream>
#include <string_view>

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  //UTF-8 -> UTF-16
  auto length = ::MultiByteToWideChar(CP_UTF8, 0, 
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    nullptr, 0);

  std::wstring result(length, '\0');

  auto res = ::MultiByteToWideChar(CP_UTF8, 0,
    reinterpret_cast<const char*>(u8str.data()), static_cast<int>(u8str.length()),
    result.data(), static_cast<int>(result.length()));

  // 標準出力をユニコードモードにする
  ::_setmode(_fileno(stdout), _O_U16TEXT);
  // 出力
  std::wcout << result;
}
```

この方法、実はユニコードモードといいつつユニコード直接出力出来ているわけではありません（コピペしてみると分かります）。おそらく内部でUTF-16 -> Shift-JIS変換が行われています。変換に失敗した文字列はスペースが当てられているのでしょうか。

なお、この方法だと`std::cout`が使用できなくなります。出力するとエラー吐いて止まります・・・。他人の書いたライブラリを使っているときなどはログ出力に`std::cout`が使用されている可能性があるので注意が必要です。

### 4. コンソールのコードページを変更してUTF-8バイト列を直接流し込む

```cpp
#include <iostream>
#include <string_view>

#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  // 出力先コンソールのコードページをUTF-8にする
  ::SetConsoleOutputCP(65001u);
  // 標準出力をバイナリモードにする
  ::_setmode(_fileno(stdout), _O_BINARY);
  // バイナリ列として直接出力
  std::cout.write(reinterpret_cast<const char*>(u8str.data()), u8str.length());
}
```

この方法でも、VSCodeなどにコピペしてみれば絵文字が正しく表示されるので、UTF-8を直接出力することに成功しているようです。Ascii範囲内の文字ならば`std::cout`は依然として使用可能ですが、`std::wcout`は文字化けします。

コードページを変更してあるので、コンソールは入ってきたバイト列をUTF-8文字列として表示します。UTF-8はAscii文字と下位互換性があるので`std::cout`はAscii範囲内に限って使用可能となり、`std::wcout`は通常`wchar_t`（UTF-16）を受け付けるのでそのままだと文字化けするわけです。

ただし、コンソールのスクリーンバッファへの出力は通常UTF-16なので、UTF-8がそのまま出力されているわけではなく、スクリーンバッファへの出力にあたってはUTF-8 -> UTF-16の変換が行われているようです。  
なお、VSのプロジェクトの設定をマルチバイト文字セットに変えるとおそらくコンソールスクリーンバッファの文字コードはANSI(Shift-JIS)になるはずです。

### 5. Boost.Nowideを使用する

boost1.73から追加された[Boost.Nowide](https://github.com/boostorg/nowide)は`<iostream>`や`<fstream>`のUTF-8対応をポータブルにするライブラリです。非Windows環境に対しては`char`のエンコードがUTF-8だと仮定しそのまま、Windows環境ではUTF-8 -> UTF-16変換して`WriteConsoleW()`などWindowsのユニコード対応APIで出力します。

残念ながら`char8_t`対応はされていない（おそらく厳しい）のですが、これを利用すれば一番最初に紹介した方法がポータブルになります。

```cpp
#include <string_view>
#include <boost/nowide/iostream.hpp>

int main() {
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  boost::nowide::cout << reinterpret_cast<const char*>(u8str.data()) << std::endl;
}
```

試していないので出力がどうなるのかは分かりませんが、実装を見るにおそらく`WriteConsoleW()`を使用したときと同様になるかと思われます。

### UTF-8の直接出力 in Windows

無理です。

### 絵文字の表示 in Windows

通常のコンソールでは、無理です。

Windows Terminalを使えば表示できる様子です。なんかまだ非Ascii圏対応は怪しそうですが、今後に期待です・・・

### 参考文献

- コンソール出力関連
    - [標準ストリーム - Wikipedia](https://ja.wikipedia.org/wiki/標準ストリーム)
    - [ファイルとストリーム - Microsoft Docs](https://docs.microsoft.com/ja-jp/cpp/c-runtime-library/files-and-streams?view=vs-2019)
    - [C言語のワイド文字入出力 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio/)
    - [C言語のワイド文字入出力 — MSVCRTの場合 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio-msvcrt/)
    - [C言語のワイド文字入出力 — Windows Console 編 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio-on-windows-console/)
    - [WindowsコマンドプロンプトにUnicode表示 - エンジニア徒然草](http://mitaka1954.cocolog-nifty.com/blog/2013/01/windowsunicode-.html)
    - [標準入出力とリダイレクト - EternalWindows](http://eternalwindows.jp/windevelop/console/console02.html)
    - [コンソールへの入出力 - EternalWindows](http://eternalwindows.jp/windevelop/console/console02.html)
    - [Unicode Stream I/O in Text and Binary Modes - EternalWindows](https://docs.microsoft.com/en-us/cpp/c-runtime-library/unicode-stream-i-o-in-text-and-binary-modes?view=vs-2019)
    - [CHAR_INFO structure - Microsoft Docs](https://docs.microsoft.com/en-us/windows/console/char-info-str)
    - [コードページ - Microsoft Docs](https://docs.microsoft.com/ja-jp/cpp/c-runtime-library/code-pages?view=vs-2019)
    - [Windows 10までほとんど手が入れられてこなかったWindowsのコンソール機能 - ASCII.jp](https://ascii.jp/elem/000/001/718/1718052/)
- 各方法関連
    - [Visual C++における文字コード変換 - C++と色々](https://nekko1119.hatenablog.com/entry/2017/01/02/054629)
    - [[めも]コンソールに日本語を出力したい場合(wcoutで日本語出力する場合など) - Qita](https://qiita.com/toris-birds/items/5443777ad0bb0ae05d3b)
    - [WriteConsole function - Microsoft Docs](https://docs.microsoft.com/en-us/windows/console/writeconsole?redirectedfrom=MSDN)
    - [SetConsoleOutputCP function - Microsoft Docs](https://docs.microsoft.com/en-us/windows/console/setconsoleoutputcp)
    - [Boost.Nowide - github](https://github.com/boostorg/nowide)
- その他
    - [P1423R3 `char8_t` backward compatibility remediation](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1423r3.html)
    - [Windows のコンソール端末と Unicode の相性 - NUMBER-SHOT.NET](https://number-shot.net/blog/windows-console-terminal-with-unicode/)


### 謝辞

この記事の6割は以下の方々によるご指摘によって成り立っています。

- [@Reputelessさん](https://twitter.com/Reputeless/status/1243960591745605633)

