# DSDrender
Graphical user interface for [DSDPy](https://github.com/ashleylst/DSDPy) package.
### Dependencies
1. To create the Anaconda environment:
```
conda env create -f environment.yml
conda activate DSDrender
dot -c
````

2. To install OGDF library follow the [OGDF installation guide](https://github.com/ogdf/ogdf/blob/master/doc/build.md) or instructions below:

#### Requirements
- CMake 3.1+
- C++11 compliant compiler
  - gcc 4.9.2+
  - clang 3.5+
  - Microsoft Visual C++ 2015+
- GNU Make (in most cases)

#### Build
Download the latest release of [OGDF library](https://github.com/ogdf/ogdf/), change the name of the folder to `ogdf` and put the folder in `src`.

For Unix systems follow the commands below. 
```
./build.sh
```

or

```
cd ogdf
mkdir ./cmake-build-release && cd ./cmake-build-release
cmake -DCMAKE_CXX_FLAGS="-fPIC" ..
make -j 8
mkdir ./lib && cd ./lib && echo "Created new lib directory"
ar -x ../libOGDF.a
ar -x ../libCOIN.a && echo "Unpacked the static libraries libCOIN.a and libOGDF.a"
g++ -shared *.o -o libOGDF.so && echo "Created a shared library libOGDF.so"
cd ..
rsync -a ../include . && echo "Synched the header files"
```

Alternatively, you can use an IDE of your choice for building the project in 
the Release mode. Then follow the commands above from `mkdir ./lib && cd ./lib && echo "Created new lib directory"` line or copy your compiled library files (.so in the case of Unix systems, .dll and .lib in Windows) to the folder `./ogdf/cmake-build-release/lib` and synch the `include` directories in the `./ogdf/cmake-build-release` folder and `./ogdf` folder.


### Run
If you followed the build guide for OGDF, run the program without arguments.
```
python main.py
```
In the case your compiled library files are stored elsewhere, run the program with the path that points to your compiled
library files.
```
python main.py PATH_TO_COMPILED_LIBRARY_FILES
```
### Usage

#### Input
1. **DSD model** tab accepts the text input in the form described in [DSDPy manual](https://dsdpy.readthedocs.io/en/latest/tutorial.html#creating-your-own-input).
2. **Options** tab provides settings for threshold of iterations in reaction network generation

#### Simulation
1. **Generate** button starts the reaction network generation
2. **Simulate** button starts the simulation - choose the mode from the combo box (stochastic / deterministic)

#### Output
1. **Input view** tab displays the parsed input species to the DSDPy
- save the views as a SVG with save button

2. **Output view** tab displays the parsed output species from the DSDPy
- save the views as a SVG with save button

3. **Network** tab displays the chemical reaction network
- click on the species' name to view the species
- click on the reaction name to view the reactants, products and reaction rate of the reaction
- choose the network layout from the options in the combo box
- zoom and pan to navigate through the network

4. **Simulation plot** tab displays BNG simulation plot

5. **Text output** tab displays the text output from the DSDPy


