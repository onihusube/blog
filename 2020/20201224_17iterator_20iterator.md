# ［C++］ C++17イテレータ <=> C++20イテレータ

これは[C++ Advent Calendar 2020](https://qiita.com/advent-calendar/2020/cxx)の24日めの記事です。

前回と前々回でC++20のイテレータは一味も二味も違うぜ！という事を語ったわけですが、具体的にどう違うのかを見てみようと思います。

以下、特に断りが無ければ`I`はイテレータ型、`i`はイテレータのオブジェクトだと思ってください。

### iterator

イテレータとは何か？

C++20では[`std::input_or_output_iterator`](https://cpprefjp.github.io/reference/iterator/input_or_output_iterator.html)コンセプト、C++17では[*Cpp17Iterator*要件](https://en.cppreference.com/w/cpp/named_req/Iterator)がそれを定義しています。

#### C++17

まず、次の要件が要求されています

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
|`++r`|`I&`|

間接参照と前置インクリメントによる進行がかのうであれ、という事です。

C++20 `iterator_taris`で使われる対応するコンセプトは次のように規定されています。

```cpp
template<class I>
concept cpp17-iterator =
  copyable<I> && requires(I i) {
    {   *i } -> can-reference;
    {  ++i } -> same_as<I&>;
    { *i++ } -> can-reference;
  };
```

`can-reference`は戻り値型が`void`ではない事を表すコンセプトです。こっちだと後置インクリメントに対する制約が追加されていますが、意味することは大きく変わってはいません。

コンセプトを深さ優先探索していくとスタックオーバーフローで脳内コンパイラがしぬので適宜cpprefjpを参照してください。

- [`std::copyable` - cpprefjp](https://cpprefjp.github.io/reference/concepts/copyable.html)
- [`std::same_as` - cpprefjp](https://cpprefjp.github.io/reference/concepts/same_as.html)
- [`dereferenceable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/dereferenceable.html)

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

ここで直接見ることの出来るのは間接参照の要求です。これはC++17の要求と同じことを意味しています。

`std::weakly_incrementable`は`++`によってインクリメント可能であることを表すコンセプトです。

```cpp
template<class I>
concept weakly_incrementable =
  default_initializable<I> && movable<I> &&
  requires(I i) {
    typename iter_difference_t<I>;
    requires is-signed-integer-like<iter_difference_t<I>>;
    { ++i } -> same_as<I&>;   // 等しさを保持することを要求しない
    i++;                      // 等しさを保持することを要求しない
  };
```

​`difference_­type`が符号付き整数型であることが要求されており、前置戻り値型に対する要求は同じです。

ここで大きく異なる点があり、デフォルト構築可能であることと、コピー可能ではなくムーブ可能であることが求められています。また、後置インクリメントに戻り値型の要求がありません。

- [`std::weakly_incrementable` - cpprefjp](https://cpprefjp.github.io/reference/iterator/weakly_incrementable.html)

#### 差異

結局、C++20イテレータとC++17イテレータの差異は次のようになります。

|要求|C++20|C++17|
|---|---|---|
|デフォルト構築可能性|要求される|不要|
|ムーブ可能性|要求される|要求される|
|コピー可能性|不要|要求される|
|後置インクリメントの戻り値型|任意（`void`も可）|少なくとも間接参照可能な型|

コピー可能 -> ムーブ可能ですが、ムーブ可能 -> コピー可能ではありません。後置インクリメント以外は、C++20のイテレータはC++17から制約が厳しくなっています。

この*iterator*とは、全てのイテレータのベースとなる部分の分類です。すなわち、この時点ですでにそこそこの違いがあることが分かります。

そして、殆どの要件が厳しくなっていることからC++17イテレータでしかないものをC++20イテレータとして扱うことは出来ず、後置インクリメントの差異からC++20イテレータでしかないものをC++17イテレータとして扱うこともできません。

すなわち、*iterator*という分類ではC++20イテレータとC++17イテレータには相互に互換性がありません。

### input iteratorr

入力イテレータとは何ぞ？

C++20では[`std::input_iterator`](https://cpprefjp.github.io/reference/iterator/input_iterator.html)コンセプト、C++17では[*Cpp17InputIterator*要件](https://en.cppreference.com/w/cpp/named_req/InputIterator)がそれを定義しています。


### ouptut iterator

出力イテレータとは一体？

C++20では[`std::output_iterator`](https://cpprefjp.github.io/reference/iterator/output_iterator.html)コンセプト、C++17では[*Cpp17OutputIterator*要件](https://en.cppreference.com/w/cpp/named_req/OutputIterator)がそれを定義しています。


### forward iterator

前方向イテレータって何？

C++20では[`std::forward_iterator`](https://cpprefjp.github.io/reference/iterator/forward_iterator.html)コンセプト、C++17では[*Cpp17ForwardIterator*要件](https://en.cppreference.com/w/cpp/named_req/ForwardIterator)がそれを定義しています。


### bidirectional iterator

双方向イテレータとは？

C++20では[`std::bidirectional_iterator`](https://cpprefjp.github.io/reference/iterator/bidirectional_iterator.html)コンセプト、C++17では[*Cpp17BidirectionalIterator*要件](https://en.cppreference.com/w/cpp/named_req/BidirectionalIterator)がそれを定義しています。

### random access iterator

ランダムアクセスイテレータ・・・？

C++20では[`std::random_access_iterator`](https://cpprefjp.github.io/reference/iterator/random_access_iterator.html)コンセプト、C++17では[*Cpp17RandomAccessIterator*要件](https://en.cppreference.com/w/cpp/named_req/RandomAccessIterator)がそれを定義しています。


### contiguous iterator

双方向イテレータ🤔

C++20では[`std::contiguous_iterator`](https://cpprefjp.github.io/reference/iterator/contiguous_iterator.html)コンセプトがそれを定義しています。  
C++17では文章でひっそりと指定されていたのみで、名前付き要件になっておらずC++20にも対応する要件はありません（cppreference.comには[*LegacyContiguousIterator*](https://en.cppreference.com/w/cpp/named_req/ContiguousIterator)として記述があります）。



- [23.3.5 C++17 iterator requirements[iterator.cpp17] - N4861](https://timsong-cpp.github.io/cppwp/n4861/iterator.cpp17)
- [27.2 Iterator requirements[iterator.requirements] - N4659](https://timsong-cpp.github.io/cppwp/n4659/iterators#iterator.requirements.general-6)
- [`<iterator>` - cpprefjp](https://cpprefjp.github.io/reference/iterator.html)
- [Iterator library - cppreference](https://en.cppreference.com/w/cpp/iterator)