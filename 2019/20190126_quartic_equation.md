# ［C++］フェラーリの方法による4次方程式の求解

[:contents]

### フェラーリの方法
[tex:ax^ 4+bx^ 3+cx^ 2+dx+e=0]の形の実数係数4次方程式の解の公式を求める方法がフェラーリさんによって考案されたフェラーリの方法です。
まずは、これを導出してみます。

#### 1. 4次の係数を1にする
まず、4次の項の係数を1にします。全体を4次の係数[tex:a]で割ってやります。

<div align="center">[tex:
\begin{aligned}
ax^ 4+bx^ 3+cx^ 2+dx+e&=\frac{a}{a}x^ 4+\frac{b}{a}x^ 3+\frac{c}{a}x^ 2+\frac{d}{a}x+\frac{e}{a}\\
&=x^ 4+\frac{b}{a}x^ 3+\frac{c}{a}x^ 2+\frac{d}{a}x+\frac{e}{a}\\
&=x^ 4+Ax^ 3+Bx^ 2+Cx+D
\end{aligned}
]</div>

3次以下の係数をA,B,C,Dと置きなおして次に進みます。

このように最高次の係数を1にした1変数多項式をモニック多項式と呼んだりします。

#### 2. 3次の項を削除する（チルンハウス変換）
次に、チルンハウス変換により3次の項の係数を0にします。3次項を消し去ります・・・。
[tex:x=y-\frac{A}{4}]と置換してやります。

<div align="center">[tex:
\begin{aligned}
x^ 4+Ax^ 3+Bx^ 2+Cx+D&=\left(y-\frac{A}{4}\right)^ 4+A\left(y-\frac{A}{4}\right)^ 3+B\left(y-\frac{A}{4}\right)^ 2+C\left(y-\frac{A}{4}\right)+D\\
&=y^ 4-4y^ 3\left(\frac{A}{4}\right)+6y^ 2\left(\frac{A}{4}\right)^ 2-4y\left(\frac{A}{4}\right)^ 3+\left(\frac{A}{4}\right)^4+Ay^ 3-A3y^ 2\frac{A}{4}+A3y\left(\frac{A}{4}\right)^ 2-A\left(\frac{A}{4}\right)^ 3+By^ 2-B2y\frac{A}{4}+B\left(\frac{A}{4}\right)^ 2+Cy-C\frac{A}{4}+D\\
&=y^ 4+(-A+A)y^ 3+\left(\frac{6A^ 2}{16}-\frac{3A^ 2}{4}+B\right)y^ 2+\left(-\frac{4A^ 3}{64}+\frac{3A^ 3}{16}-\frac{AB}{2}+C \right)y+\left(\frac{A}{4}\right)^ 4-A\left(\frac{A}{4}\right)^ 3+B\left(\frac{A}{4}\right)^ 2-C\left(\frac{A}{4}\right)+D\\
&=y^ 4+\left(-\frac{6}{16}A^ 2+B \right)y^2+\left(\frac{8}{64}A^ 3-\frac{AB}{2}+C \right)y+\left(\frac{A}{4}-A\right)\left(\frac{A}{4}\right)^ 3+B\left(\frac{A}{4}\right)^ 2-C\left(\frac{A}{4}\right)+D\\
&=y^ 4+\left(-6\left(\frac{A}{4}\right)^ 2+B\right)y^ 2+\left(8\left(\frac{A}{4}\right)^3-2B\left(\frac{A}{4}\right)+C\right)y+\left(-3\left(\frac{A}{4}\right)^4+B\left(\frac{A}{4}\right)^2-C\left(\frac{A}{4}\right)+D\right)\\
&=y^ 4+py^ 2+qy+r
\end{aligned}
]</div>

係数をp,q,rと置いて次に行きます。

##### チルンハウス変換
一般のn次方程式[tex:a _ nx^ n + a _ {n-1}x^ {n-1}+ ... + a _ 0 = 0]に対して[tex:x = y - \frac{a _ {n-1}}{na _ n}]のような変数変換を行うと、n-1次の係数を0にすることができます。これをチルンハウス変換と呼びます。

ちなみに、5次方程式で出てくるチルンハウス変換はこれを推し進めた結果4～2次までの項を消し去ることに成功した、少しハイレベルなチルンハウス変換です。結果として手計算がほぼ不可能になっているようですが・・・。

