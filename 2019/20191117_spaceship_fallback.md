# ［C++］宇宙船演算子のフォールバック処理

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

[:contents]

### なるべく`default`にお任せしたい

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

上記の場合、例えば`T`が`double`の時にエラーになります。しかし、`double`の時は普通に`default`実装が利用可能であるはずです・・・

```cpp
template<typename T>
struct wrap {
  T v;

  //この2つの宣言を両立できない・・・
  auto operator<=>(const wrap&) const = default;
  std::weak_ordering operator<=>(const wrap&) const = default;
};
```

この様な場合、指定する戻り値型が`T`に合わせて変化すればいいはずです。つまり、`T`が`<=>`を使用可能ならその戻り値型を指定し、使用可能でないなら特定の比較カテゴリ型を指定する、という風になればいいわけです。

```cpp
template<typename T, typename Cat>
using fallback_comp_cat = std::conditional_t<std::three_way_comparable<T>, std::compare_three_way_result_t<T>, Cat>;
```

そこでこの様なマジックアイテムを用意します。これを使って先ほどの`<=>`宣言を修正します。

```cpp
template<typename T>
struct wrap {
  T v;

  //Tが<=>を使用可能ならそれを使って、そうでないなら< ==を利用して、<=>をデフォルト実装
  fallback_comp_cat<T, std::weak_ordering> operator<=>(const wrap&) const = default;
};
```

この様にすることで`T`が`<=>`を使用可能であるかに関わらず、1つの宣言から`<=>`のデフォルト実装を利用することができます。

```cpp
//<=>を実装していない型
struct no_spaceship {
  int n;

  bool operator<(const no_spaceship& that) const noexcept {
    return n < that.n;
  }

  bool operator==(const no_spaceship& that) const noexcept {
    return n == that.n;
  }
};

int main()
{
  wrap<no_spaceship> t1 = {{20}}, t2 = {{30}};

  std::cout << std::boolalpha;

  //全て利用可能！
  std::cout << (t1 <=> t2 < 0) << std::endl;
  std::cout << (t1 <  t2) << std::endl;
  std::cout << (t1 <= t2) << std::endl;
  std::cout << (t1 >  t2) << std::endl;
  std::cout << (t1 >= t2) << std::endl;
  std::cout << (t1 == t2) << std::endl;
  std::cout << (t1 != t2) << std::endl;
}
```

特に、`default`実装にしておくことで`==`を暗黙宣言してもらえるのはとても嬉しいです。

ところで`fallback_comp_cat`とは一体・・・

```cpp
template<typename T, typename Cat>
using fallback_comp_cat = std::conditional_t<std::three_way_comparable<T>, std::compare_three_way_result_t<T>, Cat>;
```

`three_way_comparable<T>`はC++20から利用可能になる、型が三方比較可能であることを表明するコンセプトです。コンセプトの制約式そのものは`bool`値を生成する定数式として利用可能です。  
それを`conditional_t`の条件とすることで、`T`が`<=>`を利用可能であるかに応じて型を変化させます。

利用可能なら、`compare_three_way_result_t<T>`（これもC++20から利用可能）によってその戻り値型を、利用不可能ならば指定したカテゴリ型（`Cat`）を返します。

これによって、`fallback_comp_cat<T, Cat>`は`T`が`<=>`を利用可能なときはその戻り値型になり、利用できなければ指定したカテゴリ型`Cat`になるわけです。

これを`default`な`<=>`の戻り値型に指定してやることで、`T`の型に応じて自動で最適な`default`実装を選択してもらうようにするわけです。

### defaultを諦めて更にフォールバックする

しかし`T`が`==`を持っていなかったらどうしましょうか・・・  
さすがにそうなるともうコンパイラに頼ることは出来ません。  
そのような場合でも、なんとか`<`演算子だけから`<=>`を構成したいものです。

弱順序（`weak_orderin`）における順序付けにおいてなら、`!(a < b) && !(b < a)`ならば`a == b`と判断することができます。  
そこで、先ほどと同じ感じで`<=>`を使用可能であるか否かで分けることにしましょう。

