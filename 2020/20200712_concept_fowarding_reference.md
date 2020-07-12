# ［C++］Forwarding referenceとコンセプト定義

コンセプトを定義するとき、あるいは`requires`節で制約式を書くとき、はたまた`requires`式でローカルパラメータを使用するとき、その型パラメータが*Forwarding reference*から来ているものだと使用する際に少し迷う事があります。

```cpp
// operator*による間接参照が可能であること
template<typename T>
concept weakly_indirectly_readable = requires(T& t /*👈ローカルパラメータ*/) {
  *t;
};

template<weakly_indirectly_readable T>
void f(T&& t) {
  auto v = *std::forward<T>(t);
}

int main() {
  std::optional<int> opt{10};

  f(opt); // 左辺値を渡す
  f(std::optional<int>{20});  // 右辺値を渡す
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/SU9G5BZveoZZKGYU)

さてこの時、`weakly_indirectly_readable`は右辺値に対してきちんと制約出来ているでしょうか？値カテゴリの情報まできちんと伝わっていますか？？  
残念ながらこれでは右辺値に対して適切に制約出来ていません。例えば右辺値の時は呼べないような意地の悪い型を用意してあげると分かります。

```cpp
struct dereferencable_l {
  int n = 0;

  int& operator*() & {
    return n;
  }

  int&& operator*() && = delete;
};


int main() {
  dereferencable_l d{10};

  f(d); // 左辺値を渡す
  f(dereferencable_l{20});  // 右辺値を渡す、エラー
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NMDRLEfKCaAI3ysy)

エラーにはなりますが、それは右辺値を渡したときに`f()`の定義内で発生するハードエラーです。コンセプトによる制約はすり抜けています。


ではこの時どのようにすれば左辺値と右辺値両方に対して適切な制約を書けるのでしょう・・・？


### *Forwarding reference*と参照の折り畳み

*Forwarding reference*とは先程の`f()`の引数にある`T&&`のような引数宣言の事です。これはそこに引数として左辺値が来ても右辺値が来ても、テンプレートの実引数推定時にいい感じの型に変化してくれる凄い奴です。

そのルールは単純で、*Forwarding reference*に対応する引数の値カテゴリによって次のようになります。

- 引数として左辺値（*lvalue*）が渡されたとき
    - テンプレートパラメータ`T`は渡された型を`T`として`T&`になる
- 引数として右辺値（*xvalue, prvalue*）が渡されたとき
    - テンプレートパラメータ`T`は渡された型そのままの`T`になる

```cpp
template<typename T>
void f(T&& t);

int n = 0;

f(n);  // intの左辺値を渡す、T = int&
f(1);  // intの右辺値を渡す、T = int
```

ではこの時、引数宣言の`T&&`はどうなっていて、引数の`t`はどうなっているのでしょう？  
これは参照の折り畳み（*reference collapsing*）というルールによって、元の値カテゴリの情報を表現するように変換されます。

- 引数に左辺値が渡されたとき
    - テンプレートパラメータは`T -> T&`となり、引数型は`T&&& -> T&`となる
    - 引数`t`は左辺値参照
- 引数に右辺値が渡されたとき
    - テンプレートパラメータは`T -> T`となり、引数型は`T&& -> T&&`となる
    - 引数`t`は右辺値参照

これ以降の場所でこの`T`を使用する場合も同様になります。参照の折り畳みは別に*Forwarding reference*専用のルールではないのでそれ以外の場所でも同様に発動します。  
そして、参照の折り畳みによって右辺値参照が生成されるのは、`T&&`に`&&`を付けた時だけです。それ以外はすべて左辺値参照に折りたたまれます。

```cpp
using rawt = int;
using lref = int&;
using rref = int&&;

using rawt_r  = rawt&;   // int&
using rawt_rr = rawt&&;  // int&&
using lrefr   = lref&;   // int& & -> int&
using lrefrr  = lref&&;  // int& && -> int&
using rrefr   = rref&;   // int&& & -> int&
using rrefrr  = rref&&;  // int&& && -> int&&
```

### 最適解

*Forwarding reference*に対して制約を行うコンセプトの定義内、あるいは`requires`節の制約式では上記の様に折り畳まれた後の型が渡ってきます。つまりは、それを前提にして書けばいいのです。先程の`weakly_indirectly_readable`を書き直してみると次のようになります。

