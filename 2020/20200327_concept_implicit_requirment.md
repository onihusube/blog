# ［C++］コンセプトの無言のお願い事

[:contents]

### 等しさの保持（*equality preservation*）

ある式が等しい入力に対して等しい出力を返すとき、その式は **等しさを保持（*equality-preserving*）** しています。式とはわかりやすいところでは関数であり、演算子のことです。ある式を`f()`とすると`a == b`ならば`f(a) == f(b)`となり、かつ常にこれが成り立つ時、`f()`は等しさを保持する式ということです。

この場合の入力とは、その式に直接与えられた引数全てのことであり、1つの引数は1つの式のことです。正確には以下のものだけを含む一番大きな部分式のことです。

- id-expression（一次式）
- `std::move(), std::forward(), std::declval()`の呼び出し

例えば、`f(std::move(a), std::declval<T>(), c)`みたいなコードでは、まずこの全体が1つの式です。この式の部分式とは`std::move(a), a, std::declval<T>(), c`で、上記2つだけを含む最大の部分式=入力は、`std::move(a), std::declval<T>(), c`の3つです。  
別の例では、`a = std::move(b)`と言う式の入力は`a, std::move(b)`の2つです。

式は最終的に結果となる1つの値になるので、等しさを保持する式の入力（の式）というのはつまりある1つの引数値と言う事です。

そして、出力とは式の結果（上記の`f()`ならその戻り値）および、その式の実行によって変更された引数の集合です（変更されなかった引数は含まれない）。

等しさを保持する式の入力と出力はこれら以外にあってはいけません。

#### 安定（*stable*）

あるオブジェクトを入力（引数）にとるある式の2回の評価において、そのオブジェクトの明示的な変更が介在しない限り等しい出力が得られる時、その式は **安定（*stable*）** な式です。等しさを保持する式は安定でなければなりません。

つまり、等しさを保持し安定である式は内部や外部の状態に依存してはならず、直接の引数以外に対して副作用を持ってはならないと言う事です。

そして、標準ライブラリにおけるコンセプト定義内の全ての制約式は、特に注釈がない限り等しさを保持し安定でなければなりません。これは、そのコンセプトを満たそうとする場合にユーザーコードに対しても要求されます。

