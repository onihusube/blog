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

### voidify()の役割

`voidify()`がやっていることは、ポインタ型を`void*`に変換することです。ではなぜこれが必要なのか？というと、オーバーロードされていないグローバルな`operator new()`を確実に呼び出すためです。

`voidify()`が使われているところでは、`::new (voidify(...)) T(...)`のようにして`voidify()`の結果のポインタを`::operator new()`に渡してその両機に`T`のオブジェクトを配置`new`しています。まず、`::new()`としていることでグローバルなもの（クラススコープでオーバーロードされたものではない）を呼び出そうとしています。

この後で問題となるのはグローバルな`operator new`もオーバーロードされている可能性があることで、特に特定の型のポインタ型に特殊化されている可能性があります。

```cpp
#include <new>
#include <iostream>
#include <memory>

struct S {
  int n;
};

// 特殊化された配置new演算子
[[nodiscard]]
void* operator new(std::size_t size, S* ptr) noexcept {
  std::cout << "call S specific operator new()\n";
  return ptr;
}

int main() {
  // Sの場合
  S s{ .n = 1 };
  std::destroy_at(&s);

  // S*に特殊化されたoperator newが使用される
  S* sp = ::new(&s) S{10};

  std::cout << sp->n << '\n';

  // 非Sの場合
  int n = 1;
  std::destroy_at(&n);

  // デフォルトのoperator newが使用される
  int* ip = ::new(&n) int{};
  
  std::cout << *ip << '\n';
}
```

出力例

```
call S specific operator new()
10
0
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/VTKjAuR1EiKFpTu0)

この時に、配置`new`の入力ポインタを`void*`にするとこのような変な`new`演算子オーバーロードを弾くことができます。

```cpp
int main() {
  S s{ .n = 1 };
  std::destroy_at(&s);

  S* sp = ::new((void*)&s) S{10};

  std::cout << sp->n << '\n';
}
```

出力例

```
0
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/h2AgmrEnHKkxPykr)

本来配置`new`を行う`::operator new()`のオーバーロードは許可されておらず、`void*`でのオーバーロードは多重定義エラーとなるはずです。しかし、特定の型のポインタ`T*`に特殊化したものはコンパイルエラーにはならず、この例のように実行できてしまいます（当然未定義動作ですが）。

`voidify()`が使用されるところでは、`std::construct_at()`がそうであるように、ポインタの指す領域に対して新しいオブジェクトを構築することを意図していて、`voidify()`はその効果の説明のために使用されます。`voidify()`の使用は、それらの関数の呼び出しがこのような変なオーバーロードを呼び出さないこと（それによって未定義動作とならないこと）を表明し、なおかつ、実装が同様に変なオーバーロードを呼び出さないことを要求している、と思われます。

### voidify()の実装

`voidify()`の内部でやっていることは、その役割のために必要な任意のポインタから`void*`へのキャスト実装です。先程の例のように、`(void*)`ないし`static_cast<void*>()`ではダメなのでしょうか？

その前に、使用側のコード（上記の`construct_at()`の効果）を見て凄く気になる点を解消しておきます。それは、未初期化領域のポインタ`location`に対して`voidify(*location)`としているところです。

`location`は未初期化領域のはずなので`*location`は未定義動作になるように思えて、とても奇妙です。しかし、これは規格中で*equivalent to*という形で指定されていて、実際に未定義動作を起こせという意味ではありません。`voidify(*location)`はその式全体として、`location`のポインタ型を`void*`に変換するという意味でしかありません。

それと関連して、なぜ`voidify()`の入力は`T&`であって`T*`でないのか？という疑問がわきます。`voidify()`の入力が`T*`ならば、そもそも未初期化領域のポインタをデリファレンスするみたいなコードが表面化することもないはずです。結局、`voidify(*location)`はなぜこうなっていてこれは何をしているのでしょうか？

この理由はおそらく、`T * const (volatile)`を`T*`に変換するため（ポインタ型のトップレベルCV修飾を除去するため）です。

```cpp
int main() {
  int * const volatile p = 0;
  
  using T1 = decltype(*p);    // int&
  using T2 = decltype(&*p);   // int*

  int* p2 = p;  // ok
}
```

このように、ポインタ型のトップレベル（`*`の右側）CV修飾はデリファレンスしてからアドレスを取得すると外すことができます。

