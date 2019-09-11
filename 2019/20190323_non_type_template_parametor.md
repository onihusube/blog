# ［C++］非型テンプレートパラメータたりうるには

※この内容はC++20より有効なものです。現行（C++17）ではまだ1ミリも利用可能な情報ではありません。また、随時記述が変更される可能性があります。

こちらの記事との関連があるので、予め目を通しておくと良いかもしれません。
[https://onihusube.hatenablog.com/entry/2019/01/13/180100:embed:cite]

[:contents]

### 非型テンプレートパラメータとなれるもの
C++17では以下のものが非型テンプレートパラメータとなることができます。

- 整数型
- 列挙型
- オブジェクト・関数ポインタ
- オブジェクト・関数参照（左辺値参照のみ）
- メンバポインタ
- `std::nullptr_t`

C++20では、主に以下の2つのものが非型テンプレートパラメータとなることができるようになります。

- strong structural equalityなリテラル型
- 左辺値参照型

減ってるように見えますが、参照型以外が一つ目にまとめられただけです。  
そして、任意のクラス型（共用体を含まない）がstrong structural equalityであり、constexprに構築可能であるとき、そのクラスのオブジェクトを非型テンプレートパラメータとして利用することができるようになります。

そのような非型テンプレートパラメータとして渡されたオブジェクトはconstなglvalueオブジェクトとなり、異なる非型テンプレートパラメータ毎に唯一つのインスタンスがプログラム内に存在します。当然、メンバ関数呼び出しやアドレス取得が可能です。

こんなことができる・・・かもしれません。
```cpp
//何か値のペアを受け取り出力する
template<auto Pair>
void f() {
   std::cout << std::get<0>(Pair) << ", " << std::get<1>(Pair) << std::endl;
}

f<std::pair<int, int>{10, 20}>();
f<std::tuple<int, int>{10, 20}>();

//固定文字列型
template<typename CharT, std::size_t N>
struct fixed_string {
   constexpr fixed_string(const CharT (&array)[N + 1]) {
      std::copy_n(array, N + 1, str);
   }

   auto operator<=>(const fixed_string&) = default;
   //auto operator==(const fixed_string&) = default;
   
   CharT str[N + 1];
};

template<typename CharT, std::size_t N>
fixed_string(const CharT (&array)[N]) -> fixed_string<CharT, N-1>;

//fixed_stringを出力
template<fixed_string Str>
void g() {
   std::cout << Str.str<< std::endl;
}

g<"Hello World!">();
g<"<=> Awesome!">();
```

### strong structural equality（強い構造的等価性）？
ところで、ぽっと出のstrong structural equalityなる横文字は一体何なのでしょうか・・・？


ある型`T`がstrong structural equalityであるとは以下のどちらかを満たしているときです。

- `T`がクラス型でない場合
    - `cosnt T`の値`a`について`a <=> a`が呼び出し可能
    - その結果となる比較カテゴリ型が`std::strong_­ordering`か`std::strong_­equality`のどちらか
- `T`がクラス型の場合
    - `T`のすべての基底型及び非staticメンバ変数がstrong structural equalityである
    - mutable及びvolatileな非staticメンバ変数を持たない
    - `T`の定義の終了点で、`cosnt T`の値`a`について`a == a`のオーバーロード解決が成功し、`public`なものか`frined`で`default`実装の`==`が見つかる

`T`がクラス型でない場合というのは組み込み型の場合の事で、組み込みの宇宙船演算子の比較カテゴリ型が`std::strong_­equality`に変換可能であればいいわけです。  
浮動小数点型および`void`以外のすべての型がstrong structural equalityになります。

任意のクラス型の場合は`public`か`frined`なdefault実装の`operator==`を持っていて、すべての非staticメンバ変数がstrong structural equalityで（mutable、volatileはng）、基底クラスもそのようになっていればstrong structural equalityになります。  
ただし、この`==`はあくまでstrong structural equalityであることの表明のために必要なだけで実際に比較をするわけではなく、また実際の比較結果によってstrong structural equalityであるかどうか決定されるわけではありません。

これらの諸条件は、浮動小数点型をメンバに持たずに`operator==`をdefault実装していれば、おおよそのケースで満たすことができるはずです。  
ただし、参照型がメンバにある時とUnion-likeな型では`default`の`operator==`は暗黙`delete`されているので注意です。

その上で、非型テンプレートパラメータとして利用するためには`T`はリテラル型である必要があります。  
C++17基準ならば、コンパイル時に構築可能（初期化が定数式で可能）でなくてはなりません。

#### クラス型の`operator==`のチェック

オーバーロード解決が成功し使用可能な`==`が見つかる、という遠回りな言い回しになっているのは、`default`で定義されていても削除されていたりアクセスできないケースのためです。
例えば任意の型を保持するようなクラステンプレートでは、その型次第で`operator==`は削除されている可能性があります。

そのような型には例えば`std::pair`があります。そして、`std::pair`は参照型を保持することができます。

```cpp
//std::pairの参考用簡易実装
template <typename T, typename U>
struct pair {
    T first;
    U second;

    //デフォルト実装のみを提供すると・・・
    friend constexpr bool operator==(const pair&, const pair&) = default;
};

int i = 42, j = 42;
pair<int&, int> p(i, 17);
pair<int&, int> q(j, 17);
assert(p == q);   //C++17までは有効なコード、しかし上記実装だと==はdeleteされているため比較不可能
```
このような場合には`operator==`のデフォルト実装はもはや出来ず、参照型用の実装を追加で提供する必要があります。

```cpp
template <typename T, typename U>
struct pair {
    T first;
    U second;

    friend constexpr bool operator==(const pair&, const pair&) = default;
    
    //参照型用の実装、T,Uのどちらかが参照型ならばより特殊化されているこちらが優先される
    friend constexpr bool operator==(const pair& lhs, const pair& rhs)
       requires (is_reference_v<T> || is_reference_v<U>)
    {
       return lhs.first == rhs.first && lhs.second == rhs.second;
    }
};
```

このようにしておけば参照型に対しても`==`による比較を提供できますが、同時に`default`な`operator==`も存在はしています。
このような場合に、オーバーロード解決を用いて使用可能な`operator==`をチェックすることで非型テンプレートパラメータとして使用されてしまうことを防止しています。


### なぜstrong structural equalityなリテラル型なのか？
それは、二つのインスタンス化されたテンプレートがあるとき、その等価性を判断するためです。

関数・クラステンプレートはODR遵守のために、複数の翻訳単位にわたってその定義がただ一つとなるようにコンパイルされます。それは多くの場合、コンパイラによる名前マングルとリンカによる重複削除によって実現されます。

非型テンプレートパラメータを与えられた関数やクラス名をどうマングルするのかというと至極簡単で、その型名と定数値をマングル名に埋め込みます。そのうえでリンカがそのマングル名のマッチングにより重複定義を削除し、全ての翻訳単位にわたって定義がただ一つになるようにします。

そのため、非型テンプレートパラメータとなれる値は定数でなければならず、`operator==`による比較は同値関係ではなく等価関係でなければなりません。つまり、その定数表現（マングル名に埋め込む値の表現）が異なる値に対して`==`が`true`となったり、同じ値となる筈なのにその定数表現が異なっていたりする型は非型テンプレートパラメータとして認めることは出来ません。

そのような型の典型例は浮動小数点型です。浮動小数点の定数表現はおそらくバイナリ列（2進浮動小数点表現）になると思われますが、丸めの影響で10進固定小数点表現とバイナリ列は必ずしも1対1対応せず、計算を行うとその影響はさらに複雑になります。  
また、`+0.0`と`-0.0`のようにバイナリ列も見た目も異なるが`operator==`による比較が`true`となる値があり、`NaN`という一見同じ値なのに内部表現がいくつもある値も持っており、これらの問題から今後も浮動小数点数を非型テンプレートパラメータとして渡すことは出来ないでしょう・・・。

この様に、何も考えずにクラス型を非型テンプレートパラメータとして許可してしまうと、名前マングルだけではテンプレートの同一性を判定できなくなります。
全基底及びメンバ単位で正確に等価であるかを確認できればその問題は解決されますが、ユーザー定義された`operator==`(or `!=`)においてそれを判定するのは困難です。また、比較演算子のdefault実装もC++17以前にはありません。

しかしC++20では宇宙船演算子が導入され、組み込み型の宇宙船演算子の戻り値型は比較の種類を表す比較カテゴリ型となります。それがstd::strong_equalityであれば等価性を保証できます（weak_equalityでは同値であることしか保証できません）。

また、クラス型についてはdefault実装の`operator==`が導入され、その実装は全基底及びメンバの辞書式比較で実行されます。  
したがって、全基底クラスを含めた全メンバが`<=>`の比較においてstd::strong_equalityを返すような組み込み型に行きつくかぎり、クラス型についてもその等価性を保証できます。

そしてリテラル型であれば、名前マングルを行う段階ではその定数値はすべて確定しており、そのクラスの全メンバの定数表現の列をマングル名とすることで、非型テンプレートパラメータを含めたマングル名の同一性をリンカが判定できるようになります

そしてそのような保証は、ユーザー定義の比較演算子で行うにはあまりにもコンパイラの多大な努力が必要である事が分かるでしょう。

これらの必要な条件をまとめたものが「strong structural equalityなリテラル型」となるわけです。

### 参考文献
- [P0732R2 Class Types in Non-Type Template Parameters](http://wg21.link/p0732)
- [P1185R2 <=> != ==](http://wg21.link/p1185)
- [P1630R1 Spaceship needs a tune-up](http://wg21.link/p1630)
- [テンプレートの実体化の実装方法とODR違反について - 本の虫](https://cpplover.blogspot.com/2013/12/odr.html)

[この記事のMarkdownソース](https://github.com/onihusube/blog/blob/master/2019/20190323_non_type_template_parametor.md)