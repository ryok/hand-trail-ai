#!/bin/bash
# Mac↔GPU SSHトンネル(8765)を自動再接続で常駐させる。
# 事前に ~/.ssh/config で GPU ホストを "gpu-host" として定義しておく:
#   Host gpu-host
#     HostName <your.gpu.host>
#     User <you>
#     Port <22>
# 使い方: 別ターミナルで  bash tunnel.sh   (別ホスト名なら GPU_HOST=xxx bash tunnel.sh)
# 落ちても2秒後に自動で張り直す。Ctrl-Cで終了。
set -u
HOST="${GPU_HOST:-gpu-host}"
PORT=8765
echo "[tunnel] $HOST:$PORT 常駐開始 (Ctrl-Cで終了)"
while true; do
  ssh -o ConnectTimeout=15 -o ServerAliveInterval=15 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes -N -L ${PORT}:localhost:${PORT} "$HOST"
  echo "[tunnel] 切断されました。2秒後に再接続..."
  sleep 2
done
