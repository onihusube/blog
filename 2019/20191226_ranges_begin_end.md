# ［C++］ std::rangesの範囲アクセス関数（オブジェクト）の使いみち

C++20のRangeライブラリ導入に伴って、`std::ranges`名前空間の下に`begin,end,size,data`等の、これまでコンテナアクセスに用いられていた関数が追加されています。しかし、これらの関数はすでに`std`名前空間に存在しており、一見すると同じ役割を持つものが重複して存在しているようにも見えてしまいます。

### 従来の`std::begin()/std::end()`の問題点

元々、範囲を表すイテレータのペアを取り出す口としての`begin()/end()`は各コンテナのメンバ関数として定義されていました。しかしその場合、メンバ関数を持つことのできない生の配列型だけは特別扱いする必要があり、イテレータのペアを取り出す操作が完全に共通化できていませんでした。

C++11にて、`std::begin()/std::end()`が追加され、この関数を利用することで配列とコンテナの間で共通の操作によってイテレータのペアを取り出せるようになりました。  
しかし、標準ライブラリ外の`begin()/end()`をメンバではなくグローバル関数として定義しているようなユーザー定義の型に対してはこれに加えて以下のような一手間を加えなければなりません。

```cpp
//イテレータのペアを取り出す
template<typename Iterable>
auto get_range(Iterable& range_obj) {
  using std::begin;
  using std::end;

  return std::make_pair(begin(range_obj), end(range_obj));
}
```

`std::begin()/std::end()`をそれぞれ`using`した上で`begin()/end()`するのです。これによってメンバではなく同じ名前空間に`begin()/end()`を用意しているユーザー定義型の場合はADLによってそれを発見し、それ以外の型は`std::begin()/std::end()`を経由してメンバのものを呼び出すか配列として処理されます。

C++17まではイテレータ範囲をジェネリックに得るにはこうする事がベストでした（はずです）。


### `std::ranges::begin/std::ranges::end`

しかし、先ほどのコードは正直言って意味わからないし面倒です。C++ヲタクにしかその意味は分からないし、ああいう風に書くという発想は出てきません。一々あんなまどろっこしい書き方も支度なでいす。

