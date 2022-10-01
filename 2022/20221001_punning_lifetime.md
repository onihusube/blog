# ［C++］type punningとオブジェクト生存期間

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

以下の3つの方法のうち、最初の2つは未定義動作となる危険な方法です。

#### `reinterpret_cast`

`reinterpret_cast`はこういう場合にまず思いつく方法だと思います。

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

これは有名なわりに知名度がない気がするのですが、`memcpy`を用いた方法があります。

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

この方法が好かれない？のは、`memcpy`を用いている点でしょう。他の方法はゼロコピーで行えるのに（`union`による方法はよく見るとコピーしてますが）、この方法は`memcpy`という明確なコピー操作を伴っています（実際には最適化によって取り除かれうるようです）。また、`memcpy`が`constexpr`ではないことからC++では定数式でこの方法を実行できなくなっています。

`std::bit_cast`は`memcpy`の方法にあるそれらの問題を解消したものでもあります。その利点とは

- type punningを関数呼び出しとして1行で書ける
- 定数式で使用可能
- `To`の型にデフォルト構築可能性を要求しない
- のぞき穴的最適化が効きやすくなる
    - コピーを削減しやすくなる

などが考えられます。

より正確には、`std::bit_cast`はその実装については何も指定していません。C++23 ワーキングドラフトの[[bit.cast]](http://eel.is/c++draft/bit.cast)から翻訳すると、戻り値に関して次のように指定されているだけです

> （戻り値は）`To`型のオブジェクト。
> 結果の型（`To`）にネストされたオブジェクト（基底クラスやメンバ）を暗黙的に作成する。
> 結果オブジェクトの値表現の各ビットは、`from`オブジェクトの対応するビットと等しくなる。
> ...（以下パディングビットの扱いや、ビット表現に対応する値が無い場合、`from`のオブジェクト（サブオブジェクト）が生存期間の外にある場合、などについて述べられている）

ほとんどの場合、これはコンパイラの組み込み命令（通称コンパイラマジック）によって実装されるでしょう。

### 合法的type punning手法の境界

よく、`reinterpret_cast`や`union`による方法が未定義動作となるのはStrict Aliasing Ruleに抵触しているからだと言われます。たしかに`memcpy`の方法は抵触していませんが、`std::bit_cast`はどうなのでしょうか？`std::bit_cast`が合法なのはそういう関数だからでしょうか？それともコンパイラマジックで実装されるから？もちろん、そうではありません。

その境界線を別つのは、オブジェクトの生存期間（*lifetime*）という概念です。合法で行える方法は常に生存期間内にあるオブジェクトを参照してしかいません。

`union`による方法を見てみましょう

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

C++の共用体オブジェクトが生存期間内にある場合、そのメンバ変数はいずれか1つだけが生存期間内にあります。このメンバのことを特にアクティブメンバと呼びます。(1)の部分で初期化されているのは`u.d`のみであり、以降この関数内で生存期間内にある`U`のメンバ（アクティブメンバ）は`u.d`のみです。

C++において、生存期間外にあるオブジェクトの操作（値の読み出しや非静的メンバ関数/変数の使用）は未定義動作です（[[basic.life]/4](http://eel.is/c++draft/basic.life#4)）。したがって、`union`の方法が未定義となるのは(2)で非アクティブなメンバの値を読み出そうとしているところです。

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

共用体のアクティブメンバを切り替えるには明示的に非アクティブなメンバを初期化する必要がありますが、この関数ではそれは行われていません。

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

これを踏まえると、`reinterpret_cast`の方法もポインタの参照先で生存期間内にあるオブジェクトとは別のオブジェクトに対してアクセスしようとしているため、未定義動作を踏んでいることがわかります。

```cpp
#include <bit>

std::uint64_t punning(double v) {
  auto* p reinterpret_cast<const std::uint64_t*>(&v); // vには当然、double型のオブジェクトが生存期間内にある
  return *p;  // ub、pの参照先ではuint64_tのオブジェクトが生存期間内にない
}
```

`std::bit_cast`が未定義とならない理由は、その効果が明確に`To`のオブジェクトを返すと指定されていることによります。これは生存期間内にあるオブジェクトを返すという意味であり、その実装の如何によらず戻り値のオブジェクトは生存期間内にあることが保証され、コンパイラはそう認識します。合法性を保つ重要な点は返されるオブジェクトが入力のバイト表現を保ちながらも生存期間が開始していることが保証されているところにあります。

`memcpy`の方法が未定義とならない理由は生存期間が既に開始しているオブジェクトに対して、別のオブジェクト由来のバイト表現をコピーしているからです。`memcpy`によるバイト表現のコピーによる書き換えはその場所にあるオブジェクトの生存期間を終了させないため、コピー前後でオブジェクトは生存期間内にあり続けます。これは`memmove`を使用しても同じ保証が得られますが、それ以外に同様の保証がある関数は無いようです。

#### 余談

ところで、`memcpy`の方法が真に合法であることを確認するには、バイト表現を`memcpy`によってコピーした時でもオブジェクトの有効性は保たれ続けるのかということを確認しなければなりません。巷にある説明（つまりググって出てきたもの）にはその部分に言及しているものが見つからず、`memcpy`の方法は合法だから合法なのだという感じで終了している気がします。

[cppreferenceの`std::memcpy`のページ](https://en.cppreference.com/w/cpp/string/byte/memcpy)には、以前（2015）から次のような記述があります

> Where strict aliasing prohibits examining the same memory as values of two different types, `std::memcpy` may be used to convert the values.

これは[Cのリファレンス](https://en.cppreference.com/w/c/string/byte/memcpy)から持ってきたもののようで、おそらくCからずっと`memcpy`にはこういう効果があったのでしょう。

じゃあこれを裏付ける規定は規格書のどこにあるのか？というと見つかりませんでした・・・

近しい規定は[[basic.types.general]/2](http://eel.is/c++draft/basic.types.general#2)

> *Trivially Copyable*な型`T`の任意のオブジェクト（*potentially-overlapping*サブオブジェクトを除く）は、そのオブジェクトが型`T`の有効な値を保持しているかどうかに関わらず、基礎となるバイトを`char, unsigned char, std::byte`の配列にコピーすることができる。  
> その配列の内容が元のオブジェクトにコピーし直された場合、オブジェクトはその後元の値を保持する。
> 
> ```cpp
> constexpr std::size_t N = sizeof(T);
> char buf[N];
> T obj;                          // objは元の値で初期化されている
> std::memcpy(buf, &obj, N);      // この2つのmemcpy呼び出しの間にobjが変更されたとしても
> std::memcpy(&obj, buf, N);      // この時点で、objのスカラ型のサブオブジェクトは元の値を保持する
> ```

及び[[basic.types.general]/3](http://eel.is/c++draft/basic.types.general#3)に見つけることができます。

> *Trivially Copyable*な型`T`の異なる2つのオブジェクト`obj1, obj2`（`obj1`と`obj2`は*potentially-overlapping*サブオブジェクトではない）は、`obj1`を構成する基礎となるバイトが`obj2`にコピーされると、その後`obj2`は`obj1`と同じ値を保持する。
> 
> ```cpp
> T* t1p;
> T* t2p;
>     // t2pは初期化済のオブジェクトを指しているとする
> std::memcpy(t1p, t2p, sizeof(T));
>     // この時点で、*t1pのTrivially Copyableな型の全てのサブオブジェクトには、*t1pの対応するサブオブジェクトと同じ値が含まれる
> ```

ここに書かれているのは、まず、*Trivially Copyable*な任意の型`T`のオブジェクトについてバイト表現をバイト列（`char, std::byte`等の配列）としてコピーすることができて、別の場所にコピーしたものを後で書き戻した後で、そのオブジェクトはコピーした時点と同じ値を持つということです。そして、同じ*Trivially Copyable*な型`T`のオブジェクトの間でバイト表現をコピーすることもできて、その場合はコピー元とコピー先オブジェクトは同じ値を持つということです。

これら2つの規定からまず読み取れることは、`memcpy`によるバイト表現の上書きコピーはオブジェクトの生存期間を終了させないということです。

そして、これら2つのケースにおいてコピー元バイト列の出所を気にしないようにすると（すなわち、バイト列のコピーとはいつもそのバイト列に対応する値からのコピーであると思うようにすると）、`memcpy`によるtype punningの合法性が導けます。

ただし、[`std::bit_cast`の規定](http://eel.is/c++draft/bit.cast#2)にあるように、不定値やそれを含むオブジェクトからのコピーや、コピーしたバイト表現に対応する値をコピー先オブジェクトが持たない場合、結果は未規定ないし未定義動作になるでしょう。

とはいえ、これらの推測は明確に書かれていることではないので間違っているかもしれません（詳しい方いましたら教えてください・・・）。しかし、`memcpy`によるtype punningが合法であるのは間違いないはずです。

### 制約について

ここまで特に触れていませんが、ここまで書かれていることは型が*Trivially Copyable*であることを前提としています。`std::bit_cast`と`memcpy`によるtype punningを合法的に行うには`To`と`From`の型が共に*Trivially Copyable*でありサイズが同じでなければなりません。例えば、`std::vector`のような型（確実に*Trivially Copyable*ではない）を合法的にtype punningする方法は存在しないし、`int32_t`を`double`（通常8バイト）としてpunningすることもできないわけです。

前項の`memcpy`の規定に関しても、型が*Trivially Copyable*である場合にのみ保証されています。

### おわり

ここまで読むと、type punningの合法性についてStrict Aliasing Ruleに抵触しているからという理由は間違っているのか？と思うかもしれませんが、そうではありません。この記事の最終的な主張はここで述べていることとStrict Aliasing Ruleによることは同じ事について別の側面から見たものにすぎず、同じことを言っているという事です。

実のところ、これはそのような主張のポエムの序文です。次回は、ここでの`reinterpret_cast`によるtype punningのコードから出発して、オブジェクト生存期間とポインタについての独自研究が展開される予定です。

### 参考文献

- [`std::bit_cast` - cpprefjp](https://cpprefjp.github.io/reference/bit/bit_cast.html)
- [`std::bit_cast` - cppreference](https://en.cppreference.com/w/cpp/numeric/bit_cast)
- [Lifetime - cppreference](https://en.cppreference.com/w/cpp/language/lifetime)
- [bit_cast 実装イメージと未定義動作の話・ Issue #664 - cpprefjp/site](https://github.com/cpprefjp/site/issues/664)
- [（翻訳）C/C++のStrict Aliasingを理解する または - どうして#$@##@^%コンパイラは僕がしたい事をさせてくれないの！ - yohhoyの日記](https://yohhoy.hatenadiary.jp/entry/20120220/p1)
- [What is the Strict Aliasing Rule and Why do we care? - Github](https://gist.github.com/shafik/848ae25ee209f698763cffee272a58f8)
