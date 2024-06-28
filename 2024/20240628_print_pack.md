# ［C++］ パラメータパックをprint/formatする

[:contents]

### フォーマット文字列とパラメータパック

`std::format()`および`std::print()`のフォーマット文字列は共通のもので、文字列内の`{}`（置換フィールド）に対して、与えられた引数（フォーマット対象の値）を文字列化したものを順番に置き換えていきます。

```cpp
// フォーマット文字列の例
std::print("{}", 0);
std::print("{}{}{}", 0, 1.0, "2");
```

この時、この対応関係はコンパイル時にチェックされ、フォーマット文字列の`{}`の数に対して引数が足りない場合はエラーになります（なぜか、多いだけならエラーにはならないようです）。

```cpp
std::print("{}{}{}", 0);      // ng
std::print("{}", 0, 1, 2, 3); // ok
```

引数の値は定数である必要はなく実行時の値であっても当然問題ないのですが、フォーマット文字列そのもの、およびそれに現れている置換フィールド`{}`の数とフォーマット対象の引数の数は、コンパイル時にコード上で一致している必要があります。

ここで問題となるのは、コード上からだと一見可変長だけどコンパイル時にはその数が確定してる、ような物体です。パラメータパックがそれです。

```cpp
void any(auto&&...);

void f(auto&&... args) {
  // コンパイル時に要素数は取れる
  constexpr std::size_t N = sizeof...(args);

  // パックそのものは他に渡せない
  any(args);    // ng
  any(args...); // ok

  // パラメータパックそのものには型は無い
  using t = decltype(args); // ng
}
```

パラメータパックそのものに対してはサイズを取得することと展開することくらいしかできず、取りまわすようなことは不可能です。そのため、`std::format()/std::print()`でも、パラメータパックそのものを渡して文字列化することはできません。

```cpp
void print_pack(auto&&... args) {
  std::print("{}", args);     // ng

  // パックの先頭の値のみが出力される
  std::print("{}", args...);  // ok（パックが空でなければ）
}
```

多い分には問題ないので先頭N個だけ出力したければこういう感じでもいいのかもしれませんが、パラメータパックに含まれる値をすべて出力したい場合に、フォーマット文字列をべた書きすることはできず、なんらか生成する必要が出てきそうに思えます。

### コンパイル時生成

C++17以前だとメタメタプログラミングの世界へようこそ！するのですが、C++20であれば`std::string`がコンパイル時に使用できるのでいくらからくにはなります。

```cpp
#include <ranges>
#include <print>
#include <string>

template<std::size_t N>
consteval auto make_format_string_for_pack() {
  std::string fmtstr = "";
  
  // デリミタはお好みで
  constexpr std::string_view append = "{}, ";
  
  for (auto _ : std::views::iota(0ull, N)) {
    fmtstr += append;
  }

  std::array<char, append.length() * N + 1> save;
  std::ranges::copy(fmtstr, save.begin());
  save.back() = '\0';

  return save;
}

void print_pack(auto&&... args) {
  static constexpr auto fmtstr_array = make_format_string_for_pack<sizeof...(args)>();
  std::print(fmtstr_array.data(), args...);
}

int main() {
  print_pack(1, "str", 3.1415, 'c', true);
}
```
```
1, str, 3.1415, c, true, 
```

- [[C++] clang HEAD 19.0.0git (https://github.com/llvm/llvm-project.git c63eaddb629aa8d016b26c9c60c92aa5dcae3b43) - Wandbox](https://wandbox.org/permlink/Xbz0QTz6UvAWFIat)

これでもいいんですが、書くことが多いし、かなりテクニカルな部分が多いコードになっています。なぜわざわざ`std::array`に詰めなおしているのか？なぜ`static constexpr`？？などなど。

### 実行時フォーマットを使う

素直に実行時にやる方法です。

```cpp
#include <ranges>
#include <print>
#include <string>

void print_pack(auto&&... args) {
  std::string fmtstr = "";
  
  for (auto _ : std::views::iota(0ull, sizeof...(args))) {
    // デリミタはお好みで
    fmtstr += "{}, ";
  }
  
  std::vprint_unicode(fmtstr, {std::make_format_args(args...)});
}

int main() {
  print_pack(1, "str", 3.1415, 'c', true);
}
```
```
1, str, 3.1415, c, true, 
```

- [[C++] clang HEAD 19.0.0git (https://github.com/llvm/llvm-project.git c63eaddb629aa8d016b26c9c60c92aa5dcae3b43) - Wandbox](https://wandbox.org/permlink/j3AH6q05VoDYieiB)

記述量自体は減りましたし実装も単純になりました。しかしこの場合、フォーマット文字列のチェックがコンパイル時に行われなくなるため、例えばパックの中にフォーマットできない型が含まれていても実行時エラーになります。

### `std::tie()`

古来より、パラメータパックを扱う際には`std::tuple`とその周辺ユーティリティが便利に活用できることが良く知られています。そして、C++23からは`std::tuple`のフォーマットサポートが入るため、`std::tuple`はそのものフォーマット可能になります。

したがって、`tuple`を利用することで一番シンプルに書くことができます。

```cpp
#include <ranges>
#include <print>
#include <string>

void print_pack(auto&&... args) {
  std::print("{}", std::tie(args...));
}

int main() {
  print_pack(1, "str", 3.1415, 'c', true);
}
```
```
(1, "str\u{0}", 3.1415, 'c', true) 
```

- [[C++] clang HEAD 19.0.0git (https://github.com/llvm/llvm-project.git c63eaddb629aa8d016b26c9c60c92aa5dcae3b43) - Wandbox](https://wandbox.org/permlink/UNMBKUnAqbHeDp0E)


文字列出力がエスケープされているのはたぶんclangの実装バグです。本来エスケープされないのが正しいはず。

一番短くかつ単純でありながら、この方法であれば非パック引数と組み合わせることもできるし`std::tuple`用のフォーマットオプションを使用することもできます。

ただし、`std::tuple`のフォーマットサポートがC++23からなので、C++20の`std::format()`ではこの方法は使えません。前の2つのどちらかで頑張りましょう。

### `std::tuple`のフォーマットオプション

`std::tie()`による方法であれば、限定的なものではあるものの`std::tuple`のためのフォーマットオプションを使用することができます。

まず、`n`オプションによって囲み文字（`()`）を省くことができます。

```cpp
void print_pack(auto&&... args) {
  std::println("{:n}", std::tie(args...));
  std::println("{{{:n}}}", std::tie(args...));
}
```
```
1, "str\u{0}", 3.1415, 'c', true
{1, "str\u{0}", 3.1415, 'c', true}
```

`std::tuple`固有のオプションはこれくらいで、残りは整数型等他の型と同じく幅指定に関するオプションが使用できます。

```cpp
void print_pack(auto&&... args) {
  std::println("|{:*<40n}|", std::tie(args...));
  std::println("|{:+>40n}|", std::tie(args...));
  std::println("|{:-^40n}|", std::tie(args...));
}
```
```
|1, "str\u{0}", 3.1415, 'c', true********|
|++++++++1, "str\u{0}", 3.1415, 'c', true|
|----1, "str\u{0}", 3.1415, 'c', true----|
```

幅と寄せ、埋め文字のオプション指定は`tuple`の要素型毎ではなく`tuple`の全体に適用されます。

### 参考文献

- [`std::format()` - cpprefjp](https://cpprefjp.github.io/reference/format/format.html)
- [`std::make_format_args()` - cpprefjp](https://cpprefjp.github.io/reference/format/make_format_args.html)
