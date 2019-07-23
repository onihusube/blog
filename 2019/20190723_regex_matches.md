# ［C++］std::regexでパターンにマッチするすべての文字列を抽出する

`std::regex`を使う時多くの場合は`std::regex_search`を使うと思われますが、`std::regex_search`はそのままだとマッチする1番最初の文字列しか得ることができません。  
しかし、文字列の中からマッチする全ての要素が欲しいということはよくあることでしょう。調べても頑張ってずらしてもう一回searchだ！という方法しか出てきません。やはりスマートにやりたい・・・

### std::match_results::suffix()

`std::regex_search`の結果として得られる`std::match_results`は`suffix()`というメンバ関数を持っています。この関数は結果としてマッチした文字列を除いた残りの文字列（への参照）を返します。  
その文字列に対してもう一度searchすれば2番目にマッチする部分文字列が得られ、それを繰り返せば残りのマッチング文字列を得ることができます。

```cpp
#include <regex>

int main()
{
  std::string str = "1421, 34353, 7685, 12765, 976754";
  std::regex patern{R"(\d+)"};
  std::smatch match{};
  
  while (std::regex_search(str, match, patern)) {
    std::cout << match[0].str() << std::endl;
    str = match.suffix();
  }
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/JdEDNJA358m99Y12)

とても簡単な方法ではありますが、一々コピーが発生するのと、変更可能な`std::string`等でしか使えないのが少し残念なところです。

### std::sub_match::second
頑張ってずらしてもう一回searchだ！という方法を頑張らないでやる方法です。

`std::match_results`は`std::sub_match`としてパターン内各グループの結果を保持しており、一番最初の`std::sub_match`は見つかった文字列全体が得られます。  
そして、`std::sub_match::second`はそのサブマッチ文字列の次の位置を指すイテレータです。

つまり、一番最初の`std::sub_match::second`を始点としてもう一度`std::regex_search`をすれば2番目にマッチする文字列が得られ、それを繰り返せば文字列内からパターンに一致する全ての部分文字列を抽出することができます。

```cpp
#include <regex>

int main()
{
  constexpr char str[] = "1421, 34353, 7685, 12765, 976754";
  std::regex patern{R"(\d+)"};
  std::match_results<const char*> match{};
  
  for (bool ismatch = std::regex_search(str, match, patern); ismatch != false; ismatch = std::regex_search(match[0].second, match.suffix().second, match, patern)) {
    std::cout << match[0].str() << std::endl;
  }
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/BLusWFgC2vKl0XZ5)

for文の宣言部がとても長くて見づらいですが、`std::regex_search`を繰り返し毎に実行し、その結果の`bool`値を見て終了判定しています。

そして、ループ中の`std::regex_search`は`match[0].second`から始めることでそれまでに一致した部分を飛ばして探索しています。なお、`match.suffix().second`というのは元の文字列の終端（`std::end(str)`相当）に当たります（`std::end(str)`でも良いはずですが、型が合わないと怒られたのでこうしました・・・）。

この方法はイテレータを用いて元の文字列の参照範囲を変更して再検索しているだけなので、文字列のコピーは発生しません。

### std::regex_iterator

上記`std::sub_match::second`を用いる方法をラッピングしたイテレータが`std::regex_iterator`として標準に用意されています。

```cpp
int main()
{
  constexpr char str[] = "1421, 34353, 7685, 12765, 976754";
  std::regex patern{R"(\d+)"};
  
  for (std::regex_iterator<const char*> itr{std::begin(str), std::end(str), patern}, last{}; itr != last; ++itr) {
    std::cout << (*itr).str() << std::endl;
  }
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/VcQld37qfxNVBjX5)

多少スッキリとし、基本的なイテレータ操作で書けているので処理も分かりやすいです。  
先ほどの`std::sub_match::second`を使って次を検索、という部分を`std::regex_iterator`が中でよろしくやってくれています。

### regex_searchesを作る

やはり、`regex_search`のように一発でやりたいし、なんなら範囲for文使いたいです。なので綺麗にラッピングして少し便利にしてやりましょう。

```cpp
template<typename Str>
auto regex_searches(Str& str, const std::regex& patern) {
  using std::begin;
  using std::end;
  using str_iterator_t = decltype(begin(str));
  
  struct wrap_regex_iterator {
    using iterator = std::regex_iterator<str_iterator_t>;
  
    auto begin() const noexcept -> iterator {
      return first;
    }
    
    auto end() const noexcept -> iterator {
      return last;
    }
    
    explicit operator bool() const noexcept {
      return first != last;
    }
    
    iterator first;
    iterator last;
  };
  
  return wrap_regex_iterator{{begin(str), end(str), patern}, {}};
}


int main() {
  const std::string str = "1421, 34353, 7685, 12765, 976754";
  std::regex patern{R"(\d+)"};
  
  for (auto&& match : regex_searches(str, patern)) {
    std::cout << match.str() << std::endl;
  }
}
```
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/NrwJAYauBxtaVv9i)

ローカルクラス大好きなのでローカルクラスを使いましたが、外にあっても構いません。あと`operator bool`はあくまで`regex_search`のように戻り値を利用するために付けただけなのでなくてもいいです。というか範囲forで使う分にはほぼ無意味です。

入力となる型などを厳密にする場合は、`std::regex_search`の各オーバーロードと同様にする必要がありますが、ここでは割愛・・・

書くことが多くなるので、数カ所で使うとかどうしても範囲forでーというときに多少便利になるかもしれません。

### 参考文献
- [std::regex_search - cpprefjp](https://cpprefjp.github.io/reference/regex/regex_search.html)
- [std::regex_search - cppreference.com](https://ja.cppreference.com/w/cpp/regex/regex_search)
- [std::match_results - cpprefjp](https://cpprefjp.github.io/reference/regex/match_results.html)
- [std::sub_match - cpprefjp](https://cpprefjp.github.io/reference/regex/sub_match.html)
- [std::regex_iterator - cpprefjp](https://cpprefjp.github.io/reference/regex/regex_iterator.html)

### 謝辞
この記事の7割は以下の方によるご指摘によって成り立っています。

- [@hotwatermorning さん](https://twitter.com/hotwatermorning/status/1153505071407063042)