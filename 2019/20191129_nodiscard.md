#  ［C++］ [[nodiscard]]の言いたいこと


### 関数の戻り値に対する[[nodiscard]]

一番基本的な使い方です。この場合は単に戻り値を捨てないでね？という意思表示をし、それをコンパイラに通知してもらいます、そのままです。

```cpp

[[nodiscard]] int f() {
  return 0;
}

int main() {
  f();  //コンパイラが警告を出してくれるはず
}
```

### 型に対する[[nodiscard]]

`[[nodiscard]]`は実は型に対してもつけることができます。

```cpp
struct [[nodiscard]] S {
  int status;
};

S f() {
  return {};
}


int main() {
  f();  //コンパイラが警告をしてくれるはず
}
```

結局は関数の戻り値となるときにだけ意味を持つのですが、この場合の`[[nodiscard]]`のお気持ちは`S`のオブジェクトを破棄しないでね？という意味です。

従って、オブジェクトを返さない場合は特にエラーになりません。

```cpp
struct [[nodiscard]] S {
  int status;
};

const S& f() {
  static S s{};
  return s;
}


int main() {
  f();  //コンパイラは警告しない
}
```

戻り値を捨てて欲しく無いのではなく、`S`のオブジェクトを捨てて欲しく無いのです・・・

### コンストラクタに対する[[nodiscard]]

`[[nodiscard]]`はコンストラクタに対してもつけることができ（るようになり）ます。

```cpp
struct S {
  [[nodiscard]] S(int st) : status{st}
  {}

  S() = default;

  int status;
};

S f() {
  return {};
}

S f() {
  return {1};
}


int main() {
  f();  //コンパイラは警告しない
  g();  //コンパイラが警告をしてくれるはず
}
```

実はC++17時点では`[[nodiscard]]`はコンストラクタに対して意味を持ちませんでしたが、C++20でこれが修正され明確な意味を持つようになりました。  
ただし、C++17に対する欠陥修正であるためC++17にさかのぼって適用されます。しかし、GCC以外はどうやらこれに対応していなかったようなので、実質的に使えるのは++20からになります。

### 理由を添える[[nodiscard]]

### 参考文献
- [`[[nodiscard]]`属性 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/nodiscard.html)
- [属性: nodiscard - cppreference.com](https://ja.cppreference.com/w/cpp/language/attributes/nodiscard)
- [コンストラクタに `[[nodiscard]]` が使えるように (P1771R1) - cppmap](https://cppmap.github.io/standardization/cpp20/#nodiscard-p1771r1)
- [P1771R1 `[[nodiscard]]` for constructors (DR)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1771r1.pdf)
- [P1301R4 `[[nodiscard("should have a reason")]]`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1301r4.html)