```cpp
template<typename T>
concept less_than_compareble = requires(T a, T b) {
  //<演算子が利用可能であり、戻り値型がbooleanコンセプトを満たすこと
  {a < b} -> boolean;
}

auto fallback_cmp_3way = []<typename T>(const T& a, const T& b)
requires less_than_compareble<T>
{
  if constexpr (std::three_way_comparable<T>) {
    //<=>が使えるならそれを使う
    return a <=> b;
  } else if constexpr (less_than_compareble<T> && std::equality_comparable<T>) {
    //==と<を使って三方比較
    if (a == b) return std::weak_ordering::equivalent;
    if (b < a) return std::weak_ordering::less;
    return std::weak_ordering::greater;
  } else {
    //<だけから三方比較
    if (a < b) return std::weak_ordering::less;
    if (b < a) return std::weak_ordering::greater;
    return std::weak_ordering::equivalent;
  }
};
```

またこんなマジックアイテムを用意して、これを利用して`<=>`を定義します。

ちなみに、`std::equality_comparable`というのはC++20から標準で用意されてるコンセプトで、その名の通り`==`による比較が可能であることを表明します。

```cpp
template<typename T>
struct wrap {
  T v;

  auto operator<=>(const wrap& that) const -> decltype(fallback_cmp_3way(v, that.v)) {
    return fallback_cmp_3way(v, that.v);
  }
};
```

こうすることで、`T`が`<=>`を持っていなかったとしても、最悪`<`だけから`<=>`を構成することができるようになります。

なお、`<`演算子すら持っていなかったらもはや諦めるしかないでしょう・・・

#### 一般化

先ほどの`fallback_cmp_3way`は一つの型`T`の間でのみ`<=>`を構成しますが、二つの型の間で同じことをするように一般化しておきたくなってしまうでしょう。

ほとんどそのまま、`T, U`の2つの型を受け取るように関連するものを書き換えます。


```cpp
template<typename T, typename U>
concept less_than_compareble_with = requires(T a, U b) {
  //<演算子が利用可能であり、戻り値型がbooleanコンセプトを満たすこと
  {a < b} -> boolean;
  {b < a} -> boolean;
}

auto fallback_cmp_3way = []<typename T, typename U>(const T& a, const U& b)
requires less_than_compareble_with<T, U>
{
  if constexpr (std::three_way_comparable_with<T, U>) {
    //<=>が使えるならそれを使う
    return a <=> b;
  } else if constexpr (less_than_compareble_with<T, U> && std::equality_comparable_with<T, U>) {
    //==と<を使って三方比較
    if (a == b) return std::weak_ordering::equivalent;
    if (b < a) return std::weak_ordering::less;
    return std::weak_ordering::greater;
  } else {
    //<だけから三方比較
    if (a < b) return std::weak_ordering::less;
    if (b < a) return std::weak_ordering::greater;
    return std::weak_ordering::equivalent;
  }
};
```

`< ==`演算子が利用可能かを調べる両コンセプトは`T, U`の順番に関わらず比較可能である事をチェックするために、引数順を入れ替えて両方向から比較可能かをチェックしておきます。  
ただし、`==`演算子だけは片方しか使わないので、この用途だけを目的とするならばチェックするのは片方だけでよいかもしれません。

`std::three_way_comparable_with`はC++20より標準で用意されるコンセプトで、2つの型の間で`<=>`による比較が使用可能であることを表明します。`std::equality_comparable_with`も`==`について同様のものです。


### 同値比較演算子の導出

`<=>`を自前定義してしまうと`==`はもはや暗黙に宣言されなくなります。そもそも、`T`が`==`を利用可能でないの場合は`default`な`==`も利用可能ではありません。  
そのため、`<=>`と同様に`==`も自分で定義してあげる必要があります。

凄く楽をするのであれば、定義済みの`<=>`を用いて実装することができます。

```cpp
template<typename T>
struct wrap {
  T v;

  auto operator<=>(const wrap& that) const -> decltype(fallback_cmp_3way(v, that.v)) {
    return fallback_cmp_3way(v, that.v);
  }

  bool operator==(const wrap& that) const {
    //<=>を使って同値比較
    retunr (*this <=> that) == 0;
  }
};
```

