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

### 1. 素直に変換して`std::cout`する

ここからは全てWindowsでの話になります。

一番簡便かつ確実な方法は、UTF-8文字列をANSI(Shift-JIS)文字列へ変換して`std::cout`へ出力することです。

`std::codecvt`はC++17で非推奨化してしまったので変換にはWinAPIを利用することにしますが、`UTF-8 -> Shift-JIS`の変換を実はそのままできません。`MultiByteToWideChar : char* -> wchar_t*`、`WideCharToMultiByte : wchar_t* -> char*`なので、どうしても型を合わせられないのです・・・

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

出力例
```
日本語出力テスト　?? ?? ???♂? ?? ?? ?? ?? ?? 終端
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
  _setmode(_fileno(stdout), _O_U16TEXT);
  // 出力
  std::wcout << result;
}
```

### 4. コンソールのコードページを変更してバイナリ列を直接流し込む

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
  _setmode(_fileno(stdout), _O_BINARY);
  // バイナリ列として直接出力
  std::cout.write(reinterpret_cast<const char*>(u8str.data()), u8str.length());
}
```

### 5. boost.nowideを使用する

boost1.73から追加されたboost.nowideは`<iostream>`や`<fstream>`のUTF-8対応をポータブルにするライブラリです。非Windows環境に対しては`char`のエンコードがUTF-8だと仮定しそのまま、Windows環境ではUTF-8 -> UTF-16変換して`WriteConsoleW()`などWindowsのユニコード対応APIで出力します。

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

出力例（Windows）
```
日本語出力テスト　?? ?? ???♂? ?? ?? ?? ?? ?? 終端
```

出力例（非Windows）
```
日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端
```

### 絵文字の表示 in Windows

無理です諦めてください。

あるいは、Windows Terminalを使えば表示できる様子です。なんかまだ非Ascii圏対応は怪しそうですが、今後に期待です・・・

### 参考文献

- [P1423R3 `char8_t` backward compatibility remediation](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1423r3.html)
- [コードページ - Microsoft Docs](https://docs.microsoft.com/ja-jp/cpp/c-runtime-library/code-pages?view=vs-2019)
- [WriteConsole function - Microsoft Docs](https://docs.microsoft.com/en-us/windows/console/writeconsole?redirectedfrom=MSDN)
- [SetConsoleOutputCP function - Microsoft Docs](https://docs.microsoft.com/en-us/windows/console/setconsoleoutputcp)
- [C言語のワイド文字入出力 — MSVCRTの場合 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio-msvcrt/)
- [C言語のワイド文字入出力 — Windows Console 編 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio-on-windows-console/)
- [WindowsコマンドプロンプトにUnicode表示 - エンジニア徒然草](http://mitaka1954.cocolog-nifty.com/blog/2013/01/windowsunicode-.html)
- [[めも]コンソールに日本語を出力したい場合(wcoutで日本語出力する場合など) - Qita](https://qiita.com/toris-birds/items/5443777ad0bb0ae05d3b)
- [Visual C++における文字コード変換 - C++と色々](https://nekko1119.hatenablog.com/entry/2017/01/02/054629)
- [Windows のコンソール端末と Unicode の相性 - NUMBER-SHOT.NET](https://number-shot.net/blog/windows-console-terminal-with-unicode/)
- [Boost.Nowide - github](https://github.com/boostorg/nowide)

### 謝辞

この記事の6割は以下の方々によるご指摘によって成り立っています。

- [@Reputelessさん](https://twitter.com/Reputeless/status/1243960591745605633)

