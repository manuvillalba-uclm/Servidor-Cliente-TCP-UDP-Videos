#!/bin/sh
#
echo "Se realiza una descarga, "
echo "Downloading audio..."
./client.py --Ice.Config=client.config "orchestrator" --download "$1"

echo ""
echo "List request..."
./client.py --Ice.Config=client.config "orchestrator"

echo ""
echo "Init transfer..."
./client.py --Ice.Config=client.config "orchestrator" --transfer "$2"