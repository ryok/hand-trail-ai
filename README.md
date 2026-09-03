# hand-trail-ai

指で空中に描いた発光トレイルを、自前GPUの **StreamDiffusion** でリアルタイムにAI変換する
TouchDesigner プロジェクト。Reddit の
[Real Time Hand Tracking AI Trails](https://www.reddit.com/r/TouchDesigner/comments/1v3npnj/real_time_hand_tracking_ai_trails_w/)
を、課金サービスに頼らず手元のGPU＋WebSocketで再現したもの。

## しくみ

```
USBカメラ → MediaPipe(手21点) → 指先座標
   → Circle TOP(虹色ドット) → Feedback TOP(トレイル蓄積) → Blur+Add(発光) → trail_out
        → WebSocket DAT ─ SSHトンネル ─→ GPU: StreamDiffusion img2img → ai_out(AI変換トレイル)
```

- **手検出 + トレイル生成**: TouchDesigner + MediaPipe プラグイン(Mac完結・GPU不要)
- **AI変換**: 別マシンのGPUで StreamDiffusion(sd-turbo, img2img) を常駐させ、
  512px JPEG フレームを WebSocket で往復(準リアルタイム ~3-4fps)
- プロンプトは実行中にライブで差し替え可能

## 構成

| パス | 内容 |
|---|---|
| `server/sd_ws_server.py` | GPU側 StreamDiffusion WebSocketサーバー |
| `server/test_client.py` | 疎通テスト用クライアント |
| `server/requirements.txt` | GPU側依存 |
| `server/README.md` | GPUサーバーの詳細手順 |
| `touchdesigner/td_websocket_callbacks.py` | WebSocket DAT: 送信(in-flightガード)+受信 |
| `touchdesigner/td_ai_out_scripttop.py` | Script TOP: 受信フレームのデコード表示 |
| `touchdesigner/td_ai_driver.py` | Execute DAT: 毎フレーム送信ドライバ |
| `tunnel.sh` | Mac↔GPU SSHトンネル(自動再接続) |
| `.toe` 本体 | サイズが大きいため [Releases](../../releases) に添付 |

## クイックスタート

1. **GPU側**: `server/README.md` に従って StreamDiffusion + `sd_ws_server.py` を起動
2. **Mac側**: `bash tunnel.sh`（`~/.ssh/config` に `gpu-host` を定義しておく）
3. **TouchDesigner**: Releases の `.toe` を開く（要 [MediaPipe TouchDesigner Plugin](https://github.com/torinmb/mediapipe-touchdesigner)）
4. `websocket1` を Active にして、カメラの前で指を動かす → `ai_out` にAI変換トレイル

## 依存

- [TouchDesigner](https://derivative.ca/) 099.2023+
- [MediaPipe TouchDesigner Plugin](https://github.com/torinmb/mediapipe-touchdesigner)
- [StreamDiffusion](https://github.com/cumulo-autumn/StreamDiffusion)（GPU側・別途clone）
- NVIDIA GPU（xformers。sd-turbo が載る程度のVRAM）

## 解説記事

（Zenn記事リンクをここに追記）

## ライセンス

MIT
