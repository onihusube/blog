# ［C++］C++20のconstexpr
C++11でconstexprが導入されて以降、STLの全ての関数のconstexpr化を伺うかのようにconstexprは着実に強化されてきました。
C++20ではC++14以来の大幅な強化が行われ、constexprの世界はさらに広がることになります。

### constexprな仮想関数
ついに仮想関数をconstexprの文脈で呼び出せるようになります。初っ端から意味わからないですね・・・。


### unionのアクティブメンバの切り替え



### std::is_constant_evaluated()
`std::is_constant_evaluated()`はコンパイル時には`true`を、実行時には`false`を返す関数です。これにより、コンパイル時と実行時でそれぞれ効率的な処理を選択することが可能になります。

```cpp
```

### consteval（即時関数）
constexprを指定した関数は定数実行可能であり、定数式の文脈でコンパイル時に実行される可能性があります。あくまで可能性です。それが本当に定数式として呼ばれたかどうかを知るにはアセンブリを見に行く必要があるでしょう（前述のis_constant_evaluatedを使うこともできますが）。  
なので、必ずコンパイル時実行され、かつコンパイル時に実行されなければコンパイルエラーとなる関数が欲しい場合があります。そこで、consteval指定子が登場しました。

constevalは関数の頭（constexprと同じ位置）に付け、その関数が必ずコンパイル時実行されることを示します。そして、そのような関数は即時関数と呼ばれます。

```cpp
consteval int square(int n) {
    return n*n;
}

constexpr int sqc = square(10);   //ok. executed at compile time.
int x = 10;
int sqr = square(x);   //compile error! can't executed at compile time.
```
変数`sqc`の初期化はconstexprが付加されていることもあり定数式で実行可能ですので、`square(int)`はコンパイル時に実行され、`sqc == 100`0になります。  
一方、`sqr`は別の非constexprな変数`x`を介していることもあり、constexpr実行不可能なのでその時点でコンパイルエラーを発生させます（最適化オプションによってはコンパイラがよきに計らってくれるかもしれませんが・・・）。  
もちろん、consteval関数が定数実行不可能である場合はそれもコンパイルエラーです。

consteval関数はほかのどの関数よりも早く実行されます。すなわち、constexpr関数の実行時点にはconsteval関数の実行終わっています。ただし、consteval関数の中にネストしてconsteval関数が呼び出されている場合はその限りではありません。そのように囲んでいるconsteval関数が最終的に定数評価されればエラーにはなりません。
```cpp
consteval int sqrsqr(int n) {
  return sqr(sqr(n)); // Not a constant-expression at this  point,
}                     // but that's okay.

constexpr int dblsqr(int n) {
  return 2*sqr(n); // Error: Enclosing function is not
}                  // consteval.
```

この様な即時関数はコンパイラのフロントエンドで処理され、バックエンドはその存在を知る必要がありません。すなわち、関数形式マクロの代替として利用することができます。

デメリットとしてはテンプレートメタプログラミングと同じでデバッグが困難であることです。constexpr関数であれば通常の関数としてデバッグ可能ですが、consteval関数は実行時には跡形も残りませんので通常の手段ではデバッグ不可能です。

### try-catch

### dynamic_castとtype_id

### STL関数のconstexpr化

#### cmathとcstdlib
一部の数学関数にconstexprが付加されるようになります。

#### algorithm

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
- [P0595 : std::is_constant_evaluated()](https://wg21.link/P0595)
- [P1073 : Immediate functions](https://wg21.link/P1073)
- [P0784R5 : More constexpr containers](https://wg21.link/P0784)
- [P0202R3 : Add Constexpr Modifiers to Functions in <algorithm> and <utility> Headers](https://wg21.link/P0202R3)
- [P0415R1 : Constexpr for std::complex](https://wg21.link/P0415R1)
- [C++20 - cpprefjp](https://cpprefjp.github.io/lang/cpp20.html)