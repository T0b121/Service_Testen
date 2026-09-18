#!/usr/bin/env bash
set -euo pipefail

# SD-Turbo is a complete checkpoint: model, text encoder and VAE are contained
# in one file.  It is deliberately installed on the server-side ComfyUI volume,
# never downloaded through a browser on a user's workstation.
model_name="sd_turbo.safetensors"
model_url="https://huggingface.co/stabilityai/sd-turbo/resolve/main/${model_name}?download=true"
model_sha256="3f067a1b943cf162f2b8f8588f6cf5824bd5b4c7d1d88d87164b9ca123616549"
model_dir="/data/models/checkpoints"
model_path="${model_dir}/${model_name}"

if docker exec comfyui test -f "${model_path}"; then
  actual_sha256="$(docker exec comfyui sha256sum "${model_path}" | awk '{print $1}')"
  if [ "${actual_sha256}" = "${model_sha256}" ]; then
    printf '%s\n' "${model_name} is already installed and verified."
    exit 0
  fi
  docker exec comfyui rm -f "${model_path}"
fi

printf '%s\n' "Downloading ${model_name} directly into ComfyUI's persistent model volume ..."
docker exec comfyui sh -ec "
  mkdir -p '${model_dir}'
  rm -f '${model_path}.part'
  curl --fail --location --retry 5 --retry-delay 5 --continue-at - \\
    --output '${model_path}.part' '${model_url}'
  echo '${model_sha256}  ${model_path}.part' | sha256sum -c -
  mv '${model_path}.part' '${model_path}'
"

printf '%s\n' "${model_name} was installed and verified."
