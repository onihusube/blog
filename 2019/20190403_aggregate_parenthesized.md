# ［C++］丸かっこによる集成体初期化

※この記事は[C++20を相談しながら調べる会 #1](https://cpp20survey.connpass.com/event/124051/)の成果です。

※内容はC++20正式策定までに変化する可能性があります。

集成体初期化（Aggregate Initilization）とは、配列か集成体（Aggregate）となる条件を満たしたクラスに対して行える特別な初期化方法の事です。

C++17まではこれは波かっこ（{}）の時にのみ使用することができ、丸かっこ（()）による初期化は常にその型のコンストラクタを呼び出していました。  
しかし、C++20からはその制限がなくなり丸かっこによる初期化時にも集成体初期化が考慮され、行われるようになります。

```cpp
struct agg {
  int a;
  double b;
};

agg a{10, 3.14};  //ok
agg b(10, 3.14);  //ok

agg c = {20, 2.72};  //ok
agg d = (20, 2.72);  //ng
```

丸かっこによる集成体初期化はなるべく波かっこによるものと同じように実行されます。一方で、今までの丸かっこによる初期化の持つ意味が変わらないようにもなっています。  
そのため、波かっこによる集成体初期化と少し異なる挙動をするところがあります。

### コンストラクタとの競合

集成体初期化と従来のコンストラクタ呼び出しが競合する場合はコンストラクタ呼び出しが優先されます。  
とはいえ、集成体にはコンストラクタを一切書けないので問題になるのはコピーやムーブが起こる時です。

```cpp
struct A;

struct C { 
  operator A();  //実装略
};

struct A {
  C c;
};

C c();

{
  A a(c);  //C::operator A()を呼び、その戻り値からaをムーブ（コピー）構築
  A b(a);  //aからbをコピー構築、A::cをaから初期化する事はしない
}

{
  A a{c};  //A::cをcからコピー初期化
  A b{a};  //A::cをaからコピー初期化（できないのでエラー）
}
```


### 縮小変換の許可 

縮小変換とは変換後の型が変換前の型の表現を受け止めきれないような型の変換です（double -> float, signed -> unsigned 等）。

波かっこによる初期化時は集成体初期化でなくても、縮小変換が禁止されていました。  
それは思わぬところで変換エラーを引き起こし、特にテンプレート関数の中では波かっこ初期化は非常に使いづらくなってしまっていました。

```cpp
template<typename T>
float to_float(T v) {
  return float{v};
  //こうするとok
  return float(v);
}

auto d = to_float(3.14);  //compile error!
auto e = to_float(3.14f); //ok.


constexpr char str[50]{};
constexpr auto begin = std::begin(str);
double pi_v = 3.1415926535897932384626433832795;

if (auto [end, err] = std::to_chars(begin, std::end(str), pi_v); err == std::errc{}) {
  std::cout << std::string_view{begin, end - begin};  //compile error!
  //こう書くとok
  //std::cout << std::string_view(begin, end - begin);
}

```
これらのエラーは波かっこ初期化時には縮小変換が禁止されていることから発生しています。

しかし、丸かっこによる集成体初期化においてはそのような制限はなく、あらゆる変換が考慮され実行されます。これは同じ丸かっこによる初期化で、コンストラクタ呼び出しと集成体初期化とで挙動が異なることがないようにするためです。

ただし、このような変換が許可されるのはクラス型の集成体初期化時のみで、配列に対する丸かっこ集成体初期化時は相変わらず禁止されます。配列は元々丸かっこ初期化を持っておらず、挙動が曖昧にはならないためです。

### 潜む罠

### この変更によるメリット

この様に

### 参考文献
- [P0960R3 : Allow initializing aggregates from a parenthesized list of values](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2019/p0960r3.html)