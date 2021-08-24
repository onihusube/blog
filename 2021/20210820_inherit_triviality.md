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
  union {
    char dummy;
    T data;
  };
  bool has_value = false;

public:

  // デフォルトコンストラクタ
  constexpr my_optional() 
    : dummy{}
    , has_value(false)
  {}

  // 値を受け取るコンストラクタ
  template<typename U=T>
  constexpr my_optional(U&& v)
    : data(std::forward<U>(v))
    , has_value(true)
  {}

  // コピーコンストラクタ
  my_optional(const my_optional& that)
    : dummy{}
    , has_value(that.has_value)
  {
    if (that.has_value) {
      new (&this->data) T(that.data);
    }
  }

  // ムーブコンストラクタ
  my_optional(my_optional&& that)
    : dummy{}
    , has_value(that.has_value)
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

デストラクタのトリビアル性継承は要するに、`T`がトリビアルデストラクタを持つ場合に`default`で、そうではない場合に独自定義、という風に分岐してやればいいのです。それはクラステンプレートの部分特殊化を用いて、次のように実装できます。

```cpp
// デストラクタがトリビアルでない場合のストレージ
template<typename T, bool = std::is_trivially_destructible_v<T>>
struct optional_storage {
  union {
    char dummy;
    T data;
  };
  bool has_value = false;

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
  union {
    char dummy;
    T data;
  };
  bool has_value = false;

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

コピー/ムーブコンストラクタをトリビアルに定義するとは、先程のデストラクタのように`T`でのそれがトリビアルならば`my_optional`でのそれもトリビアルとなるようにすればいいのです。が、冷静に考えてみると、すでにデストラクタのトリビアル性で分岐している所にコピーコンストラクタのそれでさらに分岐し、さらにムーブコンストラクタでも・・・となって組合せ爆発のようになることがわかるでしょう。じゃあいい方法が・・・ないので愚直に書きましょう。

ただ、そのような分岐を1つのクラスにまとめようとすると組合せ爆発で死ぬのは想像が付くので、特殊メンバ関数一つに対して1つのクラスが必要で、その1つのクラスには`default`によるトリビアルな定義をするものと自前定義するものの2つの特殊化が必要になりそうです。  
もう少しよくよく考えてみると、`T`のある特殊メンバ関数がトリビアルであるとき、基底となる`optional_storage`でもそれはトリビアルに定義できるはずなので、そこで定義されたそれを活用すればトリビアルケースの定義を省略出来る事に気づけます（私は気づきませんでしたが）。

コピーコンストラクタだけで見てみると、次のようになります。

```cpp
// デストラクタがトリビアルでない場合のストレージ
template<typename T, bool = std::is_trivially_destructible_v<T>>
struct optional_storage {
  union {
    char dummy;
    T data;
  };
  bool has_value = false;
  
  constexpr optional_storage()
    : dummy{}
    , has_value(false)
  {}
  
  template<typename... Args>
  constexpr optional_storage(Args&&... arg)
    : data(std::forward<Args>(arg)...)
    , has_value(true)
  {}
  
  // 定義できればトリビアル、そうでないなら暗黙delete
  optional_storage(const optional_storage&) = default;
  optional_storage(optional_storage&&) = default;
  optional_storage& operator=(const optional_storage&) = default;
  optional_storage& operator=(optional_storage&&) = default;

  ~optional_storage() {
    if (has_value) {
      this->data.~T();
    }
  }
  
  template<typename... Args>
  void construct(Args&&... arg) {
    new (&this->data) T(std::forward<Args>(arg)...);
    has_value = true;
  }
  
  template<typename Self>
  void construct_from(Self&& that) {
    if (that.has_value) {
      // thatの値カテゴリを伝播する
      construct(std::forward<Self>(that).data);
    }
  }
};

// デストラクタがトリビアルである場合のストレージ
template<typename T>
struct optional_storage<T, true> {
  union {
    char dummy;
    T data;
  };
  bool has_value = false;

  constexpr optional_storage()
    : dummy{}
    , has_value(false)
  {}
  
  template<typename... Args>
  constexpr optional_storage(Args&&... arg)
    : data(std::forward<Args>(arg)...)
    , has_value(true)
  {}
  
  // 定義できればトリビアル、そうでないなら暗黙delete
  optional_storage(const optional_storage&) = default;
  optional_storage(optional_storage&&) = default;
  optional_storage& operator=(const optional_storage&) = default;
  optional_storage& operator=(optional_storage&&) = default;
  
