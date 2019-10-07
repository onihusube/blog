# ［C++］volatile

※この記事は[C++20を相談しながら調べる会 #3](https://cpp20survey.connpass.com/event/147002/)の成果として書かれました。

C++20より、一部の`volatile`の用法が非推奨化されます。提案文書は「Deprecating volatile」という壮大なタイトルなのでvolatileそのものが無くなるのかと思ってしまいますがそうではありません。  
この提案文書をもとに何が何故無くなるのかを調べてみます・・・

### そもそもvolatileってなんだろう・・・

C++における`volatile`指定の効果は次のように規定されています（[6.9.1 Sequential execution [intro.execution]](http://eel.is/c++draft/basic.exec#intro.execution-7)）。
>Reading an object designated by a volatile glvalue ([basic.lval]), modifying an object, calling a library I/O function, or calling a function that does any of those operations are all side effects, which are changes in the state of the execution environment.

`volatile`オブジェクト（メモリ領域）へのアクセス（読み/書き）、およびそれを実行する関数呼び出しは全て副作用（*side effects*）である！と言っています。

そしてそのあとに以下のように書いてあります。

>Every value computation and side effect associated with a full-expression is sequenced before every value computation and side effect associated with the next full-expression to be evaluated.

完全式（*full-expression*）の全ての値の計算および副作用（*side effects*）は、次の完全式の全ての値の計算および副作用の評価の前に位置付けられる（*sequenced before*）、と言っています。  
ここでの完全式（*full-expression*）とは、セミコロン`;`で終わる一つの式のことです。変な書き方をしていなければ、通常それは1行で書かれていると思います。

ついでに*sequenced before*と言うのも見てみると

>Sequenced before is an asymmetric, transitive, pair-wise relation between evaluations executed by a single thread ([intro.multithread]), which induces a partial order among those evaluations.  
>Given any two evaluations A and B, if A is sequenced before B (or, equivalently, B is sequenced after A), then the execution of A shall precede the execution of B.

*sequenced before*とは、__シングルスレッド実行においての__ 評価間の関係のことで、評価Aが評価Bよりも前に位置づけられる（*sequenced before*）場合、Aの実行はBの実行より前に行われる、と書かれています。シングルスレッドです。

もう一つ、C++規格がその動作の対象としている抽象機械の[観測可能な動作（*observable behavior*）](http://eel.is/c++draft/intro#abstract-6.1)のところに次のようにあります
>Accesses through volatile glvalues are evaluated strictly according to the rules of the abstract machine.  
>〜中略〜  
>These collectively are referred to as the observable behavior of the program. 

`volatile`オブジェクトへのアクセスは抽象機械の規則に従って厳密に評価される。〜中略〜 これらは、__プログラムの観測可能な動作（*observable behavior*）__ と呼ばれる、とあります。

そして、C++の適合実装（コンパイラ）はこの抽象機械上プログラムの観測可能な動作をエミュレートするように実装され、観測可能な動作の外にある事をエミュレートする必要はありません。  
非`volatile`な変数へのアクセスはこの観測可能な動作に含まれていないので、最終的なプログラムの出力に影響を与えない範囲において、それらのアクセス・計算は削除されたり順序が変わったりします。これこそがコンパイラに許可されている最適化の範囲です。

`volatile`オブジェクトへのアクセスおよびその先で起こることは全て副作用（*side effects*）になりますが、観測可能な動作（*observable behavior*）はそのうちの`volatile`オブジェクトへのアクセスそのものしか含んでいません。  
従って、コンパイラが気にするのは`volatile`オブジェクトへアクセスしたかどうかだけであり、その先で起こる事については感知しなくてもいいわけです。  
またこのことから「観測可能な動作⊂副作用」と言う関係が成り立ち、副作用は必ずしも最適化対象外にあるわけではないこともわかります。

これらの条文から、C++が規定する`volatile`指定の効果とは

- シングルスレッド実行上において
- `volatile`オブジェクトへのアクセス（読み/書き）の順序を保障し
  - すなわち、C++コード上で書いた通りになる事を保障
- `volatile`オブジェクトへのアクセスに関してはコンパイラの最適化対象外となる
  - `volatile`オブジェクト（の関与する部分）は最適化されない、と言うことと等価

と言う事だとわかります。

#### マルチスレッドとvolatile

`volatile`の効果は上記のようにシングルスレッドにおいてのものであり、マルチスレッドにおいてはなんら記述がないので、`volatile`変数を`atomic`変数のつもりで利用すると常に未定義動作の世界にこんにちはします。

マルチスレッド上での一つの`volatile`オブジェクトのアクセスの順序をどうにかしてくれたりはしません・・・  
すなわち、マルチスレッド時に利用される場合に、`volatile`オブジェクトは可視性（*visibility*）も順序性（*ordering*）も満たしません。

また、そのアクセスの原子性（*atomicity*）に関してもなんら関わっていない事がわかるでしょう。

それらの場合には`std::atomic`を利用しましょう。`volatile`は無力です。

ただ、他のプログラミング言語の中には`volatile`指定の効果に、C++の`volatile`の効果に加えて`std::atomic`の持つ効果がくっついている事があります。例えばC#がそうですが、このような言語においてはその規則の範囲内において期待する効果が得られるかもしれません。  
これが`volatile`の勘違いの原因の一つでもある気がしますが・・・・

#### 実装からの視点

ではこの`volatile`オブジェクトへのアクセス、というのはいつ有効に活用できるのでしょうか？  
おそらく一番のユースケースは、メモリマップドI/O方式を採用している環境においてI/Oアクセスを行う時に使用する変数に付加することです。

```cpp
#include <cstdint>

#define IO_ADDR = 0xffffff;  //どこかのI/Oポートを指すアドレス

int main() {
  volatile std::unit16_t* io_ptr = IO_ADDR;

  *io_ptr = 0x01;       //I/Oに書き込み
  auto data = *io_ptr;  //I/Oから読み込み
  *io_ptr = 0x80;       //I/Oに書き込み
}
```

例えばこのような場合、`IO_ADDR`のアドレスの指す先は外部デバイスのレジスタであり、その領域へのアクセスはI/Oという意味を持ちます（例えばLチカだったり、センサからのデータ取得だったり・・・）。  
しかし上記プログラムはコンパイラから見ると何の意味もない処理でしかなく、最適化の結果`io_ptr`へのアクセスは消去可能です。

このようなI/Oアクセスはこのコード上からは観測不可能な外部デバイスで何かしらの意味を持ち、アクセス及びその順序にもデバイス毎に違った意味がある筈です。  
そのため、そのアクセスを消されたり順序を変えられてしまうと意図通りの結果を得ることができなくなるので、`volatile`の出番というわけです。

この様な意味から考えると、`volatile`なオブジェクト（`volatile`と指定されたメモリ領域）へのアクセスは、CPU内部のキャッシュ機構を通り越してその領域へ直接読み書きする形になっているはずです。そうしないとこのような目的を達せないためです。  
それはすなわち、`volatile`な領域への書き込みはすぐにそのメモリ領域に書き込まれ、読み込みは常にそのメモリ領域から最新のデータを読みだしてくることになります。

これは副次的な効果として、マルチスレッドから`volatile`オブジェクトを通してメモリ領域を読み書きした場合、キャッシュが介在することによって生じる別スレッドでのアクセス順序の逆転や、最適化によって同じ値を読み取り続けるようなことが起こらなくなる可能性があります。

すなわち、一見すると`volatile`指定した変数は可視性と順序性が満たされているかのように見えることがあるかもしれません。  
無論これは保証されるようになったわけではなく、未定義動作の範疇としてたまたまそうなっているだけです。1つでも条件が変われば地獄に落ちるかもしれません。  
結局、`volatile`指定をマルチスレッド処理の同期用などに用いることは間違っています、`std::atomic`を利用しましょう。

この様な事が起こりうるのも`volatile`の効果についての混乱の原因の一つであるのでしょう・・・

### 壊れていたvolatile

### C++20から非推奨になるもの

#### 組み込みのインクリメント演算子

#### 左辺にある非クラス型volatileオブジェクトに対する代入演算子

#### volatile引数を取る関数、戻り値型がvolatileな関数

#### 構造化束縛宣言のvolatile指定

### 検討されていた他の候補

#### メンバ関数のvolatile修飾

### 参考文献
- [P1152R0 : Deprecating volatile](https://wg21.link/p1152r0)
- [P1152R1 : Deprecating volatile](https://wg21.link/p1152r1)
- [P1152R2 : Deprecating volatile](https://wg21.link/p1152r2)
- [P1152R4 : Deprecating volatile](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1152r4.html)
- [volatileが必要な場面を見つけ出す - teratail](https://teratail.com/questions/114172)
- [volatile版atomic操作関数が存在する理由 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entries/2012/07/01)
- [volatile変数とマルチスレッドとの関係についての押し問答（前編） - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20121016/p1)
- [volatile変数とマルチスレッドとの関係についての押し問答（中編） - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20131009/p1)
- [volatile変数とマルチスレッドとの関係についての押し問答（後編） - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20140808/p1)
- [POS03-C. volatile を同期用プリミティブとして使用しない - JPCERT CC](http://www.jpcert.or.jp/sc-rules/c-pos03-c.html)
- [How are side effects and observable behavior related in C++? - stackoverflow](https://stackoverflow.com/questions/13271469/how-are-side-effects-and-observable-behavior-related-in-c)
- [デバイスにアクセスするには | 学校では教えてくれないこと - uQuest](https://www.uquest.co.jp/embedded/learning/lecture13.html)

### 謝辞
- [@yohhoyさん](https://twitter.com/yohhoy/status/1181102762546712578)
- [@yohhoyさん](https://twitter.com/yohhoy/status/1181104668413267973)
- [@yohhoyさん](https://twitter.com/yohhoy/status/1181101292296343552)