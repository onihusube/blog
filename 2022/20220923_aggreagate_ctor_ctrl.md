# ［C++］集成体のコピー/ムーブコンストラクタを制御する

C++17にて集成体はあらゆるコンストラクタを宣言できなくなり、その結果コピーコンストラクタとムーブコンストラクタは常に暗黙定義されるようになりました。しかし時には、それをコントロールしたくなることがあります。

[:contents]

### 暗黙のコンストラクタ

まず前提として、集成体はコピー/ムーブコンストラクタ宣言できなくなったからといって常にそれが`delete`されているわけではありません。通常のクラス型同様に暗黙的に宣言されており、含むメンバが全てムーブ構築可能であればそのムーブコンストラクタは有効となり、含むメンバがすべてコピー可能であればコピーコンストラクタが有効となります。

```cpp
#include <vector>
#include <memory>
#include <concepts>

struct A1 {
  int n;
  std::vector<int> v;
};

struct A2 {
  int n;
  std::unique_ptr<int> p;
};

// A2はコピー構築不可
static_assert(std::copyable<A1>);
static_assert(not std::copyable<A2>);

// どちらもムーブ構築可能
static_assert(std::movable<A1>);
static_assert(std::movable<A2>);
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/ob1Bq0BUGs55Ky9B)

単純に集成体のコピーを制御したければ、コピー不可能な型をメンバに持つことによって行うことができるわけです。

### 集成体の利便性とコンストラクタ

集成体にはいくつかメリットがあり、コピーを制御したいからといってそのメリットが失われてしまうことは好ましくありません。今回は次の3つを重視します

- 集成体初期化によるコンストラクタ定義の省略
- 指示付初期化
- 構造化束縛
    - これはコンストラクタを定義するだけでは失われない

コンストラクタを定義すると上2つは失われ、制御のためにメンバを追加すると3つ目の性質が損なわれます（受けるために余計な変数が増える）。

この3つを変わらず利用しつつコピー/ムーブコンストラクタを制御するには、コンストラクタを定義せずに余計なメンバを追加することも避けなければなりません。

### 解決策

まず次のような何でもなさそうな集成体を用意して、これについてコンストラクタの制御を試みます。

```cpp
struct A {
  std::size_t l;
  std::vector<int> v;
};


auto f() -> A {
  // 指示付初期化（+集成体初期化）
  return { .l = 4, .v = {1, 2, 3, 4}};
}

int main() {
  // 構造化束縛（2メンバ分）
  auto [l, v] = f();
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gCa0Rv5kbs5oyj12)

前述のように、この`A`にメンバを追加すると指示付初期化と集成体初期化には影響ありませんが、構造化束縛は3変数で受けないといけなくなります。

```cpp
struct A {
  std::size_t l;
  std::vector<int> v;
  int a = 0;
};


auto f() -> A {
  // 指示付初期化（+集成体初期化）
  return { .l = 4, .v = {1, 2, 3, 4}};  // ok
}

int main() {
  // 構造化束縛（2メンバ分）
  auto [l, v] = f();  // error、1つ足りない
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/P20QoxUVicKxUGwX)

メンバを追加せずに集成体のコピー/ムーブを制御するには、制御用のクラスを別に作って継承させてやります。

例えばムーブオンリーにしたければ次のような型を作って

```cpp
struct enable_move_only {
  enable_move_only() = default;

  enable_move_only(const enable_move_only &) = delete;
  enable_move_only& operator=(const enable_move_only&) = delete;

  enable_move_only(enable_move_only&&) = default;
  enable_move_only& operator=(enable_move_only&&) = default;
};
```

これを継承させてやります

```cpp
struct A : enable_move_only {
  std::size_t l;
  std::vector<int> v;
};

// コピー構築不可
static_assert(not std::copyable<A>);

// ムーブ構築可能
static_assert(std::movable<A>);
```

集成体は`public`に限って継承をすることができて、基底クラスは別に集成体型でなくても構いません。

この`A`は継承以前と同じように使用することができます。

```cpp
auto f() -> A {
  // 指示付初期化（+集成体初期化）
  return { .l = 4, .v = {1, 2, 3, 4}};  // ok
}

int main() {
  // 構造化束縛（2メンバ分）
  auto [l, v] = f();  // ok
}
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/C4Lz7nIgAYHOXtet)

非`tuple-like`な構造体に対する構造化束縛は、そのクラスの直接の非静的メンバのみを対象にとって分解しようとするため、基底クラスは無視されます。なおこのとき、基底クラスがメンバを持っているとエラーになりますが、今回の場合はメンバは必要ないので問題にはなりません。

この場合の指示付初期化は基底クラスに対する初期化子が省略されたものとして扱われエラーにならず、デフォルト初期化（デフォルトコンストラクタを呼ぶ初期化）によって初期化されます。