そこで、Rangeライブラリでは独自に`begin()/end()`を備えておくことにしました。それが、[`std::ranges::begin`](http://eel.is/c++draft/range.access.begin)/[`std::ranges::end`](http://eel.is/c++draft/range.access.end)の関数（オブジェクト）です。その効果はおおよそ以下のようになります。

- 配列ならその先頭（終端）のポインタを返す
- そうではなく、メンバ関数の`begin()/end()`があればその結果を返す
- そうでもなく、グローバルな`begin()/end()`が利用可能ならばその結果を返す
- そうでもなければ*ill-formed*

つまり先ほどのコードでやっていたような事を全て中でやってくれるすごいやつです。

そして、この`std::ranges::begin/std::ranges::end`によってイテレータペアを取得可能な型こそがRangeライブラリの基本要件である`std::ranges::range`コンセプトを満足する事ができます。

C++20からは先ほどのコードは以下のように書けるでしょう。

```cpp
//イテレータのペアを取り出す
template<std::ranges::range Iterable>
auto get_range(Iterable& range_obj) {
  return std::make_pair(std::ranges::begin(range_obj), std::ranges::end(range_obj));
}
```

### `std::ranges::swap`

`begin()/end()`と全く同じ問題を抱えているのが`swap()`関数です。`std::swap()`は通常ムーブコンストラクタとムーブ代入演算子を用いて典型的なswap操作を行います。標準ライブラリの型はメンバ関数に`swao()`を持っており、`std::swap()`の特殊化を定義してそれを使ってもらっています。

ユーザー定義型で特殊なswapを行いたい場合は、非メンバ関数として`swap()`を定義しておきます（この時、メンバ関数として定義した`swap()`を非メンバ関数の`swap()`から使うようにしてもokです）。そして、使用するにあたってはさっき見たようなコードを書きます。

```cpp
template<typename T, typename U>
void my_swap(T&& t, U&& u) {
  using std::swap;

  swap(std::forward<T>(t), std::forward<U>(u));
}
```

これの問題点は上で説明した通りです。

対して、[`std::ranges::swap`](http://eel.is/c++draft/range.prim.size)関数（オブジェクト）は以下のような効果を持ちます。

- 引数`E1, E2`がクラス・列挙型でフリー関数の`swap(E1, E2)`が利用可能ならそれを利用
- そうではなく、引数`E1, E2`が配列型で`std::ranges::swap(*E1, *E2)`が有効なら、`std::ranges::swap_ranges(E1, E2)`
- そうでもなく、引数`E1, E2`が同じ型`T`の左辺値で`std::move_­constructible<T>`、`std::assignable_­from<T&, T>`両コンセプトのモデルである場合、デフォルトの`std::swap()`相当の式によってswapする。
- そうでもなければ*ill-formed*

ユーザー定義`swap()`関数は1つ目の条件によって発見されます。`using std::swap`をする必要はありません。もっと言えば、`swap`を汎用的に行うためにさっきの`my_swap()`のような関数を書くは必要ありません、この`std::ranges::swap`を使えばいいのです。

ちなみに、この`std::ranges::swap`はなぜか`<range>`ヘッダではなく`<concepts>`ヘッダにあります。多分`std::swappable`コンセプト定義の関係だと思いますが、少し見つけるのに苦労しました・・・。

### `std::ranges::size`

これも先ほどまでと似たようなものです。標準ライブラリにあるコンテナはほとんど現在抱えている要素数を`size()`メンバ関数で取得できます。しかし、生配列は当然そうではなく、`std::forward_list`はそのサイズを最小化するために`size()`を持ちません。また、`begin()/end()`の時と同じくメンバ関数ではなくフリー関数で定義している場合もあるかもしれません。

C++17までは、フリー関数の`std::size()`を使えば`std::forward_list`以外の標準のコンテナからは要素数を取得できました。追加で`std::forward_list`から取得するにはイテレータを取り出して`std::distance()`する特殊処理を自分で書く必要がありました。

そこでRangeライブラリの登場です。[`std::ranges::size`](http://eel.is/c++draft/range.prim.size)関数（オブジェクト）は以下のような効果を持ちます。

- 配列型ならその要素数
- そうではなく、メンバ関数の`size()`があればその結果を返す
- そうでもなく、グローバルな`size()`が利用可能ならばその結果を返す
- そうでもなく、`std::ranges::end(E) - std::ranges::begin(E)`が有効ならばその結果を返す（`E`は`ranges::size`の引数）
- そうでもなければ*ill-formed*

`std::forward_list`だけではなく、フリー関数として定義されている場合のフォローもしてくれています。

### `std::ranges::empty`

これも似たようなものです。標準ライブラリのコンテナは多分全て`empty()`メンバ関数を備えていますが、生配列と`initilizer_list`はそうではありませんでした。

[`std::ranges::empty`](http://eel.is/c++draft/range.prim.size)関数（オブジェクト）は以下のような効果を持ちます。

- メンバ関数の`empty()`があればその結果を返す
- そうではなく、`std::ranges::size(E) == 0`が有効ならその結果を返す
- そうでもなく、`bool(std::ranges::begin(E) == std::ranges::end(E))`が有効ならその結果を返す
- そうでもなければ*ill-formed*

すごく頑張ってくれているのが伝わります。正直、2番目に引っかからずに3番目が有効というケースが思いつきません・・・

### `std::ranges::data`

標準ライブラリで`data()`メンバ関数を持つのはその領域にメモリ連続性があるコンテナだけです（イテレータが*contiguous iterator*であるということでもあります）。そして、その戻り値はそのような領域へのポインタです。

対して、[`std::ranges::data`](http://eel.is/c++draft/range.prim.data)関数（オブジェクト）は以下のような効果を持ちます。

- 引数`E`が左辺値であり、メンバ関数の`data()`が使用可能ならその結果を返す
- そうではなく、`std::ranges::begin(E)`が有効でありその戻り値型が`std::contiguous_iterator`コンセプトのモデルである場合は、`std::to_address(std::ranges::begin(E))`
- そうでもなければ*ill-formed*

基本的には`data()`を利用できる型にその抱える要素列がメモリ連続性を満たしていることを要求する点は変わりませんが、謎の頑張りによってその対象を広げています。

`std::to_address()`はポインタもしくはポインタとみなせる型（スマートポインタ等、ファンシーポインタと呼ぶらしい）のオブジェクトからアドレスを取得するものです。  
`std::contiguous_iterator`コンセプトは*random access iterator*でありメモリ連続性を持つイテレータが満たす事の出来るコンセプトです。

おそらく、`std::ranges::begin()`でその内部のメモリ領域へのファンシーポインタを返すような型を意識しているのだと思います。ユーザー定義型ならばもしかしたらこれが有効なケースがあるかもしれません。標準ライブラリには無いはず（もしかしたらRangeライブラリにはこのような事を行う何かが潜んでいるのかもしれません）・・・


### 結論

このように、これらの範囲アクセス関数（オブジェクト）は今まで用意されていた同名の関数と比べて、さらにもう少し頑張ってその目的を達成しようとするものです。そして、その目的を達するために非自明な追加の操作を要求しません。  
またこれらはカスタマイゼーションポイントオブジェクトと呼ばれる関数オブジェクトであって関数ではありません。そのため、その呼び出しに際して効果を発揮する際に要求するコンセプトのチェックが確実に行われます（ユーザーが巧妙に迂回することができない）。

C++20からは従来の関数のことは忘れて`std::ranges`名前空間の下にあるこれらの関数（オブジェクト）を使いましょう。

### 参考文献
- [24.3 Range access [range.access]](http://eel.is/c++draft/range.access)
- [18.4.9 Concept swappable[concept.swappable]](http://eel.is/c++draft/concept.swappable#2)
- [Customization Point Object - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20190403/p1)
- [C++標準化委員会の文書集、2015-04 pre-Lenexa mailingsのレビュー: N4381-N4389 - 本の虫](https://cpplover.blogspot.com/2015/05/c2015-04-pre-lenexa-mailings-n4381-n4389.html)
- [［C++］expression-equivalentのお気持ち - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/09/12/002550)