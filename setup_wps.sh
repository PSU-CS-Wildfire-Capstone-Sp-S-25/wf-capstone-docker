#!/bin/bash
set -e
# This script uses expect to automate the configuration/installation of
# and WPS

printf "Starting installation of WPS\n"
cd /home/WPS

./clean -a

/bin/expect << EOF
log_file wps_configure.log
spawn ./configure
expect -re "Enter selection "
send -- "1\r"
expect eof
EOF

if grep -q "Configuration successful." wps_configure.log;
then
    printf "\n\nWPS configuration was successful\n"
else
    printf "\n\nWPS configuration failed!\n"
    cat wps_configure.log
    exit 1
fi

printf "\nStarting compilation of wps!\n"
./compile > compile-wps.log 2>&1;
printf "\n\nWPS successfully built!\n"
ls -l ./*.exe