#### 3. 完全平方式に
4次式のままだと相変わらず解けないので、何とかして式の次数を落とします。

式を右辺と左辺に分け、両辺を[tex:y]に関する完全平方式にすることを考えます。どういうことかというと、[tex: (y^ 2+t)^ 2 = (my+n)^ 2]の形にするのです。ただし、途中で出てくる係数を綺麗にするために[tex:t=\frac{t}{2}]と置き換えて置きます。
まず、[tex: (y^ 2+\frac{t}{2})^ 2 = y^ 4+ty^ 2+\frac{t^ 2}{4}]という公式を利用します。ここではまだ、[tex:t]は任意の数として具体的に決めないでおきます。

<div align="center">[tex:
\begin{aligned}
y^ 4+py^ 2+qy+r&=0\\
y^ 4 &=-py^ 2-qy-r\\
y^ 4 +ty^ 2+\frac{t^ 2}{4}&=-py^ 2-qy-r +ty^ 2+\frac{t^ 2}{4}\\
(y^ 2+\frac{t}{2})^2&=(t-p)y^ 2-qy+(\frac{t^ 2}{4}-r)
\end{aligned}
]</div>

左辺をまず完全平方式にするために、4次の項だけを左辺に残して両辺に[tex:ty^ 2+\frac{t^ 2}{4}]を加えて変形していきます。結果、左辺は完全平方式になりましたが右辺はまだそうなってはいません。右辺の式はよく見てみると[tex:y]に関する2次式になっています。

ここで、2次式が完全平方式になるためにはその判別式（[tex:D=b^ 2-4ac]）が0でなければならないという条件を利用します。その条件を満足するように[tex:t]の値を決めてやります。

<div align="center">[tex:
\begin{aligned}
b^ 2-4ac&=(-q)^ 2-4(t-p)(\frac{t^ 2}{4}-r)\\
&=q^ 2 -4(\frac{t^ 3}{4}-rt-\frac{pt^ 2}{4}+pr)\\
&=q^ 2 -t^ 3+4rt+pt^ 2-4pr\\
&=-t^ 3+pt^ 2+4rt+q^ 2-4pr\\
&=t^ 3-pt^ 2-4rt+(4pr-q^ 2)\\
&=0
\end{aligned}
]</div>

