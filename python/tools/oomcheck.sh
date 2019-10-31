#!/usr/bin/bash

journalctl --boot > /tmp/temp

/home/core/bin/python  tools/oomcheck.py --file=/tmp/temp 2>/dev/null
