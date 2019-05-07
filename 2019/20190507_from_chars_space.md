# ［C++］std::from_charsにおける先頭スペースの扱いについて

C++17で追加された`std::from_chars`はその効果の説明においてCライブラリのstrtol、strtod関数を参照し、そこにいくつか制限を加えた形で説明されています。

ところで、strtol、strtod関数は共に入力文字列の先頭にあるスペースを読み飛ばすようになっています。`std::from_chars`の説明を単純に読むと先頭スペースの扱いについて何も書かれていないので同じようになるように思えます。  
しかし実際には`std::from_chars`は先頭スペースの読み飛ばしを行いません。

それについては少し厄介な書き方をされているため、この記事はそこを読み解くためのメモです。

### C++17 `std::from_chars`
C++17(N4659) §23.2.9 [utility.from.chars]の`std::from_chars`の関数の効果は以下のように記述されています。

整数型のオーバーロード
> The pattern is the expected form of the subject sequence in the "C" locale for the given nonzero base, as described for strtol, (以下略

浮動小数点型のオーバーロード
> The pattern is the expected form of the subject sequence in the "C" locale, as described for strtod, (以下略

両方をまとめてざっと訳すと
> 用いるパターンは、strtol（strtod）で説明されているCロケールによるsubject sequenceのexpected formである

そして、`See also: ISO C 7.22.1.3, ISO C 7.22.1.4.`と終わりに添えられています。

（subject sequenceは説明のため、expected formはピッタリな訳が思いつかないのでそのままにしておきます・・・）

### C11 strtol, strtod
C11(N1570) §7.22.1.3, §7.22.1.4 の`strtol, strtod`では以下のように記述されています（長いので一部抜粋）。

`strtod`
>First, they decompose the input string into three parts: an initial, possibly empty, sequence of white-space characters (as speciﬁed by the isspace function), a subject sequence resembling a ﬂoating-point constant or representing an inﬁnity or NaN; and a ﬁnal string of one or more unrecognized characters, including the terminating null character of the input string.  
> ～中略～  
> The subject sequence is deﬁned as the longest initial subsequence of the input string, starting with the ﬁrst non-white-space character, that is of the expected form. The subject sequence contains no characters if the input string is not of the expected form.


`strtol`
>First, they decompose the input string into three parts: an initial, possibly empty, sequence of white-space characters (as speciﬁed by the isspace function), a subject sequence resembling an integer represented in some radix determined by the value of base, and a ﬁnal string of one or more unrecognized characters, including the terminating null character of the input string.  
> ～中略～  
> The subject sequence is deﬁned as the longest initial subsequence of the input string, starting with the ﬁrst non-white-space character, that is of the expected form. The subject sequence contains no characters if the input string is empty or consists entirely of white space, or if the ﬁrst non-white-space character is other than a sign or a permissible letter or digit.

浮動小数点と整数とで多少の違いはあれど同じようなことが書かれているのでまとめて訳すと

> まず入力文字列を3つの部分に分解する。  
> 初めに、isspace関数で識別されるホワイトスペースのシーケンス（空でも可）  
> 次に（浮動小数点数もしくは整数型の文字列を含む）subject sequence  
> 最後に、残った1文字以上の識別されない文字列（終端の`\0`を含む）
>   
> subject sequenceは最初のホワイトスペース以外の文字で始まる入力文字列の部分文字列として定義される。それはexpected formである。  
> 入力文字列がexpected formでない場合、subject sequenceは空になる。

### subject sequence
賢い人はお気づきかもしれません、C++の`std::from_chars`の効果の説明における`subject sequence`という言葉は明らかにCの`strtol, strtod`における`subject sequence`を指しています。  
そして、`subject sequence`は先頭のホワイトスペースのシーケンスを除いた最初の、パターンにマッチする文字列から構成されます。すなわち、`subject sequence`には先頭ホワイトスペースの文字列は含まれていません。

また、`std::from_chars`が入力文字列中からまず探すのは`subject sequence`（のexpected form）であり、先頭ホワイトスペースについては何ら記述がありません。

これらの事からようやく、`std::from_chars`は入力文字列先頭に1つ以上のホワイトスペースがある場合にそれを読み飛ばすことはしない、という仕様を読み取ることができます。


### 参考文献
- [std::from_chars - cpprefjp](https://cpprefjp.github.io/reference/charconv/from_chars.html)
- [Primitive numeric input conversion - N4659](https://timsong-cpp.github.io/cppwp/n4659/utility.from.chars)
- [ISO/IEC 9899:201x DIS N1570](http://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)