# ［C++］ std::arrayで各要素に対してリスト初期化したいとき

[:contents]

### `std::pair`の配列の初期化で

`std::array<std::pair<int, int>, N>`のような配列を初期化する場合、何も考えずに書くとこうなるかもしれません

```cpp
#include <array>
#include <utility>

int main() {
  // エラーになる
  std::array<std::pair<int, int>, 3> array = {
    {1, 1},
    {2, 2},
    {3, 3}
  };
}
```
https://wandbox.org/permlink/x6Tx9OdzlnT7hfgW

しかしこれはエラーになります。一方で`std::vector`で同じ事をしようとしてもエラーにはなりません。

```cpp
#include <vector>
#include <utility>

int main() {
  // エラーにならない
  std::vector<std::pair<int, int>> vec = {
    {1, 1},
    {2, 2},
    {3, 3}
  };
}
```
https://wandbox.org/permlink/tOYVbD2ZWSA68A7v

また同様に、生配列にしてもやはりエラーになりません。

### 集成体メンバを持つ集成体であること

先程のエラーになるコードは次のように書き直すと意図通りに初期化されるようになります

```cpp
#include <array>
#include <utility>

int main() {
  std::array<std::pair<int, int>, 3> array = {{
    {1, 1},
    {2, 2},
    {3, 3}
  }};
}
```

https://wandbox.org/permlink/cSDErraBVbLQZI5C

これは`std::array`が集成体であることから来ています。

`std::array`はおおよそ次のような構造をしています

```cpp
template<typename T, std::size_t N>
struct array {
  T m_array[N];

  ...
}:
```

`std::array`は集成体となるように実装されているのですが、そのメンバの内部配列もまた集成体です。そして、この構造を見ると分かるかもしれませんが、直したコードの余分な`{}`はこの内部配列のための初期化子リストを指定するものです。これは例えば同じような構造の集成体にもう一つメンバを追加してみると分かりやすいかもしれません。

```cpp
struct S {
  int arr[3];
  double d;
};

int main() {
  S s1{{1, 2, 3}, 4.0};  // ok
  S s2{ 1, 2, 3 , 4.0};  // ok（警告されるかも
  S s3{{1, 2, 3}, {4.0}};  // ok（警告されるかも
}
```

当初の`std::array`はむしろ初期化時に`{{...}}`とするしかなかったのですが、C++14において多次元配列がこれを省略できる事を拡張する形で、集成体の初期化時にその各メンバに対応する初期化子リストの`{}`を1つ省略できるようになりました。これによって、`std::array`は通常使用するように初期化子リストで自然に初期化できるようになったわけです。

しかし、今回のようにその要素型がクラス型でありコンストラクタ引数に複数の値を渡したい場合には逆に`{}`を使用できなくしています。すなわち、一番最初の例において、初期化子リスト内に含まれている初期化子のうち、最初の1つが`std::array`の内部配列の初期化子として扱われ（この場合はその時点で初期化できないのでエラー）、残りの初期化子は対応する要素がない余分なものとなっています。

```cpp
std::array<std::pair<int, int>, 3> array1 = {
  {1, 1}, // std::array内部配列の初期化子リスト
  {2, 2}, // 余分な初期化子
  {3, 3}  // 余分な初期化子
};

std::array<std::pair<int, int>, 3> array2 = {
  // std::array内部配列の初期化子リスト
  {
    {1, 1}, // 1つめの要素の初期化子
    {2, 2}, // 2つめの要素の初期化子
    {3, 3}  // 3つめの要素の初期化子
  }
};

std::array<std::pair<int, int>, 3> array3 = {
  1, 1, // 1つめと2つめの要素の初期化子（pair<int, int>は最低2つ初期化子がいるのでエラー）
  2, 2, // 3つめと4つめの要素の初期化子
  3, 3  // 5つめと6つめの要素の初期化子
};
```

集成体の直接の要素への`{}`が省略されている場合はコンパイラがよしなに初期化子リストの境界を推定してくれますが、その要素のさらに内部のクラス型のコンストラクタ引数の境界まではさすがに面倒を見てくれません。その場合、引数1つから初期化できるならエラーにはならない場合もあります（上記`array3`の例だと、`std::pair<int, int>`が1つの値から初期化でき、要素数が6以上ならエラーにならない）。

ここまでは`std::pair`で説明してきましたが、これはより一般のクラス型において起こります。より正確には、クラス型を要素とする`std::array`の要素を2つ以上の引数を与えて初期化しようとすると、同じことが起きます。

```cpp
std::array<std::vector<int>, 3> ng1 = {
  {1, 2, 3},
  {4, 5},
  {6, 7, 8, 9}
};

std::array<std::string, 3> ng2 = {
  {"string", 1},
  {"string", 2},
  {"string", 3},
};

std::array<std::array<int, 3>, 3> ng3 = {
  {1, 2, 3},
  {4, 5, 6},
  {7, 8, 9}
};
```

これらの例を改善するには、全ての場合において一番外側の初期化リストにもう1つ`{}`を追加します。

このことは`std::array`の内部構造がうっすらと隠されていることによって余計に分かりづらくなっており、あまりにも基本的過ぎるために出会ったときに多少の驚きがあります（ありました）。

### 参考文献

- [ネストする集成体初期化における波カッコ省略を許可 [N3653] - cpprefjp](https://cpprefjp.github.io/lang/cpp14/brace_elision_in_array_temporary_initialization.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2024/20241031_array_curly_brackets.md)
