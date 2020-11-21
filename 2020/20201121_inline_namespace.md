# ［C++］inline名前空間の使途

### 1. `using namespace`の範囲を限定する

これは標準ライブラリではユーザー定義リテラルの定義と利用でよく利用されます。

例えば、`std::string_view`を簡易利用するための`sv`リテラルは次のように宣言されています。

```cpp
namespace std {

  // string_view本体
  template <class CharT, class Traits = char_traits<CharT>>
  class basic_string_view;

  inline namespace literals {
    inline namespace string_view_literals {

      // svリテラル
      constexpr std::string_view operator""sv(const char* str,   std::size_t len) noexcept;
    }
  }
}
```

これによって、`using namespace std;`という広すぎる範囲を`using`することなく、次のどちらかによってこの`sv`リテラルを使用することができます。

```cpp
#include <string_view>

int main() {
  {
    // 1、標準ライブラリの定義する全リテラルだけが使用可能になる
    using namespace std::literals;

    auto str = "literals"sv;
  }
  {
    // 2、string_viewのsvリテラルだけが使用可能になる
    using namespace std::string_view_literals;

    auto str = "string_view_literals"sv;
  }
  {
    // 2、std名前空間の神羅万象が利用可能になる
    using namespace std;

    auto str = "std"sv;
  }
}
```

`std::literals`名前空間は標準ライブラリの定義するすべてのユーザー定義リテラル（`s, h, m, s, i`などなど）が定義されている`inline`名前空間であり、それを`using namespace`するとそれらのリテラルだけではありますがすべてのものがそのスコープで見えるようになります。  
`std::string_view_literals`は`sv`リテラルだけが定義されている`inline`名前空間であり、`using namespace`しても`sv`リテラル以外のものは見えません。  
そして、これらのユーザー定義リテラルは`std`名前空間直下からも参照できます。

このようにライブラリの提供するものを`inline`名前空間である程度グループ化しておくことで、使う側は適宜必要な範囲だけを`using namespace`することができるようになります。

### 2. APIのバージョニング

これは多分最もポピュラーな`inline`名前空間の使い方でしょうか。

例えば、既に利用している関数があり、その関数のAPI（インターフェース）は変えないけれども内部実装を変更したい時を考えます。

```cpp
namespace mylib {
  int f(int a) {
    return a;
  }
}
```

この処理を、2倍してから返すようにしたいとします。

```cpp
namespace mylib {
  int f(int a) {
    return 2 * a; // 2倍して返すようにしたい
  }
}
```

しかし、この関数は既に至るところで使われており、変更するならしっかりテストしてからにしたいし、使われているとこを書き換えて回るのは嫌です。そんな時、変更前のバージョンを`inline`名前空間で、変更後のバージョンを名前空間で囲っておきます。

```cpp
namespace mylib::inline v1 {

  // 現在の処理
  int f(int a) {
    return a;
  }
}

namespace mylib::v2 {

  // 変更後の処理
  int f(int a) {
    return 2 * a; // 2倍して返すようにしたい
  }
}
```

そして、新しい関数`mylib::v2::f()`の実装とテストが完了してすべての`f()`を新バージョンへ切り替えたくなったら、それぞれの名前空間の`inline`指定を逆にします。

```cpp
// 古いバージョンを非inlineに
namespace mylib::v1 {

  // 現在の処理
  int f(int a) {
    return a;
  }
}

// 新しいバージョンをinlineに
namespace mylib::inline v2 {

  // 変更後の処理
  int f(int a) {
    return 2 * a; // 2倍して返すようにしたい
  }
}
```

`inline`名前空間は透過的です。そのため、これだけで、`f()`を使用しているところを一切書き換えることなくその処理内容をアップデートできます。もし古いバージョンを使いたい場合は`mylib::v1::f()`のように名前空間を明示的に指定してやればよく、古いバージョンを使用していることも分かりやすくなります。

### 3. ABIのバージョニング

`inline`名前空間はAPIでは省略可能ですが、ABI（マングル名）では通常の名前空間と同じ扱いをされ、常にマングル名に表示されていますし、参照するときも省略できません。`inline`名前空間の効果は純粋にC++の意味論上だけのものです。

この性質によって、APIは変わらないけれどABIを破壊するような変更がなされたときにその影響を軽減することができます。

```cpp
/// header.h

namespace mylib {
  class S {
    int m = 10;
  public:

    int get_m() const;
  };
}
```

```cpp
/// source.cpp

#include "header.h"

namespace mylib {

  int S::get_m() const {
    return this->m;
  }
}
```

```cpp
/// main.cpp

#include <iostream>

#include "header.h"

int main() {
  mylib::S s{};
  
  std::cout << s.get_m();
}
```