例外的に等しさを保持することを要求されないコンセプトには例えば[`std::invocable`](https://cpprefjp.github.io/reference/concepts/invocable.html)などがあります。

#### 定義域（*domain*）

等しさを保持する式はその入力となりうる全ての値について有効である必要はありません。例えば、整数に対する`a / b`と言う式は等しさを保持する式ですが、`b == 0`の時この式は有効ではありません。  
しかし、この様な入力を取り得たとしても、そのことはその式が等しさを保持することに影響を与えません。

ある等しさを保持する式の入力の全体から、この様な有効ではない入力を除いた集合をその式の **定義域（*domain*）** と呼びます。

この用語はコンセプトの意味論的な制約条件に出現することがあります（例えば、[std::
equality_comparable_with](https://cpprefjp.github.io/reference/concepts/equality_comparable.html)など）。
 

### 制約式の引数に対しての制約

標準ライブラリのコンセプト定義においては、ある`requires`式内の各制約式が引数に対して副作用を及ぼしても良いかどうか（引数を変更することが許されるか）をその`requires`式の引数（ローカルパラメータ）の`const`修飾によって表現しています。ローカルパラメータが`const`修飾されている場合はそのパラメータを引数に取る制約式は対応する引数を変更してはなりません。逆に、`const`修飾されていなければ変更しても構いません。

このことも、コンセプトを満たそうとすれば自然にユーザーコードに対して要求されることになります。とはいえ、`const`修飾されたローカルパラメータが渡ってくるところでその引数を変更しようとするのは、`const_cast`とか`mutable`とかなんかおかしなことをしない限りそれを破ることは無いでしょう・・・？

```cpp
template<typename T>
concept C1 = requires(T a, T b) {
  f(a, b);
  a + b;
  // このC1コンセプトを満たす型は、f(T, T)とoperator+(T, T)の呼び出しが可能である必要がある
  // そして、そのような型に対するf()とoperator+の実装は、2つの引数に対して副作用を及ぼしても（引き数を変更しても）良い
};

template<typename T>
concept C2 = requires(const T a, T b) {
  f(a, b);
  a + b;
  // このC2コンセプトを満たす型Tは、f(T, T)とoperator+(T, T)の呼び出しが可能である必要がある
  // そのようなTに対するf()とoperator+の実装は、その第一引数は変更してはならない（`const`修飾されたローカルパラメータ`a`が渡されている）
  // ただし、第二引数は`const`修飾のないローカルパラメータ`b`が渡されているので、変更しても良い
};
```

この様に決めた上で、コンセプトの型パラメータ`T`がCV修飾されていないオブジェクト型であり完全型と仮定すると、その定義内`requires`式ではそのローカルパラメータのCV/参照修飾から各ローカルパラメータの値カテゴリとCV修飾を確定することができます。
このようにCV修飾と値カテゴリを指定したローカルパラメータを利用すれば、各制約式が引数としてどのようなCV修飾でどの値カテゴリを受け取るべきなのか？という制約を表現することができます。

```cpp
// このTがCV修飾されていないオブジェクト型であり完全型と仮定すると
template<typename T>
concept C = requires(T a, T&& b, const T& c) {
  // aの型はCV無しのTであり、左辺値
  // bの型はTの参照型であり、右辺値
  // cの型はconst T&であり、左辺値
  // というように、CV修飾と値カテゴリを指定できる

  f(a);             // 式f()はTのconst無し左辺値を受け取れる必要がある
  g(std::move(b));  // 式g()はTのconst無し右辺値を受け取れる必要がある
  h(c);             // 式h()はTのconst左辺値参照を受け取れる必要がある
};
```

#### `requires`式と`requires`節

C++20コンセプトでは`requires`キーワードは、それを書く場所によって*requires-clause*（`requires`節）と*requires-expression*（`requires`式）のどちらかとして扱われます。

また、`requires`節内に`requires`式を書くこともできます。

```cpp
template<typename T>
concept C1 =
  requires { T{}; };  // requires式

template<typename T>
concept C2 = 
  requires(T a) {     // requires式
    ++a; 
  };

template<typename T>
  requires C1<T> // requires節
void f(T t)
  requires C2<T> // requires節
{
  /*関数本体*/
}

template<typename T>
  requires ( requires { T{}; } )          // requires節とその中のrequires式
void g(T t)
  requires ( requires(T a) { t += a; } )  // requires節とその中のrequires式
{
  /*関数本体*/
}
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/DNnd7gtamoUbe1Ss)

`requires`式は任意の型に対する制約条件を表現する制約式となり、`requires`節はテンプレートにおいてそのテンプレートパラメータに対する制約を指定するものです。

ローカルパラメータを取れるのは`requires`式だけなので、その`const`修飾による引数への副作用の制約表現のお話は`requires`式だけの話です。

### 暗黙的な式のバリエーション（*implicit expression variations*）

`requires`式ローカルパラメータの`const`修飾によって制約式が引数を変更しないことを表明する場合、その制約式には非`const`の左辺値、右辺値、および`const`右辺値を取る追加の形式が暗黙に要求されます。これら暗黙の追加形式のことを **暗黙的な式のバリエーション（*implicit expression variations*）** と呼びます。


```cpp
template<typename T>
concept C = requires(const T a, T b) {
  f(a, b);  // このf()は第一引数に対して暗黙的な式のバリエーションが要求される
};

// 明示的に書けば以下の様になる
template<typename T>
concept C = 
  requires(const T a, T b) { 
    f(a, b);
    f(std::move(a), b);
  } &&
  requires(T   a, T b) { f(a, b); } &&
  requires(T&& a, T b) { f(std::move(a), b); };
```

この様な`f()`は例えば次の様になります。

```cpp
// 例えばT = intとすると

// ok
f(int n, int m);         // コピー・ムーブによって上記バリエーションの全てを受けられる
f(const int& n, int m);  // const左辺値参照は上記バリエーションの全てを受けられる

// ng
f(int& n, int m);  // 非const左辺値だけしか受けられない
f(int&& n, int m); // 非const右辺値だけしか受けられない
```

ただし、これら追加のバリエーションが制約式として明示的に書かれていない場合、それをどこまで構文的にチェックするのかは実装依存となります、

`requires`式ではありませんがこの様な追加の暗黙のバリエーションを明示的に書いているものには、[`std::copyable`](https://cpprefjp.github.io/reference/concepts/copyable.html)や[`std::copy_constructible`](https://cpprefjp.github.io/reference/concepts/copy_constructible.html)などがあります。


### コンセプトのモデルとなるために

「等しさの保持（かつ安定）」「引数への副作用の制約」「暗黙的な式のバリエーション」、これらの標準ライブラリのコンセプトが暗黙的に要求する事は構文的な制約ではなく意味論的な制約です。つまり、コンパイル時にチェックされる（あるいはできる）ものではありません。違反していたとしてもコンパイルエラーにはならないでしょう・・・

あるコンセプト`C`について、型`T`が`C`の要求する構文的な制約（制約式）を全て満たしていて、上記3つの暗黙的な制約も全て満たしており、かつ`C`に追加で指定される意味論的な制約を全て満たしている時、型`T`はコンセプト`C`の **モデル（*model*）** であると言います。

型がコンセプトのモデルであることは、標準ライブラリのテンプレート（クラス・関数）の事前条件（*Post Condition*）において要求されます。このとき、そこに指定されているコンセプトのモデルとならない型の入力は診断不用（チェックも警告もされない）の未定義動作になります。  
少なくとも標準ライブラリのものを利用するときは、コンセプトのモデルについて意識を向ける必要があるでしょう。

C++20で導入された`<span>, <ranges>, <format>`や`<algorithm>, <iterator>`の一部等は既にコンセプトを使用するように定義されているため、その事前条件においてはコンセプトのモデルであることを要求するようになっています。

### 参考文献

- [18.2 Equality preservation [concepts.equality]](http://eel.is/c++draft/concepts.equality)
- [16.5.4.12 Semantic requirements [res.on.requirements]](http://eel.is/c++draft/res.on.requirements)
- [`<concepts>` - cpprefjp](https://cpprefjp.github.io/reference/concepts.html)
- [P2102R0 Make “implicit expression variations” more explicit (Wording for US185)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2102r0.html)
- [P2101R0 “Models” subsumes “satisfies” (Wording for US298 and US300)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2020/p2101r0.html)

### 謝辞

この記事の6割は以下の方々によるご指摘によって成り立っています。

- [@yohhoyさん](https://twitter.com/yohhoy/status/1251165903460249602)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2020/20200327_concept_implicit_requirment.md)
