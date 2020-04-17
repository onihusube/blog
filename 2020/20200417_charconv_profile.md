# ［C++］<charconv>って実際どうなの？

`<charconv>`ヘッダはC++17から導入されたヘッダで、ロケール非依存、動的確保なし、例外なげない、などを謳うといういいことづくめで高速な文字列⇄数値変換を謳う関数が提供されています。現在フルで実装しているのはMSVCだけですが、実際速いってどのくらいなの？既存の手段と比べてどうなの？？という辺りが気になったので調べてみた次第です。

### 計測環境

- Core i7 7700T HT有効OCなしTBあり 16GBメモリ
- Windows 10 1909 8363.720
- VisualStudio 2019 update 6 preview 2

### `std::to_chars()`

[`std::to_chars()`](https://cpprefjp.github.io/reference/charconv/to_chars.html)は数値を文字列へ変換する関数です。出力は`char`の文字列限定で、戻り値を調べることでエラーの有無と文字列長が分かります。

これとの比較対象は以下のものです。

- `std::to_string()`
- `std::stringstream`
- `snprintf()`

#### 測定方法

100万件のランダムな数値を用意してそれを1つづつ全件変換にかけ、それにかかる時間を計測します。それを10回繰り返して各種統計量で見てみることにします。整数型（64bit整数型）と浮動小数点型（`double`）それぞれで実験を行います。

コードは以下のようになります。

```cpp
#include <iostream>
#include <charconv>
#include <vector>
#include <random>
#include <chrono>
#include <type_traits>
#include <cassert>
#include <thread>
#include <numeric>
#include <string>
#include <sstream>

template<typename NumericType>
auto make_data(unsigned int N) -> std::vector<NumericType> {
  
  auto rng = []() {
    if constexpr (std::is_integral_v<NumericType>) {
      return std::uniform_int_distribution<NumericType>{};
    } else if constexpr (std::is_floating_point_v<NumericType>) {
      return std::uniform_real_distribution<NumericType>{};
    } else {
      static_assert([] { return false; }, "You have to specify a number type, right?");
    }
  }();
  
  std::mt19937_64 urbg{ std::random_device{}() };
  
  std::vector<NumericType> vec;
  vec.reserve(N);

  for (auto i = 0u; i < N; ++i) {
    vec.emplace_back(rng(urbg));
  }

  return vec;
}

template<typename Container>
void report(Container&& container) {
  const auto first = std::begin(container);
  const auto last = std::end(container);
  const auto N = std::size(container);

  using value_type = typename std::iterator_traits<std::remove_const_t<decltype(first)>>::value_type;

  std::sort(first, last);

  const auto max = *(last - 1);
  const auto min = *first;

  std::cout << "min : " << min.count() << " [ms]" << std::endl;
  std::cout << "max : " << max.count() << " [ms]" << std::endl;

  const auto medpos = first + (N / 2);
  std::cout << "median : " << (*medpos).count() << " [ms]" << std::endl;
  
  const auto sum = std::accumulate(first, last, value_type{});
  const auto ave = sum.count() / double(N);
  std::cout << "average : " << ave << " [ms]" << std::endl;

  const auto var = std::inner_product(first, last, first, 0ll, std::plus<>{},
    [](auto& lhs, auto& rhs) {return lhs.count() * rhs.count(); }) / N - (ave * ave);
  std::cout << "stddev : " << std::sqrt(var) << "\n" << std::endl;
}

template<typename NumericType, typename F>
void profiling(const char* target, F&& func) {
  using namespace std::chrono_literals;

  constexpr int trialN = 10;
  constexpr int sampleN = 1'000'000;

  std::chrono::milliseconds results[trialN]{};

  for (int i = 0; i < trialN; ++i) {
    //データの準備
    auto input = make_data<NumericType>(sampleN);

    //計測開始
    auto start = std::chrono::steady_clock::now();

    for (auto v : input) {
      func(v);
    }

    //計測終了
    auto end = std::chrono::steady_clock::now();
    results[i] = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::this_thread::sleep_for(200ms);
  }

  std::cout << target << std::endl;
  report(results);
}

int main()
{
  char buf[21];
  auto first = std::begin(buf);
  auto last = std::end(buf);

  profiling<std::int64_t>("to_chars() int64", [first, last](auto v) {
    auto [ptr, ec] = std::to_chars(first, last, v);
    if (ec != std::errc{}) assert(false);
  });
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ZFA3mSxacVarkUOh)

[全部入りのコードはこちら](https://gist.github.com/onihusube/38ed1a853ec8d58fd76a7b55f80d0dcf)

#### 整数（`std::int64_t`）

|方法|最小値|最大値|中央値|平均値|標準偏差|
|:---|:---:|:---:|:---:|:---:|:---:|
|`std::to_chars()`||||||
|`std::to_string()`||||||
|`std::stringstream`||||||
|`snprintf()`||||||

#### 浮動小数点数（`double`）

|方法|最小値|最大値|中央値|平均値|標準偏差|
|:---|:---:|:---:|:---:|:---:|:---:|
|`std::to_chars()`||||||
|`std::to_string()`||||||
|`std::stringstream`||||||
|`snprintf()`||||||

### `std::from_chars()`

[`std::from_chars()`](https://cpprefjp.github.io/reference/charconv/from_chars.html)は文字列から数値へ変換するものです。入力は`char`の文字列限定で出力は引数に取った数値型変数への参照で返します。戻り値の扱いなどは`to_chars()`と似た感じです。

これとの比較対象は以下のものです。

- `std::stoll()`
- `std::stringstream`
- `sscanf()`
- `strtoll()`


#### 測定方法

100万件のランダムな数値を`to_chars()`で文字列に変換しておき、それを全件変換にかけかかる時間を計測します。それを10回繰り返して各種統計量で見てみることにします。整数型（64bit整数型）と浮動小数点型（`double`）それぞれで実験を行います。

先ほどの処理と似たようなことになります。

```cpp
#include <iostream>
#include <charconv>
#include <vector>
#include <random>
#include <chrono>
#include <type_traits>
#include <cassert>
#include <thread>
#include <numeric>
#include <string>
#include <string_view>

template<typename NumericType>
auto make_data(unsigned int N) -> std::pair<std::vector<char>, std::vector<std::string_view>> {
  
  auto rng = []() {
    if constexpr (std::is_integral_v<NumericType>) {
      return std::uniform_int_distribution<NumericType>{};
    } else if constexpr (std::is_floating_point_v<NumericType>) {
      return std::uniform_real_distribution<NumericType>{};
    } else {
      static_assert([] { return false; }, "You have to specify a number type, right?");
    }
  }();
  
  std::mt19937_64 urbg{ std::random_device{}() };
  
  std::vector<char> buffer(N * 21);
  auto* pos = buffer.data();
  std::vector<std::string_view> vec;
  vec.reserve(N);

  for (auto i = 0u; i < N; ++i) {
    const auto num = rng(urbg);
    const auto [end, ec] = std::to_chars(pos, pos + 21, num);
    if (ec != std::errc{}) assert(false);
    
    const std::size_t len = end - pos;
    vec.emplace_back(pos, len);
    pos += (len + 1);
  }

  return {std::move(buffer), std::move(vec)};
}

/*
report()関数は変更ないので省略
*/

template<typename NumericType, typename F>
void profiling(const char* target, F&& func) {
  using namespace std::chrono_literals;

  constexpr int trialN = 10;
  constexpr int sampleN = 1'000'000;

  std::chrono::milliseconds results[trialN]{};

  for (int i = 0; i < trialN; ++i) {
    //データの準備
    auto [buf, input] = make_data<NumericType>(sampleN);

    //計測開始
    auto start = std::chrono::steady_clock::now();

    for (auto sv : input) {
      func(sv);
    }

    //計測終了
    auto end = std::chrono::steady_clock::now();
    results[i] = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    std::this_thread::sleep_for(200ms);
  }

  std::cout << target << std::endl;
  report(results);
}


int main()
{
  std::int64_t v;
  
  profiling<std::int64_t>("to_chars() int64", [&v](auto sv) {
    auto [ptr, ec] = std::from_chars(sv.begin(), sv.end(), v);
    if (ec != std::errc{}) assert(false);
  });
}
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/iBR7pEd38rpzZddM)

#### 整数（`std::int64_t`）

|方法|最小値|最大値|中央値|平均値|標準偏差|
|:---|:---:|:---:|:---:|:---:|:---:|
|`std::from_chars()`||||||
|`std::stoll()`||||||
|`std::stringstream`||||||
|`sscanf()`||||||
|`strtoll()`||||||

#### 浮動小数点数（`double`）

|方法|最小値|最大値|中央値|平均値|標準偏差|
|:---|:---:|:---:|:---:|:---:|:---:|
|`std::from_chars()`||||||
|`std::stoll()`||||||
|`std::stringstream`||||||
|`sscanf()`||||||
|`strtoll()`||||||

### グラフで見てみる

#### `std::to_chars()`
#### `std::from_chars()`

### 参考文献

- [`<charconv>` - cpprefjp](https://cpprefjp.github.io/reference/charconv.html)
- [【修正あり】基本統計量をC++で計算してみる - Qita](https://qiita.com/YSRKEN/items/ffe55c93213e3fd886c4)