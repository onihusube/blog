# ［C++］C++20のconstexpr

※この内容はC++20から利用可能な情報であり、策定までの間に使用が変更された場合は記述も変更されます。

C++11でconstexprが導入されて以降、STLの全ての関数のconstexpr化を伺うかのようにconstexprは着実に強化されてきました。
C++20ではC++14以来の大幅な強化が行われ、constexprの世界はさらに広がることになります。

### constexprな仮想関数
ついに仮想関数をconstexprの文脈で呼び出せるようになります。初っ端から意味わからないですね・・・。


### dynamic_castとtype_id


### std::is_constant_evaluated()
`std::is_constant_evaluated()`はコンパイル時には`true`を、実行時には`false`を返す関数です。これにより、コンパイル時と実行時でそれぞれ効率的な処理を選択することが可能になります。

```cpp
```

### consteval（immediate function : 即時関数）
constexprを指定した関数は定数実行可能であり、定数式の文脈でコンパイル時に実行される可能性があります。あくまで可能性です。それが本当に定数式として呼ばれたかどうかを知るにはアセンブリを見に行く必要があるでしょう（前述のis_constant_evaluatedを使うこともできますが）。  
なので、必ずコンパイル時実行され、かつコンパイル時に実行されなければコンパイルエラーとなる関数が欲しい場合があります。そこで、consteval指定子が登場しました。

constevalは関数の頭（constexprと同じ位置）に付け、その関数が必ずコンパイル時実行されることを示します。そして、そのような関数は即時関数と呼ばれます。  
以下で紹介するconsteval関数の特徴以外の、例えばconsteval関数内でできる事/出来ない事等の性質はconstexpr関数と同じです（ただし、ここに書かれていない差異はあります）。

```cpp
consteval int square(int n) {
  return n*n;
}

constexpr int sqc = square(10);   //ok. executed at compile time.
int x = 10;
int sqr = square(x);   //compile error! can't executed at compile time.
```
変数`sqc`の初期化はconstexprが付加されていることもあり定数式で実行可能ですので、`square(10)`はコンパイル時に実行され、`sqc == 100`になります。  
一方、`sqr`は別の非constexprな変数`x`を介していることもあり、constexpr実行不可能なのでその時点でコンパイルエラーを発生させます（最適化オプションによってはコンパイラがよきに計らってくれるかもしれませんが・・・）。  
もちろん、consteval関数が定数実行不可能である場合はそれもコンパイルエラーです。

consteval関数はほかのどの関数よりも早く実行されます。すなわち、constexpr関数の実行時点にはconsteval関数の実行は終わっています。  
ただし、consteval関数の中にネストしてconsteval関数が呼び出されている場合はそうではなく、そのように囲んでいるconsteval関数が最終的に定数評価されればエラーにはなりません。

```cpp
consteval int sqrsqr(int n) {
  return sqr(sqr(n)); //この時点では定数評価されてないが、エラーにはならない
}

constexpr int dblsqr(int n) {
  return 2*sqr(n); // compile error! 囲む関数はconstevalではない
}
```

コンパイル時には全て終わっているという性質のため、consteval関数のアドレスを取ることは出来ません。そのような行為を働いた時点でコンパイルエラーとなります。  
また、コンストラクタに付けることは出来ますがデストラクタには付けることができません。コンストラクタに付けた場合はconstexpr指定したのと同じ意味になります。

この即時関数はコンパイラのフロントエンドで処理され、バックエンドはその存在を知りません。すなわち、関数形式マクロ（悪名高いWindows.hのmin,maxマクロのようなプリプロセッサ）の代替として利用することができます。

デメリットとしてはテンプレートメタプログラミングと同じでデバッグが困難であることです。constexpr関数であれば通常の関数としてデバッグ可能ですが、consteval関数は実行時には跡形も残りませんので通常の手段ではデバッグできません。

#### constevalラムダ
consteval指定はラムダ式に対しても行えます。その場合、ラムダ式によって生成される暗黙の関数オブジェクトの関数呼び出し演算子がconsteval関数になります。  
付ける位置はmuttableやconstexprと同じ位置です。

```cpp

auto sq = [](auto n) consteval { return n*n; };

constexpr int sqc = sq(10);
//sqc == 100

```
そのほかの性質はconsteval関数に準じます。

consteval指定されるのはあくまで関数呼び出し演算子なので、このラムダ式を受けている変数自体は即時評価される必要はありません。あくまで関数呼び出しが即時評価されます。

consteval関数はアドレスを取れないことから関数ポインタなどで持ち回れないので、可搬にするのに利用すると良いかもしれません。  
後は通常のローカル関数としての利用でしょうか。

#### consteval仮想関数
仮想関数がconstexpr指定できるようになったので、当然のように？consteval指定することもできます。ただし、constexprが非constexpr仮想関数をオーバーライド出来るのに対して、constevalはconsteval同士の間でしかオーバーライドしたり/されたりしてはいけません。

```cpp
struct polymorphic_base {
  virtual int f() const = 0;
  consteval virtual int g() const { return 0; };
  consteval virtual int h() const { return 1; };
};

struct delived : polymorphic_base {
  //compile error! polymorphic_base::f() is not consteval function.
  consteval int f() const override {
    return 10;
  }

  //ok!
  consteval int g() const override {
    return 20;
  }

  //compile error! missing consteval.
  int h() const override {
    return 30;
  }
};
```
オーバーライド前とオーバーライド後でconsteval指定の有無が一致している必要があります。

### unionのアクティブメンバの切り替え

### try-catch

### STL関数のconstexpr化

#### cmathとcstdlib
一部の数学関数にconstexprが付加されるようになります。

#### algorithm
一部の関数にconstexprが付加されるようになります。

#### 全てのメンバ関数のconstexpr化を達成したクラス
- std::array
- std::pair
- std::tuple
- std::back_insert_iterator
- std::front_insert_iterator
- std::insert_iterator


#### 追加のconstexpr対応（関数/クラス）
- std::complex
  - 四則演算の演算子（自己代入系含む）
  - 代入演算子
  - real(), imag()
  - norm(), conj()
- std::char_traits
  - move()
  - copy()
  - assign()
- std::swap()
- std::exchange()


### 参考文献
- [P1064R0 : Allowing Virtual Function Calls in Constant Expressions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1064r0.html)
- [P0595 : std::is_constant_evaluated()](https://wg21.link/P0595)
- [P1073 : Immediate functions](https://wg21.link/P1073)
- [P0784R5 : More constexpr containers](https://wg21.link/P0784)
- [P0202R3 : Add Constexpr Modifiers to Functions in <algorithm> and <utility> Headers](https://wg21.link/P0202R3)
- [P0415R1 : Constexpr for std::complex](https://wg21.link/P0415R1)
- [C++20 - cpprefjp](https://cpprefjp.github.io/lang/cpp20.html)