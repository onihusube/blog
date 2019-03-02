# ［C++］ constexprなメモリの確保と解放のために（C++20）

※この内容はC++20から利用可能な情報であり、一部の変更がC++23以降に先延ばしになるなど、内容が変更される可能性があります。  
　また、constexprなアロケータを作る類の内容ではないです。

[前回の記事](https://onihusube.hatenablog.com/entry/2019/03/02/110927)の「STLコンテナのconstexpr化のために」という項に入りきらなかった[P0784](https://wg21.link/P0784)の内容をまとめたものです。

### constexprデストラクタ
C++17まではデストラクタにconstexprを付けることはおろか、リテラル型として振舞えるクラスにデストラクタを定義することができず、デストラクタのコンパイル時実行もできませんでした。  
STLコンテナは例外なくデストラクタがtrivialでない（定義してある）ので、STLコンテナをconstexpr対応させるためにもこの制限は撤廃されます。

デストラクタにconstexpr指定が可能になり、そのデストラクタはコンパイル時に実行可能になります。ただし、そのようなクラスは仮想基底を持っては（仮想継承しては）ならず、デストラクタの中身はconstexpr実行可能である必要があります。  
`= default`なデストラクタはメンバや基底クラスのデストラクタが全てconstexprであれば、暗黙的にconstexprとなります。  
また、trivialなデストラクタも暗黙的にconstexprです。これは主に既存の組み込み型が該当します。

#### リテラル型の要件変更
そして、この変更に伴ってリテラル型となるクラスの条件が変更となります。

これまでは（メンバ変数は全てリテラル型であることを前提として）、
constexprコンストラクタとtrivialなデストラクタを要求していましたが、constexprコンストラクタとconstexprデストラクタを持つこと、という要求に少し緩和されます。  
つまり、リテラル型のオブジェクトはコンパイル時に構築・破棄可能でなければなりません。

```cpp
//これまでの、リテラル型の例
struct literal17 {
  //constexprなコンストラクタが少なくとも一つ必要
  //かつ、メンバをすべてconstexprに初期化できなければならない
  constexpr literal17()
    m{}
    d{}
  {}

  //デストラクタは書けてもdefaultまで
  ~literal17() = default;

  //メンバは全てリテラル型
  int m;
  double d;
};

//これからの、リテラル型の例
struct literal20 {
  //constexprなコンストラクタが少なくとも一つ必要
  //かつ、メンバをすべてconstexprに初期化できなければならない
  constexpr literal20()
    m{}
    d{}
  {}

  //デストラクタを書ける
  constexpr ~literal20() {
      //しかしこの例では意味のある処理を書くのがムズカシイ・・・
      m = 0;
      d = 0;
  }

  //メンバは全てリテラル型
  int m;
  double d;
};
```

#### virtual constexpr destructor
すでにconstexprな仮想関数呼び出しは可能になっていますが、それはあくまで自動変数のリテラル型のアドレスをその基底クラスのポインタに移して呼び出すもので、デストラクタがvirtualである必要はないのでリテラル型の要件（デストラクタを書けない）に変更はありませんでした。  
しかし、constexprデストラクタの導入とそれに伴うリテラル型の要件変更、そしてconstexprなメモリアロケーションによってその前提は崩れます。

つまり、コンパイル時にnewによって確保されたオブジェクトが基底クラスのポインタからdeleteされたとき、実行時と同じようにデストラクタ呼び出しの問題が発生します。  
皆様ご存知のように、この解決策はデストラクタをvirtualにしておくことです。

virtualでconstexprなデストラクタは必要不可欠なため、書くことができるようになります。

```cpp
struct base {
  virtual int f() const = 0;
  //virtual constexprと書ける！
  virtual constexpr ~base() = default;
};

struct derived : base {
  constexpr int f() const {
    return 10;
  }
};

//この様なことが可能だったとして
constexpr base* d = new derived{};
//derived::~derived()がコンパイル時にも正しく呼ばれる！
delete base;
```

### constexprなnew式/delete式
STLコンテナをconstexpr対応させるとなると一番問題となるのが動的なメモリアロケーションです。これをconstexprの文脈で認めなければSTLコンテナはコンパイル時に利用できません。そこで、一定の制限の下でコンパイル時の動的メモリ確保が認められるようになります。

constexpr関数等をコンパイル時に実行する際、未定義動作が検出された場合にはコンパイル時実行不可能になります。そのため、コンパイラはそれを可能な限り検出しようとします。  
ところが、動的なメモリ確保につきものなのがvoidポインタから別のポインタへのキャストです。
```cpp
//operator new / operator delete のうちの一つ
void* operator new(std::size_t);
void  operator delete(void* ptr) noexcept;

//std::malloc / std::free
void* malloc(std::size_t size);
void  free(void* ptr);
```
通常メモリ確保に使われるこれらは、見てわかるように`void*`からのキャストが必要です。

ポインタのキャストという行為が容易に未定義動作を踏み得る（ strict aliasing rules）上にそれを検出しづらいこともあって、現在定数式でそれは許可されていません。そして、C++20でも許可されません。

しかしそれではコンパイル時にメモリ確保のしようがありません。しかし、C++には見た目上再解釈を必要としないメモリ確保を行う式があります。つまり、new/delete式です。

（new式（new expression）とnew演算子（operator new）の違いについて → [動的メモリ確保 - 江添亮の入門C++](https://ezoeryou.github.io/cpp-intro/#動的メモリ確保)）

new式は任意の型のメモリ領域の確保と構築、delete式は（new式で確保された）任意の型の破棄とそのメモリ領域の解放を行ってくれます。そして、これらの式の入力及び出力においてはなんらポインタの再解釈は行われません。

このnew/delete式であれば確実に不正なポインタの再解釈は行われない事が分かるため、これらの式に限ってconstexprでコンパイル時実行可能になります。

ただし、呼び出せるのグローバルなoperator newを利用するようなnew式のみです。クラススコープにoperator newのオーバーロードがある場合はグローバルスコープ解決を行う必要があるかと思われます（::new T()の形で呼び出し）。  
そうでないnew式の呼び出しは、コンパイル時には単に省略されます。この省略はC++14より許可されているnew式の最適化の一環として行われます。省略された場合、別の領域をあてがわれるか、別のnew式の確保したメモリを拡張して補われます。  
省略とはいっても何もなされなくなるわけではありません。

また、コンパイル時に割り当てたメモリはコンパイル時に確実にdeleteされるか、後述する`Non-transient allocation`の要求を満たす必要があります。そうでないnew式の呼び出しはコンパイル時実行不可となります。

delete式についても、コンパイル時に確保されたメモリを開放するもの以外はコンパイル時実行不可となります。

### `std::allocator<T>`とplacement new式
ところで、C++にはもう一つ見かけ上ポインタの再解釈をする事無く任意の型のメモリ領域を確保/解放する手段があります。それが、`std::allocator<T>`です。（ただし、`std::allocator_traits<std::allocator<T>>`も同様ですので、以下`std::allocator<T>`にまつわる話は暗黙的にそれを含みます。）

`std::allocator<T>`は殆どのSTLコンテナで使われているデフォルトのアロケータで、そのメンバ関数によってメモリの確保、解放を行うことができます。それも、その式の入力と出力に際してユーザー側から見てポインタの再解釈は行われません。
そこで、この`std::allocator<T>`及び`std::allocator_traits<std::allocator<T>>`によるメモリの確保もconstexprに行うことができるようになります。

それに伴って`std::allocator<T>`のすべてのメンバがconstexpr指定されます（とはいえ、allocate/deallocate以外のメンバ関数はちょうど削除されたので、残ったのは代入演算子とコンストラクタ、デストラクタくらいですが）。

new/delete式と同じように、`std::allocator<T>::allocate`で確保したメモリはコンパイル時に確実に解放されるか後述する`Non-transient allocation`の要求を満たす必要があり、  
`std::allocator<T>::deallocate`はコンパイル時実行に確保されたメモリの解放のみを行う必要があります。  
そうでない場合はコンパイル時実行不可となります。

※備考です

これらのことに関する記述を見る限り、コンパイル時のメモリ確保と解放に関して、new/deleteとallocate/deallocateは必ずしもペアになっている必要はないようです。  
つまり、newで確保したメモリを`std::allocator<T>::deallocate`することや、`std::allocator<T>::allocate`したメモリをdeleteすることができるようです。

#### `std::construct_at`と`std::destroy_at`
詳しい人はご存知かもしれませんが、`std::allocator<T>`はnew/delete式とは違ってメモリの解放しか行いません。オブジェクトの構築・破棄を行ってくれないのです。

`std::allocator<T>::allocate`で確保したメモリを利用するにはplaccement newが、`std::allocator<T>::deallocate`でメモリの解放を行う前にはpseudo-destructor call（T型のオブジェクトaに対して a.~T()のような形のデストラクタ呼び出し）が必要になります。

placement new式はポインタの受け入れに伴って再解釈が発生します。また、両方とも定数式では現在許可されておらず、C++20でも許可されません。

これを解決するために、既存の`std::destroy_at`とそれの対となる `std::construct_at`を追加し、それらにconstexprを付加したうえで新たな役割を与えます。

```cpp
//それぞれの宣言

template<class T, class... Args>
constexpr T* construct_at(T* location, Args&&... args);

template< class T >
constexpr void destroy_at(T* p);
```

`std::construct_at`はその呼び出しが、`return ::new (location) T(std::forward<Args>(args)...);`という式と同じ効果を持つように  
`std::destroy_at`はその呼び出しがp->~T()と同じ効果を持つように  
それぞれ変更されます（正確には`std::destroy_at`は効果が変わってません）。そしてそれらはコンパイル時実行可能です。

そして現在、placement new及びpseudo-destructor callを使用している`std::allocator_traits<std::allocator<T>>`のconstruct/destroyの効果をこれらを使って定義しなおします。

これで何が変わるんじゃいという感じですが、placement new及びpseudo-destructor callの呼び出しを避け、`std::construct_at`と`std::destroy_at`をコンパイラに特別扱いしてもらう事で、それぞれの問題を解決しています。そしてついでにこれらはconstexpr関数です。  
「同じ効果を持つ」という所がキモです。

このなんとも納得のいかない（コンパイラの）努力によって、`std::allocator<T>`を用いてコンパイル時にメモリの確保と解放をする事の障害が取り除かれました。

ちなみに、類似の`std::destroy`、`std::destroy_n`、及びRangeの追加に伴ってstd::range名前空間に追加される同名の関数（`std::construct_at`も含む）にも同じ変更が適用されます。

### Non-transient allocation（）とNon-transient allocation

### Non-transient allocation
Non-transient allocationとは、コンパイル時に動的に確保されたメモリのうち、その開放もコンパイル時になされたもののことを言います。

ただし、

これはほとんど問題ありません。

### 参考文献
- [P0784R2 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r2.html)
- [P0784R3 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r3.html)
- [P0784R4 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p0784r4.html)
- [P0784R5 : More constexpr containers](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0784r5.html)


[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190302_cpp20_constexpr_allocate.md)