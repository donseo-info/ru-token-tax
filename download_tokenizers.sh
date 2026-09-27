#!/bin/bash
# Скачивает открытые токенизаторы с Hugging Face в ./tokenizers (≈32 МБ).
# Лицензии — у авторов моделей, файлы в репозиторий не входят.
set -e
cd "$(dirname "$0")/tokenizers"
get() { [ -s "$2" ] || { echo "↓ $1"; curl -sfL -o "$2" "https://huggingface.co/$1"; }; }
get ai-sage/GigaChat3-10B-A1.8B/resolve/main/tokenizer.json            ai-sage_GigaChat3-10B-A1.8B__tokenizer.json
get deepseek-ai/DeepSeek-V3/resolve/main/tokenizer.json                deepseek-ai_DeepSeek-V3__tokenizer.json
get Qwen/Qwen3-8B/resolve/main/tokenizer.json                          Qwen_Qwen3-8B__tokenizer.json
get yandex/YandexGPT-5-Lite-8B-instruct/resolve/main/tokenizer.model   yandex_YandexGPT-5-Lite-8B-instruct__tokenizer.model
ls -la
