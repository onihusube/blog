# ［C++］indirectly_writableコンセプトの謎の制約式の謎

`std::indirectly_writable`コンセプトはイテレータによる出力操作を定義するコンセプトで、`std::output_iterator`コンセプトの中核部分を成しています。

```cpp
template<class Out, class T>
concept indirectly_writable = 
  requires(Out&& o, T&& t) {
    *o = std::forward<T>(t);
    *std::forward<Out>(o) = std::forward<T>(t);
    const_cast<const iter_reference_t<Out>&&>(*o) = std::forward<T>(t);
    const_cast<const iter_reference_t<Out>&&>(*std::forward<Out>(o)) = std::forward<T>(t);
  };
```

定義を見てみると、見慣れない構文を用いた良く分からない制約式が入ってるのが分かります。

```cpp
const_cast<const iter_reference_t<Out>&&>(*o) = std::forward<T>(t);
const_cast<const iter_reference_t<Out>&&>(*std::forward<Out>(o)) = std::forward<T>(t);
```

常人ならばおおよそ使うことの無いであろう`const_cast`をあろうことかC++20のコンセプト定義で見ることになろうとは・・・

cpprefjpには

> `const_cast`を用いる制約式は、右辺値に対しても代入できるが`const`な右辺値では代入できなくなる非プロキシイテレータの*prvalue*（例えば`std::string`そのものなど）を返すイテレータを弾くためにある。これによって、間接参照が*prvalue*を返すようなイテレータ型は`indirectly_writable`のモデルとならないが、出力可能なプロキシオブジェクトを返すイテレータは`indirectly_writable`のモデルとなる事ができる。

とあり、規格書にも似たようなことが書いてありますが、なんだかわかったような分からないような・・・

これは一体何を表しているのでしょうか、またどういう意図を持っているのでしょう？

### *prvalue*を返すようなイテレータ

