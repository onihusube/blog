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

これは主にRangeライブラリのカスタマイぜーションポイントオブジェクト（以下`CPO`）の効果の定義において頻出します。  
大体次のように書かれています。

>The expression *`CPO-name(E)`* for some subexpression E is expression-equivalent to:
>- expression-equivalentとなる式 if 条件
>- Otherwise, expression-equivalentとなる式 if 条件
>- ...
>- Otherwise, *`CPO-name(E)`* is ill-formed. 

ここでの`CPO-name`はカスタマイぜーションポイントオブジェクト名で、`E`とはその`CPO`の呼び出しに引数として与えられている式のことです。  
そしてこの文章は、引数`E`によって`CPO(E)`の呼び出しがどのような効果を持つか？をつらつらと書いています（大体最後はill-formedとなりますが、ならない場合もあるようです）。

これは、これまでのライブラリ関数等ならばその効果（*Effects*）の定義において、*Equivalent to :*以下に書かれていたものです。  
つまり、*expression-equivalent*は*Equivalent to*を`CPO`用に置き換えているものだと言えます。

## 参考文献
- [16.3.11 expression-equivalent [defns.expression-equivalent]](http://eel.is/c++draft/defns.expression-equivalent)
- [Use expression-equivalent in definitions of CPOs - Github](https://github.com/ericniebler/stl2/issues/262)

## 謝辞

この記事の9割は以下の方によるご指摘によって成り立っています。

- [@yohhoy さん](https://twitter.com/yohhoy/status/1171677701498781696)