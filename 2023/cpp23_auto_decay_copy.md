# ［C++］ C++23 `auto`によるキャスト

C++23から`auto(x)`の形式のキャストが可能になります。

```cpp
int main() {
  int x = 0;
  int c = auto(x);  // ok、C++23から
}
```

[:contents]

### prvalueへのキャスト

`auto(x)`の形式のキャストは`x`をその型を`decay`した型の値としてキャストするものです。

型の`decay`とはその型からCV/参照修飾を取り除き、配列/関数はそのポインタに変換するものです。配列/関数以外の場合、`auto`によるキャストは`x`をその型の*prvalue*へキャストします。

### プライベートへのアクセス

### 例

### 参考文献

- [`auto(x)`: decay-copy in the language](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p0849r8.html)
- [`std::decay` - cpprefjp](https://cpprefjp.github.io/reference/type_traits/decay.html)
- [`decay-copy` - cpprefjp](https://cpprefjp.github.io/reference/exposition-only/decay-copy.html)