  template<typename... Args>
  void construct(Args&&... arg) {
    new (&this->data) T(std::forward<Args>(arg)...);
    has_value = true;
  }
  
  template<typename Self>
  void construct_from(Self&& that) {
    if (that.has_value) {
      // thatの値カテゴリを伝播する
      construct(std::forward<Self>(that).data);
    }
  }
};

template<typename T>
struct enable_copy_ctor : optional_storage<T> {
  using base = optional_storage<T>;

  // ユーザー定義コピーコンストラクタ
  enable_copy_ctor(const enable_copy_ctor& that)
    : base()
  {
    this->construct_from(static_cast<const base&>(that));
  }

  // 他のは全部基底のものか上で定義されるものに頼る！
  enable_copy_ctor() = default;
  enable_copy_ctor(enable_copy_ctor&&) = default;
  enable_copy_ctor& operator=(const enable_copy_ctor&) = default;
  enable_copy_ctor& operator=(enable_copy_ctor&&) = default;

};

template<typename T>
using check_copy_ctor = std::conditional_t<
  std::is_trivially_copy_constructible_v<T>,
  optional_storage<T>,
  enable_copy_ctor<T>
>;

template<typename T>
class my_optional : private check_copy_ctor<T> {
public:
  // 他略

  // コピーコンストラクタ
  // copy_ctor_enabler<T>のコピーコンストラクタを利用する
  my_optional(const my_optional& that) = default;
};
```

C++11以降の共用体は内包する型の特殊メンバ関数がトリビアルでないならば、対応する自身の特殊メンバ関数が暗黙`delete`されます。従って、`optional_storage`ではデストラクタ以外をとりあえず全部`default`定義しておけば、トリビアルの時だけは定義されていることになります。

それを利用し、`T`が*trivially copyable*の時だけ、`optional_storage`に至るクラス階層にコピーコンストラクタ定義を追加し、そうでなければ`optional_storage`を直接利用します。すると、最上位`my_optional`クラスからはその基底クラスのコピーコンストラクタは常に何かしら定義されているように見えるため、`my_optional`のコピーコンストラクタは`default`で定義する事ができます。

派生クラスのコンストラクタ初期化子リストからは最基底の`optional_storage`のメンバは触れませんので、`optional_storage`にはコンストラクタが必要です。また、フラグの管理とか構築周りのことを共通化するために`optional_storage`に`construct()/construct_from()`関数を追加しておきます。

同じようにムーブコンストラクタを定義しましょう。

```cpp
template<typename T>
struct enable_move_ctor : check_copy_ctor<T> {
  using base = check_copy_ctor<T>
  
  // ユーザー定義ムーブコンストラクタ
  enable_move_ctor(enable_move_ctor&& that)
    : base()
  {
    this->construct_from(static_cast<base&&>(that));
  }

  // コピーコンストラクタはenable_copy_ctorで定義されるか
  // optional_storageでトリビアルに定義される
  enable_move_ctor(const enable_move_ctor&) = default;

  enable_move_ctor() = default;
  enable_move_ctor& operator=(const enable_move_ctor&) = default;
  enable_move_ctor& operator=(enable_move_ctor&&) = default;
};

template<typename T>
using check_move_ctor = std::conditional_t<
  std::is_trivially_move_constructible_v<T>,
  check_copy_ctor<T>,
  enable_move_ctor<T>
>;

template<typename T>
class my_optional : private check_move_ctor<T> {
public:
  // 他略

  // ムーブコンストラクタ
  my_optional(my_optional&&) = default;
};
```

`my_optional`と`check_copy_ctor`の間に、さっきと同じようなものを挿入してやるだけです、簡単ですね・・・

```cpp
int main() {
  // パスする
  static_assert(std::is_trivially_destructible_v<my_optional<int>>);
  static_assert(std::is_trivially_copy_constructible_v<my_optional<int>>);
  static_assert(std::is_trivially_move_constructible_v<my_optional<int>>);
  static_assert(std::is_trivially_destructible_v<my_optional<std::string>> == false);
  static_assert(std::is_trivially_copy_constructible_v<my_optional<std::string>> == false);
  static_assert(std::is_trivially_move_constructible_v<my_optional<std::string>> == false);
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/auMdxpScR5Dn2yBk)

