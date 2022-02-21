# ［C++］後から触られないグローバルRAIIラッパー

C言語のライブラリにたまにある、最初にグローバル状態を`~init()`で確保して、それを最後に`~release()`で解放するというインターフェースについて、C++から使うときはRAIIで自動化したい衝動に駆られます。そのとき問題となるのは、プログラムの最初で初期化したらあとはプログラム終了時まで誰にも触ってほしくない、という気持ちをどうやって実現するのか、という事です。

[:contents]

### グローバルRAIIラッパー

単純にRAIIに従った、次のようなクラスを考えることができます。

```cpp
#include <iostream>

// グローバル状態初期化/解放関数とする
void init() {
  std::cout << "init()\n";
}
void release() {
  std::cout << "release()\n";
}

// グローバルRAIIラッパ
struct global_raii_t {

  global_raii_t() {
    init();
  }

  ~global_raii_t() {
    release();
  }
};

// RAII実態
inline const global_raii_t raii_obj{};


int main() {
  std::cout << "main()\n";
}
```

これの問題点は、別の人がいくらでも新しいオブジェクトを作って勝手に確保/解放処理を走らせることができる点です。後コピーも普通にできてしまいます。

### 型を隠そう！

デフォルトコンストラクタを隠したりコピーを防ぐこともできますが、簡単には型名を知られなければいいので型を隠す方向で行ってみます。よく知られた型隠蔽手段としてローカルクラスがあります。


```cpp
// RAII実態
inline const auto raii_obj = [] {
  // グローバルRAIIラッパ
  struct global_raii_t {

    global_raii_t() {
      init();
    }

    ~global_raii_t() {
      release();
    }
  };

  return global_raii_t{};
}();
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/csWQllfyJ4WAFUbL)

これで一見型名に触れられなくなりました。ただこれもまたよく知られているように、C++には`decltype()`があります。

```cpp
int main() {
  using C = std::decay_t<decltype(::raii_obj)>;

  C c1{};             // ok
  C c2 = ::raii_obj;  // ok
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/5i7Z0b2bRcKm4wOM)

### 初期化処理を分ける+コピー禁止

RAII型を関数内部に移したので初期化処理はそこでやることにしましょう。すると、構築された時でも初期化処理が走らなくなります。同時にコピー/ムーブを禁止してしまいます。

```cpp
// RAII実態
inline const auto raii_obj = [] {
  init();

  // グローバルRAIIラッパ
  struct global_raii_t {

    global_raii_t() = default;

    global_raii_t(const global_raii_t&) = delete;
    global_raii_t& operator=(const global_raii_t&) = delete;

    ~global_raii_t() {
      release();
    }
  };

  return global_raii_t{};
}();
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/awqAyu7fj3m31dgf)

こうすれば、型名を取られて初期化されても`init()`は走らないしコピーとかもできません（ムーブコンストラクタ/代入演算子は、宣言がなく対応するコピーコンストラクタ/代入演算子が宣言されている場合に暗黙`delete`されています）。

```cpp
int main() {
  using C = std::decay_t<decltype(::raii_obj)>;

  C c = ::raii_obj;  // ng
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/5MaucNyW1AEkjL2m)

しかしお忘れではないですか？デストラクタのことを・・・

```cpp
int main() {
  using C = std::decay_t<decltype(::raii_obj)>;

  C c{};  // ok
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Jll1XxrC0rttIA0d)

### 後から構築を禁止する

もはやグローバル`raii_obj`は動かないので、デストラクタが勝手に走るのを抑止するには新しく構築されるのを防止すればいいわけです。じゃあデフォルトコンストラクタを削除しよう！となりますが、しかし最初の一度だけは構築可能である必要があります。そこで、コンストラクタになんか引数を与えて構築するようにします。

```cpp
// RAII実態
inline const auto raii_obj = [] {
  init();

  // グローバルRAIIラッパ
  struct global_raii_t {

    global_raii_t(int){}

    global_raii_t(const global_raii_t&) = delete;
    global_raii_t& operator=(const global_raii_t&) = delete;

    ~global_raii_t() {
      release();
    }
  };

  return global_raii_t{1};
}();
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/e4M77JLmysBtaDc7)

こうすれば単純には構築できなくなりますが、必要な引数が`int`であることはコードを見ればわかります。ここでも型名が隠蔽された型が必要です。

```cpp
// RAII実態
inline const auto raii_obj = [] {
  init();

  struct tag {};

  // グローバルRAIIラッパ
  struct global_raii_t {

    global_raii_t(tag){}

    global_raii_t(const global_raii_t&) = delete;
    global_raii_t& operator=(const global_raii_t&) = delete;

    ~global_raii_t() {
      release();
    }
  };

  return global_raii_t{tag{}};
}();
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/e4M77JLmysBtaDc7)

こうすると`tag`型を外から取得して構築する手段がなくなるので、これで`global_raii_t`型を外から構築する手段はなくなりました。やった！

```cpp
int main() {
  std::cout << "main()\n";

  using C = std::decay_t<decltype(::raii_obj)>;

  C c{{}};  // ok!
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gbD4HfZl15dg37hP)

型推論とオーバーロード解決の前では、型名など飾りです。

これは、`tag`型が集成体であるため`{}`による集成体初期化が可能であることによって起こっています。これを防ぐには`tag`型が非集成体であればいいわけです。その方法はいくつかありますが、一番簡単なのは`explicit`コンストラクタを追加することです。

```cpp
// RAII実態
inline const auto raii_obj = [] {
  init();

  struct tag {
    explicit tag() = default;
  };

  // グローバルRAIIラッパ
  struct global_raii_t {

    global_raii_t(tag){}

    global_raii_t(const global_raii_t&) = delete;
    global_raii_t& operator=(const global_raii_t&) = delete;

    ~global_raii_t() {
      release();
    }
  };

  return global_raii_t{tag{}};
}();
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/yYNKDhrxSiF3yLN6)

こうすれば先ほどのように`{}`を用いた構築はできなくなります。そして、もはやこの`global_raii_t`型を外から構築する手段はありません。

```cpp
int main() {
  std::cout << "main()\n";

  using C = std::decay_t<decltype(::raii_obj)>;

  C c{{}};  // ng
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/aSv6Z5GmCv8a6ksD)

なお、これはC++17以降から有効です。C++14以前では`explicit`デフォルトコンストラクタがあってもクラスは集成体となり得ます。C++14以前で集成体でなくするには、仮想関数を何か定義しておくか継承しておくのが楽かと思います。

いやまあ、正直ここまでやる必要性はあまり感じられません。ローカルクラスで包むだけでもいいと思いますし、何なら最初の素のRAIIラッパで十分な気がします・・・

### さらなる懸念

まあ何とここからデストラクタを呼び出すことができてしまうんですね・・・

```cpp
int main() {
  std::cout << "main()\n";

  std::destroy_at(&raii_obj); // oK
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/j2WVriU3U3CJ4LzV)

この場合`std::destroy_at`の実行以降は未定義動作の世界です。しかしこれはちょっと防止する方法が思いつきません。

### 参考文献

- [STL/optional - microsoft/STL](https://github.com/microsoft/STL/blob/20b8f611c8b9bf570632e80bae1e704991b9e11e/stl/inc/optional#L33-L37)
- [llvm-project/optional - llvm/llvm-project](https://github.com/llvm/llvm-project/blob/main/libcxx/include/optional#L212-L216)
- [［C++］集成体の要件とその変遷 - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/02/22/201044)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2022/20220221_raii_wrapper.md)
