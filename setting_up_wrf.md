# Looking into WRF

## Resources

 - https://unr-wrf-fire.readthedocs.io/en/latest/index.html
 - https://www2.mmm.ucar.edu/wrf/OnLineTutorial/compilation_tutorial.php
 - https://github.com/wrf-model/WRF
 - https://github.com/wrf-model/WPS
 - https://github.com/wrf-model/Users_Guide/blob/main/fire.rst
 - https://www.mce2.org/11_aug_2_wrf_and_wps_compile%20(Dave%20Gill).pdf

# Steps to Setup WRF

 1. Setup a VM or WSL2 ubuntu 20.04 instance
 2. Using the below bash script should do most of the setup
```bash
#!/bin/bash
set -e

sudo apt-get -y update
sudo apt-get -y install gcc gfortran g++ git wget build-essential libpng-dev libcurl4-gnutls-dev m4 software-properties-common
sudo add-apt-repository universe
sudo apt-get -y install csh make libxml2 libxml2-dev


export DIR="$HOME/wrf_dependencies"
export CC="gcc"
export CXX="g++"
export FC="gfortran"
export FCFLAGS="-m64"
export F77="gfortran"
export FFLAGS="-m64"
export JASPERLIB="$DIR/grib2/lib"
export JASPERINC="$DIR/grib2/include"
export PATH="$DIR/mpich/bin:$DIR/netcdf/bin:$DIR/hdf5/bin:$PATH"
export NETCDF="$DIR/netcdf"
export HDF5="$DIR/hdf5/lib"
export LDFLAGS="-L$DIR/grib2/lib -L${DIR}/hdf5/lib -L${DIR}/netcdf/lib"
export CPPFLAGS="-I$NETCDF/include -I$DIR/grib2/include -fcommon"
export LD_LIBRARY_PATH="$NETCDF/lib:$DIR/grib2/lib"

mkdir $DIR
cd $DIR
echo -e "starting on hdf5\n"
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.10/hdf5-1.10.5/src/hdf5-1.10.5.tar.gz
tar xzvf hdf5-1.10.5.tar.gz > hdf5_tar.log 2>&1
cd hdf5-1.10.5
echo -e "configuring hdf5\n"
./configure --prefix=$DIR/hdf5 --enable-fortran > hdf5_configure.log 2>&1
echo -e "running make on hdf5\n"
make -j > hdf5_make.log 2>&1
echo -e "running make install on hdf5\n"
make -j install > hdf5_make_install.log 2>&1
cd ..

echo -e "starting on netcdf-c\n"
wget https://downloads.unidata.ucar.edu/netcdf-c/4.9.3/netcdf-c-4.9.3.tar.gz
tar xzvf netcdf-c-4.9.3.tar.gz > netcdf-c_tar.log 2>&1
cd $DIR/netcdf-c-4.9.3/
echo -e "configuring netcdf-c\n"
./configure --prefix=$DIR/netcdf --enable-netcdf-4 LDFLAGS="-L$DIR/hdf5/lib" CPPFLAGS="-I$DIR/hdf5/include" > netcdf-c_configure.log 2>&1
echo -e "running make on netcdf-c\n"
make -j > netcdf-c_make.log 2>&1
echo -e "running make install on netcdf-c\n"
make -j install netcdf-c_make_install.log 2>&1
cd ..

echo -e "starting on netcdf-fortran\n"
wget https://downloads.unidata.ucar.edu/netcdf-fortran/4.6.2/netcdf-fortran-4.6.2.tar.gz
tar xzvf netcdf-fortran-4.6.2.tar.gz > netcdf-fortran_tar.log 2>&1
cd netcdf-fortran-4.6.2
echo -e "configuring netcdf-fortran\n"
./configure --prefix=$DIR/netcdf LDFLAGS="$LDFLAGS" CPPFLAGS="$CPPFLAGS" > netcdf-fortran_configure.log 2>&1
echo -e "running make on netcdf-fortran\n"
make -j > netcdf-fortran_make.log 2>&1
echo -e "running make install on netcdf-fortran\n"
make -j install netcdf-fortran_make_install.log 2>&1
cd ..

echo -e "starting on mpich\n"
wget https://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/mpich-3.0.4.tar.gz
tar xzvf mpich-3.0.4.tar.gz > mpich_tar.log 2>&1
cd mpich-3.0.4
echo -e "configuring mpich\n"
./configure --prefix=$DIR/mpich > mpich_configure.log 2>&1
echo -e "running make on mpich\n"
make -j > mpich_make.log 2>&1
echo -e "running make install on mpich\n"
make -j install > mpich_make_install.log 2>&1
cd ..

echo -e "starting on zlib\n"
wget https://www.zlib.net/zlib-1.3.1.tar.gz > zlib_tar.log 2>&1
tar xzvf zlib-1.3.1.tar.gz
cd zlib-1.3.1
echo -e "configuring zlib\n"
./configure --prefix=$DIR/grib2 > zlib_configure.log 2>&1
echo -e "running make on zlib\n"
make -j > zlib_make.log 2>&1
echo -e "running make install on zlib\n"
make -j install > zlib_make_install.log 2>&1
cd ..

echo -e "starting on jasper\n"
wget http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/jasper-1.900.1.tar.gz
tar xzvf jasper-1.900.1.tar.gz > jasper_tar.log 2>&1
cd jasper-1.900.1
echo -e "configuring jasper\n"
./configure --prefix=$DIR/grib2 > jasper_configure.log 2>&1
echo -e "running make on jasper\n"
make -j > jasper_make.log 2>&1
echo -e "running make install on jasper\n"
make -j install > jasper_make_install.log 2>&1
cd ../../
```
3. Clone WRF and WPS submodules into the home directory
`git clone --recurse-submodule https://github.com/wrf-model/WRF.git`
`git clone --recurse-submodule https://github.com/wrf-model/WPS.git`
4. Change into the WRF directory and run the configure script
`cd ~/WRF/`
`./configure`- this will prompt you for some options. For the first one use 34,1 and for the second one use the default
5. Compile WRF
`./compile em_fire >& log.compile`
6. Change into the WPS directory and run the configure script
`cd ../WPS`
`./configure`- you'll be prompted for an option and should use 1
7. Compile WPS
`./compile`
8. Run a test!
`cd ../WRF/test/em_fire/`
`ln -sf namelist.input_two_fires namelist.input`
`ln -sf input_sounding_two_fires input_sounding`
`./ideal.exe `
`./wrf.exe`

