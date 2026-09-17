#!/usr/bin/env bash
# Run this after connecting to the rented container. It intentionally does not
# install an inference engine or download a model: those choices must already be
# frozen in the campaign plan/image to keep the comparison reproducible.
set -Eeuo pipefail

output_path="${1:-remote-gpu-preflight.json}"
shift || true

python3 scripts/capture_gpu_environment.py --output "$output_path" "$@"
