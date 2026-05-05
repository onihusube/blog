# ［C++］`std::start_lifetime_as()`によるtype punning

C++ type punning環境最前線における最新のtype punning手法の紹介です。

[:contents]

### `std::start_lifetime_as()`

`std::start_lifetime_as()`はC++23で追加された関数で、指定されたストレージでimplicit-lifetime typeな型のオブジェクトの生存期間を明示的に開始させるための関数です。

```cpp
#include <memory>

// 独自アロケータのようなもの
namespace my_alloc {
  alignas(alignof(void*)) std::byte storage[1000];

  template<typename T>
  auto allocate_memory() -> T* {
    // 適当実装です
    return static_cast<T*>(static_cast<void*>(storage));
  }
}

// Xはimplicit-lifetime type
struct X { int a, b; };

static_assert(std::is_implicit_lifetime_v<X>);  // ✅

int main() {
  X* memory = my_alloc::allocate_memory<X>();

  // Xはimplicit-lifetime typeではあるものの、生存期間が開始されていない（allocate_memory()がユーザー定義関数であるため）
  X* ub_ptr1 = reinterpret_cast<X*>(memory);  
  ub_ptr1->a = 1; // ☠ UB
  ub_ptr1->b = 2; // ☠ UB

  // start_lifetime_as()を通すことで生存期間を開始する
  X* valid_ptr = std::start_lifetime_as<X>(memory);
  valid_ptr->a = 1; // ok
  valid_ptr->b = 2; // ok
}
```

