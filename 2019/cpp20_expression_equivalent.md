# ［C++］expression-equivalentのお気持ち

## expression-equivalent??
標準ライブラリへのRangeの導入に伴って新たに追加された言葉で、次のように定義されています。

>expressions that all have the same effects, either are all potentially-throwing ([except.spec]) or are all not potentially-throwing, and either are all constant subexpressions or are all not constant subexpressions

何となく噛み砕くと以下のような意味合いです

ある2つ以上の式は、次の全てを満たす場合に*expression-equivalent*である

- 式は同じ効果を持つ
- 例外を投げるかどうかが同一
  - 全ての式は例外を投げない
  - もしくは、全ての式は例外を投げうる
- 式の1部もしくは全部が定数式で実行可能であるかも同一
  - 全ての式は、1部もしくは全部が定数実行可能である
  - もしくは、全ての式はその1部も含めて定数実行不可

これは要するに、式の効果と例外を投げるかどうか、および定数式で実行可能かどうか、が全く同一である時に*expression-equivalent*の関係にある、という事です。

## これは何？

これは主にRangeライブラリのカスタマイぜーションポイントオブジェクト（以下CPO）の効果の定義において頻出します。  
大体以下の様な形式で書かれています。

>The expression *`CPO-name(E)`* for some subexpression E is expression-equivalent to:
>
>- expression-equivalentとなる式 if 条件
>- Otherwise, expression-equivalentとなる式 if 条件
>- ...
>- Otherwise, *`CPO-name(E)`* is ill-formed. 

ここでの`CPO-name`は任意のカスタマイぜーションポイントオブジェクト名で、`E`とはそのCPOの呼び出しに引数として与えられている式のことです。  
そしてこの文章は、引数`E`によって`CPO-name(E)`の呼び出しがどのような効果を持つか？をつらつらと書いています（大体最後はill-formedとなりますが、ならない場合もあります）。

これは、これまでの標準ライブラリ関数等ならばその効果（*Effects*）の定義において、*Equivalent to :*以下に書かれていたものです。  
つまり、*expression-equivalent*はこれまで説明に使われていた*Equivalent to*をCPO用に置き換えているものだと言えます。

## *Equivalent to*との違い

*Equivalent to*では、ある関数等の効果を別の式の効果と等価であるとして定義します。この時、その効果には式が例外を投げるのかどうか、また部分的にでも定数式で実行可能であるか、が含まれてはいないようです。  
それらは式の効果ではなく、関数に指定されているものだからです。

Rangeライブラリのカスタマイゼーションポイントオブジェクトは名前空間スコープに定義された関数オブジェクトであり、その呼び出しではADL等の機構によりユーザーが定義した任意の型に対してさえも目的となる処理を行おうとします。
その結果として、CPOの効果は一通りではありません。

Rangeライブラリ利用ユーザーはCPOの持つ効果のどれかに引っかかるように巧妙に自分の持つ型をカスタマイズすれば、Rangeライブラリに定義されている処理に任意の型をアダプトできます。

効果が複数あり、しかも入ってくる型がどのようにその効果のいずれかに対してアダプトされているかはわかりません。そのため、CPOの呼び出しは定数実行できるのか？呼び出しに伴って例外を投げるのか？は実行される処理によります。

*Equivalent to*では指定した式の`constexpr`性及び`noexcept`性は伝播されないので、*Equivalent to*で効果を指定するだけではCPOの呼び出しが`constexpr`であるか`noexcept`であるかは未規定になってしまいます。

そのため、*expression-equivalent*が必要になります。*expression-equivalent*な関係にある2つの式は、効果だけではなく`constexpr`性及び`noexcept`性に関しても同一です。  
従って、CPOの呼び出しの効果として*expression-equivalent*とされている式に呼び出された型を当てはめることで、その効果と定数実行可能であるか？例外を投げうるか？をも含めて表明することができます。

## 例

なにいってんだこいつという感じなので例として、[`std::ranges::begin()`](http://eel.is/c++draft/range.access.begin)を見てみましょう。  
`std::begin()`は関数ですが、これはカスタマイゼーションポイントオブジェクトです。その効果は次のようにあります。

>The name ranges​::​begin denotes a customization point object. The expression ranges​::​​begin(E) for some subexpression E is expression-equivalent to: 
>
>- `E + 0` if E is an lvalue of array type ([basic.compound]).
>- Otherwise, if E is an lvalue, `decay-copy(E.begin())` if it is a valid expression and its type I models input_­or_­output_­iterator.
>- Otherwise, `decay-copy(begin(E))` if it is a valid expression and its type I models input_­or_­output_­iterator with overload resolution performed in a context that includes the declarations: 
>
> ```cpp
>template<class T> void begin(T&&) = delete;
>template<class T> void begin(initializer_list<T>&&) = delete;
> ```
>
> and does not include a declaration of ranges​::​begin.
>- Otherwise, ranges​::​begin(E) is ill-formed.

引数の式を`E`として`std::ranges::begin(E)`のように呼び出したとき、その効果は`E`に応じてその下に書かれている4つのいずれかと等価（*expression-equivalent*）、という事を言っています。

ユーザーが自作する任意の型に対して作用するのはおそらく2つ目と3つ目のものです。それぞれ以下のように定義されます。

- 2つ目は、引数`E`の（結果となるオブジェクトの）メンバ関数として定義されている`E.begin()`を呼び出す。  
- 3つ目は、`E`の（結果となるオブジェクトの）関連名前空間からADLで見つかる`begin()`か、`std::begin()`を呼び出す。


この`begin()`をアダプトしたつもりの自作の型`T`のオブジェクト`a`で呼び出したときに*expression-equivalent*であるとは

2つ目の形式にアダプトした場合、`std::ranges::begin(a)`の呼び出しが`constexpr`となるかは（あなたが書いた）`a.begin()`の定義によって決まり、例外を投げるかも（あなたが書いた）`a.begin()`によって決まるという事です。

同様に、3つ目の形式にアダプトした場合も、ユーザーが定義した（あなたが書いた）フリー関数の`begin(a)`が`constexpr`なのか`noexcept`なのかでそれらが決定される訳です。

さらに、どちらの場合も結果となるイテレータは`decay_copy`されて返されますが、この`decay_copy`の処理が同様に`constexpr`なのか`noexcept`なのかも（おそらくあなたが定義しているであろう）返されたイテレータ型によるわけです。

~~つまりはとっても他力本願な定義の仕方なのです。~~

## 参考文献
- [16.3.11 expression-equivalent [defns.expression-equivalent]](http://eel.is/c++draft/defns.expression-equivalent)
- [Use expression-equivalent in definitions of CPOs - Github](https://github.com/ericniebler/stl2/issues/262)

## 謝辞

この記事の9割は以下の方によるご指摘によって成り立っています。

- [@yohhoy さん](https://twitter.com/yohhoy/status/1171677701498781696)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/cpp20_expression_equivalent.md)