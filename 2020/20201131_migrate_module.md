# ［C++］モジュールへの移行を考える

C++20ではモジュールが導入され、C++は長年欠いていたプログラムの分割と構成の効率的な手段を手に入れました。[MSVCは既に実装を完了しており](https://devblogs.microsoft.com/cppblog/a-tour-of-cpp-modules-in-visual-studio/)、[GCC11も来年春に使用できるようになるかもしれない](https://www.phoronix.com/scan.php?page=news_item&px=GCC-Modules-Code-Review)など、モジュールを利用可能な環境は着実に整いつつあります。  
ところが、モジュールは複雑に規定されており、そこそこ分量がある上にあっちこっちに散らばっていて、規格書をちょっと読んだだけではなんだかよく分かりません。

この一連の記事は面倒な聖典の解釈作業を避けてモジュールを使用してもらうために、今まで当たり前に書いていたコードはモジュールによってどのように書くの？という疑問を解消するための一助となれたらいいなあというものです。

## 目次（予定）

1. 単一ヘッダファイル+単一ソースファイル（この記事）
2. 単一ヘッダファイル+複数ソースファイル
3. 複数ヘッダファイル+単一ソースファイル
4. 複数ヘッダファイル+複数ソースファイル
5. ヘッダオンリー
6. モジュールとヘッダファイルの同時提供

## 1 - 単一ヘッダファイル+単一ソースファイル

まず最初は最も普通な構成と思われる、ヘッダとソースが1つづつある場合のプログラムの移行について見てみます。

```cpp
/// mylib.h

namespace mylib {

  class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  void print_S(const S& s);
}
```

```cpp
/// mylib.cpp

#include <iostream>
#include "mylib.h"

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

このような構成のファイルは一対一でモジュールインターフェース単位とモジュール実装単位が対応します。

まずヘッダファイルはモジュールインターフェース単位に対応し、次のように書くことになります。。

```cpp
/// mylib.ixx

export module mylib;  // mulibモジュールのインターフェース単位の宣言

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  // フリー関数のエクスポート
  export void print_S(const S& s);
}
```

モジュールインターフェース単位であることは、ファイル先頭の`export module mylib;`によって宣言します（これをモジュール宣言と呼びます）。以降このファイルは`mylib`モジュールのインターフェースとして扱われます（ファイル拡張子は実装によって変わります。`.ixx`はMSVCの指定する拡張子です）。  
`mylib`の部分はモジュールの名前であり、`.`が使用可能なこと以外は名前空間の名前とほぼ同様の規則の下で自由な名前を付けることができます。

モジュールのインターフェースにはヘッダファイルと同様に外部に公開したいものの宣言を書きます。`export`をその先頭に付加することで公開したい宣言を明示します。

次に、ソースファイルはモジュール実装単位に置き換えられます。

```cpp
/// mylib.cpp

module; // グローバルモジュールフラグメント

// #includeはグローバルモジュールフラグメント内で行う
#include <iostream>

module mylib;  // mylibモジュールの実装単位の宣言
// mylibモジュールのインターフェースを暗黙にインポートしている

// ここから下は書き換える必要が無い
namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

モジュール実装単位であることは、ファイル先頭の`module mylib;`によって宣言します（これもモジュール宣言と呼びます）。このとき、モジュール名は先程のインターフェースを作った時と同じ名前にします。このモジュール宣言以降、このファイルは`mylib`モジュールの実装単位として扱われます。  
この例のように、従来のヘッダファイルのインクルードが必要となるときはグローバルモジュールフラグメントを利用します。モジュール宣言のさらに前で`module;`と書いておくことでそこからモジュール宣言までの間の領域がグローバルモジュールフラグメントとして扱われます。

モジュール実装単位は対応するインターフェース単位を暗黙にインポートしています。すなわち、先程別ファイルに書いた`mylib`モジュールのインターフェース単位内のものを（ここでは前方宣言として）参照することができます。

このようにモジュールへの移行自体はとても簡単で、モジュール宣言をファイル先頭で行って公開する宣言に`export`を付ける以外は、ほぼ従来通りに書くことができます。

### プライベートモジュールフラグメント

ヘッダもソースもそれぞれ1つしかない場合、わざわざファイルを分けずに1ファイルでモジュールを完結させたいことが多いと思われます。そのような場合に、プライベートモジュールフラグメントを利用できます。

