#!/usr/bash

if [ "$#" != 1 ]; then
  echo "Formato incorrecto. El script tiene el formato: run_client.sh <URL>"
  exit
fi
python3 Client.py "$(head -1 proxy_orch.out)" "$1"