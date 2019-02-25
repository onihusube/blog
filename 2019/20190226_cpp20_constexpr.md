# C++20のconstexpr世界
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