#!/usr/bin/env bash

if [ -n "${BASH_VERSION:-}" ]; then
  _ENV_FILE="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION:-}" ]; then
  _ENV_FILE="${(%):-%x}"
else
  _ENV_FILE="$0"
fi

ROOT_DIR="$(cd "$(dirname "$_ENV_FILE")/.." && pwd)"
PICKER_HOME="$ROOT_DIR/local/picker"
JAVA_HOME="$ROOT_DIR/local/jre17"
MILL_HOME="$ROOT_DIR/local/mill"
NUTSHELL_HOME="$ROOT_DIR/upstream/NutShell"

export PICKER_HOME
export JAVA_HOME
export MILL_HOME
export NOOP_HOME="$NUTSHELL_HOME"
export PATH="$PICKER_HOME/bin:$JAVA_HOME/bin:$MILL_HOME/bin:$PATH"
export PYTHONPATH="$PICKER_HOME/share/picker/python:${PYTHONPATH:-}"
