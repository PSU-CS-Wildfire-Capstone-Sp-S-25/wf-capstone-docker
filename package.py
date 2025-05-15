# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# This is largely based on the already existing WRF package located here:
# https://github.com/spack/spack/blob/develop/var/spack/repos/spack_repo/builtin/packages/wrf/package.py
import glob
import re
import sys
import time
from os.path import basename
from pathlib import Path
from subprocess import PIPE, Popen

from spack.package import *

if sys.platform != "win32":
    from fcntl import F_GETFL, F_SETFL, fcntl
    from os import O_NONBLOCK

re_optline = re.compile(r"\s+[0-9]+\..*\((serial|smpar|dmpar|dm\+sm)\)\s+")
re_paroptname = re.compile(r"\((serial|smpar|dmpar|dm\+sm)\)")
re_paroptnum = re.compile(r"\s+([0-9]+)\.\s+\(")
re_nestline = re.compile(r"\(([0-9]+=[^)0-9]+)+\)")
re_nestoptnum = re.compile(r"([0-9]+)=")
re_nestoptname = re.compile(r"=([^,)]+)")


def setNonBlocking(fd):
    """
    Set the given file descriptor to non-blocking
    Non-blocking pipes are not supported on windows
    """
    flags = fcntl(fd, F_GETFL) | O_NONBLOCK
    fcntl(fd, F_SETFL, flags)


def collect_platform_options(stdoutpipe):
    # Attempt to parse to collect options
    optiondict = {}
    for line in stdoutpipe.splitlines():
        if re_optline.match(line):
            numbers = re_paroptnum.findall(line)
            entries = re_paroptname.findall(line)
            paropts = dict(zip(entries, numbers))
            platline = re_optline.sub("", line).strip()
            optiondict[platline] = paropts

    return optiondict


def collect_nesting_options(stdoutpipe):
    nestoptline = re_nestline.search(stdoutpipe)[0]
    nestoptnum = re_nestoptnum.findall(nestoptline)
    nestoptname = re_nestoptname.findall(nestoptline)
    nestoptname = [x.replace(" ", "_") for x in nestoptname]

    return dict(zip(nestoptname, nestoptnum))


