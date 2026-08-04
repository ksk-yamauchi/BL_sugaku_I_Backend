---
tags:
  - format/concept
  - format/concept_level4
  - Role/Stasap_Concept_Action
  - Competency/知識・技能
  - MEXT/8451503212000000
---
# 概念(アクション): 負の正接 $\tan\theta < 0$ から相互関係式 $1 + \tan^2\theta = \frac{1}{\cos^2\theta}$ を用いて角の鈍角性を判定し $\cos\theta, \sin\theta$ を求める

## 🔼 親概念 (Level 3)
- [[親概念_三角比の相互関係]]

## 🏛️ 指導要領アライメント
- **観点分類**: `知識・技能`
- **階層**: 高等学校 > 数学 > 数学Ⅰ > 内容 > (2) 図形と計量 > ア > (ｲ)
- **指導要領コード**: `8451503212000000`
- **スタサプ枝番**: `_025`

> **【公式テキスト】**
> (ｲ) 三角比を鈍角まで拡張する意義を理解し，鋭角の三角比の値を用いて鈍角の三角比の値を求める方法を理解すること。

> **【💡 解説要約】**
> 座標平面上の半円を用いて角度の範囲を180°まで広げる意義を理解し、補角の公式などを活用して鈍角の三角比の値を求める方法を修得させる。

## 📌 スタサプ独自概要
$\tan\theta < 0$ であることから $\theta$ が鈍角（$\cos\theta < 0$）であることを判定し、$1 + \tan^2\theta = \frac{1}{\cos^2\theta}$ から $\cos\theta = -\frac{1}{\sqrt{1 + \tan^2\theta}}$ を求め、さらに $\sin\theta = \tan\theta \cos\theta$（または相互関係）を用いて $\sin\theta$ を算出する処理。

## ➡️ 前提知識 (重み付きネットワーク)
- [[親概念_三角比の相互関係]]
- `鈍角の三角比の符号`
- `平方根の計算`
- `分数の計算`

## 🎬 📘 概念理解インプット講義動画
- **動画**: [[BL_sugaku_I_12-4-2.mp4]] (`03:55`〜`05:35`)
  - 📝 板書OCR: この等式の両辺を $\cos^2\theta$ で割って整理すると\n$1 + \tan^2\theta = \frac{1}{\cos^2\theta}$\nしたがって、$0^\circ \leqq \theta \leqq 180^\circ$ のときも次の関係が成り立つ。\n三角比の相互関係\n1 $\tan\theta = \frac{\sin\theta}{\cos\theta}$\n2 $\sin^2\theta + \cos^2\theta = 1$\n3 $1 + \tan^2\theta = \frac{1}{\cos^2\theta}$
  - 💡 理由: 相互関係式 $1 + \tan^2\theta = \frac{1}{\cos^2\theta}$ の成立とその適用範囲、定義域について説明しているインプット講義セグメントであるため。
- **動画**: [[BL_sugaku_I_12-4-2.mp4]] (`05:35`〜`08:34`)
  - 📝 板書OCR: 三角比の相互関係\n1 $\tan\theta = \frac{\sin\theta}{\cos\theta}$ 2 $\sin^2\theta + \cos^2\theta = 1$ 3 $1 + \tan^2\theta = \frac{1}{\cos^2\theta}$\n$\theta$ が鋭角（$0^\circ < \theta < 90^\circ$）の場合:\n$\sin\theta > 0$, $\cos\theta > 0$, $\tan\theta > 0$\n$\theta$ が鈍角（$90^\circ < \theta < 180^\circ$）の場合:\n$\sin\theta > 0$, $\cos\theta < 0$, $\tan\theta < 0$
  - 💡 理由: $\tan\theta < 0$ のときに $\theta$ が鈍角領域にあり $\cos\theta < 0$ となる符号の判定ルールを解説しているセグメントであるため。

## 🔗 この概念を使用する確認問題
[[第12講 三角比の拡張 PART4 $180^_circ-_theta$ の三角比，単位円と三角比の相互関係_Q6]]

## 🤝 関連する他の概念（オントロジー・ネットワーク）
- 特記なし
