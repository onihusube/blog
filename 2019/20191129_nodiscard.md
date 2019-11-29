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

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/PANooicFTC95qXkB)

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
  S{};  //警告してくれるはず・・・
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xX3AGWkj3h6dUHXh)

関数の戻り値となるときには似たような意味を持つことになるのですが、この場合の`[[nodiscard]]`のお気持ちは`S`のオブジェクトを捨てないでね？という意味です。

従って、関数からオブジェクトを返さない場合は特にエラーになりません。

```cpp
struct [[nodiscard]] S {
  int status;
};

const S& f() {
  static S s{};
  return s; //参照を返す
}


int main() {
  f();  //コンパイラは警告しない
}
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/pMdl0RMTZ63oUnNV)

戻り値を捨てて欲しく無いのではなく、`S`のオブジェクトを捨てて欲しく無いことを表明するのです。

### コンストラクタに対する[[nodiscard]]

`[[nodiscard]]`はコンストラクタに対してもつけることができ（るようになり）ます。

```cpp
struct S {
  int status;

  [[nodiscard]] S(int st) : status(st) {}

  S() = default;
};

S f() {
  return {};
}

S g() {
  return {1};
}


int main() {
  f();  //コンパイラは警告しない
  g();  //コンパイラが警告をしてくれる・・・と、思うじゃん？

  S{};  //コンパイラは警告しない
  S{1}; //コンパイラが警告をしてくれるはず
}
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/v1W3Vmo0TTRtLfxL)

この場合は特定のコンストラクタを通して構築されたときは、そのオブジェクトを捨てないでね？という意味になります。  
状況によってはオブジェクトを捨てても良いけど、また状況によっては捨て欲しくないことを表明します。エラーを表現する型やリソースを保持するような型などに利用するといいかもしれません・・・

しかし、上記`g()`の呼び出しのように関数の戻り値になった時は特に警告してくれないようです、罠っぽいです・・・

ちなみに、C++17時点では`[[nodiscard]]`はコンストラクタに対して意味を持ちませんでしたが、C++20でこれが修正され明確な意味を持つようになりました。  
ただし、C++17に対する欠陥修正であるためC++17にさかのぼって適用されます。しかし、GCC以外はどうやらこれに対応していなかったようなので、実質的に使えるのはC++20からになります。

### 理由を添える[[nodiscard]]

C++20より、`[[nodiscard("Why did you throw it away?")]]`のように戻り値ないしはオブジェクトを捨ててほしくない理由を書いておくことができるようになります。   
これを利用すると、上記のように暗黙的なお気持ち表明に頼らずに`[[nodiscard]]`の意図を表明できます。

```cpp
struct [[nodiscard("Will i die?")]] S {
  int status;
};

[[nodiscard("Look carefully!")]]
int f() {
  return 0;
}

S g() {
  return {};
}


int main() {
  f();  //コンパイラが警告をしてくれるはず
  g();  //コンパイラが警告をしてくれるはず

  S{};  //コンパイラが警告をしてくれるはず
  S{1}; //コンパイラが警告をしてくれるはず
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BFy6Qkrip8iJmYui)

大変良いので積極的に利用したいですね、早くC++20に移行しましょう！

ちなみに、これを利用するとコンパイラの警告メッセージにかわいいAAを貼れます。まあ`static_assert`でもできるので今更です・・・  
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/XZJsETNZSONCJDlI)



### 参考文献
- [`[[nodiscard]]`属性 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/nodiscard.html)
- [属性: nodiscard - cppreference.com](https://ja.cppreference.com/w/cpp/language/attributes/nodiscard)
- [コンストラクタに `[[nodiscard]]` が使えるように (P1771R1) - cppmap](https://cppmap.github.io/standardization/cpp20/#nodiscard-p1771r1)
- [P1771R1 `[[nodiscard]]` for constructors (DR)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1771r1.pdf)
- [P1301R4 `[[nodiscard("should have a reason")]]`](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1301r4.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20191129_nodiscard.md)