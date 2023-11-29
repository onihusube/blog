# ［C++］使用しないことを意味する変数名`_`

C++26より、使用しない値に対する共通した変数名として`_`を言語サポート付きで使用できるようになります。

```cpp
[[nodiscard]]
auto f() -> int;

auto g() -> std::tuple<int, double, std::string>;

int main() {
  auto _ = f(); // ok、警告なし
  auto [n, _, str] = g();   // ok

  std::cout << _;   // ng
}
```

[:contents]

### 概要

ローカル変数でその変数名が`_`（アンダースコア）であるものは、暗黙的に`[[maybe_unused]]`が指定されます。

```cpp
[[nodiscard]]
auto f() -> int;

int main() {
  // この宣言は
  auto _ = f();
  
  // この宣言と等価になる
  [[maybe_unused]]
  auto _ = f();
}
```

これによって、この変数`_`は以降使用されていなくてもコンパイラは警告しません。また、`[[nodiscard]]`指定された関数では、戻り値を破棄している警告も抑制されます。

変数名`_`はまた、ローカルの構造化束縛の変数名としても使用でき、同じことが適用されます。

```cpp
auto g() -> std::tuple<int, double, std::string>;

int main() {
  auto [_, d, str] = g(); // ok
  auto [n, _, _] = g();   // ok
  auto [_, _, _] = g();   // ok
}
```

構造化束縛の例からもわかるかもしれませんが、変数名`_`は同じスコープで何度でも使用することができます。

```cpp
int main() {
  auto _ = 0;   // ok
  auto _ = f(); // ok
  auto [_, _, str] = g(); // ok
  auto _ = 1.0; // ok
}
```

そして、`_`が2回以上再宣言されている場合、そのコンテキストにおける`_`の利用はコンパイルエラーとなります。

```cpp
void h(auto);

int main() {
  auto _ = 0; // ok

  std::cout << _ << '\n'; // ok、この時点では使用可能

  auto _ = 1.0; // ok

  std::cout << _ << '\n'; // ng
  _ = f();    // ng
  int n = _;  // ng
  h(_);       // ng
}
```

この場合、`_`は変数名として宣言することにのみ使用できます。

このように、C++26における変数名`_`は初期化するもののその後使用しない変数に対する共通の名前として使用できるようになります。

そして、この機能はまた、将来のパターンマッチング構文で`_`を使用するための前準備でもあります。

### name-independent declaration

### 破棄のタイミング

C#やRustなどの`_`変数名と異なる点として、C++26の`_`変数名はその値の破棄（デストラクタ呼び出し）を意味していません。あくまで、その変数（オブジェクト）の利用に興味がないことを意味しています。

したがって、`_`変数の破棄のタイミングは他の変数と同じになり、そのスコープの終わりで宣言と逆順に破棄されます。

```cpp
struct check_dtor {
  int n;

  check_dtor(int a) : n(a) {}

  ~check_dtor() {
    std::println("Destructor called {:d}.", n);
  }
};

int main() {
  auto _ = check_dtor{1};
  auto _ = check_dtor{2};

  {
    auto _ = check_dtor{3};
  }

  auto _ = check_dtor{4};
}
```
```
Destructor called 3.
Destructor called 4.
Destructor called 2.
Destructor called 1.
```

- [[C++] clang HEAD 18.0.0 (https://github.com/llvm/llvm-project.git 57a0416e0e8ccd522d4242dbe5d0d7893864a10a) - Wandbox](https://wandbox.org/permlink/cjf5gmJoT4h6CM68)

デストラクタがトリビアルな型の場合は最適化によってスタック上から消し去られる可能性はありますが、C++の意味論としては`_`変数に束縛されたオブジェクトが即座に破棄されることはありません。

これはまた、`[[nodiscard]]`な戻り値を破棄するテクニックとの違いでもあります。

```cpp
[[nodiscard]]
auto f() -> int;

int main() {
  // いずれも警告されない
  auto _ = f();       // 戻り値は破棄されていない
  (void)f();          // 戻り値はこの行で破棄される
  std::ignore = f();  // 戻り値はこの行で破棄される
}
```

このようになっているのは、RAII以外の役割を持たない型のオブジェクトに対する変数名として`_`を使用できるようにすることを意図しているためです。

```cpp
std::mutex mtx{};

auto f() {
  // lock_guardのオブジェクトはRAIIのためだけに必要
  std::lock_guard _{mtx};

  ...
}

auto g() {
  using namespace std::experimental;

  // scope_exitのオブジェクトもRAIIのためだけに必要
  scope_exit _{[]() { ... }};

  ...
}
```

`std::lock_guard`等による`std::mutex`のロックが分かりやすいと思いますが、これらのオブジェクトはRAIIのためだけに宣言が必要であり、初期化後にアクセスする必要が全くありません。従来はこのような変数に対しても名前を付ける必要があり、そのようなものが同じスコープに複数ある場合は特に命名に少し面倒さがありました。そこに`_`を使用することで、このようなRAIIオブジェクトがいくつあったとしても1つの共通の意味を持つ名前を使用できるようになります。

このようなRAIIオブジェクトの変数名のために`_`を使用するようにする場合、`_`の初期化の行でそのオブジェクトが即破棄されると意図通りになりません。そのため、`_`変数名で初期化されているときでも、そのオブジェクト実体の破棄順序は通常と同じになっています。

### 後方互換について

C++23以前から、`_`そのものは任意のC++エンティティの名前（変数名や関数名など）として使用することができました。とはいえ、変数名として使用した時にはあるスコープに一度しかその名前は出現できなかったので、ローカルの`_`変数名の再宣言を許可する仕様変更に問題はありません。また、この`_`変数名は必ず変数宣言として導入されるため、他の名前に使用されていてもローカルスコープでは`_`という他の名前を隠蔽するだけです。

ただし、`_`変数名が一度しか宣言されていない場合は従来意図して`_`を使用していたコードの動作を変えないために、`_`は通常の変数名とほぼ変わりなく扱われており、複数回宣言された場合にのみその使用がコンパイルエラーとなるようにされています。

この機能の導入に当たって、`_`という名前が実際に使用されているのかどうかが調査されたところ、2つの例が見つかりました。まず1つはGoogl Mockというライブラリで、グローバル変数名として使用されていました。

```cpp
// Google Mockにおける_使用例
namespace testing {
  
  const internal::AnythingMatcher _ = {};

}
```

この正当な利用例を妨げないようにするために、C++26の`_`変数名の特別扱いは関数スコープにのみ制限されています。

2つ目は、Gettextというライブラリを使用するプロジェクトにおいてのもので、そこでは`_`はGettextのラッパの関数マクロとしてよく使用されています。

```cpp
#define _(msgid) gettext (msgid)
```

ただしこれは、Gettextライブラリヘッダ自体が提供するものではなく、あくまでその利用側での慣習として良く定義されているものです。また、この場合は関数マクロであるので、この機能の`_`の利用に支障はありません。

```cpp
constexpr const char* gettext(int) { return nullptr;}
#define _(msgid) gettext (msgid)

int main() {
  constexpr auto _ = _(42); // ok
  auto _ = 42;  // ok
  static_assert(_ == nullptr);  // ng
}
```

### 参考文献

- [P2169R4 A nice placeholder with no name](https://open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2169r4.pdf)
- [破棄 - 未代入の破棄可能な変数 - C# | Microsoft Learn](https://learn.microsoft.com/ja-jp/dotnet/csharp/fundamentals/functional/discards)
- [Rustの変数名におけるアンダースコアの意味 | rs.nkmk.me](https://rs.nkmk.me/rust-underscore-variable/)