プライベートモジュールフラグメントを使用すると、先程モジュールとして定義した2つのインターフェース単位と実装単位は次のようにまとめられます。

```cpp
/// mylib.ixx

module; // グローバルモジュールフラグメント

// #includeはグローバルモジュールフラグメント内で行う
#include <iostream>

export module mylib;
// ここからはインターフェース

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  // フリー関数のエクスポート
  export void print_S(const S& s);
}

// インターフェースはここまで
private : module;
// ここからが実装

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

ファイル途中の`private : module;`というのが、プライベートモジュールフラグメントであり、そこを境界としてインターフェースと実装を1つのファイル内で分割します。すなわち、`private : module;`よりも前の領域がインターフェース単位に、後ろの領域が実装単位に対応しています。  
プライベートモジュールフラグメントの実装部分ではグローバルモジュールフラグメントを作れないので、グローバルモジュールフラグメントはファイルの先頭に移動することになりますが、それ以外は2つのファイルでモジュール化したときと同様に書くことができます。

なお、プライベートモジュールフラグメント内では`export`を伴う宣言を行うことはできず、行った場合コンパイルエラーになります。

正確な用語では、プライベートモジュールフラグメントというのは`private : module;`←これの事ではなく、それを使用したファイルあるいはモジュールの事を指すのでもなく、`private : module;`の直後からそのファイル終端までの実装部分の領域の事を指しています。

### 利用側

普通の方法とプライベートモジュールフラグメントによる方法のどちらを用いたとしてもモジュールを利用する側からはそれを観測することはできず、同じように利用できます。

```cpp
import mylib; // mylibモジュールのインポート宣言

int main() {
  mylib::S s1{};
  mylib::S s2{20};
  
  mylib::print_S(s1); // 0
  mylib::print_S(s2); // 20
}
```

モジュールの使用はインポート宣言によって行い、`import`に続いてモジュール名を指定します（セミコロンは必須です）。モジュール名はモジュールを作るときのモジュール宣言に指定した名前と同じ名前を指定します。

そしてこの時、モジュールのグローバルモジュールフラグメントでインクルードしたヘッダの内容はインポートした側からは参照することができません。

```cpp
import mylib; // mylibモジュールのインポート宣言

int main() {
  std::cout << "hello world.";  // コンパイルエラー！
}
```

グローバルモジュールフラグメントでヘッダをインクルードするように推奨するのは、このような保護が働くためです。というか、グローバルモジュールフラグメントはそのために用意されたものです。

### おまけ 一括`export`

公開する宣言に`export`を付けるというのは、その数が多くなると面倒くさくなりがちです。そこで、ある名前空間にあるものをすべてエクスポートする場合は、その名前空間ごとエクスポートすることで一括処理可能です。

```cpp
/// mylib.ixx

export module mylib;  // mulibモジュールのインターフェース単位の宣言

// 名前空間ごとエクスポート！
export namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  // フリー関数のエクスポート
  void print_S(const S& s);
}
```

また、エクスポートしたいものをある程度まとめることができる場合、ブロックで囲うことでも一括処理することができます。

```cpp
/// mylib.ixx

export module mylib;  // mulibモジュールのインターフェース単位の宣言

namespace mylib {

  // エクスポートブロック、このブロックはスコープを作らない
  // 内部のものはすべてエクスポート！
  export {
     // クラスのエクスポート、暗黙に全メンバがエクスポートされる
     class S {
       int m_num = 0;
     public:

       S();
       S(int n);

       int get() const;
     };

     // フリー関数のエクスポート
     void print_S(const S& s);
  }

  // エクスポートされない
  void private_func(int);
}
```

このような一括`export`をする場合どちらの方法を使った時でも、`export`しているブロック`{}`の内部で`export`することはできません。

## 2 - 実装の隠蔽について

前回書き忘れていました・・・

前回、次の様な2つのファイルによってモジュールを構成していました。

```cpp
/// mylib.ixx

export module mylib;  // mulibモジュールのインターフェース単位の宣言

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  // フリー関数のエクスポート
  export void print_S(const S& s);
}
```

```cpp
/// mylib.cpp

module; // グローバルモジュールフラグメント

// #includeはグローバルモジュールフラグメント内で行う
#include <iostream>

module mylib;  // mylibモジュールの実装単位の宣言
// mylibモジュールのインターフェースを暗黙にインポートしている

// ここから下は書き換える必要が無い
namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

