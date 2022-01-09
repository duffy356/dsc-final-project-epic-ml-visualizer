#!/bin/sh

BASE_URL="https://huggingface.co/papluca/xlm-roberta-base-language-detection/resolve/main"

mkdir -p models/
cd models/

echo "xxx starting model downloads ..."

if [ ! -f "config.json" ]; then
    curl "$BASE_URL/config.json" -O
else
  echo "models/config.json already exists!"
fi

if [ ! -f "tokenizer.json" ]; then
  curl "$BASE_URL/tokenizer.json" -O
  echo "models/tokenizer.json downloaded!"
else
  echo "models/tokenizer.json already exists!"
fi

if [ ! -f "special_tokens_map.json" ]; then
  curl "$BASE_URL/special_tokens_map.json" -O
  echo "models/special_tokens_map.json downloaded!"
else
  echo "models/special_tokens_map.json already exists!"
fi

if [ ! -f "tokenizer_config.json" ]; then
  curl "$BASE_URL/tokenizer_config.json" -O
  echo "models/tokenizer_config.json downloaded!"
else
  echo "models/tokenizer_config.json already exists!"
fi

if [ ! -f "pytorch_model.bin" ]; then
  curl "$BASE_URL/pytorch_model.bin" -O -L
  echo "models/pytorch_model.bin downloaded!"
else
  echo "models/pytorch_model.bin already exists!"
fi

echo "xxx completed model downloads ..."
