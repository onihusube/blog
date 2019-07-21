# ［C++］集成体の要件とその変遷
集成体（aggregate）とは配列と幾つかの条件を満たしたクラス（union含む）の事で、集成体初期化（aggregate initialization）を行えるような型のことです。一様初期化構文の導入によってその他の初期化との見た目の差異が無くなりあまり意識されなくなったかもしれませんが、集成体初期化という初期化方式および集成体という分類がなくなったわけではありません。

自前のクラスを集成体にして集成体初期化を行えるようにすることのメリットは、データメンバの初期化と参照のための煩わしい各種関数の定義をしなくて済むことです。これにより取り扱いやすくなり、コードとしての見た目が見やすくなります。 
デメリットは、カプセル化を完全に破壊していることです。なので、単にデータをまとめて可搬にするためだけの型に使用することが多いかと思います。

実はクラスが集成体になるための条件はC++11以降毎回少しづつ変化しているので、それをバージョン毎に見てみます。  
以下、staticメンバは関わってこないのでstaticメンバに関しては触れません。また、配列は特に変化がないのでクラスの条件のみを対象にしています。

### C++98/03
- ユーザー宣言のコンストラクタを持たない
- privateやprotectedなメンバ変数を持たない
- 仮想関数をメンバに持たない
- 継承していない

おそらくC言語由来の基本要件。これを満たしておけばC++14以降のどのバージョンでも集成体となれますので集成体となる要件が知りたい場合はこれでお話が終わります（C++11はここにもう一つ制約が加わります）。

### C++11
- ユーザー定義のコンストラクタを持たない
  - defaultやdelete指定された宣言はあってもok
- privateやprotectedなメンバ変数を持たない
- 仮想関数をメンバに持たない
- 継承していない
- メンバ変数が初期化されていない

これらを満たせばC++11での集成体となれます（同時にC++14での要件も満たします）。また、メンバ変数が集成体である必要はありませんし、仮想関数でなければ関数がいくらあっても構いません。

集成体初期化は一様初期化のようなコンストラクタ呼び出しとは異なり、値を直接初期化するような構文です。そのため、全メンバはpublicであり、ユーザー定義コンストラクタがあってはいけません。

メンバ変数が初期化されていないとは、C++11から可能になったデフォルトメンバ初期化子による初期化がされていてはいけないという事です。

```cpp
//集成体の例
struct aggregate {
  aggregate() = default;
  aggregate(aggregate&&) = delete;

  int a;
  int b;
  std::string str;
};

//全メンバを明示的に初期化
aggregate a1 = {10, 20, "string"};
//全メンバをデフォルト初期化（各メンバmiについて mi = {}、のような空の初期化リストからのコピー初期化を行う）
aggregate a2 = {};

//集成体でない例
struct not_aggregate {
  not_aggregate()
    : a{} 
    , b{}
  {}
  
private:
  int a;
  int b;
};

struct default_initialized {
  int a = 10;
};

struct has_vfuuc {
  int n;
  
  virtual int f() {
    return n;
  }
};

//base自体は集成体
struct base {
  int a;
};

struct derived : base {};

//complie error 集成体初期化不可
not_aggregate a = {10, 20};
default_initialized d = {30};
has_vfuuc h = {10};
derived d = {10};
```

VisualStudio 2015同梱のcl.exeは部分的にC++17まで対応していますが、集成体の要件に関してはこのC++11止まりです。

### C++14
- ユーザー定義のコンストラクタを持たない
  - defaultやdelete指定された宣言はあってもok
- privateやprotectedなメンバ変数を持たない
- 仮想関数をメンバに持たない
- 継承していない

メンバ変数の初期化が解禁されました。これは疑問の余地のない当然の変更といえるでしょう。

```cpp
//集成体の例
struct aggregate {
  aggregate() = default;
  aggregate(aggregate&&) = delete;

  int a = 0;
  int b;
  std::string str = "string";
};

aggregate ag = {10, 20};

//集成体でない例
struct not_aggregate {
  not_aggregate()
    : a{} 
    , b{}
  {}
  
private:
  int a;
  int b;
};

struct has_vfuuc {
  int n;
  
  virtual int f() {
    return n;
  }
};

//base自体は集成体
struct base {
  int a;
};

struct derived : base {};

//complie error 集成体初期化不可
not_aggregate a = {10, 20};
has_vfuuc h = {10};
derived d = {10};
```

