#  ［C++］ rangesのパイプにアダプトするには

C++20の`<ranges>`のパイプ（`|`）に自作の`view`（Rangeアダプタ）を接続できるようにするにはどうすればいいのでしょうか？その方法は一見よくわからず、特に提供されてもいません。それでもできないことはないので、なんとかする話です。

### パイプの実態

rangesのパイプは言語組み込みの機能ではなく、ビット論理和演算子（`|`）をオーバーロードしたものです。そのため、単純には`|`のオーバーロードを自作の`view`に対して提供すれば良さそうに思えます。

しかし、よくあるパイプライン記法による記述を見てみると、それではダメそうなことがわかります。

```cpp
int main() {
  using namespace std::views;

  auto seq = iota(1) | drop(5)
                     | filter([](int n) { return n % 2 == 0;})
                     | transform([](int n) { return n * 2; })
                     | take(5);
}
```

このチェーンの起点となっているのは`iota(1)`であり、これは入力となる`range`を生成しています。この`iota`は`iota_view`という`view`を返していて、このように引数から何か`view`を生成しているものをRangeファクトリと呼びます。Rangeファクトリはこの`iota`のようにパイプの最初で使用して入力となる`range`を生成するタイプのものです。今回どうにかしたいのはこれではありません。

`iota(1)`の後ろで、`|`で接続されているの（`drop, filter`など）がRangeアダプタと呼ばれるもので、これは`view`を入力として何かしらの変換を適用した`view`を返すもので、これは必ず`|`の右辺に来ます。今回どうにかしたいのはこれです。

ここで注意すべきなのは、Rangeファクトリの戻り値型は常に`view`であるのに対して、Rangeアダプタの戻り値型はそうではないことです。例えば`drop(5)`の戻り値型は引数に与えられた`5`を保持した何かを返しています。その後、`|`によって`range`を入力することでようやく`view`を生成します（`iota(1) | drop(5)`の結果は`dorp_view`になる）。

Rangeファクトリを`RF`、Rangeアダプタを`RA`、与える0個以上の引数を`Args`として、コンセプトっぽい書き方で表すと次のようになっています

- Rangeファクトリ : `RF(Args) -> view`
- Rangeアダプタ : `RA(Args) -> ??`
- パイプライン  : `view | RA(Args) -> view`

