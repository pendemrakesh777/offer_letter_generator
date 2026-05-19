#!/bin/zsh
set -e

cd "$(dirname "$0")"
/Users/rakeshpendem/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 generate_offer_letters.py

echo
echo "Offer letters generated in: $(pwd)/generated_docs"
echo "You can close this window."