ところで、これは実は単に`T*`のポインタにコピーしても同じことができます。そうしていないのはおそらく1行で記述したいためで、同様のことをするキャストを使用しないのは`voidify()`の入力で複雑長大なキャストを回避したい（`T * const volatile`みたいなのから`T*`を求めるにはメタ関数を一つかます必要があります）、などの理由によるものでしょう。

脇道に逸れたようですが、実はこのことも`voidify()`実装の一部です。これを念頭に置いて、`voidify()`の本体に戻ります。

```cpp
template<class T>
constexpr void* voidify(T& ptr) noexcept {
  // このキャスト2段重ねは何？
  return const_cast<void*>(static_cast<const volatile void*>(addressof(ptr)));
}
```

使用時に`voidify(*location)`としていることでポインタ入力からトップレベルのCV修飾を取り除いているので、残るのは`T`に指定されるCV修飾のみで、それはデリファレンスした後でも伝播されるものであり、そこからポインタを取得しても残っています。ここで`addressof()`を使用しているのは、その意図通りに`&`演算子のオーバーロードを回避して確実にポインタを取得するためです。

その後、`T`にCV修飾がある場合に、`static_cast<void*>()`の形のキャストはできません。なぜなら、`static_cast`はCV修飾を取り除けないからです。一方で、`static_cast`はCV修飾を追加することはできるため、`static_cast<const volatile void*>()`は`addressof(ptr)`の結果のポインタ型がなんであれ`const volatile void*`にキャストすることができます。

ここまで来れば残りの`const_cast<void*>()`はそこからCV修飾を外して`void*`にキャストしているだけであることがわかるでしょう。

すなわち、このキャスト2段重ねは入力の（トップレベルのCV修飾が既にない）ポインタ型を、そのCV修飾に関わらず`void*`にキャストするためのものです。

実はここ`(void*)`ならできてしまうのですが、それは多分標準ライブラリでは好まれないでしょう。また、このキャスト2段重ねは特別扱いなしで定数式で実行可能です。

そのようなポインタがここに渡ってくる場合はいつか？というと、外側の関数（`std::construct_at`など）の入力に`const (volatile) T*`みたいなのが渡された場合です。`std::construct_at`をはじめとする未初期化領域にオブジェクト構築を行う関数は、この場合でも正しく動作します。

```cpp
#include <new>
#include <iostream>
#include <memory>

int main() {
  const int n = 0;
  
  // const int*を渡しても動作する
  std::destroy_at(&n);
  const int* p = std::construct_at(&n, 10);

  std::cout << *p << '\n';
}
```

ではこの場合にこのポインタの領域にオブジェクト構築することは正しい振る舞いなのでしょうか？標準ライブラリがそう動作しているのだから正しいに決まっていますが、納得できる理由を提供するのであれば、次のようになるでしょうか。

`const (volatile) T*`のようにポインタの参照先に対するCV修飾は、参照先のオブジェクトに対する修飾です（領域ではなく）。そして、`std::construct_at`をはじめとする関数群は未初期化領域にオブジェクトを構築することを役割としており、期待される事前条件として（これは明文化されていませんが）入力の領域にはオブジェクトがまだ構築されていないことがあります。つまり、これらの関数がその役割を遂行する際には、CV修飾を適用すべきオブジェクトはまだ無いためCV修飾は意味をなさず、これらの関数がその領域にオブジェクトを構築して初めてそのCV修飾は意味を持ちます。したがって、これらの関数が`const (volatile) T*`な領域に行うことはそのCV修飾の意味を犯してはいないのです。

また、デストラクタがトリビアルな型であれば事前に構築されていても上書き構築が行えるのですが、その場合でも`const`オブジェクトに対してデストラクタは呼べるので別段問題はないでしょう。

### 反voidify()派閥

### 参考文献

- [Why do we need voidify function template in uninitialized_copy - stackoverflow](https://stackoverflow.com/questions/72761908/why-do-we-need-voidify-function-template-in-uninitialized-copy)
- [[specialized.algorithms]/4 - N4861](https://timsong-cpp.github.io/cppwp/n4861/specialized.algorithms#4)
- [`std::construct_at` - cpprefjp](https://cpprefjp.github.io/reference/memory/construct_at.html)
- [operator new/delete | Programming Place Plus　C++編【言語解説】　第３６章](https://programming-place.net/ppp/contents/cpp/language/036.html)
- [How could I sensibly overload placement operator new? - stackoverflow](https://stackoverflow.com/questions/3675059/how-could-i-sensibly-overload-placement-operator-new)