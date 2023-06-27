# ［C++］ mdspanでインターリーブレイアウトを扱う

### レイアウトマッピングクラスの要件

`std::mdspan`におけるレイアウト調整は、その3番目のテンプレートパラメータにレイアウトポリシークラス型を渡して行います。そして、実際のレイアウトマッピングカスタム処理は、レイアウトポリシークラスのメンバ型であるレイアウトマッピングクラス型で実装します。

レイアウトポリシークラスを`LP`とすると、レイアウトマッピングクラス型は`mapping`という名前で`LP::mapping`のようにアクセスできる必要があり、唯一のテンプレートパラメータとして`Extents`（配列サイズを示す型）を受け取ります。

```cpp
// レイアウトポリシークラス
struct LP {

  // レイアウトマッピングクラス
  template <class Extents>
  class mapping {
    ...
  };
};
```

この`Extents`は`std::mdspan`から供給されるもので、`std::extents`の特殊化となります。レイアウトマッピングクラス内からは、この`Extents`とそのオブジェクトを介して現在の`std::mdspan`がハンドルしている配列のサイズ（次元と次元ごとの要素数）を取得することができます。

今回はインターリーブされたレイアウトをハンドルするので`LP`の名前は`layout_right_interleaved`にすることにして、レイアウト計算のために必要となるパラメータとしてインターリーブされている配列数`N`を受け取っておきます。

```cpp
// レイアウトポリシークラス
template<std::unsigned_integral auto N>
struct layout_right_interleaved {

  // レイアウトマッピングクラス
  template <class Extents>
  class mapping {
    ...
  };
};
```

#### 型に対する要件

レイアウトマッピングクラス型に関しては次のことが要求されます。

