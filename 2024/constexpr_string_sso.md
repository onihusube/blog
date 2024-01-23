# ［C++］ コンパイル時`std::string`を実行時に持ち越す方法

[:contents]

### コンパイル時動的メモリ確保の制約

C++20でコンパイル時の動的メモリ確保が可能になり、それに伴って`std::vector`と`std::string`が完全に定数式で使用可能になりました。ただしそれには制限があり、コンパイル時に確保したメモリはコンパイル時に返却しなければならないため、定数式で構築した`std::vector`や`std::string`のオブジェクトを実行時に持ち越すことはできません（少なくともC++23時点では）。

```cpp
#include <vector>
#include <string>

int main() {
  constexpr std::vector vec = {1, 2, 3, 4, 5};  // ng
  constexpr std::string str = "non transient constexpr allocation"; // ng
}
```

これはどちらも、コンパイルエラーとなります。

- [`std::vector`の例 - [C++] clang 17.0.1 - Wandbox](https://wandbox.org/permlink/dRATsVhUQ9SD3klH)
- [`std::string`の例 - [C++] clang 17.0.1 - Wandbox](https://wandbox.org/permlink/nrGI40ew8ql1XYyv)

実行時からも参照可能な様にコンパイル時の定数が残るということはそのデストラクタは呼ばれていないということで、`std::vector`/`std::string`の場合はどちらもデストラクタで確保したメモリを解放するため、このように`constexpr`変数として受けてしまうと定数式で確保されたメモリを解放していないことになり、その様なメモリ確保は定数式で許可されないためコンパイルエラーとなります。

したがって、コンパイル時の`std::vector`と`std::string`の可能な使用法はコンパイル時に呼ばれる関数内に閉じた形で利用するなど、あくまで定数式の中だけで参照可能な様に使用することです。

```cpp
#include <concepts>
#include <ranges>
#include <algorithm>
#include <vector>
#include <array>

using namespace std::ranges;

// 単純な範囲の結合処理
template<input_range R1, input_range R2>
  requires std::same_as<range_value_t<R1>, range_value_t<R2>>
constexpr auto concat_to_vector(const R1& r1, const R2& r2) -> std::vector<range_value_t<R1>> {
  std::vector<range_value_t<R1>> vec{};

  for (const auto& v : r1) {
    vec.push_back(v);
  }

  for (const auto& v : r2) {
    vec.push_back(v);
  }

  return vec;
}

// ok
static_assert(equal(concat_to_vector(std::array{1, 2, 3}, views::iota(4, 7)), std::vector{1, 2, 3, 4, 5, 6}));
```

- [[C++] gcc HEAD 14.0.1 20240121 (experimental) - Wandbox](https://wandbox.org/permlink/TrVVIrsGjJZooSLU)

```cpp
#include <concepts>
#include <ranges>
#include <algorithm>
#include <string>

using namespace std::ranges;

// 単純な文字列フォーマット処理
constexpr auto simple_format(std::string_view fmt, std::string_view str) -> std::string {
  // 文字列fmt中の%をstrで置換する
  auto replace = [str](const char& c) -> std::string_view {
    if (c != '%') {
      return std::string_view{&c, 1};
    } else {
      return str;
    }
  };

  std::string result;

  for (char c : fmt | views::transform(replace)
                    | views::join)
  {
    result += c;
  }

  return result;
}

// ok
static_assert(simple_format("Hello % !!", "world") == "Hello world !!");
```

- [[C++] gcc HEAD 14.0.1 20240121 (experimental) - Wandbox](https://wandbox.org/permlink/kfGbQ21TJC9JJ6Zh)

このことはまた、C++23の`std::unique_ptr`に対しても同じことが当てはまります。

### コンパイル時SSO！

実は、`std::string`に限ってはこの制限を回避することが可能です。

この制限はコンパイル時に確保したメモリをコンパイル時に解放しなければならないことから来ているため、そもそもメモリを確保しなければその様な制限に引っかからないわけです。そして、`std::string`はSSOという短い文字列に対して動的メモリ確保を回避してそのオブジェクト内に文字列を保持する最適化が行われています。

コンパイル時の`std::string`でもSSOが実装されている場合、短い文字列に対してはコンパイル時にもメモリ確保が行われないため、SSOが行われている`std::string`オブジェクトは実行時に持ち越すことができます。

```cpp
#include <string>
#include <concepts>
#include <ranges>
#include <print>
#include <string_view>

using namespace std::literals;

constexpr auto make_string(char init, std::unsigned_integral auto N) -> std::string {
  std::string str;
  
  for (auto i : std::views::iota(init, init + char(N))) {
    str += i;
  }

  return str;
}

constexpr std::string cstr = make_string('a', 10u);

int main() {
  static_assert(cstr == "abcdefghij"sv);  // なぜかgccのみng
  std::println("{:s}", cstr);
}
```

- [Compiler Explorer](https://godbolt.org/z/b99G55EM9)

現時点で最新のコンパイラバージョンが必要ですが、これはC++の主要3実装で利用可能です。

### 最大文字数

SSOは`std::string`内部に文字列を保持するため、SSOが行われる文字列の最大長は`std::string`のサイズ以下になります。実装の制限などが加わることでその長さは減り、主要3実装ではコンパイル時SSOが可能な文字列長（`\0`は除く）は次の様になります

- Clang libc++ : 22
- GCC libstdc++ : 15
- MSVC STL : 15

```cpp
#include <string>
#include <ranges>
#include <print>

constexpr auto make_string(char init, std::unsigned_integral auto N) -> std::string {
  std::string str;
  
  for (auto i : std::views::iota(init, init + char(N))) {
    str += i;
  }

  return str;
}

// 各実装における最大容量
#ifdef __clang__
  constexpr std::size_t length = 22;
#elif defined(__GNUC__)
  constexpr std::size_t length = 15;
#elif defined(_MSC_VER)
  constexpr std::size_t length = 15;
#else
  #error not covered
#endif

constexpr std::string cstr = make_string('a', length);

int main() {
  std::println("{:s}", cstr);
}
```

- [Compiler Explorer](https://godbolt.org/z/b99G55EM9)

ただしこのことは、定数式における`std:string`の使用時にその実装詳細が露呈しコードの可搬性に影響を与えるとして、バグではないかとする向きもあります。

```cpp
// clangのみok、gcc/msvcはng
constinit std::string contant_init_str = make_string('a', 16);
```

どういう文字列で初期化するかはともかくとして、この様なコードは普通に書かれる可能性があります。その場合に、SSOの制限によってエラーになったりならなかったりするのは非自明なことかもしれません。

### 実装状況

`std::string`のSSOはほぼ全ての実装で実装されていますが必須ではなく、コンパイル時の`std::string`に対しても求められていません。そのため、ほとんどの実装では`std::string`の`constexpr`対応よりも遅れてコンパイル時SSOへの対応が行われています。また、これは実装品質の問題であるため個別の提案による機能に比べて扱いが小さく、どのバージョンから導入されたのか分かりづらいものがあります。

ここに、主要3実装において`std::string`のコンパイル時SSOが利用可能になる最小のバージョンについてメモしておきます

- Clang libc++ : Clang 18.0
- GCC libstdc++ : GCC 14.1
- MSVC STL : VS2022 17.4

ただし、GCC（libstdc++）の現時点の実装では、実装の都合上ローカル`constexpr`変数で使用できません。

```cpp
// clang/gcc/msvc全てでok
constexpr std::string global_str = "global";

int main() {
  // gccのみng
  constexpr std::string local_str = "local";
}
```

### 実装について

主要3実装におけるコンパイル時SSO実装はどれも、実行時のSSO実装をコンパイル時にも利用できるように調整したもので、その仕組みは実行時のものと変わりありません。したがって、SSO可能な最大文字数も実行時とコンパイル時で共通しています。

実装についてはこちらの記事を参照

- [std::stringのSSO(Small-string optimization)がどうなっているか調べた · melpon/qiita · GitHub](https://github.com/melpon/qiita/tree/master/items/stdstringのSSO(Small-string%20optimization)がどうなっているか調べた)

主要3実装はそれぞれ異なる実装を取っているわけですが、GCCの実装は`std::string`オブジェクト内部にSSO文字列へのポインタを保持する様な実装になっています。これは実行時に条件分岐を削減するためのものと思われますが、このことがローカル`constexpr`変数としてSSO`std::string`を保持することを妨げています。

GCCの`std::string`のSSO実装のエッセンスを抽出すると、次の様になっています

```cpp
// GCCのstd::string SSOの簡易実装例（libstdc+++の実装を改変）
strucy string {
  ...

  // EBOによりアロケータサイズを圧縮
  struct _Alloc_hider : allocator_type {
    ...

    char* ptr;  // 文字列領域へのポインタ
  };

  _Alloc_hider dataplus;      // アロケータと文字列ポインタ
  std::size_t	string_length;  // 文字列長

  // SSO最大長の定数
  enum { local_capacity = 15 / sizeof(char) };

  // ローカルバッファとキャパシティをオーバーラップさせる
  union {
    char local_buf[local_capacity + 1]; // SSOの場合のバッファ
    std::size_t allocated_capacity;     // 非SSOの場合のキャパシティ
  };

  ...

  // 文字列リテラルを受け取るコンストラクタ
  constexpr basic_string(const char* str, const allocator_type& alloc = _Alloc())
    : dataplus(+local_buf, alloc) // SSOバッファのポインタを保存
  {
    const std::size_t len = std::char_traits<char>::length(str);

    if (len > local_capacity) {
      // SSO最大長を超える場合、動的メモリ確保を行う
      auto [new_ptr, new_capacity] = allocate_new_memory(len);  // allocate_new_memory()はメモリ確保と初期化を行う架空の関数

      dataplus.ptr = new_ptr; // 確保した領域へのポインタを保存
      allocated_capacity = new_capacity;
    }

    // 文字列コピーなど残りの処理
    ...
  }

  ...

  constexpr const char* data() const {
    return dataplus.ptr;  // 分岐が必要ない
  }
};
```

これはGCCの現在の`std::string`実装の一部を抜き出して見やすく整えたものです。

`_Alloc_hider::ptr`はSSOされているかに関わらず文字列領域の先頭を指すポインタであり、SSOが行われている場合は`std::string`内部にある`local_buf`へのポインタとなります。

`std::string`がローカル変数である場合、`local_buf`はローカル変数内のストレージであり、`_Alloc_hider::ptr`の指すポインタはスタック領域を指すポインタとなります。

実行時の場合、スタック領域へのポインタ（ローカル変数の配置場所）は関数実行のたびに変化します。それが定数式でも同様でしょうが、定数式におけるその様なポインタが`constexpr`変数に保存されて実行時に参照される場合それはどうなるでしょうか？スタック領域へのポインタであるため実行のたびに変化しますが、一方でそれは`constexpr`変数でありコンパイル時に決定される値であるはずです。

その様な矛盾を表面化させないために、現在のC++はこのような定数式におけるローカルなポインタが実行時に残るような変換や式の実行を禁止しています。これにより、GCCの`std::string`のSSO実装はローカル`constexpr`変数の場合に定数式で実行できずにコンパイルエラーとなります。

これが`static`変数あるいはグローバル変数であればこの様な問題は起こらないため、静的ストレージに配置される`constexpr`な`std::string`ではSSOが利用可能です。

ちなみに余談ですが、これと同様のことが構造化束縛の`constexpr`宣言を許可する議論の過程で問題となっており、そこでは定数式におけるポインタ/参照の実装戦略として記号的なアドレス指定（*Symbolic addressing*）と呼ばれるアドレス値の使用を回避した新しい実装方法が検討されています。

- [P2686R1 constexpr structured bindings and references to constexpr variables - WG21月次提案文書を眺める（2023年05月）](https://onihusube.hatenablog.com/entry/2023/07/08/205803#P2686R1-constexpr-structured-bindings-and-references-to-constexpr-variables)

これが導入されると、この問題も解消されるかもしれません。

### `std::vector`の場合

`std::vector`は基本的にSSO（SOO）の様なことが行われることはありません。ただし、`std::vector`にも構築後にメモリ確保を全く行わない状態があり、その場合は実行時に持ち越すことができそうです。

```cpp
#include <vector>

int main() {
  constexpr std::vector<int> cvec{};
}
```

- [Compiler Explorer](https://godbolt.org/z/joW6EYn4o)

`std::vector`のデフォルトコンストラクタはせいぜいそのメンバを初期化するくらいのことしか行わないため、動的メモリ確保が走ることはありません。主要3実装はこれを許可する様です。

一見これは無意味に見えますが、これができるということはこの初期化は定数式で完了しているということでもあり、次の様にすると用途がありそうに見えてきます

```cpp
// 初期化のみをコンパイル時に終わらせる
constinit std::vector<int> constant_init_vec{};
```

### 参考文献

- [C++20 可変サイズをもつコンテナのconstexpr化 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/more_constexpr_containers.html)
- [c++ - C++20 constexpr vector and string not working - Stack Overflow](https://stackoverflow.com/questions/69498115/c20-constexpr-vector-and-string-not-working?noredirect=1&lq=1)
- [Implement SSO for constexpr string by miscco · Pull Request #1735 · microsoft/STL](https://github.com/microsoft/STL/pull/1735)
- [[libcxx] Allow string to use SSO in constant evaluation. by jyknight · Pull Request #66576 · llvm/llvm-project · GitHub](https://github.com/llvm/llvm-project/pull/66576)
- [std::stringのSSO(Small-string optimization)がどうなっているか調べた · melpon/qiita · GitHub](https://github.com/melpon/qiita/tree/master/items/stdstringのSSO(Small-string%20optimization)がどうなっているか調べた)
- [Small String Optimization で Rust ライブラリ ratatui を最適化した話 - はやくプログラムになりたい](https://rhysd.hatenablog.com/entry/2023/11/30/200857)
- [GitHub - elliotgoodrich/SSO-23: Memory optimal Small String Optimization implementation for C++](https://github.com/elliotgoodrich/SSO-23)
- [Just how `constexpr` is C++20's `std::string`? – Arthur O'Dwyer – Stuff mostly about C++](https://quuxplusone.github.io/blog/2023/09/08/constexpr-string-firewall/)
- [111351 – constexpr std::string objects permitted to escape constant evaluation when SSO](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=111351)
- [C++20 コンパイル時初期化を強制する`constinit`キーワードを追加 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/constinit.html)
