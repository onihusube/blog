# ［C++］ラムダキャプチャの記述順序

ラムダ式を雰囲気で書いているので、キャプチャの正しい順序が分かりません。そのため、コンパイラに怒られて直したり怒られなかったからﾖｼ！をしています。

正しい順序とは一体何なのでしょうか・・・？

### 正しいキャプチャ順序

C++20現在、キャプチャには3種類の方法があります。明確に書かれているわけではありませんがそこには確かに順序があり、次のようになります。

1. デフォルトキャプチャ
      - `&`
      - `=`
2. それ以外
      - 簡易キャプチャ
        - `&x` 
        - `x` 
        - `this` 
        - `*this` 
      - 初期化キャプチャ

はい、これだけです。悩む事も無いですね・・・

```cpp
// 正しい順番
[&]{};
[=]{};
[=, x]{};
[=, &x]{};
[=, x = 0]{};
[=, this]{};
[=, *this]{};
[=, x, &y, z = 0, this]{};
[=, this, &x, y, z = 0]{};

// 間違った順番
[x, =]{};
[x, &]{};
[&x, &]{};
[&x, =]{};
[x = 0, =]{};
[this, &]{};
[*this, =]{};
```

`= &`によるデフォルトキャプチャが先頭にきてさえいれば、後はどういう順番でも構わないという事です。

### 詳細

ラムダ式の文法定義の中で、ラムダ導入子（`[]`）の中のキャプチャ（`lambda-capture`）は次のように構文定義されています。

```ebnf
lambda-capture:
  capture-default
  capture-list
  capture-default , capture-list

capture-default:
  &
  =

capture-list:
  capture
  capture-list , capture

capture:
  simple-capture
  init-capture

simple-capture:
  identifier ...(opt)
  & identifier ...(opt)
  this
  * this

init-capture:
  ...(opt) identifier initializer
  & ...(opt) identifier initializer
```

まず最初の`lambda-capture`を見てみると、`capture-default`か`capture-list`それぞれ単体あるいは`capture-default , capture-list`の形の列のいずれかとして定義されています。`capture-default`はその次で定義されており、`= &`のどちらかです。そして、`capture-default`はここ以外では出現しません。

従ってまず、`capture-default`は`capture-list`よりも前に来なければならない事が分かります。

では`capture-list`とは何なのかと見に行けば、`capture`あるいは`capture-list , capture`のどちらかとして定義されています。この書き方はEBNFにおいて繰り返しを表現する定番の書き方であり、`capture-list`とは1つ以上の`capture`の列として定義されています。

`capture`はさらに`simple-capture`と`init-capture`のどちらかとして定義され、ここには順序がありません。

`simple-capture`は4つのキャプチャが定義されており、上からコピーキャプチャ、参照キャプチャ、`this`のコピーキャプチャ、`*this`のコピーキャプチャ、が定義されています。ここにもその出現順を制約するものはありません。

`init-capture`はその名の通り初期化キャプチャを定義しており、コピーキャプチャと参照キャプチャの2種類が定義されています。そしてここにも順序付けはありません。

結局、`lambda-capture`の中で出現順が定義されているのは`capture-default , capture-list`という形式だけであり、これがデフォルトキャプチャ（`= &`）が先頭に来て後は順不同という事を意味しています。

なお、`...(opt)`はパラメータパック展開のことで、これはC++20で許可されたものです。これも`= &`が先頭にきてさえいればどういう順番で現れても構いません。

### 参考文献

- [N4861 7.5.5.3 Captures [expr.prim.lambda.capture]](http://eel.is/c++draft/expr.prim.lambda#nt:lambda-capture)
- [C++11 ラムダ式 - cpprefjp](https://cpprefjp.github.io/lang/cpp11/lambda_expressions.html)
- [C++14 ラムダ式の初期化キャプチャ - cpprefjp](https://cpprefjp.github.io/lang/cpp14/initialize_capture.html)
- [C++20 ラムダ式のキャプチャとして[=, this]を許可する - cpprefjp](https://cpprefjp.github.io/lang/cpp20/allow_lambda_capture_equal_this.html)
- [C++20 ラムダ式の初期化キャプチャでのパック展開を許可 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/allow_pack_expansion_in_lambda_init_capture.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2021/20210221_lambda_capture_order.md)