### C++17
- ユーザー定義のコンストラクタ、explictコンストラクタ宣言、継承されたコンストラクタを持たない
  - explictでなければ、defaultやdelete指定された宣言はあってもok
- privateやprotectedなメンバ変数を持たない
- 仮想関数をメンバに持たない
- virtual, private, protectedな基底クラスを持たない

public継承に限って継承が許可されました。ただし、基底クラスのコンストラクタを継承してはいけません。しかし、基底クラスが集成体でなければならないわけではありません。  
単にpublic継承しただけでは、基底クラスのすべてのコンストラクタは隠蔽されています（言うなれば、コンストラクタは継承していません）。基底クラスのコンストラクタを使用可能にするにはusing宣言が必要です。

``` cpp
struct Base {
    Base() : m{10}
    {}

    Base(int n) : m{n}
    {}

    int m;
}

struct Derived : Base {
    //このusingによって基底クラスの全てのコンストラクタは継承される
    using Base::Base;
}

//call Base::Base(int) not aggregate initialization, d.m == 30
Derived d{30};
```
継承されたコンストラクタを持たないとは、この様なusing宣言を行っていないことを意味します。

もう一つの変更点、explictなコンストラクタの宣言があってはならないというのはどういうことでしょうか？ユーザー定義コンストラクタはそもそも書けないので同じことではないか？  
しかし、explicit default/deleteなコンストラクタの宣言は可能なのです。そしてその結果、集成体でありながら集成体初期化できないという意味のないことが起こります。そのため、explicitコンストラクタ宣言をもつ場合は集成体となれないとされたわけです。

``` cpp
struct explicit_ctor {
  explicit explicit_ctor() = delete;
  
  int a;
  int b;
};

//compile error! before C++14 and after C++17
explicit_ctor e = {10, 20};
```

以下コード例
```cpp
struct base {
  base(int n) : a{n} {}

private:
  int a;
};

//集成体の例
struct aggregate : base {
  aggregate() = default;
  aggregate(aggregate&&) = delete;

  int a = 0;
  int b;
  std::string str = "string";
};

aggregate ag = {10, 20, 30, "string."};

//集成体でない例
struct not_aggregate {
  not_aggregate()
    : a{} 
    , b{}
  {}
  
private:
  int a;
  int b;
};

struct has_vfuuc {
  int n;
  
  virtual int f() {
    return n;
  }
};

//complie error 集成体初期化不可
not_aggregate a = {10, 20};
has_vfuuc h = {10};
```

### C++20
※C++20はまだ発効前なのでこれはあくまで予定です。

- ユーザー宣言のコンストラクタ、継承されたコンストラクタを持たない
- privateやprotectedなメンバ変数を持たない
- 仮想関数をメンバに持たない
- virtual, private, protectedな基底クラスを持たない

defaultやdelete指定も含めてあらゆるコンストラクタの宣言が禁止されました。C++03までの要件+継承可能、になった感じです。この変更はなぜなされたのでしょうか？

#### C++20での要件変更の理由

##### 1. 意図しない初期化
以下のようなケースが可能になってしまうことです。

```cpp
struct delete_defctor {
  delete_defctor() = delete;
};

//compile error!
delete_defctor x;
//ok. aggregate initialization
delete_defctor x{};
```
デフォルトコンストラクト不可能にしたいのに、集成体の要件を満たしているので集成体初期化が可能になっており、結果としてデフォルトコンストラクト可能であるかのように振舞っています。  
これはprivateにしても変わりません。
```cpp
struct delete_defctor {
private:
  delete_defctor() = delete;
};

//compile error!
delete_defctor x;
//ok. aggregate initialization
delete_defctor x{};
```
簡単な回避策としてはとりあえずexplicitを付ければ期待通りになりますが、それを理解できる人がどれほどいるのでしょうか・・・？

また、上のコードにメンバがある場合にまた面白いことになります。
```cpp
struct delete_init_int {
  delete_defctor() = delete;
  delete_defctor(int) = delete;

  int n = 10;
};

//compile error!
delete_init_int x(3);
//ok. aggregate initialization
delete_init_int x{3};
```
intで初期化してほしくないが集成体初期化によりコンストラクタを完全にスルー出来てしまっています。  
これも解決はexplicitつけるとか、privateにしろよ、とかですが、このような些末な仕様の詳細をほとんどのC++プログラマは知らず、知ることもなく、また知る必要がないようにすべき。というのが理由の一つです。

