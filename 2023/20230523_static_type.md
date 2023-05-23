# ［C++］ 式のstatic type

式の静的型（*static type*）は参照型にならない、すなわち、式の静的型は値カテゴリの情報を含まない、あるいは、式の静的型と式の値カテゴリは直行する概念である、ということに関するメモです。

以下、規格書の文面はC++20規格と同等のドラフトであるN4861を参照します。

なお、この記事はC++の規格書を読む場合にたまーに問題になることがある概念についてのものであって、通常のC++プログラミングで気にする必要は全くありません。普通式の型と言ったら、値カテゴリの情報も含んだ型です（つまり参照型になりうる）。

[:contents]

### *static type*と*value category*

*static type*とは[[defns.static.type]](https://timsong-cpp.github.io/cppwp/n4861/intro.defs#defns.static.type)で次のように定義されています

> type of an expression ([basic.types]) resulting from analysis of the program without considering execution semantics

> 実行時意味論を考慮しないでプログラムを解析した結果得られる、式の型

「実行時意味論を考慮しないでプログラムを解析した結果得られる」とはおおよそ、C++の規則に従ってコンパイルしていく過程で得られる、という意味です。*static type*とはその字面の通り、コンパイル時に定まっている型のことだと思って構いません。対になる概念として*dynamic type*というものがあり、こちらは式の実行時に定まる式の型として定義されています。

式の型とは[[expr.type]](https://timsong-cpp.github.io/cppwp/n4861/expr.type)で定義されています。特に、その最初の項には次のようにあります

> If an expression initially has the type “reference to T” ([dcl.ref], [dcl.init.ref]), the type is adjusted to T prior to any further analysis. The expression designates the object or function denoted by the reference, and the expression is an lvalue or an xvalue, depending on the expression. 

> 式の最初の型が`T`への参照（`T&`/`T&&`）である場合、以降の解析の前に式の型は`T`に調整される。
> 式は参照によって示されるオブジェクトまたは関数を指定し、式によってlvalueまたはxvalueとなる。

ついでに、次の項には*prvalue*の型に関して次のようにあります

> If a prvalue initially has the type “cv T”, where T is a cv-unqualified non-class, non-array type, the type of the expression is adjusted to T prior to any further analysis.

> prvalueの最初の型が`cv T`となり、`T`がCV修飾されていない非クラス型、非配列型である場合、以降の解析の前に式の型は`T`に調整される

ここで、式（*prvalue*）の最初の型とは、式の種類ごとに個別に式の型として指定されているものです。また、式の値カテゴリの決定に関しても同様に式の種類ごとに指定されています。

### 式の型 ⊥ 式の値カテゴリ

静的型（*static type*）はコンパイル時にわかる式の型のことを言い、式の型は、式の種類によって決まる型から参照を取り除いた型になります。従って、静的型は参照型になることはありません。

cppreferenceの値カテゴリのページにも次のようにあり

> Each C++ expression (an operator with its operands, a literal, a variable name, etc.) is characterized by two independent properties: a type and a value category. Each expression has some non-reference type, and each expression belongs to exactly one of the three primary value categories: prvalue, xvalue, and lvalue.

> C++の各式は型と値カテゴリという二つの独立したプロパティによって特徴付けられる。各式は何らかの非参照型を持ち、3つの主要な値カテゴリ（*prvalue*, *xvalue*, *lvalue*）のどれか1つに属している。

この記述からも、静的型は参照型にならず、静的型と値カテゴリは式の持つ直交した性質であることは間違いないようです。

### 影響

規格書中では静的型（*static type*）という言葉は時々出てきますが、それはほとんどの場合式（あるいはオブジェクト）のコンパイル時に定まる型というふわっとした理解でも困ることはありません。

[N4861中のstatic typeの出現箇所（goole検索による）](https://www.google.com/search?q=%22static+type%22+site:timsong-cpp.github.io/cppwp/n4861&client=safari&ei=vlNsZLTEKsGq-QbPjJ0I&start=0&sa=N&filter=0&ved=2ahUKEwi0m-KG34r_AhVBVd4KHU9GBwE4ChDy0wN6BAgEEAQ&biw=2151&bih=1207&dpr=2)

おそらく唯一その違いを認識する必要があるところは、例外オブジェクトの型を決めるところです。例外オブジェクトの型はそれを送出した`throw`式のオペランド（式）の静的型から決定されますが、ここで静的型を参照していることによって例外オブジェクトの型は決して参照型になりません。以降の例外ハンドラでのマッチングなどはこれを前提にされていて、参照型を考慮していません。そのため、ここだけは式の静的型が参照型ではないことを認識しておく必要があります。他のところでは、おそらく気にしなくても行けてしまう気がします。

### 参考文献

- [N4861 3.28 static type [defns.static.type]](https://timsong-cpp.github.io/cppwp/n4861/intro.defs#defns.static.type)
- [N4861 7.2.2 Type [expr.type]](https://timsong-cpp.github.io/cppwp/n4861/expr#type-1)
- [Value categories - cppreference](https://en.cppreference.com/w/cpp/language/value_category)