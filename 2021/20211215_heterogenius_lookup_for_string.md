# ［C++］std::stringをキーとする（非順序）連想コンテナでHeterogeneous Overloadを有効化する

### Heterogeneous Overload？

Heterogeneous Overloadというのは、（非順序）連想コンテナ（`C<Key, ...>`）の操作において`Key`と異なる型のオブジェクトをとることのできるオーバーロードのことです。

例えば`std::map::find()`はC++14から次の2つのオーバーロードを持っています（`const`は無視します）

```cpp
iterator find(const key_type& x);             // (1)

template <class K>
iterator find(const K& x);                    // (2) C++14
```

- [`std::map::find` - cpprefjp](https://cpprefjp.github.io/reference/map/map/find.html)


ここで`key_type`とは`std::map<Key, Value>`の`Key`型であり、2つ目のオーバーロードは`Key`と異なる型の任意のオブジェクトを受け取るようになっています。これがHeterogeneous Overloadであり、`key`と比較可能な別の型のオブジェクトを直接用いて値を検索することができ、使いやすさが向上するだけでなく、`Key`の一時オブジェクトを作る必要がないため効率的です。

ところが、Heterogeneous Overloadを使用するためには`Key`と比較可能な型の値を渡すだけではだめで、連想コンテナならば比較クラス`Compare`に、非順序連想コンテナならばそれに加えてハッシュクラス`Hash`に、`is_transparent`メンバ型が定義されていなければなりません。

悲しいことに、互換性のためにデフォルトの比較クラス（`std::less<Key>, std::equal_to<Key>`）およびハッシュクラス（`std::hash<Key>`）には`is_transparent`メンバ型が定義されておらず、デフォルトではHeterogeneous Overloadは有効になりません。そのため、Heterogeneous Overloadを有効化するためには、自分で要件が満たされるように一工夫しなければなりません・・・

ここでは、一番需要が高くてよく出会いそうな`std::string`をキーとする（非順序）連想コンテナについて見ていきます。

#### `std::map<std::string, T>`

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <map>

using namespace std::literals;

int main() {
  std::cout << std::boolalpha;

  std::map<std::string, int> map = { {"1", 1}, {"2", 2}, {"3", 3}};

  std::cout << (map.find("1"sv) != map.end()) << std::endl; // エラー
  std::cout << (map.find("4") != map.end()) << std::endl;   // OK、ただし一時オブジェクトが作成されている
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/nBGVJlhRqZFp5MJn)

`std::string_view`をそのまま受け取れないのは、`std::string_view`から変換する`std::string`のコンストラクタに`explicit`が付加されているためです。静かなパフォーマンス低下を（イミフな）コンパイルエラーという形で教えてくれるのでとても親切だといえるでしょう・・・

#### `std::unordered_map<std::string, T>`

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <map>

using namespace std::literals;

int main() {
  std::cout << std::boolalpha;

  std::map<std::string, int> map = { {"1", 1}, {"2", 2}, {"3", 3}};

  std::cout << (map.find("1"sv) != map.end()) << std::endl; // エラー
  std::cout << (map.find("4") != map.end()) << std::endl;   // OK、ただし一時オブジェクトが作成されている
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LTOl581sdxXYxdmQ)

これもエラーが起きてるのは`map`と同じ理由です。

### 連想コンテナ

連想コンテナの場合、問題となるのはデフォルトの比較クラスが`is_transparent`を持っていないことだけです。デフォルトの比較クラス`std::less`等はなぜか`void`に対する特殊化に対してのみ`is_transparent`が定義されるのでそれを使ってもいいですし、C++20からなら`std::ranges`にある比較クラスを使ってもいいでしょう。

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <map>

using namespace std::literals;

int main() {
  std::cout << std::boolalpha;

  std::map<std::string, int, std::ranges::less> map = { {"1", 1}, {"2", 2}, {"3", 3}};

  std::cout << (map.find("1"sv) != map.end()) << std::endl; // OK
  std::cout << (map.find("4") != map.end()) << std::endl;   // OK
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/9oQ6QUE9ntguOPaC)

これだけで連想コンテナはHeterogeneous Overloadを有効化できます。当然どちらのケースでも`std::string`の一時オブジェクトは生成されておらず、直接比較されています（はずです）。`std::ranges::less`の代わりに`std::less<void>`を使用しても大丈夫です、お好みでどうぞ。

`std::ranges::map`みたいな感じでこれを標準で用意してほしいものです。


### 非順序連想コンテナ


### 連想コンテナのHeterogeneous Overload

### 参考文献

- [N3657 Adding heterogeneous comparison lookup to associative containers (rev 4)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3657.htm)
- [P0919R3 Heterogeneous lookup for unordered containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0919r3.html)
- [P2077R3 Heterogeneous erasure overloads for associative containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2077r3.html)
- [P2363R1 Extending associative containers with the remaining heterogeneous overloads](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2363r1.html)
- [`std::unordered_map<Key, T, Hash, KeyEqual, Allocator>::find` - cppreference](https://en.cppreference.com/w/cpp/container/unordered_map/find)