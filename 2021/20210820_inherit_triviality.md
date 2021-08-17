#  ［C++］メンバ型のトリビアル性を継承するロストテクノロジー

`std::optional`や`std::variant`は保持する型がトリビアルな型であれば、そのトリビアル性を継承することが規格によって求められており、その実装には非常に難解なテクニックが使用されます。しかし、C++20以降、このテクニックは過去のものとなり忘れ去られていく事でしょう。この記事はそんなロストテクノロジーの記録です。

### メンバ型のトリビアル性を継承、とは？

テンプレートパラメータで指定された型の値をメンバとして保持するときに、そのテンプレートパラメータの型のトリビアル性を継承する事です。

```cpp
template<typename T>
struct wrap {
  T t;
};

template<typename T>
void f(wrap<T>) {
  // 要素型Tがトリビアルであれば
  static_assert(std::is_trivial_v<T>);
  // wrap<T>もトリビアルとなってほしい
  static_assert(std::is_trivial_v<wrap<T>>);
}
```

トリビアルというのは、クラスの特殊メンバ関数がユーザーによって定義されていないことを言います（単純には）。これによって、[*trivially copyable*](https://cpprefjp.github.io/reference/type_traits/is_trivially_copyable.html)ならば`memcpy`できるようになるとか、[*trivially destructible*](https://cpprefjp.github.io/reference/type_traits/is_trivially_destructible.html)ならばデストラクタ呼び出しを省略できる、などの保証が得られます。

上記の`wrpa<T>`型のように単純な型であれば単純にメンバとして保持しただけでも継承していますが、`std::optional`のように複雑な型ではそうは行きません。しかしそれをなんとかする方法がちゃんと存在しています。

### `optional<T>`簡易実装

この記事では`optional`の簡易実装によってメンバ型のトリビアル性継承がどのように行われるのかを見ていきますので、ここでベースとなる簡易実装rev1を書いておきます。

```cpp
template<typename T>
class my_optional {
  bool has_value = false;
  union {
    char dummy;
    T data;
  };

public:

  // デフォルトコンストラクタ
  constexpr my_optional() 
    : has_value(false)
    , dummy{}
  {}

  // 値を受け取るコンストラクタ
  template<typename U=T>
  constexpr my_optional(U&& v)
    : has_value(true)
    , data(std::forward<U>(v))
  {}

  // コピーコンストラクタ
  my_optional(const my_optional& that)
    : has_value(that.has_value)
    , dummy{}
  {
    if (that.has_value) {
      new (&this->data) T(that.data);
    }
  }

  // ムーブコンストラクタ
  my_optional(my_optional&& that)
    : has_value(that.has_value)
    , dummy{}
  {
    if (that.has_value) {
      new (&this->data) T(std::move(that.data));
    }
  }

  // コピー代入演算子
  my_optional& operator=(const my_optional& that) {
    auto copy = that;
    *this = std::move(copy);
    
    return *this;
  }

  // ムーブ代入演算子
  my_optional& operator=(my_optional&& that) {
    if (this->has_value) {
      this->data.~T();
    }

    this->has_value = that.has_value;

    if (that.has_value) {
      new (&this->data) T(std::move(that.data));
    }

    return *this;
  }

  // デストラクタ
  ~my_optional() {
    if (has_value) {
      this->data.~T();
    }
  }
};
```

この実装はとりあえず`optional`っぽい働きはします。C++11で制限解除された共用体はそのメンバ型が非トリビアルな特殊メンバ関数を持つとき、対応する特殊メンバ関数が`delete`されます。そのため、それをラップする外側の型はそれを書いておく必要があります。`optional`は遅延構築や任意タイミングでの無効値への切り替えが可能であり、それを実現するためには共用体を利用するのが最短でしょう。なお、状態を変化させるのは他のメンバ関数や代入演算子で行いますが、ここではそれは重要ではないので省略します。また、`noexcept`については考えないことにします。

### デストラクタ

簡易実装rev1はデストラクタがトリビアルではありません。`T`が*trivially destructible*であるならばデストラクタ呼び出しは省略できるので、`my_optional`のデストラクタもトリビアルに出来そうです。そしてそれは、C++17の世界で`my_optional`が`constexpr`となるための必要十分条件です。

デストラクタのトリビアル性継承は、次のように実装できます。

```cpp
// デストラクタがトリビアルでない場合のストレージ
template<typename T, bool = std::is_trivially_destructible_v<T>>
struct optional_storage {
  bool has_value = false;
  union {
    char dummy;
    T data;
  };

  // デストラクタは常に非トリビアルでdeleteされているので定義する
  ~optional_storage() {
    if (has_value) {
      this->data.~T();
    }
  }
};

// デストラクタがトリビアルである場合のストレージ
template<typename T>
struct optional_storage<T, true> {
  bool has_value = false;
  union {
    char dummy;
    T data;
  };

  // デストラクタはトリビアルであり常にdeleteされないので、宣言すらいらない
};

template<typename T>
class my_optional : private optional_storage<T> {
public:

  // 他略

  // デストラクタ、この宣言も実はいらない
  ~my_optional() = default;
};
```

`optional_storage<T>`というクラスにデータを保持する部分を移管し、`optional_storage<T>`は`T`が*trivially destructible*である場合とない場合でテンプレートの部分特殊化によって実装を切り替えます。そしてその実装では、`T`が*trivially destructible*である場合はデストラクタはトリビアルに定義され（ユーザー定義されず）、`T`が*trivially destructible*でない場合に引き続きユーザー定義されます。これらの選択は与えられた型`T`によって自動的に行われ、`my_optional<T>`は`T`の*trivially destructible*性を継承します。


```cpp
int main() {
  // パスする
  static_assert(std::is_trivially_destructible_v<my_optional<int>>);
  static_assert(std::is_trivially_destructible_v<my_optional<std::string>> == false);
}
```

簡易実装rev2は次のようになりました。

```cpp
// デストラクタがトリビアルでない場合のストレージ
template<typename T, bool = std::is_trivially_destructible_v<T>>
struct optional_storage {
  bool has_value = false;
  union {
    char dummy;
    T data;
  };

  // デストラクタは常に非トリビアルでdeleteされているので定義する
  ~optional_storage() {
    if (has_value) {
      this->data.~T();
    }
  }
};

// デストラクタがトリビアルである場合のストレージ
template<typename T>
struct optional_storage<T, true> {
  bool has_value = false;
  union {
    char dummy;
    T data;
  };

  // デストラクタはトリビアルであり常にdeleteされないので、宣言すらいらない
};

template<typename T>
class my_optional : private optional_storage<T> {
public:

  // デフォルトコンストラクタ
  constexpr my_optional() 
    : has_value(false)
    , dummy{}
  {}

  // 値を受け取るコンストラクタ
  template<typename U=T>
  constexpr my_optional(U&& v)
    : has_value(true)
    , data(std::forward<U>(v))
  {}

  // コピーコンストラクタ
  my_optional(const my_optional& that)
    : has_value(that.has_value)
    , dummy{}
  {
    if (that.has_value) {
      new (&this->data) T(that.data);
    }
  }

  // ムーブコンストラクタ
  my_optional(my_optional&& that)
    : has_value(that.has_value)
    , dummy{}
  {
    if (that.has_value) {
      new (&this->data) T(std::move(that.data));
    }
  }

  // コピー代入演算子
  my_optional& operator=(const my_optional& that) {
    auto copy = that;
    *this = std::move(copy);
    
    return *this;
  }

  // ムーブ代入演算子
  my_optional& operator=(my_optional&& that) {
    if (this->has_value) {
      this->data.~T();
    }

    this->has_value = that.has_value;

    if (that.has_value) {
      new (&this->data) T(std::move(that.data));
    }

    return *this;
  }
};
```

### コピー/ムーブコンストラクタ


### デフォルトコンストラクタ

`optional`はその実装の都合上、デフォルトコンストラクタをトリビアルにすることができません。そのため`optional`以外を例にすると、次のように書くことで要素型の*trivially default constructible*性を継承できます。

```cpp
template<typename T>
class wrap {
  T t;  // 初期化しない

public:
  wrap() = default;
};
```

他のコンストラクタが存在するとデフォルトコンストラクタは暗黙`delete`されるため、`default`で書いておきます。この時、メンバに持っている`T`のオブジェクトをに対してデフォルトメンバ初期化してしまうとトリビアルにならないので注意が必要です。

```cpp
int main() {
  static_assert(std::is_trivially_default_constructible_v<wrap<int>>);  // パスする
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/tgDiKULdlA3F7SUV)

またおそらく、このような単純な型ではその他の部分のトリビアル性継承時にも先程までのような謎のテクニックを駆使する必要はないはずです。

### C++20からは・・・

### なぜにトリビアル？

型（の特殊メンバ関数）がトリビアルであることは、ABIにとってとても重要です。

例えば、型`T`が*trivially default constructible*であれば`T t;`のような変数宣言時に初期化処理を省略することができ、*trivially destructible*であれば`t`の破棄時（スコープ外になる時）にデストラクタ呼び出しを省略できます。この2つのトリビアル性は`std::vector`などコンテナに格納した際にも活用されます。そして、型`T`のコピー/ムーブコンストラクタがトリビアルであれば、`T`のコピーは`memcpy`相当の簡易な方法によってコピーすることができ、それは代入演算子でも同様です。

もしそれらがトリビアルでは無い時、コンパイラはそれらの呼び出しが必要になる所で必ずユーザー定義の関数を呼び出すようにしておく必要があります。それが実質的にトリビアル相当のことをしていたとしても、トリビアルでない限りは何らかの関数呼び出しが必要になります。もっともそのような場合、インライン展開をはじめとする最適化によってそのような呼び出しは実質的に省略されるでしょう。

より重要なのは（あるいは問題となるのは）、トリビアルでない型のオブジェクトが関数引数として値渡しされる時、あるいは戻り値として直接返される時、静かなオーバーヘッドを埋め込んでしまうことです。

どういうことかというと、`T`のオブジェクトを値渡しした時に、`T`がトリビアル型であればレジスタに配置されて渡される（可能性がある）のに対し、`T`が非トリビアル型であるとスタック上に配置したオブジェクトのポインタ渡しになります。これはC++コード上からは観測できず、出力されたアセンブラを確認して初めて観測できます。

```cpp
struct trivial {
  int n;
};

struct non_trivial {
  int n;

  ~non_trivial() {}
};

int f(trivial t);

int f(non_trivial t);

trivial g1() {
  return {20};
}

non_trivial g2() {
  return {20};
}

void h(int);

int main() {
  int n1 = f(trivial{10});
  int n2 = f(non_trivial{10});
}
```
- [godbolt](https://godbolt.org/z/nv5TTMrsh)


GCCのものをコピペすると、次のようなコードが生成されています。

```asm
g1():
        mov     eax, 20
        ret
g2():
        mov     DWORD PTR [rdi], 20
        mov     rax, rdi
        ret
main:
        sub     rsp, 24
        # f(trivial)の呼び出し
        mov     edi, 10
        call    f(trivial)
        # f(not_trivial)の呼び出し
        lea     rdi, [rsp+12]
        mov     DWORD PTR [rsp+12], 10
        call    f(non_trivial)
        # main()の終了
        xor     eax, eax
        add     rsp, 24
        ret
```

godbolt上で見ると対応がより分かりやすいかと思います。

`f(trivial)`の呼び出し時は`edi`レジスタ（32bit）に即値`10`を配置して（`trivial`型を構築して）呼び出しているのに対し、`f(not_trivial)`の呼び出し時は、`rdi`レジスタ（64bit）に`rsp`（スタックポインタ）の値に`12`を足したアドレスをロードし、その領域に即値`10`を配置して（`non_trivial`型を構築して）から呼び出しを行なっています。  
`rdi`レジスタはx64の呼び出し規約において整数/ポインタ引数に対して最初に使用されるレジスタであり、`edi`レジスタは`rdi`の下位32bitの部分で役割は同様です。したがって、`f(trivial)`の呼び出しでは`trivial`型をレジスタに構築して渡しているのに対して、`f(not_trivial)`の呼び出し時は`non_trivial`型をスタック上に配置してそのポインタを渡しています。

今度は、`g1(), g2()`の定義について生成されたコードを見てみると、`trivial`型を返す`g1()`は`eax`レジスタ（32bit）に即値`20`を配置して（`trivial`型を構築して）`return`しているのに対し、`non_trivial`型を返す`g2()`は`rdi`レジスタ（64bit）の値をポインタとして読みその領域に即値`20`を配置し（`non_trivial`型を構築し）、`rax`レジスタ（64bit）に`rdi`の値をコピーしてから`return`しています。  
`rax`レジスタはx64の呼び出し規約において戻り値を返すのに使用されるレジスタであり、`eax`はその下位32bit部分で役割は同様です。したがって、`g1()`の`return`では`trivial`型をレジスタに構築して返しているのに対して、`g2()`の`return`では`non_trivial`型をスタック上に配置してそのポインタを渡しています。

MSVCは`f()`の呼び出しがどちらも同じコードを生成していますが、`g1(), g2()`はGCC/clangと同じことをしているのが分かります。

このトリビアル型と非トリビアル型の扱いの差異は、ABIによって規定され要求されている事です（MSVCとGCC/clangの差異も使用しているABIの違いによります）。そしておそらく、C++における各種トリビアル性はこうしたABIからの要請によって生まれた規定でしょう。また、ABIの規定するトリビアルな型とは

有名な所では、`std::unique_ptr`がトリビアル型ではないために生ポインタと比較した時にこの種のオーバーヘッドを発生させてしまっています。このことによるオーバーヘッドは微々たるものですが、例えばそれがヘビーループの中で起こっていると問題となるかもしれません。しかもこの事は非常に認識しづらく、よく知られてはいません。このため、`std::optional/std::variant`に見られるように、標準ライブラリのクラス型はトリビアル性に注意を払って設計されます（あるいは、されるようになりました）。

とはいえ、MSVC ABIにおける`std::span`のように（`std::span`は常にトリビアル型）、ABIの別の事情によってこの種のオーバーヘッドが発生してしまっていたりと、ABIにまつわる問題は複雑で把握しづらいものがあります・・・

### 各種ABIでのトリビアル

#### Itanium C++ ABI

> A type is considered non-trivial for the purposes of calls if:
>
> - it has a non-trivial copy constructor, move constructor, or destructor, or  
> - all of its copy and move constructors are deleted.


さらにすぐ下にはこう書かれています。

> This definition, as applied to class types, is intended to be the complement of the definition in [class.temporary]p3 of types for which an extra temporary is allowed when passing or returning a type. A type which is trivial for the purposes of the ABI will be passed and returned according to the rules of the base C ABI, e.g. in registers; often this has the effect of performing a trivial copy of the type.

#### System V AMD64 ABI

#### Windows x64 ABI (MSVC ABI)

MSVC ABIではトリビアルという言葉は出現しません。

### 参考文献

- [C++17 optionalの実装について - 茅の下](https://ryooooooga.hateblo.jp/entry/2016/07/10/225710)
- [C++11 共用体の制限解除 - cpprefjp](https://cpprefjp.github.io/lang/cpp11/unrestricted_unions.html)
- [P0848R0 Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0848r0.html)
- [P0848R3 Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0848r3.html)
- [Conditionally Trivial Special Member Functions - C++ Team Blog](https://devblogs.microsoft.com/cppblog/conditionally-trivial-special-member-functions/)
- [C++20 コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [Why does std::tuple break small-size struct call convention optimization in C++? - stackoverflow](https://stackoverflow.com/a/63723752)
- [`std::span` is not zero-cost because of the ms abi. - Developer Community](https://developercommunity.visualstudio.com/t/std::span-is-not-zero-cost-because-of-th/1429284)
- [Itanium C++ ABI](https://itanium-cxx-abi.github.io/cxx-abi/abi.html)
- [System V Application Binary Interface AMD64 Architecture Processor Supplement (With LP64 and ILP32 Programming Models) Version 1.0](https://github.com/hjl-tools/x86-psABI/wiki/x86-64-psABI-1.0.pdf)
- [x64 での呼び出し規則 - Microsoft Docs](https://docs.microsoft.com/ja-jp/cpp/build/x64-calling-convention?view=msvc-160)