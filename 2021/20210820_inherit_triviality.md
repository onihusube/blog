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

### C++20からは・・・

### なぜにトリビアル？

### 参考文献

- [C++17 optionalの実装について - 茅の下](https://ryooooooga.hateblo.jp/entry/2016/07/10/225710)
- [C++11 共用体の制限解除 - cpprefjp](https://cpprefjp.github.io/lang/cpp11/unrestricted_unions.html)
- [P0848R0 Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0848r0.html)
- [P0848R3 Conditionally Trivial Special Member Functions](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0848r3.html)
- [Conditionally Trivial Special Member Functions - C++ Team Blog](https://devblogs.microsoft.com/cppblog/conditionally-trivial-special-member-functions/)