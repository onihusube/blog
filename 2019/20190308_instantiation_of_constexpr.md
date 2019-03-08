# ［C++］ constexpr関数がインスタンス化されるとき

「[P0859R0 評価されない文脈でconstexpr関数が定数式評価されることを規定](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)」を理解するためのメモです。

constexpr関数についてのインスタンス化という言葉はテンプレートにおけるインスタンス化と同じ意味、すなわちconstexpr関数の定義の評価が発生するという意味合いで使用しています。

### 必要な知識

#### potentially evaluated（潜在的に評価される）

#### unevaluated operands（未評価オペランド）
unevaluated operandsとは、`sizeof`、`decltype`、`noexcept`、`typeid`のオペランド（引数）として指定されるもの（式）の事で、その名の通りそのオペランドは評価されません。

評価されないとは、そのオペランドに含まれるいかなる計算や関数呼び出しも実行されないということで、そこで参照される関数やクラス等の宣言のみを考慮する（定義が必要ない）ことを意味します。

```cpp
struct S;

template<typename T>
int f();

int main()
{
  //評価されないのでSとfには定義が必要ない
  decltype(f<S>()) n = sizeof(f<S>()); //int n = sizeof(int);と等価
  std::cout << n;
}
```
ただし、`noexcept`以外は型名を指定することができ、その場合の型名オペランドはunevaluated operandsではありません。

#### odr-use(d)


#### 特殊メンバ関数が実装されるとき


### 問題
```cpp
struct duration {
  constexpr duration() {}
  constexpr operator int() const { return 0; }
};

int main()
{
  //duration d = duration();
  int n = sizeof(short{duration(duration())});
  std::cout << n;
}
```
コンパイルエラー : [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NeVfflG6R807YydL)  
コメントを外す : [[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/uMlwuCST5e0QM8g7)


### 解決のための変更


### 参考文献
- [5.2 未評価オペランド（unevaluated operand） - C++11の文法と機能(C++11: Syntax and Feature)](http://ezoeryou.github.io/cpp-book/C++11-Syntax-and-Feature.xhtml#unevaluated_operand)
- [リンク時に関連するルールの話 - ここは匣](http://fimbul.hateblo.jp/entry/2014/12/11/000123)
- [mainとodr-usedとpotentially evaluatedの関係 - Qita](https://qiita.com/yohhoy/items/e06227ab0a5c1f579e35)
- [P0859R0: Core Issue 1581: When are constexpr member functions defined?](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/p0859r0.html)
- [1581. When are constexpr member functions defined? - C++ Standard Core Language Active Issues, Revision 100](http://www.open-std.org/jtc1/sc22/wg21/docs/cwg_active.html#1581)