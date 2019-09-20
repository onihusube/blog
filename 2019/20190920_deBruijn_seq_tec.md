# ［C++］de Bruijn sequenceを用いたLSB/MSB位置検出テクニック

### de Bruijn sequence（ド・ブラウン列）

de Bruijn sequenceとは、いくつかの文字である長さの文字列を作ることを考えた時、その組み合わせの全てを含んだ文字列のことを言います。

例えば、文字`a, b`を使った長さ3の文字列は`aaa, aab, aba, baa, abb, bab, bbb, bba`の8通りなので、このde Bruijn sequenceは`aaababbbaa`になります。  
この文字列の先頭から3文字づつ、1文字づつ右にずらしながら見ていくと、確かに8通りの組み合わせ全てを含んでいる事がわかります。

```
aaababbbaa
aaa
 aab
  aba
   bab
    abb
     bbb
      bba
       baa
```

文字`a, b`を`0, 1`に置き換えてやれば、2進数列のde Bruijn sequenceを考える事ができそうです。

### de Bruijn sequenceによるMSB位置検出

この2進数列のde Bruijn sequenceを用いて、高速にMSB位置を検出するアルゴリズムがあります。

```cpp
unsigned int v;   
int r;

static const int MultiplyDeBruijnBitPosition[32] = 
{
  0, 1, 28, 2, 29, 14, 24, 3, 30, 22, 20, 15, 25, 17, 4, 8, 
  31, 27, 13, 23, 21, 19, 16, 7, 26, 12, 18, 6, 11, 5, 10, 9
};
r = MultiplyDeBruijnBitPosition[((uint32_t)((v & -v) * 0x077CB531U)) >> 27];
```






### 参考文献
- [Using de Bruijn Sequences to Index a 1 in a Computer Word](http://supertech.csail.mit.edu/papers/debruijn.pdf)
- [一番右端の立っているビット位置を求める「ものすごい」コード - 当面C#と.NETな記録](https://siokoshou.hatenadiary.org/entries/2009/07/04)
- [De Bruijn sequence - Wikipedia](https://en.wikipedia.org/wiki/De_Bruijn_sequence)
- [De Bruijn列 - Thoth Children!!](http://www.thothchildren.com/chapter/5bc89f5b51d930518902dded)
- [組合せとグラフの理論 ( 塩田 )](http://lupus.is.kochi-u.ac.jp/shiota/graph07/euler_hamilton.pdf)
- [de Bruijn Graph を使った de novo アセンブリの発想がすごい件 - ほくそ笑む](https://hoxo-m.hatenablog.com/entry/20100930/p1)