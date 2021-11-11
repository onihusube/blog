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
  [[maybe_unused]] std_array_with_int ar2 = { 1, 2, 3 };  // ng、なして？
  [[maybe_unused]] std_array_with_3 ar3 = { 1, 2, 3 };    // ng、なして？
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ZYpj0t8CFK4ALCOm)

ようするに、`std::array`のテンプレートパラメータの一部だけを束縛したエイリアステンプレートで[CTAD](https://cppmap.github.io/articles/acronyms/#ctad-class-template-argument-deduction)を期待すると、謎のコンパイルエラーに悩まされています。

エイリアステンプレートのCTADが絡み非常に複雑な問題であり、簡易に回答できなさそうなのでこの記事を書きました。

[:contents]

### CTADの仕組み（雑）

あるクラステンプレート`C`についてのCTADは、`C`のコンストラクタを変換して得た関数テンプレート（引数はそのコンストラクタの引数、テンプレートパラメータは`C`のテンプレートパラメータにそのコンストラクタのテンプレートパラメータを合併したもの、戻り値型はそのコンストラクタのテンプレートパラメータのうち`C`のものに対応するパラメータで特殊化された`C<Ts...>`）と、`C`に定義された推論補助を関数テンプレートとして抽出し、初期化式（`C = c{args...};`）に与えられている実引数列（`args...`）を用いてそれらの関数テンプレートを呼び出したかのようにオーバーロード解決を行い、最適にマッチした1つの関数テンプレートの戻り値型からテンプレートパラメータが補われた`C<Ts...>`を取得するものです。

CTADはコンストラクタ呼び出しよりも前に行われ、必ずしも使用される推論補助（コンストラクタからの関数テンプレート）と実際に呼び出されるコンストラクタが対応していなくても良く、推論補助に関してはほぼ関数テンプレートのように書くことができます（コンセプトやSFINAEによる制約などを行えます）。

重要なことは、コンストラクタおよび推論補助を関数テンプレートとして扱って、実引数を用いてオーバーロード解決を行なって、残った1つの戻り値型から完全な型を取得するという手順です。CTADはクラス型・集成体型・エイリアステンプレートの3つに対して行われますが、バックエンド部（関数テンプレートとしてオーバーロード解決以降）はそれらで共通で、異なるのはその関数テンプレートをなんとか抽出するフロントエンド部分のプロセスです。

### エイリアステンプレートのCTADの仕組み

エイリアステンプレートのCTADは、元の型の推論補助を変換してエイリアステンプレートの推論補助を導出し、それを利用することで行われます。そのアルゴリズムはおおよそ次のようになります（以下では、導出したいエイリアステンプレートの推論補助を`A`、元の型に存在する推論補助（およびコンストラクタからの関数テンプレート）を`B`と表します）。

1. エイリアステンプレートの元の型のコンストラクタと推論補助`B`を（関数テンプレートとして）全て取得する
      - 以下の手順はそうして取得した`B`1つ1つに対してそれぞれ行われる
2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する
      - この処理は、関数テンプレートのテンプレートパラメータ推論と同様に行われる（ただし、推論できないパラメータがある場合でも失敗しない）
      - 推論できないコンテキストが存在しうるため、この時に全てのテンプレートパラメータを推論する必要はない
3. 2で暫定的に得られた`A`の内容を、`B`にフィードバックして置き換える
      - 2で全てのパラメータの推論が出来ていない可能性があるので、ここで得られた推論補助はエイリアステンプレートと`B`それぞれからのテンプレートパラメータを含む可能性がある
4. 結果の型（3で得られた推論補助の右辺）からエイリアスを推定し、3で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する
      - 結果の型からエイリアスを推定するか、またどのように推定するかは実引数型に依存するため、追加の制約が必要となる場合がある

このような導出（あるいは推論補助の変換）は、エイリアステンプレートの元の型のコンストラクタと推論補助から抽出した関数テンプレート1つづつに対して行われ、そうして無事に導出できた（中には失敗するものがありうる）推論補助を、通常の推論補助と同じように扱ってエイリアステンプレートのCTADは行われます。

### 例1、単純な例

次のような型で動作例を見てみます。

```cpp
// 今回の例の対象エイリアステンプレート
template<typename T>
using P = std::pair<int, T>;
```

このコードで、`P`に対する推論補助がどのように導出されるかを先ほどの手順に沿って見てみます（以下、`std::pair`の`std`を省略します）。

#### 2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する

`pair`の推論補助は1つだけが用意されています（コンストラクタからのものは今回は無視します）

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

の右辺から、テンプレートパラメータのペア`<T1, T2>`と`<int, T>`から、`T1 = int, T2 = T`（と`typename T2 = typename T`）の対応を得ます。

ここでは、`pair`の推論補助`B`のテンプレートパラメータを持ち、`B`の右辺の型（`pair<T1, T2>`）を引数型とする関数テンプレートに対して、エイリアステンプレート`P`の右辺の型（`pair<int, T>`）の値を引数として渡したときの関数テンプレートのテンプレートパラメータ推論とほぼ同じことを行なって、テンプレートパラメータの対応を得ます。

```cpp
template<typename T1, typename T2>
void f(pair<T1, T2>);

f(pair<int, T>{});
```

このような`f`の`T1, T2`に推論される型を求めることで対応を得ます。この時、`T`のように具体的な型ではないテンプレートパラメータに対しても推論を行い、テンプレートパラメータのまま対応させます。それによって、`T1 = int, T2 = T`の対応が得られます。

#### 3. 2で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える

`B`

```cpp
template<typename T1, typename T2>
pair(T1, T2) -> pair<T1, T2>;
```

に、先ほど得た対応（`T1 = int, T2 = T`）とエイリアステンプレートのテンプレートパラメータをフィードバックします。

まずエイリアステンプレートのテンプレートパラメータをそのまま、推論補助のテンプレートパラメータリストの先頭にフィードバックすると

```cpp
template<typename T, typename T1, typename T2>
pair(T1, T2) -> pair<T1, T2>;
```

となり、次に`B`と`P`のテンプレートパラメータの対応（`T1 = int, T2 = T`）をフィードバックします。

```cpp
template<typename T>
pair(int, T) -> pair<int, T>;
```

この時、対応が確定している`B`のテンプレートパラメータについてはすでにテンプレートではないので（対応先が`P`のテンプレートパラメータだったとしても）、テンプレートパラメータ宣言（`typename T1, typename T2`）は削除します。

#### 4. 結果の型（2で得られた推論補助の右辺）からエイリアスを推定し、3で得られた推論補助を書き換えることで、エイリアステンプレートに対する推論補助`A`を生成する

最後に、得られた推論補助とエイリアステンプレート

```cpp
template<typename T>
pair(int, T) -> pair<int, T>;

template<typename T>
using P = pair<int, T>;
```

の対応から、エイリアステンプレートのテンプレート実引数を推論し、推論補助を完成します。ここでは、エイリアスを戻すような形で推論補助の型を置き換えます。

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

これらの右辺からテンプレートパラメータの対応を求めます。それは、関数テンプレートの引数推論と同様に行われるので、

```cpp
template<class T>
void f(VeryLongNameXXXXX<decay_t<T>>);

f(VeryLongNameXXXXXX<A>{});
```

このように呼んだ時の`T`の推論によって対応を求めますが、ご存知のように？これは推論できないコンテキストとされ、`T`の推論はできません。したがって、ここでは何の対応も得られません。

#### 3. 2で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える


先ほど得られた情報を`B`にフィードバックするわけですが、何の対応も得られていないのでフィードバックは行われず、このステップは何もしません。よって、元の推論補助そのままが得られます。

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

// 今回のエイリアステンプレート
template<class V>
using A = C<V*, V*>;
```

#### 2. エイリアステンプレートの右辺と`B`の右辺から、`A`のテンプレートパラメータを推論する

`C`の推論補助は1つだけです（コンストラクタからのものは無視）。

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

関数テンプレートで表すと

```cpp
template<class T, class U>
void f(C<T, std::type_identity_t<U>>);

f(C<V*, V*>{});
```

のように呼んだ時の`T, U`に行われるのと同じ推論が行われます。

ここで得られる対応は、`T = V*`のみで、`U`との対応は得られません（推論できないコンテキストです）。

#### 3. 2で暫定的に得られた`A`の内容を、元の推論補助`B`にフィードバックして置き換える

先ほど得られた情報（`T = V*`）とエイリアステンプレートのテンプレートパラメータを`B`

```cpp
template<class T, class U>
C(T, U) -> C<T, std::type_identity_t<U>>;
```

にフィードバックします。

まずテンプレートパラメータをフィードバックし

```cpp
template<class V, class T, class U>
C(T, U) -> C<T, std::type_identity_t<U>>;
```

テンプレートパラメータの対応（`T = V*`）をフィードバックします

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

実際は、エイリアステンプレートに対して推論補助を導出するのか、あくまで元の型に対するものを導出するのかは実装定義というか未規定で、GCCは元の型に対する推論補助を導出し使用するようです。

### `std::array`のエイリアステンプレート1

エイリアステンプレートに対するCTADがどうなっているのかを理解したところで、本題に戻ります。

まずは、`std::array<T, N>`の`T`を束縛するエイリアス

```cpp
// 要素型を束縛するエイリアス
template<auto N>
using std_array_with_int = std::array<int, N>;
```

について導出される推論補助を求めてみます。

`std::array`には推論補助が1つしかなく、コンストラクタ（集成体初期化）からの推論補助相当のものは得られません（要素1つに対して初期化子複数となるため）。

```cpp
namespace std {
  template <class T, class... U>
  array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```

この推論補助とエイリアスから、テンプレートパラメータの対応を求めます。

```cpp
template <class T, class... U>
void f(array<T, 1 + sizeof...(U)>);

f(std::array<int, N>{});
```

明らかに要素数は推論できないコンテキストなので、得られるのは`T = int`という対応のみです。

対応が得られているので、まずエイリアステンプレートのテンプレートパラメータを推論補助へフィードバックし

```cpp
template <auto N, class T, class... U>
array(T, U...) -> array<T, 1 + sizeof...(U)>;
```

`T = int`の対応をフィードバックします。

```cpp
template <auto N, class... U>
array(int, U...) -> array<int, 1 + sizeof...(U)>;
```

そしてエイリアスを推定する（戻す）と

```cpp
template <auto N, class... U>
std_array_with_int(int, U...) -> std_array_with_int<1 + sizeof...(U)>;
```

省略していますが、`std::array`の元の推論補助には`T`と`U...`のすべての型が同じであることが制約されているので、それも継承されています。

そして、この推論補助の問題点は`auto N`を解決できないことです。どのような初期化式が与えられてもこの`N`が推論されることはなく、そのためコンパイルエラーを起こします。

#### GCCの導出する推論補助

GCCは、CTADでエラーが起きた時に使用した推論補助の候補をエラーメッセージ中に出力してくれます。

```
prog.cc: In function 'int main()':
prog.cc:12:53: error: class template argument deduction failed:
   12 |     [[maybe_unused]] std_array_with_int ar2 = {1,2,3};//ng
      |                                                     ^
prog.cc:12:53: error: no matching function for call to 'array(int, int, int)'
In file included from prog.cc:1:
/opt/wandbox/gcc-head/include/c++/12.0.0/array:267:5: note: candidate: 'template<auto N, class _Tp, class ... _Up> std::array(_Tp, _Up ...)-> std::array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, (1 + sizeof... (_Up))> requires  __is_same(std::std_array_with_int<N>, std::array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, 1 + sizeof ... (_Up ...)>)'
  267 |     array(_Tp, _Up...)
      |     ^~~~~
/opt/wandbox/gcc-head/include/c++/12.0.0/array:267:5: note:   template argument deduction/substitution failed:
prog.cc:12:53: note:   couldn't deduce template parameter 'N'
   12 |     [[maybe_unused]] std_array_with_int ar2 = {1,2,3};//ng
      |                                                     ^

```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ZYpj0t8CFK4ALCOm)


今回のケースでGCCが導出して使用している推論補助は

```cpp
template<auto N, class _Tp, class ... _Up>
array(_Tp, _Up ...) -> array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, (1 + sizeof... (_Up))>
  requires  __is_same(std::std_array_with_int<N>,
                      std::array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, 1 + sizeof ... (_Up ...)>)
```

というものです（見やすいように改変しています）。先ほどは省略していた関連制約が見えていますが、ほぼ求めた推論補助と同じものであることが分かります。ただし、テンプレートパラメータが1つ多いです。

GCC実装の`std::array`の推論補助は次のように宣言されています。

```cpp
template<typename _Tp, typename... _Up>
array(_Tp, _Up...) -> array<enable_if_t<(is_same_v<_Tp, _Up> && ...), _Tp>, 1 + sizeof...(_Up)>;
```

`_Tp`と`_Up`の各型が同じであることを`enable_if`によって制約しているわけです。CTADとこの推論補助はともにC++17で導入されたものであるため、この実装は妥当です。そして、テンプレートパラメータ名的に、先ほどエラーメッセージから拾い上げた推論補助に含まれる余分なテンプレートパラメータ`_Tp`はここからのもので、`_Tp = int`の対応が取れていないことがうかがえます。

これは、2ステップ目のテンプレートパラメータの対応を求める際に

```cpp
template <class T, class... U>
void f(array<enable_if_t<(is_same_v<_Tp, _Up> && ...), _Tp>, 1 + sizeof...(_Up)>);

f(std::array<int, N>{});
```

となり、`T`も推論できないコンテキストとなって`T = int`の対応が取れなくなるため起きています。そのためそれがフィードバックされず、導出された推論補助のテンプレートパラメータは`auto N, class _Tp, class ... _Up`の3つになっています。ただ、ステップ4では`enable_if_t<(is_same_v<_Tp, _Up> && ...), _Tp> = int`の対応が取れることが分かるため、それについての制約が追加の`requires`節にておこなわれているようです。

とはいえ、そうであっても結論は変わらず、結局`auto N`が推定できないためこの推論補助は使い物になりません。そしてそれは、先ほどのGCCのエラーメッセージにも表示されています（最後のほうの「couldn't deduce template parameter 'N'」）。

### `std::array`のエイリアステンプレート2

次に、`std::array<T, N>`の`N`を束縛するエイリアス

```cpp
// 要素数を束縛するエイリアス（区別のためにT->Eへパラメータ名を変更
template<typename E>
using std_array_with_3 = std::array<E, 3>;
```

について導出される推論補助を求めてみます。

```cpp
namespace std {
  template <class T, class... U>
  array(T, U...) -> array<T, 1 + sizeof...(U)>;
}
```

この推論補助とエイリアスから、テンプレートパラメータの対応を求めます。

```cpp
template <class T, class... U>
void f(array<T, 1 + sizeof...(U)>);

f(std::array<E, 3>);
```

要素数の方は推論できないコンテキストなので、得られるのは、`T = E`という対応です。

これを推論補助へフィードバックすると

```cpp
template <typename E, class T, class... U>
array(T, U...) -> array<T, 1 + sizeof...(U)>;
```

```cpp
template <typename E, class... U>
array(E, U...) -> array<E, 1 + sizeof...(U)>;
```

そしてエイリアスを推定する（戻す）と

```cpp
template <typename E, class... U>
std_array_with_3(E, U...) -> std_array_with_3<E> requires (1 + sizeof...(U) == 3);
```

省略していますが、`std::array`の元の推論補助には`T`（`E`）と`U...`のすべての型が同じであることが制約されているので、それも継承されています。

あれ？これはなんかいけそうな雰囲気がしていますが・・・？

#### GCCの導出する推論補助

実際エラーとなってるGCCの出力を見てみましょう。

```
prog.cc: In function 'int main()':
prog.cc:13:51: error: class template argument deduction failed:
   13 |     [[maybe_unused]] std_array_with_3 ar3 = {1,2,3};//ng
      |                                                   ^
prog.cc:13:51: error: no matching function for call to 'array(int, int, int)'
In file included from prog.cc:1:
/opt/wandbox/gcc-head/include/c++/12.0.0/array:267:5: note: candidate: 'template<class T, class _Tp, class ... _Up> std::array(_Tp, _Up ...)-> std::array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, (1 + sizeof... (_Up))> requires  __is_same(std::std_array_with_3<T>, std::array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, 1 + sizeof ... (_Up ...)>)'
  267 |     array(_Tp, _Up...)
      |     ^~~~~
/opt/wandbox/gcc-head/include/c++/12.0.0/array:267:5: note:   template argument deduction/substitution failed:
prog.cc:13:51: note:   couldn't deduce template parameter 'T'
   13 |     [[maybe_unused]] std_array_with_3 ar3 = {1,2,3};//ng
      |                                                   ^
In file included from prog.cc:1:
/opt/wandbox/gcc-head/include/c++/12.0.0/array:95:12: note: candidate: 'template<class T> array(std::array<T, 3>)-> std::array<T, 3>'
   95 |     struct array
      |            ^~~~~
/opt/wandbox/gcc-head/include/c++/12.0.0/array:95:12: note:   template argument deduction/substitution failed:
prog.cc:13:51: note:   mismatched types 'std::array<T, 3>' and 'int'
   13 |     [[maybe_unused]] std_array_with_3 ar3 = {1,2,3};//ng
      |                                                   ^
In file included from prog.cc:1:
/opt/wandbox/gcc-head/include/c++/12.0.0/array:95:12: note: candidate: 'template<class T> array()-> std::array<T, 3>'
   95 |     struct array
      |            ^~~~~
/opt/wandbox/gcc-head/include/c++/12.0.0/array:95:12: note:   template argument deduction/substitution failed:
prog.cc:13:51: note:   candidate expects 0 arguments, 3 provided
   13 |     [[maybe_unused]] std_array_with_3 ar3 = {1,2,3};//ng
      |     
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/nt5lW7TPqUjVo3m2)

使用されている推論補助は

```cpp
template<class T, class _Tp, class ... _Up>
array(_Tp, _Up ...) -> array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, (1 + sizeof... (_Up))>
  requires  __is_same(std::std_array_with_3<T>,
                      std::array<typename std::enable_if<(is_same_v<_Tp, _Up> && ...), _Tp>::type, 1 + sizeof ... (_Up ...)>)
```

先ほどど同じ理由で、エイリアステンプレートの`T`と`std::array`の推論補助の`_Tp`の対応が取れない結果、エイリアステンプレートの`T`が推論補助にフィードバックされてしまい、テンプレートパラメータが`class T, class _Tp, class ... _Up`の3つになります。しかも、`T`に対応する仮引数はないので（推論補助の左辺に`T`が現れていない）、結局`auto N`と同じように`T`を実引数から推論できず、コンパイルエラーを起こしています。

エラーメッセージを見ると、MSVCもほぼ同じ理由によってエラーとなっている様子です。
- [godbolt](https://godbolt.org/z/s19PKsaGx)

これは、推論補助に対する制約（`_Tp`と`_Up...`のすべての型が同じ型である）をSFINAEによって行なっていることから生じています。

#### SFINAEを使わなくしたら行ける？

C++20からはコンセプトが使用でき、コンセプトによって制約してやれば`requires`節で（すなわち推論補助の右辺の外で）パラメータに対する制約を行えます。`std::array`の要素数を束縛するエイリアステンプレートの場合、そのようにすればCTADが正しく働く気がしてなりません。実験してみましょう。

```cpp
#include <concepts>

template<typename T, std::size_t N>
struct my_array {
  T arr[N];
};

template<typename T, typename... Us>
  requires (std::same_as<T, Us> && ...)
my_array(T, Us...) -> my_array<T, sizeof...(Us) + 1>;


template<typename T>
using myarray_3 = my_array<T, 3>;
```

`std::array`相当のクラス（`my_array`）を作成して、これに対して要素数を束縛するエイリアステンプレート（`myarray_3`）を書いて試してみます。

```cpp
int main() {
  // ok
  [[maybe_unused]]
  my_array a1 = {1, 2, 3, 4};

  // これは制約に引っかかって正しくエラーになる
  [[maybe_unused]]
  my_array a2 = {1, 2.0, 3, 4};
  
  // ok!
  [[maybe_unused]]
  myarray_3 a3 = {1, 2, 3};
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NE0B6BKZ2TONPfBV)

無事正しく動きました。つまり、`std::array`の推論補助の実装でSFINAEを避ければ要素型の推論はできそうです。

（ただし、[MSVCは受け入れてくれない](https://godbolt.org/z/f6rh3x4T4)ようです）

ここでGCCがやっていることを確かめるために、わざとエラーを起こしてエラーメッセージを見てみます。

```
prog.cc: In function 'int main()':
prog.cc:24:28: error: class template argument deduction failed:
   24 |   myarray_3 a3 = {1, 2, 3.0};
      |                            ^
prog.cc:24:28: error: no matching function for call to 'my_array(int, int, double)'
prog.cc:10:1: note: candidate: 'template<class T, class ... Us>  requires (same_as<T, Us> && ...) my_array(T, Us ...)-> my_array<T, (sizeof... (Us) + 1)> requires  __is_same(myarray_3<T>, my_array<T, sizeof ... (Us ...) + 1>)'
   10 | my_array(T, Us...) -> my_array<T, sizeof...(Us) + 1>;
      | ^~~~~~~~
prog.cc:10:1: note:   template argument deduction/substitution failed:
prog.cc:10:1: note: constraints not satisfied
prog.cc: In substitution of 'template<class T, class ... Us>  requires (same_as<T, Us> && ...) my_array(T, Us ...)-> my_array<T, (sizeof... (Us) + 1)> requires  __is_same(myarray_3<T>, my_array<T, sizeof ... (Us ...) + 1>) [with T = int; Us = {int, double}]':
prog.cc:24:28:   required from here
prog.cc:10:1:   required by the constraints of 'template<class T, class ... Us>  requires (same_as<T, Us> && ...) my_array(T, Us ...)-> my_array<T, (sizeof... (Us) + 1)> requires  __is_same(myarray_3<T>, my_array<T, sizeof ... (Us ...) + 1>)'
prog.cc:10:1: note: the expression '(same_as<T, Us> && ...) [with T = int; Us = {int, double}]' evaluated to 'false'
prog.cc:4:8: note: candidate: 'template<class T> my_array(my_array<T, 3>)-> my_array<T, 3>'
    4 | struct my_array {
      |        ^~~~~~~~
prog.cc:4:8: note:   template argument deduction/substitution failed:
prog.cc:24:28: note:   mismatched types 'my_array<T, 3>' and 'int'
   24 |   myarray_3 a3 = {1, 2, 3.0};
      |                            ^
prog.cc:4:8: note: candidate: 'template<class T> my_array()-> my_array<T, 3>'
    4 | struct my_array {
      |        ^~~~~~~~
prog.cc:4:8: note:   template argument deduction/substitution failed:
prog.cc:24:28: note:   candidate expects 0 arguments, 3 provided
   24 |   myarray_3 a3 = {1, 2, 3.0};
      |   
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/45BUfScvGe9YzEQL)

ここでGCCが使用している推論補助は

```cpp
template<class T, class ... Us>
  requires (same_as<T, Us> && ...)
my_array(T, Us ...) -> my_array<T, (sizeof... (Us) + 1)>
  requires  __is_same(myarray_3<T>, my_array<T, sizeof ... (Us ...) + 1>)
```

これは先ほど手（脳内CTADマシーン）で求めてみた推論補助の想定とほぼ一致しています。

### `std::array`のエイリアステンプレートでCTADするには結局どうすればいいんですか？

この質問は2つのパターンに分岐し、それぞれで答えが異なります。

1. 要素数を束縛したエイリアスの場合（最初の`std_array_with_int`）
     - 無理です（もしかしたら、推論補助の形を工夫すれば行けるかもしれませんが、わかりません・・・）
2. 要素型を束縛したエイリアスの場合（最初の`std_array_with_3`）
     - 実装の推論補助をSFINAEを使わない形で書き直させれば行けます

1をなんとかするアイデアをお持ちの方がいましたら教えて欲しいです（多分LWG Issueとして提出できます）。

### 参考文献

- [P1021R4 Filling holes in Class Template Argument Deduction](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1021r4.html)
- [P1814R0 Wording for Class Template Argument Deduction for Alias Templates](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1814r0.html)
- [CTAD for alias templates algorithm examples](https://htmlpreview.github.io/?https://github.com/mspertus/CTAD_POST_CPP17/master/CTAD_alias_examples.html)
- [Template argument deduction - cppreference](https://en.cppreference.com/w/cpp/language/template_argument_deduction)
- [12.4.1.8 Class template argument deduction [over.match.class.deduct] - N4861](https://timsong-cpp.github.io/cppwp/n4861/over.match.class.deduct)

### 謝辞

この記事の9割は次の方のご指摘によって成り立っています。

- [@yohhoyさん](https://twitter.com/yohhoy/status/1458739193262215172)
- [@nus_mizさん](https://twitter.com/nus_miz/status/1458751881858015240)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2021/20211110_alias_template_ctad.md)
