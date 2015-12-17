#!/bin/sh

echo -n 'Stopping OOBRE... '
kill -15 $(cat twistd.pid)
echo 'done'