#!/bin/bash

cd ./ogdf
mkdir ./cmake-build-release && cd ./cmake-build-release
cmake ..
make -j 8
mkdir ./lib && cd ./lib && echo "Created new lib directory"
ar -x ../libOGDF.a && ar -x ../libCOIN.a && echo "Unpacked the static libraries libCOIN.a and libOGDF.a"
g++ -shared *.o -o libOGDF.so && echo "Created a shared library libOGDF.so"
cd ..
rsync -a ../include . && echo "Synched the header files"