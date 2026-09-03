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

- **手検出 + トレイル生成**: TouchDesigner + MediaPipe プラグイン(Mac完結・GPU不要) ← このリポジトリ
- **AI変換**: 別マシンのGPUで StreamDiffusion img2img を WebSocket 常駐 ← [**streamdiffusion-ws**](https://github.com/ryok/streamdiffusion-ws)（別リポジトリ）
- プロンプトは実行中にライブで差し替え可能

このリポジトリは **TouchDesigner側（手トレイル生成＋WebSocket送受信）** を担当する。
GPU側の変換サーバーは、TD非依存で再利用可能な [streamdiffusion-ws](https://github.com/ryok/streamdiffusion-ws) に分離した。

## 構成

| パス | 内容 |
|---|---|
| `touchdesigner/td_websocket_callbacks.py` | WebSocket DAT: 送信(in-flightガード)+受信 |
| `touchdesigner/td_ai_out_scripttop.py` | Script TOP: 受信フレームのデコード表示 |
| `touchdesigner/td_ai_driver.py` | Execute DAT: 毎フレーム送信ドライバ |
| `tunnel.sh` | Mac↔GPU SSHトンネル(自動再接続) |
| `.toe` 本体 | サイズが大きいため [Releases](../../releases) に添付 |
| GPU変換サーバー | 別リポジトリ [streamdiffusion-ws](https://github.com/ryok/streamdiffusion-ws) |

## クイックスタート

1. **GPU側**: [streamdiffusion-ws](https://github.com/ryok/streamdiffusion-ws) の README に従ってサーバーを起動
2. **Mac側**: `bash tunnel.sh`（`~/.ssh/config` に `gpu-host` を定義しておく）
3. **TouchDesigner**: Releases の `.toe` を開く（要 [MediaPipe TouchDesigner Plugin](https://github.com/torinmb/mediapipe-touchdesigner)）
4. `websocket1` を Active にして、カメラの前で指を動かす → `ai_out` にAI変換トレイル

## 依存

- [TouchDesigner](https://derivative.ca/) 099.2023+
- [MediaPipe TouchDesigner Plugin](https://github.com/torinmb/mediapipe-touchdesigner)
- [streamdiffusion-ws](https://github.com/ryok/streamdiffusion-ws)（GPU変換サーバー・別リポジトリ）
- NVIDIA GPU（xformers。sd-turbo が載る程度のVRAM）

## 解説記事

（Zenn記事リンクをここに追記）

## ライセンス

MIT
