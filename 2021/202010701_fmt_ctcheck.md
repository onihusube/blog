# ［C++］ std::formatあるいは{fmt}のコンパイル時フォーマット文字列チェックの魔術

[:contents]

### コンパイル時フォーマットチェック

[{fmt}ライブラリ](https://github.com/fmtlib/fmt)および[`<format>`](https://cpprefjp.github.io/reference/format.html)には、コンパイル時のフォーマットチェック機能が実装されています。

```cpp
#include <format>
#include <fmt/core.h>

int main() {
  // 共にコンパイルエラーを起こす
  auto str = std::format("{:d}", "I am not a number");
  fmt::print("{:d}", "I am not a number");
}
```
- [godbolt](https://godbolt.org/z/sMxcohGjz)（[{fmt} v8.0.0のリリースノートより](https://github.com/fmtlib/fmt/releases/tag/8.0.0)）

`{:d}`は10進整数値1つのためのフォーマット指定であるのに、引数として整数値ではなく文字列が渡っているためにエラーとなっています。

これは先に{fmt}ライブラリで実装されたものが、遅れてC++20 `<format>`に導入されたものです。一見すると言語やコンパイラの特別のサポート無くしてはこのようなことはできないように思われますが、これは純粋にライブラリ機能として実装されています。

{fmt}ライブラリを追うのは辛かったので、`<format>`がどのようにこれを達成しているかを見てみることにします。

### `basic-format-string`クラス

`std::format`の宣言を見てみると、次のようになっています。

```cpp
template<class... Args>
  string format(format-string<Args...> fmt, const Args&... args);

template<class... Args>
  wstring format(wformat-string<Args...> fmt, const Args&... args);
```

どちらも第一引数にフォーマット文字列を取り、第二引数以降でフォーマット対象の変数列を受け取ります。`format-string`みたいなのは説明専用の型で、フォーマット文字列を構成しているものです。

```cpp
template<class charT, class... Args>
  struct basic-format-string;

template<class... Args>
  using format-string = basic-format-string<char, type_identity_t<Args>...>;

template<class... Args>
  using wformat-string = basic-format-string<wchar_t, type_identity_t<Args>...>;
```

`basic-format-string`クラスは説明専用のもので、実際の型名は実装によって異なります。その実装は次のように描かれています

```cpp
template<class charT, class... Args>
struct basic-format-string {
private:
  basic_string_view<charT> str;

public:
  template<class T>
  consteval basic-format-string(const T& s);
};
```

そのコンストラクタの効果については次のように規定されています。

> Constraints: const T& models convertible_­to<basic_­string_­view<charT>>.  
> Effects: Direct-non-list-initializes str with s.  
> Remarks: A call to this function is not a core constant expression ([expr.const]) unless there exist args of types Args such that str is a format string for args.

この3つめの*Remarks*指定がまさに、コンパイル時フォーマットチェックを規定しています。

### `consteval`コンストラクタ

> A call to this function is not a core constant expression ([expr.const]) unless there exist args of types Args such that str is a format string for args.

を訳すと（Powerd by DeepL）

> この関数の呼び出しは、`str`が`args`のフォーマット文字列であるような`Args`型の`args`が存在しない限り、コア定数式ではない。

ややこしいですが、`std::format`の引数として与えられたフォーマット文字列`str`とフォーマット対象の`args`について、`str`が正しくそのフォーマット文字列となっていなければこのこのコンストラクタの呼び出しはコア定数式でない、と言っており、コア定数式でないものは定数式で実行できません。

ところで、このコンストラクタには`consteval`指定がなされています。`consteval`はC++20から追加された言語機能で、`consteval`指定された関数は必ずコンパイル時に実行されなければならず、さもなければコンパイルエラーとなります。それは`consteval`コンストラクタにおいても同様です。

この*Remarks*指定と`consteval`の効果を合わせると、フォーマット文字列`str`が`Args...`に対して正しくない場合にコンパイルエラー、となるわけです。

### 実体

規定は分かりましたが、それだけでフォーマットチェックができるわけではありません。結局、ユーザーランドで規定に沿うように実装することが可能なのかどうかが知りたいことです。

C++20に強い人ならここまでのことで実装イメージが浮かんでいるでしょうが、一応書いてみることにします。

```cpp
// 定数式で呼べない関数
void format_error();

// フォーマットチェック処理
// 詳細は省略するが定数式で実行可能なように実装されているとする
template<typename CharT, typename... Args>
consteval void fmt_checker(std::basic_string_view<CharT> str) {

  // ...

  if (/*かっこが足りないとかの時*/) {
    format_error(); // 定数式で実行できないため、ここに来るとコンパイルエラー
  }

  // ...

  if (/*型が合わない時*/) {
    throw "invalid type specifier"; // throw式は定数式で実行不可
  }

  // ...
}

template<typename CharT, typename... Args>
struct basic_format_string {
  std::basic_string_view<CharT> str;

  template<typename T>
    requires std::convertible_­to<const T&, std::basic_­string_­view<charT>>
  consteval basic_format_string(const T& s) 
    : str(s)
  {
    fmt_checker<std::basic_string_view<CharT>, Args...>(str);
  }
};

template<class... Args>
using format_string = basic_format_string<char, std::type_identity_t<Args>...>;


// std::format
template<class... Args>
std::string format(format_string<Args...> fmt, const Args&... args) {
  // フォーマット済み文字列を作成する部分は省略
  return std::vformat(fmt.str, std::make_format_args(args...));
}
```

一応標準ライブラリのものを使っているところには`std::`を付加していますが、実際はこのような実装も`std`名前空間内で実装されるので不要です。

`format()`の引数として構築された`basic_format_string`（`format_string`）のコンストラクタ本体において、フォーマットチェックを行う`fmt_checker()`を呼び出します。`fmt_checker()`が行うフォーマットチェック機能は定数式で実行可能なように実装されているものとして、受け取ったフォーマット文字列`basic_format_string::str`をそこに渡して`fmt_checker()`が完了すればフォーマット文字列チェックは完了です。

`basic_format_string`のコンストラクタおよび`fmt_checker()`は`consteval`関数であるので、一連のフォーマットチェック機能は定数式で必ず実行される事になります。

`fmt_checker()`においてフォーマット文字列エラーが発生した場合コンパイルエラーとしなければなりませんが、実行環境が`consteval`コンテキストなので、定数式で実行できない事をしようとすればコンパイルエラーを引き起こすことができます。それは例えば、非`constexpr`関数の呼び出しや`throw`式の実行などがあります。

`fmt_checker()`にはフォーマット文字列`str`および、`format()`に指定された残りの戻り値の型`Args`が正しく伝わっています。`str`の内容と`Args`の各型を順番にチェックしていけば、指定されたフォーマット文字列に対して正しい引数が指定されているか？という事までチェックできます。

このような`format()`には任意の文字列型を渡すことができます。`basic_format_string`ではなく。

```cpp
int main() {
  // 文字配列 -> basic_format_stringへの暗黙変換
  // basic_format_stringのコンストラクタがconstevalのため、必ずコンパイル時に実行される
  auto str = format("{:d}", "I am not a number");
}
```

この`foramt()`の呼び出しの第一引数においては、文字配列（任意の文字型）->`basic_format_string`の一時オブジェクト->`basic_format_string`の左辺値、のような変換によって`foramt()`第一引数の`fmt`が構築されています。

`basic_format_string`の宣言された唯一つのコンストラクタは`explicit`されていないテンプレートコンストラクタなので、`string_view`に変換可能な任意の文字列型から暗黙変換によって呼び出すことができます。そして、そのコンストラクタは`consteval`なので暗黙変換からフォーマット文字列チェックまで必ずコンパイル時に実行されます。

すなわち、このコンパイル時フォーマット文字列チェックを支えているのは、`consteval`という機能なわけです。`consteval`自体は`<format>`と無関係に導入されており、コンパイル時フォーマット文字列チェックは何らの言語サポートを受けたものではありません。また、暗黙変換というのもミソなところで、これを利用する事によってコンパイル時チェックを走らせるための追加の何かをする必要がなくなっています。うーんかしこい！！

このように、コンパイル時フォーマット文字列チェックは純粋にC++20の範囲内で実装することができます。

### 応用例

### 参考文献

- [P2216R3 `std::format` improvements](https://wg21.link/p2216)
- [C++20 即時関数 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/immediate_functions.html)
- [`<format>` - cpprefjp](https://cpprefjp.github.io/reference/format.html)