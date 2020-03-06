# ［C++］ メンバ関数のCV/参照修飾

### メンバ関数の修飾

メンバ関数にはCV修飾と参照修飾を行えます。CV修飾は呼び出すオブジェクトが`const/volatile`であるときに優先して選択されるようになり、参照修飾は呼び出すオブジェクトの状態が左辺値/右辺値であるときに優先して選択されるようになります。そして、この二つは重複して指定することができます。つまり、以下のような組み合わせが可能です。

```cpp
struct X {
  int f() &       // *thisが非constな左辺値である場合に呼び出される
  { return 1; }

  int f() const & // *thisがconstな左辺値である場合に呼び出される
  { return 2; }

  int f() &&      // *thisが右辺値である場合に呼び出される
  { return 3; }

  int f() const &&      // *thisがconstな右辺値である場合に呼び出される
  { return 4; }

  int f() volatile &    // *thisがvolatileな左辺値である場合に呼び出される
  { return 5; }

  int f() const volatile &  // *thisがconst volatileな左辺値である場合に呼び出される
  { return 6; }

  int f() volatile &&       // *thisがvolatileな右辺値である場合に呼び出される
  { return 7; }

  int f() const volatile && // *thisがconst volatileな右辺値である場合に呼び出される
  { return 8; }
};
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gscUq5xoWbBJgKwi)

まあこんだけ全部書いてあれば想定通りに呼び出されます。しかし、実際は書いたとしても`const`と参照修飾あるいはその組み合わせくらいでしょう。すると、書かなかった種類のものは書いてあるもののどれかにマッチすればそれによって呼び出されるはずです。

例えば次のように、関数を左辺値からのみ呼び出したいが`const`である場合は処理を分けたいこともあるでしょう。この場合は、右辺値オブジェクトから`f()`を呼び出そうとするとコンパイルエラーになることが期待されるはず・・・

```cpp
struct X {
  int f() &       // *thisが非constな左辺値である場合に呼び出される
  { return 1; }

  int f() const & // *thisがconstな左辺値である場合に呼び出される
  { return 2; }
};

int main() {
  X x;
  const X cx;

  std::cout << x.f() << std::endl;   // 1
  std::cout << cx.f() << std::endl;  // 2
  std::cout << X().f() << std::endl; // 2 !?
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/JCOtYHTg6J4aiGWk)

なんと、右辺値からの呼び出しがコンパイルエラーになりません。どうやら`const &`な関数に引っかかっているようです。

`const auto&`が右辺値を束縛できるのは理解できますが、この挙動は一見非自明でイミフです・・・

#### 暗黙の引数`this`

C++のクラスメンバ関数はユーザーが指定した引数リストの一番先頭で、暗黙の引数として`this`ポインタを受け取っています。CV修飾はこの暗黙の引数の型に対して適用されます。

```cpp
struct X {
  int f() const
  { return 0; }

  int f(int arg1, int arg2) volatile
  { return -1; }
};

X x;
x.f();

//↑この様なクラスXとメンバ関数呼び出しは、実質的に次↓の様なコードの様に扱われている

struct X {};

int f(const X* this)
{ return 0; }

int f(volatile X* this, int arg1, int arg2)
{ return -1; }

X x;
f(&x);
```

この辺りのことはコンパイラがよしなにしていることなので、C++ヲタク以外は気にしなくても良いことです。

これを知ると多分もうわかると思いますが、参照修飾もこれと同じことが起こっています。そして上記のことはより正確にはポインタではなく参照によって行われます。

```cpp
struct X {
  int f() const
  { return 0; }

  int f(int arg1, int arg2) volatile
  { return -1; }

  int f() &
  { return 1; }

  int f() const &
  { return 2; }
};

X x;
x.f();

//↑この様なクラスXとメンバ関数呼び出しは、実質的に次↓の様なコードの様に扱われている

struct X {};

int f(const X& this)
{ return 0; }

int f(volatile X& this, int arg1, int arg2)
{ return -1; }

int f(X& this)
{ return 1; }

int f(const X& this) // 実はconst修飾とconst&修飾は同じ意味を持つので両方書くとコンパイルエラー
{ return 2; }

X x;
f(x);
```

