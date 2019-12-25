# ［C++］ std::rangesの範囲アクセス関数の使いみち

C++20のRangeライブラリ導入に伴って、`std::ranges`名前空間の下に`begin,end,size,data`等の、これまでコンテナアクセスに用いられていた関数が追加されています。しかし、これらの関数はすでに`std`名前空間に存在しており、一見すると同じ役割を持つものが重複して存在しているようにも見えてしまいます。

### 従来の`std::begin()/std::end()`の問題点

元々、範囲を表すイテレータのペアを取り出す口としての`begin()/end()`は各コンテナのメンバ関数として定義されていました。しかしその場合、メンバ関数を持つことのできない生の配列型だけは特別扱いする必要があり、イテレータのペアを取り出す操作が完全に共通化できていませんでした。

C++11にて、`std::begin()/std::end()`が追加され、この関数を利用することで配列とコンテナの間で共通の操作によってイテレータのペアを取り出せるようになりました。  
しかし、標準ライブラリ外の`begin()/end()`をメンバではなくグローバル関数として定義しているようなユーザー定義の型に対してはこれに加えて以下のような一手間を加えなければなりません。

```cpp
//イテレータのペアを取り出す
template<typename Iterable>
auto get_range(Iterable& range_obj) {
  using std::begin;
  using std::end;

  return std::make_pair(begin(range_obj), end(range_obj));
}
```

`std::begin()/std::end()`をそれぞれ`using`した上で`begin()/end()`するのです。これによってメンバではなく同じ名前空間に`begin()/end()`を用意しているユーザー定義型の場合はADLによってそれを発見し、それ以外の型は`std::begin()/std::end()`を経由してメンバのものを呼び出すか配列として処理されます。

C++17まではイテレータ範囲をジェネリックに得るにはこうする事がベストでした（はずです）。


### `std::ranges::begin/std::ranges::end`

しかし、先ほどのコードは正直言って意味わからないし面倒です。C++ヲタクにしかその意味は分からないし、ああいう風に書くという発想は出てきません。一々あんなまどろっこしい書き方も支度なでいす。

そこで、Rangeライブラリでは独自に`begin()/end()`を備えておくことにしました。それが、[`std::ranges::begin`](http://eel.is/c++draft/range.access.begin)/[`std::ranges::end`](http://eel.is/c++draft/range.access.end)の関数（オブジェクト）です。その効果はおおよそ以下のようになります。

- 配列ならその先頭（終端）のポインタを返す
- そうではなく、メンバ関数の`begin()/end()`があればその結果を返す
- そうでもなく、グローバルな`begin()/end()`が利用可能ならばその結果を返す
- そうでもなければ*ill-formed*

つまり先ほどのコードでやっていたような事を全て中でやってくれるすごいやつです。

そして、この`std::ranges::begin/std::ranges::end`によってイテレータペアを取得可能な型こそがRangeライブラリの基本要件である`std::ranges::range`コンセプトを満足する事ができます。

C++20からは先ほどのコードは以下のように書けるでしょう。

```cpp
//イテレータのペアを取り出す
template<std::ranges::range Iterable>
auto get_range(Iterable& range_obj) {
  return std::make_pair(std::ranges::begin(range_obj), std::ranges::end(range_obj));
}
```

### `std::ranges::size`

### `std::ranges::empty`

### `std::ranges::data`

### 結論

このように、これらの範囲アクセス関数（オブジェクト）は今まで用意されていた同名の関数と比べて、さらにもう少し頑張ってその目的を達成しようとするものです。そして、その目的を達するために非自明な追加の操作を要求しません。

C++20からは従来の関数のことは忘れて`std::ranges`名前空間の下にあるこれらの関数（オブジェクト）を使いましょう。

### 参考文献
- [24.3 Range access [range.access] - ](http://eel.is/c++draft/range.access)
- [［C++］expression-equivalentのお気持ち - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/09/12/002550)