そして、このモジュールを利用する側では次のようにします。

```cpp
import mylib; // mylibモジュールのインポート宣言

int main() {
  mylib::S s1{};
  mylib::S s2{20};
  
  mylib::print_S(s1); // 0
  mylib::print_S(s2); // 20
}
```

この例ではインターフェース（`mylib.ixx`）で宣言されたものしか使用していません。もし実装単位でしか宣言・定義されていないものを参照したらどうなるのでしょう？

```cpp
/// mylib.cpp

module;

#include <iostream>

module mylib;

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }

  // 実装単位だけで宣言されている関数
  void private_func() {
    std::cout << "private\n";
  }
}
```

```cpp
import mylib;

int main() {
  mylib::private_func();  // コンパイルエラー！
}
```

モジュールの実装単位（あるいはプライベートモジュールフラグメントの実装部分）だけで宣言されているものは、外部から完全に参照できません。モジュール実装単位にあるものをモジュール外部から参照するには、予めそのインターフェース単位において`export`宣言をしておく必要があります。

「外部から __完全__ に参照できない」というのは、従来のソースファイル（`.cpp`）なら宣言を用意してしまえばヘッダに無い物も呼び出せていたところでも、モジュール実装単位にしかないものはその外側から参照する手段が全く無いという事です。

```cpp
/// test.h

int f();
```

```cpp
/// test.cpp

#include "test.h"

int f() {
  return 10;
}

int g() {
  return 20;
}
```

```cpp
/// main.cpp

#include <iostream>

#include "test.h"

int g();  // 対応する宣言を勝手に追加してしまう

int main() {
  std::cout << f() << std::endl;  // 10
  std::cout << g() << std::endl;  // 20
}
```
- [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/xZavZdTtlHgA4XTA)

こんな事をすべきではありませんが出来てしまいます。これもヘッダファイルがプログラム分割のための適切な手法ではない事の証左でもあります。

モジュールの実装単位では、`export`されていない宣言・定義を呼び出す手段はありません。そして、`export`はモジュールのインターフェース単位でしか行うことができません。従って、モジュールの実装部にあるものは外部からは完全に隠蔽されています。

このことは実装単位でもインターフェース単位でも変わりません。インターフェース単位で`export`していない宣言をモジュール外部から呼び出す手段は基本的にはありません。

```cpp
/// mylib.ixx

export module mylib;

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  // フリー関数のエクスポート
  export void print_S(const S& s);

  
  // エクスポートされない関数
  void non_expote_func(int n) {
    std::cout << n;
  }
}
```

```cpp
import mylib;

int main() {
  mylib::non_expote_func();  // コンパイルエラー！
}
```

（この含みのある言い方は、実は間接的に呼び出す手段があることを意味しています・・・・）

### リンケージ

リンケージという言葉が分かる人に向けて少し詳しく解説です。

先程の宣言を勝手に追加して呼び出せてしまう例がなぜできるのかというと、関数`g()`が外部リンケージを持っているからです。外部リンケージを持つ名前は翻訳単位を超えて参照することができます。従って、ヘッダファイルに無く見えていなくても、全く同じ名前を用意することができれば、それを通じて翻訳単位を超えた参照を行えるわけです。  
これを呼び出せなくするには内部リンケージを与えてやれば良くて、そのもっとも単純な方法は`static`を付加することです。

C++20においてもリンケージの持つ意味は変わっていません。そしてモジュールでは、`export`宣言による名前だけが外部リンケージを持ちます。従来内部リンケージを持つものはそのまま内部リンケージをもつためその翻訳単位内でしか参照できません。  
残った、従来は外部リンケージを持っていたものについては、新しいリンケージ区分であるモジュールリンケージが与えられます。

モジュールリンケージを持つ名前は同じモジュール（モジュール宣言時の名前が同じモジュール名のモジュール）内でのみ翻訳単位を超えて参照することができますが、モジュールの外側からは参照できません。これはちょうど内部リンケージを同モジュール内部まで少しだけ拡張したものです。  
そして、一度与えられたリンケージはその後変化することはありません。

```cpp
/// mylib.ixx

export module mylib;

namespace mylib {

  export int f(); // 外部リンケージ
  static int g(); // 内部リンケージ
  int h();        // モジュールリンケージ
}
```

