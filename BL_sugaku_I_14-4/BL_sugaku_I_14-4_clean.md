ベーシックレベル数学Ⅰ 第 14 講 PART4

# PART4 空間図形への応用

---

## 要点① 直方体の切り口の面積

空間図形に含まれる三角形に注目し，長さや面積を求める。

### 例
右図のような直方体 ABCD-EFGH がある。
$\triangle ACF$ の面積を求める。

[図の説明: 直方体 ABCD-EFGH において、縦 $AD = 3\sqrt{3}$、横 $AB = 3$、高さ $AE = 4$ である。頂点 A, C, F を結んだ三角形 ACF が斜めの切り口として描かれている。]

$\triangle ABC$，$\triangle ABF$，$\triangle BCF$ のそれぞれにおいて三平方の定理より
$$AC = \sqrt{3^2 + (3\sqrt{3})^2} = \sqrt{36} = 6$$
$$AF = \sqrt{4^2 + (3\sqrt{3})^2} = \sqrt{43}$$
$$CF = \sqrt{3^2 + 4^2} = \sqrt{25} = 5$$

$\triangle ACF$ で余弦定理より
$$\cos \angle ACF = \frac{6^2 + 5^2 - (\sqrt{43})^2}{2 \cdot 6 \cdot 5} = \frac{18}{2 \cdot 6 \cdot 5} = \frac{3}{10}$$

$$\sin \angle ACF = \sqrt{1 - \cos^2 \angle ACF} = \sqrt{1 - \left(\frac{3}{10}\right)^2} = \frac{\sqrt{91}}{10}$$

よって 
$$\triangle ACF = \frac{1}{2} \cdot AC \cdot CF \cdot \sin \angle ACF = \frac{1}{2} \cdot 6 \cdot 5 \cdot \frac{\sqrt{91}}{10} = \frac{3\sqrt{91}}{2}$$

---

## 要点② 空間の測量

三角比を利用して，直接測ることが難しい長さを求めることができる。

### 例
校庭にポール PH が地面に垂直に立っている。ポールより離れた 2 地点 A，B とポールの先端 P について，$AB = 20 \text{ (m)}$，$\angle PAB = 60^\circ$，$\angle PBA = 75^\circ$，$\angle PBH = 45^\circ$ であった。ポールの高さ PH を求めたい。

[図の説明: 地面に垂直に立つポール PH（H は地面の足、P は先端）と、地面上の 2 地点 A, B を表す図。$AB = 20\text{m}$、$\angle PAB = 60^\circ$、$\angle PBA = 75^\circ$、$\angle PBH = 45^\circ$ と示されている。]

$\triangle PAB$ において
$$\angle APB = 180^\circ - (60^\circ + 75^\circ) = 45^\circ$$

正弦定理より
$$\frac{BP}{\sin 60^\circ} = \frac{20}{\sin 45^\circ}$$

$$BP = 20 \div \sin 45^\circ \times \sin 60^\circ = 20 \cdot \sqrt{2} \cdot \frac{\sqrt{3}}{2} = 10\sqrt{6}$$

よって直角三角形 PBH において
$$PH = BP \sin 45^\circ = 10\sqrt{6} \cdot \frac{1}{\sqrt{2}} = 10\sqrt{3} \text{ (m)}$$

---

## 演習問題

### 4
**(1)** 右の図のように，$AB = 4\sqrt{3}$，$AD = 2\sqrt{5}$，$AE = 4$ である直方体 ABCD-EFGH がある。$\triangle AFC$ の面積を求めよ。

[図の説明: 直方体 ABCD-EFGH において、$AB = 4\sqrt{3}$、$AD = 2\sqrt{5}$、$AE = 4$。頂点 A, F, C を結んだ三角形 AFC が描かれている。]

**(2)** 右の図において，木の周りが柵で囲まれている。木より離れた 2 地点 A，B と木の先端 C について，$AB = 10 \text{ (m)}$，$\angle CAH = 30^\circ$，$\angle HAB = 15^\circ$，$\angle HBA = 30^\circ$ であった。このとき木の高さ CH を求めよ。

[図の説明: 地面に垂直に立つ木 CH（H は地面の足、C は先端）と、地面上の 2 地点 A, B を表す図。$AB = 10\text{m}$、$\angle CAH = 30^\circ$、$\angle HAB = 15^\circ$、$\angle HBA = 30^\circ$ と示されている。]

---

### Point Pickup
**空間図形への応用**
空間図形に含まれる三角形に注目し，辺の長さや面積を求める。

---
---

# 第 14 講 PART4 確認問題

## 1
次の図のように，$AB = \sqrt{3}$，$AD = 1$，$AE = \sqrt{2}$ である直方体 ABCD-EFGH がある。

[図の説明: 直方体 ABCD-EFGH において、$AB = \sqrt{3}$、$AD = 1$、$AE = \sqrt{2}$。頂点 A, C, F を結んだ三角形 AFC があり、$\angle ACF = \theta$ と示されている。]

$\angle ACF = \theta$ とすると，$\cos \theta = \sqrt{\frac{\text{[ ア ]}}{\text{[ イ ]}}}$ であるから，
$\triangle AFC$ の面積は $\frac{\sqrt{\text{[ ウエ ]}}}{\text{[ オ ]}}$ である。

---

## 2
次の図のように，地面に垂直に立つ木 PQ と，地面の点 A，B があり，$AB = 6 \text{ (m)}$，$\angle PAQ = 60^\circ$，$\angle QAB = 75^\circ$，$\angle QBA = 45^\circ$ である。

