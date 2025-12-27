#! /usr/bin/env bash
set -e
set -x

# Run tests directly - no pre-start checks needed for base version
bash scripts/test.sh "$@"
