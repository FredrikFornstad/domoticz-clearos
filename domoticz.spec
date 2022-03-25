%global boostver 1_72_0
%global jsoncpp_ver 2a6e163b02ac5044d74a44ed15f8aa7af687aea5
%global minizip_ver 78eb93e8e0ba228f37b197d2022d66b73856c9ff
%global sqlite_amalgamation_ver afb008e9d7185f84c23a590dd06538fb9b2f1e19
%global fmt_ver a1c6bfd77b409f21e234cc7042795ca4d31fa020

Name:		domoticz
Version:	2022.1
Release:	2%{?dist}
Summary:	Domoticz Home Automation System

License:	GNU GPL 3
URL:		http://www.domoticz.com
Source0:	https://github.com/%{name}/%{name}/archive/%{version}.tar.gz
#Source0:	https://github.com/domoticz/domoticz/archive/41b1ae7f68b11d6e71005ad453d4ae85978c068f.zip

Source1:	https://dl.bintray.com/boostorg/release/1.72.0/source/boost_%{boostver}.tar.bz2
Source2: 	ver.py
Source3:        libboost_thread.so
Source4:	readme.txt
Source5:	run-domoticz
Source6:	https://github.com/open-source-parsers/jsoncpp/archive/%{jsoncpp_ver}.zip
Source7:	https://github.com/domoticz/minizip/archive/%{minizip_ver}.zip
Source8:	https://github.com/azadkuh/sqlite-amalgamation/archive/%{sqlite_amalgamation_ver}.zip
Source9:	https://www.lua.org/ftp/lua-5.4.3.tar.gz
Source10:	CMakeLists-lua.txt
Source11:	CMakeLists-lua-src.txt
Source12:	https://github.com/fmtlib/fmt/archive/%{fmt_ver}.zip

Patch1:		CMakeLists.txt.patch
Patch2:		download_update.sh.patch
Patch3:		update_domoticz.patch
Patch4:		updatedomo.patch
Patch5:		setup.html.patch
Patch6:		index.html.patch
Patch7:		restart_domoticz.patch
Patch8:		SQLHelper.cpp.patch
#Patch8:	History.txt.patch
Patch9:		domoticz.cpp.patch

# https://svn.boost.org/trac/boost/ticket/6150
Patch10: boost-1.50.0-fix-non-utf8-files.patch

# Add a manual page for bjam, based on the on-line documentation:
# http://www.boost.org/boost-build2/doc/html/bbv2/overview.html
Patch11: boost-1.48.0-add-bjam-man-page.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=828856
# https://bugzilla.redhat.com/show_bug.cgi?id=828857
# https://svn.boost.org/trac/boost/ticket/6701
Patch12: boost-1.58.0-pool.patch

# https://svn.boost.org/trac/boost/ticket/5637
Patch13: boost-1.57.0-mpl-print.patch

# https://svn.boost.org/trac/boost/ticket/9038
Patch14: boost-1.58.0-pool-test_linking.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1102667
Patch15: boost-1.57.0-python-libpython_dep.patch
Patch16: boost-1.66.0-python-abi_letters.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1190039
Patch17: boost-1.66.0-build-optflags.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1318383
Patch18: boost-1.66.0-no-rpath.patch


BuildRequires:	make cmake3
BuildRequires:	openssl11-devel git
BuildRequires:	curl-devel
BuildRequires:	devtoolset-9 devtoolset-9-build
BuildRequires:  libusb-devel systemd-devel

BuildRequires: m4

%ifarch x86_64
BuildRequires: libquadmath-devel
%endif

# BuildRequires: libstdc++-devel
BuildRequires: bzip2-devel
BuildRequires: zlib-devel
BuildRequires: python-devel python3-devel python34-devel
BuildRequires: libicu-devel
BuildRequires: libopenzwave-devel telldus-core-devel
BuildRequires: mosquitto-devel cereal-devel sqlite-devel

Requires: python python34 python34-devel bzip2 tar mosquitto cereal-devel openssl11-libs

%description
Domoticz is a Home Automation System that lets you monitor and configure various devices like:
Lights, Switches, various sensors/meters like Temperature, Rain, Wind, UV, Electricity, Gas, Water and much more.
Notifications/Alerts can be sent to any mobile device.

