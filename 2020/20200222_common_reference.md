# ［C++］std::common_reference

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

Rangeライブラリのようなシーケンスを抽象化して扱うライブラリ（例えばC#のLINQなど）によくある操作に、2つのシーケンスのzipという操作があります。zipは2つのシーケンスをまとめて1つのシーケンスとして扱う操作です（2つのシーケンスを1つのシーケンスに圧縮するからzip？）。2つのシーケンスの同じ位置の要素をペアにして、そのペアのシーケンスを生成する操作とも言えます。その場合、わざわざ元のシーケンスをコピーしてから新しいシーケンスを作成なんてことをするはずもなく、イテレータを介してそのようなシーケンスを仮想的に作成します。

その時、そのイテレータ（`zip_iterator`と呼ぶことにします）の`::reference`と`::value_type`はどうなっているでしょう？例えば、`std::vector<int>`と`std::vector<double>`をzipしたとすれば、その場合の`zip_iterator`の2つの入れ子型は次のようになるでしょう。

- `reference`  : `std::pair<int&, double&>`
- `value_type` : `std::pair<int, double>`

見て分かるように、これらの型はもはや`const value_type&`という型で受けることはできず、`value_type t = *it`のような操作もできません。2つの型の間の関連性は失われてしまっています。

しかし、この場合でもこの2つの型の間に何の関連も無いという事はなく、なにかしら関連性があるように思えます。しかし、どのような関連性を仮定し利用できるのでしょうか・・・？

### `std::common_reference`





### ～_withなコンセプト定義に現れる`common_reference_with`コンセプト

### 参考文献

- [What is the purpose of C++20 std::common_reference? - stackoverflow](https://stackoverflow.com/questions/59011331/what-is-the-purpose-of-c20-stdcommon-reference)
- [P0022R1 Proxy Iterators for the Ranges Extensions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/p0022r1.html)
- [std::common_reference - cpprefjp](https://cpprefjp.github.io/reference/type_traits/common_reference.html)