Source code for the simulation software is in directory


Simulations of different solutions are in Nxcy, where x is the number of particle species, and y is the number of colors. 
Each case has multiple temperatures simulated; for each simulation input file has to specify plugin_search_path directory to point to 
the compiled oxdna code directory where contrib/romano subdirectory is located (with compiled interaction file PatchyShapeInteraction). 
The simulations are launched using 

oxDNA inputfile

Each simulation specifies interactions between patches by specifying interaction file (option patchy_file),
which lists position of each patch, and assigned colors. Colors with value > -10  and  < 10 are self-complementary; 
colors with other values are complementary with colors such that they sum to 0. The list of which patches are assigned to
what particle type is specified in a file given by option particle_file



