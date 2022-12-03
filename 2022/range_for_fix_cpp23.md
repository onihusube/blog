# ［C++］地に足のついた範囲forの夢

問題です。次のコードには未定義動作が少なくとも1つ含まれています。それは何でしょう？

```cpp
#include <vector>
#include <string>

// どこかで定義されているとして
auto f() -> std::vector<std::string>;

int main() {
  for (auto&& str : f()) {
    std::cout << str << '\n';
  }

  for (auto&& c : f().at(0)) {
    std::cout << c << ' ';
  }
}
```

以下、この記事ではここの`f()`をたびたび再利用しますが、宣言は再掲しません。

[:contents]

### 答え

```cpp
#include <vector>
#include <string>

auto f() -> std::vector<std::string>;

int main() {
  for (auto&& str : f()) {
    std::cout << str << '\n';
  }

  for (auto&& c : f().at(0)) { // 👈 この行
    //            ^^^^^^^^^   
    std::cout << c << ' ';
  }
}
```

`f()`は`std::string`を要素に持つ`std::vector`の*prvalue*を返す関数です。その戻り値は一時オブジェクトであるので、値として受けるか`auto&&`で受けるなどして寿命を延長する必要があります。範囲`for`文でもそれは行われるので、最初の`for`文は問題ありません。

ところが、2つ目の`for`文は`f()`の戻り値からその要素を引き出しています。ここで問題なのは、要素数が不明なことではありません。`f().at()`の戻り値は*lavlue*（`std::string&`）であり、範囲`for`はこの結果のオブジェクトだけを保存してループを廻してくれます。その結果、`f()`の直接の戻り値は`f().at(0)`の後で捨てられ、当然ここから取得した`std::string&`の参照はダングリング参照となります。

### なぜ？

範囲`for`文はシンタックスシュガーであり、その実態は通常の`for`文によるコードへ展開される形で実行されます。

例えば、規格においては範囲`for`の構文はつぎのように規定されています

```
for ( init-statement(opt) for-range-declaration : for-range-initializer ) statement
```

