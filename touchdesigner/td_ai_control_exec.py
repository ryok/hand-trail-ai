# =============================================================
# Parameter Execute DAT (/project1/ai_control_exec)
# ai_control のカスタムパラメータを監視し、WebSocket経由で
# サーバーへ制御メッセージ(PROMPT: / TINDEX:)を送る。
#   - Dragon/Inkwash/Neon (pulse): プリセットプロンプト送信
#   - Strength (0..1 slider): t_index にマップして TINDEX: 送信
#   - Customprompt + Sendcustom: 自由入力プロンプト送信
# 監視対象: parameterexecuteDAT の OP を /project1/ai_control に設定すること
# =============================================================
WS = '/project1/websocket1'

PRESETS = {
    'Dragon':  'neon dragon made of flowing energy, dark background',
    'Inkwash': 'flowing ink wash painting, glowing smoke, elegant',
    'Neon':    'glowing neon light trails, cyberpunk, vibrant colors, dark background',
}


def _send(msg):
    ws = op(WS)
    if ws is not None and ws.par.active.eval():
        ws.sendText(msg)
    else:
        debug('websocket not active, skip:', msg[:40])


def _strength_to_tindex(s):
    # s=0(弱・入力に忠実) → [30,40] / s=1(強・AI解釈) → [10,20]
    # s=0.4 で [22,32](既定)に一致
    a = int(round(30 - s * 20))
    return a, a + 10


def onValueChange(par, prev):
    if par.name == 'Strength':
        a, b = _strength_to_tindex(float(par.eval()))
        _send(f'TINDEX:{a},{b}')
    return


def onPulse(par):
    if par.name in PRESETS:
        _send('PROMPT:' + PRESETS[par.name])
    elif par.name == 'Sendcustom':
        p = par.owner.par.Customprompt.eval().strip()
        if p:
            _send('PROMPT:' + p)
    return


def onValuesChanged(changes):
    # TD 2023+ の一括コールバック。個別 onValueChange/onPulse を使うので何もしない
    return
