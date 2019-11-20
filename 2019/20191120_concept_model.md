#  ［C++］コンセプトの文脈におけるmeet、satisfyとmodelの使い分けについて

この3つの言葉はどれも、あるコンセプトもしくは制約を満たすという意味で使われているのですが、同じ意味のように思えますが標準ライブラリ中では明確な使い分けがなされています。

[:contents]

### old conceptに対する*meet*

*meet*が使われるのはC++17までの名前付き要件を使用しているところです。それはC++20からは`Cpp17CopyConstructible`のような名前になっています。

これらの名前付き要件はコンセプトのように構文的にチェックされるわけではなく、満たすべき要件は規格書に記述されており、それを使用する所に入ってくる型は暗黙にそれを満たしているものとして扱います。  
この制約には型が満たすべき静的なものと、実際の値が満たすべき動的なものの2種類が含まれます。

特にイテレータが絡む所での`ForwardIterator`などがお馴染みでしょうか。

この制約を仮に満たさなかった場合、プログラムはill-formdとなりますが必ずしもそれはコンパイルエラーになるとは限りません。ひょっとしたら実行時にすらエラーとはならないかもしれません。未定義動作の世界です。

これは原初のSTL時代からの制約手法でありますが、C+20以降はコンセプトを使用することが望ましく、標準ライブラリからも次第に姿を消していくでしょう・・・


### syntactic conceptに対する*satisfy*

*satisfy*が使われるのはコンセプトを使用している文脈です。  
特に、「*Constraints: T satisfies C*」みたいに使われるようです。これは、（テンプレートパラメータに対する）制約として型TはコンセプトCを満たしていること、のような意味です。

この場合の満たしている（*satisfy*）とは、そのコンセプトによってチェックされる構文的（Syntactic）な制約を満たしていること、という意味です。

構文的な制約はコンセプトによってコンパイル時にチェックされるため、制約を満たさない場合は必ずコンパイルエラーになります。  
このことからもわかるように、構文的な制約にはその型が満たしているべき静的な制約だけが含まれます。


### semantic conceptに対する*model*

*model*が使われるのはコンセプトを定義、使用している文脈の両方です。

コンセプト定義の文脈では、「*T models C only if 条件列*」のように使用されます。これは、条件をすべて満たす場合に限り型TはコンセプトCのモデルである、というような意味です。

ライブラリ中で使用される際は、「*Preconditions: T models C.*」のように使用されます。これは、事前条件として、型TはコンセプトCのモデルであること、というような意味です。

この*model*とは、構文的な制約に加えてそのコンセプトを規定する文書によって指定される意味論的（Semantic）な制約を満たしていること、という意味です。

この意味論的な制約は必ずしもコンパイル時にチェックできるわけではないため、一切チェックされません。仮に満たしていなかったとしてもコンパイルエラーにはならず、もしかしたら実行時にもエラーは出ないかもしれません。  
ただし、標準ライブラリにおいては*model*であることを要求することがあるため、コンセプトを満たす型を定義する場合はそのモデルとなるようにしておくべきです。

このように、意味論的な制約にはその型の値が満たしているべき動的な制約が含まれています。

こうして見ると、C++20からのコンセプトはC++17まで使用していた型及びその値に対する暗黙の要件を構文的なものと意味論的なものに分解したうえで、構文的なものをコンセプトによってコンパイル時にチェックし、意味論的なものはこれまで通り文書で指定し暗黙に要求する、という運用となっていることが分かります。  
そして、型がコンセプトのモデルであるとはその両方を満足しているものの事を指しています。

おそらく、型がコンセプトのモデルとなっているかをチェックするのはContractsの役割だったはずです。順調に行っていればC++23の標準ライブラリはModuleでConceptとContractsなものになっていたのかもしれません・・・


### 実際の利用例

文書で言われてもイメージ付かないので、C++20規格書中の例を見てみましょう。

#### コンセプト定義例

