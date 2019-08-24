# ［C++］ constexprなメモリの確保と解放のために（C++20）

※この内容はC++20から利用可能予定の情報であり、内容が変更される可能性があります。また、constexprなアロケータを作る類の内容ではないです。

[前回の記事](https://onihusube.hatenablog.com/entry/2019/03/02/110927)の「コンパイル時メモリアロケーション」の所に入りきらなかった[P0784](https://wg21.link/P0784)の内容をまとめたものです。

[:contents]

### constexprデストラクタ
C++17まではデストラクタにconstexprを付けることはおろか、リテラル型として振舞えるクラスにデストラクタを定義することができず、デストラクタのコンパイル時実行もできませんでした。  
標準コンテナは例外なくデストラクタがtrivialでない（定義してある）ので、標準コンテナをconstexpr対応させるためにもこの制限は撤廃されます。

C++20より、デストラクタにconstexpr指定が可能になり、そのデストラクタはコンパイル時に実行可能になります。ただし、そのようなクラスは仮想基底を持っては（仮想継承しては）ならず、デストラクタの中身は定数式で実行可能である必要があります。

`= default;`なデストラクタやtrivialなデストラクタは、メンバや基底クラスのデストラクタが全てconstexprであれば、暗黙的にconstexprとなります。

#### リテラル型の要件変更
そして、この変更に伴ってリテラル型となるクラスの条件が変更となります。

C++17までは（メンバ変数および基底型は全てリテラル型であることを前提として）、
constexprコンストラクタとtrivialなデストラクタを要求していました。  
C++20からは、constexprコンストラクタとconstexprデストラクタを持つこと、という要求に少し緩和されます。  
つまり、リテラル型のオブジェクトはコンパイル時に構築・破棄可能である必要があります。

```cpp
//C++17でのリテラル型の例
struct literal17 {
  //constexprなコンストラクタが少なくとも一つ必要
  //かつ、そこからメンバをすべて定数式で初期化できなければならない
  constexpr literal17()
    : m{}
    , d{}
  {}

  //デストラクタは書けてもdefaultまで
  ~literal17() = default;

  //メンバは全てリテラル型
  int m;
  double d;
};

//C++20でのリテラル型の例
struct literal20 {
  //constexprなコンストラクタが少なくとも一つ必要
  //かつ、そこからメンバをすべて定数式で初期化できなければならない
  constexpr literal20()
    : m{}
    , d{}
    , str{"constexpr string"}
  {}

  //constexprであればデストラクタを書ける
  constexpr ~literal20() {
      //しかしこの例では意味のある処理を書くのがムズカシイ・・・
      m = 0;
      d = 0;
      str.clear();
  }

  //もちろんこう書いてもok
  //~literal20() = default;

  //メンバは全てリテラル型
  int m;
  double d;
  std::string str;  //!?
};
```

`std::string`はこれから説明する変更に伴って全メンバ`constexpr`指定されるようになるので、リテラル型として扱うことができるようになります。

#### virtual constexpr destructor
すでにconstexprな仮想関数呼び出しは可能になっていますが、それはあくまでリテラル型自動変数のアドレスをその基底クラスのポインタ/参照に移して呼び出すもので、デストラクタがvirtualである必要はありませんでした。  
しかし、constexprデストラクタの導入とそれに伴うリテラル型の要件変更、そしてconstexprなメモリアロケーションによってその前提は崩れます。

つまり、コンパイル時にnewによって確保されたオブジェクトが基底クラスのポインタからdeleteされたとき、実行時と同じようにデストラクタ呼び出しの問題が発生します。  
皆様ご存知のように、この解決策はデストラクタをvirtualにしておくことです。

virtualでconstexprなデストラクタは（この後の変更のためにも）必要不可欠なため、許可されます。

```cpp
struct base {
  virtual int f() const = 0;

  //virtual constexprと書ける！
  virtual constexpr ~base() = default;
};

struct derived : base {
  constexpr int f() const override {
    return 10;
  }
};


constexpr int new_sample() {
  //この様なことが可能だったとして
  base* d = new derived{};

  int n = d->f();

  delete_func(d);

  return n;
}

constexpr void delete_func(base* ptr) {
  //derived::~derived()がコンパイル時にも正しく呼ばれる！
  delete ptr;
}

int main() {
  constexpr n = new_sample(); //定数式で実行
}
```

### constexprなnew式/delete式
標準コンテナをconstexpr対応させるとなると一番問題となるのが動的なメモリアロケーションです。これを定数式で認めなければ標準コンテナはコンパイル時に利用できません。そこで、一定の制限の下でコンパイル時の動的メモリ確保が認められるようになります。

constexpr関数等をコンパイル時に実行する際、未定義動作が検出された場合にはコンパイル時実行不可能
になります。そのため、コンパイラはそれを可能な限り検出しようとします。  
ところが、動的なメモリ確保につきものなのがvoidポインタから別のポインタへのキャストです。
```cpp
//operator new / operator delete のうちの一つ
void* operator new(std::size_t);
void  operator delete(void* ptr) noexcept;

//std::malloc / std::free
void* malloc(std::size_t size);
void  free(void* ptr);
```
通常メモリ確保に使われるこれらは、見てわかるように`void*`への/からのキャストが必要です。

ポインタのキャストという行為が容易に未定義動作を踏み得る（strict aliasing rulesなど）上にそれを検出しづらいこともあって、現在定数式でそれは許可されていません。そして、C++20でも許可されません。  
しかし、C++には見た目上ポインタのキャストを必要とせずにメモリ確保と解放を担う式があります。つまり、`new`/`delete`式です。

（new式（new expression）とnew演算子（operator new）の違いについて → [動的メモリ確保 - 江添亮の入門C++](https://ezoeryou.github.io/cpp-intro/#動的メモリ確保)）

new式は任意の型のメモリ領域の確保と構築、delete式は（new式で確保された）任意の型の破棄とそのメモリ領域の解放を行ってくれます。そして、これらの式の入力及び出力においてはなんらポインタの再解釈は行われません。

このnew/delete式であれば確実に不正なポインタの再解釈は行われない事が分かるため、これらの式に限ってconstexprでコンパイル時実行可能になります。

ただし、呼び出せるのグローバルな`operator new`を利用するようなnew式のみで、そうでないnew式の呼び出しはコンパイル時には常に省略されます（クラススコープの`operator new`オーバーロードがある場合など）。  
この省略はC++14より許可されているnew式の最適化の一環として行われます。省略された場合、別の領域をあてがわれるか別のnew式の確保したメモリを拡張して補われます。  
省略とはいっても何もなされなくなるわけではありません。

また、コンパイル時に割り当てたメモリはコンパイル時に確実にdeleteされる必要があり、そうなっていないnew式の呼び出しはコンパイル時実行不可となります。

delete式についても、コンパイル時にnew式で確保されたメモリを開放するもの以外はコンパイル時実行不可となります。

```cpp
struct base {
  virtual bool f() const = 0;
  
  virtual constexpr ~base() = default;
};

struct derived : base {
  constexpr bool f() const override {
    return false;
  }
};

constexpr bool allocate_test1() {
  base* d = new derived{};
  auto b = d->f();
  delete d;

  return b;
}

constexpr bool allocate_test2() {
  base* d = new derived{};
  auto b = d->f();
  //現実にもよくあるdelete忘れをする
  //delete d;

  return b;
}

constexpr bool b1 = allocate_test1();  //ok
constexpr bool b2 = allocate_test2();  //compile error!
```

delete忘れるとコンパイルエラー！誰もが望んだことが可能になります。

### `std::allocator<T>`、`std::allocator_traits`
ところで、C++にはもう一つポインタの危険な再解釈を必要とせずに任意の型のメモリ領域を確保/解放する手段があります。それが、`std::allocator<T>`と`std::allocator_traits<std::allocator<T>>`です。

`std::allocator<T>`は殆どの標準コンテナで使われているデフォルトのアロケータで、そのメンバ関数によってメモリの確保、解放を行うことができます。それも、その式の入力と出力に際してユーザー側から見てポインタの再解釈は行われません。
そこで、この`std::allocator<T>`及び`std::allocator_traits`によるメモリの確保と解放もconstexprに行うことができるようになります。

それに伴って`std::allocator<T>`及び`std::allocator_traits`のすべてのメンバがconstexpr指定されます（とはいえ、`std::allocator<T>`の`allocate()/deallocate()`以外のメンバ関数はちょうど削除されたので、残ったのは代入演算子とコンストラクタ、デストラクタくらいですが）。

`std::allocator<T>`の`allocate()/deallocate()`は実際には定数式で呼び出し可能ではない`new/delete`演算子を呼び出してしまうのですが、言語機能として特別扱いすることでconstexprに呼び出しができるようになります。

new/delete式と同じように、コンパイル時に`std::allocator<T>::allocate()`で確保したメモリはコンパイル時に`std::allocator<T>::deallocate()`によって確実に解放される必要があり、`std::allocator<T>::deallocate()`はコンパイル時に`std::allocator<T>::allocate()`によって確保されたメモリの解放のみを行う必要があります。  
そうでない場合はコンパイル時実行不可となります。

少し注意点ですが、`new`式で確保したメモリを`std::allocator<T>::deallocate()`で解放する、`std::allocator<T>::allocate()`で確保したメモリを`delete`式で解放する、等といったことは定数式ではできません。コンパイルエラーです。

#### `std::construct_at`と`std::destroy_at`
詳しい人はご存知かもしれませんが、`std::allocator<T>`は`new/delete`式とは違ってメモリの確保と解放しか行いません。オブジェクトの構築・破棄を行ってくれないのです。

`std::allocator<T>::allocate()`で確保したメモリを利用するにはplaccement newが、`std::allocator<T>::deallocate()`でメモリの解放を行う前にはpseudo-destructor call（T型のオブジェクトaに対して `a.~T()`のような形のデストラクタ呼び出し）もしくは`std::destroy_at()`の呼び出しが必要になります。

placement new式はvoidポインタの受け入れに伴って再解釈が発生します。また、両方とも定数式では現在許可されておらず、C++20でも許可されません。  
`std::destroy_at()`もconstexpr関数ではなく定数式で実行できません。

これを解決するために、既存の`std::destroy_at()`の対となる `std::construct_at()`を追加し、それらにconstexprを付加します。

```cpp
//C++20からのそれぞれの宣言
namespace std {
  template<class T, class... Args>
  constexpr T* construct_at(T* location, Args&&... args);

  template<class T>
  constexpr void destroy_at(T* location);
}
```

`std::construct_at()`はその呼び出しが、`return ::new (location) T(std::forward<Args>(args)...);`という式（つまりplacement new）と同じ効果を持つように定義されます。  
`std::destroy_at()`はその呼び出しが`location->~T()`（つまりpseudo-destructor call）と同じ効果を持つと定義されており、特に変更はありません。
そして、両方ともconstexprが付加されコンパイル時実行可能になります。

そして現在、placement new及びpseudo-destructor callを使用している`std::allocator_traits`の`construct()/destroy()`両関数の効果をこれらを使って定義しなおします（`std::allocator<T>`は`std::allocator_traits`を通して使われることを前提とするため、構築・破棄に関わるこれらの関数を持ちません）。

これで何が変わるんじゃいという感じですが、placement new及びpseudo-destructor callの呼び出しを避け、`std::construct_at`と`std::destroy_at`をコンパイラに特別扱いしてもらって定数式で実行してもらうことで、それぞれの問題を解決しています。「同じ効果を持つ」という所がキモです。

このような機能実現方法のことをコンパイラーマジックと呼んだりして、C++11以降いくつかの機能の実現において利用されています。

この涙なしには語れない（コンパイラの）努力によって、`std::allocator<T>`を用いてコンパイル時にメモリの確保と解放をする事の障害が取り除かれました。

ちなみに、類似の`std::destroy()`、`std::destroy_n()`、及びRangeの追加に伴って`std::range`名前空間に追加される同名の関数も同様にされ、定数式で実行できます（`std::construct_at()`関連も同様）。

瑣末な注意点ですが、定数式での`std::construct_at()`/`std::destroy_at()`の呼び出し時の第一引数`T*`は`std::allocator<T>::allocate()`によって確保された領域を指すポインタでなければなりません（当然、new式で確保されたものであってもダメ）。  
また、それぞれの関数内で呼び出される`T`のコンストラクタおよびデストラクタが定数式で実行可能でなければconstexpr実行不可となります、これは`new/delete`式でも同様です。

```cpp
struct base {
  virtual int f() const = 0;
  
  virtual constexpr ~base() = default;
};

struct derived : base {
  constexpr bool f() const override {
    return false;
  }
};

constexpr bool allocate_test1() {
  std::allocator<derived> alloc{};
  //メモリ確保と構築
  derived* d = alloc.allocate(1);
  base* b = std::construct_at(d);  // b = new(d) derived{};と等価

  auto r = b->f();

  //オブジェクト破棄とメモリ解放
  std::destroy_at(b);  // b->~base();と等価
  alloc.deallocate(d, 1);

  return r;
}

constexpr bool allocate_test2() {
  std::allocator<derived> alloc{};
  //メモリ確保と構築
  derived* d = alloc.allocate(1);
  base* b = std::construct_at(d);  // b = new(d) derived{};と等価

  auto r = d->f();

  //忘れる
  //std::destroy_at(b);
  //alloc.deallocate(d, 1);

  return r;
}

constexpr bool b1 = allocate_test1();  //ok
constexpr bool b2 = allocate_test2();  //compile error!
```

`std::allocator<T>`と`std::construct_at()`/`std::destroy_at()`の組み合わせで、プログラマから見た扱いはnew/delete式とほぼ同じになるわけです。

また、`std::allocator_traits`の確保と解放・構築と破棄に関わるメンバが全て同様にconstexpr関数として定数式で実行可能になっているので、メモリ確保周りに関して標準コンテナは追加の作業無しでconstexpr対応をすることができます（他の部分で考慮が必要ではあります）。  
C++20では、`std::vector`と`std::string`がこれらの変更によってconstexpr対応を果たします。

これらの多大なる努力によってコンパイル時メモリ確保に関する障害はほぼ取り除かれ、全人類の夢であったコンパイル時動的メモリ確保が可能になります。

### コンパイル時確保メモリの解放タイミング

#### Transient allocation（一時的な割り当て）
Transient allocationとは、コンパイル時に動的に確保されたメモリのうち、その開放もコンパイル時になされたもののことを言います。  
そのようなメモリは実行時に参照されず、できません。

これはほとんど問題ないでしょう。

#### Non-transient allocation（非一時的な割り当て）

C++20における最終的な仕様では、Non-transient allocationは認められないことになりました（P0784R6で削除されました）。従って、コンパイル時に確保したメモリは確実にコンパイル時に解放されなければなりません。

#### Non-transient allocationに関する以前の仕様

※以下の記述は、以前の仕様を記したものです。参考に残しておきます・・・・

Non-transient allocationはその名の通り、コンパイル時に確保されたメモリ領域のうち、コンパイル時には解放されない物の事です。  
コンパイル時に確保したメモリ領域を実行時に参照したいことがある事からこの様な場合分けがなされています。

そのようなメモリ確保を許可する場合、その領域を実行時にどう扱うのかが問題となります。つまり、実行時に改めてメモリを確保しなおすのかどうかということです。C++のゼロオーバーヘッド原則的にも実行時に確保しなおすのはちょっと・・・、という感じでしょう。

そこで、クラス型内部で確保されるメモリについてのみ特別な条件を課すことでこれを可能にします。その条件とは、あるリテラル型`T`について

- `T`は非トリビアルconstexprデストラクタを持つ
- そのデストラクタはコンパイル時実行可能
- そのデストラクタ内で、`T`の初期化時に確保されたメモリ領域（Non-transient allocation）を解放する

そして、これらの条件を満たしていれば、そのNon-transient allocationなメモリ領域は実行時に静的ストレージへ昇格されます。

```cpp
template<typename T>
struct sample {
  std::allocator<T> m_alloc;
  T* m_p;
  size_t m_size;

  template<size_t N>
  constexpr sample(T(&p)[N])
    : m_alloc{}
    , m_p{m_alloc.allocate(N)}
    , m_size{N}
  {
    for(size_t i = 0; i < N; ++i) {
      std::construct_at(m_p + i, p[i]);
    }
  }

  constexpr ~sample() {
    for(size_t i = 0; i < N; ++i) {
      std::destroy_at(m_p + i);
    }
    m_alloc.deallocate(m_p, m_size);
  }
}

constexpr sample<char> str{"Hello."};
//実行時には、strは"Hello"を保持する静的配列を参照するようになる
```
このようなsampleクラスが上の条件を満たしています。

コンパイル時にメモリを確保してそれを実行時まで残すことを話していたのに、なぜか開放している・・・

どういうことかというと、この場合のsmple::~sample()は必要なものですが呼ばれないものです。Non-transient allocationとなる場合に、このデストラクタは見かけ上コンパイル時に確保したメモリを全て解放しているように見せるためにあります。  
そして、この様に一旦解放した様に扱ったメモリ領域を最終的には静的ストレージへ移行することで実行時にも参照可能になります（つまりこの場合、const char*な文字列と同じ扱いになる）。実行時にはそのクラスのオブジェクト共々定数となるので、コンパイル時に評価完了した場合は実行時にデストラクタが呼ばれることはありません。

もちろんこの要件を満たしていればTransient allocationとして扱う事にも何ら問題はありません（constexpr関数のローカル変数として利用されるなど）。そして実行時に扱う事にも問題がない事が分かるでしょう。

まどろっこしいですが、この様な規則を導入することで前項の確保・解放関数のコンパイル時実行条件の修正や、コンパイル時動的メモリ→実行時動的メモリの変換、などのさらに煩わしいことを考えなくて済むようになります。

##### `std::mark_immutable_if_constexpr()`

ここまでで、コンパイル時に解放され切らないメモリについての扱いは分かりました。しかしそこにはまだ問題があります。

先のsampleクラスがNon-transient allocationとなる場合にはそのデストラクタは見た目だけのもので、それは呼ばれることはありません。そしてそのコンパイル時動的メモリ領域は静的記憶域へ昇格されます。  
では、そのメモリの内容はどの時点で決まるのでしょうか？

先のsampleクラスはポインタをパブリックに公開しているのでコンパイル時のどの時点でもそれを書き換えることができます。さてその場合、呼び出し時点の値を実行時に持ち越せばいいのでしょうか？それともコンパイル時の全ての評価を待たねばならないのでしょうか？

利用するプログラマ視点から見るとどうでもいい話かもしれませんが、コンパイラ様から見ると大変です。えっ？コンパイル時に動的確保した領域すべてを監視し続けるんですか！？という感じです。

そのようなコンパイラ様をお助けするために、`std::mark_immutable_if_constexpr()`という関数が`<new>`に追加されます。  
その役割はある時点以降はそのメモリ領域は不変であることをコンパイラに通知することです。
```cpp
//宣言
template<class T>
constexpr void mark_immutable_if_constexpr(T* p);
```

`std::mark_immutable_if_constexpr()`でマークされた領域は不変であるとして扱われます。おそらく実行時に残る値は`std::mark_immutable_if_constexpr()`が呼び出された時点の値となるでしょう。その後で変更しても何も起きないかと思われます（そして、それについての指示が見当たらないことから未定義動作でしょう）。ちなみに実行時に（の文脈で）呼び出しても何の効果もありません。

先のsampleクラスは以下のように修正されます。

```cpp
template<typename T>
struct sample {
  std::allocator<T> m_alloc;
  T* m_p;
  size_t m_size;

  template<size_t N>
  constexpr sample(T(&p)[N])
    : m_alloc{}
    , m_p{m_alloc.allocate(N)}
    , m_size{N}
  {
    for(size_t i = 0; i < N; ++i) {
      std::construct_at(m_p + i, p[i]);
    }
    //ここ以降は確保した領域は不変
    std::mark_immutable_if_constexpr(m_p);
  }

  constexpr ~sample() {
    for(size_t i = 0; i < N; ++i) {
      std::destroy_at(m_p + i);
    }
    m_alloc.deallocate(m_p, m_size);
  }
}

constexpr sample<char> str{"Hello."};
//strは"Hello"を保持する静的配列を参照するようになる
```
この様にしておけば、`str`はその後どう弄繰り回されても実行時から見たら`Hello`を保持するようになります。

なるはずでした・・・

### 参考文献
- [P0784R2 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r2.html)
- [P0784R3 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r3.html)
- [P0784R4 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r4.html)
- [P0784R5 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0784r5.html)
- [P0784R6 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0784r6.html)
- [P0784R7 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0784r7.html)


[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190302_cpp20_constexpr_allocate.md)