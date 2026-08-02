ベーシックレベル数学Ⅰ

# 第 14 講 図形の計量
## PART1 三角形の面積

---

### 要点 1 三角形の高さと面積

三角比を用いて，三角形の面積を求める。  
$\triangle \mathrm{ABC}$ において，辺 $\mathrm{AB}$ を底辺としたときの高さを $h$ とする。

(i) $A$ が鋭角のとき  
$\sin A = \frac{h}{b}$ より $h = b \sin A$  
[図の説明: $\triangle \mathrm{ABC}$ で, 角Aが鋭角の図。頂点Cから辺AB（長さc）に下ろした垂線の長さがh, 辺ACの長さがb, 角Aが図示されている。]

(ii) $A$ が鈍角のとき  
$\sin (180^\circ - A) = \frac{h}{b}$ より  
$h = b \sin (180^\circ - A) = b \sin A$  
[図の説明: $\triangle \mathrm{ABC}$ で, 角Aが鈍角の図。辺BAをAの方向に延長した直線へ頂点Cから下ろした垂線の長さがh, 辺ACの長さがb, 角Aの外角が $180^\circ - A$ である。]

(i), (ii)より $h = b \sin A$ である。  
また，$A$ が直角のときも $h = b = b \cdot 1 = b \sin 90^\circ = b \sin A$ である。

したがって，$\triangle \mathrm{ABC}$ の面積 $S$ は
$$S = \frac{1}{2} c h = \frac{1}{2} c \cdot b \sin A = \frac{1}{2} b c \sin A$$

よって，$\triangle \mathrm{ABC}$ の面積 $S$ は，2 辺の長さ $b$, $c$ とその間の角の正弦の値 $\sin A$ で表される。  
以上より，次のことが成り立つ。

> **三角形の面積**  
> $\triangle \mathrm{ABC}$ の面積を $S$ とすると  
> $$S = \frac{1}{2} b c \sin A = \frac{1}{2} c a \sin B = \frac{1}{2} a b \sin C$$  
> [図の説明: $\triangle \mathrm{ABC}$。辺BC=a, CA=b, AB=cと角Aが示されている。]

#### 例
$\triangle \mathrm{ABC}$ において，$b=4$，$c=5$，$A=30^\circ$ のとき，$\triangle \mathrm{ABC}$ の面積 $S$ を求める。

$$S = \frac{1}{2} b c \sin A = \frac{1}{2} \cdot 4 \cdot 5 \cdot \sin 30^\circ = \frac{1}{2} \cdot 4 \cdot 5 \cdot \frac{1}{2} = 5$$

[図の説明: $\triangle \mathrm{ABC}$ で, 辺AC=4, 辺AB=5, 角A=30°の図。]

---

### 要点 2 3 辺の長さから三角形の面積を求める

余弦定理を利用して，3 辺の長さが与えられた三角形の面積を求める。

#### 例
$a=7$，$b=5$，$c=8$ である $\triangle \mathrm{ABC}$ の面積 $S$ を求める。

余弦定理より
$$\cos A = \frac{5^2 + 8^2 - 7^2}{2 \cdot 5 \cdot 8} = \frac{40}{2 \cdot 5 \cdot 8} = \frac{1}{2} \quad A = 60^\circ$$

よって 
$$S = \frac{1}{2} b c \sin A = \frac{1}{2} \cdot 5 \cdot 8 \cdot \sin 60^\circ = \frac{1}{2} \cdot 5 \cdot 8 \cdot \frac{\sqrt{3}}{2} = 10\sqrt{3}$$

※ $\cos A = \frac{1}{2}$ より，三角比の相互関係 $\sin^2 A + \cos^2 A = 1$ から
$$\sin^2 A = 1 - \cos^2 A = 1 - \left(\frac{1}{2}\right)^2 = \frac{3}{4}$$

$\sin A > 0$ より $\sin A = \frac{\sqrt{3}}{2}$

よって 
$$S = \frac{1}{2} b c \sin A = \frac{1}{2} \cdot 5 \cdot 8 \cdot \frac{\sqrt{3}}{2} = 10\sqrt{3}$$

