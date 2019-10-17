#!/bin/bash
# $1 how long mtr check (second)
for node in 10.19.140.6 10.19.140.10 10.19.140.11
do
	mtr -n -i 1 -c $1 -s 1024 -r 172.16.128.5 > $node.log
	if [[ $? -ne 0 ]]
	then
         echo "err exist"
	 exit 0
	fi
done