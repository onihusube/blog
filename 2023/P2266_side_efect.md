# ［C++］暗黙ムーブの副作用

C++23から、参照を返す関数においてローカル変数を直接返すケースがコンパイルエラーとなるようになります。

```cpp
int& f() {
  int n = 10;

  return n; // コンパイルエラー
}

int main() {
  int& r = f();
}
```

これは意図された振る舞いであるとはいえ個別の提案によって導入されたものではなく、一見関係なさそうな別の提案の副作用として導入されました。それは、[P2266R3 Simpler implicit move](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2266r3.html)という提案で、これは`return`文における暗黙ムーブの機会を拡大しようとするものです。

### 暗黙ムーブ

暗黙ムーブとはC++11で許可された戻り値最適化（*Return value optimization*）の一種で、ローカル変数が`return`文でコピーされた返される場合に暗黙的にムーブを行うことでコピーを回避する最適化のことです。

### P2266の概要

### ダングリング参照生成の抑止

### 参考文献

- [P2266R3 Simpler implicit move](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2266r3.html)
- [暗黙のムーブ対象の拡大 - C++20 コア言語機能](https://github.com/onihusube/books/blob/master/cpp20_lang/document.md#%E6%9A%97%E9%BB%99%E3%81%AE%E3%83%A0%E3%83%BC%E3%83%96%E5%AF%BE%E8%B1%A1%E3%81%AE%E6%8B%A1%E5%A4%A7)
- [P2266R0 Simpler implicit move - WG21月次提案文書を眺める（2021年01月）](https://onihusube.hatenablog.com/entry/2021/02/11/153333#P2266R0-Simpler-implicit-move)