[図の説明: 辺の長さが5 (AC), 7 (BC), 8 (AB) である $\triangle \mathrm{ABC}$。角Aに角のマークがついている。]

---

### 問題 1
次の $\triangle \mathrm{ABC}$ の面積 $S$ を求めよ。
(1) $b=4$，$c=7$，$A=60^\circ$  
(2) $a=5$，$b=3$，$C=135^\circ$  
(3) $c=8$，$a=6$，$\sin B = \frac{\sqrt{7}}{4}$  
(4) $a=\sqrt{13}$，$b=2$，$c=\sqrt{3}$

---

### Point Pickup

> **三角形の面積**  
> $\triangle \mathrm{ABC}$ の面積を $S$ とすると  
> $$S = \frac{1}{2} b c \sin A = \frac{1}{2} c a \sin B = \frac{1}{2} a b \sin C$$  
> [図の説明: $\triangle \mathrm{ABC}$。辺の長さ $a, b, c$ と角 $A$ が示されている図。]  
> 2 辺とその間の角（またはその間の角の正弦の値）が与えられた場合は，この公式で面積を求めることができる。

3 辺の長さが与えられたときは，以下の手順で三角形の面積を求める。  
① 余弦定理より $\cos A$ の値を求める。  
② $\cos A$ から角度 $A$ が求められる場合は求める。  
   角度 $A$ が求められない場合は，三角比の相互関係 $\sin^2 A + \cos^2 A = 1$ を用いて $\sin A$ の値を求める。  
③ 公式を用いて面積を求める。

---

## 第 14 講 PART1 確認問題

### 1
$\triangle \mathrm{ABC}$ において，$b=3$，$c=4$，$A=60^\circ$ のとき，面積は [ ア ]$\sqrt{[ イ ]}$ である。

### 2
$\triangle \mathrm{ABC}$ において，$a=4$，$b=3\sqrt{2}$，$C=45^\circ$ のとき，面積は [ ウ ] である。

### 3
$\triangle \mathrm{ABC}$ において，$c=5$，$a=3$，$\sin B = \frac{2}{3}$ のとき，面積は [ エ ] である。

### 4
$\triangle \mathrm{ABC}$ において，$a=4$，$b=3$，$c=2$ のとき，  
$\cos A = - \frac{[ オ ]}{[ カ ]}$，$\sin A = \frac{\sqrt{[ キ ][ ク ]}}{[ ケ ]}$ であるから，面積は $\frac{[ コ ]\sqrt{[ サ ][ シ ]}}{[ ス ]}$ である。

---

## 解答

### 1 次の $\triangle \mathrm{ABC}$ の面積 $S$ を求めよ。
(1) $b=4, c=7, A=60^\circ$  
(2) $a=5, b=3, C=135^\circ$  
(3) $c=8, a=6, \sin B = \frac{\sqrt{7}}{4}$  
(4) $a=\sqrt{13}, b=2, c=\sqrt{3}$

#### ［解答］
(1) $S = \frac{1}{2} b c \sin A = \frac{1}{2} \cdot 4 \cdot 7 \cdot \sin 60^\circ = \frac{1}{2} \cdot 4 \cdot 7 \cdot \frac{\sqrt{3}}{2} = 7\sqrt{3}$

(2) $S = \frac{1}{2} a b \sin C = \frac{1}{2} \cdot 5 \cdot 3 \cdot \sin 135^\circ = \frac{1}{2} \cdot 5 \cdot 3 \cdot \frac{1}{\sqrt{2}} = \frac{15\sqrt{2}}{4}$

(3) $S = \frac{1}{2} c a \sin B = \frac{1}{2} \cdot 8 \cdot 6 \cdot \frac{\sqrt{7}}{4} = 6\sqrt{7}$

