ベーシックレベル数学Ⅰ 第 1 4 講 PART2

# PART2 三角形の内接円と面積

---

### 要点① 三角形の内接円と面積

三角形の 3 つの辺に接する円はただ 1 つに定まる。  
この円を，その三角形の「**内接円**」という。

$\triangle \mathrm{ABC}$ の内接円の中心を $\mathrm{I}$，半径を $r$ とすると，$\triangle \mathrm{ABC}$ は 3 つの三角形 $\triangle \mathrm{IBC}$，$\triangle \mathrm{ICA}$，$\triangle \mathrm{IAB}$ に分割することができ，$r$ は $\triangle \mathrm{IBC}$，$\triangle \mathrm{ICA}$，$\triangle \mathrm{IAB}$ の底辺をそれぞれ辺 $\mathrm{BC}$，辺 $\mathrm{CA}$，辺 $\mathrm{AB}$ としたときの高さである。

よって，$\triangle \mathrm{ABC}$ の面積 $S$ は
$$S = \triangle \mathrm{IBC} + \triangle \mathrm{ICA} + \triangle \mathrm{IAB}$$
$$= \frac{1}{2}ar + \frac{1}{2}br + \frac{1}{2}cr = \frac{1}{2}r(a+b+c)$$

[図の説明: 上から順に、1つ目は三角形ABC内に内接円(中心I, 半径r)が描かれ、辺BC=a, CA=b, AB=cとされている図。2つ目は中心Iから各頂点A, B, Cおよび各辺への垂線(長さr)が引かれ、3つの三角形IBC, ICA, IABに分割されている図。3つ目は内接円の各辺への垂線(半径r)と各辺a, b, cが示された図。]

以上より，次のことが成り立つ。

> **三角形の内接円と面積**  
> $\triangle \mathrm{ABC}$ の面積を $S$，内接円の半径を $r$ とすると  
> $$S = \frac{1}{2}r(a+b+c)$$

---

#### 例
$\triangle \mathrm{ABC}$ において，$a=4$，$b=5$，$c=6$ のとき，この三角形の内接円の半径 $r$ を求める。

余弦定理より
$$\cos A = \frac{5^2+6^2-4^2}{2 \cdot 5 \cdot 6} = \frac{45}{2 \cdot 5 \cdot 6} = \frac{3}{4}$$

$\sin A > 0$ より
$$\sin A = \sqrt{1-\cos^2 A} = \sqrt{1-\left(\frac{3}{4}\right)^2} = \frac{\sqrt{7}}{4}$$

$\triangle \mathrm{ABC}$ の面積を $S$ とすると
$$S = \frac{1}{2} \cdot 5 \cdot 6 \cdot \frac{\sqrt{7}}{4} = \frac{15\sqrt{7}}{4}$$

$S = \frac{1}{2}r(a+b+c)$ より
$$\frac{15\sqrt{7}}{4} = \frac{15}{2}r \quad \implies \quad r = \frac{\sqrt{7}}{2}$$

[図の説明: 辺の長さがAB=6, AC=5, BC=4の三角形ABCに内接円(半径r)が描かれている図。]

---

### Point Pickup

**2** $a=8$，$b=7$，$c=6$ である $\triangle \mathrm{ABC}$ の内接円の半径 $r$ を求めよ。

> **三角形の面積**  
> $\triangle \mathrm{ABC}$ の面積を $S$，内接円の半径を $r$ とすると  
> $$S = \frac{1}{2}r(a+b+c)$$

[図の説明: 三角形ABC内に中心Iの内接円が接しており、中心Iから各辺への垂線(半径r)が下ろされ、辺BC=a, CA=b, AB=cと示されている図。]

---

### 第 14 講 PART2 確認問題

**1** $\triangle \mathrm{ABC}$ において，$a=7$，$b=3$，$c=8$ である。  
この三角形の内接円の半径 $r$ を求める。

余弦定理により，
$$\cos A = \frac{\text{[ ア ]}}{\text{[ イ ]}}$$
であるから，
$$A = \text{[ ウエ ]}^\circ$$

$\triangle \mathrm{ABC}$ の面積を $S$ とすると，
$$S = \text{[ オ ]}\sqrt{\text{[ カ ]}}$$

以上により，$r$ を求めると，
$$r = \frac{\text{[ キ ]}\sqrt{\text{[ ク ]}}}{\text{[ ケ ]}}$$

---

### 解答・解説

#### 2 の解答・解説

$a=8$，$b=7$，$c=6$ である $\triangle \mathrm{ABC}$ の内接円の半径 $r$ を求めよ。

**［解答］**  
余弦定理より
$$\cos A = \frac{7^2+6^2-8^2}{2 \cdot 7 \cdot 6} = \frac{21}{2 \cdot 7 \cdot 6} = \frac{1}{4}$$

$\sin A > 0$ より
$$\sin A = \sqrt{1-\cos^2 A} = \sqrt{1-\left(\frac{1}{4}\right)^2} = \frac{\sqrt{15}}{4}$$

$\triangle \mathrm{ABC}$ の面積を $S$ とすると
$$S = \frac{1}{2} \cdot 7 \cdot 6 \cdot \frac{\sqrt{15}}{4} = \frac{21\sqrt{15}}{4}$$

$S = \frac{1}{2}r(a+b+c)$ より
$$\frac{21\sqrt{15}}{4} = \frac{1}{2}r(8+7+6)$$
$$\frac{21}{2}r = \frac{21\sqrt{15}}{4} \quad \text{よって} \quad r = \frac{\sqrt{15}}{2}$$

[図の説明: 辺の長さがAB=6, AC=7, BC=8の三角形ABCと、その内接円(半径r)が描かれている図。]

---

#### 第 14 講 PART2 確認問題 解答

**1［正解］**  
ア：1，イ：2，ウエ：60，オ：6，カ：3，キ：2，ク：3，ケ：3

**［解説］**  
[図の説明: 辺の長さがAB=8, AC=3, BC=7の三角形ABCと、その内接円が描かれている図。]

余弦定理より，［A］
$$\cos A = \frac{3^2+8^2-7^2}{2 \cdot 3 \cdot 8} = \frac{9+64-49}{2 \cdot 3 \cdot 8} = \frac{24}{2 \cdot 3 \cdot 8} = \frac{1}{2}$$
よって，$A = 60^\circ$

$\triangle \mathrm{ABC}$ の面積を $S$ とすると，［B］
$$S = \frac{1}{2} \cdot 3 \cdot 8 \sin 60^\circ = \frac{1}{2} \cdot 3 \cdot 8 \cdot \frac{\sqrt{3}}{2} = 6\sqrt{3}$$

$S = \frac{1}{2}r(a+b+c)$ より，［C］
$$6\sqrt{3} = \frac{1}{2}r(7+3+8)$$
$$9r = 6\sqrt{3}$$
$$r = \frac{2\sqrt{3}}{3}$$

---

* **［A］** $a^2 = b^2 + c^2 - 2bc \cos A \iff \cos A = \frac{b^2+c^2-a^2}{2bc}$
* **［B］** $\triangle \mathrm{ABC}$ の面積を $S$ とすると，$S = \frac{1}{2}bc \sin A$
* **［C］** 三角形の内接円と面積：$\triangle \mathrm{ABC}$ の面積を $S$，内接円の半径を $r$ とすると，$S = \frac{1}{2}r(a+b+c)$

[図の説明: 三角形ABCとその内接円(中心I, 半径r)、辺の長さa, b, cを示す参考図。]