ベーシックレベル数学Ⅰ 第14講 PART3

# PART3 四角形の面積

## 要点① 四角形の面積

四角形の面積を，対角線によって分割された 2 つの三角形の面積の和として求める。

### 例
右図のような四角形 ABCD の面積 $S$ を求める。

[図の説明: 対角線 BD で分割された四角形 ABCD。$\triangle ABD$ において $AB=\sqrt{2}$, $AD=1+\sqrt{3}$, $\angle A=45^\circ$。$\triangle BCD$ において $CD=\sqrt{2}$, $\angle DBC=45^\circ$。]

$\triangle ABD$ において，余弦定理より
$$BD^2 = (\sqrt{2})^2 + (1+\sqrt{3})^2 - 2 \cdot \sqrt{2} \cdot (1+\sqrt{3}) \cdot \cos 45^\circ$$
$$= 2 + 4 + 2\sqrt{3} - 2\sqrt{2}(1+\sqrt{3}) \cdot \frac{1}{\sqrt{2}} = 4$$

$BD > 0$ より $BD = 2$

よって $S = \triangle ABD + \triangle BCD$
$$= \frac{1}{2} \cdot \sqrt{2} \cdot (1+\sqrt{3}) \cdot \sin 45^\circ + \frac{1}{2} \cdot 2 \cdot \sqrt{2} \cdot \sin 45^\circ$$
$$= \frac{1}{2} \cdot \sqrt{2} \cdot (1+\sqrt{3}) \cdot \frac{1}{\sqrt{2}} + \frac{1}{2} \cdot 2 \cdot \sqrt{2} \cdot \frac{1}{\sqrt{2}} = \frac{1+\sqrt{3}}{2} + 1 = \frac{3+\sqrt{3}}{2}$$

---

### 例
右図のような四角形 ABCD の面積 $S$ を求める。

[図の説明: 四角形 ABCD。対角線 BD で分割されており、$AB=\sqrt{2}$, $AD=1+\sqrt{3}$, $\angle A=45^\circ$, $CD=\sqrt{2}$, $\angle B=75^\circ$。]

$\triangle ABD$ において
余弦定理より $BD = 2$

正弦定理より $\frac{2}{\sin 45^\circ} = \frac{\sqrt{2}}{\sin \angle ABD}$
$$\sin \angle ABD = \sqrt{2} \cdot \frac{\sin 45^\circ}{2} = \frac{\sqrt{2}}{2} \cdot \frac{1}{\sqrt{2}} = \frac{1}{2}$$

$\angle ABD < 135^\circ$ より $\angle ABD = 30^\circ$

よって $\angle DBC = 75^\circ - 30^\circ = 45^\circ$

したがって $S = \triangle ABD + \triangle BCD = \frac{3+\sqrt{3}}{2}$

---

分割されたそれぞれの三角形の面積を求めるために，どの辺の長さや角の大きさが必要かを考え，正弦定理や余弦定理などを用いて三角形の辺の長さや角の大きさを求める。

---

ベーシックレベル数学Ⅰ 第14講 PART3

［MEMO］

---

ベーシックレベル数学Ⅰ 第14講 PART3

### 3
$AB = \sqrt{3}-1$, $BC = 2$, $DA = \sqrt{2}$, $\angle A = 75^\circ$, $\angle B = 120^\circ$ である四角形 ABCD の面積 $S$ を求めよ。

[図の説明: 四角形 ABCD。辺 $AB=\sqrt{3}-1$, $BC=2$, $DA=\sqrt{2}$ で、角 $\angle A=75^\circ$, $\angle B=120^\circ$ が示されている。]

---

## Point Pickup

### 四角形の面積
対角線によって分割された 2 つの三角形の面積の和として求める。正弦定理や余弦定理などを用いてそれぞれの三角形の辺の長さや角の大きさを求める。

---

ベーシックレベル数学Ⅰ 第14講 PART3

# 第14講 PART3 確認問題

### 1
$AB = 3-\sqrt{3}$, $BC = 2\sqrt{3}$, $DA = \sqrt{6}$, $\angle A = 75^\circ$, $\angle B = 120^\circ$ である。この四角形 ABCD の面積 $S$ を求める。

[図の説明: 四角形 ABCD。辺 $AB=3-\sqrt{3}$, $BC=2\sqrt{3}$, $DA=\sqrt{6}$ で、角 $\angle A=75^\circ$, $\angle B=120^\circ$ が示されている。]

$\triangle ABC$ で余弦定理より，対角線 AC の長さを求めると，
$$AC = [ ア ] \sqrt{[ イ ]}$$

$\triangle ABC$ で正弦定理により，
$$\angle BAC = [ ウエ ]^\circ$$

また，$\angle DAC = [ オカ ]^\circ$

よって，四角形 ABCD の面積 $S$ は，
$$S = \frac{[ キ ]}{[ ク ]}$$

---

ベーシックレベル数学Ⅰ 解答 第14講 PART3