```
Quilting with   1 groups of   0 I/O tasks.
 Ntasks in X            1 , ntasks in Y            1
  Domain # 1: dx =    50.000 m
WRF V4.7.0 MODEL
git commit eeacb821626feb34c62c3c1e169594d886d13adb
 *************************************
 Parent domain
 ids,ide,jds,jde            1          43           1          43
 ims,ime,jms,jme           -4          48          -4          48
 ips,ipe,jps,jpe            1          43           1          43
 *************************************
DYNAMICS OPTION: Eulerian Mass Coordinate
   alloc_space_field: domain            1 ,             115107228  bytes allocated
  med_initialdata_input: calling input_input
   Input data is acceptable to use: wrfinput_d01
 CURRENT DATE          = 2006-01-01_09:00:00
 SIMULATION START DATE = 2006-01-01_09:00:00
Timing for processing wrfinput file (stream 0) for domain        1:    0.06054 elapsed seconds
Max map factor in domain 1 =  0.00. Scale the dt in the model accordingly.
FIRE:fire_driver_em_init: FIRE initialization start
FIRE:Using ideal ignition coordinates, m from the lower left domain corner
FIRE:Reading file namelist.fire
FIRE:Namelist fuel_moisture not found, using defaults
Timing for Writing wrfout_d01_2006-01-01_09:00:00 for domain        1:    0.09120 elapsed seconds
 Tile Strategy is not specified. Assuming 1D-Y
WRF TILE   1 IS      1 IE     43 JS      1 JE     43
WRF NUMBER OF TILES =   1
FIRE:Time       0.500 s Average wind           0.125E+01 m/s
FIRE:Time       0.500 s Maximum wind           0.124E+01 m/s
FIRE:Time       0.500 s Fire area              0.000E+00 m^2
FIRE:Time       0.500 s Heat output            0.000E+00 W
FIRE:Time       0.500 s Max heat flux          0.000E+00 W/m^2
FIRE:Time       0.500 s Latent heat output     0.000E+00 W
FIRE:Time       0.500 s Max latent heat flux   0.000E+00 W/m^2
d01 2006-01-01_09:00:00  ----------------------------------------
d01 2006-01-01_09:00:00  W-DAMPING  BEGINS AT W-COURANT NUMBER =    1.00000000
d01 2006-01-01_09:00:00  ----------------------------------------
Timing for main: time 2006-01-01_09:00:00 on domain   1:    0.19990 elapsed seconds
FIRE:Time       1.000 s Average wind           0.125E+01 m/s
FIRE:Time       1.000 s Maximum wind           0.124E+01 m/s
FIRE:Time       1.000 s Fire area              0.000E+00 m^2
FIRE:Time       1.000 s Heat output            0.000E+00 W
FIRE:Time       1.000 s Max heat flux          0.000E+00 W/m^2
FIRE:Time       1.000 s Latent heat output     0.000E+00 W
FIRE:Time       1.000 s Max latent heat flux   0.000E+00 W/m^2
Timing for main: time 2006-01-01_09:00:01 on domain   1:    0.07687 elapsed seconds

......

FIRE:Time      18.000 s Average wind           0.125E+01 m/s
FIRE:Time      18.000 s Maximum wind           0.124E+01 m/s
FIRE:Time      18.000 s Fire area              0.000E+00 m^2
FIRE:Time      18.000 s Heat output            0.000E+00 W
FIRE:Time      18.000 s Max heat flux          0.000E+00 W/m^2
FIRE:Time      18.000 s Latent heat output     0.000E+00 W
FIRE:Time      18.000 s Max latent heat flux   0.000E+00 W/m^2
Timing for main: time 2006-01-01_09:00:18 on domain   1:    0.07399 elapsed seconds
FIRE:Time      18.500 s Average wind           0.125E+01 m/s
FIRE:Time      18.500 s Maximum wind           0.124E+01 m/s
```
