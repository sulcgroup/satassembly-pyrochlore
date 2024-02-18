**Patchy simulations and source code**

The simulation code is in [sim_source_code](sim_source_code/) directory.
Simulation setups of different solutions (and simulation temperatures) are in directories called Nxcy, where x is the number of particle species, and y is the number of colors:

* [N1c1](N1c1/)
* [N1c3](N1c3/)
* [N2c12](N2c12/)
* [N4c24](N4c24/)

Each case has multiple temperatures simulated; for each simulation input file has to specify `plugin_search_path` option to point to 
the compiled oxdna code directory where contrib/romano subdirectory is located (with compiled interaction file PatchyShapeInteraction). 

The simulations are launched using 

```bash
oxDNA input_BIG
```

where `input_BIG` is the name of the file that specifies simulation parameter options.
Each simulation specifies interactions between patches by specifying interaction file (option `patchy_file`),
which lists position of each patch, and assigned colors. Colors with value > -10  and  < 10 are self-complementary; 
colors with other values are complementary with colors such that they sum to 0. The list of which patches are assigned to
what particle type is specified in a file given by option `particle_file`.



