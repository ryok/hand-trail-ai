# =============================================================
# Script TOP (/project1/trail_accum) — 描画に依存しないトレイル蓄積
#
# なぜ自前で持つか:
#   Feedback TOP は「実際に画面へ描画されるフレーム」でしかバッファを進めず、
#   cook(force=True) を毎フレーム呼んでも蓄積しない。ビューアを開き続ける運用は
#   脆いので、numpy バッファを自分で保持して減衰＋描画する方式にした。
#   これなら Execute DAT の onFrameStart から強制cookするだけで確実に伸びる。
#
# 入力: finger_lag(平滑化した指先) と 生値(検出ゲート)
# 出力: 虹色に色相循環する発光ドットの軌跡 (SIZE x SIZE)
# =============================================================
import math

SIZE = 512          # 正方形。AIへ送るサイズと一致させ、クロップ不要にする
DECAY = 0.99        # 1フレームあたりの残存率(大きいほど尾が長い)
                    # 60fpsで 0.96→尾は約1秒 / 0.99→約5秒。AIに形を掴ませるには
                    # 長めが有利(描いた形が残る)
RADIUS = 22         # ドット半径(px)。太いほどAIが形を掴みやすい
FINGER = '/project1/finger_lag'
GATE_SRC = '/project1/finger_sel'      # 生値(Lag前)。検出ゲート判定用

_buf = None         # 永続バッファ (SIZE,SIZE,4) float32


def _rainbow(t):
    return (0.5 + 0.5 * math.sin(t * 0.8),
            0.5 + 0.5 * math.sin(t * 0.8 + 2.094),
            0.5 + 0.5 * math.sin(t * 0.8 + 4.188))


def onCook(scriptOp):
    global _buf
    import numpy as np
    if _buf is None or _buf.shape[0] != SIZE:
        _buf = np.zeros((SIZE, SIZE, 4), np.float32)

    _buf[:, :, :3] *= DECAY          # 減衰(尾が消えていく)
    _buf[:, :, 3] *= DECAY

    # 検出ゲート: 生値が非ゼロの時だけ描く(未検出で隅に線が飛ぶのを防ぐ)
    gate = False
    g = op(GATE_SRC)
    if g is not None:
        try:
            gx = abs(g['h1:index_finger_tip:x'].eval())
            gy = abs(g['h1:index_finger_tip:y'].eval())
            gate = (gx > 0.001 or gy > 0.001)
        except Exception:
            gate = False

    fl = op(FINGER)
    if gate and fl is not None:
        try:
            fx = float(fl['h1:index_finger_tip:x'].eval())
            fy = float(fl['h1:index_finger_tip:y'].eval())
        except Exception:
            fx = fy = None
        if fx is not None:
            # 正規化0..1 → ピクセル。Yはプラグインが下原点なので素直に使う
            cx = int(fx * SIZE)
            cy = int((1.0 - fy) * SIZE)      # numpyは上が0行なので反転
            r, gg, b = _rainbow(absTime.seconds)
            y0, y1 = max(0, cy - RADIUS), min(SIZE, cy + RADIUS + 1)
            x0, x1 = max(0, cx - RADIUS), min(SIZE, cx + RADIUS + 1)
            if y1 > y0 and x1 > x0:
                yy, xx = np.ogrid[y0:y1, x0:x1]
                d2 = (yy - cy) ** 2 + (xx - cx) ** 2
                # 中心1.0→縁0.0のソフトな円(加算合成)
                soft = np.clip(1.0 - d2 / float(RADIUS ** 2), 0.0, 1.0).astype(np.float32)
                sub = _buf[y0:y1, x0:x1]
                sub[:, :, 0] = np.clip(sub[:, :, 0] + soft * r, 0, 1)
                sub[:, :, 1] = np.clip(sub[:, :, 1] + soft * gg, 0, 1)
                sub[:, :, 2] = np.clip(sub[:, :, 2] + soft * b, 0, 1)
                sub[:, :, 3] = np.clip(sub[:, :, 3] + soft, 0, 1)

    scriptOp.copyNumpyArray(_buf)
    return
