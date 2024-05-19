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


P2831R0	Functions having a narrow contract should not be noexcept	Timur Doumler, Ed Catmur	2023-05-16	2023-05		Library Evolution	
P2834R0	Semantic Stability Across Contract-Checking Build Modes	Joshua Berne, John Lakos	2023-05-15	2023-05		SG21 Contracts	
P2835R0	Expose std::atomic_ref's object address	Gonzalo Brito Gadeschi	2023-05-18	2023-05		SG1 Concurrency and Parallelism	
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
- データを無視しない！！！
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