`view`は[`view`コンセプト](https://cpprefjp.github.io/reference/ranges/view.html)を満たす型であることを表します。

この性質から分かるように、パイプライン演算子（`|`）を提供しているのはRangeアダプタの戻り値型（上記の`??`）です。そして、自作のRangeアダプタをパイプにチェーンしたければこれらと同じことをする必要があります。

### Rangeアダプタオブジェクト/Rangeアダプタクロージャオブジェクト

Rangeアダプタは関数のように見えますがそうではなく、CPOと呼ばれる関数オブジェクトの一種です。そのため、Rangeアダプタの実体のことをRangeアダプタオブジェクトと呼びます。

Rangeアダプタオブジェクトとは、1つ目の引数に[`viewable_range`](https://cpprefjp.github.io/reference/ranges/viewable_range.html)を受けて呼出可能なカスタマイゼーションポイントオブジェクトであり、その戻り値型は`view`となります。中でも、1引数のRangeアダプタオブジェクトのことを特に、Rangeアダプタクロージャオブジェクトと呼びます。

このRangeアダプタクロージャオブジェクトには規格によって変な性質が付加されています。

Rangeアダプタクロージャオブジェクト`C`と入力の`range`（正確には、`viewable_range`）オブジェクト`r`があった時、次の2つの記述は同じ意味と効果を持ちます

```cpp
C(r);   // 関数記法
r | C:  // パイプライン記法
```

ようはRangeアダプタクロージャオブジェクトに入力`range`を関数呼出とパイプラインの2つの方法で入力できるということです。先ほど見たように、この戻り値型は`view`となります（でなければなりません）。コンセプトを用いて書いてみると次のようになります

```cpp
// 入力のrange(viewable_range)オブジェクト
viewable_range auto r = ...;

// この2つの呼び出しは同じviewを返す
view auto v1 = C(r);
view auto v2 = r | C ;
```

さらに、別のRangeアダプタクロージャオブジェクト`D`に対して、`C | D`が有効である必要があり、その戻り値型はまたRangeアダプタクロージャオブジェクトである必要があります。

```cpp
auto E = C | D;  // EはRangeアダプタクロージャオブジェクト

// これらの呼び出しは同じviewを返す
view auto v1 = r | C | D;
view auto v2 = r | (C | D) ;
view auto v3 = r | E ;
view auto v4 = E(r) ;
```

つまりは、Rangeアダプタクロージャオブジェクト同士もまた`|`で（事前に）接続可能であるということです。そしてその結果もRangeアダプタクロージャオブジェクトとなり、入力に対して順番に接続した時と同じ振る舞いをしなければなりません。ただし、Rangeアダプタクロージャオブジェクト同士の事前結合においては関数記法を使用できません。

```cpp
auto E = D(C);  // これはできない
```

Rangeアダプタクロージャオブジェクトは1引数ですが、Rangeアダプタオブジェクトの中には追加の引数を受け取る者もいます（というかそっちの方が多い）。その場合、引数を渡してから`range`を入力しても、`range`と一緒に引数を渡しても、等価な振る舞いをします。

```cpp
view auto v1 = r | C(args...);
view auto v2 = C(r, args...);
view auto v3 = C(args...)(r);
```

つまりは、Rangeアダプタオブジェクトにその追加の引数`args...`をあらかじめ渡すことができて、その結果（`C(args...)`）はRangeアダプタクロージャオブジェクトとなります。

ここまでくると、Rangeアダプタクロージャオブジェクトとは、このように追加の引数を全て部分適用して、あとは入力の`range`を受け取るだけになったRangeアダプタオブジェクト（1引数で呼出可能なRangeアダプタオブジェクト）、であることがわかります。そして、パイプで使用可能なRangeアダプタオブジェクトとはRangeアダプタクロージャオブジェクトのことです。

なお、事前結合が可能なのはRangeアダプタクロージャオブジェクトだけなので、そうではないRangeアダプタオブジェクトを事前に`|`で接続することはできません。

### 実例

```cpp
int main() {
  auto seq = iota(1) | std::views::take(5);
}
```

ここでは、`std::views::take`はRangeアダプタオブジェクトですがまだRangeアダプタクロージャオブジェクトではありません。`take(5)`によって必要な引数が満たされ、Rangeアダプタクロージャオブジェクトとなり、これで`|`で使用可能となります。そして、`iota(1) | take(5)`の結果は`view`を生成します。

標準にあるRangeアダプタクロージャオブジェクトには例えば`views::common`があります。

```cpp
int main() {
  auto seq = iota(1) | std::views::common;
}
```

`views::common`はすでにRangeアダプタクロージャオブジェクトであるので追加の引数を渡す必要がなく、そのままパイプで接続可能です。`iota(1) | common`の結果は`view`を生成します。

Rangeアダプタの事前適用は次のようになります

```cpp
int main() {
  using namespace std::views;

  auto adoptor = drop(5)
               | filter([](int n) { return n % 2 == 0;})
               | transform([](int n) { return n * 2; })
               | take(5);

  auto seq = iota(1) | adoptor;
}
```

ここで、`adoptor`はRangeアダプタクロージャオブジェクトであり、まだ`range`は入力されていません。そして、`iota(1) | adoptor`は冒頭の全部まとめているコードと同じ振る舞いをします（ただし、ここではまだ処理を開始していないので何も始まっていません）。

- [ここまでの例 - Compiler Explorer](https://godbolt.org/z/Y8ThbT4zP)

自作のRangeアダプタ（`view`）でパイプを使用可能にするとは、その`view`のためのRangeアダプタオブジェクトを定義した上で、それそのものあるいはその呼出がRangeアダプタクロージャオブジェクトを返すようにし、そのRangeアダプタクロージャオブジェクト型に対して`|`をオーバーロードし、なおかつ上記のRangeアダプタ（クロージャ）オブジェクトの性質を満たすようにしなければなりません。

### 標準ライブラリ実装による実装

やるべきことはわかりましたたが、そこはかとなく面倒臭そうですしどのように実装すれば適切なのかもよくわかりません。そこで、主要なC++標準ライブラリ実装がRangeアダプタをどのように実装しているのかを見てみます。

#### GCC 10

例えば、`filter_view`（`view`型）と`views::filter`（Rangeアダプタオブジェクト）を見てみると、次のように定義されています

```cpp
namespace std::ranges {

  ...

  template<input_range _Vp,
	         indirect_unary_predicate<iterator_t<_Vp>> _Pred>
    requires view<_Vp> && is_object_v<_Pred>
  class filter_view : public view_interface<filter_view<_Vp, _Pred>>
  {
    ...
  };

  ...

  namespace views
  {
    inline constexpr __adaptor::_RangeAdaptor filter
      = [] <viewable_range _Range, typename _Pred> (_Range&& __r, _Pred&& __p)
      {
	      return filter_view{std::forward<_Range>(__r), std::forward<_Pred>(__p)};
      };
  } // namespace views

}
```

また、Rangeアダプタクロージャオブジェクト`views::common`と`common_view`は次のように定義されています。

```cpp
namespace std::ranges {

  ...

  template<view _Vp>
    requires (!common_range<_Vp>) && copyable<iterator_t<_Vp>>
  class common_view : public view_interface<common_view<_Vp>>
  {
    ...
  };

  ...

  namespace views
  {
    inline constexpr __adaptor::_RangeAdaptorClosure common
      = [] <viewable_range _Range> (_Range&& __r)
      {
      	if constexpr (common_range<_Range>
      		      && requires { views::all(std::forward<_Range>(__r)); })
      	  return views::all(std::forward<_Range>(__r));
      	else
      	  return common_view{std::forward<_Range>(__r)};
      };

  } // namespace views
}
```

Rangeアダプタの実体型は`__adaptor::_RangeAdaptor`、Rangeアダプタクロージャオブジェクトの実体型は`__adaptor::_RangeAdaptorClosure`であるようです。省略しますが、他のRangeアダプタに対してもこれらと同様の実装方針が採られています。

まずはRangeアダプタの実装を見てみます。

```cpp
template<typename _Callable>
struct _RangeAdaptor
{
protected:
  [[no_unique_address]]
   __detail::__maybe_present_t<!is_default_constructible_v<_Callable>, 
                               _Callable> _M_callable;

public:

  constexpr
  _RangeAdaptor(const _Callable& = {})
   requires is_default_constructible_v<_Callable>
  { }

  constexpr
  _RangeAdaptor(_Callable __callable)
   requires (!is_default_constructible_v<_Callable>)
   : _M_callable(std::move(__callable))
  { }

  template<typename... _Args>
    requires (sizeof...(_Args) >= 1)
    constexpr auto
    operator()(_Args&&... __args) const
    {
     // [range.adaptor.object]: If a range adaptor object accepts more
     // than one argument, then the following expressions are equivalent:
     //
     //   (1) adaptor(range, args...)
     //   (2) adaptor(args...)(range)
     //   (3) range | adaptor(args...)
     //
     // In this case, adaptor(args...) is a range adaptor closure object.
     //
     // We handle (1) and (2) here, and (3) is just a special case of a
     // more general case already handled by _RangeAdaptorClosure.
     if constexpr (is_invocable_v<_Callable, _Args...>)
       {
          static_assert(sizeof...(_Args) != 1,
          	      "a _RangeAdaptor that accepts only one argument "
          	      "should be defined as a _RangeAdaptorClosure");
          // Here we handle adaptor(range, args...) -- just forward all
          // arguments to the underlying adaptor routine.
          return _Callable{}(std::forward<_Args>(__args)...);
       }
     else
       {
          // Here we handle adaptor(args...)(range).
          // Given args..., we return a _RangeAdaptorClosure that takes a
          // range argument, such that (2) is equivalent to (1).
          //
          // We need to be careful about how we capture args... in this
          // closure.  By using __maybe_refwrap, we capture lvalue
          // references by reference (through a reference_wrapper) and
          // otherwise capture by value.
          auto __closure
            = [...__args(__maybe_refwrap(std::forward<_Args>(__args)))]
              <typename _Range> (_Range&& __r) {
                // This static_cast has two purposes: it forwards a
                // reference_wrapper<T> capture as a T&, and otherwise
                // forwards the captured argument as an rvalue.
                return _Callable{}(std::forward<_Range>(__r),
          	              (static_cast<unwrap_reference_t
          			                       <remove_const_t<decltype(__args)>>>
          		            (__args))...);
              };
          using _ClosureType = decltype(__closure);
          return _RangeAdaptorClosure<_ClosureType>(std::move(__closure));
       }
   }
};

template<typename _Callable>
  _RangeAdaptor(_Callable) -> _RangeAdaptor<_Callable>;
```

めちゃくちゃ複雑なので細かく解説はしませんが、ここではRangeアダプタオブジェクト（not クロージャオブジェクト）の追加の引数を事前に受け取って保持しておくことができる、という性質を実装しています。

```cpp
view auto v1 = r | C(args...);  // #1
view auto v2 = C(r, args...);   // #2
view auto v3 = C(args...)(r);   // #3
```

このクラスは何か呼出可能と思われるもの（`_Callable`）を受け取って、それがデフォルト構築不可能な場合のみメンバ（`_M_callable`）に保存しています。最初に見た使われ方では、ラムダ式によって初期化されていて、そのラムダ式で対象の`view`に合わせたRangeアダプタの効果が実装されていました。

Rangeアダプタの性質を実装しているのは`operator()`内で、ここでは上記`#2, #3`の2つのケースを処理していて、`#1`はRangeアダプタクロージャオブジェクト（`_RangeAdaptorClosure`）のパイプライン演算子に委ねています。

`operator()`内、`constexpr if`の`true`分岐では、`C(r, args...)`を処理しています。この場合は引数列`__args`の1つ目に入力`range`を含んでおり、残りの引数を保存する必要もないため、それらをそのまま転送して`_Callable`を呼び出し、それによってRangeアダプタを実行します。この場合の戻り値は`view`となります。

`constexpr if`の`false`分岐では、`C(args...)(r)`を処理しています。この場合は引数列`__args`に入力`range`は含まれておらず、それは後から入力（`|`or`()`）されるので、渡された引数列を保存して後から入力`range`と共に`_Callable`の遅延呼び出しを行う呼び出し可能ラッパを返しています。それはラムダ式で実装されており、引数の保存はキャプチャによって行われています。この場合の戻り値はRangeアダプタクロージャオブジェクトであり、引数と`_Callable`を内包したラムダ式を`_RangeAdaptorClosure`に包んで返しています。

どちらの場合でもメンバに保存した`_M_callable`を使用していませんが、この`#1, #2`のケースの場合はどちらも`_Callable`がデフォルト構築可能であることを仮定することができます。なぜなら、この二つの場合にわたってくる`_Callable`は状態を持たないラムダ式であり、C++20からそれはデフォルト構築可能であるためです。`_M_callable`を使用する必要があるのは実は`C(args...)`相当の部分適用をおこなった場合のみで、それはRangeアダプタクロージャオブジェクト（`_RangeAdaptorClosure`）において処理されます。

次はそのRangeアダプタクロージャオブジェクトの実装を見てみましょう。

```cpp
template<typename _Callable>
struct _RangeAdaptorClosure : public _RangeAdaptor<_Callable>
{
  using _RangeAdaptor<_Callable>::_RangeAdaptor;

  template<viewable_range _Range>
    requires requires { declval<_Callable>()(declval<_Range>()); }
  constexpr auto
  operator()(_Range&& __r) const
  {
    if constexpr (is_default_constructible_v<_Callable>)
      return _Callable{}(std::forward<_Range>(__r));
    else
      return this->_M_callable(std::forward<_Range>(__r));
  }

  // 1. range | RACO -> view  ※説明のため追記
  template<viewable_range _Range>
    requires requires { declval<_Callable>()(declval<_Range>()); }
  friend constexpr auto
  operator|(_Range&& __r, const _RangeAdaptorClosure& __o)
  { return __o(std::forward<_Range>(__r)); }

  // 2. RACO | RACO -> RACO ※説明のため追記
  template<typename _Tp>
  friend constexpr auto
  operator|(const _RangeAdaptorClosure<_Tp>& __x,
            const _RangeAdaptorClosure& __y)
  {
    if constexpr (is_default_constructible_v<_Tp>
                  && is_default_constructible_v<_Callable>)
      {
        auto __closure = [] <typename _Up> (_Up&& __e) {
          return std::forward<_Up>(__e) | decltype(__x){} | decltype(__y){};
        };
        return _RangeAdaptorClosure<decltype(__closure)>(__closure);
      }
    else if constexpr (is_default_constructible_v<_Tp>
                       && !is_default_constructible_v<_Callable>)
      {
        auto __closure = [__y] <typename _Up> (_Up&& __e) {
          return std::forward<_Up>(__e) | decltype(__x){} | __y;
        };
        return _RangeAdaptorClosure<decltype(__closure)>(__closure);
      }
    else if constexpr (!is_default_constructible_v<_Tp>
                       && is_default_constructible_v<_Callable>)
      {
        auto __closure = [__x] <typename _Up> (_Up&& __e) {
          return std::forward<_Up>(__e) | __x | decltype(__y){};
        };
        return _RangeAdaptorClosure<decltype(__closure)>(__closure);
      }
    else
      {
        auto __closure = [__x, __y] <typename _Up> (_Up&& __e) {
          return std::forward<_Up>(__e) | __x | __y;
        };
        return _RangeAdaptorClosure<decltype(__closure)>(__closure);
      }
  }
};

template<typename _Callable>
  _RangeAdaptorClosure(_Callable) -> _RangeAdaptorClosure<_Callable>;
```

まず見て分かるように、`_RangeAdaptorClosure`は`_RangeAdaptor`を継承していて、受けた呼出可能なものの保持などは先ほどの`_RangeAdaptor`と共通です。そして、2つの`operator|`オーバーロードが定義されています。この実装方法は[Hidden friends](https://cpprefjp.github.io/article/lib/hidden_friends.html)と呼ばれる実装になっています。

Rangeアダプタクロージャオブジェクトは1つの`range`を関数呼出によって入力することができ、それは`operator()`で実装されています。ここで、`_Callable`がデフォルト構築可能かによって`_RangeAdaptor::_M_callable`を使用するかの切り替えが初めて行われており、`_Callable`がデフォルト構築可能ではない場合というのは、Rangeアダプタに追加の引数を部分適用した結果生成されたRangeアダプタクロージャオブジェクトの場合のみで、それは`_RangeAdaptor::operator()`内`constexpr if`の`false`パートの結果として生成されます。

1つ目の`operator|`オーバーロードは追記コメントにあるように、左辺に`range`を受けて結合する場合の`|`のオーバーロードです。この場合は先ほどの関数呼び出しと同じことになるので、`operator()`に委譲されています。わかりづらいですが、2つ目の引数の`__o`が`*this`に対応しています。

2つ目の`operator|`オーバーロードは残った振る舞い、すなわちRangeアダプタクロージャオブジェクト同士の事前結合を担っています。なんか`if`で4分岐しているのは、引数の`_RangeAdaptorClosure`オブジェクトの`_Callable`がデフォルト構築可能か否かでメンバの`_M_callable`を参照するかが変化するためで、それが引数2つ分の2x2で4パターンの分岐になっています。実際の結合処理は1つ目の`|`に委譲していて、その処理はラムダ式で記述していて、そのラムダ式のオブジェクトを`_RangeAdaptorClosure`に包んで返しています。`if`の分岐の差異は必要な場合にのみ引数`__x, __y`を返すラムダにキャプチャしていることです。

GCC10の実装では、Rangeアダプタとしての動作はステートレスなラムダ式で与えられ、Rangeアダプタオブジェクトはそれを受けたこの2つの型のどちらかのオブジェクトとなり、ややこしい性質の実装はこの2つの型に集約され共通化されています。`<ranges>`のパイプライン演算子は`_RangeAdaptorClosure`に定義されたものが常に使用されています。

#### GCC 11

GCC11になると、この実装が少し変化していました。

```cpp
namespace std::ranges {

  // views::filter
  namespace views
  {
    namespace __detail
    {
      template<typename _Range, typename _Pred>
	      concept __can_filter_view
	        = requires { filter_view(std::declval<_Range>(), std::declval<_Pred>()); };
    } // namespace __detail

    struct _Filter : __adaptor::_RangeAdaptor<_Filter>
    {
      template<viewable_range _Range, typename _Pred>
        requires __detail::__can_filter_view<_Range, _Pred>
        constexpr auto
        operator()(_Range&& __r, _Pred&& __p) const
        {
          return filter_view(std::forward<_Range>(__r), std::forward<_Pred>(__p));
        }

      using _RangeAdaptor<_Filter>::operator();
      static constexpr int _S_arity = 2;
      static constexpr bool _S_has_simple_extra_args = true;
    };

    inline constexpr _Filter filter;
  } // namespace views

  // views::common
  namespace views
  {
    namespace __detail
    {
      template<typename _Range>
        concept __already_common = common_range<_Range>
          && requires { views::all(std::declval<_Range>()); };

      template<typename _Range>
        concept __can_common_view
          = requires { common_view{std::declval<_Range>()}; };
    } // namespace __detail

    struct _Common : __adaptor::_RangeAdaptorClosure
    {
      template<viewable_range _Range>
        requires __detail::__already_common<_Range>
          || __detail::__can_common_view<_Range>
        constexpr auto
        operator()(_Range&& __r) const
        {
          if constexpr (__detail::__already_common<_Range>)
            return views::all(std::forward<_Range>(__r));
          else
            return common_view{std::forward<_Range>(__r)};
        }

      static constexpr bool _S_has_simple_call_op = true;
    };

    inline constexpr _Common common;
  } // namespace views
}
```

`filter`と`common`だけを見ても、`_RangeAdaptorClosure`とかの名前そのものは変わっていなくてもその使い方が大きく変わっていることがわかります。どちらも継承して使用されていて、`_RangeAdaptor`はCRTPになっています。それらに目を向けてみると

```cpp
// The base class of every range adaptor non-closure.
//
// The static data member _Derived::_S_arity must contain the total number of
// arguments that the adaptor takes, and the class _Derived must introduce
// _RangeAdaptor::operator() into the class scope via a using-declaration.
//
// The optional static data member _Derived::_S_has_simple_extra_args should
// be defined to true if the behavior of this adaptor is independent of the
// constness/value category of the extra arguments.  This data member could
// also be defined as a variable template parameterized by the types of the
// extra arguments.
template<typename _Derived>
struct _RangeAdaptor
{
  // Partially apply the arguments __args to the range adaptor _Derived,
  // returning a range adaptor closure object.
  template<typename... _Args>
    requires __adaptor_partial_app_viable<_Derived, _Args...>
    constexpr auto
    operator()(_Args&&... __args) const
    {
      return _Partial<_Derived, decay_t<_Args>...>{std::forward<_Args>(__args)...};
    }
};
```
```cpp
// The base class of every range adaptor closure.
//
// The derived class should define the optional static data member
// _S_has_simple_call_op to true if the behavior of this adaptor is
// independent of the constness/value category of the adaptor object.
struct _RangeAdaptorClosure
{

  // 1. range | RACO -> view  ※説明のため追記
  // range | adaptor is equivalent to adaptor(range).
  template<typename _Self, typename _Range>
    requires derived_from<remove_cvref_t<_Self>, _RangeAdaptorClosure>
      && __adaptor_invocable<_Self, _Range>
    friend constexpr auto
    operator|(_Range&& __r, _Self&& __self)
    { return std::forward<_Self>(__self)(std::forward<_Range>(__r)); }

  // 2. RACO | RACO -> RACO ※説明のため追記
  // Compose the adaptors __lhs and __rhs into a pipeline, returning
  // another range adaptor closure object.
  template<typename _Lhs, typename _Rhs>
    requires derived_from<_Lhs, _RangeAdaptorClosure>
      && derived_from<_Rhs, _RangeAdaptorClosure>
    friend constexpr auto
    operator|(_Lhs __lhs, _Rhs __rhs)
    { return _Pipe<_Lhs, _Rhs>{std::move(__lhs), std::move(__rhs)}; }
};
```

この二つのクラスの実装そのものはかなりシンプルになっています。`_RangeAdaptor::operator()`でRangeアダプタの性質（追加の引数を部分適用してRangeアダプタクロージャオブジェクトを生成する）を実装していて、`_RangeAdaptorClosure::operator|`でパイプライン演算子を実装しているのも先ほどと変わりありません。

ただし、どちらの場合もその実装詳細を`_Partial`と`_Pipe`という二つの謎のクラスに委譲しています。これらのクラスの実装は複雑で長いので省略しますが、`_Partial`はRangeアダプタの追加の引数を保存してRangeアダプタクロージャオブジェクトとなる呼び出し可能なラッパ型で、`_Pipe`はRangeアダプタクロージャオブジェクト2つを保持したRangeアダプタクロージャオブジェクトとなる呼び出し可能なラッパ型です。

`_Partial`と`_Pipe`はどちらも部分特殊化を使用することで、渡された追加の引数/Rangeアダプタクロージャオブジェクトを効率的に保持しようとします。`_RangeAdaptor/_RangeAdaptorClosure`を継承するクラス型に`_S_has_simple_call_op`とか`_S_has_simple_extra_args`だとかの静的メンバが生えているのは、これを適切に制御するためでもあります。

実装が細分化され分量が増えてはいますが、基本的にやっていることはGCC10の時と大きく変わってはいません。

これらの変更はおそらく、[P2281](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2281r1.html)の採択と[P2287](https://wg21.link/p2387r3)を意識したものだと思われます（どちらもC++23では採択済）。

- [P2281R0 Clarifying range adaptor objects - WG21月次提案文書を眺める（2021年01月）](https://onihusube.hatenablog.com/entry/2021/02/11/153333#P2281R0-Clarifying-range-adaptor-objects)
- [P2387R0 Pipe support for user-defined range adaptors - WG21月次提案文書を眺める（2021年06月）](https://onihusube.hatenablog.com/entry/2021/07/12/182757#P2387R0-Pipe-support-for-user-defined-range-adaptors)

#### MSVC

`views::filter`（Rangeアダプタオブジェクト）

```cpp
namespace views {
    struct _Filter_fn {
        // clang-format off
        template <viewable_range _Rng, class _Pr>
        _NODISCARD constexpr auto operator()(_Rng&& _Range, _Pr&& _Pred) const noexcept(noexcept(
            filter_view(_STD forward<_Rng>(_Range), _STD forward<_Pr>(_Pred)))) requires requires {
            filter_view(static_cast<_Rng&&>(_Range), _STD forward<_Pr>(_Pred));
        } {
            // clang-format on
            return filter_view(_STD forward<_Rng>(_Range), _STD forward<_Pr>(_Pred));
        }

        // clang-format off
        template <class _Pr>
            requires constructible_from<decay_t<_Pr>, _Pr>
        _NODISCARD constexpr auto operator()(_Pr&& _Pred) const
            noexcept(is_nothrow_constructible_v<decay_t<_Pr>, _Pr>) {
            // clang-format on
            return _Range_closure<_Filter_fn, decay_t<_Pr>>{_STD forward<_Pr>(_Pred)};
        }
    };

    inline constexpr _Filter_fn filter;
} // namespace views
```

`views::common`（Rangeアダプタクロージャオブジェクト）

```cpp
namespace views {
    class _Common_fn : public _Pipe::_Base<_Common_fn> {
    private:
        enum class _St { _None, _All, _Common };

        template <class _Rng>
        _NODISCARD static _CONSTEVAL _Choice_t<_St> _Choose() noexcept {
            if constexpr (common_range<_Rng>) {
                return {_St::_All, noexcept(views::all(_STD declval<_Rng>()))};
            } else if constexpr (copyable<iterator_t<_Rng>>) {
                return {_St::_Common, noexcept(common_view{_STD declval<_Rng>()})};
            } else {
                return {_St::_None};
            }
        }

        template <class _Rng>
        static constexpr _Choice_t<_St> _Choice = _Choose<_Rng>();

    public:
        // clang-format off
        template <viewable_range _Rng>
            requires (_Choice<_Rng>._Strategy != _St::_None)
        _NODISCARD constexpr auto operator()(_Rng&& _Range) const noexcept(_Choice<_Rng>._No_throw) {
            // clang-format on
            constexpr _St _Strat = _Choice<_Rng>._Strategy;

            if constexpr (_Strat == _St::_All) {
                return views::all(_STD forward<_Rng>(_Range));
            } else if constexpr (_Strat == _St::_Common) {
                return common_view{_STD forward<_Rng>(_Range)};
            } else {
                static_assert(_Always_false<_Rng>, "Should be unreachable");
            }
        }
    };

    inline constexpr _Common_fn common;
} // namespace views
```

雰囲気はGCC11の実装に似ています。Rangeアダプタオブジェクトでは、`range`を受け取る方の呼び出しを`operator()`でその場（Rangeアダプタ型内部）で定義し外出し（共通化）しておらず、追加の引数を部分適用してRangeアダプタクロージャオブジェクトを返す呼出では`_Range_closure`という型に自身と追加の引数をラップして返しています。

Rangeアダプタクロージャオブジェクトでは、`_Pipe::_Base`といういかにもな名前の型を継承しています。どうやら、パイプライン演算子はそこで定義されているようです。

```cpp
template <class _Fn, class... _Types>
class _Range_closure : public _Pipe::_Base<_Range_closure<_Fn, _Types...>> {
public:
    // We assume that _Fn is the type of a customization point object. That means
    // 1. The behavior of operator() is independent of cvref qualifiers, so we can use `invocable<_Fn, ` without
    //    loss of generality, and
    // 2. _Fn must be default-constructible and stateless, so we can create instances "on-the-fly" and avoid
    //    storing a copy.

    _STL_INTERNAL_STATIC_ASSERT((same_as<decay_t<_Types>, _Types> && ...));
    _STL_INTERNAL_STATIC_ASSERT(is_empty_v<_Fn>&& is_default_constructible_v<_Fn>);

    // clang-format off
    template <class... _UTypes>
        requires (same_as<decay_t<_UTypes>, _Types> && ...)
    constexpr explicit _Range_closure(_UTypes&&... _Args) noexcept(
        conjunction_v<is_nothrow_constructible<_Types, _UTypes>...>)
        : _Captures(_STD forward<_UTypes>(_Args)...) {}
    // clang-format on

    void operator()(auto&&) &       = delete;
    void operator()(auto&&) const&  = delete;
    void operator()(auto&&) &&      = delete;
    void operator()(auto&&) const&& = delete;

    using _Indices = index_sequence_for<_Types...>;

    template <class _Ty>
        requires invocable<_Fn, _Ty, _Types&...>
    constexpr decltype(auto) operator()(_Ty&& _Arg) & noexcept(
        noexcept(_Call(*this, _STD forward<_Ty>(_Arg), _Indices{}))) {
        return _Call(*this, _STD forward<_Ty>(_Arg), _Indices{});
    }

    template <class _Ty>
        requires invocable<_Fn, _Ty, const _Types&...>
    constexpr decltype(auto) operator()(_Ty&& _Arg) const& noexcept(
        noexcept(_Call(*this, _STD forward<_Ty>(_Arg), _Indices{}))) {
        return _Call(*this, _STD forward<_Ty>(_Arg), _Indices{});
    }

    template <class _Ty>
        requires invocable<_Fn, _Ty, _Types...>
    constexpr decltype(auto) operator()(_Ty&& _Arg) && noexcept(
        noexcept(_Call(_STD move(*this), _STD forward<_Ty>(_Arg), _Indices{}))) {
        return _Call(_STD move(*this), _STD forward<_Ty>(_Arg), _Indices{});
    }

    template <class _Ty>
        requires invocable<_Fn, _Ty, const _Types...>
    constexpr decltype(auto) operator()(_Ty&& _Arg) const&& noexcept(
        noexcept(_Call(_STD move(*this), _STD forward<_Ty>(_Arg), _Indices{}))) {
        return _Call(_STD move(*this), _STD forward<_Ty>(_Arg), _Indices{});
    }

private:
    template <class _SelfTy, class _Ty, size_t... _Idx>
    static constexpr decltype(auto) _Call(_SelfTy&& _Self, _Ty&& _Arg, index_sequence<_Idx...>) noexcept(
        noexcept(_Fn{}(_STD forward<_Ty>(_Arg), _STD get<_Idx>(_STD forward<_SelfTy>(_Self)._Captures)...))) {
        _STL_INTERNAL_STATIC_ASSERT(same_as<index_sequence<_Idx...>, _Indices>);
        return _Fn{}(_STD forward<_Ty>(_Arg), _STD get<_Idx>(_STD forward<_SelfTy>(_Self)._Captures)...);
    }

    tuple<_Types...> _Captures;
};
```

#### Clang

under implementing...

### 自作`view`のアダプト

#### ユニバーサル実装（Rangeアダプタオブジェクトとか知らねえ！とりあえず`|`で繋げればいい！！っていう人向け）

Rangeアダプタの性質を知り色々実装を見てみると、`|`につなぐだけなら簡単なことに気付けます。Rangeアダプタは必ず`|`の右辺に来て、左辺は`range`（`viewable_range`）オブジェクトとなります。複数チェーンしている時でも、1つの`range | RA`の結果は`view`になります。つまり、`range`を左辺に受ける`|`の実装においては左辺のオブジェクトは常に`viewable_range`となります。

それを例えば自作の`xxx_view`に実装すると

```cpp
namespace myrange {

  template<std::ranges::view V>
  class xxx_view;

  namespace views {
    namespace detail {

      struct xxx_view_adoptor {

        // Rangeアダプタの主処理
        template<typename R>
        [[nodiscard]]
        constexpr auto operator(R&& r) const {
          // xxx_viewの生成処理
        }

        // range | RA -> view なパイプライン演算子
        template <std::ranges::viewable_range R>
          requires requires(R&& r, const xxx_view_adoptor& self) {
            self(std::forward<R>(r));
          }
        [[nodiscard]]
        friend constexpr std::ranges::view auto operator|(R&& r, const xxx_view_adoptor& self) noexcept(noexcept(self(std::forward<R>(r)))) {
          return self(std::forward<R>(r));
        }
      };

    }

    inline constexpr xxx_view_adoptor xxx;
  }
}
```

他の部分を適切に整えさえすれば、この`operator|`定義は全ての実装でrangesのパイプラインチェーンにアダプトすることができます（多分）。

ただしこの`xxx_view_adoptor`はRangeアダプタとして必要なことを何もしていないので、それ以外の保証はありません。未定義動作にはならないと思いますが、標準のRangeアダプタ/Rangeアダプタクロージャオブジェクトと同等の振る舞いはできないので本当にとりあえずの実装です。

#### GCC10
#### GCC11
#### MSVC
SBC PROFIVE® NUCE - V2516
### C++23から

### 参考文献

- [GCC10 `<ranges>` - github](https://github.com/gcc-mirror/gcc/blob/releases/gcc-10.2.0/libstdc++-v3/include/std/ranges)
- [GCC11 `<ranges>` - github](https://github.com/gcc-mirror/gcc/blob/releases/gcc-11.2.0/libstdc++-v3/include/std/ranges)
- [C++20 状態を持たないラムダ式を、デフォルト構築可能、代入可能とする - cpprefjp](https://cpprefjp.github.io/lang/cpp20/default_constructible_and_assignable_stateless_lambdas.html)
- [P2281R1 Clarifying range adaptor objects](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2021/p2281r1.html)
- [P2281R1 Clarifying range adaptor objects - WG21月次提案文書を眺める（2021年01月）](https://onihusube.hatenablog.com/entry/2021/02/11/153333#P2281R0-Clarifying-range-adaptor-objects)
- [P2387R3 Pipe support for user-defined range adaptors](https://wg21.link/p2387r3)
- [P2387R3 Pipe support for user-defined range adaptors - WG21月次提案文書を眺める（2021年12月）](https://onihusube.hatenablog.com/entry/2022/01/10/235544#P2387R3-Pipe-support-for-user-defined-range-adaptors)