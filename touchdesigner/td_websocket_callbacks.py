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


def _encode(top, size=SIZE):
    import cv2
    import numpy as np
    a = top.numpyArray(delayed=False)                 # float32 RGBA 0..1, 左下原点
    rgb = (np.flipud(a)[:, :, :3] * 255).clip(0, 255).astype('uint8')
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    if bgr.shape[1] != size or bgr.shape[0] != size:
        bgr = cv2.resize(bgr, (size, size))
    ok, enc = cv2.imencode('.jpg', bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(enc.tobytes()).decode('ascii')


def send_frame(dat):
    global _inflight
    if _inflight:
        return
    try:
        dat.sendText(_encode(op(SRC_TOP)))
        _inflight = True
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