##### 2. = defaultの位置による違い
```cpp
struct aggregate {
  aggregate() = default;

  int n;
};

struct not_aggregate {
  not_aggregate();

  int n;
};

not_aggregate::not_aggregate() = default;

aggregate x{10};
//compile error! can't aggregate initialization
not_aggregate y{10};
```
コンストラクタの宣言と定義を分割すると、集成体ではなくなります。同じ意味のコードであるはずなのにdefaultの位置で型の意味が全く変わってしまっているのは思わぬバグの原因になりえます。

##### 3. C++20より可能になる通常の（）による集成体初期化のため

[https://onihusube.hatenablog.com/entry/2019/04/06/123202:embed:cite]

C++20より集成体初期化を普通の丸かっこで行えるようなります。この環境の下では、明らかに上の1の問題がさらに深刻になります。

#### 要件変更によるメリット
このように些末な問題ではありますが、ただでさえ複雑なC++における初期化についてこれらの問題はその複雑度を上げてしまっています（C++17で禁止されたexplicitコンストラクタの宣言という特殊ケースも含めて）。この複雑性はユーザー宣言コンストラクタを持つ型は集成体ではない、と決めることで取り除くことができるためそのようになりました。

この変更によって、ユーザー宣言コンストラクタがある場合にはコンパイラが暗黙に生成するデフォルトコンストラクタは無効になる、というルールに集成体初期化（が提供する仮想的なコンストラクタ）も含まれることになり初期化に関するセマンティクスの一貫性が増します。  
クラスの初期化に関して複雑なルールを覚えることなく、クラスに宣言されたコンストラクタがあれば必ずそれらのうちの一つを通してクラスは初期化される、という単純なルールを覚えればよくなります。

そして、この変更は意図せず集成体となってしまっていたバグを取り除きます。以下のコードのように、C++03まではコンストラクタのdefaultなど無かったため、デフォルトコンストラクタを取り合えず書いておけば集成体にはなりませんでした。
```cpp
struct X {
  X() {}
  // some data members...
};
```
しかしC++11に対応する過程でそのようなコードが=defaultによって書き直された場合、それは集成体になってしまい意図しない初期化が可能になります。これは実際にLLVM/clangのコードで確認されたことのようです。

こうしてみればバラ色の提案にも見えますが問題がないわけではありません。意図をもって各コンストラクタをdeleteしているようなC++11以降のコードは完全に壊れます（この変更はC++03以前とは互換性がある）。  
また現在の所、集成体のムーブ/コピーコンストラクタを明示的に制御する方法は提供されていません。つまりは、集成体がムーブ/コピー可能であるかはそのデータメンバによって暗黙的に変化します。これはC++20正式採用までに変化する可能性はありますが・・・

以下C++20におけるコード例
```cpp
struct base {
  base(int n) : a{n} {}

private:
  int a;
};

//集成体の例
struct aggregate : base {
  int a = 0;
  int b;
  std::string str = "string";
};

aggregate ag = {10, 20, 30, "string."};

//集成体でない例
struct not_aggregate {
private:
  int a;
  int b;
};

struct has_ctor {
  has_ctor() = default;

  int n;
};

struct has_vfuuc {
  int n;
  
  virtual int f() {
    return n;
  }
};

//complie error 集成体初期化不可
not_aggregate a = {10, 20};
has_ctor c = {10};
has_vfuuc h = {10};
```

### 参考文献
- [Aggregates - N3337](https://timsong-cpp.github.io/cppwp/n3337/dcl.init.aggr)
- [Aggregates - N4140](https://timsong-cpp.github.io/cppwp/n4140/dcl.init.aggr)
- [Aggregates - N4659](https://timsong-cpp.github.io/cppwp/n4659/dcl.init.aggr)
- [P0398R0: Core issue 1518: Explicit default constructors and copy-list-initialization ](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0398r0.html)
- [p1008r1 Prohibit aggregate types with user-declared constructors](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2018/p1008r1.pdf)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190219_aggregate.md)