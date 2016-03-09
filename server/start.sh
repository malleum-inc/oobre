#!/bin/sh

echo 'Starting OOBRE... '
export PYTHONPATH=../examples:../src
twistd -y oobre.tac
echo 'done.'