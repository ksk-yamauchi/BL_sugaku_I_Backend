ベーシックレベル数学Ⅰ 第 3 講 PART3

# PART3 根号を含む式の計算

---

## 要点① 平方根

2 乗すると $a$ になる数を，$a$ の「 **平方根** 」という。

$a > 0$ のとき，$a$ の平方根のうち正の方を $\sqrt{a}$，負の方を $-\sqrt{a}$ と表す。これらをまとめて $\pm\sqrt{a}$ と表すことができる。記号 $\sqrt{\phantom{a}}$ を根号といい，$\sqrt{a}$ をルート $a$ と読む。

$a = 0$ のとき，$a$ すなわち 0 の平方根は 0 だけであり，$\sqrt{0} = 0$ とする。

どのような実数も，2 乗すると 0 以上になり，負の数になることはない。したがって，$a < 0$ のとき，$a$ の平方根は，実数の範囲では存在しない。

### 例
- 2 の平方根は $\sqrt{2}$ と $-\sqrt{2}$ である（2 つをまとめて $\pm\sqrt{2}$ と表すことができる）。
- $\sqrt{9}$ は 9 の正の平方根であり，$-\sqrt{9}$ は 9 の負の平方根である。  
  よって $\sqrt{9} = 3$，$-\sqrt{9} = -3$ である。
- $(\sqrt{5})^2 = 5$，$(-\sqrt{5})^2 = 5$ である。
- また，$\sqrt{6^2} = \sqrt{36} = 6$，$\sqrt{(-6)^2} = \sqrt{36} = 6$ である。

一般に，次のことが成り立つ。

> **1** $a \geqq 0$ のとき　$(\sqrt{a})^2 = a, \quad (-\sqrt{a})^2 = a$
> 
> **2** 
> - $a \geqq 0$ のとき　$\sqrt{a^2} = a$
> - $a < 0$ のとき　$\sqrt{a^2} = -a$
>
> すなわち $\sqrt{a^2} = |a|$

---

## 要点② 平方根の積と商

平方根の積と商について，次のことが成り立つ。

> $a > 0, b > 0, k > 0$ のとき
> 
> **1** $\sqrt{a}\sqrt{b} = \sqrt{ab}$
> 
> **2** $\frac{\sqrt{a}}{\sqrt{b}} = \sqrt{\frac{a}{b}}$
> 
> **3** $\sqrt{k^2 a} = k\sqrt{a}$

### 1 の証明
$\sqrt{a}\sqrt{b}$ を 2 乗すると
$$(\sqrt{a}\sqrt{b})^2 = (\sqrt{a})^2(\sqrt{b})^2 = ab$$

ここで，$\sqrt{a} > 0, \sqrt{b} > 0$ より，$\sqrt{a}\sqrt{b} > 0$

よって，$\sqrt{a}\sqrt{b}$ は $ab$ の正の平方根である。

したがって，$\sqrt{a}\sqrt{b} = \sqrt{ab}$

**2** も同様に証明することができる。
**1** より $\sqrt{k^2 a} = \sqrt{k^2}\sqrt{a} = k\sqrt{a}$ であるから，**3** も成立。

### 例
- $\sqrt{2}\sqrt{3} = \sqrt{6}$
- $\frac{\sqrt{15}}{\sqrt{3}} = \sqrt{5}$
- $\sqrt{80} = 4\sqrt{5}$

---

## 要点③ 分母の有理化

「分母の有理化」… 分母に根号を含む式を変形し，分母に根号を含まない式にすること

### 例
$$\frac{\sqrt{7}}{\sqrt{5}} = \frac{\sqrt{7}\sqrt{5}}{\sqrt{5}\sqrt{5}} = \frac{\sqrt{35}}{5}$$

分母が $\sqrt{a} + \sqrt{b}$ や $\sqrt{a} - \sqrt{b}$ の形の場合は，乗法公式
$$(A+B)(A-B) = A^2 - B^2$$
を用いて分母を有理化することができる。

### 例
$$\frac{2}{\sqrt{3}+\sqrt{2}} = \frac{2(\sqrt{3}-\sqrt{2})}{(\sqrt{3}+\sqrt{2})(\sqrt{3}-\sqrt{2})}$$

---

## 例題 3

