# GCC
source /cvmfs/sft.cern.ch/lcg/external/gcc/4.7.2/x86_64-slc6-gcc47-opt/setup.sh ''  # empty arg needed!

# Python 2.7
export PythonPrefix=/cvmfs/sft.cern.ch/lcg/external/Python/2.7.3/x86_64-slc6-gcc47-opt
export PATH="$PythonPrefix/bin:$PATH"
export LD_LIBRARY_PATH="$PythonPrefix/lib:$LD_LIBRARY_PATH"

exec bash
