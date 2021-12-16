# ［C++］std::stringをキーとする（非順序）連想コンテナでHeterogeneous Overloadを有効化する

この記事は[C++ Advent Calendar 2021](https://qiita.com/advent-calendar/2021/cxx)の17日目の記事です。

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

ところが、Heterogeneous Overloadを使用するためには`Key`と比較可能な型の値を渡すだけではだめで、連想コンテナならば比較クラス`Compare`に、非順序連想コンテナならばそれに加えてハッシュクラス`Hash`に、`is_transparent`メンバ型が定義されていて、`Key`と異なる型との直接比較および一貫したハッシュ生成をサポートしている必要があります。。

悲しいことに、互換性のためにデフォルトの比較クラス（`std::less<Key>, std::equal_to<Key>`）は比較がテンプレートではないため異なる型との直接比較ができず、ハッシュクラス（`std::hash<Key>`）には`is_transparent`メンバ型が定義されていないため、デフォルトではHeterogeneous Overloadは有効になりません。そのため、Heterogeneous Overloadを有効化するためには、自分で要件が満たされるように一工夫しなければなりません・・・

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

`std::string_view`をそのまま受け取れないのは、`std::string_view`から変換する`std::string`のコンストラクタに`explicit`が付加されているためです。静かなパフォーマンス低下を長文コンパイルエラーで教えてくれるのでとても親切だといえるでしょう・・・

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

連想コンテナ（`std::set, std::map`とその`multi`バージョン）の場合、問題となるのはデフォルトの比較クラスがテンプレートパラメータに指定された型の比較しかできず`is_transparent`を持っていないことだけです。デフォルトの比較クラス`std::less`等はなぜか`void`に対する特殊化に対してのみ`is_transparent`が定義される（比較がテンプレートになる）のでそれを使ってもいいですし、C++20からなら`std::ranges`にある比較クラスを使ってもいいでしょう。

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <map>
#include <functional> // ranges::lessとかはここにある

using namespace std::literals;

int main() {
  std::cout << std::boolalpha;

  std::map<std::string, int, std::ranges::less> map = { {"1", 1}, {"2", 2}, {"3", 3} };

  std::cout << (map.find("1"sv) != map.end()) << std::endl; // OK
  std::cout << (map.find("4") != map.end()) << std::endl;   // OK
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/9oQ6QUE9ntguOPaC)

これだけで連想コンテナはHeterogeneous Overloadを有効化できます。当然どちらのケースでも`std::string`の一時オブジェクトは生成されておらず、直接比較されています（はずです）。`std::ranges::less`の代わりに`std::less<void>`を使用しても大丈夫です、お好みでどうぞ。

`std::ranges::map`みたいな感じでこれを標準で用意してほしいものです。

### 非順序連想コンテナ

非順序連想コンテナ（`std::unorderd_map, std::unorderd_set`とその`multi`バージョン）の場合、比較クラスに加えてハッシュクラスも問題となります。残念ながらハッシュクラスに関しては自分で定義をするしかありません・・・

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <map>
#include <functional>

using namespace std::literals;

struct string_hash {
  using hash_type = std::hash<std::string_view>;
  using is_transparent = void;

  std::size_t operator()(std::string_view str) const {
    return hash_type{}(str);
  }
};

int main() {
  std::cout << std::boolalpha;

  std::unordered_map<std::string, int, string_hash, std::ranges::equal_to> map = { {"1", 1}, {"2", 2}, {"3", 3} };

  std::cout << (map.find("1"sv) != map.end()) << std::endl; // OK
  std::cout << (map.find("4") != map.end()) << std::endl;   // OK
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/8YnlrqsRVF5KNObn)

少し面倒ですが、`std::hash`をそのまま利用してやればハッシュを独自実装する必要はありません。ハッシュクラス（`string_hash`）の`operator()`の引数型を`std::string_view`にしておけば、`const char*, std::string, std::string_view`の3つを受け取ることができます。

`std::string`系の文字列クラスならこうすればいいのですが、他の型の場合はハッシュ共通化が難しい場合もあるかもしれません。そういう場合は自分でハッシュ実装をする必要がありそうです。

#### `const char*, std::string, std::string_view`のハッシュ一貫性保証

ところで、上記のように`const char*, std::string`のハッシュ値を`std::string_view`から計算することに問題はないのでしょうか？

これは保証されていて、[[basic.string.hash]/1](http://eel.is/c++draft/string.classes#basic.string.hash-1)によれば

> If `S` is one of these string types, `SV` is the corresponding string view type, and `s` is an object of type `S`, then `hash<S>()(s) == hash<SV>()(SV(s))`.

とあります。

要は、事前定義されている各種`std::basic_string`のハッシュ値と、それに対応する`string_view`のハッシュ値は一致すると言っています。


また、[[string.view.hash]/1](http://eel.is/c++draft/string.view#hash-1.sentence-2)にも

> The hash value of a string view object is equal to the hash value of the corresponding string object ([basic.string.hash]). 

と、同じことを逆方向から確認しています。`const char*`の文字列も`std::string/std::string_view`を経由して考えれば同じ結論となるので、各種文字列のハッシュ値はその型によらず一致することが分かります。

どうやらこれはC++17から規定されたもののようですが、この規定によって変更が必要になるとすればそれは破壊的となるはずなので、おそらく実装がそうなっていたことを規格に反映しただけで、以前から同様の保証は暗黙的に存在していたと思われます。

### （非順序）連想コンテナのHeterogeneous Overload

Heterogeneous Overloadは、連想コンテナの検索系の関数（`find(), count(), lower_bound(), upper_bound(), equal_range()`）に対してC++14で追加され（N3657）、続いてC++20にて非順序連想コンテナの検索系関数に対しても追加されました（P0919）。

C++23ではさらに、全ての連想コンテナの削除（`erase()`）とノードハンドルの取り出し（`extract()`）に対してもHeterogeneous Overloadが追加されました（P2077）。

さらに、挿入系の操作（`insert(), insert_or_assign(), try_emplace(), bucket()`）についてもHeterogeneous Overloadを追加する提案が進行中で（P2363）、まだ入ってはいませんがC++23を目指しています。これが入ると`Key`を指定するタイプの操作のほぼ全てでHeterogeneous Overloadを使用可能となるため、それにアダプトする方法および`std::string`と`std::string_view`使用時の問題について頭の隅にとどめておく重要性が高まるでしょう。

### 参考文献

- [N3657 Adding heterogeneous comparison lookup to associative containers (rev 4)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2013/n3657.htm)
- [P0919R3 Heterogeneous lookup for unordered containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0919r3.html)
- [P2077R3 Heterogeneous erasure overloads for associative containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2077r3.html)
- [P2363R1 Extending associative containers with the remaining heterogeneous overloads](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2363r1.html)
- [`std::unordered_map<Key, T, Hash, KeyEqual, Allocator>::find` - cppreference](https://en.cppreference.com/w/cpp/container/unordered_map/find)
- [`std::hash (std::string, std::wstring, std::u16string, std::u32string, std::u8string, std::pmr::string, std::pmr::wstring, std::pmr::u16string, std::pmr::u32string, std::pmr::u8string)` - cppreference](https://en.cppreference.com/w/cpp/string/basic_string/hash)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2021/20211217_heterogenius_lookup_for_string.md)
