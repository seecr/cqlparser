## begin license ##
# 
# "CQLParser" is a parser that builds a parsetree for the given CQL and can convert this into other formats. 
# 
# Copyright (C) 2005-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) https://seecr.nl
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

from distutils.core import setup

setup(
    name='cqlparser',
    packages=['cqlparser'],
    version='%VERSION%',
    url='https://seecr.nl',
    author='Seecr',
    author_email='info@seecr.nl',
    description='CQLParser is a parser that builds a parsetree for the given CQL and can convert this into other formats.',
    long_description='CQLParser is a parser that builds a parsetree for the given CQL and can convert this into other formats.',
    license='GNU Public License',
    platforms='all',
)
