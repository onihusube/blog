# ［C++］宇宙船演算子のフォールバック処理


### 動機

宇宙船演算子の導入によって比較演算子の定義が著しく楽になります。ただ、テンプレートな所ではそう単純にはいかない事もあります。

```cpp
template<typename T>
struct wrap {
  T v;

  auto operator<=>(const wrap&) const = default;
  //Tが<=>を持っていなかったら？
  //Tが参照型だったら？？？
};
```

例えばこの様に任意の型を保持するようなクラステンプレートです。この様な型は標準ライブラリにも`pair`、`tuple`や`optional`などがあります。  
このような型では`T`によっては`<=>`がそのまま利用できないかもしれません・・・

この様な時でも`<=>`だけを書くのがC++20からのC++でしょう。しかし、そんな時でもなるべく楽をしたい・・・


### なるべく`default`にお任せする

与えられた`T`が`<=>`を定義しておらず利用可能でなかったとしても、比較カテゴリ型の指定と`< ==`演算子から`default`な`<=>`を実装する仕組みがあります。

```cpp
template<typename T>
struct wrap {
  T v;

  std::weak_ordering operator<=>(const wrap&) const = default;
};
```

この様に明示的に戻り値型を指定することで、`T`が持つ`< ==`演算子が利用可能であればそれらを用いて`<=>`を実装してもらうことができます。

しかし、この様に書いてしまうと逆に`<=>`を使用可能な型に対して戻り値型を明示してしまうことになり、`T`の`<=>`が返す比較カテゴリ型が指定したものに変換可能でなければコンパイルエラーを引きおこします。

### それでも自前実装するとき

### 参照型メンバがあるとき

### 同値比較演算子の導出

### 参考文献

- [一貫比較 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/consistent_comparison.html)
- [P1186R3 When do you actually use <=>?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1186r3.html)
- [P1614R2 The Mothership has Landed (Adding <=> to the Library)](http://wg21.link/p1614)