### 問題
**(1)** 次の式を計算せよ。
- (i) $\sqrt{2} \times \sqrt{6}$
- (ii) $\sqrt{12} - \sqrt{27}$
- (iii) $(\sqrt{5} - 2\sqrt{2})^2$
- (iv) $(\sqrt{7} - 2)(\sqrt{7} + 2)$

**(2)** 次の式の分母を有理化せよ。
- (i) $\frac{2\sqrt{3}}{\sqrt{2}}$
- (ii) $\frac{1}{\sqrt{2} - \sqrt{6}}$
- (iii) $\frac{4}{3 + \sqrt{7}}$

---

### 解答

**(1)**
- (i) $\sqrt{2} \times \sqrt{6} = \sqrt{2} \times \sqrt{2 \cdot 3} = \sqrt{2^2 \cdot 3} = 2\sqrt{3}$
- (ii) $\sqrt{12} - \sqrt{27} = 2\sqrt{3} - 3\sqrt{3} = -\sqrt{3}$
- (iii) $(\sqrt{5} - 2\sqrt{2})^2 = (\sqrt{5})^2 - 2 \cdot \sqrt{5} \cdot 2\sqrt{2} + (2\sqrt{2})^2 = 5 - 4\sqrt{10} + 8 = 13 - 4\sqrt{10}$
- (iv) $(\sqrt{7} - 2)(\sqrt{7} + 2) = (\sqrt{7})^2 - 2^2 = 7 - 4 = 3$

**(2)**
- (i) $\frac{2\sqrt{3}}{\sqrt{2}} = \frac{2\sqrt{3} \times \sqrt{2}}{\sqrt{2} \times \sqrt{2}} = \frac{2\sqrt{6}}{2} = \sqrt{6}$
- (ii) $\frac{1}{\sqrt{2} - \sqrt{6}} = \frac{\sqrt{2} + \sqrt{6}}{(\sqrt{2} - \sqrt{6})(\sqrt{2} + \sqrt{6})} = \frac{\sqrt{2} + \sqrt{6}}{2 - 6} = -\frac{\sqrt{6} + \sqrt{2}}{4}$
  
  *(別解)* 
  $$\frac{1}{\sqrt{2} - \sqrt{6}} = -\frac{1}{\sqrt{6} - \sqrt{2}} = -\frac{\sqrt{6} + \sqrt{2}}{(\sqrt{6} - \sqrt{2})(\sqrt{6} + \sqrt{2})} = -\frac{\sqrt{6} + \sqrt{2}}{6 - 2} = -\frac{\sqrt{6} + \sqrt{2}}{4}$$

- (iii) $\frac{4}{3 + \sqrt{7}} = \frac{4(3 - \sqrt{7})}{(3 + \sqrt{7})(3 - \sqrt{7})} = \frac{4(3 - \sqrt{7})}{9 - 7} = \frac{4(3 - \sqrt{7})}{2} = 2(3 - \sqrt{7}) = 6 - 2\sqrt{7}$

---

## Point Pickup

### 根号を含む式の計算
- $\sqrt{\phantom{a}}$ の中を素因数分解し，$\sqrt{k^2 a} = k\sqrt{a}$ を用いて，$\sqrt{\phantom{a}}$ の中の数を小さくする。
- $(\sqrt{a})^2 = a$，$\sqrt{a}\sqrt{b} = \sqrt{ab}$，$\frac{\sqrt{a}}{\sqrt{b}} = \sqrt{\frac{a}{b}}$ と乗法公式を用いて，文字式と同じように四則計算を行う。

### 分母の有理化
- $(\sqrt{a})^2 = a$，$(\sqrt{a}+\sqrt{b})(\sqrt{a}-\sqrt{b}) = a-b$ を利用し，分母に根号を含まない形に。

---

## 第 3 講 PART3 確認問題

次の式を計算せよ。

**1** $\sqrt{6} \times \sqrt{3} = \text{[ ア ]}\sqrt{\text{[ イ ]}}$

**2** $\sqrt{8} - \sqrt{18} = \text{[ ウ ]}\sqrt{\text{[ エ ]}}$

**3** $(\sqrt{3} - \sqrt{2})^2 = \text{[ オ ]} - \text{[ カ ]}\sqrt{\text{[ キ ]}}$

