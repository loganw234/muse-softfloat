#!/usr/bin/env bash
echo "child sees MSF_BOARD_SERIAL=[${MSF_BOARD_SERIAL:-EMPTY}] MSF_BOARD_PORT=[${MSF_BOARD_PORT:-EMPTY}] MSF_PYTHON=[${MSF_PYTHON:-EMPTY}]"
env | grep -i '^MSF_' || echo "no MSF_ vars in env"
