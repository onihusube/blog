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

### CTADの仕組み（簡易）

あるクラステンプレート`C`についてのCTADは、`C`のコンストラクタを変換して得た関数テンプレート（引数はそのコンストラクタの引数、テンプレートパラメータは`C`のテンプレートパラメータにそのコンストラクタのテンプレートパラメータを合併したもの、戻り値型はそのコンストラクタのテンプレートパラメータのうち`C`のものに対応するパラメータで特殊化された`C<Ts...>`）と、`C`に定義された推論補助を関数テンプレートとして抽出し、初期化式（`C = c{args...};`）に与えられている実引数列（`args...`）を用いてそれらの関数テンプレートを呼び出したかのようにオーバーロード解決を行い、最適にマッチした1つの関数テンプレートの戻り値型からテンプレートパラメータが補われた`C<Ts...>`を取得するものです。

CTADはコンストラクタ呼び出しよりも前に行われ、必ずしも使用される推論補助（コンストラクタからの関数テンプレート）と実際に呼び出されるコンストラクタが対応していなくても良く、推論補助に関してはほぼ関数テンプレートのように書くことができます（コンセプトやSFINAEによる制約などを行えます）。

重要なことは、コンストラクタおよび推論補助を関数テンプレートとして扱って、実引数を用いてオーバーロード解決を行なって、残った1つの戻り値型から完全な型を取得するという手順です。CTADはクラス型・集成体型・エイリアステンプレートの3つに対して行われますが、バックエンド部（関数テンプレートとしてオーバーロード解決以降）はそれらで共通で、異なるのはその関数テンプレートをなんとか抽出するフロントエンド部分のプロセスです。

### エイリアステンプレートのCTADの仕組み

エイリアステンプレートのCTADは、元の型の推論補助を変換してエイリアステンプレートの推論補助を導出し、それを利用することで行われます。そのアルゴリズムはおおよそ次のようになります（以下では、導出したいエイリアステンプレートの推論補助を`A`、元の型に存在する推論補助を`B`と表します）。

1. エイリアステンプレートの元の型に定義された推論補助`B`を全て取得する
      - 以下の手順はそうして取得した`B`1つ1つに対してそれぞれ行われる
2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する
      - この処理は、関数テンプレートのテンプレートパラメータ推論と同様に行われる（ただし、推論できないパラメータがある場合でも失敗しない）
      - 推論できないコンテキストが存在しうるため、この時に全てのテンプレートパラメータを推論する必要はない
3. 2で暫定的に得られた`A`の内容を、`B`にフィードバックして置き換える
      - 2で全てのパラメータの推論が出来ていない可能性があるので、ここで得られた推論補助はエイリアステンプレートと`B`それぞれからのテンプレートパラメータを含む可能性がある
4. 結果の型（3で得られた推論補助の右辺）からエイリアスを推定し、3で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する
      - 結果の型からエイリアスを推定するか、またどのように推定するかは実引数型に依存するため、追加の制約が必要となる場合がある

このような導出（あるいは推論補助の変換）は、エイリアステンプレートの元の型に定義されている推論補助1つづつに対して行われ、そうして無事に導出できた（中には失敗するものがありうる）推論補助を、通常の推論補助と同じように扱ってエイリアステンプレートのCTADは行われます。

### 例1、単純な例

次のような型で動作例を見てみます。

```cpp
// 今回の例の対象エイリアステンプレート
template<typename T>
using P = std::pair<int, T>;

int main() {
  P p = {1, 2}; // ok、CTADがエイリアステンプレートに対して行われる
}
```

このコードで、`P`に対する推論補助がどのように導出されるかを先ほどの手順に沿って見てみます（以下、`std::pair`の`std`を省略します）。

#### 2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する

`pair`の推論補助は1つだけが用意されています

```cpp
namespace std {

  // ...

  template<typename T1, typename T2>
  pair(T1, T2) -> pair<T1, T2>;
}
```

これを`B`として、これとエイリアステンプレート`P`

```cpp
template<typename T>
using P = pair<int, T>;
```

の右辺から、テンプレートパラメータのペア`<T1, T2>`と`<int, T>`から、`T1 = int, T2 = T`と`typename T2 = typename T`の対応を得ます。

ここでは通常の関数テンプレートのテンプレートパラメータ推論と同じこと、つまり

```cpp
template<typename T1, typename T2>
void f(T1, T2);

f(int{}, T{});
```

のように呼び出した時に、推論される`T1, T2`の型を求めることで対応を得ます。この時、`T2`のように確定しないパラメータは確定しないまま対応させます。

#### 3. 2で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える

`B`に

```cpp
template<typename T1, typename T2>
pair(T1, T2) -> pair<T1, T2>;
```

先ほど得た内容（`T1 = int, T2 = T`と`typename T2 = typename T`）をフィードバックします。

```cpp
template<typename int, typename T>
pair(int, T) -> pair<int, T>;
```

となり、`T1`は型が確定しているのでもはやテンプレートではなく

```cpp
template<typename T>
pair(int, T) -> pair<int, T>;
```

となります。

#### 4. 結果の型（2で得られた推論補助の右辺）からエイリアスを推定し、3で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する

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

### 例2、単に名前を短縮したいだけの例

