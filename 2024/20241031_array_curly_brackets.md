# ［C++］ std::arrayで各要素に対してリスト初期化したいとき

[:contents]

### クラス型を要素に持つ`std::array`の初期化時

`std::array<std::pair<int, int>, N>`のような配列を初期化する場合、何も考えずにこう書こうとすると思います

```cpp
#include <array>
#include <utility>

int main() {
  std::array<std::pair<int, int>, 3> array = {
    {1, 1},
    {2, 2},
    {3, 3}
  };
}
```

しかしこれはエラーになります。一方`std::vector`

### 参考文献

- [c++ - Using std::array with initialization lists - Stack Overflow](https://stackoverflow.com/questions/8192185/using-stdarray-with-initialization-lists)