```cpp
/// mylib.cpp

module mylib;

namespace mylib {

  // 再宣言、外部リンケージを持つ
  int f() {
    return 1;
  }

  // インターフェース単位のg()とは別物、内部リンケージ
  static int g() {
    return 2;
  }

  // 再宣言、モジュールリンケージを持つ
  int h() {
    return 3;
  }
}
```

## 3 - 複数ヘッダファイル+単一ソースファイル

```cpp
/// mylib1.h

namespace mylib {

  class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };
}
```

```cpp
/// mylib2.h

namespace mylib {

  void print_S(const S& s);
}
```

```cpp
/// mylib.cpp

#include <iostream>
#include "mylib1.h"
#include "mylib2.h"

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

例えばこんな風に、ヘッダが分割されてるけど実装は1ファイルで行われているときの事です。

モジュールにおいては、インターフェース単位と実装単位はそれぞれ一つづつしか存在してはいけません。そのため、インターフェース単位を複数作ることは出来ません、多分コンパイルエラーとなるはずです。

しかし、何かしらの基準でもってインターフェースをいくつかのファイルに分けておきたいこともあるでしょう。そんなときのために、モジュールはパーティションによって分割することができます。2つのヘッダファイルは2つのインターフェースパーティションが対応します。

```cpp
/// mylib_interface1.ixx

// mulibモジュールのインターフェースパーティションの宣言
export module mylib:interface1;

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };
}
```

```cpp
/// mylib_interface2.ixx

// mulibモジュールのインターフェースパーティションの宣言
export module mylib:interface2;

// クラスSの宣言を参照するためにインポートする
import :interface1;

namespace mylib {

  // フリー関数のエクスポート
  export void print_S(const S& s);
}
```

```cpp
/// mylib.ixx

// mulibモジュールのプライマリインターフェース単位の宣言
export module mylib;

// 全てのインターフェースパーティションの再エクスポート、必須！
export import :interface1;
export import :interface2;

// 書くことがないので空、ここでさらに宣言をしてもいい
```

```cpp
/// mylib.cpp

module;

#include <iostream>

// mylibモジュールの実装単位の宣言
module mylib;

// mylibモジュールのインターフェースを暗黙にインポートしており
// それを通して全てのパーティションも暗黙にインポートしている

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

この様に、複数のヘッダファイルはインターフェースパーティションが対応します。インターフェースパーティションであることは、モジュール宣言においてモジュール名の後に`:パーティション名`を続けることで行います。

```cpp
// モジュールインターフェースパーティションの宣言
export module mylib:interface1;
export module mylib:interface2;

// プライマリインターフェース単位の宣言
export module mylib;
```

`:`で区切られていることがパーティションである証です。コンパイラさんもこれを見て判別します。

インターフェースパーティションと区別するために、パーティションではないインターフェース単位の事をプライマリインターフェース単位と呼びます。そして、同じモジュールに属しているインターフェースパーティションは全てプライマリインターフェース単位からエクスポートする必要があります。これがなされないとモジュール外から参照できません。

インターフェースパーティションのエクスポートは`export import`に続いて`:`とパーティション名を指定することで行い、これはそのパーティションをインポートしながらエクスポートも行う構文です（再エクスポートなどとも呼ばれます）。

```cpp
// インターフェースパーティションの再エクスポート
export import :interface1;
export import :interface2;

// これはエラー、モジュール名が余計
export import mylib:interface1;

// 普通のモジュールの再エクスポート（otherlibというモジュールがあったとして）
export import otherlib;
```

なんとなく気持ち悪いかもしれませんが、インターフェースパーティションをインポート/再エクスポートするときは、パーティション名の前に`:`が必須です。モジュール名はあってはならず、`:`は無くてはなりません。

再エクスポートをする事によって、インターフェースパーティション内の宣言があたかもプライマリインターフェース単位にあるかのようにモジュールを使う側からは見えるようになります（”あたかも”であって`#include`のようにコピぺしているわけではありません）。

なお、再エクスポート自体はパーティションだけでなく一般のモジュールでも行うことができます。ただし、当然ながらモジュールの外や実装単位では行えず、モジュールのインターフェース単位（パーティション含む）でだけ行うことができます。

この例の`interface2`パーティションのように、他のインターフェスにある宣言を参照したいときはそのインターフェースをインポートすることができます。

```cpp
// 他インターフェースパーティションのインポート
import :interface1;
```

