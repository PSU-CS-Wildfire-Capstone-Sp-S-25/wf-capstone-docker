#!/bin/bash
set -e

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
make -j install > netcdf-c_make_install.log 2>&1
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
make -j install > netcdf-fortran_make_install.log 2>&1
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
