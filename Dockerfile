FROM ubuntu:20.04

# Optional ARG for speeding up our make install
# By default if no arg is passed it'll be 2 (same defaults as WRF/WPS)
ARG CORES="2"
# Install basic requirements
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
    gcc gfortran g++ git wget build-essential \
    libpng-dev libcurl4-gnutls-dev m4 software-properties-common \
    csh make libxml2 libxml2-dev expect

# Set environment variables
ENV DIR=/root/wrf_dependencies
RUN mkdir -p "${DIR}"
ENV NETCDF="${DIR}/netcdf"
ENV CC=gcc \
    CXX=g++ \
    FC=gfortran \
    FCFLAGS="-m64" \
    F77=gfortran \
    FFLAGS="-m64" \
    JASPERLIB="${DIR}/grib2/lib" \
    JASPERINC="${DIR}/grib2/include" \
    PATH="${DIR}/mpich/bin:${DIR}/netcdf/bin:${DIR}/hdf5/bin:${PATH}" \
    HDF5="${DIR}/hdf5/lib" \
    LDFLAGS="-L${DIR}/grib2/lib -L${DIR}/hdf5/lib -L${DIR}/netcdf/lib" \
    CPPFLAGS="-I${NETCDF}/include -I${DIR}/grib2/include -fcommon" \
    LD_LIBRARY_PATH="${NETCDF}/lib:${DIR}/grib2/lib" \
    WRF_DIR="/home/WRF-SFIRE"


# Copy dependency installation script
COPY setup_dependencies.sh /setup_dependencies.sh
RUN chmod +x /setup_dependencies.sh

# Run the dependency installation script
RUN /setup_dependencies.sh ${CORES:+"$CORES"}

WORKDIR /home

# Clone WRF-SFIRE and WPS
RUN git clone --recurse-submodule https://github.com/openwfm/WRF-SFIRE && \
    git clone --recurse-submodule https://github.com/wrf-model/WPS.git

# Copy sfire install script
COPY setup_sfire.sh /setup_sfire.sh
RUN chmod +x /setup_sfire.sh

RUN /setup_sfire.sh ${CORES:+"$CORES"}

# Copy wps install script
COPY setup_wps.sh /setup_wps.sh
RUN chmod +x /setup_wps.sh

RUN /setup_wps.sh

WORKDIR /home/WRF-SFIRE

# Command to run when container starts
CMD ["/bin/bash"]
