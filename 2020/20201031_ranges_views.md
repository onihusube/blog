# ［C++］ `<range>`の*View*

## 前準備

### コンセプトによる定義

#### `range<T>`

```cpp
template<class T>
concept range =
  requires(T& t) {
    ranges::begin(t);
    ranges::end(t);
  };
```

#### `borrowed_range<T>`

```cpp
template<class T>
concept borrowed_­range =
  range<T> &&
  (is_lvalue_reference_v<T> || enable_borrowed_range<remove_cvref_t<T>>);

template<class>
inline constexpr bool enable_borrowed_range = false;
```

#### `sized_range<T>`

```cpp
template<class T>
concept sized_­range =
  range<T> &&
  requires(T& t) { ranges::size(t); };
```

#### `views<T>`

```cpp
template<class T>
concept view =
  range<T> && movable<T> && default_­initializable<T> && enable_view<T>;

template<class T>
inline constexpr bool enable_view = derived_from<T, view_base>;
```

#### *range*のカテゴリ

#### `common_range<T>`

```cpp
template<class T>
concept common_­range =
  range<T> && same_­as<iterator_t<T>, sentinel_t<T>>;
```
#### `viewable_range<T>`

```cpp
template<class T>
concept viewable_­range =
  range<T> && (borrowed_range<T> || view<remove_cvref_t<T>>);
```


### `view_interface`

### `subrange`

## *range factories*

### *View* 🤔

*range*ライブラリにおける*View*とは、他の所（言語、ライブラリ、概念・・・）での任意のシーケンスにおける*View*と呼ばれるものと同じ意味です。元のシーケンスに対して何か操作を適用した結果得られ、元のシーケンスをコピーせず参照し、かつ遅延評価によってシーケンスに操作を適用するものです。  
さらに、*View*自身もシーケンスなので、*View*に対してさらに他の処理を適用していくことができるようになっています。

*range*ライブラリにおける*View*はコンセプトによって次のように定義されます。

```cpp
template<class T>
concept view =
  range<T> &&                 // begin()/end()が共に呼び出し可能でイテレータを返す
  movable<T> &&               // ムーブ可能
  default_­initializable<T> && // デフォルト構築可能
  enable_view<T>;
```

- ムーブ構築/代入は定数時間
- デストラクトは定数時間
- コピー不可もしくは、コピー構築/代入は定数時間

これら全ての要件を満たしたものが*range*ライブラリにおける*View*として扱われます。

随分分かりづらいかもしれませんが意味するところはすなわち、任意の範囲（*range* : イテレータペア）を所有せず参照し、*View*自身の構築・コピー・ムーブ・破棄は参照する範囲とは無関係であるということです。  
これは同時に、一般的な意味の*View*であるための最低限の要求です。

#### `view_interface`

`<ranges>`にある*View*となるクラスは共通部分の実装を簡略化するために`view_interface`というクラスを継承しています。`view_interface`はCRTPによって派生クラス型を受け取り、派生している*View*に対してコンテナインターフェースを備えるためのものです。

これによって、*View*の保持する*range*の種類（すなわち、イテレータカテゴリ）によって`empty()/data()/size()/front()/back()/[]`と言った要素を参照する操作が利用可能となります。

```cpp
template<class D>
  requires is_class_v<D> && same_as<D, remove_cv_t<D>>
class view_interface : public view_base {
  // 略
};
```

`view_base`というのは単なるタグ型で、*View*となるクラスを識別するためのものです。

#### 名前空間



### `empty_view`


### `single_view`
### `iota_view`
### `basic_istream_view`

