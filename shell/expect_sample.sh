#!/bin/bash

passwd='111111'
/usr/bin/expect <<-EOF
set time 30

spawn ssh icy@10.20.38.187 ls
expect {
"*yes/no" { send "yes\r"; exp_continue }
"*assword:" { send "$passwd\r" } 
}
expect eof
EOF
