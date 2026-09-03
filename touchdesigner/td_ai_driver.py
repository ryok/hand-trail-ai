# =============================================================
# Execute DAT (/project1/ai_driver) の onFrameStart
# 1) 毎フレーム trail_out を強制cookして Feedback ループを進める
#    (トレイル蓄積を送信可否/inflightと独立させる。これが無いと送信が
#     止まった瞬間にループがcookされず軌跡が伸びない)
# 2) websocket1 が Active なら数フレーム毎に send_frame を試みる
#    (in-flight ガードで返信待ち中はスキップ=サーバー律速)
# =============================================================
WS = '/project1/websocket1'
CB = '/project1/websocket1_callbacks1'
SRC = '/project1/trail_out'
EVERY = 3   # 何フレーム毎に送信を試みるか(ガードがあるので小さくてOK)


def onFrameStart(frame):
    # 1) トレイル連鎖を毎フレームcook(Feedback蓄積を保証)
    tr = op(SRC)
    if tr is not None:
        tr.cook(force=True)
    # 2) 送信
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
