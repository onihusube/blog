# ［C++］クラス/変数テンプレートとコンセプト

### クラス/変数テンプレートに対する制約

クラス/変数テンプレートに対するコンセプトによる制約は、後置`requires`節が使用できないことを除いて関数テンプレートと同様に行うことができます。

```cpp
// クラステンプレートに対する制約の例

template<typename T>
struct S1 {
  static constexpr int N = 1;
};

template<std::integral T>
struct S1<T> {
  static constexpr int N = 2;
};

template<typename T>
struct S2 {
  static constexpr int N = 1;
};

template<typename T>
  requires std::integral<T>
struct S2<T> {
  static constexpr int N = 2;
};
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/hC6jLc8SdOae6avW)


```cpp
// 変数テンプレートに対する制約の例

template<typename T>
constexpr int v1 = 1;

template<std::integral T>
constexpr int v1<T> = 2;

template<typename T>
constexpr int v2 = 1;

template<typename T>
  requires std::integral<T>
constexpr int v2<T> = 2;
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/1YJCoGrNTglbZmjC)


クラス/変数テンプレートではオーバーロードを表現するためには部分特殊化を使用する必要がありますが、ほぼ関数テンプレートと同じような雰囲気で使用可能です。

### プライマリテンプレートへの制約

先程の例では、プライマリテンプレートに制約を行わず、部分特殊化に対してのみ制約を行っていました。

ここでそれを逆にしてみましょう


```cpp
// プライマリテンプレートに制約してみる

template<std::integral T>
struct S1 {
  static constexpr int N = 2;
};

template<typename T>
struct S1<T> {
  static constexpr int N = 1;
};

template<std::integral T>
constexpr int v1 = 2;

template<typename T>
constexpr int v1<T> = 1;
```

