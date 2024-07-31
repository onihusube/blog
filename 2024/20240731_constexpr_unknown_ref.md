# ［C++］定数式における未知の参照の利用の許可

C++23から、定数式における、非定数式な参照の読み取り（特にコピー）が定数式において許可されるようになります。

[:contents]

### 定数式における非定数式の参照

定数式における非定数式の参照という一見意味の分からないものは、生配列に対する`std::size()`の使用で容易に出会うことができます

```cpp
void check(int const (&param)[3]) {
  int local[] = {1, 2, 3};

  constexpr auto s0 = std::size(local); // ok
  constexpr auto s1 = std::size(param); // ng
}
```
https://wandbox.org/permlink/gaYeDLdSKZtFrENY

この`s0, s1`はともに`constexpr`ローカル変数であり、その初期化式（ここでは`std::size()`の呼び出し）は定数式でなければなりません。しかし、ここでは変数`local`は定数式として扱われるのに対して、変数`param`は定数式として扱われておらず、それによってエラーになっています。

これは定数式で禁止されている事項に引っかかっているためにこの差が出ています

[N4861 7.7 Constant expressions [expr.const]/5.12](https://timsong-cpp.github.io/cppwp/n4861/expr.const#5.12)より

> - 参照に先行して初期化されていて次のどちらかに該当するものを除いた、変数の参照または参照型データメンバである*id-expression*
>     - 定数式で使用可能である
>     - その式の評価の中で*lifetime*が開始している

[expr.const]/5では定数式で現れてはいけない式が列挙されています。これはそのうちの一つです。

`loacl`および`param`という名前を参照する式は*id-expression*であり、`local`は参照に先行していて初期化されていて定数式で使用可能である参照である（ただし参照先の読み取りはできない）のに対して、`parama`は初期化されていないためこの事項に即抵触しています。

他にも、値ではなくその型にしか関心が無い場合に変数の型の取得のために関数テンプレートの引数推論を利用することはよくあると思います。このような場合にも、同様の問題に遭遇する可能性があります

```cpp
template <typename T, typename U>
constexpr bool is_type(U &&) {
  return std::is_same_v<T, std::decay_t<U>>;
}
```

これは例えば次のように使用することを意図しています

```cpp
auto visitor = [](auto&& v) {
  // vは非定数式の参照
  if constexpr(is_type<Alternative1>(v))  // ng
  {
    ...
  }
  else if constexpr(is_type<Alternative2>(v)) // ng
  {
    ...
  }
};
```

この例の`v`は定数式ではないので、`if constexpr`の条件式（当然定数式でなければならない）の中で他の関数に渡すことはできません。この場合、参照`v`そのものには関心が無いのが分かりやすいでしょう。

ラムダ式を`constexpr`にしてもこれは解決できません。

また別のところでは、`this`引数として出会うこともできます

```cpp
struct S {
  int buffer[2048];

  void foo() {
    constexpr size_t N = std::size(buffer); // ng

    ...
  }
};
```
https://wandbox.org/permlink/slJqqHKLw6bJmBqn

このエラーは今度は、`std::size(buffer)`の引数において`this`が定数式で使用できないと怒られています。ここの`buffer`はメンバ変数なので、その参照には`this`が必要ですが、このコンテキスト（`N`の初期化式）での`this`は定数式ではないため定数式で使用できずに怒られています。

この場合、`foo()`を`constexpr`にしても変わりません。

また、冒頭のコードを`std::array`と`.size()`メンバ関数呼び出しに置き換えると、`this`による同様のエラーに出会えます

```cpp
void check(const std::array<int, 3>& param) {
  std::array<int, 3> local = {1, 2, 3};

  constexpr auto s0 = local.size(); // ok
  constexpr auto s1 = param.size(); // ng
}
```
https://wandbox.org/permlink/XLH8LNnIUZ4X8gaN

この`this`の使用でエラーの起きている2例はいずれも、`this`を介して（間接参照して）アクセスしようとしているわけではありません。

`this`とよく似た場合で、あるクラスのオブジェクトを通してそのクラスの静的メンバにアクセスする場合もこの問題に出会うことができるかもしれません

```cpp
struct S {
  static constexpr bool f() {
    return true;
  }

  static constexpr int constant = 1;
};

void call(S& s) {
  // sは非定数式の参照
  constexpr bool b = s.f();     // ng
  constexpr int N = s.constant; // ng
}
```
https://wandbox.org/permlink/48AsQDbo7v3COWOw

この場合、`s.`は構文上の略記でしかなく、`s`の具体的な値に興味がありません。にもかかわらず、`s`が非定数式であることによって`s`を介した定数式の呼び出しがエラーになっています。

### やりたいこととそうじゃないこと

これが例えば次のような例であれば、これができないことは仕方のないことだと理解できます

```cpp
constexpr int read(auto& array) {
  return array[0];
}

void check(int const (&param)[3]) {
  int local[] = {1, 2, 3};

  constexpr auto s0 = read(local); // ng
  constexpr auto s1 = read(param); // ng
}
```

しかし先ほど一通り見ていた例はいずれも、このようなことがやりたいわけではありません。なんなら、参照（`this`）の参照先どころか参照そのものに対してすら全く興味がありません。

一連のコード例で重要なのは参照の型情報であって、参照そのものはどうでもいいのです。

しかしいずれの例でも、定数式の実行に際して非定数式である参照値の読み取り（別の関数への受け渡し、コピー）が発生しており、これによって全体の式の定数式としての実行が妨げられてしまっています。ここでの読み取りとは参照そのものの値に対してであって、参照先にアクセスしようとするものではありません。

### 定数式における参照そのものの読み取りの許可

このような問題の原因は、定数式の実行においては未定義動作が許可されないことによって、定数式で使用されるすべての参照は有効なものでなくてはならないためです。関数の中からでは関数引数の参照の有効性は判定できないためそのような参照の有効性は未知であり、最初の方で引用したルールはそれをあらかじめ弾いておくためのものでした。

従って、この問題は参照（言語参照、`this`、および一般のポインタ）でのみ起こります。ほぼ同等のコードであっても、それが値であれば起こりません。

```cpp
void check(int const (&param)[3]) {
  int local[] = {1, 2, 3};

  constexpr auto s0 = std::size(local); // ok、参照のコピー渡し
  constexpr auto s1 = std::size(param); // ng、未知の参照のコピー渡し
}

void check_arr_val(std::array<int, 3> const param) {
  std::array<int, 3> local = {1, 2, 3};

  constexpr auto s3 = std::size(local); // ok、値の参照渡し
  constexpr auto s4 = std::size(param); // ok、値の参照渡し
}
```
https://wandbox.org/permlink/JCc3rgIcRXSc8UO7

もちろん値の場合でもこのように渡した先の関数内でその具体的な値にアクセスすることはできません。しかし、今回問題となっているケースでは参照先には全く関心が無いため、参照もこれと同じ扱いになってもよさそうです。

この問題はP2280によって補足され、P2280R4はC++23に対して採択されました。

P2280R4では、ここまで示したような定数式における未知の参照及び`this`ポインタそのもの読み取り（コピー、not間接参照）を許可します。これによりここまでいくつか示してきたような、参照そのものに興味はないが未知の参照がコピーされることによって定数実行できなかったコードがすべて定数式で実行可能になります。

```cpp
void check(int const (&param)[3]) {
  int local[] = {1, 2, 3};

  constexpr auto s0 = std::size(local); // ok
  constexpr auto s1 = std::size(param); // ng -> ok
}
```
```cpp
auto visitor = [](auto&& v) {
  if constexpr(is_type<Alternative1>(v))  // ng -> ok
  {
    ...
  }
  else if constexpr(is_type<Alternative2>(v)) // ng -> ok
  {
    ...
  }
};
```
```cpp
struct S {
  int buffer[2048];

  void foo(){
    constexpr size_t N = std::size(buffer); // ng -> ok

    ...
  }
};
```
```cpp
void check(const std::array<int, 3>& param) {
  std::array<int, 3> local = {1, 2, 3};

  constexpr auto s0 = local.size(); // ok
  constexpr auto s1 = param.size(); // ng -> ok
}
```
```cpp
struct S {
  static constexpr bool f() {
    return true;
  }

  static constexpr int constant = 1;
};

void call(S& s) {
  // sは非定数式の参照
  constexpr bool b = s.f();     // ng -> ok
  constexpr int N = s.constant; // ng -> ok
}
```

ただし、この緩和の対象は参照と`this`ポインタのみで、より一般のポインタに対しては適用されません。

```cpp
void f(std::array<int, 3>& r, std::array<int, 4>* p) {
  static_assert(r.size() == 3);    // #1、ok（この提案による）
  static_assert(p->size() == 4);   // #2、ng
  static_assert(p[3].size() == 4); // #3、ng
  static_assert(&r == &r);         // #4、ng
}
```

ポインタは参照と比べるとできることが多いため、定数式における未知のポインタに対して何の操作が適用可能で何がそうではないのかを規定しなければならず、作業が複雑になることからP2280R4では当初の目標である未知の参照と`this`だけに的を絞って緩和されました。

### 欠陥報告

P2280R4はDR（*Defect Report*）として以前のすべてのバージョン（この場合`constexpr`が初めて導入されたC++11まで）に対してさかのぼって適用されます。したがって、P2280R4を実装したコンパイラではC++23モードだけでなく、C++11やC++20モードなどでもこの問題が解決されます。

この記事を書いている時点では、GCC14だけがこれを実装しています。

### `requires`式の引数

この未知の参照概念、基本的に関数引数で遭遇することが多いと思われるのですが、なんと`requires`式の引数の参照さえもその対象です。

```cpp
template<typename T>
concept to_char_narrowing_check = requires(T&& t) {
  { std::int8_t{ t.size() } };  // -128 ~ +127 の範囲内はtrue
};

static_assert(to_char_narrowing_check<std::array<int, 1>>);
static_assert(to_char_narrowing_check<std::array<int, 127>>);
static_assert(to_char_narrowing_check<std::array<int, 128>> == false);
```
GCC14: https://wandbox.org/permlink/ikcs2twJfdfumqa7
clang15: https://wandbox.org/permlink/dRmTPwTNeGMMrs0e

この`to_char_narrowing_check`コンセプトは、`std::int8_t{ t.size() }`という式の有効性をチェックしています。引数型がすべて`std::array`であるとすると、その`.size()`の戻り値型は`std::size_t`なので常に縮小変換となり、`{}`初期化では縮小変換が許可されないことから常にコンパイルエラーになります（P2280R4以前は）。

ただし、このような縮小変換は定数式で行われた場合にのみ、変換元の値が変換先の型で表現可能であれば許可されます。

ただ前述のように、P2280R4以前は`std::array::size()`は`this`ポインタのコピーが必要になり、それが定数式ではないのでエラーになっていました。P2280R4以前の世界では、この例の上2つの`static_assert`が満たされることはありません（clang15の例）。しかし、P2280R4以降ではこの例の上2つの`static_assert`は満たされるようになります（GCC14の例）。

何が起きているかというと、`requires`式内部の`std::int8_t{ t.size() }`の式の妥当性チェックの際に、定数式で縮小変換が可能かどうかがチェックされており、P2280R4の緩和によってそれを妨げるものが無くなったことで、`t.size()`の値が取得されてその値がチェックされるようになっていいます。

ただしここでは、`array`のオブジェクト（`t`の参照先）は具体的に使用されておらず、`t.size()`の値は`t`の型情報から取得されています。

#### `std::declval()`

P2280R4の緩和はC++17以前の世界にももたらされます。その世界で、`requires`式の引数のような役割を担っていたのは`std::declval()`でした。残念なことに`std::declval()`は定数式で呼べないため、その返す参照はP2280R4の緩和対象ではありません。そのため、SFINAEの世界では先程の`to_char_narrowing_check`と同等の制約を表現でき・・・ないこともありません。

要は何とかして、`std::declval()`を使用していたところを関数引数から取ってくるように書き換えればいいわけです。

```cpp
template <typename T>
auto to_char_narrowing_check_helper(T&& t)
  -> decltype(std::int8_t{ t.size() });   // 先程のrequires式の例と同等のチェックはここで行われる

template<typename T, typename = void>
constexpr bool to_char_narrowing_check_v = false;

template<typename T>
constexpr bool to_char_narrowing_check_v<
  T,
  std::void_t<decltype(to_char_narrowing_check_helper(std::declval<T&>()))> // std::declval()を使用して、ヘルパ関数を呼ぶ（呼んではいない）
> = true;

static_assert(to_char_narrowing_check_v<std::array<int, 1>>);
static_assert(to_char_narrowing_check_v<std::array<int, 127>>);
static_assert(to_char_narrowing_check_v<std::array<int, 128>> == false);
```
GCC14: https://wandbox.org/permlink/doHxvy8q1Mgw9C5g
clang15: https://wandbox.org/permlink/0tqFtsGEJSMF620m

かなり複雑な実装ですが、GCC14の実行結果を見れば、SFINAEの制約においても縮小変換が定数式でチェックされていることが分かります。

`std::void_t`を利用した検出テクニックについては説明を割愛します。

従来のSFINAEなら、この`to_char_narrowing_check_helper()`のような余分な関数は必要なく、`void_t`の中で直接`std::void_t<decltype(std::uint8_t{ std::declval<T&>().size() })>`のようにしてしまえば十分でした。ただ、P2280R4の緩和を考えると、チェックしたい式に直接`std::declval()`が現れるのは良いこととは言えません（前述のように`declval()`の呼び出しは常に定数式ではないため）。

そこで、`std::declval()`を使用して`decltype()`内で`T`の参照を取得するものの、それを別の関数（`to_char_narrowing_check_helper()`）の引数に渡すことで参照の出どころをロンダリングします。呼び出された関数内では、その引数の参照は未知の参照として出所に関わらず使用できる（参照先を見に行かない限り）ので、あとはそちらのSFINAEの文脈で対象の式をチェックするようにするわけです。このようにすると、従来のSFINAEの文脈でもP2280R4の緩和の恩恵にあずかることができます。


ここでは例として`std::array`の`size()`を使っていたわけですが、実際にはそれに対してこういう事をする需要というのはほぼ皆無でしょう。より実用的なのは、`std::integral_constant`のような定数値クラスに対してです。

すでに、`std::variant`の初期化において`std::integral_constant`のような型の値からの変換時にこのようにP2280R4を考慮して縮小変換を定数式で検査するようにする提案（P3146）が提案されています。

```cpp
using IC = std::integral_constant<int, 42>;

IC ic;
std::variant<float> v = ic; // C++23でもすべての実装でエラー
                            // P3146では値に応じて初期化できるようにすることを提案
```

この際に問題となったのがまさに、`std::variant`の制約の実装がSFINAEによって行われていることで、ここで説明していることはP3146R1でより詳細に解説されています。特に、SFINAEでもP2280R4の恩恵にあずかれるようにするテクニックは私が思いついたものではなく、この提案に例として載っているものをより簡易に直しただけです。

### 参考文献

- [P2280R4 Using unknown references in constant expressions](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2022/p2280r4.html)
    - [P2280R0 Using unknown references in constant expressions - WG21月次提案文書を眺める（2021年01月）](https://onihusube.hatenablog.com/entry/2021/02/11/153333#P2280R0-Using-unknown-references-in-constant-expressions)
- [P3146R1 Clarifying `std::variant` converting construction](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/p3146r1.html)
    - [P3146R0 Clarifying `std::variant` converting construction - WG21月次提案文書を眺める（2024年02月）](https://onihusube.hatenablog.com/entry/2024/05/18/235613#P3146R0-Clarifying-stdvariant-converting-construction)
- [c++ - クラスの非静的メンバーの配列の要素数を定数式として取得したい - スタック・オーバーフロー](https://ja.stackoverflow.com/questions/93436/%E3%82%AF%E3%83%A9%E3%82%B9%E3%81%AE%E9%9D%9E%E9%9D%99%E7%9A%84%E3%83%A1%E3%83%B3%E3%83%90%E3%83%BC%E3%81%AE%E9%85%8D%E5%88%97%E3%81%AE%E8%A6%81%E7%B4%A0%E6%95%B0%E3%82%92%E5%AE%9A%E6%95%B0%E5%BC%8F%E3%81%A8%E3%81%97%E3%81%A6%E5%8F%96%E5%BE%97%E3%81%97%E3%81%9F%E3%81%84)