(4) 余弦定理より
$$\cos A = \frac{2^2 + (\sqrt{3})^2 - (\sqrt{13})^2}{2 \cdot 2 \cdot \sqrt{3}} = \frac{4 + 3 - 13}{2 \cdot 2 \cdot \sqrt{3}} = \frac{-6}{2 \cdot 2 \cdot \sqrt{3}} = -\frac{\sqrt{3}}{2}$$
$$A = 150^\circ$$
よって 
$$S = \frac{1}{2} b c \sin A = \frac{1}{2} \cdot 2 \cdot \sqrt{3} \cdot \sin 150^\circ = \frac{1}{2} \cdot 2 \cdot \sqrt{3} \cdot \frac{1}{2} = \frac{\sqrt{3}}{2}$$

---

## 第 14 講 PART1 確認問題 解答

### 1
［正解］ ア：3，イ：3

［解説］  
$\triangle \mathrm{ABC}$ の面積を $S$ とすると，
$$S = \frac{1}{2} b c \sin A$$
$$= \frac{1}{2} \cdot 3 \cdot 4 \sin 60^\circ$$
$$= \frac{1}{2} \cdot 3 \cdot 4 \cdot \frac{\sqrt{3}}{2} = 3\sqrt{3}$$

[図の説明: $\triangle \mathrm{ABC}$。辺AC=3, 辺AB=4, 角A=60°。]  
※ ［A］$\triangle \mathrm{ABC}$ の面積を $S$ とすると，$S = \frac{1}{2} b c \sin A = \frac{1}{2} c a \sin B = \frac{1}{2} a b \sin C$

### 2
［正解］ ウ：6

［解説］  
$$S = \frac{1}{2} a b \sin C$$
$$= \frac{1}{2} \cdot 4 \cdot 3\sqrt{2} \sin 45^\circ$$
$$= \frac{1}{2} \cdot 4 \cdot 3\sqrt{2} \cdot \frac{1}{\sqrt{2}} = 6$$

[図の説明: $\triangle \mathrm{ABC}$。辺BC=4, 辺AC=$3\sqrt{2}$, 角C=45°。]  
※ ［B］2 辺とその間の角が与えられた場合，公式で面積を求められる。 $S = \frac{1}{2} a b \sin C$

### 3
［正解］ エ：5

［解説］  
$$S = \frac{1}{2} c a \sin B$$
$$= \frac{1}{2} \cdot 5 \cdot 3 \cdot \frac{2}{3}$$
$$= 5$$

[図の説明: $\triangle \mathrm{ABC}$。辺AB=5, 辺BC=3, 角Bが示されている。]  
※ ［C］2 辺とその間の角（またはその間の角の正弦の値）が与えられた場合，公式で面積を求められる。 $S = \frac{1}{2} c a \sin B$

### 4
［正解］ オ：1，カ：4，キク：15，ケ：4，コ：3，サシ：15，ス：4

［解説］  
[図の説明: 辺の長さが $a=4, b=3, c=2$ の $\triangle \mathrm{ABC}$。角Aが図示されている。]

余弦定理より，  
$$\cos A = \frac{3^2 + 2^2 - 4^2}{2 \cdot 3 \cdot 2} = \frac{9 + 4 - 16}{2 \cdot 3 \cdot 2} = -\frac{3}{2 \cdot 3 \cdot 2} = -\frac{1}{4}$$

$$\sin^2 A = 1 - \cos^2 A = 1 - \left(-\frac{1}{4}\right)^2 = \frac{15}{16}$$

$\sin A > 0$ より，$\sin A = \sqrt{\frac{15}{16}} = \frac{\sqrt{15}}{4}$

よって，面積 $S$ は，
$$S = \frac{1}{2} b c \sin A = \frac{1}{2} \cdot 3 \cdot 2 \cdot \frac{\sqrt{15}}{4} = \frac{3\sqrt{15}}{4}$$

※
- ［D］$a^2 = b^2 + c^2 - 2bc \cos A \iff \cos A = \frac{b^2 + c^2 - a^2}{2bc}$
- ［E］3 辺の長さが与えられた場合の面積を求める手順  
  ① 余弦定理より $\cos A$ の値を求める。  
  ② $\cos A$ から角度 $A$ を求め，$\sin A$ の値を求める，または，三角比の相互関係より，$\sin A$ の値を求める。  
  ③ 公式を用いて面積を求める。  
- ［F］三角比の相互関係 $\sin^2 \theta + \cos^2 \theta = 1$