```cpp
// とても長い名前のクラス
template<class T>
class VeryLongNameXXXXX { /* ... */ };

template<class T>
VeryLongNameXXXXX(T) -> VeryLongNameXXXXX<decay_t<T>>;

// 名前を短縮するためのエイリアステンプレート
template<class A>
using MyAbbrev = VeryLongNameXXXXXX<A>;
```

この場合に、`MyAbbrev`に対して導出される推論補助を見てみます。

#### 2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する

`VeryLongNameXXXXX`の推論補助は1つだけです。

```cpp
template<class T>
VeryLongNameXXXXX(T) -> VeryLongNameXXXXX<decay_t<T>>;
```

これを`B`として

```cpp
// 名前を短縮するためのエイリアステンプレート
template<class A>
using MyAbbrev = VeryLongNameXXXXXX<A>;
```

これらの右辺からテンプレートパラメータの対応を求めます。

ところでそれは、関数テンプレートの引数推論と同様に行われるのでしたから

```cpp
template<typename T>
void f(decay_t<T>);

f(A{});
```

のように呼んだ時と同じ推論が行われます。ご存知のように？これは推論できないコンテキストとされ、`T`の推論はできません。したがって、ここでは何の情報も得られません（`T = A`の対応は自明ですが、それはここでは求められません）。

#### 3. 2で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える


先ほど得られた情報を`B`にフィードバックするわけですが、何もフィードバックするものはないのでこのステップは何もしません。よって、元の推論補助そのままが得られます。

```cpp
template<class T>
VeryLongNameXXXXX(T) -> VeryLongNameXXXXX<decay_t<T>>;
```

#### 4. 結果の型（2で得られた推論補助の右辺）からエイリアスを推定し、3で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する

次の2つからエイリアステンプレートの推論補助`A`を導出するわけですが

```cpp
template<class T>
VeryLongNameXXXXX(T) -> VeryLongNameXXXXX<decay_t<T>>;

template<class A>
using MyAbbrev = VeryLongNameXXXXXX<A>;
```

これは何も難しいところはないでしょう

```cpp
template<class T>
MyAbbrev(T) -> MyAbbrev<decay_t<T>>;
```

### 例3、規格書の意図的な例

```cpp
template <class T, class U>
struct C {
  C(T, U);
};

template<class T, class U>
C(T, U) -> C<T, std::type_identity_t<U>>;

// 今回のお客様
template<class V>
using A = C<V*, V*>;
```

#### 2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する

`C`の推論補助は1つだけです。

```cpp
template<class T, class U>
C(T, U) -> C<T, std::type_identity_t<U>>;
```

これを`B`として

```cpp
template<class V>
using A = C<V*, V*>;
```

これらの右辺からテンプレートパラメータの対応を求めます。

関数テンプレートで表してみると

```cpp
template<typename T, class U>
void f(T, std::type_identity_t<U>);

f(V*{}, V*{});
```

のように呼んだ時と同じ推論が行われます。

ここで得られる対応は、`T = V*`と`typename T = class V`のみで、`U`との対応は得られません（推論できないコンテキストです）。

#### 3. 2で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える

先ほど得られた情報（`T = V*`と`typename T = class V`）を`B`

```cpp
template<class T, class U>
C(T, U) -> C<T, std::type_identity_t<U>>;
```

にフィードバックします。

```cpp
template<class V, class U>
C(V*, U) -> C<V*, std::type_identity_t<U>>;
```

#### 4. 結果の型（2で得られた推論補助の右辺）からエイリアスを推定し、3で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する

次の2つからエイリアステンプレートの推論補助`A`を導出するわけです。

```cpp
template<class V, class U>
C(V*, U) -> C<V*, std::type_identity_t<U>>;

template<class V>
using A = C<V*, V*>;
```

単純にエイリアスを戻すと次のようになりそうです。

```cpp
template<class V, class U>
A(V*, U) -> A<V>;
```

が、これだとエイリアステンプレートの意味が変わってしまっています。そこで、`std::type_identity_t<U> = V*`という対応が見えていますので、これの情報を制約として加えたものが最終的な`A`となります。

```cpp
template<class V, class U>
A(V*, U) -> A<V> requires std::same_as<V*, std::type_identity_t<U>>;
```

ここでの制約はわかりやすくした一例です。例えばGCCはこの時`requires std::same_as<A<V>, C<V*, std::type_identity_t<U>>>`のような制約を生成しているようです。

より正確に書けば、ここで導出されるのは元の型に対する次のような推論補助です。

```cpp
template<class V, class U>
C(V*, U) -> C<V*, std::type_identity_t<U>> requires std::same_as<V*, std::type_identity_t<U>>;
```

実際は、エイリアステンプレートに対して推論補助を導出するのか、あくまで元の型に対するものを導出するのかは実装定義というか未規定ではあります。GCCは元の型に対する推論補助を導出し使用するようです。

### `std::array`のエイリアステンプレートに対するCTADがうまく動かない理由

### 参考文献

- [P1021R4 Filling holes in Class Template Argument Deduction](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1021r4.html)
- [P1814R0 Wording for Class Template Argument Deduction for Alias Templates](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1814r0.html)
- [CTAD for alias templates algorithm examples](https://htmlpreview.github.io/?https://github.com/mspertus/CTAD_POST_CPP17/master/CTAD_alias_examples.html)
- [Template argument deduction - cppreference](https://en.cppreference.com/w/cpp/language/template_argument_deduction)