例えばこんなクラスとそのメンバ関数がありヘッダと実装が分かれているとき、これを利用する`main.cpp`が同じコンパイラを使って`source.cpp`をコンパイルしている間は何も問題はありません。

しかし、`source.cpp`を静的ライブラリや動的ライブラリの形であらかじめコンパイルしてから利用しているときに、この`mylib::S`にABIを破壊する変更がなされてしまったとします。

```cpp
/// header.h

namespace mylib {
  class S {
    float f = 1.0;  // メンバを追加した
    int m = 10;
  public:

    int get_m() const;
  };
}
```

このような変更はAPIに何も影響を及ぼしませんが、クラスのレイアウトが変更されているのでABIから見ると重大な変更です。ABIを破壊しています。

このとき、`source.cpp`をコンパイルした静的or動的ライブラリを再コンパイルせずに使い続けて（リンクして）いたとしてもコンパイラは何も言わないでしょう。この場合の変更によってはマングル名は変化しておらず、コンパイルもリンクもつつがなく完了します。

```cpp
/// main.cpp

#include <iostream>

// これは最新のものを参照しているとする
#include "header.h"
// source.cppは10年前にコンパイルしたものをリンクして使い続けているとする

int main() {
  mylib::S s{};
  
  std::cout << s.get_m(); // 未定義動作！
}
```

古い`S::get_m()`関数の定義は`source.cpp`をコンパイルした外部ライブラリにあり、`mylib::S`のレイアウトを知りません。したがって、レイアウト変更後のクラスのどこかの領域を`int`型のメンバ`S::m`として読みだした値を返してくれるでしょう（たぶん実行時エラーも起きないのではないかと思われます）。これは紛う事なき未定義動作です・・・

これは稀によくあるビルド済みバイナリをリンクして利用する時の問題で、C++でヘッダオンリーライブラリが好まれる傾向にある事の一つの理由でもあります。

こんな時、`inline`名前空間を利用することでこの問題の軽減を図れます。

#### リンクエラーにする

解決策の一つ目は、変更後のコードをそれを表す`inline`名前空間で囲ってしまう事です。

```cpp
/// header.h

// inline名前空間を追加する
namespace mylib::inline v2 {
  class S {
    float f = 1.0;  // メンバを追加した
    int m = 10;
  public:

    int get_m() const;
  };
}
```

```cpp
/// source.cpp

#include "header.h"

// inline名前空間を追加する
namespace mylib::inline v2 {

  int S::get_m() const {
    return this->m;
  }
}
```

`inline`名前空間はAPI（C++コード上）からは透過的ですがABI（マングル名）には表示されます。従って、この変更後の`mylib::S`およびそのメンバ関数を利用するコードに変更は必要ありませんが、そのマングル名は変更前のものと異なっています。  
結果、再コンパイルしないで用いている変更前ソースによるビルド済みバイナリからはそのようなシンボルが見つからずリンクエラーによってコンパイル時に気づくことができます。

```cpp
/// main.cpp

#include <iostream>

// これは最新のものを参照しているとする
#include "header.h"
// source.cppは10年前にコンパイルしたものをリンクして使い続けているとする

int main() {
  mylib::S s{};
  
  std::cout << s.get_m(); // リンクエラー、シンボルが見つからない
}
```

#### ABI互換性を確保する

もう一つの方法は初めから`inline`名前空間を利用していた場合にのみ利用可能となります。例えば先程のサンプルは初めから次のように`inline`名前空間に囲まれていたとします。

```cpp
/// header.h

// inline名前空間に包まれている
namespace mylib::inline v1 {

  class S {
    int m = 10;
  public:

    int get_m() const;
  };
}
```

```cpp
/// source.cpp

#include "header.h"

// inline名前空間に包まれている
namespace mylib::inline v1 {

  int S::get_m() const {
    return this->m;
  }
}
```

このコードに対して先程の変更がなされたとしましょう。その際、古いバージョンの`inline`名前空間を非`inline`にし、新しいバージョンの`inline`名前空間名を変更しておきます。

```cpp
/// header.h

// 古いバージョン、inline名前空間ではなくする
namespace mylib::v1 {

  class S {
    int m = 10;
  public:

    int get_m() const;
  };
}

// 最新版
namespace mylib::inline v2 {

  class S {
    float f = 1.0;  // メンバを追加した
    int m = 10;
  public:

    int get_m() const;
  };
}
```

```cpp
/// source.cpp

#include "header.h"

// 古いバージョン、inline名前空間ではなくする
namespace mylib::v1 {

  int S::get_m() const {
    return this->m;
  }
}

// 最新版
namespace mylib::inline v2 {

  int S::get_m() const {
    return this->m;
  }
}
```

