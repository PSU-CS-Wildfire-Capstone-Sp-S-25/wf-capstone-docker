#!/bin/bash
set -e
# This script uses expect to automate the configuration/installation of
# WRF-SFIRE

# The Dockerfile has an optional ARG that we
number_ofjobs_for_make=${1}

printf "Starting installation of S-Fire\n"
cd /home/WRF-SFIRE

./clean -a

# Configure script runs into a slight error when trying to do a comparison with
# == instead of the = it should be using. So this updates the == to = on just
# line 919
sed -i '919s/==/=/' configure

/bin/expect << EOF
log_file sfire_configure.log
spawn ./configure
expect -re "Enter selection "
send -- "34,1\r"
expect "Compile for nesting?"
send -- "1\r"
expect eof
EOF

if grep -q "Configuration successful!" sfire_configure.log;
then
    printf "\n\nWRF-SFIRE configuration was successful"
else
    printf "\n\nWRF-SFIRE configuration failed!\n"
    cat sfire_configure.log
    exit 1
fi

printf "\nStarting compilation of sfire!\n"
./compile -j "${number_ofjobs_for_make:-2}" em_fire > compile-sfire.log 2>&1

if grep -q "Executables successfully built" compile-sfire.log;
then
    printf "\n\nS-Fire Executables successfully built!\n"
    ls -l main/*.exe
else
    printf "\n\nS-Fire compilation failed!\n"
    grep -i error compile-sfire.log | grep -v "(ignored)"
    exit 1
fi
