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

このトリビアル型と非トリビアル型の扱いの差異は、ABIによって規定され要求されている事です（MSVCとGCC/clangの差異も使用しているABIの違いによります）。そしておそらく、C++における各種トリビアル性はこうしたABIからの要請によって生まれた規定でしょう。

有名な所では、`std::unique_ptr`がトリビアル型ではないために生ポインタと比較した時にこの種のオーバーヘッドを発生させてしまっています。このことによるオーバーヘッドは微々たるものですが、例えばそれがヘビーループの中で起こっていると問題となるかもしれません。しかもこの事は非常に認識しづらく、よく知られてはいません。このため、`std::optional/std::variant`に見られるように、近年（C++17以降くらい）の標準ライブラリのクラス型はトリビアル性に注意を払って設計されるようになりました。

とはいえ、MSVC ABIにおける`std::span`のように（`std::span`は常にトリビアル型）、ABIの別の事情によってこの種のオーバーヘッドが発生してしまっていたりと、ABIにまつわる問題は複雑で把握しづらいものがあります・・・

### 各種ABIでのトリビアル

#### Itanium C++ ABI

[1.1 Definitions *non-trivial for the purposes of calls*](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#definitions)で定義されています。

> A type is considered non-trivial for the purposes of calls if:
>
> - it has a non-trivial copy constructor, move constructor, or destructor, or  
> - all of its copy and move constructors are deleted.

これはItanium C++ ABIの定める非トリビアルな型の定義で、以下のどちらかの時にクラス型は非トリビアルとして扱われます

- コピー/ムーブコンストラクタおよびデストラクタのいずれか一つでも非トリビアルである
- 全てのコピー/ムーブコンストラクタが`delete`されている

さらにすぐ下にはこう書かれています。

> This definition, as applied to class types, is intended to be the complement of the definition in [class.temporary]p3 of types for which an extra temporary is allowed when passing or returning a type. A type which is trivial for the purposes of the ABI will be passed and returned according to the rules of the base C ABI, e.g. in registers; often this has the effect of performing a trivial copy of the type.

この定義に該当する非トリビアルな型は、引数として渡すときと戻り値として返す時に一時オブジェクトを作成して返すことが許容され、そうでない型はレジスタ等で受け渡される、みたいな事を言っています。これがまさに先ほどの生成コードに現れている静かなオーバーヘッドの正体であり根拠です。  
「non-trivial for the purposes of calls」という用語からもトリビアルという性質がABI（特に関数呼び出しの都合）からきている事が窺えます。

そして、この定義を用いて、関数呼び出し時の非トリビアル型引数について次のように規定されています（[3.1.2.3 Non-Trivial Parameters](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#non-trivial-parameters)）

> If a parameter type is a class type that is non-trivial for the purposes of calls, the caller must allocate space for a temporary and pass that temporary by reference. Specifically:
> 
> - Space is allocated by the caller in the usual manner for a temporary, typically on the stack.
> - The caller evaluates the argument in the space provided.
> - The function is called, passing the address of the temporary as the appropriate argument. In the callee, the address passed is used as the address of the parameter variable.
> - If the type has a non-trivial destructor, the caller calls that destructor after control returns to it (including when the caller throws an exception).
> - If necessary (e.g. if the temporary was allocated on the heap), the caller deallocates space after return and destruction.

意訳

> 非トリビアルな型のオブジェクトを関数引数として渡す時、呼び出し元が一時オブジェクトを作成しその参照を渡さなければならない。具体的には
> 
> - 呼び出し元は、一時オブジェクトを作成する通常の方法で、一般的にはスタック上に領域を確保し構築する
> - 呼び出された側（関数内）は、その提供された領域で引数を評価する
> - 関数は、その一時オブジェクトのアドレスを適正な引数として受け取って呼び出される。呼び出された側では渡されたアドレスが引数変数のアドレスとして使用される
> - 型が非トリビアルデストラクタを持つ場合、呼び出し側は関数がリターンした後（制御を戻した後）にデストラクタを呼び出す（関数が例外を投げた場合も同様）
> - 関数のリターンとデストラクタ呼び出しの後、呼び出し側は必要に応じて一時オブジェクトに割り当てられていた領域を解放する（一時オブジェクトがヒープに構築されていた場合など）

戻り値の非トリビアル型引数について次のように規定されています（[3.1.3.1 Non-trivial Return Values](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#non-trivial-return-values)）

> If the return type is a class type that is non-trivial for the purposes of calls, the caller passes an address as an implicit parameter. The callee then constructs the return value into this address. If the return type has a non-trivial destructor, the caller is responsible for destroying the temporary when control is returned to it normally. If an exception is thrown out of the callee after the return value is constructed but before control returns to the caller, e.g. by a throwing destructor, it is the callee's responsibility to destroy the return value before propagating the exception to the caller. Thus, in general, the caller is responsible for destroying the return value after, and only after, the callee returns control to the caller normally.
> 
> The address passed need not be of temporary memory; copy elision may cause it to point anywhere, including to global or heap-allocated memory.

意訳

> 戻り値の型が非トリビアル型である場合、呼び出し側は暗黙のパラメータとしてアドレスを渡す。呼び出された側は、そのアドレスに戻り値を構築する。戻り値型が非トリビアルデストラクタを持つ場合、呼び出し側には制御が戻った後でこの一時オブジェクトを破棄する責任が発生する。  
> 戻り値が構築された後呼び出し元に制御が戻る前に、呼び出された関数から例外が送出された場合（ローカル変数のデストラクタからの例外送出など）、呼び出し元に例外を送出する前に戻り値オブジェクトを破棄する（デストラクタを呼び出す）のは呼び出された側（関数内）の責任である。  
> したがって、一般的には、呼び出し側は呼び出した関数が正常にリターンした場合にのみ戻り値を破棄する責任を負う。
> 
> この暗黙に渡される戻り値格納用領域のアドレスは、スタックなどの一時領域のものである必要はなく、コピー省略などによってグローバル領域やヒープ領域のアドレスなど、どこを指していても構わない。

先ほどのサンプルコードを改めて見てみると、まさにこのあたりに書かれている通りになっている事がわかります。

ところで、非トリビアル型戻り値に関する規定の最後の一文は少し驚きです。

```cpp
// Tは何かしら非トリビアル型とする
T f();

int main() {
  T* p = new T(f());
}
```

C++17以降コピー省略が保証されているため、このような場合に`f()`の戻り値は`p`の領域に直接構築されることになり、先ほどの規定によると、`new`式によるメモリの確保->`f()`の評価->`T`の構築、のような順番で処理が実行されることが示唆されます。すなわち、`new`式が行なう2つのこと（メモリの確保とオブジェクトの構築）の間に`f()`の評価が挟まる事になり、この評価順序はかなり非自明です。

#### System V AMD64 ABI

System V AMD64 ABIはItanium C++ ABIを参照しており、「non-trivial for the purposes of calls」という言葉とその定義をそのまま使用しています。したがって、System V AMD64 ABIにおけるトリビアルな型とは先ほどのItanium C++ ABIにおけるそれと同様という事になります。

その扱いについて、「3.2.3 Parameter Passing」のクラス型の引数渡しについての欄外に次のようにあります

> An object whose type is non-trivial for the purpose of calls cannot be passed by value because such objects must have the same address in the caller and the callee. Similar issues apply when returning an object from a function. See C++17 [class.temporary] paragraph 3.

非トリビアルな型のオブジェクトは、呼び出し元と呼び出された側で同じアドレスを持っている必要があるため、値で渡す事ができず、関数からオブジェクトを返す場合も同様の問題がある。のように書かれています。

この一文は非トリビアル型がなぜ特別扱いされるのか？という疑問の回答となるものです。非トリビアル型のオブジェクトが関数の呼び出し元と呼び出された側で同じアドレスを持っている必要がある、というのは非トリビアルなコピー/ムーブコンストラクタおよび非トリビアルデストラクタの呼び出しを避けるためでしょう。関数の呼び出しに伴って実装の予測できないユーザー定義の関数（コピー/ムーブコンストラクタ等）を何度も呼び出す可能性（レジスタとスタックやメモリとの間のコピー）が生じるというのはとてつもないオーバーヘッドになります。それを避けるために、レジスタの外、関数の呼び出し前後で消えたりしない領域に一時オブジェクトを作成してその領域を共有していると考えられます。

逆に、トリビアルな型ではコピー/ムーブコンストラクタは`memcpy`相当（CPUにとっては普通のコピー）、トリビアルデストラクタは省略可能であるので、レジスタにコピーして渡したり、レジスタからコピーして受け取ったりと言ったことを何の問題もなく行う事ができます。

System V AMD64 ABIでの関数の呼び出しでは、引数型・戻り値型はまず型ごとにカテゴリ判定されます。クラス型の場合は、64 [byte]を超える場合は`MEMORY`というカテゴリになり、

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