なお、`enable_move_only`にデフォルトコンストラクタを宣言しているのは、この場合に基底クラスが未初期化であるという警告を抑制するためです。集成体初期化において初期化子が省略されデフォルトメンバ初期化子も持たないメンバ（サブオブジェクト）はデフォルト初期化と呼ばれる初期化が行われるのですが、クラス型にデフォルトコンストラクタが存在しない場合は初期化しない初期化が行われます。それは`int`型の変数を`int n;`の様に宣言した場合と同様の初期化であり、値が不定となります。`enable_move_only`のような型はメンバを持たないので悪影響は皆無なのですが、警告はうざいのでデフォルトコンストラクタを追加しておきます（こうすると、デフォルトコンストラクタによって初期化される）。

ちなみにGCCでは、基底クラスに対する初期化子がないぞ！って警告が出ますが、現在のC++指示付初期化の仕様では基底クラスに対する指示付初期化の方法が無いのでどうしようもありません。無視するか`-Wno-missing-field-initializers`によって抑制しましょう・・・

さらに説明しておくと、`enable_move_only`のムーブコンストラクタをわざわざ書いているのは、コピーコンストラクタを宣言するとムーブコンストラクタの宣言は暗黙`delete`されるからです。`delete`かどうかに関係なく、コピーコンストラクタの宣言はムーブコンストラクタを暗黙的に削除するため明示的な宣言が必要です。ちなみにこれは逆（ムーブコンストラクタを`delete`宣言した場合）も同様です。

このテクニックは、`noncopyable`とかコピー禁止Mix-in等と呼ばれてC++11以前の世界でクラス型のコピーを禁止するためによく使用された古のテクニックの応用です。

### その他の場合

コピー/ムーブコンストラクタを制御したくなる時とは次の3パターンのいずれかになると思います。

1. ムーブのみ許可したい
2. ムーブもコピーも禁止したい
3. 常にコピーになってほしい

1の場合は先程の`enable_move_only`によって行えますが、他の場合の例も一応書いておきます。

2の場合

```cpp
// コピーとムーブを禁止する
struct disable_copy_move {
  disable_copy_move() = default;

  disable_copy_move(const disable_copy_move &) = delete;
  disable_copy_move& operator=(const disable_copy_move&) = delete;

  disable_copy_move(disable_copy_move&&) = delete;
  disable_copy_move& operator=(disable_copy_move&&) = delete;
};

// コピー構築不可
static_assert(not std::copyable<A>);

// ムーブ構築不可
static_assert(not std::movable<A>);
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/simJQwq1Nc5eZivH)


この時、ムーブもコピーも不可能なのに`f()`から`A`の値を返せているのは、C++17から保証されるようになった[コピー省略](https://cpprefjp.github.io/lang/cpp17/guaranteed_copy_elision.html)の効果によります。

3の場合（いつ？

```cpp
// ムーブを禁止（コピーとして実行）する
struct disable_move {
  disable_move() = default;

  disable_move(const disable_move &) = default;
  disable_move& operator=(const disable_move&) = default;

  disable_move(disable_move&&) = delete;
  disable_move& operator=(disable_move&&) = delete;
};

// コピー構築可能
static_assert(std::copyable<A>);

// ムーブ構築可能
static_assert(std::movable<A>);
```

- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/sjAwuh3daCNtiGNl)

この場合、ムーブ構築は常にコピー構築として実行されます。

### ADLの考慮

あるクラス型のオブジェクトに対するADLにおいては、そのクラス型の基底クラスの名前空間も考慮されるため、この`enable_move_only`などが別の名前空間にあるとADLによって予期しない関数呼び出しが行われる可能性があります。それを防ぐためにADL Firewallというテクニックがあります。詳細は以下を参照

- [ADL FIREWALL - 闇夜のC++](https://cpp.aquariuscode.com/adl-firewall)

### 参考文献

- [［C++］集成体の要件とその変遷 - 地面を見下ろす少年の足蹴にされる私](https://onihusube.hatenablog.com/entry/2019/02/22/201044)
- [C++ 集成体](https://github.com/onihusube/books/blob/master/cpp_aggregate/document.md)
- [More C++ Idioms/コピー禁止ミックスイン(Non-copyable Mixin)](https://ja.wikibooks.org/wiki/More_C%2B%2B_Idioms/%E3%82%B3%E3%83%94%E3%83%BC%E7%A6%81%E6%AD%A2%E3%83%9F%E3%83%83%E3%82%AF%E3%82%B9%E3%82%A4%E3%83%B3(Non-copyable_Mixin))
- [コピー禁止MIX-IN - 闇夜のC++](https://cpp.aquariuscode.com/uncopyable-mixin)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2022/20220923_aggreagate_ctor_ctrl.md)
