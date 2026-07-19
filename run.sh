#!/bin/bash
cd "$(dirname "$0")"
python3 update.py && python3 -m VideoEncoder