ちゃんとトリビアル性が伝播されてる事がわかります。

### 代入演算子


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

他のコンストラクタが存在するとデフォルトコンストラクタは暗黙`delete`されるため、`default`で書いておきます。この時、メンバに持っている`T`のオブジェクトに対してデフォルトメンバ初期化してしまうとトリビアルにならないので注意が必要です。

```cpp
int main() {
  static_assert(std::is_trivially_default_constructible_v<wrap<int>>);  // パスする
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/tgDiKULdlA3F7SUV)

またおそらく、このような単純な型ではその他の部分のトリビアル性継承時にも先程までのような謎のテクニックを駆使する必要はないはずです。

### C++20からは・・・

C++20ではコンセプトが導入され、それを利用した[Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0848r3.html)という機能が追加されました。これはまさに、ここまで見てきた事をコンセプトによって簡易に実現するための機能です。

これによって、`my_optional`実装は次のようになります。

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

  // トリビアルに定義できるならそうする
  my_optional(const my_optional& that) requires std::is_trivially_copyable_v<T> = default;
  my_optional(my_optional&& that) requires std::is_trivially_movable_v<T> = default;
  my_optional& operator=(const my_optional& that) requires std::is_trivially_copy_assignable_v<T> = default;
  my_optional& operator=(my_optional&& that) requires std::is_trivially_move_assignable<T> = default;
  ~my_optional() requires std::is_trivially_destructible_v<T> = default;


  // そうでない場合はユーザー定義する

  my_optional(const my_optional& that)
    : has_value(that.has_value)
    , dummy{}
  {
    if (that.has_value) {
      new (&this->data) T(that.data);
    }
  }

  my_optional(my_optional&& that)
    : has_value(that.has_value)
    , dummy{}
  {
    if (that.has_value) {
      new (&this->data) T(std::move(that.data));
    }
  }

  my_optional& operator=(const my_optional& that) {
    auto copy = that;
    *this = std::move(copy);
    
    return *this;
  }

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

  ~my_optional() {
    if (has_value) {
      this->data.~T();
    }
  }
};
```

`default`な特殊メンバ関数に対して`requires`による制約を付加する事で、テンプレートパラメータの性質によって定義するしないを分岐することができます。

ここでは、オーバーロード解決時の制約式による半順序に基づいて、特殊メンバ関数定義にも制約によって順序が付けられ、最も制約されている（かつそれを満たしている）1つだけが資格のある（*eligible*）特殊メンバ関数として定義され、それ以外は`delete`されます。

この場合、`my_optional`の`default`な特殊メンバ関数定義は`is_trivially_~`によって制約されており、`T`の対応する特殊メンバ関数がトリビアルである時`my_optional`の対応する特殊メンバ関数もトリビアルな方が選択され、ユーザー定義のものは無制約なので`delete`されます。逆に、`T`の対応する特殊メンバ関数がトリビアルではない時、制約を満たさないことから`default`のものが`delete`され、結果的に適切な一つだけが定義されています。

先ほどまで書いていたものすごく労力のかかった意味のわからないコードはこれによって不要になります。このConditionally Trivial Special Member Functionsという機能がいかに強力で、どれほどマイナーなのかがわかるでしょう！

そしてC++20以降、あのようなテクニックは忘れ去られていく事でしょう。この記事は、失われいく謎のテクニックを後世に伝えるとともに、理解しづらいConditionally Trivial Special Member Functionsという機能の解説を試みるものでした・・・

### なぜにトリビアル？

長いので分けました。そもそもなんでそこまでしてトリビアル性にこだわるのか？という事を書いています。

- [［C++］トリビアルってトリビアル？](https://onihusube.hatenablog.com/entry/2021/08/20/002116)

### 参考文献

- [C++17 optionalの実装について - 茅の下](https://ryooooooga.hateblo.jp/entry/2016/07/10/225710)
- [C++11 共用体の制限解除 - cpprefjp](https://cpprefjp.github.io/lang/cpp11/unrestricted_unions.html)
- [`xsmf_control.h` - microsoft/STL](https://github.com/microsoft/STL/blob/main/stl/inc/xsmf_control.h)
- [P0848R0 Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0848r0.html)
- [P0848R3 Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0848r3.html)
- [Conditionally Trivial Special Member Functions - C++ Team Blog](https://devblogs.microsoft.com/cppblog/conditionally-trivial-special-member-functions/)
- [C++20 コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)