`init-statement`は`for`の初期化式（[C++20 初期化式をともなう範囲for文](https://cpprefjp.github.io/lang/cpp20/range-based_for_statements_with_initializer.html)）で`(opt)`は省略可能であることを表します。

`for-range-declaration`は`for(auto&& v : r)`の`auto&& v`の部分で、`for-range-initializer`は`r`の部分です。

残った`statement`は`for`文の本体です。

そして、これは次のように展開されて実行されます

```
{
	init-statement(opt)

	auto &&range = for-range-initializer ;  // イテレート対象オブジェクトの保持
	auto begin = begin-expr ; // std::begin(range)相当
	auto end = end-expr ;     // std::end(range)相当
	for ( ; begin != end; ++begin ) {
		for-range-declaration = * begin ;
		statement
	}
}
```

つまりはうまい事イテレータを使ったループに書き換えているわけです。そして、問題は展開後ブロックの3行目にあります。

```cpp
auto &&range = for-range-initializer ;
```

この式では、`auto&&`で範囲`for`のイテレート対象オブジェクトを受けており、これによって左辺値も右辺値も同じ構文で受けられ、なおかつ右辺値に対しては寿命延長がなされます。ここに先程の`for`文から実際の式をあてはめてみてみましょう。

```cpp
// 1つ目のforから
auto &&range = f() ;  // ✅ ok

// 2つ目のforから
auto &&range = f().at(0) ;  // 💀 UB
```

2つ目の初期化式の何が問題なのかというと、変数`range`に受けられているのは`f().at(0)`の戻り値（`std::string&`）であって、`f()`の直接の戻り値であり`.at(0)`で取り出した`std::string`の本体を所有するオブジェクト（`std::vector<std::string>`）はどこにも受けられていないからです。

このような一時オブジェクトの寿命はその完全式の終わりに尽きる、と規定されていて、それはとても簡単にはその式を閉じる`;`です。すなわち、この2つ目の初期化式では`f()`の戻り値の寿命はこの行で尽き、そこから取り出されたすべての参照はダングリング参照となります。

これを回避するには`f()`の戻り値を直接受けてからその要素を参照すればいいので、例えば上記初期化式を次のようにすればいいわけです

```cpp
auto &&range0 = f();            // ✅ ok
auto &&range = range0.at(0) ;   // ✅ ok
```

ただし、ユーザーコードからでは展開後のコードをこのようにすることはできないので、範囲`for`の構文でできる範囲の事をしなければなりません。

```cpp
int main() {
  {
    // 範囲forの外で受けておく
    auto tmp = f();
    for (auto&& c : tmp) {
      ...
    }
  }

  {
    // 初期化式を利用する
    for (auto tmp = f(); auto&& c : tmp) {
      ...
    }
  }
}
```

C++20で追加された範囲`for`文における初期化式は、この問題の回避策として導入されたものでもあります。

### その他の例

これだけならめでたしめでたしで終わりそうですので、さらに変な例を置いておきます。

```cpp
struct Person {
  std::vector<int> values;

  const auto& getValues() const {
    return values;
  }
};

// prvalueを返す
auto createPerson() -> Person;

for (auto elem : createPerson().values)       // ✅ ok
for (auto elem : createPerson().getValues())  // 💀 UB
```

```cpp
#include <vector>
#include <span>

auto f() -> std::vector<int>;

int main() {
  for (auto n : std::span{f().data(), 2}) {  // 💀 UB
    ...
  }
}
```

```cpp
#include <optional>
#include <string>

auto f() -> std::optional<std::string>;

int main() {
  for (auto c : f().value()) {  // 💀 UB
    ...
  }
}
```

```cpp
#include <variant>
#include <string>

auto f() -> std::variant<std::string, int>;

int main() {
  for (auto c : std::get<std::string>(f())) {  // 💀 UB
    ...
  }
}
```

```cpp
#include <tuple>
#include <string>

auto f() -> std::tuple<std::string, int>;

int main() {
  for (auto c : std::get<0>(f())) {  // 💀 UB
    ...
  }
}
```

```cpp
#include <map>
#include <string>

auto f() -> std::map<int, std::string>;

int main() {
  for (auto c : f()[0]) {  // 💀 UB
    ...
  }
}
```

```cpp
#include <coroutine>
#include <string>

// std::lazyはC++26予定
auto f() -> std::lazy<std::string&>;

std::lazy<> g() {
  for (auto c : co_await f()) {  // 💀 UB（コルーチンローカルのstd::stringへの参照を返す場合）
    ...
  }
}
```

さて、これらの例を見て、これらの問題のあるコードを絶対書かないと断言できるでしょうか？私はやってしまいそうです・・・

初学者やC++言語そのものにさほど興味のないプログラマなど、範囲`for`の仕様を知らない場合はこの問題に気付くことはできないでしょう。この問題を把握するほど詳しい人でも、この問題の起こる場所が範囲`for`に隠蔽されていることによって、ぱっと見て気づくことが難しい場合があるでしょう。

この問題は範囲`for`に初期化子を指定できるようにした程度で解決できるようなものではなく、より本質的な解決策が必要な問題であるといえます。

### C++23における解決

### 紆余曲折

### 参考文献

- [P2644R0 Get Fix of Broken Range-based for Loop Finally Done](https://wg21.link/p2644r0)
- [P2644 Get Fix of Broken Range-based for Loop Finally Done - cplusplus/papers](https://github.com/cplusplus/papers/issues/1316)
- [P2012R0 Fix the range-based for loop, Rev0ix the range-based for loop - WG21月次提案文書を眺める（2020年11月）](https://onihusube.hatenablog.com/entry/2020/12/06/015108#P2012R0-Fix-the-range-based-for-loop-Rev0ix-the-range-based-for-loop)
- [P2644R0 Get Fix of Broken Range-based for Loop Finally Done - WG21月次提案文書を眺める（2022年10月）](https://onihusube.hatenablog.com/entry/2022/11/13/233529#P2644R0-Get-Fix-of-Broken-Range-based-for-Loop-Finally-Done)
