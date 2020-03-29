# ［C++］Windowsコンソール出力にchar8_t文字列を出力したい

### 非Windows

おそらくほとんどの場合、非Windows環境では`char`のエンコードがUTF-8なのでそのまま出力できるはずです。しかし、C++20では標準出力ストリームに対する`char8_t char16_t char32_t`のあらゆる出力が`delete`されているため、そのままではコンパイルエラーになります。でもまあ`char`がUTF-8なのですから、こう、ちょっとひねってやれば、無事出力できます・・・

```cpp
#include <iostream>
#include <string_view>

int main()
{
  using namespace std::string_view_literals;
  auto u8str = u8R"(日本語出力テスト　🤔 😢 🙇‍♂️ 🎉 😰 😊 😭 😥 終端)"sv;

  std::cout << reinterpret_cast<const char*>(u8str.data()) << std::endl;
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xPs4T0lwjqQaVuzl)

### 1. 素直に変換する

### 2. 標準出力をユニコードモードにする

### 3. コンソールのコードページを変更してバイナリ列を直接流し込む

### 絵文字の表示 in Windows

無理です諦めてください。

あるいは、Windows Terminalを使えば表示できる様子です。なんかまだ非Ascii圏対応は怪しそうですが、今後に期待です・・・

### 参考文献

- [C言語のワイド文字入出力 — MSVCRTの場合 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio-msvcrt/)
- [C言語のワイド文字入出力 — Windows Console 編 - 雑記帳](https://blog.miz-ar.info/2017/01/wide-stdio-on-windows-console/)
- [[めも]コンソールに日本語を出力したい場合(wcoutで日本語出力する場合など) - Qita](https://qiita.com/toris-birds/items/5443777ad0bb0ae05d3b)
- [WindowsコマンドプロンプトにUnicode表示 - エンジニア徒然草](http://mitaka1954.cocolog-nifty.com/blog/2013/01/windowsunicode-.html)
- [Visual C++における文字コード変換 - C++と色々](https://nekko1119.hatenablog.com/entry/2017/01/02/054629)
- [コードページ - Microsoft Docs](https://docs.microsoft.com/ja-jp/cpp/c-runtime-library/code-pages?view=vs-2019)
- [P1423R3 `char8_t` backward compatibility remediation](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1423r3.html)
- [Windows のコンソール端末と Unicode の相性 - NUMBER-SHOT.NET](https://number-shot.net/blog/windows-console-terminal-with-unicode/)

### 謝辞

この記事の6割は以下の方々によるご指摘によって成り立っています。

- [@Reputelessさん](https://twitter.com/Reputeless/status/1243960591745605633)

