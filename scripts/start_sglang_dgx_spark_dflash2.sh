#!/usr/bin/env bash
set -Eeuo pipefail

MODEL_HOME="/workspace/models"
TARGET_DIR="$MODEL_HOME/Qwen3.8-27B-NVFP4"
TOKENIZER_DIR="$MODEL_HOME/Qwen3.8-27B"
DRAFT_DIR="$MODEL_HOME/Qwen3.8-27B-DFlash2"
IMAGE="lmsysorg/sglang@sha256:616a3e97f45191af975896cfa644279096cb31bd408a071c2e99ca7209c3cafe"
CONTAINER_NAME="sglang-c025"
PORT="8001"

for required_file in \
  "$TARGET_DIR/config.json" \
  "$TOKENIZER_DIR/tokenizer_config.json" \
  "$DRAFT_DIR/config.json"; do
  if [[ ! -f "$required_file" ]]; then
    printf 'Missing model file: %s\n' "$required_file" >&2
    exit 2
  fi
done

if ! command -v docker >/dev/null 2>&1; then
  printf 'docker is required on the DGX Spark host.\n' >&2
  exit 2
fi

if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
  printf 'Container name already exists: %s\nStop or rename it explicitly before launching.\n' "$CONTAINER_NAME" >&2
  exit 2
fi

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker pull "$IMAGE"
fi

docker image inspect "$IMAGE" --format 'SGLang image ID={{.Id}} RepoDigests={{json .RepoDigests}}'
printf 'Starting %s on 127.0.0.1:%s; logs: docker logs -f %s\n' "$CONTAINER_NAME" "$PORT" "$CONTAINER_NAME"

exec docker run --detach \
  --name "$CONTAINER_NAME" \
  --device nvidia.com/gpu=all \
  --network host \
  --ipc host \
  --volume "$MODEL_HOME:$MODEL_HOME" \
  --env HF_HOME="$MODEL_HOME" \
  "$IMAGE" \
  python3 -m sglang.launch_server \
  --model-path "$TARGET_DIR" \
  --tokenizer-path "$TOKENIZER_DIR" \
  --served-model-name Qwen3.8-27B \
  --trust-remote-code \
  --tp-size 1 \
  --context-length 262144 \
  --kv-cache-dtype fp8_e4m3 \
  --mem-fraction-static 0.80 \
  --attention-backend flashinfer \
  --chunked-prefill-size 2048 \
  --mamba-ssm-dtype float32 \
  --mamba-radix-cache-strategy extra_buffer \
  --max-mamba-cache-size 50 \
  --max-running-requests 10 \
  --reasoning-parser qwen3 \
  --tool-call-parser qwen3_coder \
  --speculative-algorithm DFLASH \
  --speculative-draft-model-path "$DRAFT_DIR" \
  --speculative-num-draft-tokens 8 \
  --disable-flashinfer-autotune \
  --enable-metrics \
  --host 127.0.0.1 \
  --port "$PORT"
