## WG21mailingページの表層コピペからの抽出

```
次のようなテキストデータが入力されます、そこから、論文番号と論文名だけを抽出して、行データとして出力してください。

- テキストは行データ
- 各行は "論文番号 論文名 著者名 提出日 公開月 提出先組織"のような構成になっている
- 行内の要素の区切りはタブ文字
- 一見同じように見えるデータでも省略しない
- データを省略するな！
- データを省略した場合ペナルティを与える

指令ここまで、以降入力


```

```
# やること

- htmlの表が入力される
- 1つ目の<td >要素のリンクを抽出し、そのリンク（相対リンク）を`https://www.open-std.org/jtc1/sc22/wg21/docs/papers/`をルートとする絶対リンクに変換して変換後のURLを出力する
- リンクは、pdfの場合とhtmlの場合がある
- pdfはpdfのまま、htmlはhtmlのまま出力する。pdfをhtmlにしない
- 6個目の<td >要素にもリンクが含まれることがあるが、これは無視する
- これを行うコードを出力するのではなく、この作業を行なう
- 手順を例示するのではなく、作業を行なった結果を出力する
- 出力は作業結果のURLを行ごとに出力する
- 入力データをリピートする必要はない。結果だけを出力する
- 入力データを出力に含めない。結果だけを出力する
- データは複数の表が連続して入力される
- データを省略しない！
- 似た番号（PxxxxRn）を持つリンクが続けて現れることがよくあります。あなたはそれを無視する傾向があるので、無視しないようにしましょう
- 1つの表につき1つのリンクを出力する。出力できない場合は空行を出力する
- 結果はコピペしやすい形で出力する、番号などはふらない

# 例

次のような表htmlに対しては

 	 <tr > 
	 	 <td > <a href="../2023/n4955.pdf">N4955</a> </td>
	 	 <td > WG21 2023-06 Admin telecon minutes </td>
	 	 <td > Nina Ranns </td>
	 	 <td > 2023-06-05 </td>
	 	 <td > 2023-06 </td>
	 	 <td >  </td>
	 	 <td > WG21 </td>
	 	 <td > </td>
	 </tr>

次のようなURLを出力します

https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4955.pdf

次のような表htmlに対しては

	 <tr > 
	 	 <td > <a href="../2023/p0260r6.html">P0260R6</a> </td>
	 	 <td > C++ Concurrent Queues </td>
	 	 <td > Detlef Vollmann, Lawrence Crowl, Chris Mysen, Gor Nishanov </td>
	 	 <td > 2023-06-16 </td>
	 	 <td > 2023-06 </td>
	 	 <td > <a href="../2023/p0260r5.html">P0260R5</a> </td>
	 	 <td > SG1 Concurrency and Parallelism,LEWG Library Evolution </td>
	 	 <td > </td>
	 </tr>

次のようなURLを出力します

https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p0260r6.html

# データ

例示と指令はここまで、以降入力

```


## NotebookLM

（該当期間部分のHTMLソースを入力として）

このHTMLソースに含まれているpdf/htmlファイルへのリンク及びその番号とタイトルを抽出して、次のような形式のMrkdownでリストアップしてください。なお、全部で35本（行）分あります。

```
### [提案番号 文書タイトル](文書へのリンク)
```

- 提案番号: P1234R0やN5678のような形式の番号
- 文書へのリンクはhttpsから始まる絶対リンクにしてください
    - カレントのリンクは"https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2024/"を使用してください
- 表の6列目にもリンクはあることがありますが、これは無視してください
- 表の6列目（各ブロックの上から6つめの`<td>...</td>`）は無視しなさい！！

# 例

文書1つは例えば次のようなhtmlの1ブロックに対応しています

```html
 	 <tr > 
	 	 <td > <a href="../2023/n4955.pdf">N4955</a> </td>
	 	 <td > WG21 2023-06 Admin telecon minutes </td>
	 	 <td > Nina Ranns </td>
	 	 <td > 2023-06-05 </td>
	 	 <td > 2023-06 </td>
	 	 <td >  </td>
	 	 <td > WG21 </td>
	 	 <td > </td>
	 </tr>
```

この例の場合、結果は次のようになります

```
### [N4955 WG21 2023-06 Admin telecon minutes](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/n4955.pdf)
```

別の例です

```html
	 <tr > 
	 	 <td > <a href="../2023/p0260r6.html">P0260R6</a> </td>
	 	 <td > C++ Concurrent Queues </td>
	 	 <td > Detlef Vollmann, Lawrence Crowl, Chris Mysen, Gor Nishanov </td>
	 	 <td > 2023-06-16 </td>
	 	 <td > 2023-06 </td>
	 	 <td > <a href="../2023/p0260r5.html">P0260R5</a> </td>
	 	 <td > SG1 Concurrency and Parallelism,LEWG Library Evolution </td>
	 	 <td > </td>
	 </tr>
```

この例の場合、結果は次のようになります

```
### [P0260R6 C++ Concurrent Queues](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2023/p0260r6.html)
```


## NotebookLM Lint

あなたはLinterです。この文書を精査して、以下の問題点を検出・報告してください：

- 誤字・脱字（typo）
- 文法エラー
- 不自然または不明瞭な表現
- 掲載されているサンプルコードの誤り（文法エラー、実行不能部分、論理的不整合など）
- 複数の文や段落にまたがる整合性の欠如
- その他の表現上の問題点

出力は以下の形式で行ってください：

1. 問題の種類
2. 該当箇所（場所を特定可能なように前後の文脈を含める）
3. 問題の説明
4. （可能であれば）改善案

一度の精査で文書の全体を見て、見つかった問題点は全てまとめて一度で報告してください。
