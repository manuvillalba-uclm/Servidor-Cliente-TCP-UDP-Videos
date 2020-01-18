#!/bin/sh
#
echo "Esto es una demostración de uso de un cliente:"

echo ""
echo "Se van a descargar un vídeo, espere unos segundos"
./client.py --Ice.Config=client.config "orchestrator" --download "https://www.youtube.com/watch?v=HoBa2SyvtpE"
echo ""
echo "List request"
./client.py --Ice.Config=client.config "orchestrator"
echo ""
echo "Ahora nos vamos a hacer una transferencia de dicho vídeo"
./client.py --Ice.Config=client.config "orchestrator" --transfer "Roblox Death Sound - OOF _ Sound Effect.mp3"
echo ""
echo "Esto es una demostración, para un ejemplo más detallado utilice makefile o directamente client.py"