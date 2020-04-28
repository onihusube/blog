# ［C++］std::common_referenceの概念

C++20より追加された`std::common_reference<T, U>`は型`T, U`両方から変換可能な共通の参照型を求めるメタ関数です。ただしその結果型は必ずしも参照型ではなかったりします。`std::common_type`との差など、存在理由がよく分からない物でもあります・・・

同じ事を思う人は他にも居たようでstackoverflowで質問している人がいて、そこに`common_reference`を考案したEric Nieblerさん御本人が解説を書いていました。本記事はそれを日本語で説明し直したものです。

- [What is the purpose of C++20 std::common_reference? - stackoverflow](https://stackoverflow.com/questions/59011331/what-is-the-purpose-of-c20-stdcommon-reference)

### イテレータの`::reference`と`::value_type`の関連性

標準ライブラリのイテレータは`::reference`と`::value_type`という二つの入れ子型を持っています。`reference`は通常`*it`の戻り値型であり、`value_type`はイテレートしているシーケンスの要素型（`const`や参照型ではない）を表します。そして、`reference`は`value_type&`もしくはその`const`付きの型です。これによって次のような操作が可能です。

```cpp
//要素型を明示的にコピーしたい場合など？
value_type t = *it;
```

このように、これら2つの型の間には通常自明な関係性が存在しています。そして、それら2つの型は`const value_type&`という共通の型に変換可能であるはずで、実際ほとんどのイテレータはそうなっています。

#### より高機能なイテレータ

rangeライブラリのようなシーケンスを抽象化して扱うライブラリ（例えばC#のLINQなど）によくある操作に、2つのシーケンスのzipという操作があります。zipは2つのシーケンスをまとめて1つのシーケンスとして扱う操作です（[2つのシーケンスを1つのシーケンスにまとめる様がzipperに似ていることから来ているそうです](https://twitter.com/yohhoy/status/1237378765207916544)）。2つのシーケンスの同じ位置の要素をペアにして、そのペアのシーケンスを生成する操作とも言えます。その場合、わざわざ元のシーケンスをコピーしてから新しいシーケンスを作成なんてことをするはずもなく、イテレータを介してそのようなシーケンスを仮想的に作成します。

その時、そのイテレータ（`zip_iterator`と呼ぶことにします）の`::reference`と`::value_type`はどうなっているでしょう？例えば、`std::vector<int>`と`std::vector<double>`をzipしたとすれば、その場合の`zip_iterator`の2つの入れ子型は次のようになるでしょう。

- `reference`  : `std::pair<int&, double&>`
- `value_type` : `std::pair<int, double>`

見て分かるように、これらの型はもはや`const value_type&`という型で受けることはできず、`value_type t = *it`のような操作もできません。2つの型の間の関連性は失われてしまっています。

しかし、この場合でもこの2つの型の間に何の関連も無いという事はなく、なにかしら関連性があるように思えます。しかし、どのような関連性を仮定し利用できるのでしょうか・・・？

### `std::common_reference`

`std::common_reference`はそれに対する1つの解（あるいは要求）です。つまり、イテレータ種別に関わらずその`reference`と`value_type`の間には共通の参照型（従来のイテレータにおける`const value_type&`）に相当するものがあるはずであり、あるものとして、ジェネリックな操作において（すなわち任意のイテレータについて）その仮定を安全なものであると定めます。

そして、そのような共通の参照型に相当するものを統一的に求め、表現するために用意されたのが`std::common_reference`メタ関数です。

これは次のような操作が常に可能であることを保証します。

```cpp
template<typename Iterator>
void algo(Iterator it, Iterator::value_type val) {
  using CR = std::common_reference<Iterator::reference, Iterator::value_type>::type;

  //共に束縛可能
  CR r1 = *it;
  CR r2 = val;
}
```

このように、`common_reference`は従来のイテレータ型の`reference`と`value_type`の間の関連性をより一般化したものであり、ジェネリックな処理において`zip_iterator`のようなより一般的なイテレータを区別なく扱うために必要なものであることが分かります。

なお、名前に`referencce`とあるのは従来のイテレータにおける`common_reference`が`const value_type&`という参照型であったことから来ていると思われ、より一般的な`common_reference`は必ずしも参照型ではなく、そうである必要もありません。

#### `std::common_reference_with`コンセプト

ある型のペアが`common_reference`を有しているかを`std::common_reference<T, U>::type`が有効かを調べて判定するなどということは前時代的です。C++20にはコンセプトがあり、それで判定すればいいはず。

ということで？C++20ではそのような用途のために`std::common_reference_with`コンセプトが`<concepts>`に用意されています。これは、`std::common_reference_with<T, U>`のように2つの型の間に`common_reference`があることを表明（要求）するそのままのものです。

#### C++20に`zip_view`が無いのは・・・

`std::common_reference`の動機付けでもあった`zip_iterator`を返す`zip_view`のようなrange操作はC++20には導入されていません（同じ事情を持つものには`std::vector<bool>`が既にあります）。なぜかといえば、`zip_iterator`についての`common_reference`を単純には求められなかったためです。再掲になりますが、`zip_iterator`の`reference`と`value_type`は一般的には次のようになります。

- `reference`  : `std::pair<T&, U&>`
- `value_type` : `std::pair<T, U>`

この場合の`common_reference`は単純には`std::pair<T&, U&>`になるでしょうが、現在の`std::pair`は`std::pair<T, U> -> std::pair<T&, U&>`のような変換はできません。C++20でもそれは可能になってはいません。かといって、`zip_view`のためだけにpair-likeな型を用意するのも当然好まれません。

この問題をどうするのかの議論はされていますが、結論がC++20には間に合わなかったためC++20には`zip_view`はありません。

そして、この影響を受けてしまったのが`std::flat_map`です。C++20入りを目指していましたが、パフォーマンスのためにそのKeyのシーケンスとvalueのシーケンスをそれぞれ別で持つという設計を選択していたため、要素のイテレートのために`zip_view`が必要となりました。しかし、`zip_view`は延期されたのとその設計からくる問題があったのとで`std::flat_map`も延期され、それに引きずられて`std::flat_set`もC++20には入りませんでした。

どれも将来的には入るとは思いますが、C++20で使いたかった・・・

### コンセプト定義に現れる`common_reference_with`

`std::common_reference`はイテレータ型を受け取るのではなく2つの型を受け取ってその間の`common_reference`を求めます。`common_reference`の動機付けはイテレータ型からのものでしたが、そこから脱却すれば、`common_reference`はより一般化した2つの型の間の関連性ととらえることができます。

そのような`common_reference`とは、2つの型に共通している部分を表す型だと見ることができます。`std::common_type`は集合論的な意味での共通部分に相当していますが、`std::common_reference`はそのような共通部分を参照、あるいは束縛できる型を表します。つまり、`std::common_reference`は`std::common_type`を包含しています。  
このことは逆に言えば、`common_reference`を持つ2つの型は何かしら共通した部分を持つ、という事です。それはおそらく基底クラスもしくは同じ型のメンバであるでしょう。

そして、この性質は標準ライブラリにおけるコンセプト定義において利用されます。例えば、`std::totally_ordered_with<T, U>`や`std::swappable_with<T, U>`のように2つの型の間で可能な性質を表明するコンセプトの定義においてほぼ必ず`std::common_reference_with<T, U>`が現れています（そのようなコンセプトは多くが`~_with`という命名になっています）。  
これらのようなコンセプトが表明する関係は明らかに2つの型の間に共通した部分があることを前提にしています。`std::common_reference_with`を定義中に使用しているのは、そのような関連性があることを表明し、要請するためです。

例えば、`std::totally_ordered_with, std::equality_comparable_with, std::three_way_comparable_with`など比較に関するコンセプトなら、比較可能であるという事は2つの型の間に比較可能な部分がある筈ですし、`std::swappable_with`ならば2つの型の間に交換可能な共通の部分がある筈です。

`std::common_reference`と`std::common_reference_with`は一見すると意味不明で何に使うのか良く分かりませんが、ここまでくるとようやく意味合いが見えてくるでしょうか。特に、コンセプト定義における`std::common_reference_with`は[意味のあるコンセプト](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#t20-avoid-concepts-without-meaningful-semantics)を定義するのに役立つかもしれません。

### 参考文献

- [What is the purpose of C++20 std::common_reference? - stackoverflow](https://stackoverflow.com/questions/59011331/what-is-the-purpose-of-c20-stdcommon-reference)
- [P0022R1 Proxy Iterators for the Ranges Extensions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/p0022r1.html)
- [std::common_reference - cpprefjp](https://cpprefjp.github.io/reference/type_traits/common_reference.html)
- [P1727R0 Issues with current flat_map proposal](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1727r0.pdf)
- [Trip Report: ISO C++ Meeting Cologne (2019) by Matthias Gehre](https://www.silexica.com/news/iso_cpp_meeting_2019/)
    - `std::flat_map`と`zip_view`についての議論に触れられていたが、リンク切れしている・・・

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20200224_common_reference.md)