- [`copyable`](https://cpprefjp.github.io/reference/concepts/copyable.html)かつ[`equality_comparable`](https://cpprefjp.github.io/reference/concepts/equality_comparable.html)
- ムーブ構築が例外を投げない
- ムーブ代入が例外を投げない
- スワップ操作が例外を投げない

これを満たすためには通常、コピーコンストラクタとコピー代入演算子、および同値比較演算子を`default`定義しておきます。

```cpp
template<std::unsigned_integral auto N>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
  public:
  
    mapping(const mapping &) & = default;
    mapping &operator=(const mapping &) & = default;

    friend bool operator==(mapping, mapping) = default;
  };
};
```

レイアウトマッピングクラス型は通常`Extents`のオブジェクト1つを保持するだけで足りるため、コピーコストが低い型となるためこれで十分です。もし変なレイアウトのハンドル時にムーブが効率的となる場合は、ムーブコンストラクタ/代入演算子を定義したり、`operator==`の引数型を参照にしたりといったことをすればいいでしょう。

ここからは必須の要件ではありませんが、レイアウトマッピングクラスの他のコンストラクタの存在は`std::mdspan`のコンストラクタの利用可能性に影響を与えます。

- デフォルトコンストラクタ
    - `std::mdspan`のデフォルトコンストラクタを有効にするために必須
- `Extents`を受け取るコンストラクタ
    - 動的`Extents`をサポートする場合に必要
    - `std::mdspan`のレイアウトマッピングクラスを受け取らないコンストラクタを有効にするために必須
        - デフォルトコンストラクタは除く
- 他のレイアウトマッピングクラスからの変換コンストラクタ
    - `std::mdspan`の変換コンストラクタを有効にするために必須

最後のレイアウトマッピング変換は必ずしもサポートできるとは限らないため任意ですが、残りの2つは可能ならば提供しておきましょう。`std::mdspan`の構築は複雑なので、これらのコンストラクタを欠いているとそのレイアウトマッピングを使用した`std::mdspan`の構築が難しくなる可能性があります。

```cpp
template<std::unsigned_integral auto N>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
    // エクステントを保存しておく（動的エクステントを使用する場合に必要）
    Extents m_extent;
  public:

    // デフォルトコンストラクタ
    mapping() = default;

    // エクステントを受け取るコンストラクタ
    constexpr mapping(const Extents& ex)
      : m_extent{ex}
    {}
  
    mapping(const mapping &) & = default;
    mapping &operator=(const mapping &) & = default;

    friend bool operator==(mapping, mapping) = default;
  };
};
```

エクステントを受け取るコンストラクタには`const Extents&`が渡されるので、このように`const`参照か値で受ける必要があります。

これ以外のコンストラクタは必要なら定義することができ、これらのものと曖昧にならなければそれは自由です。

#### メンバ型

メンバ型は次の4つが要求されます

- `extents_type` : 要素数を表すクラス型
    - `std::extents`の特殊化であること
- `index_type` : 計算結果のインデックスの型
    - `extents_type::index_type`
- `rank_type` : ランク（次元数）の型
    - `extents_type::rank_type`
- `layout_type` : レイアウトマッピングクラスを包むレイアウトポリシー型
    - レイアウトマッピングクラスが`LP::mapping`のようになっている時の`LP`
    - `std::mdspan`のレイアウトマッピングクラスを受け取るコンストラクタがレイアウトポリシー型を取得するのに使用される

この4つはおそらく多くの場合ほとんどコピペで済むようなコードになります。

```cpp
template<std::unsigned_integral auto N>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
  public:

    // メンバ型定義
    using extents_type = Extents;
    using index_type = typename extents_type::index_type;
    using rank_type = typename extents_type::rank_type;
    using layout_type = layout_right_interleaved<N>;    // 都度変更すべきはおそらくここだけ
  };
};
```

#### レイアウトの特性を表す関数

レイアウトがどういう性質を持つかに関する性質を取得する関数が3種類要求されます

レイアウトマッピングクラスのオブジェクトを`m`としておきます

- `is_unique()`
    - 配列の1つの要素に1つのインデックスだけが対応する
    - 対称行列における重複要素を節約するようなレイアウトだと1つの要素に複数のインデックスが対応するため満たさない
      - 2次元の場合`m(i, j) == m(j, i)`となるためユニークではない
- `is_exhaustive()`
    - `[0, m.required_span_size())`の範囲内の全ての`k`に対して、`m(idx...) == k`となる多次元インデックス`idx...`が存在する場合に`true`
      - 変換後のインデックスによるアクセスはメモリ上の要素全てにアクセスする（パディングがない）
      - 要素がメモリ上で連続していることとほぼ等しいが、変換後のインデックスが必ずしも連続的ではない場合があり、その場合でも与えられたメモリ範囲の要素全てに対応するインデックスが計算されることを表す
- `is_strided()`
    - インデックス計算がストライドによって行われている場合に`true`
    - 幅`w`高さ任意の2次元行列なら、多次元インデックス`j, i`に対して`m(j, i)`は`w * j + i`を返す。この時、各次元のストライドは`(w, 1)`となる。
      - これと同等の計算によってインデックス計算が行われている場合に`true`を返す
- `is_always_unique()` （静的メンバ関数）
    - `is_unique()`が常に`true`となるなら`true`
- `is_always_exhaustive()` （静的メンバ関数）
    - `is_exhaustive()`が常に`true`となるなら`true`
- `is_always_strided()` （静的メンバ関数）
    - `is_strided()`が常に`true`となるなら`true`

これらの関数は全てその性質を満たしていれば`true`を返しそうでなければ`false`を返します。

`is_xxx()`に対する`is_always_xxx()`は`is_xxx()`の性質が個別のオブジェクトによらず常に満たされている場合に`true`を返します。`false`を返す場合は、その性質がオブジェクトごとに（その構築時パラメータによって）満たされないことがありうることを表します。

今回の場合、ある要素は1組のインデックスによってしかアクセスされないため`is_unique()`はつねに`true`であり、考慮する配列数`N`が2以上の場合はメモリ空間の全ての要素にアクセスしないため`is_exhaustive()`は`false`となります。そして、ストライド計算によってインデックスを計算可能なので、`is_strided()`は`true`です（詳しくは後述）。

```cpp
template<std::unsigned_integral auto N>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
  public:

    ...

    static constexpr bool is_unique() noexcept {
      return true;
    }

    static constexpr bool is_exhaustive() noexcept {
      return N == 1;
    }

    static constexpr bool is_strided() noexcept {
      return true;
    }

    static constexpr bool is_always_unique() noexcept { 
      return true;
    }

    static constexpr bool is_always_exhaustive() noexcept { 
      return N == 1;
    }

    static constexpr bool is_always_strided() noexcept {
      return true;
    }
  };
};
```

`static`メンバ関数は非静的メンバ関数と同様に`.`によるメンバアクセスで呼び出すことができるので、返す値がオブジェクトによらず決定するならば`always`ではない関数も静的メンバ関数として定義しておくことができます。

#### 基本関数

レイアウトの計算およびそれに関する情報を取得する関数が4つ要求されます

- `extents()`
    - 現在のエクステントを返す
- `operator(...)`
    - 多次元インデックスをメモリ上の一点のインデックスに変換する
- `required_span_size()`
    - 現在のレイアウトがアクセスするメモリ範囲の最大値を返す
      - `extents()`のサイズが0なら0
      - それ以外の場合、インデックス計算の結果の最大値+1
- `stride(r)`
    - 次元`r`のストライドを返す

`extents()`だけはそのままですが、`operator()`および他のものはレイアウトのインデックス計算の実装と関わってくるためインデックス計算実装時に整えます。

```cpp

template<std::unsigned_integral auto N>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
    Extents m_extent;
  public:

    ...
  
    constexpr auto extents() const noexcept -> const extents_type& {
      return m_extent;
    }

    constexpr auto required_span_size() const -> index_type;

    constexpr auto stride(rank_type r) const -> index_type;

    template<typename... Indices>
      requires (sizeof...(Indices) == extents_type::rank()) and
               (std::is_nothrow_convertible_v<Indices, index_type> && ...)
    constexpr auto operator()(Indices... idx) const -> index_type;
  };
};
```

### 実装

### ストライド

### 参考文献

- [`std::mdspan`×空間充填曲線 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20230315/p1)
- [`std::mdspan` - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20230303/p1)
- [P0009R18 MDSPAN](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p0009r18.html)
- [P2604R0 MDSPAN: rename pointer and contiguous - ［C++］WG21月次提案文書を眺める（2022年06月）](https://onihusube.hatenablog.com/entry/2022/07/09/160343#P2604R0-MDSPAN-rename-pointer-and-contiguous)
- [インターリーブ配列 VBO](https://wgld.org/d/webgl/w088.html)