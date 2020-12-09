# ［C++］ C++20からのiterator_traits

これは[C++ Advent Calendar 2020](https://qiita.com/advent-calendar/2020/cxx)のn日めの記事です。

C++20の`iterator_traits`には、互換レイヤとして複雑な役割が与えられるようになります。

### `iterator_traits`の役割

ここまで見たように、C++20以降はイテレータ利用にあたっては`iterator_traits`を利用する必要は全く無くなっています。それに伴って`iterator_traits`にはC++20イテレータをC++17互換イテレータとして利用するための互換レイヤとしての役割が新たに与えられています。

どういう事かというと、C++20のイテレータはC++17イテレータから求められることが変化しており、C++20イテレータにはC++17イテレータに対する後方互換性がありません。そのために、C++17のコードからC++20以降のイテレータを利用しようとすると謎のコンパイルエラーが多発する事になるでしょう。
そんな時でも、`iterator_traits`はC++17以前のコードからは利用されているはずで、イテレータを利用する際は何かしらそれを介しているはずです。そこで、`iterator_traits`でイテレータ互換性のチェックとC++17イテレータへの変換を行う事にしたようです。




### 参考文献

- [`<iterator>` - cpprefjp](https://cpprefjp.github.io/reference/iterator.html)
- [`std::iterator_traits` - cppreference](https://en.cppreference.com/w/cpp/iterator/iterator_traits)
- [P2259R0 Repairing input range adaptors and counted_iterator](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2259r0.html)