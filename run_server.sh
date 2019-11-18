#!/usr/bash
python3 Downloader.py --Ice.Config=Server.config | tee proxy_dwn.out &
sleep 3
python3 Orchestrator.py "$(head -1 proxy_dwn.out)" --Ice.Config=Server.config | tee proxy_orch.out
