# =============================================================
# WebSocket DAT (/project1/websocket1) コールバック
#   - trail_out を base64 JPEG にして送信 (send_frame)
#   - in-flight ガード: 返信待ち中は送らない(サーバーを溢れさせない)
#   - 受信 base64 JPEG を保持し Script TOP(ai_out) を再クック
#   - エンコードは cv2 を使用(TDのPIL は無関係venvを掴んで dlopen 失敗するため)
# =============================================================
import base64

SRC_TOP = '/project1/trail_out'
DST_TOP = '/project1/ai_out'
SIZE = 512

_latest_jpg_b64 = None
_inflight = False
_sent_at = 0.0          # 最後に送信した時刻(秒)
TIMEOUT = 3.0           # 応答がこの秒数返らなければ送信済み扱いを解除(ウォッチドッグ)
                        # 接続断で応答が来ないと _inflight が固まり ai_out が凍るため


def _encode(top, size=SIZE):
    import cv2
    import numpy as np
    a = top.numpyArray(delayed=False)                 # float32 RGBA 0..1, 左下原点
    rgb = (np.flipud(a)[:, :, :3] * 255).clip(0, 255).astype('uint8')
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    # 中央正方形クロップ(横潰れ防止): 1280x720 → 中央720x720 → size
    h, w = bgr.shape[:2]
    s = min(h, w)
    y0, x0 = (h - s) // 2, (w - s) // 2
    bgr = bgr[y0:y0 + s, x0:x0 + s]
    if s != size:
        bgr = cv2.resize(bgr, (size, size))
    ok, enc = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(enc.tobytes()).decode('ascii')


def send_frame(dat):
    global _inflight, _sent_at
    now = absTime.seconds
    if _inflight:
        if now - _sent_at < TIMEOUT:
            return
        # ウォッチドッグ: 応答が来ないまま TIMEOUT 経過 → 見捨てて再送を許可
        debug('[ws] response timeout, releasing inflight')
        _inflight = False
    try:
        dat.sendText(_encode(op(SRC_TOP)))
        _inflight = True
        _sent_at = now
    except Exception as e:
        debug('send_frame err:', e)


def onConnect(dat):
    global _inflight
    _inflight = False
    debug('[ws] connected', dat.par.netaddress.eval(), dat.par.port.eval())
    return


def onDisconnect(dat):
    global _inflight
    _inflight = False
    debug('[ws] disconnected')
    return


def onReceiveText(dat, rowIndex, message, *args):
    global _latest_jpg_b64, _inflight
    _inflight = False
    if message.startswith('OK:'):
        debug('[ws] server:', message)
        return
    _latest_jpg_b64 = message
    d = op(DST_TOP)
    if d is not None:
        d.cook(force=True)
    return


def onReceiveBinary(dat, contents):
    return


def onReceivePing(dat, contents):
    dat.sendPong(contents)
    return


def onReceivePong(dat, contents):
    return


def onMonitorMessage(dat, message):
    return
