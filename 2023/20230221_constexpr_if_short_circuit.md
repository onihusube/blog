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

`constexpr if`はC++17で導入された新しめの言語機能であり、ユーザーフレンドリーになってることが期待されます。しかし実際には`constexpr if`は`if`文の一種でしかなく、構文的には`constexpr`があるかないか程度の違いであり、その条件式の扱いは`if`のそれに準じています（そのため、実は`costexpr if`にも[初期化式](https://cpprefjp.github.io/lang/cpp17/selection_statements_with_initializer.html)が書けます）。では、`if`の条件式の扱いがそうなっているのでしょうか？

`if`の条件式に関しては、文脈的に`bool`変換可能な式という程度にしか指定されておらず、`constexpr if`に関してはそれが定数式であることが追加で要求されるくらいです。つまり、`if/if constexpr`の条件式で短絡評価が起こるのかには`if`は関与していません。

文脈的に`bool`変換可能な式というのはめちゃくちゃ広いですが、今回問題となるのはその中でも`&&`と`||`の2つだけです（前述のように演算子オーバーロードは考慮しません）。実は`&&`と`||`の組み込み演算子が短絡評価するかどうかは実装定義だったりするのでしょうか？

これもそんなはずはなく、（`A && B`もしくは`A || B`とすると）どちらの演算子もそのオペランドの評価順序は`A -> B`の順で評価されることが規定され、なおかつ短絡評価に関してもきちんと規定されており未規定や実装定義などではありません。C++適合実装は、場所が`if`であるかどうかに関係なく、`A && B`もしくは`A || B`という式の実行において、式`A`の結果に応じた短絡評価を行わなければなりません。

さて、ここまで掘り返しても冒頭のエラーの原因がわかりません。一体何が起きているのか・・・？

### コンセプトはテンプレート（重要！！）

回り道をしましたが、実はここで起きていることはそれら以前の問題です。

```cpp
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
```

この局所的なコードのコンパイルにおいて、コンパイル時には次の順番で処理が実行されます

1. `f()`のインスタンス化
2. `cosntexpr if`の条件式のインスタンス化
3. `constexpr if`の条件式の評価
4. `constexpr if`の分岐

この時、2番目の条件式のインスタンス化においては主に、テンプレートパラメータ`T`に依存するもののインスタンス化が行われます。インスタンス化が必要なものとはつまりテンプレートのことであり、そこにはコンセプトも含まれています。そう、コンセプトはテンプレートの一種なので、単体の定数式として評価する前にコンセプトそのもののインスタンス化が必要となります。

この例でのコンセプトのインスタンス化では、`std::integral<T>`と`std::invocable<decltype(func<T>), T>`の2つのコンセプトのインスタンス化が行われます。前者は今回関係ないことが分かっているので、後者を詳しく見てみます。

まず、`std::invocable`の定義は次のようになっています

```cpp
template<class F, class... Args>
concept invocable = requires(F&& f, Args&&... args) {
  invoke(std::forward<F>(f), std::forward<Args>(args)...);
};
```

コンセプトの定義は基本的にはこの`requires`式内に求める要件式を並べて行い（また、複数の`requires`式をつなげることもでき）、コンセプトのインスタンス化に伴って、その字句順（`requires`式の並び順）（たぶん）にテンプレートパラメータの置換（*substitution*）とテンプレートのインスタンス化（以降単にインスタンス化）が行われていきます。その際、`requires`式内部ではインスタンス化に伴ってill-formed（コンパイルエラー/ハードエラー）になるようなことが起きたとしても、その`requires`式がその式の評価時に`false`となるだけでハードエラーを起こしません。

`requires`式のインスタンス化とその式の値の評価も、注意深く規格署の記述を読むと、テンプレートパラメータ置換およびインスタンス化と評価は段階が異なることが読み取れ（る気がし）ます。

この時、次のような記述（[[expr.prim.req]/5](http://eel.is/c++draft/expr.prim.req#general-note-1)）によって、インスタンス化された式がハードエラーを起こす場合がある事が指定されています

> `requires`式内の要件式に無効な型や式を含むものが含まれていて  
> それが*templated entity*の宣言内に表示されない場合  
> プログラムはill-formed

*templated entity*というのはテンプレート定義内の何かの事で、ここでは`requires`式に含まれる色々なものの事です。その宣言内に含まれない場合というのは要するに、コンセプト定義に直接見えていないような場合ということで、`requires`式に書かれた各要件式の内部で、別の式等が何かハードエラーを起こす場合のことを言っています（とおもいます・・・）。

さて、`std::invocable`は1つの`requires`式だけからなるコンセプトで、その1つの`requires`式は1つの単純要件だけを持ち、それは`std::invoke`によって`F`が`Args`で呼び出し可能かどうかを調べています。

`std::invocable<decltype(func<T>), T>`の場合、最終的には`func<std::unique_ptr>()`が呼び出し可能かが問われることになります。そして、そのチェックは宣言のみのチェックではなく、`invoke(std::forward<F>(f), std::forward<Args>(args)...);`という式の有効性のチェックとなるため、テンプレートパラメータの置換とそのインスタンス化が発生します。

`func<std::unique_ptr>()`はインスタンス化されると、その`return`文でコピーができないことからハードエラーを起こしますが、それはまさに`invocable`コンセプト定義の`requires`式の要件式に直接現れずにその呼び出し先の関数本体内で発生するため、これは`requires`式の範囲外となりそのままハードエラーになります。

冒頭の例の謎のエラーはまさに、この場合に起こるエラーです。つまりは、式として短絡評価されるか以前のところ（テンプレートのインスタンス化）でエラーが起きています。

この場合に`constexpr if`に求めるべきだったのは、その条件式においてその評価順序に応じたインスタンス化と短絡評価によるインスタンス化そのもののスキップだったわけです。当然そんなことはC++17でも20でも要求されておらず、現在のコンパイラはそのようなことはしてくれません。想像ですが、インスタンス化そのものがスキップされると定義の存在有無が変化し、それはひいてはODRに関係してくる気がします。

### 回避手段

とはいえ、`constexpr if`はコンパイル時の条件によってインスタンス化の抑制を行うものなので、その条件式はほとんどの場合に何かしらのテンプレートパラメータに依存することになるでしょう。テンプレートのインスタンス化に伴うハードエラー回避のために短絡評価を期待するのはある種自然な発想であるため、この問題は割と深刻かもしれません（それでも、実行時`if`と異なり問題はコンパイル時の謎のエラーとして報告されるのでマシではあります）。

そのため、短絡評価を期待通りに行ってもらう方法を考えてみます。


#### 関数に制約をかける

この場合の例にアドホックな解決策ですが、呼び出そうとする関数が適切に制約されていることによって`std::invoke`の呼び出し先がなくなれば、このような場合に`std::invoke`の内部の呼び出し先内でのエラー発生を回避できます。

```cpp
template<typename T, typename F>
void f(T&&, F&&) {
  // Tが整数型かつfuncで呼び出し可能
  // Tが整数型ではない場合は右辺の条件（funcの呼び出し可能性）はチェックされないことが期待される
  if constexpr (std::integral<T> && std::invocable<F, T>) {
    
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
  }
}

int main() {
  std::unique_ptr<int> up{};

  f(std::move(up), [](const std::copyable auto& v) { return v; }); // ok
  f(std::move(up), [](const               auto& v) { return v; }); // ng
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LJE5B8X6T4uscaev)

例示のために少し書き換えています。

この場合、`std::invocable`コンセプト定義内の`requires`式内の`std::invoke`による制約式では、呼び出すべき関数が見つからない（`std::unique_ptr`が`std::copyable`ではない）ことから`std::invoke`そのものがエラーになり、それは`requires`式の範囲内なのでハードエラーになる代わりにその`requires`式の式としての評価結果が`false`になり、`std::invocable<F, T>`も`false`に評価されます。

とはいえ、このような回避手段はこの問題を理解したうえで適用可能であるかを調べる必要があり、いつでも可能な汎用的なソリューションではありません。

#### 条件式を分ける

`&&`でつながれた条件式であれば複数の`if constexpr`文に分割することができるかもしれません。

```cpp
auto func(const auto& v) {
  return v; // コピーされる
}

template<typename T>
void f(T&&) {

  if constexpr (std::integral<T>) {
    // Tがunique_ptrの場合はここには来ない
    if constexpr (std::invocable<decltype(func<T>), T>) {
      ...
    }
    ...
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
    ...
  }
}

int main() {
  std::unique_ptr<int> up{};

  f(std::move(up)); // ok
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/zR33tn660gWOboVR)

`costexpr if`の`false`となる（選ばれなかった）ステートメントはインスタンス化されません。そのため、`costexpr if`がネストしていれば疑似的に短絡評価のようになります。

この場合は、分岐が増えることによって考慮すべきパスが増加することに注意が必要です

```cpp
template<typename T>
void f(T&&) {

  if constexpr (std::integral<T>) {
    // Tがunique_ptrの場合はここには来ない
    if constexpr (std::invocable<decltype(func<T>), T>) {
      ...
      return;
    }
    ...
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
    ...
    return;
  }

  // ここに来る場合がある
  std::unreachable();
}
```

あと`||`はどうしようもありません。ド・モルガンで頑張れる可能性はありますが・・・

#### `requires`式と入れ後要件を使う

[@yohhoyさんご提供](https://twitter.com/yohhoy/status/1627516336342732800)の方法です。

```cpp
auto func(const auto& v) {
  return v; // コピーされる
}

template<typename T>
void f(T&&) {

  if constexpr (requires { requires std::is_integral_v<T>;　requires std::invocable<decltype(func<T>), T>; }) {
    // Tがunique_ptrの場合はここには来ない
    ...
  } else {
    // Tがunique_ptrの場合はこちらに来る
    ...
  }
}

int main() {
  std::unique_ptr<int> up{};

  f(std::move(up)); // ok
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/SBq1fI0FKq7Ldaus)


実は`requires`式はコンセプト定義や`requires`節の外側でも書くことができて、その場合も内部の要件をチェックした結果の`bool`型の*prvalue*を生成する定数式になります。そのため、`costexpr if`の条件式でも使用することができます。

上記の`requires`式を取り出して見やすくすると

```cpp
requires { 
  requires std::is_integral_v<T>;
  requires std::invocable<decltype(func<T>), T>;
}
```

`requires`式内部で`requires expr;`のようにしているこの書き方は入れ子要件の制約と呼び、そのインスタンス化及び評価の順序は、字句順すなわちこのようにフォーマットした場合の上から順番に行われます。そのため、実質的にこれは`&&`条件を書いたのと同様になっており、なおかつコンセプトの`requires`式はその要件を満たさない（`false`に評価された）式が出現するとそこでインスタンス化と評価を停止するため短絡評価が期待できます。

ただ、短絡評価に関しては、「`requires`式の結果を決定する条件に出会うと、インスタンス化と評価を停止する」のように規定されており短絡評価を指定しているかは微妙です。実際、MSVCは短絡評価をしないような振る舞いをする場合があります（上記の例ではMSVCでも回避可能でしたが）。

また、これはも`||`で使用できません。ド・モルガンで頑張ることはできるかもしれませんが。

#### コンセプトに埋め込む

[@yohhoyさんご提供](https://twitter.com/yohhoy/status/1627524416564494338)の方法その2です。

前項の方法の`requires`式を1つのコンセプトに纏めてしまう方法です。

```cpp
#include <iostream>
#include <concepts>
#include <memory>

auto func(const auto& v) {
  return v; // コピーされる
}

// constecpr if条件を抽出したコンセプト定義
template<typename T>
concept C = std::integral<T> && std::invocable<decltype(func<T>), T>;

template<typename T>
void f(T&&) {

  if constexpr (C<T>) {
    // Tがunique_ptrの場合はここには来ない
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
  }
}

int main() {
  std::unique_ptr<int> up{};

  f(std::move(up)); // ok
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/nS3BbRtn5s8HPX24)

コンセプト定義内で`requires`式を用いずに直接`bool`型の定数式を指定することもできます。この場合のインスタンス化と評価の順序の規定は複雑ですが、コンセプトの定義内でこのように書いている場合は`&&`でも`||`でも同様に、字句順あるいは左から右にインスタンス化と評価が進行します（またこれは、`requires`式が複数ある場合のインスタンス化と評価の順序と同様です）。

さらに、`requires`式内部ではなくコンセプト定義で直接このように書いた場合は、`&&`と`||`の結果に従った適切な短絡評価が規定されています。従って、この場合は`std::integral<T>`が`false`と評価されれば`std::invocable<decltype(func<T>), T>`は評価もインスタンス化もされません。

前項の`requires`式と入れ後要件による方法は移植可能性に懸念があるのと、`||`で使用できないのが問題でしたが、この方法であればそれらの問題点はすべて解消され、インスタンス化と評価時に短絡評価が保証されます。

#### `std::conjunction`/`std::disjunction`を使用する

前項のコンセプトに切り出してしまう方法はほぼ完璧な方法ですが、コンセプトが名前空間内でしか定義できないことから、名前空間を汚すのが忌避されるかもしれません。短絡評価を行いつつ条件式はその場での使い捨てにしたい場合の方法として、古のTMPのユーティリティである[`std::conjunction`](https://cpprefjp.github.io/reference/type_traits/conjunction.html)/[`std::disjunction`](https://cpprefjp.github.io/reference/type_traits/disjunction.html)を使用する方法があります。

```cpp
#include <iostream>
#include <concepts>
#include <memory>

auto func(const auto& v) {
  return v; // コピーされる
}

// func<T>のインスタンス化を遅延させるラッパ型
template<typename T>
struct C {
  static constexpr value = std::invocable<decltype(func<T>), T>;
};

template<typename T>
void f(T&&) {

  if constexpr (std::conjunction_v< std::is_integral<T>, C<T> >) {
    // Tがunique_ptrの場合はここには来ない
  } else {
    // Tがunique_ptrの場合はこちらに来ることが期待される
  }
}

int main() {
  std::unique_ptr<int> up{};

  f(std::move(up)); // ok
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/S8ybmzvOQRMDaX8E)

`std::conjunction`および`std::disjunction`は、`T::value`が`bool`型定数であるメタ関数を任意個数受けて、その`&&`/`||`を求めるメタ関数ですが、その評価に当たっては短絡評価が規定されています。そのため、条件をメタ関数に落とすことができるならば、この方法を用いてもインスタンス化を短絡評価させることができます。

ただ、この例はあまり適切ではない例で、`func<T>`の出現（インスタンス化）を遅延させるために別の型に埋め込まなければならなくなっており、どのみち名前空間に不要なものがばらまかれてしまっています・・・

最後にこの古のメタ関数にたどり着いたところで、冒頭の例の問題とはまさにこれらのメタ関数が導入された理由の一つでもある事に気づきます。つまり、`T1::value && T2::value && T3::value && ...`というようにすると、この式の評価よりも前に`Tn::value`のインスタンス化が要求されてしまい、そのいずれかがハードエラーを起こす場合にまさに冒頭の例と同じ問題にぶつかります。`std::conjunction`および`std::disjunction`はその内部で先頭から1つづつ`Tn::value`を呼んで行き結果が確定したところでインスタンス化と評価を停止することで、インスタンス化の短絡評価を行うためのユーティリティです。

`constexpr if`とコンセプトという真新しい言語機能に惑わされてしまっただけで、本質的な問題はTMPの時代から変わっていなかったわけでした・・・。

### 参考文献

- [C++17 `constexpr if` 文 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/if_constexpr.html)
- [C++20 コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [if statement - cppreference](https://en.cppreference.com/w/cpp/language/if)
- [Logical operators - cppreference](https://en.cppreference.com/w/cpp/language/operator_logical)
- [conjunction/disjunctionと短絡インスタンス化 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20171103/p1)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2023/20230221_constexpr_if_short_circuit.md)