プライマリインターフェース単位からはそのモジュールにあるすべてのインターフェースパーティションがエクスポートされている必要があります（チェックされるとは言ってない）。そして、モジュール実装単位はプライマリインターフェース単位を暗黙的にインポートしています。  
従って、実装単位からはパーティションも含めたすべてのインターフェスの宣言が常に見えています。そのため、この例の場合はモジュール実装単位を書き換える必要はありません。

### 別の書き方

先程はヘッダファイル2つをインターフェースパーティション2つに対応させましたが、別にそれぞれを対応させる必要はなくて、1つだけをインターフェースパーティションにしてしまうだけでもokです。

```cpp
/// mylib_interface.ixx

// mulibモジュールのインターフェースパーティションの宣言
export module mylib:interface;

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };
}
```

```cpp
/// mylib.ixx

// mulibモジュールのプライマリインターフェース単位の宣言
export module mylib;

// インターフェースパーティションの再エクスポート
export import :interface;

namespace mylib {

  // フリー関数のエクスポート
  // :interfaceがインポート（再エクスポート）されているので、Sは参照可能
  export void print_S(const S& s);
}
```

こうしたとしても、先程と全く同じようにモジュールを構成できます。

インターフェースパーティションをどう分けるか、プライマリインターフェースに何を書くか、あるいは何も書かないか、などは自由です。将来的に広くコンセンサスの取れた書き方ができるかもしれませんが、基本的には各人の好みで書くことができます。

### 利用側

利用側は全く変わりません。インターフェースパーティションへの分割以前と同じように利用することができます。

```cpp
import mylib; // mylibモジュールのインポート宣言

int main() {
  mylib::S s1{};
  mylib::S s2{20};
  
  mylib::print_S(s1); // 0
  mylib::print_S(s2); // 20
}
```

モジュールをその内部でどうインターフェースパーティションに分割しようが、プライマリインターフェース単位からの再エクスポートを忘れさえしなければモジュール外部からそれを観測・識別する手段はありません。  
この観点からも、モジュール内部のパーティションによる構成は自由に行うことができます。

## 4 - 単一ヘッダファイル+複数ソースファイル


```cpp
/// mylib.h

namespace mylib {

  class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  void print_S(const S& s);
}
```

```cpp
/// mylib1.cpp

#include "mylib.h"

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }
}
```

```cpp
/// mylib2.cpp

#include <iostream>
#include "mylib.h"

namespace mylib {

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

例えばこんな風に、1つのヘッダに対して複数の実装ファイルが対応している場合の事です。  
ヘッダはそのままインターフェース単位に対応しますが、ソースファイルが複数あるときもそのまま複数書いても良いのでしょうか・・・？



```cpp
/// mylib.ixx

// mulibモジュールのインターフェース単位
export module mylib;

namespace mylib {

  // クラスのエクスポート、暗黙に全メンバがエクスポートされる
  export class S {
    int m_num = 0;
  public:

    S();
    S(int n);

    int get() const;
  };

  // フリー関数のエクスポート
  export void print_S(const S& s);
}
```

```cpp
/// mylib1.cpp

// mulibモジュールの実装パーティション1
module mylib:part1;

// インターフェースのインポート
import mylib;

namespace mylib {

  S::S() = default;
  S::S(int n) : m_num{n} {}

  inline int S::get() const {
    return this->m_num;
  }
}
```

```cpp
/// mylib2.cpp

module; // グローバルモジュールフラグメント

// #includeはグローバルモジュールフラグメント内で行う
#include <iostream>

// mulibモジュールの実装パーティション2
module mylib:part2;

// インターフェースのインポート
import mylib;

namespace mylib {

  void print_S(const S& s) {
    std::cout << s.get() << std::endl;
  }
}
```

モジュール実装パーティションであることは、モジュール宣言においてモジュール名の後に`:パーティション名`を続けることで行います。同じモジュールに含めたい場合はモジュール名を同じにします。パーティション名は被らないようにしましょう（ここでは`part1`とかいう名前にしましたけど、もっとちゃんとした名前つけましょうね）。

実装単位とは異なり、実装パーティションはそのモジュールのインターフェースを暗黙にインポートしていないので、明示的にインポートする必要があります。

### 実装パーティションの別の用法

## 5 - 複数ヘッダファイル+複数ソースファイル
## 6 - ヘッダオンリー
## 7 - モジュールとヘッダファイルの同時提供
### ヘッダユニット
### エクスポートブロック