**4** $(\sqrt{5} + 1)(\sqrt{5} - 1) = \text{[ ク ]}$

次の式の分母を有理化せよ。

**5** $\frac{\sqrt{5}}{\sqrt{3}} = \frac{\sqrt{\text{[ ケコ ]}}}{\text{[ サ ]}}$

**6** $\frac{1}{\sqrt{7} + \sqrt{2}} = \frac{\sqrt{\text{[ シ ]}} - \sqrt{\text{[ ス ]}}}{\text{[ セ ]}}$

**7** $\frac{4}{3 - \sqrt{5}} = \text{[ ソ ]} + \sqrt{\text{[ タ ]}}$

---

## 第 3 講 PART3 確認問題 解答

### 1
**［正解］** ア：3，イ：2  
**［解説］**  
$$\sqrt{6} \times \sqrt{3} = \sqrt{6 \times 3} = \sqrt{3^2 \times 2} = 3\sqrt{2}$$

- **［A］** $\sqrt{a} \times \sqrt{b} = \sqrt{ab}$
- **［B］** $k > 0$ のとき，$\sqrt{k^2 a} = k\sqrt{a}$

---

### 2
**［正解］** ウ：-，エ：2  
**［解説］**  
$$\sqrt{8} - \sqrt{18} = \sqrt{2^2 \times 2} - \sqrt{3^2 \times 2} = 2\sqrt{2} - 3\sqrt{2} = -\sqrt{2}$$

- **［C］** $k > 0$ のとき，$\sqrt{k^2 a} = k\sqrt{a}$

---

### 3
**［正解］** オ：5，カ：2，キ：6  
**［解説］**  
$$(\sqrt{3} - \sqrt{2})^2 = (\sqrt{3})^2 - 2\sqrt{3}\sqrt{2} + (\sqrt{2})^2 = 3 - 2\sqrt{6} + 2 = 5 - 2\sqrt{6}$$

- **［D］** 展開の公式 $(a-b)^2 = a^2 - 2ab + b^2$ を利用する。

---

### 4
**［正解］** ク：4  
**［解説］**  
$$(\sqrt{5} + 1)(\sqrt{5} - 1) = (\sqrt{5})^2 - 1^2 = 5 - 1 = 4$$

- **［E］** 展開の公式 $(a+b)(a-b) = a^2 - b^2$ を利用する。

---

### 5
**［正解］** ケコ：15，サ：3  
**［解説］**  
$$\frac{\sqrt{5}}{\sqrt{3}} = \frac{\sqrt{5} \times \sqrt{3}}{\sqrt{3} \times \sqrt{3}} = \frac{\sqrt{15}}{3}$$

- **［F］** 分母・分子に $\sqrt{3}$ をかけ，$(\sqrt{a})^2 = a$ を利用し，分母を有理化する。

---

### 6
**［正解］** シ：7，ス：2，セ：5  
**［解説］**  
$$\frac{1}{\sqrt{7} + \sqrt{2}} = \frac{1 \times (\sqrt{7} - \sqrt{2})}{(\sqrt{7} + \sqrt{2})(\sqrt{7} - \sqrt{2})} = \frac{\sqrt{7} - \sqrt{2}}{(\sqrt{7})^2 - (\sqrt{2})^2} = \frac{\sqrt{7} - \sqrt{2}}{7 - 2} = \frac{\sqrt{7} - \sqrt{2}}{5}$$

- **［G］** 分母・分子に $\sqrt{7} - \sqrt{2}$ をかけ，$(\sqrt{a}+\sqrt{b})(\sqrt{a}-\sqrt{b}) = a-b$ を利用し，分母を有理化する。

---

### 7
**［正解］** ソ：3，タ：5  
**［解説］**  
$$\frac{4}{3 - \sqrt{5}} = \frac{4(3 + \sqrt{5})}{(3 - \sqrt{5})(3 + \sqrt{5})} = \frac{4(3 + \sqrt{5})}{3^2 - (\sqrt{5})^2} = \frac{4(3 + \sqrt{5})}{9 - 5} = 3 + \sqrt{5}$$

- **［H］** 分母・分子に $3 + \sqrt{5}$ をかけ，分母を有理化する。