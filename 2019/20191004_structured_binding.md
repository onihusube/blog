# ［C++］構造化束縛の動作モデルとラムダキャプチャ

一部のコンパイラでは構造化束縛宣言で導入された変数をラムダ式によってキャプチャすることができません。  
実は、厳密に規格にのっとればC++17ならば出来ない、C++20からはできる、が正しい動作になります。

ただ、規格を眺めてもC++17でできず、C++20できるようになる理由を見出せません。なぜなら、結果的にどこにも書かれていないからです・・・

[:contents]

### C++17における構造化束縛宣言の動作モデル（N4659時点の仕様）

※ここの項目は構造化束縛宣言の仕様を読み解くことに熱を入れすぎて脱線しています。構造化束縛宣言に指定する名前は変数名ではない、という結論だけ頭に入れて次に進んでも構いません・・・。

構造化束縛宣言は変数宣言のように見えますが、その見た目と用途ほど動作は単純ではありません（しかし、通常はこれを知る必要はありません・・・）。

構造化束縛宣言は次のような形式の宣言です。

- attribute-specifier-seq(opt) decl-specifier-seq ref-qualifier(opt) [identifier-list] initializer ;

何書いてあるのか良く分からないので説明のために単純化します。属性指定（attribute-specifier-seq）は多分使わないので省略し、decl-specifier-seqは`CV auto`の事なのでそう書き直し、参照修飾（ref-qualifier）も直接書いておきます。  
また、初期化子（initializer）には`=, (), {}`の3つの形が使用できますが、専ら使うのは`=`だけだと思うので`=`の形だとしておきます。

- (`cv`) `auto` (`&`|`&&`) `[identifier-list]` `= expression;`

構造化束縛宣言はまず、右辺にある`expression`の結果となるオブジェクト（`result`と名付けておきます）を受けるための暗黙の変数を導入します。名前を`temp`とでもしておきます（規格書中では`e`）。  
この変数`temp`の型の決定及び初期化は次のように決まります。

- `result`の型が参照型でない型`A`の配列なら、`(cv) A`の配列（CV修飾は構造化束縛宣言の`cv`から） 
    - `temp`の各要素は対応する`result`の要素からコピーor直接初期化される
- それ以外の場合、構造化束縛宣言の`[identifier-list]`を`temp`で置き換えた式によって`temp`を定義する
    - (`cv`) `auto` (`&`|`&&`) `temp = result;`

この様な決定の仕方によって、構造化束縛宣言に指定されているCV・参照修飾（及び属性指定）は暗黙の変数`temp`に対して適用され、`identifier-list`内の変数名に適用される訳ではない事が分かります。

この様に初期化された`temp`の、参照を除去した型を`E`とすると（`E = std::remove_reference_t<decltype(temp)>`）、`E`の型に応じて次の3つのパターンに分岐します。

1. `E`が配列型
2. `E`がtuple-likeな型
3. `E`が構造体

#### 配列型の場合

`[identifier-list]`内の変数名を順に`vi`とすると、各`vi`は`temp`の`i`番目の要素を示す左辺値の名前です。  
`E`の要素型を`(cv) T`とすると**参照される型**は`(cv) T`であり、そのCV修飾は構造化束縛宣言の指定によります。

当然ですが、`temp`（`result`）の要素数と`[identifier-list]`内の名前の数は一致している必要があります。

#### tuple-likeな型の場合（user-defined case）
tuple-likeな型というのは`std::tuple`と同様に扱うことができるような、`std::tuple_size<T>`と`std::tuple_element<N, T>`が適用可能な型の事です。

まず前提として、`std::tuple_size<E>::value`が整数定数として取得可能であり、その値が`[identifier-list]`内の変数名の数と一致していなければなりません。

ここでの`temp`の値カテゴリは、`E`が左辺値参照であればlvalue、そうでなければxvalueになります。  
型`E`が左辺値参照となるのは、構造化束縛宣言の参照指定が`auto&`の場合、もしくは`auto&&`で`result`がlvalueである場合です。すなわち、ここでは完全転送が行われます。

