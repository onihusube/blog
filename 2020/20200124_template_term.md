# ［C++］特殊化？実体化？？インスタンス化？？？明示的？？？？部分的？？？？？

C++のテンプレートの用語は日本語に優しくなく、似た言葉がこんがらがってよく分からなくなります。分からないのでメモしておきます。

### 特殊化（*specialization*）

単に特殊化と言ったら、あるテンプレートに対してそのテンプレート引数を全て埋めた状態のものをさします。つまり、テンプレートを使った時、その使っている（もはやテンプレートではない）テンプレートのことをテンプレートの特殊化と呼びます。

```cpp
template<typename T>
struct S {
  T t;
};

template<typename T>
void f(T t) {
  return t;
}

// クラステンプレートSの特殊化
S<int> s{};     // S<int>
S s = {1.0};    // S<double>

// 関数テンプレートfの特殊化
f(10);          // f<int>
f<float>(1.0);  // f<double>
```

#### 明示的特殊化（*explicit specialization*）

あるテンプレートについて、テンプレートパラメータを全て埋めた状態の定義を追加することを明示的特殊化と呼びます。関数テンプレートやクラステンプレートについて特定の型に対する特殊処理を追加したい場合に行います。

明示的特殊化は全てのテンプレートパラメータが確定するため、もはやテンプレートではありません。

```cpp
template<typename T>
struct S {
  T t;
};

template<typename T>
void f(T t) {
  std::cout << t << std::endl
}

// S<int>は常にこちらが使用される
template<>
struct S<int> {
  t t = 10;
};

// f<int>は常にこちらが使用される
template<>
void f(int t) {
  std::cout << (2 * t) << std::endl
}
```

#### 完全特殊化

明示的特殊化のことです。

#### 部分特殊化（*partial specialization*）

明示的特殊化に対して、全てではなく一部のテンプレートパラメータだけを埋めた定義を追加することを部分特殊化と言います。必然的に、2つ以上のテンプレートパラメータを持つテンプレートでだけ行えます。また、これはクラステンプレートと変数テンプレートでしか行えません。

部分的特殊化と呼ばれることもあります。

部分特殊化は全てのテンプレートパラメータが確定していないので、まだテンプレートです。

```cpp
template<typename T, typename U>
struct P {
  T t;
  U u;
};


// Pの1つ目のパラメータだけを特殊化
template<typename U>
struct P<int, U> {
  int t = 10;
  U u;
};

// Pの2つ目のパラメータだけを特殊化
template<typename T>
struct P<T, double> {
  T t;
  double u = 1.0;
};
```

クラステンプレートに対して明示的・部分的特殊化を追加することを、クラステンプレートのオーバーロードと言うことがあります。

#### プライマリテンプレート（*primary template*）

明示的・部分特殊化において、大元の（一番最初に定義された）テンプレートのことをプライマリテンプレートと呼びます。

テンプレートの使用時には、明示的特殊化→部分特殊化→プライマリテンプレート、の順番に考慮されます。つまりは、テンプレート特殊化の半順序においてプライマリテンプレートの優先度は最低です。

### インスタンス化（実体化：*instantiation*）

あるテンプレートが特殊化された時、その特殊化にマッチする元のテンプレートのテンプレートパラメータに具体的な型が渡され、テンプレートの（2段階目の）コンパイルが行われることをテンプレートのインスタンス化と言います。これはまた、実体化とも呼ばれます。

```cpp
template<typename T>
struct S {
  T t;
};

template<typename T>
void f(T t) {
  std::cout << t << std::endl
}


S<int> s{};     // S<int>がインスタンス化される
S s = {1.0};    // S<double>がインスタンス化される

f(10);          // f<int>がインスタンス化される
f<float>(1.0);  // f<float>がインスタンス化される

S<int> s2{};    // S<int>はインスタンス化済
f(20);          // f<int>はインスタンス化済
```

このようにテンプレート使用時に自動的にインスタンス化が行われるため、これを暗黙的インスタンス化（*implicit instantiation*）と呼ぶことがあります。

ある特殊化についてのインスタンス化は翻訳単位につき一度だけ行われます。

#### 明示的インスタンス化（*explicit instantiation*）

暗黙的インスタンス化に頼らずに、あらかじめテンプレートをインスタンス化させておくことができます。そのようなインスタンス化（そのもの、もしくは方法・構文）のことを明示的インスタンス化と言います。

普通のテンプレートの宣言と少し変わった形の宣言で行います。

```cpp
template<typename T>
struct S {
  T t;
};

template<typename T>
void f(T t) {
  std::cout << t << std::endl
}

// S<int>の明示的インスタンス化
template struct S<int>;

// 関数テンプレートfの2種類の明示的インスタンス化
template void f(int);
template void f<int>(int);

S<int> s{};    // S<int>はインスタンス化済
f(10);         // f<int>はインスタンス化済
```

テンプレートは明示的インスタンス化をした場所でインスタンス化と定義が行われ、そのテンプレート内部から参照できるものもその明示的インスタンス化した場所に基づいて決定されます。

また、部分特殊化に対して明示的インスタンス化を行うこともできます。

#### 明示的インスタンス化の定義と宣言

実は、いわゆる`extern template`もまた明示的インスタンス化に含まれます。この時、`extern`の付かないものを明示的インスタンス化の定義（*explicit instantiation definition*）、`extern`の付くものを明示的インスタンス化の宣言（*explicit instantiation declaration*）と呼び分けています。

```cpp
template<typename T>
struct S {
  T t;
};

template<typename T>
void f(T t) {
  std::cout << t << std::endl
}

// 明示的インスタンス化の定義
template struct S<int>;
template void f(int);

// 明示的インスタンス化の宣言
extern template S<bool>;
extern template void f(bool);
```

ほぼ規格書でしかでてこない用語です。その用語と裏腹？に、意味するところは真逆になる上、使用されるときは*decralation*と言う言葉が何を指すのかわかりづらくなる効果を持ちます・・・

### 参考文献

- [テンプレートの明示的 (完全) 特殊化 - cppreference](https://ja.cppreference.com/w/cpp/language/template_specialization)
- [テンプレートの部分特殊化 - cppreference](https://ja.cppreference.com/w/cpp/language/partial_specialization)
- [13.9 Template instantiation and specialization[temp.spec]](http://eel.is/c++draft/temp.spec#temp.explicit-7.sentence-1)
- [`extern template` - cpprefjp](https://cpprefjp.github.io/lang/cpp11/extern_template.html)