```cpp
// operator*による間接参照が可能であること
template<typename T>
concept weakly_indirectly_readable = requires(T&& t) {
  *std::forward<T>(t);
};

template<weakly_indirectly_readable T>
void f(T&& t) {
  auto v = *std::forward<T>(t);
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NMDRLEfKCaAI3ysy)

`f()`に左辺値を渡したとき、`weakly_indirectly_readable`に渡る型は左辺値参照型`T&`です。`weakly_indirectly_readable`のローカルパラメータ`t`は参照の折り畳みによって`T&& & -> T&`となり、左辺値参照になります。`std::forward`に渡している`T`も`T&`なので、ここではムーブされません。

`f()`に右辺値を渡したとき、`weakly_indirectly_readable`に渡る型は単に`T`です。`weakly_indirectly_readable`のローカルパラメータ`t`はそのまま`&&`が付加されて`T&&`となり、右辺値参照になります。`std::forward`に渡している`T`も`T`なので、ムーブされることになります。

これはコンセプト定義内ではなく、`requires`節で直接書くときも同様です。

```cpp
template<typename T>
  requires requires(T&& t) {
    *std::forward<T>(t);
  }
void f(T&& t) {
  auto v = *std::forward<T>(t);
}
```

先程の意地の悪い例を渡してみてもコンセプトによるエラーが発生するのが分かります。

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/6plI9Q99l3ET3zhV)

この様に、*Forwarding reference*と参照の折り畳みを考慮することで、値カテゴリを適切に処理しつつ制約を行うことができます。

### 値カテゴリを指定する制約

先程完璧に仕上げた`weakly_indirectly_readable`ですが、それをあえて右辺値と左辺値パターンで分けて書いてみます。

```cpp
template<typename T>
concept weakly_indirectly_readable = requires(T& t) {
  *t;             // 左辺値に対する制約
  *std::move(t);  // 右辺値に対する制約
};
```

これは先ほどの`T&&`と`std::forward`を使った制約と同じ意味になります。

あえてこのように書くことで、ローカルパラメータとその型の参照修飾を用いて制約式に値カテゴリの制約を指定している様を見ることができます。すなわち、`weakly_indirectly_readable`のモデルとなる型は`operator*()`が右辺値・左辺値の両方で呼べること！という制約を表現しています。これを略記すると先ほどの`T&&`と`std::forward`を使った制約式になるわけです。

例えば制約したい対象の式（ここでは`operator*`）が左辺値でだけ呼べれば良いのであれば右辺値に対する制約は必要なく、逆に右辺値だけをチェックすればいい場合は左辺値に対する制約は必要ありません（ただし、そのようなコンセプト定義は適切ではないかもしれません）。

さらに、ローカルパラメータをCV修飾することで、値カテゴリに加えてCV修飾を指定した制約を行えます。

```cpp
template<typename T>
concept weakly_indirectly_readable = requires(const T& t) {
  *t;             // const 左辺値に対する制約
  *std::move(t);  // const 右辺値に対する制約
};
```

ちなみにこの場合に、非`const`に対する制約も同時に行いたい場合は以下のようにします。

```cpp
template<typename T>
concept weakly_indirectly_readable = requires(T& t) {
  *t;             // 左辺値に対する制約
  *std::move(t);  // 右辺値に対する制約
  *const_cast<const T&>(t);             // const 左辺値に対する制約
  *std::move(const_cast<const T&>(t));  // const 右辺値に対する制約
};
```

非`const`のローカルパラメータを取って`const_cast`します。`requires`式を分けても良い気がしますが、標準ライブラリのコンセプトはこの様に定義されるようです。

これらのように、`requires`式のローカルパラメータのCV・参照修飾を用いて制約式に対するCV修飾と値カテゴリの制約を表現する事ができます。そして、標準ライブラリのコンセプトは全てそのように書かれています。

### 結局

脱線しながら長々と語ってきましたが、コンセプトを定義するあるいは`requires`節で制約をする際に意識すべきことは一つだけです。

- コンセプト定義あるいは`requires`節において、引数となる型パラメータは常にCV修飾無し、参照修飾無しの完全型が渡ってくると仮定して書く

これに近いことは規格書にも書いてあります。この仮定を置いてそれに従って書けば、結果的に適切なCV修飾と値カテゴリによって制約を行うことができます。これは実際に渡ってくる型が云々と悩むのではなく、そう思って書け！という事です。

標準ライブラリのコンセプトはそのように定義されており、これを意識の端っこに置いておけばそのようなコンセプトを利用しやすくなり、自分で定義する際もすっきり書くことができるようになるかもしれません。

### 参考文献

- [C++20 コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [C++11 参照への参照を折りたたむ - cpprefjp](https://cpprefjp.github.io/lang/cpp11/reference_collapsing.html)
- [［C++］コンセプトの無言のお願い事 - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/03/27/193043)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20200712_concept_fowarding_reference.md)