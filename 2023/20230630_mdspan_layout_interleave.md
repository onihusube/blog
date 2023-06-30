# ［C++］ mdspanでインターリーブレイアウトを扱う

`mdspan`お勉強のメモです。ここでのサンプルコードは全て[kokkos/mdspan](https://github.com/kokkos/mdspan)を用いています。

`std::mdspan`そのものについてはあまり解説しないので、`std::mdspan`の使い方などに関しては例えばこれらの記事などをご参照ください

- [`std::mdspan` - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20230303/p1)
- [`std::mdspan` - cppreference.com](https://en.cppreference.com/w/cpp/container/mdspan)

[:contents]

### インターリーブレイアウト

行列（配列）のインターリーブとは、同じサイズの複数の行列を1つの行列に詰め込むようなメモリレイアウトで、その際に同じ添字を持つ要素を連続的に配置するものです。

インターリーブレイアウトへの変換イメージ

![](https://jp.mathworks.com/matlabcentral/mlc-downloads/downloads/submissions/65036/versions/3/screenshot.png)  
([Interleave - File Exchange - MATLAB Central](https://jp.mathworks.com/matlabcentral/fileexchange/65036-b-interleave-dim-a1-a2-a3-an)より引用)

1次元（配列）の場合は、AoSに対してSoAと呼ばれるレイアウトのことです。

このようなレイアウトを取ることによる利点は、対応する添字要素をメモリ上で隣接させて配置することで局所性を高めメモリアクセスを効率化できる点です。

例えば、複数の行列を使用するある処理がそれら行列の対応する要素ごとに処理を行なっていくような場合、通常のレイアウトだと複数の行列間で対応する（同じ添字を持つ）要素はメモリ上で少なくとも行列サイズ分離れた位置に配置されています。それを読み込もうとすると全部の要素を読み込むのに異なる位置へのメモリアクセスが何度も発生し、1要素読み込むごとにキャッシュが無効化されるなど非効率となります。インターリーブレイアウトをとることで、1度のメモリアクセスで使いたい要素を一括でロードし、なおかつキャッシュにも乗りやすくなるなど効率化を図れます。

インターリーブレイアウトを用いる場合、行列のメモリ配置が複雑になり1つの行列にアクセスする際に工夫しなければなりません。

C++23からは多次元配列ビューである`std::mdspan`が追加されました。`std::mdspan`のデフォルトはC++の配列レイアウトを元にした行優先の多次元配列を扱いますが、`std::mdspan`はレイアウトをカスタムできるようになっており、それを利用するとインターリーブレイアウトを取り扱うことができるようになります。

この記事では、`std::mdspan`のレイアウトカスタマイズ機能を利用してインターリーブレイアウトをハンドルできるようにしながら、複雑に見えがちな`std::mdspan`の内部構造に触れていきます。

なお、上記イメージのようにインターリーブレイアウトには行優先と列優先の2種類がありますが、ここではインターリーブはいつも行優先であるものとし列優先のレイアウトは扱いません。列優先でも考え方はそんなに変わらないはずですが。

### `mdspan`のカスタマイズ

`std::mdspan`は`std::mdspan<T, E, L, A>`のように4つのテンプレートパラメータを受け取ります。ただし、実際使用する際に指定する必要があるのは前2つのテンプレートパラメータのみで、後2つはデフォルトのものが設定されています。このパラメターはそれぞれ

- `T` : 要素型
- `E` : エクステント（次元数とその要素数）
- `L` : レイアウトポリシー型
- `A` : アクセサポリシー型

となっています。

```cpp
// mdspnaの宣言例
namespace std {
  template<
    class T,
    class Extents,
    class LayoutPolicy = std::layout_right,
    class AccessorPolicy = std::default_accessor<T>
  >
  class mdspan;
}
```

例えばこんな感じで使用します

```cpp
template<typename T>
using mat33 = std::mdspan<T, std::extents<std::size_t, 3, 3>>;

int main() {
  int storage[] = {
    0, 1, 2,
    3, 4, 5,
    6, 7, 8
  };

  // CTADによって要素型を推論
  mat33 A{storage};

  for (int y = 0; y < 3; ++y) {
    for (int x = 0; x < 3; ++x) {
      std::cout << A[y, x] << " ";
    }
    std::cout << '\n';
  }  
}
```
```
0 1 2 
3 4 5 
6 7 8 
```

- [Compiler Explorer (gcc13.1)](https://godbolt.org/z/jxbfEnjxh)
    - 参照しているヘッダの実装が間違っているためCTADが失敗するので、要素型を明示指定している

デフォルトの`L, A`によるアクセスはC++の配列へのアクセス同様の行優先レイアウトとなります。

レイアウトポリシー`L`を変更することによって考慮するレイアウトを変更することができ、例えば列優先レイアウトにする場合は`L`を`std::layout_left`に変更します。

```cpp
// レイアウトを行優先に
template<typename T>
using mat33 = std::mdspan<T, std::extents<std::size_t, 3, 3>, std::layout_left>;

int main() {
  int storage[] = {
    0, 1, 2,
    3, 4, 5,
    6, 7, 8
  };

  mat33 A{storage};

  for (int y = 0; y < 3; ++y) {
    for (int x = 0; x < 3; ++x) {
      std::cout << A[y, x] << " ";
    }
    std::cout << '\n';
  }  
}
```
```
0 3 6 
1 4 7 
2 5 8
```

- [Compiler Explorer (gcc13.1)](https://godbolt.org/z/nEbn1x85c)

`std::mdspan`は参照する領域のポインタと`L, A`（`E`は`L`に保存される）をメンバとして持ち、簡単には次のような動作をしています

```cpp

namespace std {
  template<
    class T,
    class Extents,
    class LayoutPolicy = std::layout_right,
    class AccessorPolicy = std::default_accessor<T>
  >
  class mdspan {
    // 領域ポインタ
    T* ptr;
    // インデックス計算
    LayoutPolicy::mapping<Extents> map;
    // アクセスを行う
    AccessorPolicy acc;
  
  public:

    ...

    template<class... OtherIndexTypes>
    auto operator[](OtherIndexTypes... indices) const {
      // 多次元インデックスから1次元のインデックスを求める
      auto idx = map(indices...);

      // 要素ポインタとインデックスから要素を引き当て
      return acc(ptr, idx);
    }
  };
}
```

動作の流れとしてはこんな感じですが、これは単純な例であり実際にはもう少し複雑になっています。

レイアウトポリシー`L`は多次元のインデックス列を1次元のインデックス空間への写像で、例えば幅`W`の2次元領域なら、`y, x`の2次元インデックスに対して`y * W + x`を計算するものです。

アクセサポリシー`A`はインデックス`i`と領域ポインタ`ptr`からどのように要素を取得するかをカスタマイズする型で、基本的には`*(ptr + i)`を返します。ここではこれはカスタムしませんが、カスタマイズの方向性としては例えば、`std::atomic_ref`を通してアクセスするとか、`std::assume_aligned`を通してアクセスするなどがあります。

このように、多次元配列アクセスにおいてやるべきことをレイアウトポリシーとアクセサポリシーで分割してハンドルし、かつそれをテンプレートパラメータで受け取ることによって柔軟にカスタマイズできるようにしています。

従って、インターリーブレイアウトを`mdspan`で扱うためには、レイアウトポリシー型`L`をカスタマイズする必要があります。

### レイアウトポリシー型の構造

レイアウトポリシー型を`LP`とすると、レイアウトマッピングクラス型は`mapping`という名前で`LP::mapping`のようにアクセスできる必要があり、唯一のテンプレートパラメータとして`Extents`（配列サイズを示す型）を受け取ります。

```cpp
// レイアウトポリシー型
struct LP {

  // レイアウトマッピングクラス
  template <class Extents>
  class mapping {
    ...
  };
};
```

この`Extents`は`std::mdspan`から供給されるもので、`std::extents`の特殊化となります。レイアウトマッピングクラス内からは、この`Extents`とそのオブジェクトを介して現在の`std::mdspan`がハンドルしている配列のサイズ（次元と次元ごとの要素数）を取得することができます。

レイアウトポリシー型はこのレイアウトマッピングクラスを定義しておくことだけが役割であり、実際のレイアウトカスタマイズはレイアウトマッピングクラス内部で行います。

今回は行優先でインターリーブされたレイアウトをハンドルするので`LP`の名前は`layout_right_interleaved`にすることにして、レイアウト計算のために必要となるパラメータとしてインターリーブされている配列数`D`を受け取っておきます。

```cpp
// レイアウトポリシー型
template<std::unsigned_integral auto D>
struct layout_right_interleaved {

  // レイアウトマッピングクラス
  template <class Extents>
  class mapping {
    ...
  };
};
```

このような構造になっているのは、`mdspan<T, E, L>`のようにテンプレートパラメータで渡した時に、`L`が`L<E>`のように`E`に依存してしまうのを避けるためだと思われます。これは記述が冗長となるほか、CTADが難しくなる可能性があります。

### レイアウトマッピングクラスの要件

レイアウトマッピングクラスには満たすべき性質や定義すべき関数などの要件がいくつもあります。

#### 型に対する要件

レイアウトマッピングクラス型に関しては次のことが要求されます。

- [`copyable`](https://cpprefjp.github.io/reference/concepts/copyable.html)かつ[`equality_comparable`](https://cpprefjp.github.io/reference/concepts/equality_comparable.html)
- ムーブ構築が例外を投げない
- ムーブ代入が例外を投げない
- スワップ操作が例外を投げない

これを満たすためには通常、コピーコンストラクタとコピー代入演算子、および同値比較演算子を`default`定義しておきます。

```cpp
template<std::unsigned_integral auto D>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
  public:
  
    mapping(const mapping &) = default;
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
    - デフォルトコンストラクタは除いて、`std::mdspan`のレイアウトマッピングクラスを受け取らないコンストラクタを有効にするために必須
- 他のレイアウトマッピングクラスからの変換コンストラクタ
    - `std::mdspan`の変換コンストラクタを有効にするために必須

最後のレイアウトマッピング変換は必ずしもサポートできるとは限らないため任意ですが、残りの2つは可能ならば提供しておきましょう。`std::mdspan`の構築は複雑なので、これらのコンストラクタを欠いているとそのレイアウトマッピングを使用した`std::mdspan`の構築が難しくなる可能性があります。

```cpp
template<std::unsigned_integral auto D>
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
  
    mapping(const mapping &) = default;
    mapping &operator=(const mapping &) & = default;

    friend bool operator==(mapping, mapping) = default;
  };
};
```

エクステントを受け取るコンストラクタには`const Extents&`が渡されるので、`const`参照か値で受ける必要があります。

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
template<std::unsigned_integral auto D>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
  public:

    // メンバ型定義
    using extents_type = Extents;
    using index_type = typename extents_type::index_type;
    using rank_type = typename extents_type::rank_type;
    using layout_type = layout_right_interleaved<D>;    // 都度変更すべきはおそらくここだけ
  };
};
```

#### レイアウトの特性を表す関数

レイアウトがどういう性質を持つかについてを取得する関数が3種類要求されます。これらはすべて引数を取らず`bool`を返す関数です。

説明のために、レイアウトマッピングクラスのオブジェクトを`m`としておきます

- `is_unique()`
    - 配列の1つの要素に1つのインデックスだけが対応する場合に`true`
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

今回の場合、ある要素は1組のインデックスによってしかアクセスされないため`is_unique()`はつねに`true`であり、考慮する配列数`D`が2以上の場合はメモリ空間の全ての要素にアクセスしないため`is_exhaustive()`は`false`となります。そして、ストライド計算によってインデックスを計算可能なので、`is_strided()`は`true`です（詳しくは後述）。

```cpp
template<std::unsigned_integral auto D>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
  public:

    ...

    static constexpr bool is_unique() noexcept {
      return true;
    }

    static constexpr bool is_exhaustive() noexcept {
      return D == 1;
    }

    static constexpr bool is_strided() noexcept {
      return true;
    }

    static constexpr bool is_always_unique() noexcept { 
      return true;
    }

    static constexpr bool is_always_exhaustive() noexcept { 
      return D == 1;
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
    - インデックス計算の実装はここで行う
- `required_span_size()`
    - 現在のレイアウトがアクセスするメモリ範囲の最大値を返す
      - `extents()`のサイズが0なら0
      - それ以外の場合、インデックス計算の結果の最大値+1
- `stride(r)`
    - 次元`r`のストライドを返す

`extents()`だけはそのままですが、`operator()`および他のものはレイアウトのインデックス計算の実装と関わってくるためインデックス計算実装時に整えます。

```cpp
template<std::unsigned_integral auto D>
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

エクステント型の静的メンバ関数`extents_type::rank()`はそのエクステントのランク（次元数）を取得するもので、これは必ずコンパイル時の定数となります。静的`constexpr`メンバ関数であるため、型の文脈でも使用することができます。

### インターリーブレイアウトにおけるインデックス計算

レイアウトマッピングクラスの役割は、`d`次元の多次元インデックス`i_0, i_1, ..., i_(d-1)`を1次元の空間インデックスに変換することです。結果のインデックスがどのように使われるのかは`mdspan`のアクセサポリシークラスが決めることですが、通常のポインタ演算（計算結果のインデックス`idx`とストレージポインタ`ptr`に対して`*(ptr + idx)`）を仮定して良いでしょう。したがって、レイアウトマッピングクラスでは要素のサイズとかバイト単位のアクセスとかを気にする必要はなく、要素サイズを1単位とした1次元領域上でのインデックス計算のみを考えれば良いわけです。

今実装したい配列（行列）のインターリーブレイアウトとは、複数の配列の対応するインデックスの要素を連続的に配置していくものでした。例えば3つの2次元行列を1つの2次元行列に行優先でインターリーブするとは次のようになります

```cpp
// この3つの配列を
int A[] = {
  100, 101, 102,
  110, 111, 112,
  120, 121, 122,
};
int B[] = {
  200, 201, 202,
  210, 211, 212,
  220, 221, 222,
};
int C[] = {
  300, 301, 302,
  310, 311, 312,
  320, 321, 322,
};

// このように詰める
int interleaved[] = {
  100, 200, 300, 101, 201, 301, 102, 202, 302,
  110, 210, 310, 111, 211, 311, 112, 212, 312,
  120, 220, 320, 121, 221, 321, 122, 222, 322,
};
```

2次元の場合により一般化して考えてみると

1つのインターリーブ配列の中に含まれる2次元行列の数を`D`、行列の行数を`J`、行列の列数を`I`として、`d = D - 1`、`i = I - 1`、`j = J - 1`とすると

$$
M_{int} = \begin{pmatrix}
a_{000} & ... & a_{d00} & a_{001} & ... & a_{d01} & ... & a_{00i} & ... & a_{d0i} \\
a_{010} & ... & a_{d10} & a_{011} & ... & a_{d11} & ... & a_{01i} & ... & a_{d1i} \\
\vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots & \vdots \\
a_{0j0} & ... & a_{dj0} & a_{0j1} & ... & a_{dj1} & ... & a_{0ji} & ... & a_{dji}
\end{pmatrix}
$$

こんな感じになります。

1次元方向（行方向）を見てみると、ある`n`番目の行列の隣り合う要素（例えば$a_{n00}$と$a_{n01}$）の間には含まれる行列分、つまり`D`個の要素があります。そのため、ある1つの行列の行内で`l`番目の要素のインデックスは`l * D`で求められます。

2次元方向（列方向）を見てみると、ある`n`番目の行列の上下で隣り合う要素（例えば$a_{n00}$と$a_{n10}$）の間には、含まれる行列全ての列要素の個数分の要素、つまり`D * I`（行列数 × 列幅）個の要素があります。そのため、ある1つの行列の列間のオフセットは`m * D * I`で求められます。

したがって、ある1つの行列の先頭要素から見た時、その行列の`y`列`x`行の要素へのインデックス`idx`は

$$
idx = y \times D \times I + x \times D
$$

で求められます。

#### 多次元行列への一般化

含まれる行列を3次元以上にしたくなる場合があるかもしれません。3次元以上となるとイメージを描くのも難しくなりますが、3次元行列の配置がどうなるのかについては2次元行列の要素を1次元配列と思うことで考えることができます。あるいは、何次元だろうが1次元配列に詰めてしまうことを考えると、3次元配列とは2次元配列の配列であり、N次元配列とはN-1次元配列の配列です。

つまり、普通の3次元行列の3次元軸方向に隣り合う要素（例えば$a_{000}$と$a_{100}$）の間には、その行列の一部である2次元行列1つ分の要素が詰まっています。

その上でインターリーブされている場合のインデックスを考えると、インターリーブされているある3次元行列の3次元軸方向に隣り合う要素（例えば$a_{n000}$と$a_{n100}$）の間には、インターリーブされている行列の個数分の2次元行列が間に挟まっています。

インターリーブされている行列数を`D`、3次元行列の各次元の要素数を1次元目から`I, J, K`とすると、ある1つの行列の先頭要素から見た時、その行列の`(x, y, z)`（左側が低位次元）要素へのインターリーブされた空間上でのインデックス`idx`は

$$
idx = z \times D \times I \times J + y \times D \times I + x \times D
$$

で求められます。

同様に一般化すると、インターリーブされている行列数を`D`、N次元行列の各次元のサイズ（要素数）を`In`（`0 <= n < N`）とすると、ある1つの行列の先頭要素から見た時、その行列の`(i0, ..., in)`要素へのインターリーブされた空間上でのインデックス`idx`は、

$$
idx = D \times (i_n \times (I_{n - 1} \times ... \times I_0) + ... + i_2 \times I_1 \times I_0 + i_1 \times I_0  + i_0) 
$$

のようになります（多分）。

今回は2次元行列のインターリーブだけを確認することにして、高次元はとりあえずこれに則って実装はしますが特にチェックしないことにします（間違ってたら教えてください）。

### 実装

後は上式をコードに直すだけです。色々な方法が考えられますが、ここでは上式をホーナー法によって変換して、それをそれを実装する事にします。

$$
idx = D \times (I_0 \times ( I_1 \times ...(I_{n - 2} \times (I_{n - 1} \times i_n + i_{n-1}) + i_{n-2})... + i_1) + i_0)
$$

ここでのインターリーブされている行列数`D`はテンプレートパラメータ`N`から、行列の次元数`N`はエクステント型の`extents_type::rank()`から、各次元の要素数`I_i`はエクステントオブジェクトのメンバ関数`m_extent.extent(i)`から、多次元インデックス`i_n`はレイアウトマッピング型の`operator()`の引数から取得できます。

```cpp
template<std::unsigned_integral auto D>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
    Extents m_extent;
  public:

    ...

    constexpr auto required_span_size() const -> index_type {
      // 丸投げ
      return layout_stride::mapping<Extents>(m_extent).required_span_size();
    }

    // 次元rのインデックスにかけられている係数を求める
    constexpr auto stride(rank_type r) const -> index_type
      requires (extents_type::rank() != 0)
    {
      assert(r < extents_type::rank());

      index_type stride = D;

      for (auto i : std::views::iota(0u, r)) {
        stride *= m_extent.extent(i);
      }

      return stride;
    }

    template<typename... Indices>
      requires (sizeof...(Indices) == extents_type::rank()) and
               (std::is_nothrow_convertible_v<Indices, index_type> && ...)
    constexpr auto operator()(Indices... indices) const -> index_type {
      // 行列次元数
      // extent()が0indexなので最大値は-1する
      constexpr std::unsigned_integral auto N = extents_type::rank() - 1;
      static_assert(0u < N);

      // インデックス配列
      // indicesは先頭が最大次元、末尾が1次元
      const std::array<index_type, extents_type::rank()> idx_array = {static_cast<index_type>(indices)...};

      index_type idx = idx_array[0];

      for (auto m = N - 1; const auto in : idx_array | std::views::drop(1)) {
        idx *= m_extent.extent(m);
        idx += in;
        --m;
      }

      return D * idx;
    }
  }
};
```

計算してる部分（`operator()`）では、先ほどのホーナー法による式の内側から計算しています。このレイアウトマッピングクラスの`operator()`の引数の多次元インデックスは、`mdspan`の`operator[]`に渡されるものがそのまま渡され、先頭が最大次元で末尾が1次元のインデックスとなるような順番で渡ってきます。

`std::array`に格納しているのはパラメータパックのままだと取り扱いが面倒だったためで、パック展開を駆使すればもっといい感じにできる可能性があります。

範囲`for`内では、次元`n`のインデックス`in`に`m = n - 1`次元のサイズ`Im`をかけてから、`n + 1`次元のインデックスを足し合わせ、`m`の次元を1つ落としてループします。この時、`m`が先に-1に到達しモジュロ演算で最大値になってしまうのでその`m`にはアクセスしないようにする必要があり、先頭インデックス（`idx_array[0]`）を先に取ってそれを飛ばした残りの要素でループを回しているのはその対策のためです。

`required_span_size()`の実装を委譲しているのは、多次元インデックス空間が0の時とランクが0の時をハンドルするのとか最大範囲を求めるのが面倒だとかの理由によるものです。`stride(r)`と`required_span_size()`の実装の意味については後述します。

これをこんなコードで簡単にテストすると

```cpp
int main() {
  using test = layout_right_interleaved<3u>::mapping<extents<std::size_t, 3, 3>>;

  test m{extents<std::size_t, 3, 3>{}};

  std::cout << m.stride(0) << '\n';
  std::cout << m.stride(1) << '\n';

  std::cout << "(0, 0) -> " << m(0, 0) << '\n';
  std::cout << "(0, 1) -> " << m(0, 1) << '\n';
  std::cout << "(1, 0) -> " << m(1, 0) << '\n';
  std::cout << "(1, 1) -> " << m(1, 1) << '\n';
  std::cout << "(2, 2) -> " << m(2, 2) << '\n';
}
```

こんな出力が得られます

```
3
9
(0, 0) -> 0
(0, 1) -> 3
(1, 0) -> 9
(1, 1) -> 12
(2, 2) -> 24
```

多分合ってそうです。

これを`mdspan`に組み込みます。`mdspan`のテンプレートパラメータは`mdspan<T, E, L, A>`の順で、今回`A`は弄らず`L`を変えたいためそこまでの3つのテンプレートパラメータの手動指定が必要です。

`mdspan`では少なくとも要素型とエクステント型は都度指定する必要があるので、`mdspan`を利用する際はあらかじめ必要なテンプレートパラメータを埋めた型エイリアスを作成しておくと便利です。

```cpp
// 3x3行列D個のインターリーブ配列を参照するmdspan
template <typename T, std::unsigned_integral auto D>
using interleaved_mat33 = mdspan<T, extents<std::size_t, 3, 3>, layout_right_interleaved<D>>;
```

これを、次のようなコードでテストすると

```cpp
// 3x3 mdspanを受け取り出力
template <typename T, typename L>
void print_mat(mdspan<T, extents<std::size_t, 3, 3>, L> mat33) {
  for (int y = 0; y < 3; ++y) {
    for (int x = 0; x < 3; ++x) {
      std::cout << mat33[y, x] << ' ';
    }
    std::cout << '\n';
  }
  std::cout << '\n';
}

int main() {
  // 3x3行列を3つインターリーブ
  int storage[] = {
    111, 211, 311, 112, 212, 312, 113, 213, 313,
    121, 221, 321, 122, 222, 322, 123, 223, 323,
    131, 231, 331, 132, 232, 332, 133, 233, 333
  };

  // それぞれの行列の先頭要素のポインタを渡す
  interleaved_mat33<int, 3u> A{storage};
  interleaved_mat33<int, 3u> B{storage + 1};
  interleaved_mat33<int, 3u> C{storage + 2};

  print_mat(A);
  print_mat(B);
  print_mat(C);
}
```

次のような出力が得られます

```
111 112 113 
121 122 123 
131 132 133 

211 212 213 
221 222 223 
231 232 233 

311 312 313 
321 322 323 
331 332 333 
```

- [Compiler Explorer (clang 16.0)](https://godbolt.org/z/x4xseK6GE)

どうも正しくインターリーブされた行列を参照できているようです。

今回のレイアウトポリシー型では先頭要素からの相対インデックスを計算するようにしたので`mdspan`の参照する領域は参照したい行列の先頭要素から始まる必要があり、初期化時には少なくとも先頭要素のアドレスを計算する必要があります。

### ストライドと`layout_stride`

先ほど求めたインターリーブレイアウトのインデックス計算の各次元でインデックスに対して固定的に積算されている値、例えば`idx = y * D * I + x * D`の`y`に対する`D * I`と`x`に対する`D`は各次元における要素のずらし幅となっています。例えば、`D = 1`（つまりインターリーブなし）とすると、通常の2次元インデックス計算の式に一致することがわかるでしょう。

このずらし幅は一般化されストライドと呼ばれ、多次元配列に対するストライドはこのインターリーブを含めてさまざまなレイアウトを表現することができます。

レイアウトマッピングクラス型のメンバ関数として要求されていた`is_strided()`と`is_allways_strided()`が`true`を返すとは、このストライドによってレイアウト計算されていることを表します。そして、レイアウトマッピングクラスに要求される`stride(r)`というのは、`r`次元におけるストライド（`r`次元のインデックスにかけられる係数）を求めるための関数です。それは`m`次元のサイズを`I(m)`と表すと、`n`次元のインデックス`in`に対して`D * I(n-1) * ... * I(0)`のように計算されます。

ストライドによってさまざまなレイアウトの配列を表現できることはよく知られているため、`mdspan`にはデフォルトで任意のストライドを扱うことのできるレイアウトポリシー型である`std::layout_stride`が用意されています。インターリーブレイアウトをハンドルするためにはこんな手間をかけてレイアウトポリシー型を自作しなくてもこれを使用すると簡単に処理できます。

`std::layout_stride`は各次元に対するストライドを手動で指定することで、任意のストライドによるレイアウトを表現することができます。ストライド値は、レイアウトマッピング型（`std::layout_stride::mapping`）のコンストラクタに`std::array`で渡します。

```cpp
// 要素型Tの3x3インターリーブ行列
template <typename T>
using stride_interleaved_mat33 = mdspan<T, extents<std::size_t, 3, 3>, layout_stride>;

int main() {
  // 3x3行列を3つインターリーブ
  int storage[] = {
    111, 211, 311, 112, 212, 312, 113, 213, 313,
    121, 221, 321, 122, 222, 322, 123, 223, 323,
    131, 231, 331, 132, 232, 332, 133, 233, 333
  };

  // レイアウトマッピング型取り出し
  using mapping = stride_interleaved_mat33<int>::mapping_type;

  // この場合の各次元のストライド（右側ほど低次元）
  // 要素型はextentsの要素型に変換できればなんでもいい
  constexpr std::array<std::size_t, 2> stride = {9, 3};

  // CTADによりテンプレートパラメータを推論している
  stride_interleaved_mat33 A{storage,     mapping{{}, stride}};
  stride_interleaved_mat33 B{storage + 1, mapping{{}, stride}};
  stride_interleaved_mat33 C{storage + 2, mapping{{}, stride}};

  print_mat(A);
  print_mat(B);
  print_mat(C);
}
```

- [Compiler Explorer (gcc13.1)](https://godbolt.org/z/Gv1qa9Wer)

この`layout_stride`に対する手間をかけて作成した`layout_right_interleaved`のメリットは

- ストライド計算の自動化
    - ストライドを手動で渡す必要がない
- ストライドの定数化が可能
    - エクステントが全て定数なら、後述
- オブジェクトごとにストライドを保持する必要がない
    - オブジェクトサイズの削減

などでしょうか。このメリットにこの手間が釣り合うと考える場合は自作する価値があるかもしれません（今回はお勉強のためなのでメリットとか無視してます）。

大抵のメモリレイアウトはストライドを工夫することで表現できるので、`mdspan`でカスタムレイアウトを取り扱おうと思い立った時はまず`layout_stride`の利用を検討してみるといいかもしれません。更なる最適化が欲しかったり、ストライドでは表現できない場合にレイアウトポリシー型の自作に進むと良いでしょう。

インターリーブレイアウトは`layout_stride`によって表現可能なので、`layout_right_interleaved`の特性は`layout_stride`のそれと同じになります。そのため、`required_span_size()`のような少し面倒な実装は`layout_stride`の実装を流用することができます。

### 静的エクステントの場合の最適化

ひとまず完成した`layout_right_interleaved`の実装は、`extents_type`（`std::extents`）の各次元の要素数が動的な場合でも対応可能な実装になっています。動作例がそうであるように、全ての次元の要素数がコンパイル時に既知であれば、計算の一部をコンパイル時に終わらせておくことができます。

エクステントが完全に静的であるか（動的エクステントが含まれていないかどうか）は、`std::extents`の静的メンバ関数である`rank_dynamic()`が`0`を返すかどうかで判定できます。これは静的`constexpr`関数なのでコンパイル時に呼び出すことができ、コンセプトなどの制約にも用いることができます。

まず、エクステントが静的である場合に、各次元のストライドをコンパイル時に求めておきます。

```cpp
template<std::unsigned_integral auto D>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
    [[no_unique_address]]
    Extents m_extent;
  public:
    using extents_type = Extents;
    using index_type = typename extents_type::index_type;
    using rank_type = typename extents_type::rank_type;
    using layout_type = layout_right_interleaved<D>;
  
  private:

    // コンパイル時のストライド計算
    static constexpr auto calc_static_stride() -> std::array<index_type, Extents::rank()> {
      // 動的エクステントの場合は空
      if constexpr (Extents::rank_dynamic() != 0) {
        return {};
      }

      // 全て静的なら、各次元のストライドを求める
      std::array<index_type, Extents::rank()> stride;

      stride[0] = D;

      for (auto i = 1u; i < Extents::rank(); ++i) {
        stride[i] = stride[i - 1] * Extents::static_extent(i - 1);
      }

      return stride;
    }

    // コンパイル時に求めたストライド
    static constexpr std::array<index_type, Extents::rank()> static_stride = calc_static_stride();

    ...
  };
};
```

静的メンバ変数として保存しておくことでコンパイル時に使用でき、オブジェクトのサイズを消費しないようにします。

次に、これを用いてインデックス計算周りを書き換えます。

```cpp
template<std::unsigned_integral auto D>
struct layout_right_interleaved {
  template <class Extents>
  class mapping {
    ...

    // コンパイル時に求めたストライド
    static constexpr std::array<index_type, Extents::rank()> static_stride = calc_static_stride();
  public:

    constexpr auto stride(rank_type r) const -> index_type
      requires (extents_type::rank() != 0)
    {
      assert(r < extents_type::rank());

      if constexpr (Extents::rank_dynamic() != 0) {
        index_type stride = D;

        for (auto i : std::views::iota(0u, r)) {
          stride *= m_extent.extent(i);
        }

        return stride;
      } else {
        // 全て静的ならあらかじめ計算したものを返す
        return static_stride[r];
      }
    }

    template<typename... Indices>
      requires (sizeof...(Indices) == extents_type::rank()) and
               (std::is_nothrow_convertible_v<Indices, index_type> && ...)
    constexpr auto operator()(Indices... indices) const -> index_type {
      // 行列次元数
      // extent()が0indexなので最大値は-1
      constexpr std::unsigned_integral auto N = extents_type::rank() - 1;
      static_assert(0u < N);

      // インデックス配列
      // indicesは先頭が最大次元、末尾が1次元
      const std::array<index_type, extents_type::rank()> idx_array = {static_cast<index_type>(indices)...};

      if constexpr (Extents::rank_dynamic() != 0) {
        // 動的エクステントを含む場合の計算

        index_type idx = idx_array[0];

        for (auto m = N - 1; const auto in : idx_array | std::views::drop(1)) {
          idx *= m_extent.extent(m);
          idx += in;
          --m;
        }

        return D * idx;
      } else {
        // 全て静的エクステントな場合の計算

        index_type idx = 0;

        // 求めたストライドは先頭が1次元になっているので、反転させる
        for (index_type i = 0; const auto st : static_stride | std::views::reverse) {
          idx += st * idx_array[i];
          ++i;
        }

        return idx;
      }
    }

  };
};
```

- [Compiler Explorer (gcc13.1)](https://godbolt.org/z/3YzM83GTc)

Compiler Explorerのアセンブリ出力対応の色付けを見ると、静的と動的の両方の処理がきちんと使われており、出力も正しいことがわかります。

あらかじめストライドが求めてある場合、各次元のインデックスに対応するストライドをかけて足すだけなので処理はだいぶ簡単になります。ここではやっていませんが、それによって畳み込み式で簡単に書けるようになると思われます。ただし、コンパイル時にストライドを求めるようにする場合でも、実行時の処理と掛け算と足し算の回数がほぼ変わらないのであまり効率的にはならないかもしれません。

また、`std::extents`はエクステントが全て静的である場合にサイズが1になるので、これによってエクステントが静的なら`layout_right_interleaved`は空のクラスとなりそのサイズも1になります（EBOが働く場合）。これは`mdspan`をコピーするときのコストを低下させることにつながります。

### ソースコード全体

- [mdspan_interleave_test.cpp](https://gist.github.com/onihusube/c57b4f8d3d60274578930300cf3d9a38)

### 参考文献

- [kokkos/mdspan : Reference implementation of mdspan targeting C++23](https://github.com/kokkos/mdspan)
- [`std::mdspan`×空間充填曲線 - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20230315/p1)
- [`std::mdspan` - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20230303/p1)
- [P0009R18 MDSPAN](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p0009r18.html)
- [P2604R0 MDSPAN: rename pointer and contiguous - ［C++］WG21月次提案文書を眺める（2022年06月）](https://onihusube.hatenablog.com/entry/2022/07/09/160343#P2604R0-MDSPAN-rename-pointer-and-contiguous)
- [インターリーブ配列 VBO](https://wgld.org/d/webgl/w088.html)
- [Introducing interleave-batched linear algebra functions in Arm PL - Arm Community blogs](https://community.arm.com/arm-community-blogs/b/tools-software-ides-blog/posts/new-interleave-batched-linear-algebra-functions-in-arm-pl)
- [Interleave - File Exchange - MATLAB Central](https://jp.mathworks.com/matlabcentral/fileexchange/65036-b-interleave-dim-a1-a2-a3-an)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2023/20230630_mdspan_layout_interleave.md)