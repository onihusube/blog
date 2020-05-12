# ［C++］モジュールとプリプロセス

C++20より使用可能になるはずのモジュールは3つの新しいトークンによって記述されますが、それらのトークンは必ずしも予約語ではなく、コンパイラによる涙ぐましい努力によって特殊な扱われ方をしています。全部入りを書くと次のようになります。

```cpp
module;
#include <iosream>
export module sample_module;

import <vector>;
export import <type_traits>;

export int f();

module : private;

int f() {
  return 20;
}
```

これは例えばプリプロセス後（翻訳フェース4の後）に次のようになります。

```cpp
__module_keyword;
#include <iosream>
__export_keyword __module_keyword sample_module;

__import_keyword <vector>;
__export_keyword __import_keyword <type_traits>;

// export宣言はプリプロセッシングディレクティブでは無い
export int f();

__module_keyword : private;

int f() {
  return 20;
}
```

これは実際には実装定義なのでどう置き換えられるのかは不明ですが、これら置換されている`module, import, export`トークンの現れていた所とその行は実はプリプロセッシングディレクティブとして処理され、その結果としてこのような謎のトークンが生成されます。そして、C++のコードとしてはこれらの謎のトークンによるものをモジュール宣言やインポート宣言などとして扱います。

### `module`トークンの扱い
### `import`トークンの扱い
### `export`トークンの扱い

### 何故？

### サンプルコード

### 参考文献

- [P1857R3 Modules Dependency Discovery](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p1857r3.html)
- [P1703R1 Recognizing Header Unit Imports Requires Full Preprocessing](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1703r1.html)