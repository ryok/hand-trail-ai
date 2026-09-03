# GPU 変換サーバー (自作 StreamDiffusion)

TouchDesigner のトレイル(`trail_out`)を GPU(例: RTX 6000 Ada)へ送り、
StreamDiffusion img2img で塗り替えて返す準リアルタイム WebSocket サーバー。

> `gpu-host` は各自の `~/.ssh/config` で定義した GPU マシンの SSH エイリアス。

## 構成
```
TouchDesigner(Mac)
  └ WebSocket DAT → localhost:8765
      └ SSH トンネル ( ssh -L 8765:localhost:8765 -N gpu-host )
          └ GPU: sd_ws_server.py  (127.0.0.1:8765)  ← sd-turbo img2img 常駐
```

## セットアップ (GPUマシン側)
```bash
git clone https://github.com/cumulo-autumn/StreamDiffusion.git
cd StreamDiffusion
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/pip install -r <このリポジトリ>/server/requirements.txt
cp <このリポジトリ>/server/sd_ws_server.py .   # utils.wrapper を import するため StreamDiffusion 直下に置く
```
依存の地雷: `numpy<2` / `huggingface_hub==0.24.6` / xformers 用 `setuptools`。

## 実測レイテンシ (512px, t_index=[22,32], xformers)
- 初回フレーム: ~7.3s (CUDAカーネルJIT/キャッシュ構築)
- 定常: ~0.3s/frame (≒3-4fps)  ※GPU推論自体は55ms、残りはトンネル往復+JPEG/base64

## サーバー起動 (tmuxで常駐)
```bash
ssh gpu-host 'tmux kill-session -t sd 2>/dev/null; \
  tmux new-session -d -s sd "cd ~/StreamDiffusion && \
  CUDA_VISIBLE_DEVICES=0 .venv/bin/python -u sd_ws_server.py \
  --size 512 --acceleration xformers --t-index 22 32 --port 8765 \
  > ~/srv.log 2>&1"'
# 起動確認 (listening が出ればOK):
ssh gpu-host 'grep listening ~/srv.log'
```
⚠️ `pkill -f sd_ws_server.py` は使わないこと。`-f` が自分のSSHシェル自身(`bash -c '...sd_ws_server.py...'`)に
   マッチしてセッションごと落ち(exit 255)、原因不明のまま詰まる。旧プロセスは `tmux kill-session -t sd` で。
⚠️ モデル構築(warmup)は `asyncio.run()` の**外**(同期)で行うこと。中で回すと warmup 中に
   トレースバック無しでサイレントクラッシュする(CUDAストリーム同期とイベントループの干渉)。

## トンネル (Mac側)
```bash
bash ../tunnel.sh   # 自動再接続で常駐 (推奨)
```

## 疎通テスト (Mac側)
```bash
python3 test_client.py   # 3フレーム往復して client_out.jpg を保存
```

## TouchDesigner 側
`../touchdesigner/` の3ファイルを使う:
1. `WebSocket DAT` (`websocket1`): Network Address=`localhost`, Port=`8765`, Active=On,
   Callbacks に `td_websocket_callbacks.py`
2. `Script TOP` (`ai_out`): Callbacks に `td_ai_out_scripttop.py`
3. `Execute DAT` (`ai_driver`): `td_ai_driver.py`。Frame Start を On にすると数フレーム毎に送信
4. 送信元は `td_websocket_callbacks.py` の `SRC_TOP`(既定 `/project1/trail_out`)
5. `ai_out` を表示 = AIで塗り替わったトレイル

### 注意: 画像エンコードは cv2 を使う
TDの Python は環境によって別venvの壊れた PIL を掴み、`import PIL` は通るのに実行時に
`_imaging` の dlopen で落ちることがある。本実装は TD 内蔵の **cv2 (OpenCV)** を使用している。

## プロンプト変更 (実行中)
WebSocket DAT から `PROMPT:新しいプロンプト` を sendText すると即反映。
```python
op('/project1/websocket1').sendText('PROMPT:neon dragon made of flowing energy')
```

## 停止 / GPU解放
```bash
ssh gpu-host 'tmux kill-session -t sd'   # サーバー停止 (GPUメモリ解放)
```