コンセプトの定義例として、[`boolean`](http://eel.is/c++draft/concept.boolean)コンセプトの定義を見てます。

まず最初に目に入るのは`boolean`の定義そのものでしょうか。

```cpp
template<class B>
  concept boolean =
    movable<remove_cvref_t<B>> &&       // (see [concepts.object])
    requires(const remove_reference_t<B>& b1,
             const remove_reference_t<B>& b2, const bool a) {
      { b1 } -> convertible_to<bool>;
      { !b1 } -> convertible_to<bool>;
      { b1 && b2 } -> same_as<bool>;
      { b1 &&  a } -> same_as<bool>;
      {  a && b2 } -> same_as<bool>;
      { b1 || b2 } -> same_as<bool>;
      { b1 ||  a } -> same_as<bool>;
      {  a || b2 } -> same_as<bool>;
      { b1 == b2 } -> convertible_to<bool>;
      { b1 ==  a } -> convertible_to<bool>;
      {  a == b2 } -> convertible_to<bool>;
      { b1 != b2 } -> convertible_to<bool>;
      { b1 !=  a } -> convertible_to<bool>;
      {  a != b2 } -> convertible_to<bool>;
    };
```

意味としては、`movable`コンセプトを満たしており、かつその次の行以降の`requires`式内に書かれている式が使用可能であり、戻り値型がそれぞれの制約を満たすこと、のような意味です。

これが構文的な制約であり、これらの制約は全てコンパイル時にチェックされます。型がこれらの制約を満たさない（*satisfy*でない）場合はコンパイルエラーとなります。

さて、次にその下のだ書に目を向けると次のように書かれています。

>For some type `B`, let `b1` and `b2` be lvalues of type `const remove_­reference_­t<B>`. `B` *models* `boolean` only if
>
>- `bool(b1) == !bool(!b1)`.
>- `(b1 && b2)`, `(b1 && bool(b2))`, and `(bool(b1) && b2)` are all equal to `(bool(b1) && bool(b2))`, and have the same short-circuit evaluation.
>- `(b1 || b2)`, `(b1 || bool(b2))`, and `(bool(b1) || b2)` are all equal to `(bool(b1) || bool(b2))`, and have the same short-circuit evaluation.
>- `bool(b1 == b2)`, `bool(b1 == bool(b2))`, and `bool(bool(b1) == b2)` are all equal to `(bool(b1) == bool(b2))`.
>- `bool(b1 != b2)`, `bool(b1 != bool(b2))`, and `bool(bool(b1) != b2)` are all equal to `(bool(b1) != bool(b2))`.

なんとなく訳せば

>型`B`に対して`const remove_­reference_­t<B>`の左辺値として定義する値`t, u`について、次の条件をすべて満たしている場合に限って型`B`は`boolean`のモデルである
>
>- `(b1 && b2)`, `(b1 && bool(b2))`, `(bool(b1) && b2)`の式は全て `(bool(b1) && bool(b2))`と等値であり、短絡評価されるかどうかも一致する。
>- `(b1 || b2)`, `(b1 || bool(b2))`, `(bool(b1) || b2)`の式は全て `(bool(b1) || bool(b2))`と等値であり、短絡評価されるかどうかも一致する。
>- `bool(b1 == b2)`, `bool(b1 == bool(b2))`, `bool(bool(b1) == b2)` の式は全て `(bool(b1) == bool(b2))`と等値である
>- `bool(b1 != b2)`, `bool(b1 != bool(b2))`, `bool(bool(b1) != b2)` の式は全て `(bool(b1) != bool(b2))`と等値である

これが`boolean`コンセプトのモデルとなる型が満たしているべき意味論的な制約です。このようにコンセプト定義そのものと分けて書かれており、その内容的にも一つ一つチェックするのは困難であることが分かります。

そして最後に例としてこんなことが書かれています。
>The types `bool`, `true_­type` ([meta.type.synop]), and `bitset<N>​::​reference` ([template.bitset]) are `boolean` types. Pointers, smart pointers, and types with only explicit conversions to `bool` are not `boolean` types.

なんとなく訳すと
>`bool, std::true_type, std::bitset<N>​::​reference`は`boolean`型である。しかし、ポインタ、スマートポインタや明示的に`bool`に変換できるだけの型は`boolean`型ではない。

とあります。コンセプト定義に書かれている構文的な制約だけならポインタ等の型でも満たすことはできそうですが、モデルとなるための意味論的な制約は満たすことができないものが含まれています（後ろから2つの条件）。

そして、`boolean`型であると上げられている型を見るとモデルとなる条件を満たしている事が分かるでしょう。  
そういう意味でコンセプトのモデルとはそのコンセプトの構文的な制約を満たす型のうち典型的・理想的な型の事であると言え、意味論的な制約はそのコンセプトを満たすならば自然に要求されることを記述しているものであると言えるでしょう（とはいえ要求事項は割とコーナーケースな気もします）。

#### 制約の利用例

次に標準ライブラリでこれらコンセプト、ないしは制約を利用しているところを見てみましょう。C++20から導入される`format`ライブラリがこれらの３つの例をすべて確認できるためそれを見てみます。

[`std::format_to_n`](http://eel.is/c++draft/format#functions-16)関数は全ての例を含んでいるので見てみます。4つあるオーバーロードのうち1つだけコピペしておきます。

```cpp
template<class Out, class... Args>
  format_to_n_result<Out> format_to_n(Out out, iter_difference_t<Out> n,
                                      string_view fmt, const Args&... args);
```

まず、テンプレートパラメータに対する制約としてこう書かれています。

>Constraints: `Out` *satisfies* `output_­iterator<const charT&>`.

型`Out`は`output_­iterator<const charT&>`コンセプトを満たしていること、という意味ですがこの場合は構文的な制約を満たすことしか要求されていません。  
このConstraintsな制約はコンセプト機構によってコンパイル時にチェックされます。満たしていなければコンパイルエラーになります。

ちなみに、`output_­iterator`コンセプトは2引数を取るコンセプトであり、この場合に正確に書くと`output_­iterator<Out, const charT&>`という構文になります。`requires`式内の戻り値型制約を書くときも同様に第一引数を省略し、その定義文脈から適切な型を第一引数に渡す、というようになっているのでそれに倣っているようです。

次に、事前条件としてこうあります。

>Preconditions: `Out` *models* `output_­iterator<const charT&>`,  
>and `formatter<Ti, charT>` *meets* the *Formatter requirements* ([formatter.requirements]) for each `Ti` in `Args`.

型`Out`は`output_­iterator<const charT&>`のモデルであり、引数型`Args...`内の各型`Ti`は*Formatter*要件を満たしていること、みたいな意味です。  

これによって結局、型`Out`は`output_­iterator<const charT&>`コンセプトの構文的、意味論的な制約の両方を満たしていることが要求されていることが分かります。ただし、意味論的な制約はチェックされず暗黙に満たしているものとして扱われます。満たしていなければ未定義動作です・・・

*Formatter*要件は長いので割愛しますが、デフォルト構築可能とかコピー可能とかスワップ可能とかの構文的な制約と、そのイテレータの値についての意味論的な制約をごっちゃ煮にした制約が文書で指定されています。  
この要件は全て明確にチェックされるものではありません。満たしていなければ未定義動作です。


### 参考文献

- [Library-wide: Use "model" instead of "satisfy" with library concept requirements - cplusplus/draft](https://github.com/cplusplus/draft/pull/2797)
- [P0898R3 Standard Library Concepts (comment) - cplusplus/draft](https://github.com/cplusplus/draft/pull/2176#discussion_r196590990)
- [モデルとは何か? -  北海道大学大学院情報科学研究科 システム環境情報学特論](http://dse.ssi.ist.hokudai.ac.jp/~onosato/lectures/DSE19/H19-Model.pdf)
- [bool型へのexplicitユーザ定義変換 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20121110/p1)

### 謝辞

この記事の9割は以下の方々によるご指摘によって成り立っています。

- [yohhoyさん](https://twitter.com/yohhoy/status/1177578518164561922)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20191120_concept_model.md)