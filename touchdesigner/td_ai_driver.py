# =============================================================
# Execute DAT (/project1/ai_driver) の onFrameStart
# websocket1 が Active のとき、数フレーム毎に send_frame を試みる。
# 実送信は in-flight ガードで返信待ち中はスキップされる(=サーバー律速)。
# =============================================================
WS = '/project1/websocket1'
CB = '/project1/websocket1_callbacks1'
EVERY = 3   # 何フレーム毎に送信を試みるか(ガードがあるので小さくてOK)


def onFrameStart(frame):
    ws = op(WS)
    if ws is None or not ws.par.active.eval():
        return
    if frame % EVERY == 0:
        op(CB).module.send_frame(ws)
    return


def onFrameEnd(frame):
    return


def onStart():
    return


def onCreate():
    return


def onExit():
    return
