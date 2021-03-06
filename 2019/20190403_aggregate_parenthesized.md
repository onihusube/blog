# ［C++］丸かっこによる集成体初期化

※この記事は[C++20を相談しながら調べる会 #1](https://cpp20survey.connpass.com/event/124051/)の成果です。

※内容はC++20正式策定までに変化する可能性があります。

[:contents]

集成体初期化（Aggregate Initilization）とは、配列か集成体（Aggregate）となる条件を満たしたクラスに対して行える特別な初期化方法の事です。

C++17まではこれは波かっこ"{}"の時にのみ使用することができ、丸かっこ"()"による初期化は常にその型のコンストラクタを呼び出していました。  
しかし、C++20からはその制限がなくなり丸かっこによる初期化時にも集成体初期化が考慮され、必要なら行われるようになります。

```cpp
struct aggregate {
  int a;
  double b = -1.0;
};

aggregate a{10, 3.14};  //ok
aggregate b(10, 3.14);  //ok

aggregate c = {20, 2.72};  //ok
aggregate d = (20, 2.72);  //ng

aggregate e(30);  //ok e.a == 30, e.b == -1.0

aggregate f();  //ng これは関数宣言となる

int arr1[]{0, 1, 2, 3};  //ok
int arr2[](0, 1, 2, 3);  //ok

int arr3[] = {0, 1, 2, 3};  //ok
int arr4[] = (0, 1, 2, 3);  //ng

int arr5[4](0, 1) //ok 残りの要素は0で初期化

int arr6[4]();  //ng 必ず1つ以上の初期化子が必要
```

波かっこの時と同じように、初期化子の数が足りないときはデフォルトメンバ初期化で初期化され、それもない場合は値初期化（デフォルトコンストラクタを呼び出すような初期化）されます。  
逆に、初期化子の数が多すぎる場合はコンパイルエラーになります。これも波かっこと同じです。

ただし、丸かっこによる初期化を行う場合はその内部の要素（初期化子）の数は1つ以上なければなりません。そうしないと関数宣言と区別がつかないためです。  
（[@yohhoyさんご指摘ありがとうございました！](https://twitter.com/yohhoy/status/1114529110506651648)）

丸かっこによる集成体初期化はなるべく波かっこによるものと同じように実行されます。一方で、今までの丸かっこによる初期化の持つ意味が変わらないようにもなっています。  
そのため、波かっこによる集成体初期化と少し異なる挙動をするところがあります。

### コンストラクタとの競合

集成体初期化と従来のコンストラクタ呼び出しが競合する場合はコンストラクタ呼び出しが優先されます。これは波かっこでも同様ですが、集成体はコンストラクタ宣言を行えないので問題となるのはコピー・ムーブコンストラクタとの競合時です。  
そして、この時の挙動が少し異なっています。

```cpp
struct A;

struct C { 
  operator A();  //実装略
};

struct A {
  C c;
};

C c{};  //cを値初期化

{
  A a(c);  //C::operator A()を呼び、その戻り値からaをムーブ（コピー）構築
  A b(a);  //bをaからコピー初期化
}

{
  A a{c};  //A::cをcからコピー初期化
  A b{a};  //bをaからコピー初期化
}
```

丸かっこによる初期化においては、あらゆる変換が考慮された（通常のオーバーロード解決を行った）うえで、マッチングするコンストラクタが見つからないときに集成体初期化が行われます。

波かっこによる初期化においては、渡された初期化子リストの要素が一つであり、その要素が初期化しようとしている型`T`もしくはその派生型である場合にのみ、その要素から`T`をコピー・ムーブ初期化します。  
それ以外の場合はすべて集成体初期化が行われます。

このように微妙ではありますが初期化方法が選択されるまでの手順が異なります。とはいえ、ただ1つの要素で初期化しようとしたときにのみ起こる事なのであまり出会わないでしょう。

これは、丸かっこによる初期化の持つ意味を変更しないようにしているために生じています。  
配列は元々丸かっこ初期化を持っておらず挙動が曖昧にはならないため、配列の初期化時はこの問題は起きません。

### 縮小変換の許可 

縮小変換とは変換後の型が変換前の型の表現を受け止めきれないような型の変換です（double -> float, signed -> unsigned 等）。  
波かっこによる初期化時は集成体初期化でなくても、縮小変換が禁止されていました。それは思わぬところで変換エラーを引き起こし、特にテンプレート関数の中では波かっこ初期化は非常に使いづらくなってしまっていました。

```cpp
template<typename T>
float to_float(T v) {
  return float{v};
  //こうするとok
  //return float(v);
}

auto d = to_float(3.14);  //compile error!
auto e = to_float(3.14f); //ok.


constexpr char str[50]{};
constexpr auto begin = std::begin(str);

if (auto [end, err] = std::to_chars(begin, std::end(str), 3.141592653589793); err == std::errc{}) {
  std::cout << std::string_view{begin, end - begin};  //compile error!
  //こう書くとok
  //std::cout << std::string_view(begin, end - begin);
}

```
これらのエラーは波かっこ初期化時には縮小変換が禁止されていることから発生しています。  
しかし、丸かっこによる集成体初期化においてはそのような制限はなく、あらゆる変換が考慮され実行されます。

これは同じ丸かっこによる初期化において、コンストラクタ呼び出しと集成体初期化とで挙動が異なることがないようにするためにこうなっています。

### 初期化子を指定しない要素の初期化
集成体初期化においては、どちらのかっこを使ったとしてもすべての要素に対して初期化子を提供する必要はありません。初期化子の無い要素はデフォルトコンストラクタで初期化したように初期化されます。

```cpp
struct aggregate {
  int a;
  double b = -1.0;
  char c;
};

//どちらも、array = {1, 2, 4, 0, 0}と初期化
int array1[5]{ 1, 2, 4 };
int array2[5]( 1, 2, 4 );

//どちらも、::a = 10, ::b = -1.0, ::c = 0 と初期化
aggregate agg1{10};
aggregate agg2(10);
```

しかし、実は丸かっこと波かっこでは初期化子の無い要素の初期化方法が異なります。


なぜこのような差異が生じているかというと、どちらのかっこを使った初期化においても、内部の要素を再帰的に同様の方法で初期化するためです。

元々集成体初期化は波かっこでしかできなかったので、波かっこによる初期化時は内部要素



### ネストするかっこの省略（できない！）
ネストする波かっこ省略について → [宣言時のメンバ初期化を持つ型の集成体初期化を許可 - cpprefjp](https://cpprefjp.github.io/lang/cpp14/brace_elision_in_array_temporary_initialization.html)

波かっこ初期化時はネストしている内部の型に対する波かっこ初期化時に、一番外側以外の波かっこを省略できます。しかし、丸かっこではできません・・・。  
また、ネストする初期化のために丸かっこを使うと意図しない結果になります。何故かというと、ネストする丸かっこにはすでに意味があるからです。

```cpp
//この二つは同じ意味
int arr1[2][2]{{1, 2}, {3, 4}}; //ok
int arr2[2][2]{1, 2, 3, 4};     //ok

//丸かっこはこうするしかない
int arr3[2][2]({1, 2}, {3, 4}); //ok

//できない・・・
int arr4[2][2](1, 2, 3, 4);   　//ng
int arr5[2][2]((1, 2), (3, 4)); //ng (2, 4)と書いたのと同じになるがどのみちできない
```
おそらく3次元以上の配列の場合は丸かっこ内の波かっこのさらに内側では波かっこを省略できます。そんな配列初期化は普通しないと思うのであまり意味は無いですが・・・

そして、丸かっこ初期化の内側でさらに丸かっこを使う場合は、通常のかっこに囲まれた式として処理されてしまい、内側のカンマはカンマ演算子として解釈されます。

クラス型の集成体の場合
```cpp
//この二つは同じ意味
std::array<int, 3> arr1{{ 1, 2, 3 }}; //ok
std::array<int, 3> arr2{ 1, 2, 3 };   //ok

//丸かっこはこうするしかない
std::array<int, 3> arr3({ 1, 2, 3 }); //ok

//できない・・・
std::array<int, 3> arr4( 1, 2, 3 );   //ng
std::array<int, 3> arr4(( 1, 2, 3 )); //ng arr4(3)と同じ、どのみちできない
```

丸かっこ初期化の内側に丸かっこを使えないのはおそらくどうしようもないですが、波かっこ省略はそのうち可能になるような気はします。

### 一時オブジェクトの寿命延長（されない！）

丸かっこによる集成体初期化時は、渡された初期化子リスト内の一時オブジェクトの寿命が延長されません。ドラフト規格文書より、以下のコードをご覧ください。

```cpp
struct A {
  int a;
  int&& r;
};

int f() { 
  return -1;
}

int n = 10;

A a1{1, f()};                   // OK, lifetime is extended
A a2(1, f());                   // well-formed, but dangling reference
A a3{1.0, 1};                   // error: narrowing conversion
A a4(1.0, 1);                   // well-formed, but dangling reference
A a5(1.0, std::move(n));        // OK
```

縮小変換（narrowing conversion）によるエラーはここでは関係なく、`a2, a4`の初期化後の右辺値参照メンバの状態が問題です。

波かっこによる集成体初期化においては渡された一時オブジェクト（`f()`の戻り値やリテラル`1`）が右辺値参照メンバ`A::r`を初期化すると、その一時オブジェクトの寿命は参照`A::r`の寿命と同じになります（延長される）。

しかし丸かっこによる集成体初期化時はそうはなりません。その初期化式が終了すると、そのような一時オブジェクトはそこで死にます（寿命が尽きる）。  
すなわち、そのように初期化された右辺値参照メンバは不正な参照となってしまい、これへのアクセスは未定義動作となります。

`a5`の初期化にあるように、すでに初期化済みの変数でこういう事をしたい場合にはきちんと`move`することでこの罠を回避することができます（ただし、リテラルや関数の戻り値は`move`しても回避できない）。

右辺値参照メンバなんてものはそうそう使うことはないでしょうが、これがconst 左辺値参照メンバならばたまに使う事があるでしょう。その際も同じ罠が待ち構えていることになるので注意せねばなりません・・・

#### 少し詳細な考察

サンプルコードのコメントにもある通り、右辺値参照メンバ`A::r`を`f()`の戻り値やリテラル`1`という`prvalue`で初期化するときに問題が起きています。

まず、`prvalue`を右辺値参照（もしくはconst左辺値参照）に束縛する（結びつける）と`xvalue`な一時オブジェクトに変換されたうえで、結びつけられます。

波かっこ初期化ではそのような一時オブジェクトは集成体要素の右辺値参照（`A::r`）に直接結び付ける（形になる）ため、その一時オブジェクトの寿命は結びつけた参照の寿命まで延長されます。

しかし、丸かっこによる集成体初期化ではそのような一時オブジェクトの寿命の延長がなく、その一時オブジェクトが生成された後の最初のセミコロンまでしか延長されません（明確に規定されています）。  
そのため、初期化の完了後に一時オブジェクトの寿命は尽きることになり、メンバの参照は不正な参照となります。

一方`lvalue`（`n`）を`move`した後の値（`xvalue`）は一時オブジェクトではないので、先ほどの規則には当てはまらず、右辺値参照（const左辺値参照）に束縛すればその参照の寿命まで寿命延長されます。

なぜこのような謎な仕様になっているかははっきりとしませんが、従来の丸かっこによるコンストラクタ呼び出しとの一貫性を確保するためだと思われます。  
コンストラクタでメンバの右辺値参照を初期化するときは、一時オブジェクト等はコンストラクタ引数の右辺値参照でいったん受けてから、メンバ初期化子リストで`move`することになります。

```cpp
struct A {
  A(int&& arg)
    : r(std::move(arg))
  {}

  int&& r;
};


int n = 10;

//共にA::rが不正な参照になることはない
A a(1);
A b(std::move(n));
```

これであれば、2回寿命延長が入ることで結果的にその参照の寿命まで一時オブジェクトの寿命は延長されることになります。

丸かっこによる集成体初期化時もこの様な挙動を前提にしており、一旦コンストラクタ引数で受けてから各メンバの初期化を行うような挙動をとります（実際にそのように行われる訳ではありません）。その際、`move`するかしないかを引数型から推測することには問題があるため、メンバ初期化リストでの`move`は行われず、2度目の寿命延長が発生しません。  
その結果初期化終了後に一時オブジェクトの寿命が尽きることになるのだと思われます。

### Designated Initialization（できない！！）
Designated Initializationについて → [Designated Initialization @ C++ - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20170820/p1)

Designated Initialization（指示付初期化）は同じくC++20より可能になる集成体初期化の新しい形です。  
その名の通り、集成体要素を直接指定する形で初期化を行います。

```cpp
struct aggregate {
  int a = -10;
  double b;
};

aggregate a = {.a = 10, .b = 3.14};

union U {
  char c;
  float f;
};

U u = {.f = 2.72};
```
この様に、どの変数をどの初期化子で初期化しているのかが見やすくなり、特に共用体においては最初に初期化するアクティブメンバを選択できるようになります。

しかし、残念なことに、このDesignated Initializationは波かっこによる集成体初期化時にしか使えません。丸かっこでは、できません・・・・

```cpp
//共にコンパイルエラー！！
aggregate a(.a = 10, .b = 3.14);
U u(.f = 2.72);
```
### 引数の評価順序

丸かっこによる集成体初期化時、渡された初期化子リスト内の要素の評価順序は左から右と規定されます。  
これは波かっこと異なる動作ではなく同じ動作で、むしろ今までの丸かっこによるコンストラクタ呼び出しと異なる動作です。

詳細には、集成体（クラス、配列）の`n`個の要素を先頭（基底クラス→メンバの順）から`1 <= i < j <= n`となるように添え字付けしたとして、`i`番目の要素の初期化に関連するすべての値の計算（value computation）及び副作用（side effect）は、`j`番目の要素の初期化の開始前に位置づけられる（sequenced before）、ように規定されます。

つまり、かっこの種類にかかわらず集成体初期化を行う場合は、初期化子に与えた式の順序に依存するようなコードを書いても未規定状態にならず意図したとおりの結果を得ることができます。

```cpp
{
  int i{};

  int array[]{++i, ++i, ++i, ++i};
  //array = {0, 1, 2, 3}
}

{
  int i{};

  int array[](++i, ++i, ++i, ++i);
  //array = {0, 1, 2, 3}
}

//集成体でない
struct int_4 {
  int_4(int a, int b, int c, int d)
    : a1{a}, a2{b}, a3{c}, a4{d}
    {}

  int a1, a2, a3, a4;
};

{
  int i{};

  int_4 m{++i, ++i, ++i, ++i};
  //m = {0, 1, 2, 3}
}

{
  int i{};

  //unspecified behavior, a1~a4にどの値が入るか（++iがどの順で実行されるか）は未規定
  int_4 m(++i, ++i, ++i, ++i);
}

//集成体
struct agg_int_4 {
  int a1, a2, a3, a4;
};

{
  int i{};

  agg_int_4 m(++i, ++i, ++i, ++i);
  //m = {0, 1, 2, 3}
}
```
（[@yohhoyさんご指摘ありがとうございました！](https://twitter.com/yohhoy/status/1114541900768243712)）

この様に、丸かっこによる初期化時にコンストラクタを呼び出したときは相変わらず未規定の動作となってしまう点は注意です。

### この変更の目的

この様になんだか複雑さを増した上に影響範囲がでかそうな変更をなぜ行ったのかというと、STLにおける`make_~`系や`emplace`系の関数に代表される、内部で要素を構築するような関数において、集成体初期化が行われないことをどうにかするためです。

例えば`std::make_from_tuple`関数の実装例を見てみると
```cpp
template<class T, class Tuple, std::size_t... Index>
constexpr T make_from_tuple_impl(Tuple&& t, std::index_sequence<Index...>){
  //ここで、Tのコンストラクタを呼びだしている
  return T(std::get<Index>(std::forward<Tuple>(t))...);
}

template <class T, class Tuple>
constexpr T make_from_tuple(Tuple&& t) {
  return make_from_tuple_impl(std::forward<Tuple>(t), std::make_index_sequence<std::tuple_size_v<std::decay_t<Tuple>>>{});
}
```
`make_from_tuple_impl`内で`T`を"()"で初期化することでコンストラクタを呼び出しています。"{}"ではないので集成体初期化が行われることはありません。  
これは、与えられた引数（この場合は`t`に含まれる要素）が空か、`T`かその派生型のただ一つだけ、で無ければ集成体は構築できないことを意味しています。  
じゃあここを"{}"にすればいいじゃん？と思うかもしれませんが、上で述べた縮小変換が禁止されていることによって多くのケースで謎のエラーが発生することになるのでそれは解決にならないのです。

また、もう一つのケースとして集成体を要素とするコンテナを扱う時にも同じ問題が起こります。
```cpp
//集成体
struct aggregate {
  int n;
  double d;
  char c[5];
};

int main() {
  std::vactor<aggregate> vec{};

  vec.emplace_back(10, 1.0, "abc");   //compile error!
  vec.emplace_back(aggregate{10, 1.0, "abc"});  //ok
}
```
`emplace_back`は要素型のコンストラクタ引数を受け取って、内部で直接構築する関数です。その際、呼び出すのは丸かっこによるコンストラクタであり、集成体初期化を行いません。

結果、1つ目の`emplace_back`はコンパイルエラーとなります。しかもこのエラーはSTL内部で発生することになるので、一見すると意味の分からないものになってしまいます。

例：clang 8.0.0のエラー例
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/rQ4LS7kiOUIZnHWG)
```
/opt/wandbox/clang-8.0.0/include/c++/v1/memory:1826:31: error: no matching constructor for initialization of 'aggregate'
            ::new((void*)__p) _Up(_VSTD::forward<_Args>(__args)...);
                              ^   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
/opt/wandbox/clang-8.0.0/include/c++/v1/memory:1718:18: note: in instantiation of function template specialization 'std::__1::allocator<aggregate>::construct<aggregate, int, double, char const (&)[4]>' requested here
            {__a.construct(__p, _VSTD::forward<_Args>(__args)...);}
                 ^
```

このエラーをよく見ると、placement newによる要素構築時に丸かっこを用いている事が分かるでしょう。

これらのケースだけでなく、他のSTLコンテナや`std::optional`等Vocabulary typesにも`emplace`系関数があり、`std::pair`のpiecewise constructなど他の直接構築系の操作においても同様の問題が発生しており、この解決のために丸かっこによる集成体初期化が許可されました。

この変更によってこれらの関数は集成体を問題なく内部で構築できるようになり、丸かっこと波かっこの間の初期化に関するセマンティクスの一貫性が少し改善されることになります（むしろ悪化・・・？）。

### 参考文献
- [P0960R3 : Allow initializing aggregates from a parenthesized list of values](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0960r3.html)
- [N4462 : LWG 2089, Towards more perfect forwarding](http://open-std.org/JTC1/SC22/WG21/docs/papers/2015/n4462.html)
- [［C++］集成体の要件とその変遷 -  地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/02/22/201044)
- [コピー初期化 - cppreference.com](https://ja.cppreference.com/w/cpp/language/copy_initialization)
- [XOR swap今昔物語: sequence pointからsequenced-beforeへの変遷 - Qita](https://qiita.com/yohhoy/items/ab15739c99d3f8872407)
- [値カテゴリ - cppreference.com](https://ja.cppreference.com/w/cpp/language/value_category)
- [一時具体化（Temporary materialization conversion） - cppreference.com](https://ja.cppreference.com/w/cpp/language/implicit_conversion#Temporary_materialization)
- [std::make_from_tuple - cpprefjp](https://cpprefjp.github.io/reference/tuple/make_from_tuple.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190403_aggregate_parenthesized.md
)