次に、メンバ関数の`temp.get<i>()`、見つからなければフリー関数の`get<i>(temp)`を探索します。説明のため、以降ここで見つかった関数を単に`get<i>(temp)`と統一します。

最後に、`[identifier-list]`内の変数名を順に`vi`とすると、各`vi`は`get<i>(temp)`を初期化子として初期化された参照型の変数になります。  
その型`Ti`は`std::tuple_element<i, E>::type`で与えられ、参照修飾は対応する初期化子`get<i>(temp)`の結果が左辺値なら`&`、そうでなければ`&&`になります。

各`i`に対して、**参照される型**は参照修飾無しの`Ti`となります（すなわち、`std::tuple_element<i, E>::type`）。

このケースの場合は、`std::tuple_size`と`std::tuple_element`、及び`get()`を適切に定義してやることで任意のユーザー定義型をアダプトできることから、user-defined caseと呼ばれるようです。

#### 構造体の場合

構造体の直接のデータメンバをその宣言順に`mi`として、`[identifier-list]`内の変数名を順に`vi`とすると、各`vi`は`temp`の`i`番目のデータメンバ（`temp.mi`）を示す左辺値の名前です。

それら`vi`の型`Ti`は対応する`mi`の宣言された型であり、CV修飾は`E`と同一（つまり構造化束縛宣言の`cv`指定）になります。  
**参照される型**は`(cv) Ti`になります。

この時、対応する`mi`がビットフィールドならば`vi`もビットフィールドになります。

#### 参照される型

各ケースでそれぞれ**参照される型**として定義されている型は、構造化束縛宣言の`[identifier-list]`内のそれぞれの識別子を`decltype`したときに返される型に当たります。

これらの手順を見れば、構造化束縛宣言に指定している属性指定・参照修飾はその右辺の結果を受けている暗黙のオブジェクト（`temp`）に対して行われ、CV修飾もかならずしも変数名として指定している`[identifier-list]`内の名前に伝播しないことが分かるでしょう。

#### identifier-list内の名前の扱い

「示す左辺値の名前」と言っているように、2番目のtuple-likeな型の場合を除いて構造化束縛宣言の`[identifier-list]`内の識別子名は変数名として導入されません。  
その名前はあくまで暗黙のオブジェクトの対応する要素・メンバの別名として使われるものであり、C++コードの意味論としての参照ですらありません。

そのため、それらの名前は変数名ではないのでラムダ式でキャプチャすることができない、ということのようです。


### C++17規格（N4659）完成後の変更

N4659で規定されている構造化束縛宣言では、tuple-likeの場合のみ`[identifier-list]`内の識別子名が変数名として導入されます。すなわち、その場合のみそれらの名前は普通の変数として扱うことができます。もちろんラムダによるキャプチャも。  
ですが、この挙動は構造化束縛宣言の挙動としては一貫性を欠いており、多くのC++ユーザーからしてみれば不可思議な挙動にしか見えません。

