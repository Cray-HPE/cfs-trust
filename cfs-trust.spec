# Copyright 2020-2021, 2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# (MIT License)
Name: cfs-trust
License: MIT
Summary: A CFS library that can be used to bootstrap an environment into the CFS trust relationship
Group: System/Management
Version: %(cat .version)
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
BuildArch: noarch
Vendor: Cray Inc.
BuildRequires: python3 >= 3.6.8
Requires: python3 >= 3.6.5
Requires: python3-base
Requires: python3-requests

%description
Provides a library that contains bootstrapping of an environment into
a trusted relationship with the configuration framework service (CFS).

%prep
%setup -q
# List any Python packages directories that are already here
find %{buildroot}/usr/lib/python3*/site-packages \
     %{buildroot}/usr/local/lib/python3*/site-packages \
     -type d -print 2>/dev/null > DIR_BEFORE || true
cat DIR_BEFORE

%build
python3 setup.py build

%install
python3 setup.py install --root %{buildroot} --record=PY3_INSTALLED_FILES
# Find all Python package directories that now exist on the system
cat PY3_INSTALLED_FILES | xargs dirname | sort -u > DIR_AFTER
cat PY3_INSTALLED_FILES
cat DIR_AFTER

%clean
# Remove any new directories that were added during this install
sed 's#^#%{buildroot}#' DIR_AFTER | while read X ; do
    [ -d "$X" ] || continue
    grep -q "^$X$" DIR_BEFORE && continue
    rm -rf "$X"
done
# Remove any files that were missed in the above process
sed 's#^#%{buildroot}#' PY3_INSTALLED_FILES | while read X ; do
    [ -f "$X" ] || continue
    rm -f "$X"
done

%files -f PY3_INSTALLED_FILES
%defattr(-,root,root)
