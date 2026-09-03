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

# 被写体を名指すプロンプトが「軌跡→生き物」の鍵。強度(Strength)を高くして使う。
PRESETS = {
    'Phoenix': 'a majestic phoenix bird made of glowing embers and flowing light, '
               'wings spread wide, elegant, dark background, cinematic, highly detailed',
    'Dragon':  'an eastern dragon made of flowing neon energy, coiling through darkness, '
               'glowing scales, dark background, cinematic, highly detailed',
    'Aurora':  'a swirling aurora of glowing gas and stardust, ethereal cosmic light, '
               'deep space nebula, dark background, highly detailed',
}


def _send(msg):
    ws = op(WS)
    if ws is not None and ws.par.active.eval():
        ws.sendText(msg)
    else:
        debug('websocket not active, skip:', msg[:40])


def _strength_to_tindex(s):
    # s=0(弱・入力に忠実) → [30,40] / s=1(最強・生き物が創発) → [4,14]
    # 生き物が出るのは概ね t_index<=[8,18]。既定Strength=0.85で[8,18]付近になる。
    a = int(round(30 - s * 26))
    a = max(2, a)
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
