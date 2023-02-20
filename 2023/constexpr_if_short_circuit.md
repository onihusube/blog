# ［C++］ constexpr ifとコンセプトと短絡評価と

`constexpr if`（構文としては`if constexpr`）の条件には`bool`に変換可能な任意の定数式を使用できます。複数の条件によって分岐させたい場合、自然に`&&`もしくは`||`によって複数の条件式をつなげることになるでしょう。そしてその場合、条件式には左から右への評価順序と短絡評価を期待するはずです。

```cpp
auto func(const auto& v) {
  return v; // コピーされる
}

template<typename T>
void f(T&&) {
  // Tが整数型かつfuncで呼び出し可能
  // Tが整数型ではない場合は右辺の条件（funcの呼び出し可能性）はチェックされないことが期待される
  if constexpr (std::integral<T> && std::invocable<decltype(func<T>), T>) {
    ...
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
    ...
  }
}

int main() {
  std::unique_ptr<int> up{};

  f(std::move(up)); // ng
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/7u8YX7nUn50yan6z)

エラーは`func()`の`return`で`v`がコピーできないために起きており、ここでの`v`は`std::unique_ptr`の`const`左辺値なので当然コピーはできません。しかし、コードのどこでも`func()`を`std::unique_ptr`で呼んではいません、なぜこれはエラーになるのでしょうか？

[:contents]

### 起きていること

コードをよく見ると、直接的ではないものの`func()`を`std::unique_ptr`で呼んでいる箇所が1つだけあります。それは、`std::invocable<decltype(func<T>), T>`という式で、これは[`std::invocable`](https://cpprefjp.github.io/reference/concepts/invocable.html)コンセプトによって`T`によって`func<T>()`が呼び出し可能かを調べています。関数`f()`の引数型`T`経由で、ここで`std::unique_ptr`が`func()`にわたっています。

（コンセプトはこの様に使用した時にそれ単体で1つの式になり、`bool`型の*prvalue*を生成する定数式となります）

とはいえ、その直前（左辺）の条件では`std::integral<T>`によって`T`が整数型であることを要求しており、`std::unique_ptr`は当然整数型ではないのでその条件は`false`となり、短絡評価によって`std::invocable<decltype(func<T>), T>`は評価されないことが期待されます。しかし、ここで`func()`に`std::unique_ptr`がわたってエラーが起きているということは、どうやらその期待は裏切られている様です。

このことは、`std::integral<T>`を恒偽式に置き換えてやるとよりわかりやすくなります。

```cpp
auto func(const auto& v) {
  return v; // コピーされる
}

template<typename T>
void f(T&&) {
  if constexpr (false && std::invocable<decltype(func<T>), T>) {
    ...
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
    ...
  }
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/94JvuxKZsu0NAWyh)

どうやら`constexpr if`の条件式では短絡評価が起きていない様に見えます。

そしてこのことは主要な3コンパイラで共通していることから、どうやら仕様に則った振る舞いの様です。

- [Compiler Explorer](https://godbolt.org/z/dfbrx56jn)

`if constexpr (A && B)`としたら、`A -> B`の順番で評価されてほしいし`A = false`なら`B`は評価されないでほしい気持ちがあります（これは`||`でも同様でしょう）。そうならないのが自然な振る舞いなはずはありません・・・

### `constexpr if`の扱い

`constexpr if`はC++17で導入された新しめの言語機能であり、ユーザーフレンドリーになってることが期待されます。しかし実際には`constexpr if`は`if`文の一種でしかなく、構文的には`constexpr`があるかないか程度の扱いの差しかなく、その条件式の扱いは`if`のそれに準じています（そのため、実は`costexpr if`にも[初期化式](https://cpprefjp.github.io/lang/cpp17/selection_statements_with_initializer.html)が書けます）。では、`if`の条件式の扱いがそうなっているのでしょうか？

`if`の条件式に関しては、文脈的に`bool`変換可能な式という程度にしか指定されておらず、`constexpr if`に関してはそれが定数式であることが追加で要求されるくらいです。つまり、`if/if constexpr`の条件式で短絡評価が起こるのかには`if`は関与していません。

文脈的に`bool`変換可能な式というのはめちゃくちゃ広いですが、今回問題となるのはその中でも`&&`と`||`の2つだけです（前述のように演算子オーバーロードは考慮しません）。実は`&&`と`||`の組み込み演算子が短絡評価するかどうかは実装定義だったりするのでしょうか？

これもそんなはずはなく、（`A && B`もしくは`A || B`とすると）どちらの演算子もそのオペランドの評価順序は`A -> B`の順で評価されることが規定され、なおかつ短絡評価に関してもきちんと規定されており未規定や実装定義などではありません。C++適合実装は、場所が`if`であるかどうかに関係なく、`A && B`もしくは`A || B`という式の実行において、式`A`の結果に応じた短絡評価を行わなければなりません。

さて、ここまで掘り返しても冒頭のエラーの原因がわかりません。一体何が起きているのか・・・？

### コンセプトはテンプレート（重要！！）

### 回避手段

### 参考文献

- [C++17 `constexpr if` 文 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/if_constexpr.html)
- [C++20 コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [if statement - cppreference](https://en.cppreference.com/w/cpp/language/if)
- [Logical operators - cppreference](https://en.cppreference.com/w/cpp/language/operator_logical)