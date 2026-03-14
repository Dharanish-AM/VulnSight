#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
python3 test_target/server.py --host 127.0.0.1 --port 8081
