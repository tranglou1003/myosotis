#!/bin/sh
set -e

ollama pull aisingapore/Llama-SEA-LION-v3.5-8B-R:latest

exec ollama serve
