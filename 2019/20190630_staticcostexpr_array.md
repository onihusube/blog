# ［C++］static constexprな配列メンバの定義

クラスの静的メンバ変数は通常クラス外にその定義が必要になります。

```cpp
struct sample {
  //宣言
  static int n;
};

//定義
int sample::n = 10;
```

ただし、静的メンバ変数が`static constexpr`な変数であるときは、多くの場合その定義は省略することができます。

```cpp
struct sample {
  //宣言
  static constexpr int n = 10;
};
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/lvnDHWUXlLpQifgQ)

しかし、`static constexpr`な配列メンバは同様の場合においても定義が必要とされます（ただし、C++14まで）。
```cpp
struct sample {
  //宣言？
  static constexpr int m[] = {10, 20};
};

//定義、これが無いとリンカエラー
constexpr int sample::m[];
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/4Kw89DK1aARbIFpW)

これには変数がいつodr-usedされるのか、という難解な決まりごとが関わっています。

### 変数のodr-used

変数や関数などはodr-usedされたときにその定義が必要となります。逆に言えば、odr-usedされなければ定義は必要ではありません。

変数のodr-usedは以下のように規定されています（[N4659 6.2.3 One-definition rule [basic.def.odr]](https://timsong-cpp.github.io/cppwp/n4659/basic.def.odr#3)より、C++17とC++14ではこの部分の内容に変更は無いのでC++17規格を参照します）。
>A variable x whose name appears as a potentially-evaluated expression ex is odr-used by ex unless applying the lvalue-to-rvalue conversion to x yields a constant expression that does not invoke any non-trivial functions and, if x is an object, ex is an element of the set of potential results of an expression e, where either the lvalue-to-rvalue conversion is applied to e, or e is a discarded-value expression. 

細かく説明するのは困難なので簡単に要約すると、ある変数`x`は以下の場合を除いてodr-usedされます。

`x`が評価されうる式`ex`に現われていて

- `x`にlvalue-rvalue変換を適用すると、非トリビアルな関数を呼び出さない定数式、で行うことができる
- `x`は参照である
- `x`はオブジェクトであり、かつ
  - `ex`はlvalue-rvalue変換が適用されない結果が廃棄される式（discarded-value expression）の（想定される）結果の一つであるか
  - `ex`はlvalue-rvalue変換が適用可能なより大きな式の（想定される）結果の一つ

まあ良く分からないですね・・・。  
今回重要なのはなんとなくわかるかもしれない1つ目の条文
>`x`にlvalue-rvalue変換を適用すると、非トリビアルな関数を呼び出さない定数式、で行うことができる

という所です。

lvalue-rvalue変換とはその名の通り、変数を左辺値から右辺値へ変換するものです。そして、それが非トリビアルな関数（ユーザ定義された関数）を呼び出さず、定数式で行える時、変数はodr-usedされません。

実は、非配列の`static constexpr`な変数は常にこの規則に当てはまっており、使っている（つもり）のところではその定数値が直接埋め込まれる形に変換されているわけです。

```cpp
struct sample {
  //宣言
  static constexpr int n = 10;
};

int main() {
  //このsample::nの使用は、lvalue-rvalue変換によって
  int n = sample::n;
  //以下のように書いたように扱われている
  int n = 10;
}
```

常にこのようにすることができる場所では、その定義は必要とならないので、odr-usedである必要がない事が分かるでしょう。

ところで、lvalue-rvalue変換とはなんぞやと詳しく見に行ってみると、1番最初に以下のように書かれています（[N4659 7.1.1 Lvalue-to-rvalue conversion [conv.lval]](https://timsong-cpp.github.io/cppwp/n4659/conv.lval#1)）。

>A glvalue of a non-function, non-array type T can be converted to a prvalue.

要約すると
>関数型でも配列型でもない型Tのglvalueは、同じ型のprvalueに変換できる。

おわかりいただけたでしょうか、`static constexpr`な配列メンバを使用すると定義を必要とされるのはこの条文によります。  
つまり、配列型の変数にはlvalue-rvalue変換を適用することができないため、どのように使ったとしてもodr-usedになってしまうのです。

結果、クラス外に定が必要になってしまいます。

そして、例えばコンパイルをとりあえず通すためにヘッダにそのような定義を書き、長い時間が過ぎた後でそのヘッダを複数のソースファイル（翻訳単位）からインクルードしたとき、今度は定義が重複している、ODR違反だ！というエラーに悩まされることでしょう・・・

### C++17以降の世界

C++17以降は、冒頭の`static constexpr`な配列メンバにおいても定義をすることなく使用することができるようになります。

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Tfgn5jU1vCN22bYN)

これは、odr-usedの条件が変更されたわけではなく、C++17より導入されたinline変数の副作用によるものです。

詳しくは → [インライン変数 - cpprefjp C++日本語リファレンス](https://cpprefjp.github.io/lang/cpp17/inline_variables.html)

クラスの静的メンバ変数に`constexpr`がついているとき、暗黙的に`inline`指定したのと同じになり、定義がその場で生成されます。  
しかも、`inline`変数なのでヘッダに書いて複数ファイルからインクルードしてもその定義は一つに保たれるためにODR違反に悩まされることもありません。

つまりはC++17以降を使いましょう、という事ですね・・・。

### 参考文献
- [N4659 : Working Draft, Standard for Programming Language C++](https://timsong-cpp.github.io/cppwp/n4659/)
- [定義と ODR - cppreference.com](https://ja.cppreference.com/w/cpp/language/definition)
- [インライン変数 - cpprefjp C++日本語リファレンス](https://cpprefjp.github.io/lang/cpp17/inline_variables.html)

### 謝辞
この記事は以下の方によるご指摘によって成り立っています。

- [@mokamukurugaさん](https://twitter.com/mokamukuruga/status/1144578490512969729)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190630_staticcostexpr_array.md)