- [インスタンス化しない場合](https://wandbox.org/permlink/2QnOstutQjr4YdBm)
- [インスタンス化する場合](https://wandbox.org/permlink/QrTARrcnapIP5hF5)

謎のエラーが出ました。インスタンス化しない場合のエラーを見てみると

```
prog.cc:10:8: error: class template partial specialization does not specialize any template argument; to define the primary template, remove the template argument list
struct S1<T> {
       ^ ~~~
prog.cc:9:10: error: type constraint differs in template redeclaration
template<typename T>
         ^
prog.cc:4:15: note: previous template declaration is here
template<std::integral T>
              ^
prog.cc:18:15: error: variable template partial specialization does not specialize any template argument; to define the primary template, remove the template argument list
constexpr int v1<T> = 1;
              ^ ~~~
```

クラステンプレートの部分特殊化はどのテンプレート引数も特殊化していない、みたいに言われていて、変数テンプレートもほぼ同じメッセージです。どゆこと？？

インスタンス化した場合のエラーメッセージには少しヒントを見ることができます。

```
prog.cc:22:16: error: constraints not satisfied for class template 'S1' [with T = float]
  std::cout << S1<float>::N << '\n';
               ^~~~~~~~~
prog.cc:4:15: note: because 'float' does not satisfy 'integral'
template<std::integral T>
              ^
/opt/wandbox/clang-13.0.0/include/c++/v1/concepts:198:20: note: because 'is_integral_v<float>' evaluated to false
concept integral = is_integral_v<_Tp>;
                   ^
prog.cc:24:16: error: constraints not satisfied for variable template 'v1' [with T = float]
  std::cout << v1<float> << '\n';
               ^~~~~~~~~
prog.cc:14:15: note: because 'float' does not satisfy 'integral'
template<std::integral T>
              ^
/opt/wandbox/clang-13.0.0/include/c++/v1/concepts:198:20: note: because 'is_integral_v<float>' evaluated to false
concept integral = is_integral_v<_Tp>;
```

`float`で特殊化した場合に、`std::integral`が満たされずにエラーが出ているようです。いやそもそも、`std::integral`が満たされない場合は部分特殊化が選択されてほしいはずなのですが・・・？

### 部分特殊化の制限

クラステンプレートでも変数テンプレートでも、部分特殊化のテンプレートパラメータリスト（型名の後の`<Ts...>`）に対して次の制限がかけられています（[[temp.spec.partial]/9](http://eel.is/c++draft/temp.spec.partial#general-9)）

1. 非型テンプレート引数が特殊化されるとき、その型が部分特殊化のテンプレートパラメータに依存してはならない
2. 部分特殊化は、プライマリテンプレートよりも特殊化（*more specialized*）されていなければならない
      - *more specialized*の判定には[部分特殊化の半順序ルール](http://eel.is/c++draft/temp.spec.partial.order)が適用される
      - 部分特殊化の半順序は、クラス/変数テンプレートを関数テンプレートに変換して関数テンプレートの半順序を適用する
3. 部分特殊化のテンプレートパラメータリストはデフォルト引数を含んではならない
4. 実引数には未展開のパラメータパックを含めることはできない。実引数がパック展開の場合、テンプレート引数リストの最後に来なければならない

先程のエラーの原因となっていたのは、この2つ目の規則に抵触しているからです。

単純には、プライマリテンプレートのパラメータリストに対して、部分特殊化のパラメータリストの数の対応が取れていて、部分特殊化のパラメータのうち1つでも型が確定していれば、プライマリテンプレートよりも特殊化されています。これは部分特殊化の最も基本的な使用法に対応しています。

型が確定していなくても、SFINAEやコンセプトによってプライマリテンプレートが無効化される場合でも、部分特殊化の方がより特殊化されています。今回の例はこちらに対応しています。つまり、先程の謎のエラーが起きていたのは、部分特殊化よりもプライマリテンプレートの方がより特殊化されていたためです。

その判定では、最終的に関数テンプレートのオーバーロード解決のルールが適用されますが。今回の場合はそこに影響する要素はコンセプトによる制約のみです。従って考慮すべきはコンセプトの半順序となります。コンセプトの半順序ルールは複雑ですが、少なくとも制約されていない候補（ここでは部分特殊化）よりも制約されている候補（ここではプライマリテンプレート）の方が優先順位が高くなります。

このように、プライマリテンプレートに制約を行って部分特殊化に何も制約を行わない場合、部分特殊化はプライマリテンプレートよりも特殊化されなくなり（むしろプライマリテンプレートがより特殊化され）、部分特殊化としての基本要件を満たさないためコンパイルエラーとなっていたわけです。

このことは直感的にも、プライマリテンプレートの`T`が`std::integral`を要求するのに、部分特殊化の対応する`T`が無制約なのは特殊化になっていなくない？と気づくことができるかもしれません。私は気付きませんでした。

#### コンセプトによって順序を付ける

エラーになっていた原因がコンセプトによる優先順位付けにある事が分かったので、その解決のためにはコンセプトによって順序付けを正しく行えばよいわけです。

```cpp
template<std::integral T>
struct S1 {
  static constexpr int N = 2;
};

template<std::signed_integral T>
struct S1<T> {
  static constexpr int N = 1;
};

template<std::integral T>
constexpr int v1 = 2;

template<std::signed_integral T>
constexpr int v1<T> = 1;
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/7MuEyYIKw71S8nVr)

とはいえ、コンセプトの順序を適切に判断するのも難しいものがあるので、プライマリテンプレートには制約を行わないことが推奨されます。

### プライマリテンプレートと部分特殊化の順序

クラステンプレートでも変数テンプレートでも、オーバーロード（部分特殊化）の解決は関数テンプレートの半順序ルールを応用して行われます。そのルールは

1. 一致する部分特殊化が一つだけ見つかった場合は、それを選択
2. 一致する部分特殊化が複数見つかった場合は、[部分特殊化の半順序ルール](http://eel.is/c++draft/temp.spec.partial.order)により最も特殊化されている部分特殊化を選択する。最も特殊化された部分特殊化が複数ある場合はコンパイルエラー
3. 一致する部分特殊化が見つからなかった場合、プライマリテンプレートが選択される

となっています。すなわち、コンセプトを無視するとプライマリテンプレートと部分特殊化の間では部分特殊化の方が優先順が高くなっています。

つまり、コンセプトによってクラス/変数テンプレートをオーバーロードする場合、適切な順序付けを行うためには、まずコンセプトによる順序付けによって部分特殊化をより制約されている状態にして、プライマリテンプレートよりも部分特殊化が優先されるという事情を理解して、そのうえで部分特殊化の間で優先順序を制御する必要があります（このことはSFINAEでも同様ですが）。

言うまでもなくこれは、関数テンプレートのオーバーロード時よりも考えることが増えており複雑です。そのため、クラス/変数テンプレートのオーバーロードにおいては、プライマリテンプレートに制約をせず無効化（定義なし）したうえで部分特殊化だけを用いてオーバーロードを定義することが推奨されます。そうしておけば、すくなくともプライマリテンプレート周りの順序を気にする必要が無くなります。このような運用は、[`<numbers>`](https://cpprefjp.github.io/reference/numbers.html)の変数定義とその実装に見ることができます（おそらく）。

### おまけ : 変数テンプレートでできること

変数テンプレートはクラステンプレートとほぼ同じことができるのですが、そのことはあまり一般的に知られていないようです。特に、部分特殊化周りの仕様はクラステンプレートと共有されています。

```cpp
// detection idiom 普通の実装
template<class, template<class> class, class = void>
struct detect : std::false_type {};

template<class T, template<class> class Check>
struct detect<T, Check, std::void_t<Check<T>>> : std::true_type {};

// detection idiom 変数テンプレート版
template<class, template<class> class, class = std::void_t<>>
inline constexpr bool detect_v = false;

template<class T, template<class> class Check>
inline constexpr bool detect_v<T, Check, std::void_t<Check<T>>> = true;

// チェッカー実装
template<class T>
using check_equality_comparable = decltype(std::declval<const T&>() == std::declval<const T&>());

template<class T>
using check_iterator_type = typename T::iterator;

// 何も満たさない型
struct S {
  int n;
};


int main() {
  std::cout << std::boolalpha;

  std::cout << detect<int, check_equality_comparable>::value << '\n';
  std::cout << detect_v<int, check_equality_comparable> << '\n';
  
  std::cout << detect<S, check_equality_comparable>::value << '\n';
  std::cout << detect_v<S, check_equality_comparable> << '\n';
  
  std::cout << detect<std::vector<int>, check_iterator_type>::value << '\n';
  std::cout << detect_v<std::vector<int>, check_iterator_type> << '\n';
  
  std::cout << detect<S, check_iterator_type>::value << '\n';
  std::cout << detect_v<S, check_iterator_type> << '\n';
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/oNXGCk4JxjQrEM8O)


これがあまり知られていない（ように思える）のは、以前の変数テンプレートの仕様が曖昧で、特に部分特殊化についての仕様がはっきりしていなかったせいだと思われます。この問題は[P2096R2](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2096r2.html)によってC++23でようやく解決されました。

P2096R2では、変数テンプレートの部分特殊化の扱いがクラステンプレートと同じになるように仕様を調整しており、これはC++14当時の仕様を明確化することを意図しています。そのため、これらの事は本来、C++14時点からクラステンプレートと共通だったはずです。

### 参考文献

- [C++20 コンセプト - cpprefjp](https://cpprefjp.github.io/lang/cpp20/concepts.html)
- [C++14 変数テンプレート - cpprefjp](https://cpprefjp.github.io/lang/cpp14/variable_templates.html)
- [P2096R2 Generalized wording for partial specializations](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2096r2.html)
- [［C++］特殊化？実体化？？インスタンス化？？？明示的？？？？部分的？？？？？ - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2020/01/24/183247)
- [［C++］void_tとその周辺 - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/01/29/004929)
