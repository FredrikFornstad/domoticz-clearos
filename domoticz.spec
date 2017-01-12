%global boostver 1_60_0

Name:		domoticz
Version:	3.5877
Release:	4%{?dist}
Summary:	Domoticz Home Automation System

License:	GNU GPL 3
URL:		http://www.domoticz.com
Source0:	https://github.com/%{name}/%{name}/archive/%{version}.tar.gz
Source1:	http://downloads.sourceforge.net/boost/boost_%{boostver}.tar.bz2
Source2: 	ver.py
Source3:        libboost_thread.so
Source4:	readme.txt
Source5:	run-domoticz

Patch1:		CMakeLists.txt.patch
Patch2:		download_update.sh.patch
Patch3:		update_domoticz.patch
Patch4:		updatedomo.patch
Patch5:		appversion.default.patch
Patch6:		setup.html.patch
Patch7:		index.html.patch
Patch8:		restart_domoticz.patch

# https://svn.boost.org/trac/boost/ticket/6150
Patch10: boost-1.50.0-fix-non-utf8-files.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=828856
# https://bugzilla.redhat.com/show_bug.cgi?id=828857
# https://svn.boost.org/trac/boost/ticket/6701
Patch11: boost-1.58.0-pool.patch

# https://svn.boost.org/trac/boost/ticket/5637
Patch12: boost-1.57.0-mpl-print.patch

# https://svn.boost.org/trac/boost/ticket/8870
Patch13: boost-1.57.0-spirit-unused_typedef.patch

# https://svn.boost.org/trac/boost/ticket/9038
Patch14: boost-1.58.0-pool-test_linking.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1102667
Patch15: boost-1.57.0-python-libpython_dep.patch
Patch16: boost-1.57.0-python-abi_letters.patch
Patch17: boost-1.55.0-python-test-PyImport_AppendInittab.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1190039
Patch18: boost-1.57.0-build-optflags.patch

# Prevent gcc.jam from setting -m32 or -m64.
Patch19: boost-1.58.0-address-model.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1262444
Patch20: boost-1.59-test-fenv.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1349638
Patch21: boost-1.60-multiprecision.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1358725
# https://github.com/boostorg/python/pull/59/files
Patch22: boost-1.60-python-regptr.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1318383
Patch23: boost-1.60.0-no-rpath.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1403165
Patch24: boost-1.60-asio-use-future.patch

BuildRequires:	make cmake gcc gcc-c++
BuildRequires:	openssl-devel git
BuildRequires:	curl-devel libquadmath-devel
BuildRequires:	libstdc++-static
BuildRequires:  libusb-devel systemd-devel

BuildRequires: m4 libquadmath-devel
BuildRequires: libstdc++-devel
BuildRequires: bzip2-devel
BuildRequires: zlib-devel
BuildRequires: python-devel python34-devel
BuildRequires: libicu-devel
BuildRequires: libopenzwave-devel telldus-core-devel

Requires: python python34

%description
Domoticz is a Home Automation System that lets you monitor and configure various devices like:
Lights, Switches, various sensors/meters like Temperature, Rain, Wind, UV, Electricity, Gas, Water and much more.
Notifications/Alerts can be sent to any mobile device.

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

tar -vxjf %{SOURCE1}
cd boost_%{boostver}
%patch10 -p1
%patch11 -p0
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p2
%patch21 -p2
%patch22 -p2
%patch23 -p0
%patch24 -p2

cd ..

%build

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
export RPM_OPT_FLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-local-typedefs"

cat > ./tools/build/src/user-config.jam << "EOF"
import os ;
local RPM_OPT_FLAGS = [ os.environ RPM_OPT_FLAGS ] ;

using gcc : : : <compileflags>$(RPM_OPT_FLAGS) ;

using python : %{python2_version} : /usr/bin/python2 : /usr/include/python%{python2_version} : : : : ;
using python : %{python3_version} : /usr/bin/python3 : /usr/include/python%{python3_version}%{python3_abiflags} : : : : %{python3_abiflags} ;

EOF

./bootstrap.sh --with-toolset=gcc --with-icu

# N.B. When we build the following with PCH, parts of boost (math
# library in particular) end up being built second time during
# installation.  Unsure why that is, but all sub-builds need to be
# built with pch=off to avoid this.
#
# The "python=2.*" bit tells jam that we want to _also_ build 2.*, not
# just 3.*.  When omitted, it just builds for python 3 twice, once
# calling the library libboost_python and once libboost_python3.  I
# assume this is for backward compatibility for apps that are used to
# linking against -lboost_python, for when 2->3 transition is
# eventually done.

echo ============================= build serial ==================
./b2 -d+2 -q %{?_smp_mflags} \
        --without-mpi --without-graph_parallel --build-dir=serial \
        variant=release threading=multi debug-symbols=on pch=off \
        python=%{python2_version} stage

# See libs/thread/build/Jamfile.v2 for where this file comes from.
if [ $(find serial -type f -name has_atomic_flag_lockfree \
                -print -quit | wc -l) -ne 0 ]; then
        DEF=D
else
        DEF=U
fi

m4 -${DEF}HAS_ATOMIC_FLAG_LOCKFREE -DVERSION=%{boost_ver} \
        %{SOURCE3} > $(basename %{SOURCE3})

echo ============================= build Boost.Build ==================
(cd tools/build
 ./bootstrap.sh --with-toolset=gcc)

#
# Boost is prepared, move on to build domoticz
#

cd ..

cmake . -DCMAKE_BUILD_TYPE=Release -DBOOST_ROOT:PATH=%{_builddir}/%{name}-%{version}/boost_%{boostver} -DBOOST_LIBRARYDIR=%{_builddir}/%{name}-%{version}/boost_%{boostver}/stage/lib
make

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

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || useradd -r -g %{name} -d %{_datadir}/%{name} -s /sbin/nologin -c "Domoticz Daemon" %{name}

%post
if [ $1 -gt 1 ]; then
systemctl try-restart domoticz &> /dev/null || :
fi
chown %{name}.webconfig /var/domoticz
chmod 775 /var/domoticz

%preun

%postun

%files
%doc History.txt
%license License.txt
%attr(-,%{name},%{name}) %{_localstatedir}/%{name}
%attr(-,%{name},%{name}) %{_datadir}/%{name}

%changelog
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