[図の説明: 地面に垂直に立つ木 PQ（Q は地面の足、P は先端）と、地面上の 2 地点 A, B。$AB = 6\text{m}$、$\angle PAQ = 60^\circ$、$\angle QAB = 75^\circ$、$\angle QBA = 45^\circ$ と示されている。]

このとき，木 PQ の高さは $\text{[ カ ]}\sqrt{\text{[ キ ]}} \text{ m}$ である。

---
---

# 解答・解説

## 演習問題 4 解答

**(1)** $\triangle ABC$，$\triangle ABF$，$\triangle BCF$ のそれぞれにおいて三平方の定理より
$$AC = \sqrt{(4\sqrt{3})^2 + (2\sqrt{5})^2} = 2\sqrt{17}$$
$$AF = \sqrt{(4\sqrt{3})^2 + 4^2} = 8$$
$$CF = \sqrt{(2\sqrt{5})^2 + 4^2} = 6$$

$\triangle AFC$ で余弦定理より
$$\cos \angle AFC = \frac{8^2 + 6^2 - (2\sqrt{17})^2}{2 \cdot 8 \cdot 6} = \frac{32}{2 \cdot 8 \cdot 6} = \frac{1}{3}$$

$$\sin \angle AFC = \sqrt{1 - \cos^2 \angle AFC} = \sqrt{1 - \left(\frac{1}{3}\right)^2} = \frac{2\sqrt{2}}{3}$$

よって 
$$\triangle AFC = \frac{1}{2} \cdot AF \cdot CF \cdot \sin \angle AFC = \frac{1}{2} \cdot 8 \cdot 6 \cdot \frac{2\sqrt{2}}{3} = 16\sqrt{2}$$

**(2)** $\triangle HAB$ において
$$\angle AHB = 180^\circ - (15^\circ + 30^\circ) = 135^\circ$$

正弦定理より
$$\frac{AH}{\sin 30^\circ} = \frac{10}{\sin 135^\circ}$$

$$AH = 10 \div \sin 135^\circ \times \sin 30^\circ = 10 \cdot \sqrt{2} \cdot \frac{1}{2} = 5\sqrt{2}$$

よって直角三角形 CAH において
$$CH = AH \tan 30^\circ = 5\sqrt{2} \cdot \frac{1}{\sqrt{3}} = \frac{5\sqrt{6}}{3} \text{ (m)}$$

---

## 第 14 講 PART4 確認問題 解答

### 1
**［正解］** ア：3，イ：6，ウエ：11，オ：2

**［解説］**
$\triangle ABC$，$\triangle ABF$，$\triangle BCF$ のそれぞれにおいて，三平方の定理より，
$$AC = \sqrt{(\sqrt{3})^2 + 1^2} = 2$$
$$AF = \sqrt{(\sqrt{3})^2 + (\sqrt{2})^2} = \sqrt{5}$$
$$CF = \sqrt{1^2 + (\sqrt{2})^2} = \sqrt{3}$$

[図の説明: 三角形 AFC の 3 辺の長さが $AC = 2$, $CF = \sqrt{3}$, $AF = \sqrt{5}$ であり、$\angle ACF = \theta$ と示された図。]

$\triangle AFC$ で余弦定理より，
$$\cos \theta = \frac{2^2 + (\sqrt{3})^2 - (\sqrt{5})^2}{2 \cdot 2 \cdot \sqrt{3}} = \frac{4 + 3 - 5}{4\sqrt{3}} = \frac{2}{4\sqrt{3}} = \frac{1}{2\sqrt{3}} = \frac{\sqrt{3}}{6}$$
（$\cos \theta = \sqrt{\frac{3}{36}} = \sqrt{\frac{3}{6}}$）

$$\sin^2 \theta = 1 - \cos^2 \theta = 1 - \left(\frac{\sqrt{3}}{6}\right)^2 = \frac{33}{36}$$

$\sin \theta > 0$ より，$\sin \theta = \sqrt{\frac{33}{36}} = \frac{\sqrt{33}}{6}$

よって，$\triangle AFC$ の面積は，
$$\triangle AFC = \frac{1}{2} \cdot 2 \cdot \sqrt{3} \cdot \frac{\sqrt{33}}{6} = \frac{\sqrt{11}}{2}$$

> **［A］** $\triangle AFC$ の 3 辺の長さを求める。  
> **［B］** $a^2 = b^2 + c^2 - 2bc \cos A \iff \cos A = \frac{b^2 + c^2 - a^2}{2bc}$  
> **［C］** $\triangle ABC$ の面積を $S$ とすると，$S = \frac{1}{2} bc \sin A$

---

### 2
**［正解］** カ：6，キ：2

**［解説］**
$\triangle QAB$ において，
$$\angle AQB = 180^\circ - (75^\circ + 45^\circ) = 60^\circ$$

[図の説明: 地面上の三角形 QAB において、$AB = 6\text{m}$、$\angle QAB = 75^\circ$、$\angle QBA = 45^\circ$、$\angle AQB = 60^\circ$ が示されている図。]

正弦定理より，
$$\frac{AQ}{\sin 45^\circ} = \frac{6}{\sin 60^\circ}$$

$$AQ = \frac{6}{\sin 60^\circ} \times \sin 45^\circ = 6 \times \frac{2}{\sqrt{3}} \times \frac{\sqrt{2}}{2} = 2\sqrt{6}$$

よって，直角三角形 PAQ において，
$$PQ = AQ \tan 60^\circ = 2\sqrt{6} \cdot \sqrt{3} = 6\sqrt{2}$$

> **［D］ 正弦定理**  
> $\triangle ABC$ の外接円の半径を $R$ とすると，$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R$  
> **［E］** 直角三角形において，$a = b \tan \theta$