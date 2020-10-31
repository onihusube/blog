# ［C++］std::exchangeによるmoveしてリセットするイディオムの御紹介

2020年10月公開分の提案文書を眺めていたら良さげなものを見つけたので宣伝です。そのため、この記事の内容は次の提案文書を元にしています。

- [P2226R0 A function template to move from an object and reset it to its default constructed state](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2226r0.html)

もくじ

[:contents]

### `move`してリセット！

`std::exchange`を用いて`move`してリセットするとは、次のようなものです。

```cpp
// old_objの値をムーブしてnewobjを構築し、old_objをデフォルト状態にリセット
T new_obj = std::exchange(old_obj, {});

// old_objの値をnewobjにムーブ代入して、old_objをデフォルト状態にリセット
new_obj = std::exchange(old_obj, {});
```

[`std::exchange`](https://cpprefjp.github.io/reference/utility/exchange.html)はC++14で追加された関数で、第二引数の値を第一引数に転送し、第二引数の元の値を戻り値として返すものです。

```cpp
template <class T, class U=T>
constexpr T exchange(T& obj, U&& new_val);
```

ストリーム的に見ると、第二引数から戻り値まで右から左へその値が玉突き的に流れていくように見えます。

第二引数の型も個別のテンプレートパラメータになっており、デフォルトでは第一引数の型が推論されます。そのため、第二引数に`{}`を指定したときは`T{}`と指定したのと同等になるわけです。  
そして、そのようにデフォルト構築（正確には値初期化（*Value initialization*））された値が第一引数に`move`され、第一引数の元の値が戻り値として返されます。その際、可能であればすべて`move`されます。

このイディオムには次の2つの利点があります。

#### 1. 操作の複合化

このイディオムの利点の1つは複数の操作をひとまとめにする事でミスやエラーを起きにくくすることです。  
例えば、`std::unique_ptr`の様にポインタを所有するようなクラスのムーブコンストラクタと`reset()`で次のようにコードを改善できます。

```cpp
struct MyPtr {
  Data *d;

  // BAD, ポインタのコピーとnullptr代入が分割されているため、nullptr代入が忘れられうる
  MyPtr(MyPtr&& other) : d(other.d) { other.d = nullptr; }

  // BETTER, std::exchangeを利用してポインタを移動しリセット
  MyPtr(MyPtr&& other) : d(std::exchange(other.d, nullptr)) {}

  // GOOD, std::exchangeによる一般化されたイディオム（知っていれば意図が明確）
  MyPtr(MyPtr&& other) : d(std::exchange(other.d, {})) {}


  void reset(Data *newData = nullptr)
  {
    // BAD, 読みづらい
    std::swap(d, newData);
    if (newData) {
      dispose(newData);
    }

    // BETTER, 意図は分かりやすい
    Data *old = d;
    d = newData;
    if (old) {
      dispose(old);
    }

    // GOOD, 1行かつストリーム的
    if (Data *old = std::exchange(d, std::exchange(newData, {}))) {
      dispose(old);
    }
  }
};
```

このように、値が右から左へストリーム的に流れていくように見ることができ、そして移動とリセットの操作が合成されているために、意図が明確でミスも起こしにくいコードを書くことができます。

#### 2. `move`後状態の確定

もう一つの利点は、`move`後の抜け殻となっているオブジェクトの状態を確定できる事です。

```cpp
f(std::move(obj));          // objの状態は良く分からない・・・

f(std::exchange(obj, {}));  // objはデフォルト構築状態にリセットされる
```

例えば標準ライブラリのものであれば、`move`した後の状態は「有効だが未規定な状態」と規定されています。とはいえ結局どういう状態なのか分からず、より一般のライブラリ型などではドキュメント化されていることの方が稀です。  
このイディオムを用いることによって、`move`とその後のオブジェクトの状態の確定を1行で簡潔に書くことができます。

とはいえ完全に`move`と同等ではなくいくつか違いがあります。


||`move(old_obj)`|`exchange(old_onj, {})`|
|----|----|----|
|例外を投げる？|通常ムーブコンストラクタは`noexcept`|デフォルトコンストラクタ次第|
|処理後の`old_obj`の状態は？|有効だが未規定|デフォルト構築状態|
|呼び出しのコストは？|ムーブコンストラクタ次第|ムーブ/デフォルトコンストラクタ次第|
|`obj = xxxx(obj);`は何をする？|実装依存|例外を投げないと仮定すると、何もしない|
|`old_obj`をその後使用しない場合に最適な書き方？|Yes|No|


### いくつかのサンプル

```cpp
class C {
  Data *data;
public:
  // ムーブコンストラクタの改善
  C(C&& other) noexcept
    : data(std::exchange(other.data, {}))
  {}
};
```

```cpp
template <typename K, typename V, template <class...> class C =  std::vector>
class flat_map {
  C<K> m_keys;
  C<V> m_values;

public:

  // ムーブ後の有効だが未規定な状態を達するにはデフォルトmoveに任せられない
  // Cのムーブ操作によってはflat_mapの不変条件が破られ有効ではなくなってしまう可能性がある
  // 言い換えると、有効だが未規定な状態は合成されない
  // そのため、明示的なリセットが必要
  flat_map(flat_map&& other) noexcept(/**/)
    : m_keys(std::exchange(other.m_keys, {})),
      m_values(std::exchange(other.m_values, {}))
  {}

  flat_map &operator=(flat_map&& other) noexcept(/**/) {
    m_keys = std::exchange(other.m_keys, {});
    m_values = std::exchange(other.m_values, {});
    return *this;
  }
};
```

```cpp
void Engine::processAll() {
  // m_dataを消費しつつループする
  for (auto& value : std::exchange(m_data, {})) {
      // この処理はm_dataを変更する可能性がある
      // イテレータ破壊を回避する
      processOne(value);
  }
}
```

```cpp
void ConsumerThread::process() {
  // pendingDataをmutexの保護の元で取得し
  // 現在のスレッドがそれを安全に使用できるようにする
  Data pendingData = [&]() {
      std::scoped_lock lock(m_mutex);
      return std::exchange(m_data, {});
  }();

  for (auto& value : pendingData)
      process(value);
}
```

```cpp
// 一度だけ実行される関数
void Engine::maybeRunOnce() {
  if (std::exchange(m_shouldRun, false)) {
    run();
  }
}
```

```cpp
// Dataのオブジェクトを貯めておくクラス
struct S {
    // C++ Core Guideline F.15に基づいたオーバーロードの提供
    void set_data(const Data& d);
    void set_data(Data&& d);
} s;

Data d = ~~~;

// dをため込むが、明示的にデフォルト状態にする
s.set_data(std::exchange(d, {}));

assert(d == Data());
```

### 参考文献

- [P2226R0 A function template to move from an object and reset it to its default constructed state](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2226r0.html)
- [`std::exchange` - cpprefjp](https://cpprefjp.github.io/reference/utility/exchange.html)
- [F.15: Prefer simple and conventional ways of passing information - C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rf-conventional)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20201031_exchange_idiom.md)