%prep
%setup -q -n %{name}-%{version}
#%setup -q -n domoticz-41b1ae7f68b11d6e71005ad453d4ae85978c068f
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1


# Ugly way of fixing the submodules that was omitted upstream
rm -rf extern/*
unzip -d extern %{SOURCE6}
unzip -d extern %{SOURCE7}
unzip -d extern %{SOURCE8}
unzip -d extern %{SOURCE12}

mv extern/jsoncpp-%{jsoncpp_ver} extern/jsoncpp
mv extern/minizip-%{minizip_ver} extern/minizip
mv extern/sqlite-amalgamation-%{sqlite_amalgamation_ver} extern/sqlite-amalgamation
mv extern/fmt-%{fmt_ver} extern/fmtlib
mkdir -p lua
tar -vxzf %{SOURCE9} --directory lua --strip 1
cp %{SOURCE10} lua/CMakeLists.txt
cp %{SOURCE11} lua/src/CMakeLists.txt

tar -vxjf %{SOURCE1}
cd boost_%{boostver}
%patch10 -p1
%patch11 -p1
%patch12 -p0
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1

cd ..

%build

%{?scl:scl enable %scl - << \EOFF}
# this is a gcc-9 enabled shell

%global python2_version %(/usr/bin/python2 %{SOURCE2})
%global python3_version %(/usr/bin/python3 %{SOURCE2})
%global python3_abiflags %(/usr/bin/python3-config --abiflags)

#
# The boost version in ClearOS 7 is too old. We therefore build a more modern version of boost
# and include the required files statically in the domoticz build not to cause trouble with other programs.
#

cd boost_%{boostver}
: PYTHON2_VERSION=%{python2_version}
: PYTHON3_VERSION=%{python3_version}
: PYTHON3_ABIFLAGS=%{python3_abiflags}

# There are many strict aliasing warnings, and it's not feasible to go
# through them all at this time.
# There are also lots of noisy but harmless unused local typedef warnings.

export RPM_OPT_FLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-local-typedefs -Wno-deprecated-declarations $(pkg-config --cflags openssl11)"
export RPM_LD_FLAGS="$RPM_LD_FLAGS $(pkg-config --libs openssl11)"

export CFLAGS="$CFLAGS $(pkg-config --cflags openssl11)"
export LDFLAGS="$LDFLAGS $(pkg-config --libs openssl11)"

cat > ./tools/build/src/user-config.jam << "EOF"
import os ;
local RPM_OPT_FLAGS = [ os.environ RPM_OPT_FLAGS ] ;
local RPM_LD_FLAGS = [ os.environ RPM_LD_FLAGS ] ;

using gcc : : : <compileflags>$(RPM_OPT_FLAGS) <linkflags>$(RPM_LD_FLAGS) ;

EOF

#using python : %{python2_version} : /usr/bin/python2 : /usr/include/python%{python2_version} : : : : ;
#using python : %{python3_version} : /usr/bin/python3 : /usr/include/python%{python3_version}%{python3_abiflags} : : : : %{python3_abiflags} ;
#
#EOF

./bootstrap.sh --with-toolset=gcc --with-icu

# N.B. When we build the following with PCH, parts of boost (math
# library in particular) end up being built second time during
# installation.  Unsure why that is, but all sub-builds need to be
# built with pch=off to avoid this.
#


# TEXT below IS REMOVED ------------------------------------------------------------------
# The "python=2.*" bit tells jam that we want to _also_ build 2.*, not
# just 3.*.  When omitted, it just builds for python 3 twice, once
# calling the library libboost_python and once libboost_python3.  I
# assume this is for backward compatibility for apps that are used to
# linking against -lboost_python, for when 2->3 transition is
# eventually done.
# To HERE ------------------------------------------------------------------------------

echo ============================= build serial ==================
./b2 -d+2 -q %{?_smp_mflags} \
        --without-mpi --without-graph_parallel --build-dir=serial \
        variant=release threading=multi debug-symbols=on pch=off \
	stage
#        python=%{python2_version} stage

# See libs/thread/build/Jamfile.v2 for where this file comes from.
if [ $(find serial -type f -name has_atomic_flag_lockfree \
                -print -quit | wc -l) -ne 0 ]; then
        DEF=D
else
        DEF=U
fi

m4 -${DEF}HAS_ATOMIC_FLAG_LOCKFREE -DVERSION=%{boost_ver} \
        %{SOURCE3} > $(basename %{SOURCE3})

# NEW PART HERE--------------------------------------------------------------------------
# Previously, we built python 2.x and 3.x interfaces simultaneously.
# However, this does not work once trying to build other Python components
# such as libboost_numpy.  Therefore, we build for each separately, while
# minimizing duplicate compilation as much as possible.

cat > python3-config.jam << "EOF"
import os ;
local RPM_OPT_FLAGS = [ os.environ RPM_OPT_FLAGS ] ;
local RPM_LD_FLAGS = [ os.environ RPM_LD_FLAGS ] ;

using gcc : : : <compileflags>$(RPM_OPT_FLAGS) <linkflags>$(RPM_LD_FLAGS) ;
EOF

cat >> python3-config.jam << EOF
#using python : %{python3_version} : /usr/bin/python3 : /usr/include/python%{python3_version}${PYTHON3_ABIFLAGS} : : : : ${PYTHON3_ABIFLAGS} ;
using python : %{python3_version} : /usr/bin/python3 : /usr/include/python%{python3_version}%{python3_abiflags} : : : : %{python3_abiflags} ;
EOF

echo ============================= build serial-py3 ==================
./b2 -d+2 -q %{?_smp_mflags} \
	--user-config=./python3-config.jam \
	--with-python --build-dir=serial-py3 \
	variant=release threading=multi debug-symbols=on pch=off \
	python=%{python3_version} stage


echo ============================= build Boost.Build ==================
(cd tools/build
 ./bootstrap.sh --with-toolset=gcc)

#
# Boost is prepared, move on to build domoticz
#

cd ..

#cmake3 . -DCMAKE_BUILD_TYPE=Release -DBOOST_ROOT:PATH=%{_builddir}/%{name}-%{version}/boost_%{boostver} -DBOOST_LIBRARYDIR=%{_builddir}/%{name}-%{version}/boost_%{boostver}/stage/lib
cmake3 . -DOPENSSL_ROOT_DIR=%{_includedir}/openssl11 -DOPENSSL_SSL_LIBRARY=%{_libdir}/openssl11/libssl.so -DOPENSSL_CRYPTO_LIBRARY=%{_libdir}/openssl11/libcrypto.so \
-DCMAKE_BUILD_TYPE=Release -DBOOST_ROOT:PATH=%{_builddir}/%{name}-%{version}/boost_%{boostver}  -DBOOST_LIBRARYDIR=%{_builddir}/%{name}-%{version}/boost_%{boostver}/stage/lib
make

# End of GCC-9 enabled section
%{?scl:EOFF}

%install
%make_install
%{__install} -m0644 %{SOURCE4} ${RPM_BUILD_ROOT}%{_datadir}/%{name}/readme.txt
%{__install} -m0754 %{SOURCE5} ${RPM_BUILD_ROOT}%{_datadir}/%{name}/run-domoticz
mkdir -m 775 -p ${RPM_BUILD_ROOT}%{_localstatedir}/%{name}
chmod 775 ${RPM_BUILD_ROOT}%{_datadir}/%{name}
chmod 754 ${RPM_BUILD_ROOT}%{_datadir}/%{name}/%{name}
mv ${RPM_BUILD_ROOT}%{_datadir}/%{name}/scripts ${RPM_BUILD_ROOT}%{_localstatedir}/%{name}/
mv ${RPM_BUILD_ROOT}%{_datadir}/%{name}/www ${RPM_BUILD_ROOT}%{_localstatedir}/%{name}/
mv ${RPM_BUILD_ROOT}%{_datadir}/%{name}/*.pem ${RPM_BUILD_ROOT}%{_localstatedir}/%{name}/
rm -rf ${RPM_BUILD_ROOT}%{_localstatedir}/%{name}/scripts/logrotate*
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{name}/Config

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || useradd -r -g %{name} -d %{_datadir}/%{name} -s /sbin/nologin -c "Domoticz Daemon" %{name}
if [[ ! -L "/usr/share/domoticz/Config" ]]; then
rm -rf /usr/share/domoticz/Config $> /dev/null || :
fi
mkdir -p /var/domoticz/backup_of_old_domoticz_db &> /dev/null || :
find /var/domoticz/ -maxdepth 1 -type f \
-exec tar cvjf /var/domoticz/backup_of_old_domoticz_db/domoticz_db_before_%{version}-%{release}.tar.bz2 {} + &> /dev/null || :


%post
chown %{name}.webconfig /var/domoticz &> /dev/null || :
chmod 775 /var/domoticz &> /dev/null || :
unlink /usr/share/domoticz/Config &> /dev/null || :
ln -sf /usr/share/openzwave/config /usr/share/domoticz/Config &> /dev/null || :
chmod 775 /usr/share/openzwave/config &> /dev/null || :
chown -R root.%{name} /usr/share/openzwave/config* &> /dev/null || :
if [ $1 -gt 1 ]; then
systemctl try-restart domoticz &> /dev/null || :
fi

%preun

%postun
if [ $1 -eq 0 ] ; then
rm -rf /usr/share/domoticz &> /dev/null || :
fi


%files
%doc History.txt
%license License.txt
%attr(-,%{name},%{name}) %{_localstatedir}/%{name}
%attr(-,%{name},%{name}) %{_datadir}/%{name}

%changelog
* Fri Mar 25 2022 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2022.1-2
- Added sqlite-devel as build req to enable mock builds

* Fri Feb 4 2022 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2022.1
- New upstream release

* Sat Apr 17 2021 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2021.1-1
- New upstream release

* Wed Apr 14 2021 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2020.2.13165-1
- New upstream beta release
- Added new submodule fmtlib

* Fri Apr 9 2021 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2020.2.13150-1
- New upstream beta release, updated submodules
- Enabled SCL and gcc-9 in the build section

* Sun Jun 7 2020 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2020.2-2
- Backported upstream patches for additional display of rssi and battery level

* Thu Apr 30 2020 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2020.2-1
- New upstream release
- Made adjustments for change to submodules in upstream

* Sun Apr 12 2020 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2020.1-2
- Added Buildrequres python3-devel in an attempt to fix a build problem in Koji

* Sun Apr 12 2020 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 2020.1-1
- New upstream release
- Updated Boost library to 1.72.0
- Various fixes to make it possible to build in ClearOS

* Mon May 27 2019 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.10717-4
- Removed a duplicate build requirement

* Mon May 27 2019 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.10717-3
- Changed build requirements to hopefully allow successful build on arm too

* Mon May 27 2019 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.10717-2
- Corrected source checksum since upstream re-packaged its release

* Sun May 26 2019 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.10717-1
- New upstream release

* Sat Jun 30 2018 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.9700-3
- New build with updated libopenzwave

* Sun Jun 24 2018 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.9700-2
- Patched html files to adopt to ClearOS environment

* Sat Jun 23 2018 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 4.9700-1
- New upstream release

* Sat Aug 12 2017 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.8153-2
- Corrected link to open-zwave
- Added python34-devel requirement to avoid dynamic library load error on domoticz startup

* Mon Aug 7 2017 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.8153-1
- New upstream release
- Remove one time fix for transition to softlinked config files

* Mon Feb 20 2017 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.5877-6
- Corrected argument in run-domoticz script

* Sun Jan 15 2017 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.5877-5
- Excluded the bundled Z-wave config directory and added a soft link to libopenzwave config directory instead
- Remove /usr/share/domoticz at uninstall

* Thu Jan 12 2017 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.5877-4
- Changed installation directories after feedback from ClearOS QA Audit
- Added readme.txt to assist end users
- Added script to run domoticz manually
- Made localstatedir writable for webconfig
- Added patch to hide Check for Update
- Added patch to correct domoticz native restart script

* Sun Dec 18 2016 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.5877-3
- Added patch for python RPATH (bugzilla 1318383)
- Added patch for Boost.Asio to fix allocator usage (bugzilla 1403165)
- Prepared for Python 3 support

* Thu Dec 15 2016 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.5877-2
- Added a try-restart in case of upgrade and system has daemon script installed

* Sat Nov 19 2016 Fredrik Fornstad <fredrik.fornstad@gmail.com> - 3.5877-1
- First build for ClearOS