しかし、`T`の`==`が使えるのならそれを使いたいのが世の常というものでしょう・・・

```cpp
template<typename T>
struct wrap {
  T v;

  auto operator<=>(const wrap& that) const -> decltype(fallback_cmp_3way(v, that.v)) {
    return fallback_cmp_3way(v, that.v);
  }

  //普段はdefault任せ
  bool operator==(const wrap& that) const = default;

  //Tの==が使えないときにこちらを使用
  bool operator==(const wrap& that) const
    requires (!std::equality_comparable<T>)  //==演算子が使用可能でない
  {
    //<=>を使って同値比較
    retunr (*this <=> that) == 0;
  }
};
```

`T`が`==`を使える時はデフォルト実装を使います。この場合、もう片方の`==`は制約（`!std::equality_comparable<T>`）を満たさないので曖昧にはなりません。  
そして、`T`の`==`が使えない場合は`wrap`のデフォルトな`==`は暗黙`delete`され、もう片方は制約を満たすことから使用可能になり、やはり曖昧にはなりません。

#### 参照型メンバがあるとき

これで完璧！と思われますが、比較演算子はデフォルト実装に頼ってしまうと`T`が参照型の時に実装されないという問題に直面するかもしれません。

となれば、参照型のためのケアも必要になります。  
そんなに難しいことは無く、非デフォルトの方に制約を一つ追加するだけです。

```cpp
template<typename T>
struct wrap {
  T v;

  auto operator<=>(const wrap& that) const -> decltype(fallback_cmp_3way(v, that.v)) {
    return fallback_cmp_3way(v, that.v);
  }

  //普段はdefault任せ
  bool operator==(const wrap& that) const = default;

  //Tの==が使えないかTが参照型のときはこちらを使用
  bool operator==(const wrap& that) const
    requires (!std::equality_comparable<T> || std::is_reference_v<T>)
  {
    //<=>を使って同値比較
    retunr (*this <=> that) == 0;
  }
};
```

非デフォルトの方の制約に`std::is_reference_v<T>`を`||`で追加します。こうすることで、`T`の`==`が使用可能でないか`T`が参照型の時にのみ非デフォルトの`===`が仕様可能になります。  
そして、その場合はいずれもデフォルトの方は暗黙`delete`されているので曖昧にはなりません。

とはいえ先ほど同様、`T`が参照型であっても`==`演算子は本来参照先の型による比較になります。となれば、それを使えると良いですよね・・・

```cpp
template<typename T>
struct wrap {
  T v;

  auto operator<=>(const wrap& that) const -> decltype(fallback_cmp_3way(v, that.v)) {
    return fallback_cmp_3way(v, that.v);
  }

  //普段はdefault任せ
  bool operator==(const wrap& that) const = default;

  //Tの==が使えないかTが参照型のときはこちらを使用
  bool operator==(const wrap& that) const
    requires (!std::equality_comparable<T> || std::is_reference_v<T>)
  {
    if constexpr (std::equality_comparable<T>) {
      //Tが==を使えるのならばそれを使う
      return v == that.v;
    } else {
      //<=>を使って同値比較
      retunr (*this <=> that) == 0;
    }
  }
};
```

`if constexpr`と`std::equality_comparable`でさらに分岐させます。  
オーバーロードにしてしまうのも良いかもしれませんが、コンセプトのオーバーロードの半順序は複雑なのでお勧めしません・・・

実は、union-likeな型（共用体そのものか匿名共用体をメンバに持つ型）でも同じ問題が起きますが、それを解決することは難しいので触れないでおきます・・・

### pairのような型に対しての拡張

今まで見てきた`wrap`はしょせん1つのテンプレートパラメータしか受け取らない型です。`std::pair`のように、2つ以上の型を受けるものに対しても同じことがしたいことがあるかもしれません。

とはいえ難しくは無く、型が増えた分制約が増えるだけです。

