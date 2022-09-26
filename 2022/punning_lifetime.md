# ［C++］type punningとオブジェクト生存期間

この記事は規格書や提案書の様々な部分から感じ取れる規格文書の気持ちについての私の理解をまとめたものであり、必ずしも根拠や出典が明記されていない場合があり、内容も間違っている可能性があります。いわばポエムです。

[:contents]

### `std::bit_cast`

C++20で追加された`std::bit_cast`はあるオブジェクトのバイト表現（ビット列）を維持したまま別のオブジェクトとして扱うことを可能とするライブラリ機能です。このようなことは、type punningと呼ばれます。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  // double -> uint64_tのバイト表現を保った変換
  return std::bit_cast<std::uint64_t>(v);
}
```

よく知られているようにtype punningをしているつもりの多くのコードは未定義動作に陥っており、`std::bit_cast`はそれを合法かつ安全に、しかも定数式でも行うことができる唯一の方法です。

しかし、`std::bit_cast`が未定義動作を起こさない理由はどこにあって、他の方法はなぜ未定義動作となるのでしょうか？

### C++20以前の方法

以下の3つの方法のうち、最初の2つは未定義動作となる危険な手法です。

#### `reinterpret_cast`

`reinterpret_cast`はこういう場合に誰もが簡単に思いつく方法だと思います。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  auto* p reinterpret_cast<const std::uint64_t*>(&v);
  return *p;
}
```

ポインタは単にメモリアドレスであってメモリのどこかを指していてそこから値を読み出すだけなので、これは動作しそうに思えます。不思議ですね。

#### `union`

もうひとつよく知られているのは、`union`を使用した方法です。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  union U {
    double d;
    std::uint64_t n;
  };

  // doubleで初期化
  U u{v};

  // uint64_tとして読み出し
  return u.n;
}
```

これはC言語においては合法ですが、C++においては未定義動作とされます。共用体のメモリレイアウトを考えれば`u.d`も`u.n`も同じメモリ領域を参照しているのだから、これも動作しそうに思えます。不思議ですね。

#### `memcpy`

これはあまり知られてはいないようですが、`memcpy`を用いた方法があります。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  std::uint64_t n;

  // nの領域にvの値をコピー
  std::memcpy(&n, &v, sizeof(std::uint64_t));

  return n;
}
```

なんと、これはC++においても合法です。なんででしょうか、不思議ですね。

### `std::bit_cast`と`memcpy`の方法

`memcpy`による方法はC++17までの世界でtype punningを合法的に行う唯一の方法であり、`std::bit_cast`はそれを1つの関数にしたものです。従って、この2つの方法はおおよそ同じことをしていると思うことができます。

`memcpy`の方法を汎用的に書くと次のようになります（細かい制約は省略します）。

```cpp
template<typename To, typename From>
To bit_cast_by_memcpy(const From& from) {
  To to;  // デフォルト構築

  std::memcpy(&to, &from, sizeof(To));

  return to;  // 暗黙ムーブ？
}
```

こうしてみると、変換先の型`To`にデフォルト構築可能であることを要求していることが分かりやすくなります。あと多分`To`は少なくともムーブ構築可能である必要がありそうです。

この方法が好かれない？のは、`memcpy`を用いている点でしょう。他の方法はゼロコピーで行えるのに（`union`による方法はよく見るとコピーしてますが）、この方法は`memcpy`という明確なコピー操作を伴っています（実際には最適化によって取り除かれうるようです）。また、これによってC++では定数式でこの方法を実行できなくなっています。

`std::bit_cast`は`memcpy`の方法にあるそれらの問題を解消したものでもあります。その利点とは

- type punningを関数呼び出しとして1行で書ける
- 定数式で使用可能
- `To`の型にデフォルト構築可能性を要求しない
- のぞき穴的最適化が効きやすくなる
    - ゼロコピーになりやすくなる

などが考えられます。

より正確には、`std::bit_cast`はその実装については何も指定していません。C++23 ワーキングドラフトの[bit.cast]から翻訳すると、戻り値に関して次のように指定されているだけです

