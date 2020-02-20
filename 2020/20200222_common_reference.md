# ［C++］std::common_reference

C++20より追加された`std::common_reference<T, U>`は型`T, U`両方から変換可能な共通の参照型を求めるメタ関数です。ただしその結果型は必ずしも参照型ではなかったりします。`std::common_type`ではだめだったのでしょうか。

### イテレータの`::value_type`と`::reference`の間にあるもの

### `std::common_reference`

### ～_withなコンセプト定義に現れる`common_reference_with`コンセプト

### 参考文献

- [What is the purpose of C++20 std::common_reference? - stackoverflow](https://stackoverflow.com/questions/59011331/what-is-the-purpose-of-c20-stdcommon-reference)
- [std::common_reference - cpprefjp](https://cpprefjp.github.io/reference/type_traits/common_reference.html)