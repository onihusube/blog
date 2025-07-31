# ［C++］ 擬mdarray

[:contents]

### mdspanとmdarray

C++23で追加された`std::mdspan`は多次元配列の汎用的なビューを表現できるクラス型です。

```cpp
#include <mdspan>
#include <print>

template<typename T>
using mat33 = std::mdspan<T, std::extents<std::size_t, 3, 3>>;

int main() {
  int storage[] = {
    0, 1, 2,
    3, 4, 5,
    6, 7, 8
  };

  mat33<int> array{storage};

  for (std::size_t y = 0; y < array.extent(0); ++y) {
    for (std::size_t x = 0; x < array.extent(1); ++x) {
      std::print("{} ", array[y, x]);
    }
    std::println("");
  }
}
```

- [Wandbox](https://wandbox.org/permlink/8MsXrGwXf4oBjRhb)

しかしこの例にあるように、`std::mdspan`はビューなので配列のデータ領域を参照しません。参照する領域は別に用意する必要があり、かつそこを別に管理する必要があります。

ビューではない多次元配列クラスの要望もあったため、`std::mdarray`という`std::mdspan`とインターフェース互換で領域を所有する多次元配列クラスの提案も行われていますが、C++29以降の機能になります。

```cpp
#include <mdarray>
#include <print>

template<typename T>
using mat33 = std::mdarray<T, std::extents<std::size_t, 3, 3>>;

int main() {
  std::vector<int> storage {
    0, 1, 2,
    3, 4, 5,
    6, 7, 8
  };

  mat33<int> array{std::extents<std::size_t, 3, 3>{}, std::move(storage)};

  for (std::size_t y = 0; y < array.extent(0); ++y) {
    for (std::size_t x = 0; x < array.extent(1); ++x) {
      std::print("{} ", array[y, x]);
    }
    std::println("");
  }
}
```

これは実行できれば先ほどと同じ結果になります。`std::mdarray`はデフォルトでは`std::vector`を内部に保持して、その領域を`std:mdspan`とほぼ同じインターフェースによってアクセスできるようにすることで非ビューの多次元配列クラスとなっています。

C++23でもこの`mdarray`のようなものが欲しくなることもあるでしょう。`std::mdspan`の柔軟なカスタマイズ性を活用すると、割と近いものを作ることができます。

### mdspanの構造と要件

`std:mdspan`のクラス構造はおおむね次のようになっています

```cpp
// mdspanクラス構造概要
namespace std {
  template<
    class T,                                    // 要素型
    class Extents,                              // エクステント型（次元数と次元ごとの要素数を指定する）
    class LayoutPolicy = layout_right,          // レイアウトポリシー型
    class AccessorPolicy = default_accessor<T>  // アクセサポリシー型
  >
  class mdspan {
  public:
    // アクセサポリシー型
    using accessor_type = AccessorPolicy;
    // レイアウトマッピングクラス型
    using mapping_type = 
      typename LayoutPolicy::template mapping<extents_type>;
    // データハンドル型
    using data_handle_type = 
      typename AccessorPolicy::data_handle_type;

    ...

  private:
    accessor_type acc_;
    mapping_type map_;
    data_handle_type ptr_;  // 参照する領域のデータハンドル
  };
}
```

これら各型の詳細などは以前の記事をご覧ください

- [［C++］ mdspanでインターリーブレイアウトを扱う - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2023/06/30/200303)

具体的なテンプレートパラメータが全て与えられた`std::mdspan`の特殊化の型を`MDS`とすると、`MDS`は次の要件を満たしている必要があります

- `copyable`のモデルとなる
- `is_nothrow_move_constructible_v<MDS>`が`true`
- `is_nothrow_move_assignable_v<MDS>`が`true`
- `is_nothrow_swappable_v<MDS>`が`true`

上記クラス構造からわかるように、`MDS`がこれらの性質を満たすには`accessor_type`・`mapping_type`・`data_handle_type`のすべてがこれらの性質を満たしている必要があります（このことはレイアウトポリシーとアクセサポリシーに求められる要件によって別に指定されます）。

これらメンバのうち、`data_handle_type`と言われているものが`mdspan`の対象領域を参照するもので、通常はポインタ型が使用されます。

### アクセサポリシーのカスタマイズ

`data_handle_type`がどのような型であるべきかはアクセサポリシー要件の中で指定されており、その条件は先ほどの`std::mdspan`の具体的な特殊化`MDS`に求められていたものと同じになります。そして、`data_handle_type`は`std::mdspan<T, ...>`に対して`T*`である必要はなく、先ほどの条件を満たす型でありさえすれば任意の型が使用できます。

この意図としてはファンシーポインタ型の様な型をサポートすることを意図しており、例えば`std::share_ptr<T[]>`が使用できます。ただもっと直接的に、`std::vector`も使用できます。

すなわち、`std::mdspan`のデータハンドル型をカスタマイズすることで`mdarray`の様な動作を得ることができます。そして、データハンドル型のカスタマイズはアクセサポリシーのカスタマイズによって行えます。

#### `std::vector`が要件を満たすこと

`std::vector<T>`が先ほどの要件

- `copyable`のモデルとなる
- `is_nothrow_move_constructible_v<std::vector<T>>`が`true`
- `is_nothrow_move_assignable_v<std::vector<T>>`が`true`
- `is_nothrow_swappable_v<std::vector<T>>`が`true`

を満たすことを一応確認しておきましょう。

`copyable`は言うまでもなく、`is_nothrow_move_constructible_v<std::vector<T>>`は標準コンテナのムーブコンストラクタは無条件`noexcept`が基本なので問題ありません。

残った2つは実は少し込み入っています。

```cpp
namespace std {
  template<class T, class Allocator = allocator<T>>
  class vector {
    ...

    constexpr vector& operator=(vector&& x)
      noexcept(allocator_traits<Allocator>::propagate_on_container_move_assignment::value ||
               allocator_traits<Allocator>::is_always_equal::value);
    
    ...

    constexpr void swap(vector&)
      noexcept(allocator_traits<Allocator>::propagate_on_container_swap::value ||
               allocator_traits<Allocator>::is_always_equal::value);
    
    ...
  };
}
```

どちらも結局アロケータ次第になります。

- `propagate_on_container_move_assignment` : ムーブ代入時にアロケータを伝播させるか
- `propagate_on_container_swap` : スワップ時にアロケータを交換するか
- `is_always_equal` : アロケータがオブジェクトによらず同等であるか（アロケータが状態を持つか）

デフォルトのアロケータ`std::allocator<T>`はこれらのうち`propagate_on_container_move_assignment`と`is_always_equal`が`true`（`true_type`として定義される）なので、どちらの条件も満たすことができ、上記の要件をすべてクリアできます。

ただ、`std::pmr::polymorphic_allocator`の場合だと逆にすべて満たさなかったりするので、アロケータのカスタマイズには注意が必要です。

### アクセサポリシーのカスタマイズ

アクセサポリシー型はアクセサポリシー要件を満たす任意の型を使用できます。その詳細はcpprefjpの[`AccessorPolicy`](https://cpprefjp.github.io/reference/mdspan/AccessorPolicy.html)等を見ていただくとして、おおむね`std::default_accessor`を真似すればokです。

```cpp
namespace std {
  // mdspanのデフォルトアクセサポリシー
  // データハンドルはポインタを使用する
  template<class ElementType>
  struct default_accessor {
    using offset_policy = default_accessor;
    using element_type = ElementType;
    using reference = ElementType&;
    using data_handle_type = ElementType*;

    constexpr default_accessor() noexcept = default;

    template<class OtherElementType>
      constexpr default_accessor(default_accessor<OtherElementType>) noexcept;
    
    constexpr reference access(data_handle_type p, size_t i) const noexcept;
    
    constexpr data_handle_type offset(data_handle_type p, size_t i) const noexcept;
  };
}
```

`std::mdspan`で使用されるデータハンドル型をカスタマイズするにはここのメンバ型`data_handle_type`をカスタマイズすればいいわけです。

名前を`vector_accessor`にするとして、実装は次のようになります

```cpp
template<class ElementType>
struct vector_accessor {
  using offset_policy = std::default_accessor<ElementType>;
  using element_type = ElementType;
  using reference = const ElementType&;
  using data_handle_type = std::vector<ElementType>;

  constexpr vector_accessor() noexcept = default;

  // 変換は基本的に考慮しないものとする
  
  constexpr reference access(const data_handle_type& p, size_t i) const noexcept {
    return p[i];
  }
  
  constexpr offset_policy::data_handle_type offset(const data_handle_type& p, size_t i) const noexcept {
    return p.date() + i;
  }
};
```

先ほど見たように、データハンドルそのものは`std::mdspan`内部で保存されています。要素アクセス時にはそれとレイアウトポリシーから計算された1次元インデックスによってここの`access()`関数が呼ばれることで要素アクセスが行われます。

`offset_policy`/`offset()`は`std::submdspan`（C++26）で`mdspan`から部分ビュー（スライス）を取得する際に領域のオフセット計算をするカスタマイズポイントです。`std::vector`をコピーして返すという事もできなくは無いと思いますが、それはもうスライスではないので、デフォルトの`std::mdspan`（ポインタ+`default_accessor`）にフォールバックしておきます。

このカスタムアクセサポリシーを使用するには、`std::mdspan<T, E, L, A>`の`A`に入れてやればokです。`vector_accessor`はステートレスなので`std::mdspan`のコンストラクタから渡す必要もありません。

このようなエイリアスを作っておくと便利かもしれません

```cpp
template<typename T, typename E, typename L = std::layout_right>
using my_mdarray = std::mdspan<T, E, L, vector_accessor<T>>;
```

先ほどの`mdarray`の動かないサンプルコードをこれで動かしてみると

```cpp
#include <mdspan>
#include <print>

template<typename T, typename E, typename L = std::layout_right>
using my_mdarray = std::mdspan<T, E, L, vector_accessor<T>>;

template<typename T>
using mat33 = my_mdarray<T, std::extents<std::size_t, 3, 3>>;

int main() {
  std::vector<int> storage {
    0, 1, 2,
    3, 4, 5,
    6, 7, 8
  };

  mat33<int> array{std::move(storage)};

  for (std::size_t y = 0; y < array.extent(0); ++y) {
    for (std::size_t x = 0; x < array.extent(1); ++x) {
      std::print("{} ", array[y, x]);
    }
    std::println("");
  }
}
```

- [Wandbox](https://wandbox.org/permlink/g6NgDeOKwi12nCUA)

この`my_mdarray`オブジェクトはコンストラクタで渡された`std::vector`を所有しており、コピーもムーブも自由にできます。通常の`std::mdspan`と異なり参照先領域が先に寿命が尽きないように計らう必要もありません。

### 制限

こうしてできた`my_mdarray`はほとんど`std::mdarray`と同じように扱うことができます。というか`std::mdarray`の実装は実質これと同じです（アクセサポリシーを介せず独自のクラス型として定義しているが）。例えば、`std::mdarray`は内部コンテナを自動で拡張したりしません。

ただし`std::mdspan`固有の制限があり、その点が少し異なります。

- 要素の変更ができない
    - `std::mdspan`の`operator[]`が`const`オーバーロードしかないため
    - 標準コンテナは`const`性を正しく伝播するため、非`const`参照を返せない
        - デフォルトの`std::mdspan`はポインタの間接参照時に`const`伝播が切れるため書き換えることができる
    - `std::mdarray`は`operator[]`の非`const`オーバーロードがあるため書き換え可能
- 内部`std::vector`はコンストラクタから渡さなければならない
    - コンストラクタで渡す以外に領域をセットする方法が無いため
      - 要素の変更ができないことと合わせると、領域の初期化も済ませておく必要がある
    - `std::mdarray`はコンストラクタで初期領域を確保しておくことができる

要素の変更ができないのはちょっと不便かもしれません・・・

ちなみに、データハンドルとして使用可能なものはインデックスアクセスさえできればいいので、単に`random_access_range`な`std::deque`や、前述のように`std::shared_ptr`を使用できます。少し特性が変わるものの、`std::shared_ptr`を使用する場合は要素の変更ができる領域所有`std::mdspan`を作成できます。

```cpp
#include <mdspan>
#include <memory>
#include <print>
#include <numeric>

template<class ElementType>
struct shared_ptr_accessor {
  using offset_policy = std::default_accessor<ElementType>;
  using element_type = ElementType;
  using reference = ElementType&; // referenceは非const
  using data_handle_type = std::shared_ptr<element_type[]>;

  constexpr shared_ptr_accessor() noexcept = default;

  constexpr reference access(const data_handle_type& p, size_t i) const noexcept {
    return p[i];  // ここでconst伝播を切ることができる
  }

  constexpr offset_policy::data_handle_type offset(const data_handle_type& p, size_t i) const noexcept {
    return p.get() + i;
  }
};

template<typename T, typename E>
using shared_mdarray = std::mdspan<T, E, std::layout_right, shared_ptr_accessor<T>>;

int main() {
  const std::size_t N = 3 * 3;
  auto p = std::make_shared<int[]>(N);
  std::ranges::iota(p.get(), p.get() + N, 0);

  shared_mdarray<int, std::extents<std::size_t, 3, 3>> ms1{p};

  for (std::size_t y = 0; y < ms1.extent(0); ++y) {
    for (std::size_t x = 0; x < ms1.extent(1); ++x) {
      std::cout << ms1[y, x] << " ";
    }
    std::cout << '\n';
  }
}
```

- [Wandbox](https://wandbox.org/permlink/qr0S7NGnYlrU22e0)

### 参考文献

- [P1648R5 `mdarray`: An Owning Multidimensional Array Analog of `mdspan`](https://wg21.link/P1684R5)
- [`std::mdspan` - cpprefjp](https://cpprefjp.github.io/reference/mdspan/mdspan.html)
- [`AccessorPolicy` - cpprefjp](https://cpprefjp.github.io/reference/mdspan/AccessorPolicy.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2025/20250731_pseoud_mdarray.md)
