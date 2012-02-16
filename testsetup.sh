#!/bin/bash
## begin license ##
# 
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats. 
# 
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "CQLParser"
# 
# "CQLParser" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "CQLParser" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "CQLParser"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

set -o errexit

rm -rf tmp build

python2.6 setup.py install --root tmp

VERSION="x.y.z"

find tmp -name '*.py' -exec sed -r -e \
    "/DO_NOT_DISTRIBUTE/ d;
    s/\\\$Version:[^\\\$]*\\\$/\\\$Version: ${VERSION}\\\$/" -i '{}' \;

if [ -f /etc/debian_version ]; then
    SITE_PACKAGE_DIR=`pwd`/tmp/usr/local/lib/${fullPythonVersion}/dist-packages
else
    SITE_PACKAGE_DIR=`pwd`/tmp/usr/lib/${fullPythonVersion}/site-packages
fi

export PYTHONPATH=${SITE_PACKAGE_DIR}:${PYTHONPATH}
cp -r test tmp/test

set +o errexit
(
    cd tmp/test
    ./alltests.py
)
set -o errexit

rm -rf tmp build