そのため、C++17規格完成後に欠陥報告として[Core issue 2313](https://wg21.cmeerw.net/cwg/issue2313)が採択され、tuple-likeの場合も変数名を導入しないように変更されました。

先ほどの手順では最後の所が次のように変更されます。

>最後に、新しい変数名`ri`を導入し、各`ri`は`get<i>(temp)`を初期化子として初期化された参照型の変数になります。  
>その型`Ti`は`std::tuple_element<i, E>::type`で与えられ、参照修飾は対応する初期化子`get<i>(temp)`の結果が左辺値なら`&`、そうでなければ`&&`になります。  
>`[identifier-list]`内の変数名を順に`vi`とすると、各`vi`は対応する`ri`が参照するオブジェクトを示す左辺値の名前です。
>その型は参照なしの`Ti`であり、**参照される型**も同様に`Ti`となります。

これによって、構造化束縛宣言の`[identifier-list]`内の識別子名は常に変数名として導入されることはなくなり、ラムダでのキャプチャもできなくなりました。  
これがC++17規格としての最終的な挙動になります。

その後、C++20を対象とした[P0588R1 : Simplifying implicit lambda capture](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0588r1.html)によって、「ラムダ式は明示的にも暗黙的にも構造化束縛宣言で導入された名前をキャプチャしてはならない」と明記されました。

めでたしめでたし・・・。

### C++20での構造化束縛宣言の拡張

しかし、その後の構造化束縛の扱いを通常の変数宣言に近づける提案[P1091R3 : Extending structured bindings to be more like variable declarations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1091r3.html)の採択によって、構造化束縛宣言の`[identifier-list]`内の識別子名をラムダ式がキャプチャできるようになりました。  
この結果、P0588R1で明記されたラムダは構造化束縛宣の導入する名前をキャプチャできない、という文章は削除されました。

P1091R3には「構造化束縛をラムダがキャプチャできないことを禁止する技術的な理由はないようだ」のように書かれています。確かに、参照している名前をそのままラムダ内部までもっていけばいいだけなので最初からこうなってほしかった感があります・・・  
また、P0588R1にも備考として「この（構造化束縛をキャプチャできないという）構造化束縛に関する文言はプレースホルダであり、（後程）構造化束縛のラムダキャプチャに必要な文言に置き換えられる」という風に書いてあるので、元からこれを見据えていたようです。

これがC++20としての挙動であり、結果的に正式な規格書にはラムダが構造化束縛宣の導入する名前をキャプチャできない、という文章が載ることはありませんでした・・・

ちなみに、C++20ではこのほかにも構造化束縛宣言に対して変更が入っています。上記C++17時点の処理モデルから大きな変更はありませんが細部が異なっています。  
ただし、構造化束縛宣言の`[identifier-list]`内の識別子名が変数名として導入されるようにはなっていません。

### 余談：なぜこんな回りくどいことに・・・？

このような複雑な処理手順を規定しているのは、結果オブジェクトのサブオブジェクトをコピーする回数を最小にするためだと思われます。

構造化束縛以前の`std::tie`を使ったコードを見ると、この処理は右辺の結果を受けて暗黙のオブジェクトを初期化したうえで、指定されている変数に対応する要素をコピーして初期化していることが見えます。

構造化束縛も単純に行ってしまえばそうなりますが、パフォーマンスの観点から見れば右辺の結果オブジェクトを初期化したうえでそのサブオブジェクトをさらに別の変数にそれぞれコピーするのは明らかに無駄です。  
しかし、それをしなければ構造化束縛のうまみは皆無です・・・

この葛藤を解決するのが、プログラマからみるとローカル変数に右辺のオブジェクトを分解しているように見え、コンパイラから見ると右辺の結果オブジェクトのサブオブジェクトをそのまま利用しているように見える、というこの動作モデルなのだと思われます。

構造化束縛（Structured binding）という名前も、指定した名前を右辺の分解可能な型の要素に対してstructuredに（構造的に : 一対一で）bindして（結びつけて）同一として扱う、みたいな意味を見出せるかもしれません・・・


### 参考文献
- [Lambda implicit capture fails with variable declared from structured binding - stackoverflow](https://stackoverflow.com/questions/46114214/lambda-implicit-capture-fails-with-variable-declared-from-structured-binding)
- [Core issue 2313 : Redeclaration of structured binding reference variables](https://wg21.cmeerw.net/cwg/issue2313)
- [P0588R1 : Simplifying implicit lambda capture](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0588r1.html)
- [P1091R3 : Extending structured bindings to be more like variable declarations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1091r3.html)
- [構造化束縛 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/structured_bindings.html)
- [構造化束縛宣言 - cppreference.com](https://ja.cppreference.com/w/cpp/language/structured_binding)
- [11.5 Structured binding declarations - Working Draft, Standard for Programming Language C++ (N4659)](https://timsong-cpp.github.io/cppwp/n4659/dcl.struct.bind)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20191004_structured_binding.md)