- [Wandbox](https://wandbox.org/permlink/YzyhCXTrtsaUD4sd)

このオブジェクトの生存期間の開始はコンストラクタ呼び出しを伴うものではなく、論理的なものです。`std::start_lifetime_as()`は実質的には何もしない関数です。

### `std::start_lifetime_as()`の効果についての規定

`std::start_lifetime_as()`がオブジェクトの生存期間を開始する仕組みは関数の効果（Effects）として次のように規定されています

> Implicitly creates objects ([intro.object]) within the denoted region consisting of an object a of type T whose address is p, and objects nested within a, as follows: The object representation of a is the contents of the storage prior to the call to start_lifetime_as. The value of each created object o of trivially copyable type ([basic.types.general]) U is determined in the same manner as for a call to bit_cast<U>(E) ([bit.cast]), where E is an lvalue of type U denoting o, except that the storage is not accessed. The value of any other created object is unspecified.

翻訳（Powered by PLAMO翻訳）

> 指定された領域内に、アドレスが `p` である型 `T` のオブジェクト `a` 、および `a` 内にネストされたオブジェクトを暗黙的に作成します。  
> `a` のオブジェクト表現は、`start_lifetime_as()` 関数呼び出し前のストレージの内容となります。  
> トリビアルコピー可能な型([basic.types.general]) `U` の作成された各オブジェクト `o` の値は、`bit_cast<U>(E)`（[bit.cast]）への呼び出し時と同様に決定されます。ここで、 `E` は評価結果が `o` となる型 `U` の左辺値式ですが、この場合（`p`の）ストレージにはアクセスしません。  
> その他の場合の作成されたオブジェクトの値は未規定です。

ここでの`p`と`T`は`std::start_lifetime_as<T>(p)`のように呼び出した時の引数のポインタと作成対象のオブジェクト型です。

implicit-lifetime typeが言語の仕組みとして特定の操作（`malloc()`や`memcpy`など）において暗黙的にオブジェクトが作成される場合は単にそのコンテキストで適切なオブジェクトが作成されるというだけでそれ以上の事はせず、特に作成されたオブジェクトの持つ値やオブジェクト表現についての保証は何もありません。

しかし、`std::start_lifetime_as()`はトリビアルコピー可能な型に関して言語の仕様よりも拡張された保証を持っています。つまり次の二文です

> `a` のオブジェクト表現は、`start_lifetime_as()` 関数呼び出し前のストレージの内容となります。

> トリビアルコピー可能な型([basic.types.general]) `U` の作成された各オブジェクト `o` の値は、`bit_cast<U>(E)`（[bit.cast]）への呼び出し時と同様に決定されます。

そして、その動作は`std::bit_cast`を参照する形で指定されています。

`std::bit_cast`の規定は様々なケースを考慮してさらに複雑に書かれていますのでここでは割愛します。基本的にはビットレベルの再解釈キャストが可能であるということを理解しておけばよいでしょう。

興味ある型はこちらを参照してください

- [[bit.cast]/4 - eel.is](https://eel.is/c++draft/bit.cast#4)

なお、オブジェクト表現というのは簡単に言えば型をバイト配列として読み出した際のビット列の事です。このビット列のうち、その型の値として有効であるビット列の事を値表現と呼びます。構造体のパディングはオブジェクト表現に含まれるものの値表現には含まれません。

### type punning

`T* vp = std::start_lifetime_as<T>(p)`においては、次のことが保証されています

- `*vp`のオブジェクトのオブジェクト表現は`p`の内容と一致する
- `T`がトリビアルコピー可能である場合、`*vp`のオブジェクトの値は`p`のビット列を再解釈して決定される

すなわち、`T`がトリビアルコピー可能な型であれば`std::start_lifetime_as`は合法的にtype punningが可能です。

```cpp
#include <stdfloat>
#include <cstring>
#include <memory>
#include <bit>
#include <array>

int main() {
  const std::float32_t f = 3.14f;
  alignas(alignof(std::int32_t)) std::byte storage[sizeof(std::int32_t)];  

  // オブジェクト表現のコピー
  std::memcpy(storage, &f, sizeof(std::int32_t));

  // std::int32_tの生存期間開始
  auto* p = std::start_lifetime_as<std::int32_t>(storage);

  // bit_cast()
  auto rv = std::bit_cast<std::int32_t>(f);

  std::println("start_lifetime_as: {}", *p);
  std::println("bit_cast         : {}", rv);
}
```
```
start_lifetime_as: 1078523331
bit_cast         : 1078523331
```

- [Wandbox](https://wandbox.org/permlink/g5iVFO2341BeJtef)

この`*p`の値が`std::bit_cast<std::int32_t>(f)`として再解釈キャストを行った場合と一致することが保証されます。

このことは`std::start_lifetime_as`する際の型`T`がimplicit-lifetime typeかつトリビアルコピー可能であれば保証されます。

#### 不定値やEV

`std::start_lifetime_as`によるtype punningの保証は`std::bit_cast`に委ねられているため、そちらの規定で未定義だとか不定値だとか言われている場合は同様に有効ではなくなります。

例えば`std::bit_cast`の規定では、ソースのオブジェクト表現を再解釈した結果がキャスト先の型の値表現と対応しない場合（ビットキャスト後のビット列がその型で有効なビット列ではない場合）には結果が未定義とされています。また、不定値を持つビットを`bit_cast`した結果が値表現のビットに含まれてしまう場合はその値も不定値となります。さらにはerroneous valueも伝播します。

パディングビットを再解釈しようとする例

```cpp
#include <stdfloat>
#include <cstring>
#include <memory>
#include <bit>
#include <array>

// パディングがある
struct X {
  std::int8_t b;
  std::int32_t n;
};

static_assert(std::is_implicit_lifetime_v<X>);      // ✅
static_assert(std::is_trivially_copyable_v<X>);     // ✅
static_assert(sizeof(X) == sizeof(std::float64_t)); // ✅

int main() {
  const X x{ .b = 0, .n = 0 };
  alignas(alignof(std::float64_t)) std::byte storage[sizeof(std::float64_t)];

  // オブジェクト表現のコピー
  std::memcpy(storage, &x, sizeof(std::float64_t));

  // std::float64_tの生存期間開始
  auto* p = std::start_lifetime_as<std::float64_t>(storage);
  
  // *pの値は不定値
  auto ub = *p; // ☠ UB
}
```

この例では`*p`を読み出すと不定値を読み出すことになり未定義動作になります。`std::float64_t`オブジェクトそのものは作成済みであるため、上書きすることは問題なくできます。

### 利点

基本的には`std::bit_cast`を使った方がほとんどの場合に良いでしょう。implicit-lifetime typeに限定されずに定数式で使用でき、手動`memcpy`ステップが無いので使いやすいなどがあります。

あえてこの方法の利点を挙げるなら、ビット再解釈のためにコピー的操作が不要であることがあります。

`std::bit_cast`は`T r = std::bit_cast<T>(src)`のように呼び出して`src`から`r`へビットコピーを行ったうえで`r`のオブジェクトの生存期間を開始するような動作をします。これは操作としてコピーを暗に含んでいます。

もしあるストレージにすでに所望のオブジェクト表現が存在していることが分かっていて、単にその領域をそのまま再解釈したい場合、`std::bit_cast`のコピー動作は不要であり、省きたいかもしれません。

その場合は、`std::start_lifetime_as`のこの方法が有効であるかもしれません

```cpp
#include <stdfloat>
#include <cstring>
#include <memory>
#include <bit>
#include <array>

int main() {
  {
    const std::float32_t f = 3.14f;

    // 暗にコピーを含む
    std::int32_t r = std::bit_cast<std::int32_t>(f);
  }
  {
    const std::float32_t f = 3.14f;

    std::destroy_at(&f);  // 多分不要

    // ストレージを再利用してstd::int32_tへ再解釈
    auto* p = std::start_lifetime_as<std::int32_t>(&f);
    
    std::int32_t v = *p; // ok

    std::destroy_at(&p);  // 多分不要
  }
}
```

とはいえ`std::bit_cast`の呼び出し程度は最適化で簡単に消せる気がするので、このことが本当に有用であるかはよく分かりません・・・


#### `std::start_lifetime_as_array()`

`std::start_lifetime_as_array()`は指定領域に指定サイズの配列型の生存期間を開始する関数で、その動作は要素ごとに`std::start_lifetime_as()`によって指定されているため、同様のことが可能になります。配列全体ではなく配列の各要素ごとにですが、配列の場合各要素間にパディングが無いためある型を別の型の配列として読み替えるということもできます。

```cpp
#include <stdfloat>
#include <cstring>
#include <memory>
#include <bit>
#include <span>

int main() {
  const std::float64_t f = 2.718;

  alignas(alignof(std::int16_t)) std::byte storage[sizeof(std::float64_t)];
  
  // オブジェクト表現のコピー
  std::memcpy(storage, &f, sizeof(std::float64_t));

  // std::int16_t[4]の生存期間開始
  auto* p = std::start_lifetime_as_array<std::int16_t>(storage, 4);

  std::println("{}" , std::span{p, 4});
}
```
```
[14680, -14156, -16778, 16389]
```

- [Wandbox](https://wandbox.org/permlink/LmXSTpw7as8AYAKf)

ちなみにこの場合、配列型を返却できないことにより`std::bit_cast`が素直には使用できないため、こちらも利点となりえるかもしれません。

```cpp
int main() {
  const double f = 2.718;

  auto rv1 = std::bit_cast<std::int16_t[4]>(f); // ng、一般的に関数は生配列を返せないことによるエラー

  auto rv2 = std::bit_cast<std::array<int16_t, 4>>(f);  // ok、std::arrayはreturnできる
}
```

### 参考文献

- [P3960R0 Define copy-constructibility-from-bytes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2026/p3960r0.html)
- [[obj.lifetime] - eel.is](https://eel.is/c++draft/obj.lifetime)
- [未初期化領域への暗黙的なオブジェクト構築 [P0593R6] - cpprefjp](https://cpprefjp.github.io/lang/cpp20/implicit_creation_of_objects_for_low-level_object_manipulation.html)