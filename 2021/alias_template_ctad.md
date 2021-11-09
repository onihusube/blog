# ［C++］`std::array`のエイリアステンプレートとCTAD

twitterに密かに置いていた質問箱に次のような質問をいただきました。

```cpp
#include <array>

template<auto N>
using std_array_with_int = std::array<int,N>;

template<typename T>
using std_array_with_3 = std::array<T,3>;

int main() {
  [[maybe_unused]] std::array ar1 = { 1, 2, 3 };          // ok
  [[maybe_unused]] std_array_with_int ar2 = { 1, 2, 3 };  // ng
  [[maybe_unused]] std_array_with_3 ar3 = { 1, 2, 3 };    // ng
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ZYpj0t8CFK4ALCOm)

ようするに、`std::array`のテンプレートパラメータの一部だけを束縛したエイリアステンプレートでCTADを期待すると、謎のコンパイルエラーに悩まされています。

エイリアステンプレートのCTADが絡み非常に複雑な問題であり、簡易に回答できなさそうなのでこの記事を書きました。

### エイリアステンプレートのCTADの仕組み

エイリアステンプレートのCTADは、元の型の推論補助からエイリアステンプレートの推論補助を導出し、それを利用することで行われます。そのアルゴリズムはおおよそ次のようになります（以下では、導出したいエイリアステンプレートの推論補助を`A`、元の型に存在する推論補助を`B`と表します）。

1. エイリアステンプレートから推論補助`A`の結果（右辺）を取得し、`A`のテンプレートパラメータを推論する。
      - 推論できないコンテキストが存在しうるため、この時に全てのテンプレートパラメータを推論する必要はない
2. 1で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える
      - 1で全てのパラメータの推論が出来ていない可能性があるので、ここで得られた推論補助はエイリアステンプレートと`B`それぞれからのテンプレートパラメータを含む可能性がある
3. 結果の型（2で得られた推論補助の右辺）からエイリアスを推定し、2で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する
      - 結果の型からエイリアスを推定するか、またどのように推定するかは実引数型に依存するため、追加の制約が必要となる場合がある
4. このように導出された`A`は、オーバーロード解決時に導出されたことによる優先順位を与える

次のような型で動作例を見てみます。

```cpp
// 今回の例の対象エイリアステンプレート
template<typename T>
using P = std::pair<int, T>;

int main() {
  P p = {1, 2}; // ok、CTADがエイリアステンプレートに対して行われる
}
```

このコードで、`P`に対する推論補助がどのように導出されるかを先ほどの手順に沿って見てみます。

#### 1. エイリアステンプレートから推論補助`A`の結果（右辺）を取得し、`A`のテンプレートパラメータを推論する。

（以下、`std::pair`の`std`を省略します）

エイリアステンプレート`P`

```cpp
template<typename T>
using P = pair<int, T>;
```

の右辺から、エイリアステンプレートの推論補助`A`の結果型（右辺）とテンプレートパラメータ宣言

```cpp
template<typename T>
pair<int, T>;
```

を得ます。

元のエイリアステンプレートの右辺はそのまま推論補助の右辺（結果）として用いることができます。

#### 2. 1で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える

`pair`の推論補助は1つだけが用意されています

```cpp
namespace std {

  // ...

  template<typename T1, typename T2>
  pair(T1, T2) -> pair<T1, T2>;
}
```

これに、先ほど得た

```cpp
template<typename T>
pair<int, T>;
```

の内容をフィードバックします。

ここで、`pair`の推論補助の右辺のテンプレートパラメータのペア`(T1, T2)`と`(int, T)`から、`T1 = int, T2 = T`の対応を得ます。それを用いてフィードバックを行うと推論補助は

```cpp
template<typename T>
pair(int, T) -> pair<int, T>;
```

となります。

#### 3. 結果の型（2で得られた推論補助の右辺）からエイリアスを推定し、2で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する

最後に、得られた推論補助とエイリアステンプレート

```cpp
template<typename T>
pair(int, T) -> pair<int, T>;

template<typename T>
using P = pair<int, T>;
```

の対応から、エイリアステンプレートのテンプレート実引数を推論し、推論補助を完成します。

```cpp
template<typename T>
P(int, T) -> P<T>;
```

`P p = {1, 2};`のように書かれたとき、こうして得られた推論補助を用いてエイリアステンプレートのテンプレートパラメータが推論されます。

（正直4の意味と有効性は理解出来ていないし今回は関係ないはずなのでそこには触れません・・・

### `std::array`のエイリアステンプレートに対するCTADがうまく動かない理由

### 参考文献

- [P1021R4 Filling holes in Class Template Argument Deduction](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1021r4.html)
- [P1814R0 Wording for Class Template Argument Deduction for Alias Templates](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1814r0.html)
- [CTAD for alias templates algorithm examples](https://htmlpreview.github.io/?https://github.com/mspertus/CTAD_POST_CPP17/master/CTAD_alias_examples.html)