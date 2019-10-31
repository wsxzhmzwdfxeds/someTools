#!/usr/bin/bash

journalctl --boot > /tmp/temp

python  tools/oomcheck.py --file=/tmp/temp 2>/dev/null
