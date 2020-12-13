# ［C++］ C++20からのiterator_traits事情

これは[C++ Advent Calendar 2020](https://qiita.com/advent-calendar/2020/cxx)の14日めの記事です。

C++20の`iterator_traits`には、C++17以前のコードに対する互換レイヤとしての複雑な役割が与えられるようになります。従って、C++20からのイテレータ情報の問い合わせには前回説明したものを利用するようにする必要があります。

結論だけ先に書いておくと

- `iterator_traits`を通すと、イテレータはC++17互換として見える
- `iterator_concept`はC++20イテレータコンセプト準拠を表明している
- `iterator_traits`を特殊化しておくと、イテレータに対する非侵入的なカスタマイゼーションポイントとなる
- C++20イテレータをC++20イテレータとして扱うためには、`iterator_traits`を使用しない

前回も合わせてお読みいただくと理解が深まるかもしれません。

- [［C++］ C++20からのイテレータの素行調査方法](https://onihusube.hatenablog.com/entry/2020/12/11/000123)

目次

[:contents]

以下、特に断りが無ければ`I`はイテレータ型だと思ってください。

### C++20における`iterator_traits`の役割

[前回](https://onihusube.hatenablog.com/entry/2020/12/11/000123)見たように、C++20以降はイテレータ利用にあたっては`iterator_traits`を利用する必要は全く無くなっています。それに伴って`iterator_traits`にはC++20イテレータをC++17互換イテレータとして利用するための互換レイヤとしての役割が新たに与えられています。

どういう事かというと、C++20のイテレータはC++17イテレータから求められることが変化しており、C++20イテレータにはC++17イテレータに対する後方互換性がありません。そのために、C++17のコードからC++20以降のイテレータを利用しようとすると謎のコンパイルエラーが多発する事になるでしょう。  
そんな時でも、`iterator_traits`はC++17以前のコードからは利用されているはずで、イテレータを利用する際は何かしらそれを介しているはずです。そこで、`iterator_traits`でイテレータ互換性のチェックとC++17イテレータへの変換を行う事にしたようです。

### `iterator_traits`によるイテレータカテゴリの取得経路

C++20の`iterator_traits<I>`は大まかには次のように`I`の`iterator_category`を取得しようとします。

1. `I`のメンバ型
      - `iterator_category`は`I::iterator_category`から取得
2. `I`が*C++17入力イテレータ*に準するのであれば、可能な操作から
      - `iterator_category`は`I`が4つの*C++17イテレータコンセプト*のどれに準ずるかによって決定
3. `I`が*C++17出力イテレータ*に準ずるのであれば、そう扱う
      - `iterator_category`は`output_iterator_tag`
4. 上記いずれでも取得できなかった場合、`iterator_traits<I>`は空

この手順内で*C++17入力イテレータ*とか言っているものはコンセプトです。ただし、C++20から使用可能となっている各種イテレータコンセプトではなく、C++17までのイテレータで要求されていたことを構文的に列挙しただけのとても簡易なものです。  
これらのC++17イテレータコンセプトはC++20イテレータコンセプトほど厳密ではなく、同じカテゴリでも要件が異なるため互換性がありません。

結果、2番目の手順で取得される`iterator_category`はC++17基準の判定によって決定されます。

### イテレータコンセプトによるイテレータカテゴリの取得経路

C++20で提供される、[`std::input_iterator`](https://cpprefjp.github.io/reference/iterator/input_iterator.html)をはじめとする各イテレータカテゴリを定義するコンセプトの事をまとめて __イテレータコンセプト__ と呼びます。

`std::output_iterator`を除く5つのイテレータコンセプトは、`ITER_CONCEPT`という操作（説明専用のエイリアステンプレート）によってイテレータカテゴリを取得します。

そして、取得されたカテゴリタグ型がどのカテゴリタグ型から派生しているかを調べて、型`I`がどのイテレータカテゴリを表明しているのかを取得します。たとえば、[`std::random_access_iterator`](https://cpprefjp.github.io/reference/iterator/random_access_iterator.html)ならば、`std::derived_from<ITER_CONCEPT(I), std::random_access_iterator_tag>`のようにチェックします。継承関係もチェックすることで、より強いイテレータも含めて判定でき、将来的なイテレータカテゴリの増加にも備えています。  
もちろんこれだけではなく、`I`が備えているインターフェースがそのカテゴリのイテレータとして適格であるかかもチェックされます。

#### `ITER_CONCEPT(I)`

`ITER_CONCEPT(I)`は次のように`I`からイテレータカテゴリを取得します。

1. `iterator_traits<I>`の明示的特殊化が無い場合（`iterator_traits`のプライマリテンプレートが使用される場合）
   1. `I::iterator_concept`から取得
   2. `I::iterator_category`から取得
   3. `random_access_iterator_tag`を取得
2. `iterator_traits<I>`の明示的特殊化がある場合
   1. `iterator_traits<I>::iterator_concept`から取得
   2. `iterator_traits<I>::iterator_category`から取得
   3. `ITER_CONCEPT(I)`は型名を示さない

1-3による手順はフォールバックです。イテレータカテゴリが取得できない場合はとりあえずランダムアクセスイテレータとして扱っておいて、イテレータコンセプトの他の部分で判定するようにするためのものです。

`iterator_traits`によるカテゴリの取得時と大きく異なるところは、`iterator_concept`があればそれを優先する点にあります。

#### `itereator_concept`と`iterator_category`

`iterator_concept`はC++20からのイテレータカテゴリ表明のためのメンバ型です。やっていることは`iterator_category`と同じです。

これは主にポインタ型の互換性を取るために導入されたもので（C++20からポインタ型のイテレータカテゴリは*contiguous iterator*となる）、それまで使用されていた`iterator_category`を変更しないようにカテゴリを更新しようとするものです。  
それは`iterator_traits`のポインタ型に対する特殊化に見ることができます。

```cpp
namespace std {
  template<class T>
    requires is_object_v<T>
  struct iterator_traits<T*> {
    // C++20からのカテゴリ
    using iterator_concept  = contiguous_iterator_tag;
    // C++17までのカテゴリ
    using iterator_category = random_access_iterator_tag;
  
    using value_type        = remove_cv_t<T>;
    using difference_type   = ptrdiff_t;
    using pointer           = T*;
    using reference         = T&;
  };
}
```

これによって、`I`の`iterator_category`を見ればC++17までのイテレータとしてのカテゴリが、`iterator_concept`を見ればC++20からのイテレータとしてのカテゴリがそれぞれ取得できることになります。

つまりは、C++20イテレータ型に対してそこから`iterator_category`を取得できる場合、そのC++20イテレータをC++17イテレータとして扱うことができる事を意味しています。

また、`iterator_concept`メンバ型を定義するということは、イテレータコンセプト、ひいてはC++20イテレータへの準拠を表明することでもあります。

### `iterator_traits`を通して見るC++20イテレータ

`iterator_traits`を介してイテレータカテゴリを取得する時、そのイテレータの`iterator_category`メンバ型を取得することになります。  
`iterator_category`メンバ型はC++17以前のコードに対する互換性のために、C++17イテレータとしてのカテゴリを表明しています。

もし`iterator_category`メンバ型が無い場合、そのイテレータの可能な操作に基づくC++17の要件によって、適切なイテレータカテゴリが取得されます。

従って、`iterator_traits`を通してC++20イテレータを見てみると、C++17互換イテレータとして見えることになります。

逆に、`iterator_traits`を通してC++17イテレータを見た時はC++17までの振る舞いとほぼ変わりません。C++17イテレータはそのままC++17イテレータとして見えます。

標準のC++20イテレータ型（たとえば、`<ranges>`の各種`view`のイテレータ）には、そのメンバ型として`iterator_concept`と`iterator_category`を両方同時に提供して、`iterator_category`の方を例えば`input_iterator_tag`など弱めることで安全にC++17イテレータとして利用できるようになっているものがあります。

### イテレータコンセプトを通して見るC++17イテレータ

C++17のイテレータをイテレータコンセプトに渡したときは、`ITER_CONCEPT`を通してイテレータカテゴリが`I::iterator_cateogry`から取得され、コンセプトによってそのインターフェースがチェックされます。C++17イテレータとして定義されていて、C++20での要件も満たしている場合は問題なくそのカテゴリのC++20イテレータとして判定されるでしょう。  
多くの場合はC++17イテレータでは各カテゴリにおいての要件がC++20のものよりも厳しいはずなので、正しくC++17イテレータとして定義されていれば問題なくC++20イテレータとなれるはずです。

もちろん、C++17まではそれを判定する仕組みはなかったので思わぬところで要件を満たしていない可能性はあります。その時は、君がイテレータだと思ってるそれ、イテレータじゃないよ？ってコンパイラくんが教えてくれます。親切ですね・・・

逆に、イテレータコンセプトを通してC++20イテレータを見た時、`ITER_CONCEPT`を通して`iterator_concept`が取得され、あるいはなかったとしても、最終的にコンセプトによって定義されたC++20イテレータとしての性質を満たしているかによって判定されます。  
C++20のイテレータをC++20のイテレータとして見ることができるのはこの経路だけです。

まとめると、それぞれからイテレータを見た時にどう見えるかは、次のようになります。

|窓口 ＼ イテレータ|C++17イテレータ|C++20イテレータ|
|:---|:---|:---|
|`iterator_traits`|C++17イテレータ|C++17イテレータ|
|イテレータコンセプト|C++20イテレータ|C++20イテレータ|

こうしてみると古いものからは古いものとして、新しいものからは新しいものとして見える、というなんだか当たり前の話に見えてきます。

### `iterator_traits`の明示的特殊化

ここまであえて深く触れていませんでしたが、`iterator_traits`を使おうとイテレータコンセプトを使おうと、必ず考慮しなればならない経路がもう一つあります。それは`iterator_traits`が`I`について明示的に特殊化されていた場合です。典型的な例はポインタ型です。

その場合、`iterator_traits`にせよ`ITER_CONCEPT`にせよ、特殊化`iterator_traits<I>`を最優先で使用するようになります。

`iterator_traits`を直接使うのはC++17以前のコードがメインだと思われるので、そこに`iterator_concept`メンバが生えていても触られることはないでしょう。

`ITER_CONCEPT(I)`では、`I::iterator_concept`は無視され`iterator_traits<I>::iterator_concept`があればそれを、なければ`iterator_traits<I>::iterator_category`を取得します。

どちらにせよ重要なことは、`iterator_traits`が`I`について明示的に特殊化されている場合は、`I`のメンバや実際の性質は無視して特殊化に定義されているものが取得されるという事です。

これは、元のイテレータ型`I`に対して非侵入的なカスタマイゼーションポイントになっています。最も重要なのはその特殊化に`iterator_concept`メンバがあるかないかで、ある場合は元のイテレータが何であれC++20イテレータコンセプト準拠を表明することになり、ない場合は元のイテレータがC++20イテレータであってもC++17イテレータとして扱われる、ということになります。

特殊化された`iterator_traits<I>::iterator_concept`メンバを触るのは`ITER_CONCEPT(I)`だけですが、この場合であっても`iterator_category`の役割はC++17イテレータとして使用可能なカテゴリを表明する事なのが分かります。

`iterator_traits`はプライマリテンプレートにせよ特殊化にせよC++17コードから利用されるものなので、`iterator_category`を含めた5つのメンバ型は必ず定義しておく必要があります。オプショナルなのは`iterator_concept`のみです。

### `iterator_traits`の2つの役割

結局、C++20`iterator_traits`には大きく次の二つの役割がある事が分かります。

1. プライマリテンプレートが使用される場合、C++17互換レイヤとして機能する。  
  この時、`iterator_concept`メンバは定義されず、`iterator_category`のみがイテレータ型のC++17互換の性質によって定義される。
2. 明示的に特殊化されている場合、イテレータのメンバ型よりも優先されるカスタマイゼーションポイントとして機能する。  
  この時、`iterator_concept`メンバが定義されないならば、`iterator_category`を使用してイテレータ型のC++20的性質を制限する。

### C++20以降のイテレータ情報の問い合わせ、まとめ

（本当は前回の最後に載せるべきでしたが忘れていたのでここに置いておきます・・・）

|情報|C++17 `iterator_traits<I>`|C++20からの窓口|
|:---|:---|:---|
|距離型|`difference_type`|[`std::iter_difference_t<I>`](https://cpprefjp.github.io/reference/iterator/iter_difference_t.html)|
|要素の型|`value_type`|[`std::iter_value_t<I>`](https://cpprefjp.github.io/reference/iterator/iter_value_t.html)|
|要素の参照型|`reference`|[`std::iter_reference_t<I>`](https://cpprefjp.github.io/reference/iterator/iter_reference_t.html)|
|要素のポインタ型|`pointer`|なし|
|イテレータのカテゴリ|`iterator_category`|各種イテレータコンセプト|
|要素の右辺値参照型|なし|[`std::iter_rvalue_reference_t`](https://cpprefjp.github.io/reference/iterator/iter_rvalue_reference_t.html)|
|イテレータの*common reference*|なし|[`std::iter_common_reference_t`](https://cpprefjp.github.io/reference/iterator/iter_common_reference_t.html)|

### 参考文献

- [`<iterator>` - cpprefjp](https://cpprefjp.github.io/reference/iterator.html)
- [`std::iterator_traits` - cpprefjp](https://cpprefjp.github.io/reference/iterator/iterator_traits.html)
- [`std::iterator_traits` - cppreference](https://en.cppreference.com/w/cpp/iterator/iterator_traits)
- [`ITER_CONCEPT` - `input_iterator` - cpprefjp](https://cpprefjp.github.io/reference/iterator/input_iterator.html#iter_concept)
- [P2259R0 Repairing input range adaptors and counted_iterator](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2259r0.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20201214_cpp20_iterator_traits.md)