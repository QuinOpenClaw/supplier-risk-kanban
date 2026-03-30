#!/bin/bash
cd /opt/apps/supplier-risk-tool/repo
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 3050
