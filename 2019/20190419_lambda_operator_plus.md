# ［C++］ラムダ式と単項+演算子

状態を持たない（つまり、キャプチャをしていない）ラムダ式は暗黙的に同じシグネチャの関数ポインタに変換することができます。  
しかし、テンプレートパラメータの推論等のタイミングでは暗黙変換以前にラムダ式の生成する関数オブジェクトとしての型が推論されてしまい、関数ポインタとしてラムダ式を受け取ろうとしてもそのオーバーロードにはマッチしません。

```cpp
template<typename F>
void invoke(F&& f) {
  std::cout << "call functor." << std::endl;
  std::cout << f() << std::endl;
}

template<typename F>
void invoke(F* f) {
  std::cout << "call function pointer." << std::endl;
  std::cout << f() << std::endl;
}

int main()
{
  invoke([]{ return 10; });
}

/* 出力
call functor.
10
*/
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/EFmFqQRpCRIWl7Kl)

ごくたまに、こういう時に何とかして関数ポインタの方に行ってほしいことがあります。そんな時、わざわざ関数ポインタの型を`using`してキャストして...としなくても次のように頭に`+`を付けることで解決できます。

```cpp
template<typename F>
void invoke(F&& f) {
  std::cout << "call functor." << std::endl;
  std::cout << f() << std::endl;
}

template<typename F>
void invoke(F* f) {
  std::cout << "call function pointer." << std::endl;
  std::cout << f() << std::endl;
}

int main()
{
  invoke( []{ return 10; });
  invoke(+[]{ return 20; });
}

/* 出力
call functor.
10
call function pointer.
20
*/
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/LQD1O93SWTizPjD4)

見た目からすると、ラムダの頭に`+`を付けることで明示的に関数ポインタへ変換しているような気分になれます。

## 組み込みの単項+演算子の挙動
C++17規格の組み込み単項+演算子を見てみると次のようにあります。

>The operand of the unary + operator shall have arithmetic, unscoped enumeration, or pointer type and the result is the value of the argument. Integral promotion is performed on integral or enumeration operands. The type of the result is the type of the promoted operand.

重要なところだけをなんとなく訳すと（powered by google翻訳）

>単項+演算子の引数型は算術型、スコープ無し列挙型、ポインタ型のいずれかでなければならず、結果は引数をそのまま返す。

重要なのは任意のポインタ型に対して単項+演算子が用意されている、という所です。

つまり、単項`+`がラムダ式に対して特別に用意されているわけではなく、ラムダ式に`+`を適用すると、暗黙の型変換により関数ポインタに変換され、その関数ポインタが結果として返されているわけです。

上記のように他のものに対しての単項`+`演算子は恒等写像みたいなもので、単項`-`演算子の対としての役割しかないので、単項`+`演算子が有効に使える唯一のケースかと思われます（整数昇格される、という所も何か役立つかもしれません）。

## 使いどころ？

あまり意味がないと言えばそんな気もするのですが、`std::function`と関数ポインタを取る関数をオーバーロードとして別々に分けているとき、そこにラムダ式を渡す場合に役立つかもしれません。

```cpp
template<typename... Args>
void invoke(const std::function<void(Args...)>& f, Args&&... args) {
  std::cout << "call std::function." << std::endl;
  f(std::forward<Args>(args)...);
}

template<typename... Args>
void invoke(void(*f)(Args...), Args&&... args) {
  std::cout << "call function pointer." << std::endl;
  f(std::forward<Args>(args)...);
}

int main()
{
  //オーバーロード候補二つがマッチするため、コンパイルエラー
  invoke( [](int n, double d){ std::cout << n << ", " << d << std::endl; }, 10, 3.14);
  
  //常に関数ポインタを受け取る方が選ばれる
  invoke(+[](int n, double d){ std::cout << n << ", " << d << std::endl; }, 20, 2.72);
}
```
[上 - [Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/YFwiEPKQfh5xJK9B)  
[下 - [Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/6IMsAgcJL7fguRoJ)

こういうことをしたいときのほかにも、Cなインターフェースを持ったライブラリにラムダを渡そうとするときにも役に立つことがあるかもしれません。

## 参考文献
- [8.3.1 Unary operators [expr.unary.op] - N4659](https://timsong-cpp.github.io/cppwp/n4659/expr.unary.op#7)
- [Resolving ambiguous overload on function pointer and std::function for a lambda using + - stack overflow](https://stackoverflow.com/questions/17822131/resolving-ambiguous-overload-on-function-pointer-and-stdfunction-for-a-lambda)
- [A positive lambda: '+[]{}' - What sorcery is this? - stack overflow](https://stackoverflow.com/questions/18889028/a-positive-lambda-what-sorcery-is-this)

## 謝辞
この記事の9割は以下の方々によるご指摘で成り立っています。

- [@kariya_mitsuruさん](https://twitter.com/kariya_mitsuru/status/1118111171653988353)
- [@kazatsuyuさん](https://twitter.com/kazatsuyu/status/1118111753122902017)
- [@hoge_fuga_0000さん](https://twitter.com/hoge_fuga_0000/status/1118123498432372736)

