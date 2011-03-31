set -e

rm -rf tmp build
for pycmd in $(pyversions --installed); do

$pycmd setup.py install --root tmp --install-scripts=usr/bin 

export BINDIR=`pwd`/tmp/usr/bin
if [ "$pycmd" == "python2.5" ]; then
    export PYTHONPATH=`pwd`/tmp/usr/lib/python2.5/site-packages
else
    export PYTHONPATH=`pwd`/tmp/usr/local/lib/python2.6/dist-packages
fi
cp -r test tmp/test

(
cd tmp/test
$pycmd alltests.py
)

rm -rf tmp build
done