# PART3 四角形の面積

### 3
$AB = \sqrt{3}-1$, $BC = 2$, $DA = \sqrt{2}$, $\angle A = 75^\circ$, $\angle B = 120^\circ$ である四角形 ABCD の面積 $S$ を求めよ。

［解答］
$\triangle ABC$ で余弦定理より
$$AC^2 = (\sqrt{3}-1)^2 + 2^2 - 2 \cdot (\sqrt{3}-1) \cdot 2 \cdot \cos 120^\circ$$
$$= 4 - 2\sqrt{3} + 4 - 4(\sqrt{3}-1) \cdot \left(-\frac{1}{2}\right) = 6$$

$AC > 0$ より $AC = \sqrt{6}$

正弦定理より $\frac{\sqrt{6}}{\sin 120^\circ} = \frac{2}{\sin \angle BAC}$
$$\sin \angle BAC = 2 \cdot \frac{\sin 120^\circ}{\sqrt{6}} = \frac{2}{\sqrt{6}} \cdot \frac{\sqrt{3}}{2} = \frac{1}{\sqrt{2}}$$

$\angle BAC < 60^\circ$ より $\angle BAC = 45^\circ$

よって $\angle DAC = 75^\circ - 45^\circ = 30^\circ$

したがって $S = \triangle ABC + \triangle DAC$
$$= \frac{1}{2} \cdot (\sqrt{3}-1) \cdot 2 \cdot \sin 120^\circ + \frac{1}{2} \cdot \sqrt{2} \cdot \sqrt{6} \cdot \sin 30^\circ$$
$$= \frac{1}{2} \cdot (\sqrt{3}-1) \cdot 2 \cdot \frac{\sqrt{3}}{2} + \frac{1}{2} \cdot \sqrt{2} \cdot \sqrt{6} \cdot \frac{1}{2}$$
$$= \frac{3}{2}$$

[図の説明: 1つ目: 四角形 ABCD。$AB=\sqrt{3}-1$, $BC=2$, $DA=\sqrt{2}$, $\angle A=75^\circ$, $\angle B=120^\circ$。
 2つ目: 対角線 AC で分割された四角形 ABCD。$AC=\sqrt{6}$, $\angle BAC=45^\circ$, $\angle DAC=30^\circ$ が求められている図。]

---

ベーシックレベル数学Ⅰ 解答 第14講 PART3

# 第14講 PART3 確認問題 解答

### 1
［正解］ア：3，イ：2，ウエ：45，オカ：30，キ：9，ク：2

［解説］
$\triangle ABC$ で余弦定理より，［Ａ］
$$AC^2 = (3-\sqrt{3})^2 + (2\sqrt{3})^2 - 2 \cdot (3-\sqrt{3}) \cdot 2\sqrt{3} \cos 120^\circ$$
$$= 12 - 6\sqrt{3} + 12 - 4\sqrt{3}(3-\sqrt{3}) \cdot \left(-\frac{1}{2}\right) = 18$$

$AC > 0$ より，
$$AC = 3\sqrt{2}$$

$\triangle ABC$ で正弦定理より，［Ｂ］
$$\frac{3\sqrt{2}}{\sin 120^\circ} = \frac{2\sqrt{3}}{\sin \angle BAC}$$
$$\sin \angle BAC = 2\sqrt{3} \cdot \frac{\sin 120^\circ}{3\sqrt{2}} = \frac{2\sqrt{3}}{3\sqrt{2}} \cdot \frac{\sqrt{3}}{2} = \frac{1}{\sqrt{2}}$$

$\angle BAC < 75^\circ$ より，
$$\angle BAC = 45^\circ$$

よって，$\angle DAC = 75^\circ - 45^\circ = 30^\circ$

したがって，
$$S = \triangle ABC + \triangle DAC \quad \text{［Ｃ］}$$
$$= \frac{1}{2} \cdot (3-\sqrt{3}) \cdot 2\sqrt{3} \sin 120^\circ + \frac{1}{2} \cdot \sqrt{6} \cdot 3\sqrt{2} \sin 30^\circ$$
$$= \frac{1}{2} \cdot (3-\sqrt{3}) \cdot 2\sqrt{3} \cdot \frac{\sqrt{3}}{2} + \frac{1}{2} \cdot \sqrt{6} \cdot 3\sqrt{2} \cdot \frac{1}{2}$$
$$= \frac{9}{2}$$

[図の説明: 四角形 ABCD と対角線 AC。辺 $AB=3-\sqrt{3}$, $BC=2\sqrt{3}$, $DA=\sqrt{6}$, $AC=3\sqrt{2}$, $\angle A=75^\circ$, $\angle B=120^\circ$。]

* ［Ａ］ $\triangle ABC$ に着目して，余弦定理を利用して AC の長さを求める。
* ［Ｂ］ $\triangle ABC$ は 2 辺がわかっているので，正弦定理を利用する。
* ［Ｃ］ 2 つの三角形の和として四角形の面積を求める。