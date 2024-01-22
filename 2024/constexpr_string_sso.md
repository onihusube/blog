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

using namespace std::ranges;

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

### SSO

```cpp
#include <string>
#include <concepts>
#include <ranges>
#include <print>

constexpr auto make_string(char init, std::unsigned_integral auto N) -> std::string {
  std::string str;
  
  for (auto i : std::views::iota(init, init + char(N))) {
    str += i;
  }

  return str;
}

int main() {
  constexpr std::string cstr = make_string('a', 10u);

  std::println("{:s}", cstr);
}
```

### 最大文字数

### 参考文献

- [C++20 可変サイズをもつコンテナのconstexpr化 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/more_constexpr_containers.html)
- [c++ - C++20 constexpr vector and string not working - Stack Overflow](https://stackoverflow.com/questions/69498115/c20-constexpr-vector-and-string-not-working?noredirect=1&lq=1)
