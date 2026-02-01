# ［C++］Eigen::Transformの分かりづらいところ

はまったことのメモです。

[:contents]

### `Eigen::Transform`

`Eigen::Transform`はアフィン変換を表現するクラス型です。

```cpp
#include <Eigen/Core>
#include <Eigen/Geometry>

int main() {
  // 平行移動を表すアフィン変換を構成
  Eigen::Translation3d tr{10.0, 5.0, 0.0};
  Eigen::Transform3d transform{tr};

  Eigen::Vector3d vec{1.0, 2.0, 3.0};
  // 平行移動を適用
  Eigen::Vector3d res = transform * vec;
}
```

その他回転や拡大縮小などを行えます。ベクトルとの`*`での積の際も、同次行列を考慮して次元を足して1入れてみたいなことを内部で自動でやってくれます。

ただ、これだけならまだ普通に`Eigen::Matrix`を用意してやった方が良い気持ちが大きいですが、このクラスの良いところは多段のアフィン変換の合成をサポートしているところです。

合成は二項`*`あるいは`*=`によって行えます。

```cpp
#include <numbers>

#include <Eigen/Core>
#include <Eigen/Geometry>

int main() {
  // 3次元座標変換を表すアフィン変換を構成
  // 例えば、ローカル座標系からグローバル座標系への変換
  Eigen::Translation3d tr{10.0, 5.0, 0.0};
  Eigen::AngleAxisd rot{std::numbers::pi, Eigen::Vector3d::UnitZ()};
  Eigen::Transform3d transform{tr};
  transform *= rot;

  Eigen::Vector3d vec{1.0, 2.0, 3.0};
  // 座標変換を適用
  Eigen::Vector3d res = transform * vec;
}
```

`*`による合成はそのままアフィン変換行列の積と思えば良く、アフィン変換行列`T1, T2, T3`があり`T1 -> T2 -> T3`の順で変換を適用したい場合、そのまま`T3 * T2 * T1`のように書くことができます。つまり`*`の右側にあるものほど先に適用されます。

ただし、Eigenの場合`*`の両辺はかなり柔軟で、アフィン変換行列そのものではなくアフィン変換を表すものを直接指定することができます（上記例だと`Eigen::Translation3d`と`Eigen::AngleAxisd`）。`Eigen::Transform`およびこれらの型でオーバロードされた`*`演算子内で行列に変換して積を取った時と同等の事が行われています。

`Eigen::Transform`そのものへの変換の渡し方/適用方法も柔軟になっています。

```cpp
// *してから渡す
Eigen::Transform3d transform{tr * rot};

// *したものを代入
Eigen::Transform3d transform{};
transform = tr * rot;

// 2つのTransformの合成
Eigen::Transform3d t_rot{rot};
Eigen::Transform3d t_translate{tr};
Eigen::Transform3d transform = t_translate * t_rot;
```

この例はすべて一個前の例の`transform`と同じ変換を表すはずです。

### メンバ関数によるアフィン変換のセット・合成

`Eigen::Transform`へのアフィン変換の適用方法にはメンバ関数も利用できます。

```cpp
Eigen::Transform3d transform = Eigen::Affine3d::Identity();
transform.translate(tr);
transform.rotate(rot);
```

こちらは`*`よりも起きていることが分かりやすいのでより説明的かもしれません。

ただ、ここで問題になるのはこのように1つの`Eigen::Transform`にメンバ関数で変換を適用していった際の変換の適用順が分かりづらくなることです。この例の`transform`の場合、`transform * vec`という風に変換を適用した時、`tr * rot * vec`になるのか`rot * tr * vec`になるのかわかりづらくなります。別の言い方をすると、メンバ関数で変換をセットしていくと、セットした変換がする前の変換の左右どちらに適用されるか分かりづらくなります。

答えは、後にセットしたものがより右側に適用される（メンバ関数の呼び出し順に`*`で合成した時と同じ）です。上記のメンバ関数の例は前節での`*=`の例と同じ変換を表し、`rot -> tr`の順に変換が適用されます（`tr * rot * vec`）。

座標変換が典型ですが、複数の変換を合成したアフィン変換ではその順番が重要になるため、注意が必要になります。

```cpp
// T1 -> T2 -> T3 -> T4の順で変換を行うアフィン変換を構成したい
Eigen::Translation3d T1 = ...;
Eigen::Matrix3d T2 = ...;
auto T3 = Eigen::Scaling(...);
Eigen::Translation3d T4 = ...;

// *による合成
Eigen::Transform3d transform1{};
transform = T4 * T3 * T2 * T1;

// メンバ関数による合成
Eigen::Transform3d transform2 = Eigen::Affine3d::Identity();
transform.translate(T4);
transform.scale(T3);
transform.rotate(T2);
transform.translate(T1);
```

この`transform1`と`transform2`は同じ変換を表します。

私はこれにはまって時間を溶かし同僚に迷惑をかけたわけですが、なんかこうして書き起こしてみると全然罠でもなく自明ですね・・・

#### メンバ関数で適用順を制御する

メンバ関数による変換の合成時にも何らかの都合で右に追加するのではなく左に追加したいことがあるかもしれません。その場合は、メンバ関数名の先頭に`pre`を付けたメンバ関数によってそれを行えます。

```cpp
// T1 -> T2 -> T3 -> T4の順で変換を行うアフィン変換を構成
Eigen::Transform3d transform3{T2};
transform.translate(T1);    // 右に適用
transform.prescale(T3);     // 左に適用
transform.pretranslate(T4); // 左に適用
```

`.rotate()`に対応するのは`.prerotate()`です。

この`transform3`は`transform1`、`transform2`と同じ変換を表します。が、余計にわかりづらくなるのであまりやらない方が良さそうに思えます。

### デフォルト構築

これは書いてて気づいたおまけです。

ここまでの例では黙って回避していましたが`Eigen::Transform`をデフォルト構築すると恒等変換ではなく無の変換が構成されます。これはおそらく内部の変換行列の係数が不定値を取るため、これに対して変換を適用してもおかしな結果を招くでしょう。

```cpp
Eigen::Transform3d transform{};
transform *= T4;  // 意図通りの変換が構成されない
```

デフォルト構築はクラスメンバにしたときにそのクラスのデフォルトコンストラクタを無効化しないために用意されているだけだと思われます。デフォルト構築した後は代入演算子（`=`）によって上書きするか、そもそも`Eigen::Affine3d::Identity()`などによって明示的に恒等変換で初期化する必要があります。

```cpp
Eigen::Transform3d transform{};
transform = T4;  // T4の変換と同等の変換を構成
```
```cpp
// 恒等変換を構成
Eigen::Transform3d transform = Eigen::Affine3d::Identity();
```

### 参考文献

- [アフィン変換（平行移動、拡大縮小、回転、スキュー行列） | イメージングソリューション](https://imagingsolution.net/imaging/affine-transformation/)
- [Eigen: Space transformations](https://libeigen.gitlab.io/eigen/docs-nightly/group__TutorialGeometry.html)
- [Eigen: Eigen::Transform< Scalar_, Dim_, Mode_, Options_ > Class Template Reference](https://libeigen.gitlab.io/eigen/docs-nightly/classEigen_1_1Transform.html)