class WrfSfire(Package):
    """A coupled weather-fire forecasting model built on top of Weather Research
    and Forecasting (WRF-SFIRE)."""

    homepage = "https://wiki.openwfm.org/wiki/WRF-SFIRE"
    git = "https://github.com/openwfm/WRF-SFIRE.git"
    maintainers("relia1")

    version("W4.4-S0.1", commit="c959580092191b315d936566361314f9cab669ec", submodules=True)

    variant(
        "build_type",
        default="dmpar",
        description="Build type",
        values=("serial", "smpar", "dmpar", "dm+sm"),
    )
    variant(
        "nesting",
        default="basic",
        description="Nesting",
        values=("no_nesting", "basic", "preset_moves", "vortex_following"),
    )
    variant(
        "compile_type",
        default="em_real",
        description="Compile type",
        values=(
            "em_real",
            "em_fire",
            "em_quarter_ss",
            "em_b_wave",
            "em_les",
            "em_heldsuarez",
            "em_tropical_cyclone",
            "em_hill2d_x",
            "em_squall2d_x",
            "em_squall2d_y",
            "em_grav2d_x",
            "em_seabreeze2d_x",
            "em_scm_xy",
        ),
    )
    variant("pnetcdf", default=True, description="Parallel IO support through Pnetcdf library")
    variant("chem", default=False, description="Enable WRF-Chem")
    variant("netcdf_classic", default=False, description="Use NetCDF without HDF5 compression")

    patch("../wrf/patches/4.2/arch.Config.pl.patch", when="@W4.4:W4.5.1")
    patch("../wrf/patches/4.2/arch.conf_tokens.patch", when="@W4.4:")
    patch("../wrf/patches/4.2/external.io_netcdf.makefile.patch", when="@W4.4:W4.5.1")
    patch("../wrf/patches/4.2/var.gen_be.Makefile.patch", when="@W4.4:")
    patch("../wrf/patches/4.2/hdf5_fix.patch", when="@W4.4:W4.5.1 %aocc")
    patch(
        "../wrf/patches/4.2/add_tools_flags_acfl2304.patch",
        when="@W4.4:W4.4.2 target=aarch64: %arm@23.04.1:",
    )

    patch("../wrf/patches/4.3/add_aarch64.patch", when="@W4.4:4.4.2 target=aarch64: %gcc")
    patch("../wrf/patches/4.3/add_aarch64_acfl.patch", when="@W4.4:W4.4.2 target=aarch64: %arm")

    patch("../wrf/patches/4.4/arch.postamble.patch", when="@W4.4:W4.5.1")
    patch("../wrf/patches/4.4/configure.patch", when="@W4.4:W4.4.2")
    patch("../wrf/patches/4.4/ifx.patch", when="@W4.4: %oneapi")

    # Various syntax fixes found by FPT tool
    patch("../wrf/patches/4.2/configure_fujitsu.patch", when="@W4 %fj")

    patch("../wrf/patches/4.3/Makefile.patch", when="@W4.4:W4.5.1")
    patch("../wrf/patches/4.3/fujitsu.patch", when="@W4.4 %fj")
    # Add ARM compiler support

    depends_on("c", type="build")  # generated
    depends_on("fortran", type="build")  # generated

    depends_on("pkgconfig", type=("build"))
    depends_on("libtirpc")

    depends_on("mpi")
    # According to:
    # http://www2.mmm.ucar.edu/wrf/users/docs/user_guide_v4/v4.0/users_guide_chap2.html#_Required_Compilers_and_1
    # Section: "Required/Optional Libraries to Download"
    depends_on("parallel-netcdf", when="+pnetcdf")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("jasper")
    depends_on("libpng")
    depends_on("zlib-api")
    depends_on("perl")
    depends_on("jemalloc", when="%aocc")
    depends_on("hdf5+hl+mpi")
    # build script use csh
    depends_on("tcsh", type=("build"))
    # time is not installed on all systems b/c bash provides it
    # this fixes that for csh install scripts
    depends_on("time", type=("build"))
    depends_on("m4", type="build")
    depends_on("libtool", type="build")

    requires(
        "%gcc",
        "%intel",
        "%arm",
        "%aocc",
        "%fj",
        "%oneapi",
        policy="one_of",
        msg="WRF supports only the GCC, Intel, AMD of Fujitsu compilers",
    )
    conflicts(
        "%oneapi", when="@:4.3", msg="Intel oneapi compiler patch only added for version 4.4"
    )
    phases = ["configure", "build", "install"]

    def setup_run_environment(self, env: EnvironmentModifications) -> None:
        env.set("WRF_HOME", self.prefix)
        env.append_path("PATH", self.prefix.main)
        env.append_path("PATH", self.prefix.tools)

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        env.set("NETCDF", self.spec["netcdf-c"].prefix)
        if "+pnetcdf" in self.spec:
            env.set("PNETCDF", self.spec["parallel-netcdf"].prefix)
        # Add WRF-Chem module
        if "+chem" in self.spec:
            env.set("WRF_CHEM", "1")
        if "+netcdf_classic" in self.spec:
            env.set("NETCDF_classic", "1")
        # This gets used via the applied patch files
        env.set("NETCDFF", self.spec["netcdf-fortran"].prefix)
        env.set("PHDF5", self.spec["hdf5"].prefix)
        env.set("JASPERINC", self.spec["jasper"].prefix.include)
        env.set("JASPERLIB", self.spec["jasper"].prefix.lib)

        if self.spec.satisfies("%aocc"):
            env.set("WRFIO_NCD_LARGE_FILE_SUPPORT", "1")
            env.set("HDF5", self.spec["hdf5"].prefix)
            env.prepend_path("PATH", ancestor(self.compiler.cc))

    def flag_handler(self, name, flags):
        # Force FCFLAGS/FFLAGS by adding directly into spack compiler wrappers.
        if self.spec.satisfies("@W3.9.1.1: %gcc@10:") and name == "fflags":
            flags.extend(["-fallow-argument-mismatch", "-fallow-invalid-boz"])
        return (flags, None, None)

    def patch(self):
        # Let's not assume csh is intalled in bin
        files = glob.glob("*.csh")

        filter_file("^#!/bin/csh -f", "#!/usr/bin/env csh", *files)
        filter_file("^#!/bin/csh", "#!/usr/bin/env csh", *files)

    @run_before("configure", when="%aocc@4:")
    def create_aocc_config(self):
        param = {
            "MPICC": self.spec["mpi"].mpicc,
            "MPIFC": self.spec["mpi"].mpifc,
            "CTSM_SUBST": (
                "CONFIGURE_D_CTSM"
            ),
            "NETCDFPAR_BUILD": (
                "CONFIGURE_NETCDFPAR_BUILD" if self.spec.satisfies("@W4.4:") else ""
            ),
        }

        zen_conf = (Path(__file__).parent / "aocc_config.inc").read_text().format(**param)

        if self.spec.satisfies("@W4.0:"):
            filter_file("#insert new stanza here", zen_conf, "arch/configure.defaults")
        else:
            filter_file("#insert new stanza here", zen_conf, "arch/configure_new.defaults")

    def answer_configure_question(self, outputbuf):
        # Platform options question:
        if "Please select from among the following" in outputbuf:
            options = collect_platform_options(outputbuf)
            comp_pair = "%s/%s" % (
                basename(self.compiler.fc).split("-")[0],
                basename(self.compiler.cc).split("-")[0],
            )
            compiler_matches = dict((x, y) for x, y in options.items() if comp_pair in x.lower())
            if len(compiler_matches) > 1:
                tty.warn("Found multiple potential build options")
            try:
                compiler_key = min(compiler_matches.keys(), key=len)
                tty.warn("Selected build option %s." % compiler_key)
                return (
                    "%s\n" % compiler_matches[compiler_key][self.spec.variants["build_type"].value]
                )
            except KeyError:
                InstallError(
                    "build_type %s unsupported for %s compilers"
                    % (self.spec.variants["build_type"].value, comp_pair)
                )

        if "Compile for nesting?" in outputbuf:
            options = collect_nesting_options(outputbuf)
            try:
                return "%s\n" % options[self.spec.variants["nesting"].value]
            except KeyError:
                InstallError("Failed to parse correct nesting option")

    def do_configure_fixup(self):
        # Fix mpi compiler wrapper aliases

        config = FileFilter(join_path("arch", "configure.defaults"))

        if self.spec.satisfies("%aocc"):
            config.filter(
                "^DM_FC.*mpif90 -DMPI2SUPPORT",
                "DM_FC = {0}".format(self.spec["mpi"].mpifc + " -DMPI2_SUPPORT"),
            )
            config.filter(
                "^DM_.CC*mpicc -DMPI2SUPPORT",
                "DM_CC = {0}".format(self.spec["mpi"].mpicc) + " -DMPI2_SUPPORT",
            )

        if self.spec.satisfies("@W4.2: %intel"):
            config.filter("^DM_FC.*mpif90", "DM_FC = {0}".format(self.spec["mpi"].mpifc))
            config.filter("^DM_CC.*mpicc", "DM_CC = {0}".format(self.spec["mpi"].mpicc))

        if self.spec.satisfies("%gcc@14:"):
            config.filter(
                "^CFLAGS_LOCAL(.*?)=([^#\n\r]*)(.*)$", r"CFLAGS_LOCAL\1= \2 -fpermissive \3"
            )
            config.filter("^CC_TOOLS(.*?)=([^#\n\r]*)(.*)$", r"CC_TOOLS\1=\2 -fpermissive \3")

    def configure(self, spec, prefix):
        # Remove broken default options...
        self.do_configure_fixup()

        p = Popen("./configure", stdin=PIPE, stdout=PIPE, stderr=PIPE)
        if sys.platform != "win32":
            setNonBlocking(p.stdout)
            setNonBlocking(p.stderr)

        # Because of WRFs custom configure scripts that require interactive
        # input we need to parse and respond to questions.  The details can
        # vary somewhat with the exact version, so try to detect and fail
        # gracefully on unexpected questions.
        stallcounter = 0
        outputbuf = ""
        while True:
            line = p.stderr.readline().decode()
            if not line:
                line = p.stdout.readline().decode()
            if not line:
                if p.poll() is not None:
                    returncode = p.returncode
                    break
                if stallcounter > 300:
                    raise InstallError(
                        "Output stalled for 30s, presumably an " "undetected question."
                    )
                time.sleep(0.1)  # Try to do a bit of rate limiting
                stallcounter += 1
                continue
            sys.stdout.write(line)
            stallcounter = 0
            outputbuf += line
            if "Enter selection" in outputbuf or "Compile for nesting" in outputbuf:
                answer = self.answer_configure_question(outputbuf)
                p.stdin.write(answer.encode())
                p.stdin.flush()
                outputbuf = ""

        if returncode != 0:
            raise InstallError("Configure failed - unknown error")

    def run_compile_script(self):
        csh_bin = self.spec["tcsh"].prefix.bin.csh
        csh = Executable(csh_bin)

        # num of compile jobs capped at 20 in wrf
        num_jobs = str(min(int(make_jobs), 20))

        # Now run the compile script and track the output to check for
        # failure/success We need to do this because upstream use `make -i -k`
        # and the custom compile script will always return zero regardless of
        # success or failure
        result_buf = csh(
            "./compile",
            "-j",
            num_jobs,
            self.spec.variants["compile_type"].value,
            output=str,
            error=str,
        )

        print(result_buf)
        if "Executables successfully built" in result_buf:
            return True

        return False

    def build(self, spec, prefix):
        result = self.run_compile_script()

        if not result:
            tty.warn("Compilation failed first time (WRF idiosyncrasies?) " "- trying again...")
            result = self.run_compile_script()

        if not result:
            raise InstallError("Compile failed. Check the output log for details.")

    def install(self, spec, prefix):
        # Save all install files as many are needed for WPS and WRF runs
        install_tree(".", prefix)