こうして置いた状態で、さっきまでのように使用しようとすれば正しくリンクエラーになります。

今回のようにした場合は、逆に変更前のバージョンのものを参照し続けているようなプログラムに最新の`source.cpp`をビルドした（変更が反映された）バイナリをリンクした時でも、リンクエラーも未定義動作も起こさずに使用することができます。

```cpp
/// main.cpp
// 10年間のコードを参照ヘッダも含めて変更せずに使い続けているとする

#include <iostream>

// 変更前のものを参照している
#include "header.h"
// source.cppはさっきコンパイルした最新のものをリンクしているとする

int main() {
  // mylib::v1::Sを参照している
  mylib::S s{};

  // mylib::v1::S::get_m()を参照している
  std::cout << s.get_m(); // 10
}
```

`inline`名前空間はマングル名レベルでは名前空間と区別なく扱われます。すなわち、ABIからは名前空間名が`inline`であるかどうかは分かりません。したがって、このように変更を追記し古いバージョンを維持しておけば、古いバージョンを利用しているプログラムに対しても古いバージョンを提供し続けることができます。これによって、ABI互換性を維持し、ABIを保護することができます。

GCCやclangの最近の標準ライブラリの実装では、ABI保護のために`inline`名前空間が多用されています。

### 4. 名前の衝突を回避する

これは特にCPO（*Customization Point Object*）の定義で利用されています。

CPOはその呼び出しに当たって自身と同名の非メンバ関数をADLで探索するようになっていることがよくあります。これはあるクラスに対して*Hidden friends*と呼ばれる`friend`関数を探し出すものです。

一方で、標準ライブラリにあるCPOは一部のものを除いて`std`名前空間のすぐ下に定義されることになります。

すると、標準ライブラリにあるクラスに対する*Hidden friends*関数とCPO名とで名前が衝突してしまいます。

```cpp
namespace mystd {
  
  namespace cpo_impl {
    
    // swap CPOの実装クラス
    struct swap_cpo {
      
      template<typename T, typename U>
      void operator()(T&, U&) const;
    };
  }

  // swap CPO #1
  inline constexpr cpo_impl::swap_cpo swap{};
  
  struct S {
    
    // Hidden friendsなswap関数 #2
    friend void swap(S& lhs, S& rhs);
  };
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/Vf0AnJY7ZbsV4zl7)

この例では#1と#2の異なる宣言が同じ名前空間にあるためにコンパイルエラーになっています。

このように、CPOと同じ名前空間にあるものがそのCPOにアダプトしようとすると名前衝突してしまうわけです。

この場合にCPOの定義を`inline`名前空間で囲ってやることでこの問題を解決できます。しかも、呼び出す際に名前空間名が増えることもありません。

```cpp
namespace mystd {
  
  namespace cpo_impl {
    
    // swap CPOの実装クラス
    struct swap_cpo {
      
      template<typename T, typename U>
      void operator()(T&, U&) const;
    };
  }

  // CPO定義をinline名前空間で囲う
  inline namespace cpo {
    // swap CPO #1
    inline constexpr cpo_impl::swap_cpo swap{};
  }
  
  struct S {
    
    // Hidden friendsなswap関数 #2
    friend void swap(S& lhs, S& rhs);
  };
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/lLYmmUr5q8KIooCb)


こうしても`mystd::swap`という名前で`swap`CPOを参照できますし、#1と#2の`swap`は別の名前空間にいるために名前は衝突していません。  
このため、標準ライブラリにあるCPOはほとんどのものが`inline`名前空間に包まれています。

ここでは説明のために変な名前空間と適当なクラスを用意しましたが、`mystd`を`std`、`mystd::S`を`std::vector`とかに読み替えるとつかみやすいかもしれません。

### 参考文献

- [インライン名前空間 - cpprefjp](https://cpprefjp.github.io/lang/cpp11/inline_namespaces.html)
- [ユーザー定義リテラル - cpprefjp](https://cpprefjp.github.io/lang/cpp11/user_defined_literals.html)
- [Why does range-v3 put its function objects into an inline namespace? - stackoverflow](https://stackoverflow.com/questions/50010074/why-does-range-v3-put-its-function-objects-into-an-inline-namespace)
- [GCC5以降のlibstdc++のデフォルトABI変更について - KMC Staff Blog](http://blog.kmckk.com/archives/5425614.html)
- [GCC compatibility: inline namespaces and ABI tags - Christian Aichinger](https://greek0.net/blog/2016/10/29/gcc_compatibility/)
- [Inline Namespaces 101 - foonathan::​blog()](https://foonathan.net/2018/11/inline-namespaces/)