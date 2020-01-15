# ［C++］ 集成体のテンプレート引数推論

### C++17のテンプレートな集成体とテンプレートパラメータ推論

C++17から、クラステンプレートのコンストラクタ引数からそのテンプレート引数を推論出来るようになりました。これによって、クラステンプレートを扱う際にとても便利に書けます。

```cpp
// std::vector<int>
std::vector vec = {1, 2, 3, 4, 5};

// std::pair<int, double>
std::pair p = {1, 1.0};


template<typename T>
struct vec3 {
  T v1, v2, v3;

  vec3(T a, T b, T c) : v1(a), v2(b), v3(c) {}
};

// vec3<double>
vec3 v3 = {1.0, 2.0, 1.0};
```

ところで、この`vec3`のような型は別にコンストラクタをわざわざ書かなくても集成体にしておけば色々楽ができます。しかし、このコンストラクタを消してみると、なにやらコンパイルエラーが起こります。どうやらテンプレート引数の推論ができない様子・・・

```cpp
template<typename T>
struct vec3 {
  T v1, v2, v3;
};

// compile error! no viable constructor or deduction guide for deduction of template arguments of 'vec3'
vec3 v3 = {1.0, 2.0, 1.0};
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/FzEeR36be8FG3NsX)

仕方がないので言われた通りに推論補助を書いておきます。

```cpp
template<typename T>
struct vec3 {
  T v1, v2, v3;
};

template<typename T>
vec3(T, T, T) -> vec3<T>;


// ok、vec3<double>
vec3 v3 = {1.0, 2.0, 1.0};
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/uz30e9hbqOOSDGEx)

集成体にはコンストラクタは無いのでコンストラクタ引数から推論できないのはまあ当たり前かもしれません。そして、推論補助は別にコンストラクタと対応している必要はないので集成体でも使えるのでこれでokなのです。

でも、書かなくていいものは書きたくないですよね・・・。

### C++20からのテンプレートな集成体

C++20より、集成体に対してはその仮想的なコンストラクタを利用してテンプレート引数推論が行われるようになります。つまり、先程のような場合に推論補助を書かなくてもよくなります。神アプデ！

```cpp
template<typename T>
struct vec3 {
  T v1, v2, v3;
};

// ok、vec3<double>
vec3 v3 = { .v1 = 1.0, .v2 = 2.0, .v3 = 1.0};
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/lUAfRrbrM9Ek0gjS)

C++20からの集成体はこの様に指示付初期化が使える上に、普通に`()`でも初期化できるようになります。とても便利になります！

#### 仕様詳細

クラステンプレートのテンプレート引数推論は、初期化子からマッチするコンストラクタを関数テンプレート、推論補助を関数として抽出しオーバーロード解決によってその集合から1つを選び出したうえで、関数テンプレートならそのテンプレートパラメータから、関数ならばその戻り値型からテンプレート引数を補います。  
C++17までは集成体は推論補助が無ければそこに引っかからなかったため何も推定してくれませんでした。

C++20からは、集成体`C`の初期化時の引数リスト`(x1, ..., xi)`について、対応する`C`の要素`ei`が過不足なくぴったりと存在している場合に、`C`の要素`ei`の宣言されている型`Ti`によって`C(T1, ..., Ti)`という仮想的なコンストラクタを候補として先程の集合に入れます。その後の手順は先程と同様です。

その際、`C`のメンバとなっている入れ子の集成体は`{}`省略されていてもされていなくても問題ありません。ただし、非集成体のクラスは当然として、`C`のテンプレートパラメータに依存する集成体が入れ子になっている場合に`{}`を省略してしまうと初期化子の数と要素数が合わずコンパイルエラーとなります。  

集成体内部の集成体はその要素が一番外側の集成体まで展開された形で初期化することができます。ただ推定時に限っては、そのような集成体がテンプレートでありそのパラメータが確定していない場合は展開されず、一つのクラスとして扱われます。

提案文書（規格書ドラフト）より、サンプルコード。

```cpp
template <typename T>
struct S {
  T x;
  T y;
};

template <typename T>
struct C {
  S<T> s; //テンプレートパラメータTに依存している
  T t;
};

C c1 = {1, 2};        // error
C c2 = {1, 2, 3};     // error、{}省略できない
C c3 = {{1u, 2u}, 3}; // ok, C<int>

template <typename T>
struct D { 
  S<int> s; //テンプレートな集成体だが、型は確定している
  T t; 
};

D d1 = {1, 2};    // error、{}省略するなら初期化子は3つ必要
D d2 = {1, 2, 3}; // ok、{}省略可能
```

この様に、再帰し外側のテンプレートパラメータに依存する集成体でも、初期化子をきちんと書けばそれら全体にわたってマッチする良い感じな型を推論してくれます。

### 参考文献

- [C++17 クラステンプレートのテンプレート引数推論 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/type_deduction_for_class_templates.html)
- [P1816R0 : Wording for class template argument deduction for aggregates](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1816r0.pdf)
- [P1021R4 : Filling holes in Class Template Argument Deduction](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1021r4.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20200110_aggregate_deduce.md)