> （戻り値は）`To`型のオブジェクト。
> 結果の型（`To`）にネストされたオブジェクト（基底クラスやメンバ）を暗黙的に作成する。
> 結果オブジェクトの値表現の各ビットは、`from`オブジェクトの対応するビットと等しくなる。
> ...（以下パディングビットの扱いや、ビット表現に対応する値が無い場合、`from`のオブジェクト（サブオブジェクト）が生存期間の外にある場合、などについて述べられている）

ほとんどの場合、これはコンパイラの組み込み命令（通称コンパイラマジック）によって実装されるでしょう。

### 合法的type punning手法の境界

よく、`reinterpret_cast`や`union`による方法が未定義動作となるのはStrict Aliasing Ruleに抵触しているからだと言われます。たしかに`memcpy`の方法は抵触していませんが、`std::bit_cast`はどうなのでしょうか？`std::bit_cast`が合法なのはそういう関数だからでしょうか？それともコンパイラマジックで実装されるから？もちろん、そうではありません。

その境界線を別つのは、オブジェクトの生存期間（*lifetime*）という概念です。合法で行える方法は常に生存期間内にあるオブジェクトを参照してしかいません。

`union`による方法で見てみましょう

```cpp
#include <bit>

std::uint64_t punning(double v) {
  union U {
    double d;
    std::uint64_t n;
  };

  // doubleで初期化
  U u{v}; // (1)

  // uint64_tとして読み出し
  return u.n; // (2)
}
```

C++の共用体オブジェクトが生存期間内にある場合、そのメンバ変数はいずれか1つだけが生存期間内にあります。このメンバのことを特にアクティブメンバと呼びます。すなわち、(1)の部分で初期化されているのは`u.d`のみであり、以降この関数内で生存期間内にある`U`のメンバは`u.d`のみです。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  union U {
    double d;
    std::uint64_t n;
  };

  U u{v}; // ok、u.dをアクティブメンバとして初期化、u.dの生存期間が開始

  return u.n; // ub、u.nの生存期間は始まっていない（アクティブメンバはu.d）
}
```

C++において、生存期間外にあるオブジェクトの操作（値の読み出しや非静的メンバ関数/変数の使用）は未定義動作です。したがって、`union`の方法が未定義となるのは`return`文で非アクティブなメンバの値を読み出そうとしているところです。

共用体メンバの生存期間を切り替えるには明示的に非アクティブなメンバを初期化する必要がありますが、この関数ではそれは行われていません。

```cpp
U u{1.0}; // u.dがアクティブメンバ

{
  double d = u.d; // ok
  int n = u.n;    // ub、u.nは生存期間外
}

u.n = 10; // ok、u.dの生存期間は終了しu.nの生存期間が開始される

{
  double d = u.d; // ub、u.dは生存期間外
  int n = u.n;    // ok
}
```

これを踏まえると、`reinterpret_cast`の方法もポインタの参照先で生存期間内にあるオブジェクトとは別のオブジェクトに対してアクセスしようとしているため、未定義動作を踏んでいることがわかるでしょう。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  auto* p reinterpret_cast<const std::uint64_t*>(&v); // vには当然、double型のオブジェクトが生存期間内にある
  return *p;  // ub、pの参照先ではuint64_tのオブジェクトが生存期間内にない
}
```

これらが未定義となる理由がStrict Aliasing Ruleに抵触しているからという言説が間違っているとは言っていません。後述しますがおそらく、C++においてはそれも結局突き詰めるとこのオブジェクト生存期間の問題に帰結するためです。

### オブジェクト生存期間とC++のポインタ

### Strict Aliasing Rule


### `std::launder`

### `reinterpret_cast`

### Pointer lifetime-end zap


### pointer interconvertible

### implicitly create objects

### implicit-lifetime types

### 参考文献

- [`std::bit_cast` - cpprefjp](https://cpprefjp.github.io/reference/bit/bit_cast.html)
- [`std::bit_cast` - cppreference](https://en.cppreference.com/w/cpp/numeric/bit_cast)
- [bit_cast 実装イメージと未定義動作の話・ Issue #664 - cpprefjp/site](https://github.com/cpprefjp/site/issues/664)
- [（翻訳）C/C++のStrict Aliasingを理解する または - どうして#$@##@^%コンパイラは僕がしたい事をさせてくれないの！ - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20120220/p1)
- [Lifetime - cppreference](https://en.cppreference.com/w/cpp/language/lifetime)
