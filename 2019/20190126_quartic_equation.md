# ［C++］4次方程式の解を求める（フェラーリの方法）

#### 複二次式
[tex:ax^ 4+bx^ 3+cx^ 2+dx+e]という形の4次方程式に対して、奇数次の項の係数[tex:b,d]が0になっている形の4次方程式[tex:ax^ 4+cx^ 2+e]を複二次式と呼びます。

複二次式は[tex:x^ 2]についての二次方程式と見ることで簡単に解くことができます。

[tex:y = x^ 2]とおいてやると[tex:ay^ 2+cy+e]となるので、二次方程式の解の公式を適用してやると

[tex:y=\frac{-c \pm \sqrt{c^ 2 -4ae} }{2a}]

<div>[tex:
\begin{aligned}
x&=\sqrt{y}\\
&=\sqrt{\frac{-c \pm \sqrt{c^ 2 -4ae} }{2a}}
\end{aligned}
]</div>

この様に、簡単に解を求めることができます。

4次方程式には4つの解がありますが、複二次式の場合は二次方程式を解いた解が2つ出てきて、最後に平方根を求めるところでそれぞれ最大2つの解が得られます。

#### フェラーリの方法
[tex:ax^ 4+bx^ 3+cx^ 2+dx+e=0]の形の複二次式ではない4次方程式の解の公式を求める方法がフェラーリさんによって考案されたフェラーリの方法です。
これを導出してみます。

##### 1. 4次の係数を1にする
まず、4次の項の係数を1にします。全体を4次の係数[tex:a]で割ってやります。

<div>[tex:
\begin{aligned}
ax^ 4+bx^ 3+cx^ 2+dx+e&=\frac{a}{a}x^ 4+\frac{b}{a}x^ 3+\frac{c}{a}x^ 2+\frac{d}{a}x+\frac{e}{a}\\
&=x^ 4+\frac{b}{a}x^ 3+\frac{c}{a}x^ 2+\frac{d}{a}x+\frac{e}{a}\\
&=x^ 4+Ax^ 3+Bx^ 2+Cx+D
\end{aligned}
]</div>

3次以下の係数をA,B,C,Dと置きなおして次に進みます。

##### 2. 3次の項を削除する（チルンハウス変換）
次に、チルンハウス変換により3次の項の係数を0にします。3次項を消し去ります・・・。
[tex:x=y-\frac{A}{4}]と置換してやります。

<div>[tex:
\begin{aligned}
x^ 4+Ax^ 3+Bx^ 2+Cx+D&=\left(y-\frac{A}{4}\right)^ 4+A\left(y-\frac{A}{4}\right)^ 3+B\left(y-\frac{A}{4}\right)^ 2+C\left(y-\frac{A}{4}\right)+D{a}\\
&=y^ 4+\left(B-6\left(\frac{A}{4}\right)^ 2\right)y^ 2+\left(C-2B\frac{A}{4}+8\left(\frac{A}{4}\right)^ 3\right)y+D-C\frac{A}{4}+B\left(\frac{A}{4}\right)^ 2-3\left(\frac{A}{4}\right)^ 4\\
&=y^ 4+py^ 2+qy+r
\end{aligned}
]</div>

係数をp,q,rと置いて次に行きます。

もしこの時、[tex:q=0]ならば複二次式として解を求めることができます。

###### チルンハウス変換
一般のn次方程式[tex:a _ nx^ n + a _ {n-1}x^ {n-1}+ ... + a _ 0 = 0]に対して[tex:x = y - \frac{a _ {n-1}}{na _ n}]のような変数変換を行うと、n-1次の係数を0にすることができます。これをチルンハウス変換と呼びます。

ちなみに、5次方程式で出てくるチルンハウス変換はこれを推し進めた結果4～2次までの項を消し去ることに成功した、少しハイレベルなチルンハウス変換です。結果として手計算がほぼ不可能になっているようですが・・・。

##### 3. 3次式にする
4次式のままだと相変わらず解けないので、何とかして式の次数を落としましょう。[tex:y^ 4+py^ 2+qy+r = (y^ 2 +a)^ 2-b(x+c)^ 2]と変形した時の[tex:a,b,c]を考えてみます。

まず、変形後の式を展開します。
<div>[tex:
\begin{aligned}
(y^ 2 +a)^ 2-b(x+c)^ 2&=y^ 4 +2ay^ 2 +a^ 2 -b(y^ 2+2cy+c^ 2)\\
&=y^ 4 +2ay^ 2 +a^ 2 -by^ 2-2bcy-bc^ 2)\\
&=y^ 4 +(2a-b)y^ 2 +(-2bc)y +(a^ 2-bc^ 2)\\
&=y^ 4+py^ 2+qy+r
\end{aligned}
]</div>

[tex:p,q,r]と対応する係数を比較することで以下の関係が分かります。

<div>[tex:
\begin{aligned}
p&=2a-b\\
q&=-2bc\\
r&=a^ 2-bc^ 2
\end{aligned}
]</div>

この連立方程式から[tex:a,c]が消えるように変形すると




##### 4. 2次式にする

#### 判別式

#### C++実装


#### 参考文献
- [四次方程式 - Wikipedia](https://ja.wikipedia.org/wiki/%E5%9B%9B%E6%AC%A1%E6%96%B9%E7%A8%8B%E5%BC%8F)
- [四次方程式 - 数学対話第5期](http://aozoragakuen.sakura.ne.jp/taiwa/taiwaNch02/node12.html)
- [４次方程式解の公式 - Fukusukeの数学めも](https://mathsuke.jp/ferrari_formula/)