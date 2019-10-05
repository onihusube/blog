# ［C++］volatile

※この記事は[C++20を相談しながら調べる会 #3](https://cpp20survey.connpass.com/event/147002/)の成果として書かれました。

C++20より、一部の`volatile`の用法が非推奨化されます。提案文書は「Deprecating volatile」という壮大なタイトルなのでvolatileそのものが無くなるのかと思ってしまいますがそうではありません。  
この提案文書をもとに何が何故無くなるのかを調べてみます・・・

### そもそもvolatileってなんだろう・・・

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
- [https://yohhoy.hatenadiary.jp/entries/2012/07/01 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entries/2012/07/01)