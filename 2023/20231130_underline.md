# ［C++］ 名前に依存しない変数宣言 

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
  auto _ = 0;

  std::cout << _ << '\n'; // ok、この時点では使用可能

  auto _ = 1.0;

  std::cout << _ << '\n'; // ng
  _ = f();    // ng
  int n = _;  // ng
  h(_);       // ng
}
```

この場合、`_`は変数名として宣言することにのみ使用できます。

このように、C++26における変数名`_`は

### name-independent declaration

### 破棄のタイミング

C#やRustなどの`_`変数名と異なる点として、C++26の`_`変数名は値の破棄を意味していません。あくまで、その変数（オブジェクト）の利用に興味がないことを意味しています。

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

### 使用例
### 後方互換について

### パターンマッチング

### 参考文献

- [P2169R4 A nice placeholder with no name](https://open-std.org/jtc1/sc22/wg21/docs/papers/2023/p2169r4.pdf)
- [Rustの変数名におけるアンダースコアの意味 | rs.nkmk.me](https://rs.nkmk.me/rust-underscore-variable/)
- [破棄 - 未代入の破棄可能な変数 - C# | Microsoft Learn](https://learn.microsoft.com/ja-jp/dotnet/csharp/fundamentals/functional/discards)