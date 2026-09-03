# =============================================================
# Script TOP (/project1/ai_out) の onCook
# WebSocket コールバックが保持した最新 base64 JPEG を cv2 でデコードして出力
# =============================================================
import base64

CB_PATH = '/project1/websocket1_callbacks1'


def onCook(scriptOp):
    cb = op(CB_PATH)
    b64 = getattr(cb.module, '_latest_jpg_b64', None) if cb else None
    if not b64:
        scriptOp.clear()
        return
    try:
        import cv2
        import numpy as np
        raw = base64.b64decode(b64)
        bgr = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)  # HxWx3 BGR u8
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype('float32') / 255.0
        rgb = np.flipud(rgb)                                               # 画像原点→TD原点
        rgba = np.dstack([rgb, np.ones(rgb.shape[:2], 'float32')])
        scriptOp.copyNumpyArray(rgba)
    except Exception as e:
        debug('ai_out onCook err:', e)
    return