```cpp
template<typename T, typename U>
struct my_pair {
  T first;
  U second;

  auto operator<=>(const my_pair& that) const
    -> std::common_comparison_category_t<decltype(fallback_cmp_3way(first, that.first)), decltype(fallback_cmp_3way(second, that.second))>
  {
    if (auto comp = fallback_cmp_3way(first, that.first); comp != 0) return comp;
    return fallback_cmp_3way(second, that.second);
  }

  //普段はdefault任せ
  bool operator==(const my_pair& that) const = default;

  //TかUの==が使えないかTかUが参照型のときはこちらを使用
  bool operator==(const my_pair& that) const
    requires (
      (!std::equality_comparable<T> || !std::equality_comparable<U>) ||
      (std::is_reference_v<T> || std::is_reference_v<U>)
    )
  {
    if constexpr (std::equality_comparable<T> && std::equality_comparable<U>) {
      //==を使えるのならばそれを使う
      return first == that.first && second == that.second;
    } else {
      //<=>を使って同値比較
      retunr (*this <=> that) == 0;
    }
  }
};
```

`std::common_comparison_category`は`<=>`の正しい戻り値型である比較カテゴリ型を複数受け取り、変換可能な最も強い型（共通比較カテゴリ型）を返すメタ関数です。

まあすでに非デフォルト`==`の宣言がおかしなことになっています、もうちょっと数が増えたら考えたくないですね・・・。

### 番外編、変換可能な型との比較

`wrpa<T>`の`T`に変換可能な型`U`との比較演算子を実装したくなることもあるんじゃないでしょうか。

`fallback_cmp_3way`はさっき2つの型の間で比較できるようになったのでそのまま使えそうです。  
`==`は異種型間比較の場合全く`default`に頼れないので、それによる困ったことを考慮する必要は無さそうです。

```cpp
template<typename T>
struct wrap {
  T v;

//---自分自身との比較用---

  auto operator<=>(const wrap& that) const -> decltype(fallback_cmp_3way(v, that.v)) {
    return fallback_cmp_3way(v, that.v);
  }

  //普段はdefault任せ
  bool operator==(const wrap& that) const = default;

  //Tの==が使えないかTが参照型のときはこちらを使用
  bool operator==(const wrap& that) const
    requires (!std::equality_comparable<T> || std::is_reference_v<T>)
  {
    if constexpr (std::equality_comparable<T>) {
      //Tが==を使えるのならばそれを使う
      return v == that.v;
    } else {
      //<=>を使って同値比較
      retunr (*this <=> that) == 0;
    }
  }

//---変換可能な型との比較用---

  template<typename U>
  auto operator<=>(const U& other) const -> decltype(fallback_cmp_3way(v, other))
  requires std::convertible_to<U, T>
  {
    return fallback_cmp_3way(v, other);
  }

  template<typename U>
  bool operator==(const U& other) const
  requires std::convertible_to<U, T>
  {
    if constexpr (std::equality_comparable_with<T, U>) {
      //T, U間で==を使えるのならばそれを使う
      return v == other;
    } else {
      //<=>を使って同値比較
      retunr (*this <=> other) == 0;
    }
  }
};
```
変換可能な型との比較用のものには、それをチェックするために`std::convertible_to`コンセプトによって制約をかけておきます。  
あとは、`<=>`はほぼそのまま、`==`は`T`と`U`の間で`==`を使えるかをチェックするだけです。

なお、`requires`節をどこに置くかは好みで好きにしてください。

### 参考文献

- [一貫比較 - cpprefjp](https://cpprefjp.github.io/lang/cpp20/consistent_comparison.html)
- [［C++］素敵な宇宙船演算子（<=>） - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/01/13/180100)
- [`<compare>` - cpprefjp](https://cpprefjp.github.io/reference/compare.html)
- [`<compare>` - cppreference](https://ja.cppreference.com/w/cpp/header/compare)
- [コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [`<concpet>` - cpprefjp](https://cpprefjp.github.io/reference/concepts.html)
- [`<concpet>` - cppreference](https://ja.cppreference.com/w/cpp/header/concepts)
- [P1186R3 When do you actually use <=>?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p1186r3.html)
- [P1614R2 The Mothership has Landed (Adding <=> to the Library)](http://wg21.link/p1614)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20191117_spaceship_fallback.md)