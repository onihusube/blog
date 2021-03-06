# ［C++］ C++17イテレータ <=> C++20イテレータ != 0

これは[C++ Advent Calendar 2020](https://qiita.com/advent-calendar/2020/cxx)の24日めの記事です（大遅刻です、すいません）。

[前回](https://onihusube.hatenablog.com/entry/2020/12/14/002822)と[前々回](https://onihusube.hatenablog.com/entry/2020/12/11/000123)でC++20のイテレータは一味も二味も違うぜ！という事を語ったわけですが、具体的にどう違うのかを見てみようと思います。

[:contents]

以下、特に断りが無ければ`I`はイテレータ型、`i`はイテレータのオブジェクトだと思ってください。

### iterator

イテレータとは何か？という事は、C++20では[`std::input_or_output_iterator`](https://cpprefjp.github.io/reference/iterator/input_or_output_iterator.html)コンセプト、C++17では[*Cpp17Iterator*要件](https://en.cppreference.com/w/cpp/named_req/Iterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

- `iterator_­traits<I>`のインスタンスが存在する
- コピー構築可能
- コピー代入可能
- デストラクト可能
- *lvalue*について、スワップ可能
- `iterator_­traits<I>​::​difference_­type`は符号付き整数型もしくは`void`

これらの～可能というのはそれはそれで一つの名前付き要件になっているのですがここでは深堀しません。おそらく言葉から分かるのとそう異なる意味ではないはずです。

そして、次の式が可能であることが要求されます

|式|戻り値|
|---|---|
|`*i`|未規定|
|`++i`|`I&`|

間接参照と前置インクリメントによる進行が可能であれ、という事です。

#### C++20

C++20は言葉で長々語ったりしません。コンセプトで語ります。

```cpp
template<class I>
concept input_or_output_iterator =
  requires(I i) {
    { *i } -> can-reference;
  } &&
  weakly_incrementable<I>;
```

`can-reference`は戻り値型が`void`ではない事を表すコンセプトです。  
ここで直接見ることの出来るのは間接参照の要求です。これはC++17の要求と同じことを意味しています。

`std::weakly_incrementable`は`++`によってインクリメント可能であることを表すコンセプトです。

```cpp
template<class I>
concept weakly_incrementable =
  default_initializable<I> && movable<I> &&
  requires(I i) {
    typename iter_difference_t<I>;
    requires is-signed-integer-like<iter_difference_t<I>>;
    { ++i } -> same_as<I&>;
    i++;
  };
```

- [`std::weakly_incrementable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/weakly_incrementable.html)
- [`std::is-integer-like` - cpprefjp](https://cpprefjp.github.io/reference/iterator/is_integer_like.html)

コンセプトを深さ優先探索していくとスタックオーバーフローで脳内コンパイラがしぬので適宜cpprefjpを参照してください。

​`requires`式の中では、`difference_­type`が取得可能であることと、前置インクリメントに対しては先ほどのC++17と同じことが要求されています。

大きく異なる点は、デフォルト構築可能であることと、コピー可能ではなくムーブ可能であることです。また、`difference_­type`は`void`が認められない代わりに符号付き整数型と同等な任意の型が許可されており、後置インクリメントが要求されています。

C++20イテレータは`iterator_traits`で使用可能である事を要求されていませんが、C++20の`iterator_traits`はC++17互換窓口としてなんとかして情報をかき集めてきてくれるのでほぼ自動で使用可能となるはずです。また、前々回に説明した`iterator_traits`に代わるイテレータ情報取得手段はイテレータの性質からその情報を取ってくるので`iterator_traits`のようなものはほぼ必要なくなっています。したがって、`iterator_traits`で使用可能かどうかは差異とはみなさないことにします。


#### 差異

結局、C++20イテレータとC++17イテレータの差異は次のようになります。

|要求|C++20|C++17|
|---|---|---|
|デフォルト構築可能性|要求される|不要|
|ムーブ可能性|要求される|要求される|
|コピー可能性|不要|要求される|
|`difference_­type`|符号付整数型 or それと同等な型|符号付整数型 or `void`|
|後置インクリメント|要求される|不要|

コピー可能 -> ムーブ可能ですが、ムーブ可能 -> コピー可能ではありません。`difference_­type`を除いて、C++20のイテレータはC++17から制約が厳しくなっています。

殆どの要件が厳しくなっていることからC++17イテレータでしかないものをC++20イテレータとして扱うことは出来ませんが、`difference_­type`の差異を無視すればC++20イテレータをC++17イテレータとして扱うことは出来そうです。

`is-integer-like`が求めているものは整数型とほぼ同様にふるまうクラス型であり、通常の演算や組み込み整数型との相互の変換が可能である必要があります。すなわちジェネリックなコードにおいては何かケアの必要なく整数型として動作するものなので、この`difference_­type`の差異はほとんど気にする必要は無いでしょう。

### input iteratorr

入力イテレータとは何ぞ？という事は、C++20では[`std::input_iterator`](https://cpprefjp.github.io/reference/iterator/input_iterator.html)コンセプト、C++17では[*Cpp17InputIterator*要件](https://en.cppreference.com/w/cpp/named_req/InputIterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

- *Cpp17Iterator*要件を満たす
- 同値比較可能

そして、次の式が可能であることが要求されます（ここでは*Cpp17Iterator*要件で要求されていたものを上書きする形で含んでいます）

|式|戻り値|
|---|---|
|`i1 != i2`|*contextually convertible to* `bool`|
|`*i`|`referencce`、要素型`T`に変換可能であること|
|`i->m`||
|`++i`|`I&`|
|`(void)i++`||
|`*i++`|要素型`T`に変換可能であること|

`== !=`による同値比較と`->`、後置`++`が使用可能である事が追加されました。

#### C++20

C++20はコンセプトで(ry

```cpp
template<class I>
concept input_iterator =
  input_or_output_iterator<I> &&
  indirectly_readable<I> &&
  requires { typename ITER_CONCEPT(I); } &&
  derived_from<ITER_CONCEPT(I), input_iterator_tag>;
```

`ITER_CONCEPT`については前回の記事をご覧ください。要は`iterator_category`を取得してくるものです。

`std::indirectly_readable`は少し複雑ですが定義そのものは次のようなものです。

```cpp
template<class In>
concept indirectly-readable-impl =
  requires(const In in) {
    typename iter_value_t<In>;
    typename iter_reference_t<In>;
    typename iter_rvalue_reference_t<In>;
    { *in } -> same_as<iter_reference_t<In>>;
    { ranges::iter_move(in) } -> same_as<iter_rvalue_reference_t<In>>;
  } &&
  common_reference_with<iter_reference_t<In>&&, iter_value_t<In>&> &&
  common_reference_with<iter_reference_t<In>&&, iter_rvalue_reference_t<In>&&> &&
  common_reference_with<iter_rvalue_reference_t<In>&&, const iter_value_t<In>&>;
```

- [`std::indirectly_readable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/indirectly_readable.html)
- [`std::iter_rvalue_reference_t` - cpprefjp](https://cpprefjp.github.io/reference/iterator/iter_rvalue_reference_t.html)

`iter_value_t`などが使用可能であると言うことは窓口が違うだけで、`iterator_traits`で取得可能と言う要件と同じ意味です。また、`std::iter_rvalue_reference_t`は`std::ranges::iter_move`を使用して右辺値参照型を取得しており、`std::ranges::iter_move`はカスタマイぜーションポイントとしてC++17イテレータに対しても作用します。したがって、これらは差異とはみなさないことにします。

間接参照の戻り値型に対する要件は同じです。大きく違うのはイテレータの`reference`と`value_type`の間に*common reference*が要求されている事です。また、後置インクリメントに関しては`input_or_output_iterator`から引き継いでいるのみで、C++17イテレータが戻り値型に要求があるのに対してC++20イテレータにはそれがありません。

#### 差異

結局、C++20入力イテレータとC++17入力イテレータの差異は次のようになります（*iterator*での差異を含めています、追加されたものは先頭に+で表示）。

|要求|C++20|C++17|
|---|---|---|
|デフォルト構築可能性|要求される|不要|
|ムーブ可能性|要求される|要求される|
|コピー可能性|不要|要求される|
|`difference_­type`|符号付整数型 or それと同等な型|符号付整数型 or `void`|
|+ `== !=`による同値比較|不要|要求される|
|+ `->`|不要|要求される|
|+ 後置インクリメントの戻り値型|任意（`void`も可）|`value_type`に変換可能な型|
|+ `reference`と`value_type`との*common reference*|要求される|不要|

後置インクリメントができる事、と言う点においては一致した代わりに差異が増えました。C++17 -> C++20で緩和されたものもあれば厳しくなったものもあり、C++20入力イテレータとC++17入力イテレータの間には相互に互換性がありません。

### ouptut iterator

出力イテレータとは一体？という事は、C++20では[`std::output_iterator`](https://cpprefjp.github.io/reference/iterator/output_iterator.html)コンセプト、C++17では[*Cpp17OutputIterator*要件](https://en.cppreference.com/w/cpp/named_req/OutputIterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

- *Cpp17Iterator*要件を満たす

そして、次の式が可能であることが要求されます（ここでは*Cpp17Iterator*要件で要求されていたものを上書きする形で含んでいます）

|式|戻り値|
|---|---|
|`*i = o`|結果は使用されない|
|`++i`|`I&`|
|`i++`|`const I&`に変換可能であること|
|`*i++ = o`|結果は使用されない|

後で関係してくる事として、この`i`は左辺値（`I&`）です。

4つ全ての操作において、それぞれの操作の後でイテレータ`i`が間接参照可能であることは要求されません。

#### C++20

コンセプトによって次のように定義されます。

```cpp
template<class I, class T>
concept output_iterator =
  input_or_output_iterator<I> &&
  indirectly_writable<I, T> &&
  requires(I i, T&& t) {
    *i++ = std::forward<T>(t);
  };
```

ここを見るぶんには違いがなさそうですね。

`std::indirectly_writable`コンセプトは次のように定義されます

```cpp
template<class Out, class T>
concept indirectly_writable = 
  requires(Out&& o, T&& t) {
    *o = std::forward<T>(t);
    *std::forward<Out>(o) = std::forward<T>(t);
    const_cast<const iter_reference_t<Out>&&>(*o) = std::forward<T>(t);
    const_cast<const iter_reference_t<Out>&&>(*std::forward<Out>(o)) = std::forward<T>(t);
  };
```

- [`std::indirectly_writable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/indirectly_writable.html)

`*i`による出力が可能であることが求められているのですが、制約式がやたら複雑です。上2つは左辺値からでも右辺値からでも出力可能である事と言う要件でしょう。C++17までは右辺値イテレータからの出力は要求されていません。  
下二つの`const_cast`をしている制約式は、規格書の言によれば間接参照が*prvalue*を返すようなプロクシイテレータを弾くためにあるらしいです。よくわかんない・・・

また、`std::indirectly_writable`コンセプトの意味論的な制約に目を向けると、出力操作後の値の同一性が要求されています。またその一部として、出力操作の後で`i`が間接参照可能であることは要求されていません。

#### 差異

結局、C++20出力イテレータとC++17出力イテレータの差異は次のようになります（*iterator*での差異を含めています、追加されたものは先頭に+で表示）。

|要求|C++20|C++17|
|---|---|---|
|デフォルト構築可能性|要求される|不要|
|ムーブ可能性|要求される|要求される|
|コピー可能性|不要|要求される|
|`difference_­type`|符号付整数型 or それと同等な型|符号付整数型 or `void`|
|+ 右辺値イテレータからの出力可能性|要求される|不要|
|+ *prvalue*への出力の禁止|要求される|不要|

追加された二つはC++17 -> C++20で制約が厳しくなっています。したがって、C++17出力イテレータはC++20出力イテレータに対して互換性がありません。一方、C++20出力イテレータはC++17出力イテレータに対して`difference_­type`以外の所では互換性があります。

特に、C++20出力イテレータが`iterator_traits`を介して性質を取得される時、特に特殊化がなければ`difference_­type`は`void`になります。その場合、C++20出力イテレータはC++17出力イテレータとして完璧に振る舞うことができます。

これを利用して、出力イテレータより強いC++20イテレータに対する`iterator_traits`からの問い合わせに対して常に*output iterator*として応答することで後方互換性を確保する、と言うアイデアがあるそうです。無論、これに意味があるのかはイテレータによるでしょう。

### forward iterator

前方向イテレータって何？という事は、C++20では[`std::forward_iterator`](https://cpprefjp.github.io/reference/iterator/forward_iterator.html)コンセプト、C++17では[*Cpp17ForwardIterator*要件](https://en.cppreference.com/w/cpp/named_req/ForwardIterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

- *Cpp17InputIterator*要件を満たす
- デフォルト構築可能
- `I`が*mutable iterator*ならば、`reference`は`T`の参照（`T`は`I`の要素型）
- `I`が*constant iterator*ならば、`reference`は`const T`の参照
- マルチパス保証

そして、次の式が可能であることが要求されます（ここでは*Cpp17InputIterator*要件で要求されていたものを上書きする形で含んでいます）

|式|戻り値|
|---|---|
|`i1 != i2`|*contextually convertible to* `bool`|
|`*i`|`referencce`、要素型`T`に変換可能であること|
|`i->m`||
|`++i`|`I&`|
|`i++`|`const I&`に変換可能であること|
|`*i++`|`referencce`|

#### C++20

コンセプトによって次のように定義されます。

```cpp
template<class I>
concept forward_iterator =
  input_iterator<I> &&
  derived_from<ITER_CONCEPT(I), forward_iterator_tag> &&
  incrementable<I> &&
  sentinel_for<I, I>;
```

`std::incrementable`は`std::weakly_incrementable`を少し強くしたものです。

```cpp
template<class I>
concept incrementable =
  regular<I> &&
  weakly_incrementable<I> &&
  requires(I i) {
    { i++ } -> same_as<I>;
  };
```

- [`std::incrementable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/incrementable.html)
- [`std::regular` - cpprefjp](https://cpprefjp.github.io/reference/concepts/regular.html)

ここで重要なのは、後置インクリメントの戻り値型が自分自身であることが要求された事です。

もう一つ、`std::sentinel_for`はイテレータ自身が終端を示しうる事を表すコンセプトで、次のようなものです。

```cpp
template<class S, class I>
concept sentinel_for =
  semiregular<S> &&
  input_or_output_iterator<I> &&
  weakly-equality-comparable-with<S, I>;
```

- [`std::sentinel_for` - cpprefjp](https://cpprefjp.github.io/reference/iterator/sentinel_for.html)

`std::regular`は`std::semiregular`を包含しており、等値比較可能である事とコピー可能であることを要求しています。結局、`std::sentinel_for<I, I>`は自分自身との`== !=`による比較が可能である事を表します。

マルチパス保証は`std::forward_iterator`の意味論的な要件によって要求されています。

#### 差異

結局、C++20前方向イテレータとC++17前方向イテレータの差異は次のようになります（*input iterator*での差異を含めています、追加されたものは先頭に+で表示）。

|要求|C++20|C++17|
|---|---|---|
|`difference_­type`|符号付整数型 or それと同等な型|符号付整数型 or `void`|
|`->`|不要|要求される|
|後置インクリメントの戻り値型| `I` |`const I&`に変換可能な型|
|`reference`と`value_type`との*common reference*|要求される|不要|

デフォルト構築、コピー可能、等値比較可能、などが共通の性質となりました。残ったもので変わったのは後置インクリメントの戻り値型ですが、これはC++20イテレータの方がC++17イテレータに比べて厳しく指定されています。

ここでもC++20前方向イテレータとC++17前方向イテレータには相互に互換性はありませんが、`difference_type`と`->`の差を無視すれば、C++20前方向イテレータはC++17前方向イテレータとして使用することができます。

### bidirectional iterator

双方向イテレータとは？という事は、C++20では[`std::bidirectional_iterator`](https://cpprefjp.github.io/reference/iterator/bidirectional_iterator.html)コンセプト、C++17では[*Cpp17BidirectionalIterator*要件](https://en.cppreference.com/w/cpp/named_req/BidirectionalIterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

- *Cpp17ForwardIterator*要件を満たす

そして、次の式が可能であることが要求されます（ここでは*Cpp17ForwardIterator*要件で要求されていたものを含んでいます）

|式|戻り値|
|---|---|
|`i1 != i2`|*contextually convertible to* `bool`|
|`*i`|`referencce`、要素型`T`に変換可能であること|
|`i->m`||
|`++i`|`I&`|
|`i++`|`const I&`に変換可能であること|
|`*i++`|`referencce`|
|`--I`|`I&`|
|`i--`|`const I&`に変換可能であること|
|`*i--`|`referencce`|

#### C++20

コンセプトによって次のように定義されます。

```cpp
template<class I>
concept bidirectional_iterator =
  forward_iterator<I> &&
  derived_from<ITER_CONCEPT(I), bidirectional_iterator_tag> &&
  requires(I i) {
    { --i } -> same_as<I&>;
    { i-- } -> same_as<I>;
  };
```

ここは深掘りする必要がないですね、C++17要件とほとんど同じ事を言っています。

#### 差異

結局、C++20双方向イテレータとC++17双方向イテレータの差異は次のようになります（*forward iterator*での差異を含めています、追加されたものは先頭に+で表示）。

|要求|C++20|C++17|
|---|---|---|
|`difference_­type`|符号付整数型 or それと同等な型|符号付整数型 or `void`|
|`->`|不要|要求される|
|後置インクリメントの戻り値型| `I` |`const I&`に変換可能な型|
|`reference`と`value_type`との*common reference*|要求される|不要|
|+ 後置デクリメントの戻り値型| `I` |`const I&`に変換可能な型|

追加されたのは後置デクリメントの戻り値型ですが、インクリメントと同様にC++20イテレータの方がC++17イテレータに比べて厳しく指定されています。

互換性に関しては前方向イテレータと同様です。`difference_type`と`->`の差を無視すれば、C++20双方向イテレータはC++17双方向イテレータとして使用することができます。

### random access iterator

ランダムアクセスイテレータって・・・？という事は、C++20では[`std::random_access_iterator`](https://cpprefjp.github.io/reference/iterator/random_access_iterator.html)コンセプト、C++17では[*Cpp17RandomAccessIterator*要件](https://en.cppreference.com/w/cpp/named_req/RandomAccessIterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

- *Cpp17BidirectionalIterator*要件を満たす

そして、次の式が可能であることが要求されます（ここでは*Cpp17ForwardIterator*要件で要求されていたものを含んでいます）

|式|戻り値|
|---|---|
|`i1 != i2`|*contextually convertible to* `bool`|
|`*i`|`referencce`、要素型`T`に変換可能であること|
|`i->m`||
|`++i`|`I&`|
|`i++`|`const I&`に変換可能であること|
|`*i++`|`referencce`|
|`--I`|`I&`|
|`i--`|`const I&`に変換可能であること|
|`*i--`|`referencce`|
|`i += n`|`I&`|
|`i + n` <br/> `n + i`|`I`|
|`i -= n`|`I&`|
|`i - n`|`I`|
|`i1 - i2`|`deference_type`|
|`i[n]`|`reference`に変換可能であること|
|`i1 < i2`|*contextually convertible to* `bool`|
|`i1 > i2`|*contextually convertible to* `bool`|
|`i1 <= i2`|*contextually convertible to* `bool`|
|`i1 >= i2`|*contextually convertible to* `bool`|

出てくる`n`は`I`の`deference_type`の値です。つまり、`deference_type`は符号付整数型である事を暗に要求しています。また、4つの順序付け比較`< > <= >=`は全順序の上での比較であることが要求されています。

#### C++20

コンセプトによって次のように定義されます。

```cpp
template<class I>
concept random_access_iterator =
  bidirectional_iterator<I> &&
  derived_from<ITER_CONCEPT(I), random_access_iterator_tag> &&
  totally_ordered<I> &&
  sized_sentinel_for<I, I> &&
  requires(I i, const I j, const iter_difference_t<I> n) {
    { i += n } -> same_as<I&>;
    { j +  n } -> same_as<I>;
    { n +  j } -> same_as<I>;
    { i -= n } -> same_as<I&>;
    { j -  n } -> same_as<I>;
    {  j[n]  } -> same_as<iter_reference_t<I>>;
  };
```

`std::totally_ordered<I>`は全順序の上での4つの順序付け比較が可能である事を表し、`std::sized_sentinel_for<I, I>`は2項`-`によって距離が求められるイテレータである事を表しています。

その後に並べられているものも含めて、ほぼほぼC++17イテレータに対するものと同じ要求がなされています。

#### 差異

結局、C++20ランダムアクセスイテレータとC++17ランダムアクセスイテレータの差異は次のようになります（*forward iterator*での差異を含めています、追加されたものは先頭に+で表示）。

|要求|C++20|C++17|
|---|---|---|
|`difference_­type`|符号付整数型 or それと同等な型|符号付整数型|
|`->`|不要|要求される|
|後置インクリメントの戻り値型| `I` |`const I&`に変換可能な型|
|`reference`と`value_type`との*common reference*|要求される|不要|
| 後置デクリメントの戻り値型| `I` |`const I&`に変換可能な型|
|+ `i[n]`の戻り値型| `reference` |`reference`に変換可能な型|

添字演算子の戻り値型に関してC++20イテレータはより厳しく指定されています。

結局互換性に関しては双方向・前方向イテレータと同様です。`difference_type`と`->`の差を無視すれば、C++20ランダムアクセスイテレータはC++17ランダムアクセスイテレータとして使用することができます。

### contiguous iterator

隣接イテレータ🤔という事は、C++20では[`std::contiguous_iterator`](https://cpprefjp.github.io/reference/iterator/contiguous_iterator.html)コンセプトがそれを定義しています。  
C++17では文章でひっそりと指定されていたのみで、名前付き要件になっておらずC++20にも対応する要件はありません（cppreference.comには[*LegacyContiguousIterator*](https://en.cppreference.com/w/cpp/named_req/ContiguousIterator)として記述があります）。

#### C++17

C++17でひっそりと指定されていた文章を読み解くと、次のような要件です

- *Cpp17RandomAccessIterator*要件を満たす
- 整数値`n`、間接参照可能なイテレータ`i`と`(i + n)`について
    - `*(i + n)`は`*(addresof(*i) + n)`と等価（*equivalent*）

要はイテレータを`n`進めても、要素のポインタを`n`進めても、同じ要素を指してね？っていうことです。なるほど確かに*contiguous*。

C++17では*contiguous iterator*という分類を導入し、`std::array`や`std::vector`などのイテレータが*contiguous iterator*であると規定はしましたが、イテレータカテゴリとして正式にライブラリに取り入れたわけではありませんでした。

そのため、*contiguous iterator*であると規定したイテレータさえも、ジェネリックコード上ではランダムアクセスイテレータとしてしか扱えませんでした。C++17隣接イテレータという種類のイテレータは実質的に存在していないのです。

#### C++20

C++20では正式にライブラリに取り入れられ、コンセプトによって定義されています。

```cpp
template<class I>
concept contiguous_iterator =
  random_access_iterator<I> &&
  derived_from<ITER_CONCEPT(I), contiguous_iterator_tag> &&
  is_lvalue_reference_v<iter_reference_t<I>> &&
  same_as<iter_value_t<I>, remove_cvref_t<iter_reference_t<I>>> &&
  requires(const I& i) {
    { to_address(i) } -> same_as<add_pointer_t<iter_reference_t<I>>>;
  };
```

- [`std::to_address` - cpprefjp](https://cpprefjp.github.io/reference/memory/to_address.html)
- [`std::add_pointer` - cpprefjp](https://cpprefjp.github.io/reference/type_traits/add_pointer.html)

3つ目の制約式は間接参照の結果が*lvalue*となることを要求しており、4つ目の制約式は`I`の`reference`から`CV`修飾と参照修飾を取り除いたものが要素型になることを要求しています。

最後の`requires`式にある`std::to_address`というのはC++20から追加されたもので、イテレータを含めたポインタ的な型の値からそのアドレスを取得するものです。その経路は`std::pointer_traits`が利用可能ならそこから、そうでないなら`operator->()`の戻り値を再び`std::to_address`にかけることによってアドレスを取得します（つまり、`operator->()`がスマートポインタを返していてもいいわけです・・・）。

イテレータは`std::pointer_traits`を特殊化することを求められていないため、イテレータ型に対しての`std::to_address`は実質的にイテレータの`operator->()`を利用することになります。

そして、`std::add_pointer`は参照型に対しては参照を除去したうえでポインタを足します。

最後の制約式は全体として、`operator->`が利用可能であり、その戻り値から最終的に得られる生のポインタ型は、間接参照の結果から取得したアドレスのポインタ型と同じ、であることを要求しています。

そして、`std::contiguous_iterator`コンセプトの意味論的な制約として、`std::to_address`によって得られるポインタと、間接参照の結果値を指すポインタが一致すること、及び2つのイテレータの間の距離とその要素を指すポインタ間距離が等しくなることを要求しています。

わかりにくい制約ですが、*contiguous iterator*というのが実質的にポインタ型を指していることを考えると少し見えてくるものがあるでしょうか。

ポインタではない隣接イテレータは存在意義が良く分かりませんが、これらの制約は直接ポインタ型を要求しておらず、メモリ上の連続領域をラップした形のポインタではない隣接イテレータというのを作ろうと思えば作れることを示しています。

#### 差異

C++17隣接イテレータは居ないので、差異はあっても気にする必要はありません。C++20隣接イテレータはC++17コードからはC++17ランダムアクセスイテレータとしてしか扱われることはないでしょう。

C++20隣接イテレータは実質的に`->`が要求されるようになったため、C++17ランダムアクセスイテレータとして扱う時の非互換な部分は`deference_type`だけとなります。とはいえ、ジェネリックなコードにおいてはそこはあまり気にする必要はなさそうですので、実質的にはC++20隣接イテレータはC++17ランダムアクセスイテレータに対して後方互換性があるとみなして良いでしょう。

### まとめ

振り返ると結局、大きな差異というのは次のものでした

- C++20入力イテレータとC++17入力イテレータの相互非互換
- 全てのC++20イテレータカテゴリにおける`->`の欠如
    - 隣接イテレータも直接`->`が求められるわけではない・・・

この`->`が抜け落ちているのは忘れているわけではなく、意図的なものの様です。なぜかは知りません。

`->`を無視すると、C++20前方向イテレータ以上の強さのイテレータは同じカテゴリのC++17イテレータに対して後方互換性があり、必然的にC++17入力イテレータに対して後方互換性があります。また、C++20隣接イテレータは全てのC++17イテレータに対して実質的に後方互換性を持っています。

一方全てのカテゴリで、C++17イテレータはC++20イテレータに対する前方互換性はありません。要件が厳しくなっているためで、中には使用できるものもないではないかもしれませんが、多くの場合はC++20イテレータコンセプトによって弾かれるでしょう。

`<ranges>`の各種`view`に代表されるC++20イテレータでは、メンバ型として`iterator_concept`と`iterator_category`を二つ備えることでC++17互換イテレータとしての性質を表明しています（その詳細は前回参照）。そこでは、`iterator_concept`がランダムアクセスイテレータ等であっても、`iterator_category`は常に入力イテレータとする運用が良く行われているように見えます。  
これを見るに、標準化委員会的にはC++20イテレータの`->`の欠如は対C++17互換にとって重要な事とはみなされてはいないようです。

- [23.3.5 C++17 iterator requirements[iterator.cpp17] - N4861](https://timsong-cpp.github.io/cppwp/n4861/iterator.cpp17)
- [27.2 Iterator requirements[iterator.requirements] - N4659](https://timsong-cpp.github.io/cppwp/n4659/iterators#iterator.requirements.general-6)
- [`<iterator>` - cpprefjp](https://cpprefjp.github.io/reference/iterator.html)
- [Iterator library - cppreference](https://en.cppreference.com/w/cpp/iterator)
- [イテレータに->演算子オーバーロードは必要？ - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20191025/p1)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20201227_17iterator_20iterator.md)