# Copyright 2020-2021 Hewlett Packard Enterprise Development LP
Name: cfs-trust
License: MIT
Summary: A CFS library that can be used to bootstrap an environment into the CFS trust relationship
Group: System/Management
Version: %(cat .version)
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
Vendor: Cray Inc.
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}
Requires: python3-base
Requires: python3-requests

%description
Provides a library that contains bootstrapping of an environment into
a trusted relationship with the configuration framework service (CFS).

%{!?python3_sitelib: %define python3_sitelib %(/usr/bin/python3 -c
"from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%prep
%setup -q

%build
/usr/bin/python3 setup.py build

%install
rm -rf $RPM_BUILD_ROOT
/usr/bin/python3 setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{python3_sitelib}/*