なお、これらの事はオーバーロード解決時に行われる事なので、ユーザーが触れる部分では`this`はポインタです。

詳細には、関数呼び出しに伴うオーバーロード解決時にメンバ関数の暗黙の第一引数の型は、その関数の参照修飾と`CV`修飾によって次の様に決められます（ここでの対象となるクラス型を`T`とします）。

- メンバ関数に参照修飾がない場合
- メンバ関数が左辺値修飾(`&`)されている場合
    - `CV T&`
- メンバ関数が右辺値修飾（`&&`）されている場合
    - `CV T&&`

ここで先ほどの不可解なコードを振り返ってみると、もう自明になっている事でしょう。

```cpp
struct X {
  int f() &       // *thisが非constな左辺値である場合に呼び出される
  { return 1; }

  int f() const & // *thisがconstな左辺値である場合に呼び出される
  { return 2; }
};

//f()の宣言だけ書いてみると
int f(X& this);
int f(const X& this);

f(X{}); // const &なメンバ関数が呼ばれる
```

`const auto&`が右辺値を束縛できる様に、あるいはムーブコンストラクタがない場合は右辺値に対してコピーコンストラクタが呼ばれる様に、`this`が右辺値であり`&&`修飾されたメンバ関数がない場合には`const &`（あるいは`const`）修飾のメンバ関数がベストマッチしてしまうわけです。

C++は奥が深いですね・・・

### 防止策？

とはいえ、メンバ関数の`const`修飾の意図からするとこの事はやはり不自然であり、`const`オブジェクトに対して呼んで良くても右辺値に対しては呼んでほしくない関数はあるでしょう。そんな場合には、`&&`修飾された関数に対して`delete`指定をしてやれば意図通りになります。

```cpp
struct X {
  int f() &       // *thisが非constな左辺値である場合に呼び出される
  { return 1; }

  int f() const & // *thisがconstな左辺値である場合に呼び出される
  { return 2; }

  int f() && = delete;  // *thisが右辺値なら呼び出し禁止！
};

int main() {
  X x;
  const X cx;

  std::cout << x.f() << std::endl;   // 1
  std::cout << cx.f() << std::endl;  // 2
  std::cout << X().f() << std::endl; // コンパイルエラー
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/gDJToaTE9gG41T0k)

正直冗長だと思いますが多分こうするのがベストでしょう・・・・


### CV修飾と参照修飾と暗黙の引数の型

オブジェクト型を`T`とするとメンバ関数の修飾によって決まる、オーバーロード解決時に考慮される暗黙の第一引数（`this`）の型は以下のようになります。

|CV修飾＼参照修飾|なし|`&`|`&&`|
|:---|:---|:---|:---|
|なし|`T&`|`T&`|`T&&`|
|`const`|`const T&`|`const T&`|`const T&&`|
|`volatile`|`volatile T&`|`volatile T&`|`volatile T&&`|
|`const volatile`|`const volatile T&`|`const volatile T&`|`const volatile T&&`|

CV修飾に関してはほぼ想定通りになると思われますが、参照修飾をするときは少し気にする必要があるかもしれません。

### 参考文献

- [メンバ関数の左辺値／右辺値修飾 - cpprefjp](https://cpprefjp.github.io/lang/cpp11/ref_qualifier_for_this.html)
- [非静的メンバ関数 - cppreference](https://ja.cppreference.com/w/cpp/language/member_functions)
- [12.4.1 Candidate functions and argument lists [over.match.funcs]](http://eel.is/c++draft/over.match.funcs)

### 謝辞

この記事の8割は以下の方々によるご指摘によって成り立っています。

- [@tetzromさん](https://twitter.com/tetzrom/status/1235160659899207681)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20200306_constref_memfun.md)