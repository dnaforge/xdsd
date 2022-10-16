# XDSD
XDSD consists of two packages: DSDPy and DSDVis
# DSDPy 
The [DSDPy](https://github.com/ashleylst/DSDPy) implements a graph processing pipeline that takes a DSD model as input and generates DSD reaction network.
The DSDPy uses [PySB](https://github.com/pysb/pysb) framework and BioNetGen format for deterministic/stochastic simulation.

# DSDVis
 The DSDVis package consists of:
    1. a graphical user interface for DSDPy package
    2. a rendering engine to generate and display 2D graphical views of DNA species and DSD reaction network.

### Dependencies
1. To create the Anaconda environment:
```
conda env create -f environment.yml
```
In environment terminal window:
````
(xdsd) > dot -c
````

2. Manual installation:
```
conda install -c alubbock pysb
conda install -c conda-forge networkx
conda install -c conda-forge matplotlib
conda install -c anaconda pyqt
conda install -c conda-forge bidict
conda install -c alubbock graphviz pygraphviz
```

### Run
```
python xdsdApp.py
```
### Usage

#### Input
1. **DSD model** tab accepts the text input in the form described in [DSDPy manual](https://dsdpy.readthedocs.io/en/latest/tutorial.html#creating-your-own-input).
- choose if the parsing algorithm should be able to: permute the strands, flip the strands, flip the domains
- choose if the dots, denoting the destination of the pair, should be displayed
2. **Options** tab provides settings for:
- threshold of iterations in reaction network generation
- rendering speed - the greater the speed, the quicker and less accurate the output rendering (default settings: exponentially increasing for simple species, linearly increasing for pseudoknots)
- render button starts the rendering of the current view

#### Simulation
1. **Generate** button starts the reaction network generation
2. **Simulate** button starts the simulation - choose the mode from the combo box (stochastic / deterministic)

#### Output
1. **Input view** tab displays the parsed input species to the DSDPy
- **Render** button starts the rendering of the current view
- choose the input and output of the render from the combo box
- save the views as a PNG with save button

2. **Output view** tab displays the parsed output species from the DSDPy
- **Render** button starts the rendering of the current view
- choose the input and output of the render from the combo box
- save the views as a PNG with save button

3. **Network** tab displays the chemical reaction network
- click on the species' name to view the species
- click on the reaction name to view the reactants, products and reaction rate of the reaction
- choose the network layout from the options in the combo box
- zoom and pan to navigate through the network

4. **Simulation plot** tab displays BNG simulation plot

5. **Text output** tab displays the text output from the DSDPy
