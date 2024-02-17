##SAT solver script generators:

Requires python and minisat to be installed

#Usage:

In the file sat.py, on line 34 and 35 specify the number of species that will be used; 
For example, 2 species and 12 colors specify:

```python
Na = 2     
Nc = 12     
```

Or for 4 species and 24 colors:

```python
Na = 4     
Nc = 24
```

Then, run the script as:

```bash
python sat.py > problem.cnf
```

which formulates the design task in terms of SAT clauses and variables (CNF file format), and you can solve it using e.g. minisat solver:

```bash
minisat problem.cnf problem.sol
```

To convert into human-readable form, run:

```bash
python sat.py problem.sol > problem.sol.converted
```

In the resulting file, you will have the following information:

B(X,Y): this means color X and Y interact
C(A,B,X): this means patchy particle of type A, patch number B, has color X

The above solution is listed for all colors and all patches (0 to 5) in all particle types (0..Na-1), and for all colors (X goes from 0 to Nc-1)
There are also auxiliary variables P and F printed out. 


