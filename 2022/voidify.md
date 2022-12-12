# ［C++］voidify() is 何？

[:contents]

### 謎の関数voidify

`voidify()`とは規格書中に登場する謎の関数で、次のように定義されています。

```cpp
template<class T>
constexpr void* voidify(T& ptr) noexcept {
  return const_cast<void*>(static_cast<const volatile void*>(addressof(ptr)));
}
```

つまりは、オブジェクトの配置されているストレージのポインタを`void*`で取得する関数です。まずこの時点で、定義内で謎の2段階キャストをかけている意味が分かりません。

この`voidify()`は、標準ライブラリの関数のうち、未初期化領域にオブジェクトを構築する関数において使用されます。例えば、[`std::construct_at()`](https://cpprefjp.github.io/reference/memory/construct_at.html)ではその効果の指定において次のように使用されています。

```cpp
namespace std {

  template <class T, class... Args>
  constexpr T* construct_at(T* location, Args&&... args) {
    // こう実行したときと同じ効果となる、という指定
    return ::new (voidify(*location)) T(std::forward<Args>(args)...);
  }

}
```

`voidify()`は配置`new`の対象ポインタを取得するのに使用されています。しかし、配置`new`は`::new(location)`で十分なはずで、なぜ`voidify()`を通す必要があるのでしょうか、謎です・・・

### voidify()の引数型と入力

まず上記の`construct_at()`の効果を見て気持ち悪いのは、未初期化領域のポインタ`location`に対して`voidify(*location)`としているところです。

`location`は未初期化領域のはずなので`*location`は未定義動作になります。しかし、これは*equivalent to*という形で指定されていて、実際に未定義動作を起こせという意味ではありません。`voidify(*location)`はその式全体として、`location`のポインタ値を`void*`に変換するという意味でしかありません。

それと関連して、なぜ`voidify()`の入力は`T&`であって`T*`でないのか？という疑問がわきます。`voidify()`の入力が`T*`ならば、そもそも未初期化領域のポインタをデリファレンスするみたいなコードが表面化することもないはずです。

この理由は`voidify()`の中身にもかかってくるので詳細はそちらで語りますが、おそらく`T * const`を`T*`に変換するため（ポインタ型へのトップレベルCV修飾を除去するため）です。

```cpp
int main() {
  int * const volatile p = 0;
  
  using T1 = decltype(*p);    // int&
  using T2 = decltype(&*p);   // int*
}
```

### voidify()の役割

### voidify()の実装

### 反voidify()派閥

### 参考文献

- [Why do we need voidify function template in uninitialized_copy - stackoverflow](https://stackoverflow.com/questions/72761908/why-do-we-need-voidify-function-template-in-uninitialized-copy)
- [[specialized.algorithms]/4 - N4861](https://timsong-cpp.github.io/cppwp/n4861/specialized.algorithms#4)
- [`std::construct_at` - cpprefjp](https://cpprefjp.github.io/reference/memory/construct_at.html)