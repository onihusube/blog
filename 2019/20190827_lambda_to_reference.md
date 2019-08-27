# ［C++］ラムダ式から関数参照への変換（単項*演算子の作用について）

状態を持たないラムダ式は単項+演算子を頭につけると明示的に対応する関数ポインタに変換することができます。では、そこから関数への参照に変換した時はどうすれば良いのでしょうか？  
`+`をつけないだけでは関数参照にはなってくれません・・・

```cpp
template<typename F>
void invoke(F&& f) {
  std::cout << "call functor." << std::endl;
  std::cout << f() << std::endl;
}

void invoke(int(&f)(void)) {
  std::cout << "call function reference." << std::endl;
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
call functor.
20
*/
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/a7NtwhZDXlgxUT1l)

あるのかわからないですが、こういう時に関数の参照をとるオーバーロードが選ばれてほしい時、わざわざ関数ポインタの型を`using`してキャストして...としなくても次のように頭に`*`を付けることで解決できます。

```cpp
template<typename F>
void invoke(F&& f) {
  std::cout << "call functor." << std::endl;
  std::cout << f() << std::endl;
}

void invoke(int(&f)(void)) {
  std::cout << "call function reference." << std::endl;
  std::cout << f() << std::endl;
}

int main()
{
  invoke( []{ return 10; });
  invoke(+[]{ return 20; });
  invoke(*[]{ return 30; });
}

/* 出力
call functor.
10
call functor.
20
call function reference.
30
*/
```

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/pwcpTXhjJJ8Y7TZb)

見た目からすると、ラムダの頭に`*`を付けることで明示的に関数参照へ変換しているように見えます。

なお、同じシグネチャの関数ポインタをとるオーバーロードがあるとオーバーロード解決に失敗します。関数参照は関数ポインタに暗黙変換可能であり、その変換はオーバーロード順位に影響を及ぼさない為です（これはC++17以上からの挙動のようです）。

[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NbZLtR2MGHAu0pjt)

## 組み込みの単項*演算子
C++17規格の組み込み単項`*`演算子について見てみると次のようにあります。

>he unary * operator performs *indirection*: the expression to which it is applied shall be a pointer to an object type, or a pointer to a function type and the result is an lvalue referring to the object or function to which the expression points. 

なんとなく訳すと（powered by google翻訳）

>単項`*`演算子は間接参照を行う。引数型はオブジェクト型へのポインタ、もしくは関数へのポインタでなければならず、結果は引数が指すオブジェクトまたは関数を参照するlvalueとなる。

つまり、ラムダ式に`*`を適用すると、暗黙の型変換により関数ポインタに変換され、その関数ポインタ参照先の実体が参照として返されており、戻り値型は関数参照型となるわけです。

## 使いどころ？
正直わかりません。ほぼノーコストで対応する関数ポインタへ暗黙変換されるのでラムダ式に単項`+`を使いたくなるときに替わりに使っても良いかもしれません。  
そのようなコードを持っていけば誰かにドヤ顔できるかもしれません・・・・

## 小ネタ
単項`+`は関数ポインタから関数ポインタへ、単項`*`は関数ポインタから関数参照へ、それぞれ変換するので、それらを複数組み合わせることができるはずです、そう幾つでも・・・

```cpp
int main()
{
  invoke(*+*+*+*[]{ return 10; });
  invoke(+*+*+*[]{ return 20; });
  invoke(*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*+*[]{ return 30; });
  invoke(**************+ + + + + + + + + + + + + + + + + + + + + + +**************+*+ + +*+*+ + +[]{ return 40; });
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/J6VMUH5z6EqnIdB3)

残念ながら、`+`を複数繋げるとインクリメントになってしまうので間にスペースが必要です。`*`の連続適用は関数ポインタへ暗黙変換されるので問題ない様子です。

## 参考文献
- [8.3.1 Unary operators [expr.unary.op] - N4659](https://timsong-cpp.github.io/cppwp/n4659/expr.unary.op#1)
- [Stateless lambdas can be converted to a function pointer, but not a function reference? - reddit](https://www.reddit.com/r/cpp/comments/cvcle8/stateless_lambdas_can_be_converted_to_a_function/)
- [［C++］ラムダ式と単項+演算子 - ](https://onihusube.hatenablog.com/entry/2019/04/19/204552)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190419_lambda_operator_plus.md)