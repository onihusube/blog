## test

test
test2
test3


<!--  
以下、少し詳しめの考察。

##### potential results（予想される結果）
ある式がpotentially evaluatedであるとき、その結果として想定される式の集まりをpotential resultsといいます。

- 式がid-expression（他の式を含まない単一の式）ならば、potential resultsはその式のみ
- 配列の添え字演算子の場合は、添え字として指定される式（`a[b+c]`の`b+c`）
- クラスメンバアクセス（`., ->`）の場合は、その左辺の式（`(a+b).c, (a+b)->b`の`a+b`）
- その右辺が定数式となるようなpointer-to-memberアクセス（`.*, ->*`演算子）の場合は、その左辺の式（`(a+b).*c, (a+b)->*b`の`a+b`(`c`が定数式となる場合のみ)）
- 式がかっこで囲まれている場合、その中の式（`(expr)`の`expr`）
- 条件演算子（三項演算子）の場合は、真偽それぞれの結果となる二つの式（`a?b:c;`の`b`と`c`）
- カンマ演算子の場合は、右側の式（`a,b,c`の`c`）
- これらに当てはまらない場合potential resultsは空

これらの式、及びこれらの式に含まれる式のpotential resultsが含まれます。

ある式に上記の定義を再帰的に適用して、最後にたどり着いたid-expressionの集合がpotential resultsであるとも言えます。

また、それらの式に関数呼び出しが含まれる場合、その引数の式はpotential resultsに含まれません。
```cpp
struct S { 
  static const int x = 0; 
};

const int& f(const int &r);

int n = b ? (1, S::x)  // S​::​x is not odr-used here
          : f(S::x);   // S​::​x is odr-used here, so a definition is required
```
この例で、`n`の初期化式のpotential resultsには最初の`S::x`及び`f(S::x)`が含まれますが、`f(S::x)`の引数の式`S::x`は含まれません。

potential resultsに含まれる式は、必ずしもpotentially evaluatedではありません。
##### 変数

potentially evaluatedな式`ex`に含まれている変数`x`は、以下の両方を満たさない場合に（`ex`によって）odr-usedされると言います。
1. `x`に左辺値→右辺値変換を適用すると、non-trivialな特殊メンバ関数を呼び出さない定数式とならない。
2. `x`がオブジェクトならば、`ex`は外側の式`e`のpotential resultsの一つ。
    - そのような`e`はdiscarded-value expressionであるか、左辺値→右辺値変換が適用されている式。


左辺値→右辺値変換（lvalue-to-rvalue conversion）とは以下のように暗黙的に右辺値へのコピーが発生することです。
```cpp
int f(int n) {
  return n;  //引数nは左辺値から右辺値へ変換され、返却される
}

int n = 10;
int&& m = int(n);  //変数nは左辺値から右辺値へ変換され、右辺値参照で束縛される
```

discarded-value expressionとは、ある式の結果を得る過程で実行する必要のある式のことで、potential resultsに含まれますが、最終的にはその式の結果は廃棄される形になります。
- 配列の添え字演算子の場合は、添え字として指定される式（`a[b+c]`の`b+c`）
- クラスメンバアクセス（`., ->`）、pointer-to-memberアクセス（`.*, ->*`演算子）の場合は、その左辺の式（`(a+b).c, (a+b)->b`の`a+b`）
- 条件演算子（三項演算子）の場合は、真偽それぞれの結果となる二つの式（`a?b:c;`の`b`と`c`）
- カンマ演算子の場合は、右側の式（`a,b,c`の`c`）

potential resultsの項のリストと同じ内容になりますが主にこれらの式です。逆に言うと、discarded-value expressionはpotential resultsに含まれる、と言えます。

以上のことを踏まえて考えてみると
1. `x`に左辺値→右辺値変換を適用すると、non-trivialな特殊メンバ関数を呼び出さない定数式とならない。

まず、特殊メンバ関数とはデフォルト・コピー・ムーブコンストラクタ、デストラクタ、コピー・ムーブ代入演算子の事で、non-trivial・trivialとはユーザー定義してるかどうかということです。

non-trivialな特殊メンバ関数を呼び出さない定数式とならない、とはつまり、trivialな特殊メンバ関数を呼び出す定数式とならない、ということです。  
これは主に組み込み型のための要件だと思われます。組み込み型であればその特殊メンバ関数は定義が無くても使用可能です。そして、定数式であればその場で値を確定させられるので定義を見に行く必要もありません。  
逆に、trivialな特殊関数でなければその定義が必要ですし、定数式でないならその変数の実体（定義）を待たねばなりません。

`x`に左辺値→右辺値変換を適用すると、なので実際に適用されている必要があるわけではありません。odr-usedであるかどうか確認するために適用するわけです。

2. `x`がオブジェクトならば、`ex`は外側の式`e`のpotential resultsの一つ。
    - そのような`e`はdiscarded-value expressionであるか、左辺値→右辺値変換が適用されている式。 
-->


