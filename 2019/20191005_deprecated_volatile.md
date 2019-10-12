# ［C++］Deprecating volatile

※この記事は[C++20を相談しながら調べる会 #3](https://cpp20survey.connpass.com/event/147002/)の成果として書かれました。

C++20より、一部の`volatile`の用法が非推奨化されます。提案文書は「[Deprecating volatile](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1152r4.html)」という壮大なタイトルなのでvolatileそのものが無くなるのかと思ってしまいますがそうではありません。  
この提案文書をもとに何が何故無くなるのかを調べてみます・・・

### そもそもvolatileってなんだろう・・・

長くなったので別記事に分離しました。以下でお読みください。


[https://onihusube.hatenablog.com/entry/2019/10/09/184906:embed:cite]


C++における`volatile`の意味とは

- `volatile`指定されたメモリ領域はプログラム外部で利用されうるという事をコンパイラに通知
    - 特に、そのような領域は外部から書き換えられうる
- そして、実装は必ずしもそれを検知・観測できない

そして、`volatile`の効果は

- シングルスレッド実行上において
- `volatile`オブジェクトへのアクセス（読み/書き）の順序を保証し
- `volatile`オブジェクトへのアクセスに関してはコンパイラの最適化対象外となる

となります。

そして、マルチスレッドにおいての同期用に使用すると未定義動作の世界に突入します。マルチスレッド時のための仕組みにはなっていません。

### volatileの正しい用法

- 共有メモリ（not スレッド間）
    - 共有相手はGPU等の外部デバイスや別プロセス、OSカーネルなど
    - 特に、time-of-check time-of-use (ToCToU)を回避する正しい方法の一つ
- シグナルハンドラ内
    - シグナルハンドラ内で行えることは多くなく、共有メモリにシグナルが発生したことを書きこみ速やかに処理を終えることくらい
    - そのような共有メモリに`volatile static`変数を利用できる
- `setjmp`/`longjmp`
    - `setjmp`の2回の呼び出しの間で（つまり、`longjmp`によって戻ってきた後でも）、変数が変更されないようにするのに使用する
- プログラム外部で変更されうるメモリ領域
    - メモリマップドI/Oにおける外部I/Oデバイスのレジスタなど
    - コンパイラはこのようなメモリ領域がプログラム内でしか使われていない事を仮定できない
- 無限ループにおいて副作用を示す
    - 無限ループが削除されてしまわないために`volatile`オブジェクトを使用する
    - これは`std::atomic`や標準ライブラリのI/O操作によって代替可能
- `volatile`の効果を得るためのポインタキャスト
    - `volatile`なのはデータではなくコードである、という哲学の下で一般に利用されている
    - `volatile`へのキャストが有効なのはポインタ間のみであり、オブジェクト間で非`volatile`から`volatile`付の型にキャストしても`volatile`の効果は得られない
- [*Control dependencies*](https://en.wikipedia.org/wiki/Dependence_analysis#Control_dependencies)を保護する
    - コンパイラの最適化によってこのような依存関係が削除されないようにする
- `memory_order_consume`のいくつかの実装の保護
    - コンパイラの最適化によってデータ依存の順序が崩されないようにする？

この様な正しい用途の中には、`volatile`の代替となる方法がインラインアセンブリを使う（コンパイラへの指示 or 機械語命令の直接出力）しか無いものがあります。  
そのような方法には移植性がありません・・・

### この提案（P1152R4）の目的

この提案の目的は、C++標準内で間違っている`volatile`の利用を正すことにあります。  
`volatile`が意味がないから非推奨とか、マルチスレッド利用について混乱の下だから非推奨とか言う事ではありません。

そのため、`volatile`の正しい用法のための文言には一切手を付けていません。たとえそこにいくつかの問題がある事が分かっていても、この提案ではその修正さえもしていません。


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
- [Time of check to time of use - Wikipedia](https://ja.wikipedia.org/wiki/Time_of_check_to_time_of_use)
- [setjmp - cppreference.com](https://ja.cppreference.com/w/cpp/utility/program/setjmp)
- [Memory corruption due to word sharing. - Linus Torvalds. GCC mailing list](https://gcc.gnu.org/ml/gcc/2012-02/msg00027.html)
- [C++0xのメモリバリアをより深く解説してみる - yamasaのネタ帳](https://yamasa.hatenablog.jp/entry/20090929/1254237835)