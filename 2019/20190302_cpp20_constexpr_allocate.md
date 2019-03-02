# ［C++］ constexprなメモリ確保、解放

### constexprデストラクタ
C++17まではデストラクタにconstexprを付けることはおろか、リテラル型として振舞えるクラスにデストラクタを定義することができず、デストラクタのコンパイル時実行もできませんでした。  
STLコンテナは例外なくデストラクタがtrivialでない（定義してある）ので、STLコンテナをconstexpr対応させるためにこの制限は撤廃されます。

デストラクタにconstexpr指定が可能になり、そのデストラクタはコンパイル時実行されます。ただし、そのようなクラスは仮想基底を持ってはならず、デストラクタの中身はconstexpr実行可能である必要があります。  
`= default`なデストラクタはメンバや基底クラスのデストラクタが全てconstexprであれば、暗黙的にconstexprとなります。  
また、trivialなデストラクタも暗黙的にconstexprです。これは主に既存の組み込み型が該当します。

ちなみに、仮想関数がconstexprになれるようになったのと同じくconstexpr virtual デストラクタも可能になります。

そして、この変更に伴ってリテラル型となるクラスの条件が変更となります。（メンバ変数は全てリテラル型であることを前提として）今まではconstexprコンストラクタとtrivialなデストラクタを要求していましたが、constexprコンストラクタとconstexprデストラクタを持つこと、という要求に少し緩和されます。  
つまり、リテラル型のオブジェクトはコンパイル時に構築・破棄可能でなければなりません。

### constexprなnew式とallocator
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
ポインタのキャストという行為が容易に未定義動作を踏み得る（ strict aliasing rules）上にそれを検出しづらいこともあって、現在定数式でそれは許可されていません。そして、C++20でも許可されません。

しかしそれではコンパイル時にメモリ確保のしようがありません。しかし、C++には再解釈を必要としないメモリ確保を行う式があります。つまり、new/delete式です。

（new式とoperator newの違いについて → [動的メモリ確保 - 江添亮の入門C++](https://ezoeryou.github.io/cpp-intro/#動的メモリ確保)）

new式は任意の型のメモリ領域の確保と構築、delete式は（new式で確保された）任意の型の破棄とそのメモリ領域の解放を行ってくれます。そして、これらの式の入力及び出力においてはなんらポインタの再解釈は行われません。

そこで、このnew/delete式がconstexprで許可されコンパイル時実行可能になります。

#### `std::allocator<T>`とplacement new式
ところで、C++にはもう一つ見かけ上ポインタの再解釈をする事無く任意の型のメモリ領域を確保/解放する手段があります。それが、`std::allocator<T>`です。

`std::allocator<T>`（もしくは`std::allocator_traits<std::allocator<T>>`）は殆どのSTLコンテナで使われているデフォルトのアロケータで、そのメンバ関数によってメモリの確保、解放を行うことができます。それも、その式の入力と出力に際してユーザー側から見てポインタの再解釈は行われません。
そこで、この`std::allocator<T>`及び`std::allocator_traits<std::allocator<T>>`によるメモリの確保もconstexprに行うことができるようになります。