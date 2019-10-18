# ［C++］コンセプトの5景

C++20にてついに導入されたコンセプト、書け方にムラがあるので少し整理してみます。

[:contents]

### 1. `typename`の代わりに

まず、従来`template<typename T>`と書いていたところの`typename`の代わりにコンセプト名を書けます。

```cpp
#include <concepts>
#include <iostream>

//環であるか？
template<typename T>
concept ring = requires(T a, T b) {
  {a + b} -> std::convertible_to<T>;
  {a * b} -> std::convertible_to<T>;
};

template<ring T>
void f(T&&) {
  std::cout << "T is ring" << std::endl;
}

template<typename T>
void f(T&&) {
  std::cout << "T is not ring" << std::endl;
}

//足し算だけはある型
struct S {
  S operator+(S);
};


int main() {
  f(10);
  f(1.0);
  f(S{});
  f(std::cout);
}

/*
出力
T is ring
T is ring
T is not ring
T is not ring
*/
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LpghRpU5Ou8y2XWV)

`ring`というコンセプトによって型が環であるかどうかを雑に判定しています。使用しているのは関数`f()`の1つ目のオーバーロードです。

```cpp
template<ring T>
void f(T&&);
```
従来`typename`か`class`を書いていた所にコンセプトを書けます。分かりやすいので基本的にはこう書かれることが多いのではないかと思います。  
標準ライブラリでコンセプトが使用される時も基本的にこの形で書かれています。

クラスの場合は次のようになります。

```cpp
#include <concepts>
#include <iostream>

template<typename T>
concept ring = requires(T a, T b) {
  {a + b} -> std::convertible_to<T>;
  {a * b} -> std::convertible_to<T>;
};


template<typename T>
struct wrap {
  static constexpr char Struct[] = "T is not ring";
};

template<ring T>
struct wrap<T> {
  static constexpr char Struct[] = "T is ring";
};


struct S {
  S operator+(S);
};

int main() {
  std::cout << wrap<int>::Struct << std::endl;
  std::cout << wrap<S>::Struct << std::endl;
}

/*
出力
T is ring
T is not ring
*/
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LpghRpU5Ou8y2XWV)

クラスの場合はオーバーロード？するのに部分特殊化を利用する必要がありますが、基本的には同じように書くことができます。

ただし、この方法では1つの型に1つの制約しかかけられません。制約を追加したい場合は新しくコンセプト定義を書かなければなりません。

```cpp
//環かつデフォルト構築可能と言う制約をかけようとしたができない・・・
template<ring && std::default_constructible T>
void f(T&&);
```


- メリット
  - 宣言が複雑にならない（相対的に）
- デメリット
  - 1つの型に1つの制約しかかけられない

以降、この`f()`と`wrap`だけを見ていくことにします。

### 2. 前置`requires`節

`requires`節というものを利用してテンプレートパラメータの宣言のすぐ後に制約を書きます。

```cpp
//関数
template<typename T>
requires ring<T>
void f(T&&);

//クラス
template<typename T>
requires ring<T>
struct wrap<T>;
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/q0p40Ds9ziHDE5ro)

この形では追加の制約をかけたいときに簡単に書くことができます。

```cpp
//デフォルト構築可能（std::default_constructible）と言う制約を追加する

//関数
template<typename T>
requires ring<T> && std::default_constructible<T>
void f(T&&);

//クラス
template<typename T>
requires ring<T> && std::default_constructible<T>
struct wrap<T>;
```

- メリット
  - `&&`や`||`で繋いで複数の制約をかけられる
- デメリット
  - 関数宣言が複雑になりうる

### 3. 後置`requires`節 ※関数のみ

先ほどの`requires`節、関数の後ろにも置けます。

```cpp
//関数
template<typename T>
void f(T&&) requires ring<T>;
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gvlBmYQnugYj2uBa)

ただし、クラスではこの書き方はできません。関数のみになります。

この書き方ではクラステンプレートの非テンプレートメンバ関数に対して制約をかけることができます。

```cpp
template<typename T>
struct wrap {
  T t;

  //Tが環である時のみfma()を使用可能
  T fma(T x) requires ring<T> {
    return t * x + t;
  }
};


struct S {
  S operator+(S);
};


int main() {
  wrap<int> wi{10};
  wrap<S> si{};
  
  std::cout << wi.fma(20) << std::endl; //ok、210
  si.fma({});   //コンパイルエラー
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/fmTWcGgVMigL2mbK)

この様な非テンプレート関数に制約をかけるにはこの書き方をするしかありません。

- メリット
  - `&&`や`||`で繋いで複数の制約をかけられる
  - 非テンプレート関数に制約をかけられる
- デメリット
  - 関数宣言が複雑になりうる
  - クラスで使えない

### 4. `auto`による簡略構文 ※関数のみ

C++20より通常の関数でもジェネリックラムダのように`auto`を使って引数を宣言できます。その際にコンセプトを添えることで制約をかけることができます。

```cpp
void f(ring auto&&);
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Bjwi5uc9Yd0LU9C0)

- メリット
  - 記述量が減る
  - 引数と制約の対応が分かりやすい
- デメリット
  - 1つの型に1つの制約しかかけられない
  - クラスで使えない
    - 非型テンプレートパラメータの時は使用可能


### 5. 1と2(or 3)

1の書き方に2の書き方を合わせて書くことで、基本制約+追加の制約みたいな気持ちを込めて書くことができます。標準ライブラリではこの形式で制約されていることが多いようです。

```cpp
//環でありデフォルト構築可能、という制約をする

//関数
template<ring T>
requires std::default_constructible<T>
void f(T&&);

//クラス
template<ring T>
requires std::default_constructible<T>
struct wrap<T>;
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/3TDeay27AdWxAVMw)

クラスでは使えませんがこの時に3の方法（関数名の後）で書いても大丈夫です。

- メリット
  - 複数の制約を少しすっきりと書ける
  - 基本+追加のような意味を込められる
- デメリット
  - 1つの型に対する制約が散らばるので見辛くなりうる

#### 4と3

一応書けますよ、という・・・

```cpp
void f(ring auto&& x) requires std::default_constructible<decltype(x)>;
```

あえてこういう書き方をしたいことがあるのか、わかりません・・・


#### 全部盛り

2つと言わずに全部使っても構いませんよ、もちろん！

```cpp
//関数
template<ring T>
requires ring<T>
void f(T&&) requires ring<T>;
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/P9xjSqlSaIrd189D)


### 参考文献
- [コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)

### 謝辞
この記事の9割は以下の方によるご指摘によって成り立っています

- [@yohhoyさん](https://twitter.com/yohhoy/status/1174356205369610241)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20191018_concept_functions.md)