# ［C++］入れ子クラステンプレートの推論補助

最近少しはまったことのメモです。

[:contents]

### 入れ子クラス

入れ子クラスとは、別のクラスの内部で定義されたクラスの事です。

```cpp
struct S {
  struct N {
  };
};
```

この`S::N`の事を入れ子クラスとここでは呼びます。

入れ子になってはいてもクラスとしての制限は特になく、テンプレートにすることもできます。

```cpp
struct S {
  template<typename T>
  struct N {
    T t;
  };
};
```

この時、入れ子クラステンプレートの推論補助を書きたくなった場合、どうすればよいのでしょうか？`S`のスコープには書けないような気がしますが、名前空間スコープに書いても見つけてもらえなさそうな気もします。

この回答は、推論補助は関連するクラステンプレートと同じスコープで定義する、になります。

```cpp
struct S {
  template<typename T>
  struct N {
    T t;
  };

  N(const char*) -> N<std::string_view>;  // Nと同じスコープで定義する
};

int main() {
  S::N n{"test"}; // ok、S::N<std::string_view>が推論される

  assert(n.t.length() == 4);  // ✔ string_viewになっている
}
```

[godbolt](https://godbolt.org/z/4d953WWvh)

これはC++17でCTADが入った時から一貫した仕様です。・・・ですが、GCCは11まではこの入れ子クラステンプレートの推論補助の記述に対応していなかったようで、12から修正されています。今回見事にGCC11で困りました。

GCC11までのバグを回避する簡単な方法は、対応するコンストラクタを書くことです。CTADにおいてはコンストラクタから推論補助が導出されて使用されるため、クラステンプレートのテンプレートパラメータを使用するようなコンストラクタを書くことで推論補助が自動で生成されます。ただし、コンストラクタテンプレートにしてしまうとCTADを成功させることができなくなる（かかなり困難になる）ので注意が必要です。

ただし、上の例のような推論補助と同じ振る舞いをするコンストラクタは書くことができません（たぶん）。

### リーガルチェック

[[temp.deduct.guide]/3](https://eel.is/c++draft/temp.deduct.guide#3.sentence-4)の一節より

> A deduction-guide shall inhabit the scope to which the corresponding class template belongs and, for a member class template, have the same access.

翻訳（powered by PLAMO翻訳）

> 推論補助は、対応するクラステンプレートが属するスコープ内に配置され、入れ子クラステンプレートの場合は同じアクセス権を持つ必要がある。

すなわち、正確には同じスコープかつ同じアクセス指定を持つ必要があります。

```cpp
struct S {
  template<typename T>
  struct N {
    T t;
  };

private:
  N(const char*) -> N<std::string_view>;  // ng、Nと同じアクセス指定を持っていない
};
```

[godbolt](https://godbolt.org/z/hcof67xoW)

この時、アクセス指定が一致してればいいだけで、`private`や`protected`な入れ子クラステンプレートで推論補助が書けないわけではありません。

```cpp
struct S {
protected:
  template<typename T>
  struct N {
    T t;
  };

  N(const char*) -> N<std::string_view>;  // ok
};

struct D : public S {
  void f() {
    S::N n{"test"}; // ok

    assert(n.t.length() == 4);  // ✔
  }
};
```

[godbolt](https://godbolt.org/z/3G36K9nox)

### ローカルクラス

入れ子クラスとよく似たクラスにローカルクラスがありますが、こちらの場合は推論補助はどうなるのか気になる人もいるかもしれません。

しかし、ローカルクラスはテンプレートにすることができないため、そもそも推論補助が必要にならず、推論補助を書くこともできません。

### 参考文献

- [c++ - How to provide deduction guide for nested template class? - Stack Overflow](https://stackoverflow.com/questions/46103102/how-to-provide-deduction-guide-for-nested-template-class)
- [gcc bug 79501](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=79501)
- [Class template argument deduction (CTAD) (since C++17) - cppreference.com](https://en.cppreference.com/cpp/language/class_template_argument_deduction)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2026/20260823_nested_class_deduction_guide.md)
