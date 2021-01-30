# ［C++］推論補助（deduction guide）にexportはいるの？

A : いりません

### 根拠

モジュールにおける`export`宣言は、そのモジュールのインターフェース単位でのみ行うことができます。`export`宣言は名前を導入するタイプの宣言の前に`export`を付けることで行い、その名前に外部リンケージを与える以外は元の宣言と同じ効果を持ちます。

モジュールの`import`宣言は指定したモジュールをインポートするもので、書かれている場所と異なるモジュールを指定した場合はそのモジュールのインターフェースをインポートする事になります。

モジュールのインターフェースをインポートすると、インポートされたモジュールで`export`されている名前がインポートした側での名前探索において可視となり、インポートされたモジュールのインターフェースで宣言されているものが全て到達可能（*reachable*）となります。

推論補助そのものはテンプレートの宣言の一種であり、名前を導入するものなので`export`することができます。

推論補助に`export`がいるかどうかというのは、推論補助が名前探索を通じて発見されるのかどうか？という事でもあります。推論補助はどのようにして発見されているのでしょうか・・・？

[N4861 13.7.2.3 Deduction guides [temp.deduct.guide]](http://eel.is/c++draft/temp#deduct.guide-1)に明確に書いてあります。

> Deduction guides are not found by name lookup. Instead, when performing class template argument deduction ([over.match.class.deduct]), all reachable deduction guides declared for the class template are considered.

推論補助は名前探索では見つからず、代わりにクラステンプレートの引数推論時にそのクラステンプレートに対して __到達可能__ な全ての推論補助が考慮される。みたいに書いてあります。

ここでの到達可能（*reachable*）とは、`import`宣言によってインターフェースにあるものが到達可能になる、と言っていたところの到達可能と同じ意味です。

つまり、推論補助はモジュールのインターフェースにありさえすればそのモジュールをインポートした側で使用可能となります。`export`する必要はありません。

```cpp
/// mymodule.cpp
export module mymodule;

import <ranges>;

export
template<std::input_or_output_iterator I, std::sentinel_for<I> S>
class iter_pair {
  I it;
  S se;

public:

  template<typename R>
  iter_pair(R&& r); // (1)

  iter_pair(I i);   // (2)
};

// (1)に対する推論補助1
template<typename R>
iter_pair(R&&) -> iter_pair<std::ranges::iterator_t<R>, std::ranges::sentinel_t<R>>;

module : private;
// プライベートモジュールフラグメントの内側はインポートした側から到達可能とならない


// (2)に対する推論補助2
template<std::input_or_output_iterator I>
  requires std::sentinel_for<std::default_sentinel_t, I>
iter_pair(I) -> iter_pair<std::remove_cvref_t<I>, std::default_sentinel_t>;


// コンストラクタ定義、暗黙エクスポート
template<std::input_or_output_iterator I, std::sentinel_for<I> S>
template<typename R>
iter_pair<I, S>::iter_pair(R&& r)
  : it(std::ranges::begin(r))
  , se(std::ranges::end(r))
{}

template<std::input_or_output_iterator I, std::sentinel_for<I> S>
iter_pair<I, S>::iter_pair(I i)
  : it(std::move(i))
  , se{}
{}
```

```cpp
/// main.cpp

import <iterator>;
import mymodule;

int main() {
  int ar[3] = {1, 2, 3};
  
  iter_pair ip(ar);   // ok、推論補助1は到達可能

  std::counted_iterator ci{std::ranges::begin(ar), 2};
  
  iter_pair ip2(ci);  // ng、推論補助2は到達可能ではない
}
```

### 参考文献

- [クラステンプレートのテンプレート引数推論 - cpprefjp](https://cpprefjp.github.io/lang/cpp17/type_deduction_for_class_templates.html)
- [Working Draft, Standard for Programming Language C++ (N4861)](https://timsong-cpp.github.io/cppwp/n4861/)
- [P1103R3メモ書き - github](https://github.com/onihusube/blog/blob/master/2019/cpp20_module_memo.md)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2021/20210129_module_deduction_guide.md)