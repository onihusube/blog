# ［C++］ `auto`によるキャスト

C++23から`auto(x)`の形式のキャストが可能になります。

```cpp
template<std::copy_constructible T>
void f(T x) {
  T p = auto(x);  // ok、C++23から
}
```

これに関連する仕様等のメモです。

[:contents]

### prvalueへのキャスト

`auto(x)`の形式のキャストは`x`をその型を`decay`した型の値としてキャストするものです。

型の`decay`とはその型からCV/参照修飾を取り除き、配列/関数はそのポインタに変換するものです。配列/関数以外の場合、`auto`によるキャストは`x`をその型の*prvalue*へキャストします。

そして、`auto(x)`のキャストは単なる型変換ではなく、キャスト結果の*prvalue*は`x`の値をコピーしたものになります。したがって、その結果は`x`とは異なるオブジェクトとして得られ、`x`の状態を変更しません（コピーコンストラクタが変なことしない限り）。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // auto(x)式の値カテゴリはprvalue
  static_assert(std::same_as<decltype(auto(x)), T>);

  // pとtは異なるオブジェクト（コピーされる）
  T p = auto(x);

  // auto(x)後もtの利用は安全
  x.use();

  // pに変更を加えてもtには波及しない
  p.mutate();

  // auto(x)は同じオブジェクトに対して何度も行える
  T p2 = auto(x);
}
```

コピーを行うため、`T`は`copy_constructible`である必要があります。`move_constructible`でしかない場合はキャストは失敗しコンパイルエラーとなります。

```cpp
struct no_copy {
  no_copy() = default;
  no_copy(const no_copy&) = delete;
};

int main() {
  non_copy nc{};

  non_copy cp = auto(nc); // ng
}
```

また、`auto(x)`だけでなく`auto{x}`も有効であり、どちらも同じ効果になります。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // どちらも同じprvalueへのキャスト
  T p1 = auto(x);
  T p2 = auto{x};
}
```

#### 細かい仕様の話

`auto(x)`の形式のキャストは明示的型変換（関数スタイルキャスト）の一種であり、型名の代わりに`auto`を使用するものです。この場合に使用可能なのは丁度`auto`のみで、`decltype`や`auto&`、`const auto&`だとかは使用できません。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // すべてコンパイルエラー
  decltype(x);
  auto&(x);
  auto&&(x);
  const auto&(x);
}
```

`auto(x)`の形式のキャストにおいては`auto`は他の所と同じくプレースホルダ型として扱われており、その型は`x`の型が推論された後で置き換えられます。その推論においては通常の`auto`の推論と同様に、単一のテンプレート引数をもちその型の引数を1つだけ受ける関数テンプレートに対して`x`を渡した時にそのテンプレートパラメータに推論される型が取得されます。

```cpp
// これらのautoに推論される型は
auto c = x;
auto(x);
auto f() { return x; }

// このような関数テンプレートに対して
template<typename T>
void hf(T);

// xをそのまま渡した時のTに推論される型として取得される
hf(x);
```

この場合の推論時に行われる`x`の型から修飾を取り除いたりポインタ型に変換したりといった調整を型に対する`decay`と呼び、結果の型は`std::decay_t<decltype((x))>`で得られる型と一致します。これは、配列型・関数型以外の場合は元の型に対して*prvalue*になります。

こうして取得された型を`T`とすると、`auto(x)`のプレースホルダ`auto`はこの型`T`で置き換えられ、`T(x)`として通常の関数スタイルキャストとして処理されます。この式は`x`をコピーして`T`の新しいオブジェクトを構築する式となります。これは`auto{x}`においても同様です。

```cpp
template<std::copy_constructible T>
void f(T x) {
  // この4つは実は同じ意味
  auto(x);
  T(x);
  auto{x};
  T{x};
}
```

`auto`を用いたキャストにおいては、`{}`の中の初期化式は1つだけでないとその型が推論できないため渡せる式は1つに限定され、`()`の場合はカンマ区切りの式とみなされやはり渡せる式は1つだけになります。また、推論の仕様上取得される型は`x`と修飾だけが異なる同じ型となるため、大きな型変換は起こりません。したがって、`()`と`{}`の違い（式の評価順序や縮小変換の禁止など）はここでは顕在化せず両方は真に同じ意味を持ちます。

文法上、`auto(x), auto{x}`の`x`には任意の式を渡すことができるため、必ずしも変数名のみに対して作用するわけではありません。とは言え、何が渡されたとしてもやることは変わらず、与えられる式の結果をその型の*prvalue*へキャストすることです。

```cpp
auto f() -> std::string;

int main() {
  std::vector vec = {1, 2, 3, 4};

  auto v1 = auto(vec);  // ok
  auto v2 = auto(std::move(vec)); // ok、以降vecの利用は安全ではない
  auto s1 = auto(f());  // ok
}
```

### decay-copy

### プライベートへのアクセス

### 例

### 参考文献

- [P0849R8 `auto(x)`: decay-copy in the language](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p0849r8.html)
- [`std::decay` - cpprefjp](https://cpprefjp.github.io/reference/type_traits/decay.html)
- [`decay-copy` - cpprefjp](https://cpprefjp.github.io/reference/exposition-only/decay-copy.html)