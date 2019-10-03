# ［C++］構造化束縛とラムダキャプチャ

一部のコンパイラでは構造化束縛宣言で導入された変数をラムダ式によってキャプチャすることができません。  
実は、厳密に規格にのっとればC++17ならば出来ない、C++20からはできる、が正しい動作になります。

ただ、規格を眺めてもC++17でできず、C++20できるようになる理由を見出せません。なぜなら、結果的にどこにも書かれていないからです・・・

### C++17における構造化束縛宣言の動作モデル（N4659時点の仕様）

※ここの項目は構造化束縛宣言の仕様を読み解くことに熱を入れすぎて脱線しています。構造化束縛宣言に指定する名前は変数名ではない、という結論だけ頭に入れて次に進んでも構いません・・・。

構造化束縛宣言は変数宣言のように見えますが、その見た目と用途ほど動作は単純ではありません（しかし、通常はこれを知る必要はありません・・・）。

構造化束縛宣言は次のような形式の宣言です。

- attribute-specifier-seq(opt) decl-specifier-seq ref-qualifier(opt) [identifier-list] initializer ;

何書いてあるのか良く分からないので説明のために単純化します。属性指定（attribute-specifier-seq）は多分使わないので省略し、decl-specifier-seqは`CV auto`の事なのでそう書き直し、参照修飾（ref-qualifier）も直接書いておきます。  
また、初期化子（initializer）には`=, (), {}`の3つの形が使用できますが、専ら使うのは`=`だけだと思うので`=`の形だとしておきます。

- (`cv`) `auto` (`&`|`&&`) `[identifier-list]` `= expression;`

構造化束縛宣言はまず、左辺にある`expression`の結果となるオブジェクト（`result`と名付けておきます）を受けるための暗黙の変数を導入します。名前を`temp`とでもしておきます（規格書中では`e`）。  
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

#### 参照される型

各ケースでそれぞれ**参照される型**として定義されている型は、構造化束縛宣言の`[identifier-list]`内のそれぞれの識別子を`decltype`したときに返される型に当たります。


### C++17規格（N4659）完成後の変更

つい構造化束縛を読み解くのに熱くなってしまいましたが本題に戻りましょう・・・



ただ、この2つの変更はC++17の規格書（N4659）には載っていません。  
Core issue 2313はC++17規格完成後に欠陥報告としてC++17に適用され、P0588R1はC++20で承認され明文化されたためです。

結果全てのケースにおいて、構造化束縛宣言で変数名のつもりで指定している名前は変数名ではなく暗黙の対象オブジェクトのメンバ・要素を示す名前でしかなく、プログラム上の意味を持たないものです。そのため、それらの名前はラムダ式でキャプチャすることができません。

### C++20での構造化束縛宣言の拡張


### 参考文献
- [Lambda implicit capture fails with variable declared from structured binding - stackoverflow](https://stackoverflow.com/questions/46114214/lambda-implicit-capture-fails-with-variable-declared-from-structured-binding)
- [Core issue 2313 : Redeclaration of structured binding reference variables](https://wg21.cmeerw.net/cwg/issue2313)
- [P0588R1 : Simplifying implicit lambda capture](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0588r1.html)
- [P1091R3 : Extending structured bindings to be more like variable declarations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1091r3.html)
- [構造化束縛 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/structured_bindings.html)
- [構造化束縛宣言 - cppreference.com](https://ja.cppreference.com/w/cpp/language/structured_binding)
- [11.5 Structured binding declarations - Working Draft, Standard for Programming Language C++ (N4659)](https://timsong-cpp.github.io/cppwp/n4659/dcl.struct.bind)