どうやらこれは[range-v3において発見された問題](https://github.com/ericniebler/range-v3/issues/573)に端を発するようです。

```cpp
struct C {
  explicit C(std::string a) : bar(a) {}

  std::string bar;
};

int main() {
  std::vector<C> cs = { C("z"), C("d"), C("b"), C("c") };

  ranges::sort(cs | ranges::view::transform([](const C& x) {return x.bar;}));

  for (const auto& c : cs) {
    std::cout << c.bar << std::endl;
  }
}
```

クラス`C`の`std::vector`を`C`の要素の`std::string`の順序によって並び変えたいコードです。コンパイルは通りますし実行もできますが、順番が並び変わることはありません。

なぜかといえば、`sort`に渡している`vector`を`transform`しているラムダ式の戻り値型が`std::string`の参照ではなく*prvalue*を返しているからです。

割とよくありがちなバグで、戻り値型をきちんと指定してあげれば意図通りになります。

```cpp
ranges::sort(cs | ranges::view::transform([](const C& x) -> std::string& {return x.bar;}));
```

しかし、`ranges::sort`はrange-v3にある`indirectly_writable`コンセプトで制約されているはずで、この様なものは出力可能とは言えず、`indirectly_writable`を満たしてほしくは無いしコンパイルエラーになってほしいものです。

### *prvalue*の区別

この問題は突き詰めると

```cpp
std::string() = std::string();
```

の様な代入が可能となっているという点に行きつきます。

この様な代入操作は代入演算子の左辺値修飾で禁止できるのですが、標準ライブラリの多くの型の代入演算子は左辺値修飾された代入演算子を持っていません。メンバ関数の参照修飾はC++11からの仕様であり、C++11以前から存在する型に対して追加することは出来ず、それらの型に倣う形で他の型でも参照修飾されてはいません。

これを禁止する為の方法は、単純には間接参照の結果が常に真に参照を返すことを要求することです。

その時に問題となるのが、イテレータの間接参照でプロキシオブジェクトが得られるようなイテレータです。当然そのようなプロキシオブジェクトは*prvlaue*なので、出力可能であるはずでも`indirectly_writable`を満たさなくなってしまいます。

そうなると、プロキシオブジェクトを識別してその*prvalue*への出力は許可する必要があります。

プロキシオブジェクトはその内部に要素への参照を秘めているオブジェクトであって、自身の`const`性と参照先の`const`性は無関係です。従って、`const`であるときでも出力（代入）が可能となります。

一方、`std::string`等の型は当然`const`であるときに代入可能ではありません。

そして、イテレータ`o`について、`decltype(*o)`が真に参照を返すとき、そこに`const`を追加しても効果はありません。

これらの事から、間接参照が*prvalue*を返すときにプロキシオブジェクト以外の出力操作を弾くためには、`const_cast`を`decltype(*o)`に対して適用して`const`を付加してから、出力操作をテストすれば良いでしょう。

この結果得られたのが、`indirectly_writable`にある謎の制約式です。

```cpp
template<class Out, class T>
concept indirectly_writable = 
  requires(Out&& o, T&& t) {
    *o = std::forward<T>(t);
    *std::forward<Out>(o) = std::forward<T>(t);
    // ↓これ！
    const_cast<const iter_reference_t<Out>&&>(*o) = std::forward<T>(t);
    const_cast<const iter_reference_t<Out>&&>(*std::forward<Out>(o)) = std::forward<T>(t);
  };
```

`std::forward<Out>`の差で制約式が2本あるのは、`Out`に対する出力操作がその値カテゴリによらない事を示すためです。つまり、*lvalue*は当然として、イテレータそのものが*prvalue*であっても出力操作は可能であり、そうでなければなりません。これは今回の事とはあまり関係ありません。

`iter_reference_t`は`Out`からその間接参照の直接の結果型（`reference`）を取得します。

それが真に参照ならば（その型を`T&`あるいは`T&&`とすれば）、そこに`const`を追加しても何も起こらず、型は`T&`あるいは`T&&`のままとなります。しかし、`iter_reference_t`が*prvalue*ならば（`T`とすれば）素直に追加されて`const T`となります。

ここで起きていることは`using U = T&`に対する`const U`のようなことで、これは`T& const`（参照そのものに対する`const`修飾）となって、これは参照型には意味を持たないのでスルーされています。

最後にそこに`&&`を付加するわけですが、参照が得られているときは`T&&& -> T&`、`T&&&& -> T&&`となります。`*o`が*prvalue*を返すときは`const T&&`となり、`const`右辺値参照が生成されます。

最後にこの得られた型を用いて`*o`を`const_cast`しそこに対する代入をテストするわけですが、この過程をよく見てみれば`*o`が参照を返している場合は実質的に何もしておらず、すぐ上にある制約式と等価となっています。

つまり、この`const_cast`を用いる制約式は`*o`が*prvalue*を返しているときにしか意味を持ちません。そして、`const T&&`なオブジェクトへの出力（代入）ができるのは`T`がプロキシオブジェクト型の時だけとみなすことができます。

この様にして、冒頭のコード例の様に意図せず*prvalue*を返すケースをコンパイルエラーにしつつ、意図してプロキシオブジェクトの*prvalue*を返す場合は許可するという、絶妙に難しい識別を可能にしています。

そして、これこそが問題の制約式の存在意義です。

### `std::vector<bool>::reference`

イテレータの間接参照がプロキシオブジェクトを返すようなイテレータには、`std::vector<bool>`のイテレータがあります。その`reference`は1ビットで保存された`bool`値への参照となるプロキシオブジェクトの*prvlaue*であり、まさに先ほどの議論で保護すべき対象としてあげられていたものです。

が、実際には`std::vector<bool>`のイテレータは`std::indirectly_writable`コンセプトを構文的にすら満たしません。まさにこの`const_cast`を用いる制約式に引っかかります。

```cpp
int main() {
  // 失敗する・・・
  static_assert(std::indirectly_writable<std::vector<bool>::iterator, bool>);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ulZwZiuztDu4Pdjk)

エラーメッセージを見ると、まさにそこを満たしていないと指摘されているのが分かります。

なぜかというと、`std::vector<bool>::reference`のプロキシオブジェクトには代入演算子はあっても`const`修飾されていないためです。`const`化してしまうと代入できなくなってしまいます。自身の`const`性と参照先のそれとは無関係のはずなのに・・・

C++23に向けてここを修正する動きはあるようですが、この様なプロキシオブジェクトを用いるイテレータを作成するときは、プロキシオブジェクトの代入演算子の`const`修飾に思いを馳せる必要があります。

### 参考文献

- [`std::indirectly_writable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/indirectly_writable.html)
- [ericniebler/range-v3 Readable types with prvalue reference types erroneously model IndirectlyMovable - Github](https://github.com/ericniebler/range-v3/issues/573)
- [ericniebler/stl2 Readable types with prvalue reference types erroneously model Writable - Github](https://github.com/ericniebler/stl2/issues/381)
- [P2214R0 A Plan for C++23 Ranges](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2214r0.html#a-tuple-that-is-writable)
- [`std::vector<bool>::reference` - cppreference](https://en.cppreference.com/w/cpp/container/vector_bool/reference)

### 謝辞

この記事の99割は以下の方々のご指摘によって成り立っています

- [@wx257osn2さん](https://twitter.com/wx257osn2/status/1368194050042585088)
- [@wx257osn2さん](https://twitter.com/wx257osn2/status/1368195657496817665)
- [@wx257osn2さん](https://twitter.com/wx257osn2/status/1368195504270581761)
- [@yohhoyさん](https://twitter.com/yohhoy/status/1368193164247449614)
- [@yohhoyさん](https://twitter.com/yohhoy/status/1368194722913685506)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2021/20210306_indirectly_writable.md)
