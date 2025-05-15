# Looking into WRF-SFIRE

## Resources

 - https://unr-wrf-fire.readthedocs.io/en/latest/index.html
 - https://www2.mmm.ucar.edu/wrf/OnLineTutorial/compilation_tutorial.php
 - https://github.com/wrf-model/WRF
 - https://github.com/wrf-model/WPS
 - https://github.com/wrf-model/Users_Guide/blob/main/fire.rst
 - https://www.mce2.org/11_aug_2_wrf_and_wps_compile%20(Dave%20Gill).pdf
 - https://github.com/openwfm/WRF-SFIRE

# Steps to Setup WRF-SFIRE

 1. Clone this repository and build the docker container

`docker build -t wrf-sfire --build-arg CORES=8 .`

`CORES=8` - This does not have to be 8, it can be a number between 1-20. By
default wrf-sfire compile script will pass -j 2 to make. If you are using a
higher number here and are running into compilation issues, I would try again
with a lower number. I haven't had time to look into it, but I think there
might be a potential race condition when using a higher number here.

 2. After a successful build run the docker container

`docker run -it wrf-sfire`

 3. Run a test!

`cd test/em_fire/hill`

`./ideal.exe `

`./wrf.exe`

# Steps to create a spack package to install from the package.py
- Coming soon