と、このように[tex:t]に関しての3次方程式が出てきました。この3次方程式の3つの解のうち1つを選んで[tex:t]としてやれば、[tex:(-q)^ 2-4(t-p)(\frac{t^ 2}{4}-r)=0]の条件を満たしているため先ほどの式の右辺を完全平方式[tex:(my+n)^ 2]の形に置き換えることができます（3次方程式の求解は[以前の記事](https://onihusube.hatenablog.com/entry/2018/10/08/140426)に投げます）。

そして、ここで得られた3次方程式のことを三次分解方程式と呼びます。

それでは右辺を完全平方式に変形します。途中で、[tex:x^ 2-2ax = (x-a)^ 2-a^ 2]という関係を使って式を変形します。

<div align="center">[tex:
\begin{aligned}
(t-p)y^ 2-qy+(\frac{t^ 2}{4}-r)&=(t-p)\left(y^ 2-\frac{qy}{t-p}+\frac{\frac{t^ 2}{4}-r}{t-p} \right)\\
&=(t-p)\left(y^ 2-2\frac{q}{2(t-p)}y+\frac{\frac{t^ 2}{4}-r}{t-p} \right)\\
&=(t-p)\left(\left(y-\frac{q}{2(t-p)}\right)^ 2-\left(\frac{q}{2(t-p)}\right)^ 2+\frac{\frac{t^ 2}{4}-r}{t-p} \right)\\
&=(t-p)\left(\left(y-\frac{q}{2(t-p)}\right)^ 2-\frac{q^ 2}{4(t-p)^ 2}+\frac{\frac{t^ 2}{4}-r}{t-p} \right)\\
&=(t-p)\left(y-\frac{q}{2(t-p)}\right)^ 2-\frac{q^ 2}{4(t-p)}+\frac{t^ 2}{4}-r\\
&=(t-p)\left(y-\frac{q}{2(t-p)}\right)^ 2-\frac{1}{4(t-p)}(q^ 2-4(t-p)(\frac{t^ 2}{4}-r))\\
&=(t-p)\left(y-\frac{q}{2(t-p)}\right)^ 2-\frac{1}{4(t-p)}\cdot 0\\
&=(t-p)\left(y-\frac{q}{2(t-p)}\right)^ 2
\end{aligned}
]</div>

途中で判別式の[tex:q^ 2-4(t-p)(\frac{t^ 2}{4}-r)=0]を利用して不要な項をまとめて消してしまっています（というか、これが出てくるため前述の条件がある）。結果、完全平方式一歩手前のすっきりした式になりました。  
さらに変形して[tex:m, n]を求めてやりましょう。外に出ている[tex:(t-p)]を何とかしてかっこの中に埋め込みます。

<div align="center">[tex:
\begin{aligned}
(y^ 2+\frac{t}{2})^2&=(t-p)y^ 2-qy+(\frac{t^ 2}{4}-r)\\
&=(t-p)\left(y-\frac{q}{2(t-p)}\right)^ 2\\
&=(\sqrt{t-p})^ 2\left(y-\frac{q}{2(t-p)}\right)^ 2\\
&=\left((\sqrt{t-p}) \left(y-\frac{q}{2(t-p)}\right)\right)^ 2\\
&=\left(\sqrt{t-p}y-\frac{q \sqrt{t-p}}{2(t-p)}\right)^ 2\\
&=\left(\sqrt{t-p}y-\frac{q}{2\sqrt{t-p}}\right)^ 2\\
&=(my+n)^ 2
\end{aligned}
]</div>

半ば無理やりかっこの中へ押し込み、[tex:(my+n)^ 2]の形に持っていきました。下から二行目では[tex:\sqrt{t-p}]の有理化によって係数を少しすっきりとさせています。

#### 4. 2次式へ
天下り的に4次方程式から両辺を[tex:y]に関する完全平方式の形に変換していましたが、なぜそのようなことをするのでしょうか？得られた完全平方式を変形してみると

<div align="center">[tex:
\begin{aligned}
(y^ 2+\frac{t}{2})^ 2&=(my+n)^ 2\\
(y^ 2+\frac{t}{2})^ 2-(my+n)^ 2&=0\\
(y^ 2+\frac{t}{2} + my+n)(y^ 2+\frac{t}{2} - my -n)&=0\\
(y^ 2+my+\frac{t}{2}+n)(y^ 2-my+\frac{t}{2}-n)&=0
\end{aligned}
]</div>

2行目→3行目では、因数分解でよく出る二乗の公式（[tex:x^ 2-y^ 2=(x+y)(x-y)]）を使っています。  
このように二つの[tex:y]に関する2次方程式の積に変形することができます。この式が成り立つのはどちらか（もしくは両方）の2次式が0になるとき、つまり[tex:y]がそれぞれの2次方程式の解となるときです。

遠回りをしてきたので印象薄いかもしれませんが、ここの[tex:y]はチルンハウス変換後の式[tex:y^ 4+py^ 2+qy+r]から来ています。つまり、この二つの2次式の解として求められる[tex:y]こそが欲しかった4次方程式の解となります。

2次方程式の解の公式は分かっているのでそれを利用すれば4次方程式の解の公式は以下のようになります。

<div align="center">[tex:
\begin{aligned}
y_{1,2}&=\frac{-m\pm \sqrt{m^ 2-4(\frac{t}{2}+n)}}{2}\\
y_{3,4}&=\frac{m\pm \sqrt{m^ 2-4(\frac{t}{2}-n)}}{2}
\end{aligned}
]</div>

必要な係数[tex:m, t, n]はここまでですでに求まっていますので、この式は解くことができそうです。

#### 5. 得られた各値より解を求める
無事に[tex:y]が4つ得られたので、チルンハウス変換を解いて[tex:x]を求めてやりましょう。と言ってもそのままそれぞれの[tex:x,y]について

<div align="center">[tex:
\begin{aligned}
x_i&=y_i - \frac{A}{4}
\end{aligned}
]</div>

としてやれば、4次方程式の4つの解[tex:x]を求めることができます。  
先ほどの式をまとめて少し展開すると

<div align="center">[tex:
\begin{aligned}
y&=\frac{-(\pm m) \pm \sqrt{(\pm m)^ 2-4(\frac{t}{2}\pm n)}}{2}\\
&=\frac{\mp m \pm \sqrt{m^ 2-4(\frac{t}{2}\pm n)}}{2}\\
&=\frac{\mp m \pm \sqrt{m^ 2-2t-(\pm 4n)}}{2}\\
&=\frac{\mp m \pm \sqrt{m^ 2-2t\mp 4n}}{2}\\
&=\frac{\mp \sqrt{t-p} \pm \sqrt{(\sqrt{t-p})^ 2-2t\mp 4 \left(-\frac{q}{2\sqrt{t-p}} \right)}}{2}\\
&=\frac{\mp \sqrt{t-p} \pm \sqrt{(t-p)-2t\mp \left(-2\frac{q}{\sqrt{t-p}} \right)}}{2}\\
&=\frac{\mp \sqrt{t-p} \pm \sqrt{-t-p \pm \left(2\frac{q}{\sqrt{t-p}} \right)}}{2}\\
&=\frac{\mp_1 \sqrt{t-p} \pm_2 \sqrt{-t-p \pm_1 \left(2\frac{q}{\sqrt{t-p}} \right)}}{2}
\end{aligned}
]</div>

[tex:\mp_1,\pm_1]は二つの2次式より、[tex:\pm_2]は解の公式より来ているものなので独立に変化します。分かりやすく分けて、チルンハウス逆変換も含めて書けば各式は以下のようになります。

<div align="center">[tex:
\begin{aligned}
x_1&=\frac{- \sqrt{t-p} + \sqrt{-t-p + \left(2\frac{q}{\sqrt{t-p}} \right)}}{2}- \frac{A}{4}\\
x_2&=\frac{- \sqrt{t-p} - \sqrt{-t-p + \left(2\frac{q}{\sqrt{t-p}} \right)}}{2}- \frac{A}{4}\\
x_3&=\frac{\sqrt{t-p} + \sqrt{-t-p - \left(2\frac{q}{\sqrt{t-p}} \right)}}{2}- \frac{A}{4}\\
x_4&=\frac{\sqrt{t-p} - \sqrt{-t-p - \left(2\frac{q}{\sqrt{t-p}} \right)}}{2}- \frac{A}{4}
\end{aligned}
]</div>


### 判別式
3次以下の多項式に判別式があったように、4次方程式にも判別式があります。一見すると、最終的に求められた公式の2，3次と同じようにルートの中身[tex:\left(-t-p \pm \left(2\frac{q}{\sqrt{t-p}} \right)\right)]が使えそうに見えますが、この中のプラスマイナスは2組の2次方程式の解の公式毎に独立しています。つまり、2次方程式毎の判別式としてしか使えません。

[Wikipediaによると](https://ja.wikipedia.org/wiki/判別式)4次方程式の判別式は以下のようになります（[tex:a=1,b=0]としてここで求めた式に合わせて係数も置き換えています）。

<div align="center">[tex:
\begin{aligned}
D&=256r^ 3-128p^ 2r^ 2+144pq^ 2r-27r^ 4+16p^ 4r-4q^3r^2
\end{aligned}
]</div>

この[tex:D]は3次以下の時と同じように

- [tex:D=0] : 少なくとも二つの解が重複。それが複素数ならば、その共役も重複。
- [tex:D \gt 0] : 2組の互いに共役な複素数解
- [tex:D \lt 0] : 2つの実数解と互いに共役な複素数解

となります。

解の様子がどうなるかは分かりますが、この式はここで求めた解の公式（の各項）との関連が見られず、計算したとしても使いまわせないので今回の実装においては使用しないことにします。

### 一部の係数が0になる場合の変形

#### 複二次式
[tex:ax^ 4+bx^ 3+cx^ 2+dx+e]という形の4次方程式に対して、奇数次の項の係数[tex:b,d]が0になっている形の4次方程式[tex:ax^ 4+cx^ 2+e]を複二次式と呼びます。

複二次式は[tex:x^ 2]についての二次方程式と見ることで簡単に解くことができます。  
[tex:y = x^ 2]とおいてやると[tex:ay^ 2+cy+e]となるので、二次方程式の解の公式を適用してやると

<div align="center">[tex:
\begin{aligned}
y&=\frac{-c \pm \sqrt{c^ 2 -4ae} }{2a}\\
x&=\pm\sqrt{y}\\
&=\pm\sqrt{\frac{-c \pm \sqrt{c^ 2 -4ae} }{2a}}
\end{aligned}
]</div>

この様に、簡単に解を求めることができます。

求めた[tex:y^ 4+py^ 2+qy+r=0]の場合は、[tex:q=0]のときに[tex:y^ 4+py^ 2+r=0]となって、[tex:y = z^ 2]と置いてやれば同じように、[tex:\sqrt{\frac{-p \pm \sqrt{p^ 2 -4r} }{2}}]と求めることができます。

4次方程式には4つの解がありますが、複二次式の場合は二次方程式を解いた解が2つ出てきて、最後に平方根を求めるところでそれぞれ最大2つの解が得られます。


#### [tex:r=0]の場合
[tex:y^ 4+py^ 2+qy+r=0]の切片[tex:r=0]の場合も式を簡単にすることができます。

<div align="center">[tex:
\begin{aligned}
y^ 4+py^ 2+qy+0&=y^ 4+py^ 2+qy\\
&=y(y^ 3+py+q)
\end{aligned}
]</div>

となり、解は[tex:y=0]と[tex:y^ 3+py+q]の3つの解となります。

### C++実装
さて、必要な公式などは一通りそろったのでC++コードにコピペしていきます。公式通り順番にやっていきます。

3次式の時と同じく、値型はテンプレートにしておきます。相変わらず構造化束縛を使用しているのでC++17未満のコンパイラではstd::tieを使う等してください。

まずstep1、4次の係数を1にするところです。
``` cpp
template<typename T>
auto SolveQuarticEquation(const T a, const T b, const T c,const T d, const T e) -> std::tuple<std::complex<T>, std::complex<T>, std::complex<T>, std::complex<T>> {
	if (a == T(0.0)) {
		constexpr std::tuple<std::complex<T>> zero{};

		auto x = SolveCubicEquation(b, c, d, e);
    	return std::tuple_cat(std::move(x), zero);
	}
	else if (b == T(0.0) && d == T(0.0)) {
		//複二次式
		return BiquadraticEquation(a, c, e);
	}

	return SolveQuarticEquation(b / a, c / a, d / a, e / a);
}
```

普通に各係数を割り算をするだけ。もし4次の係数がゼロなら三次方程式として、奇数次係数がゼロなら複二次式として解いてやります。

``` cpp
template<typename T>
auto SolveQuarticEquation(const T A, const T B, const T C, const T D) -> std::tuple<std::complex<T>, std::complex<T>, std::complex<T>, std::complex<T>> {
	//(A/4)
	const auto A_d4 = A / T(4.0);
	//(A/4)^2
	const auto A_d4_sq = A_d4 * A_d4;
	//(A/4)^3
	const auto A_d4_cu = A_d4 * A_d4_sq;

	const auto p = T(-6.0) * A_d4_sq + B;
	const auto q = T(2.0) * (T(4.0) * A_d4_cu - B * A_d4) + C;
	const auto r = (T(-3.0) * A_d4_cu - C) * A_d4 + B * A_d4_sq + D;

	auto [y1, y2, y3, y4] = SolveQuarticEquation(p, q, r);

	return std::make_tuple(y1 - A_d4, y2 - A_d4, y3 - A_d4, y4 - A_d4);
}
```

step2、チルンハウス変換部分。[tex:p,q,r]を求めて、次のステップに渡します。帰ってきた各[tex:y]から[tex:\frac{A}{4}]を引いてチルンハウス変換を戻し、最終的な解[tex:x]として返します。

``` cpp
template<typename T>
auto SolveQuarticEquation(const T p, const T q, const T r) -> std::tuple<std::complex<T>, std::complex<T>, std::complex<T>, std::complex<T>> {
	if (q == T(0.0)) {
		//複二次式
		return BiquadraticEquation(T(1.0), p, r);
	}
	else if (r == T(0.0)) {
		constexpr std::tuple<std::complex<T>> zero{};

		auto x = SolveCubicEquation(p, q);

		return std::tuple_cat(std::move(x), zero);
	}

	//tの式の各係数を求める
	//t^3 -pt^2-4rt+(4pr-q^2) = 0

	const auto r4 = T(4.0)*r;
	const auto c =r4*p - q * q;

	std::complex<T> t_c{};

	//tのうち実数のものを選択
	std::tie(t_c, std::ignore, std::ignore) = SolveCubicEquation(-p, -r4, c);
		
	const auto t = t_c.real();

	//t-p
	const auto t_p = t - p;

	if (T(0.0) <= t_p) {
		//m = √(t-p)
		const auto m = std::sqrt(t_p);

		//n = q/2√(t-p)
		const auto n = q / (T(2.0)*m);

		//t/2
		const auto half_t = T(0.5)*t;

		//2つの二次式を解く！
		auto&& y_12 = SolveQuadraticEquation(T(1.0),  m, half_t - n);
		auto&& y_34 = SolveQuadraticEquation(T(1.0), -m, half_t + n);

		return std::tuple_cat(std::move(y_12), std::move(y_34));
	}
	else {
		//負の数の平方根を求めなければならない場合

		//m = √(t-p)
		const std::complex<T> m = { 0.0, std::sqrt(-t_p) };

		//n = q/2√(t-p)
		const auto n = q / (T(2.0)*m);

		//t/2
		const auto half_t = T(0.5)*t;

		//複素係数二次方程式
		auto&& y_12 = SolveQuadraticEquation({ T(1.0) },  m, half_t - n);
		auto&& y_34 = SolveQuadraticEquation({ T(1.0) }, -m, half_t + n);

		return std::tuple_cat(std::move(y_12), std::move(y_34));
	}
}
```

最後のstep、二つの二次方程式の解を求めることで各[tex:y]の値を求めます。ここでも[tex:q=0]の場合に複二次式として、[tex:r=0]の場合には3次方程式として、それぞれ飛ばします。

[tex:t]を3次方程式から求めますが、3次方程式は必ず一つは実数解があるのでそれを使うようにします（[前回実装](https://onihusube.hatenablog.com/entry/2018/10/08/140426)の通りなら、3次方程式の一つ目の解が実数解になるようになっています）。  
しかしそれでも、[tex:\sqrt{t-p}]の中身が負になってしまうと結局複素数が出て来てしまうのでその場合は複素数係数の2次方程式を解くようにします（その選択はオーバーロードにやってもらっています）。

``` cpp
template<typename T>
auto BiquadraticEquation(const T a, const T c, const T e) -> std::tuple<std::complex<T>, std::complex<T>, std::complex<T>, std::complex<T>> {
	auto [x1, x2] = SolveQuadraticEquation(a, c, e);

	auto sqrt_x1 = std::sqrt(x1);
	auto sqrt_x2 = std::sqrt(x2);

	return std::make_tuple(sqrt_x1, -sqrt_x1, sqrt_x2, -sqrt_x2);
}
```

最後に、複二次式を解く部分。こちらも2次方程式求解部分に投げます。帰ってきた値の符号を反転させたものが残りの解です。

3次も4次も主に引算の桁落ちについて慎重な考慮が必要ですが、それはまたの機会に・・・

コードとテスト実行  
[[Wandbox]三へ( へ՞ਊ ՞)へ ﾊｯﾊｯ](https://wandbox.org/permlink/S6KTktxsuhhgUjbH)

解の検証  
[四次方程式の解 - 高精度計算サイト](https://keisan.casio.jp/exec/system/1177976627)

Githubにも上げておきます（ヘッダ分けしてあったり一部異なっています、後随時更新されると思います）  
[QuarticEquation.hpp](https://github.com/onihusube/AlgebraicEequationSolver/blob/master/AlgebraicEequationSolver/Include/QuarticEquation.hpp)


### 参考文献
- [四次方程式 - Wikipedia](https://ja.wikipedia.org/wiki/%E5%9B%9B%E6%AC%A1%E6%96%B9%E7%A8%8B%E5%BC%8F)
- [四次方程式の解法 - 雨男の巣窟](https://blog.rainyman.jp/nest/?p=321)
- [４次方程式解の公式 - Fukusukeの数学めも](https://mathsuke.jp/ferrari_formula/)
- [四次方程式](http://www.geocities.co.jp/HeartLand-Himawari/3613/engine/mp0204.html)

[この記事のmarkdawnソース](https://github.com/onihusube/blog/blob/master/2019/20190126_quartic_equation.md)