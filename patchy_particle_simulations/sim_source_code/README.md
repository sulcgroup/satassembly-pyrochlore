*Compilation instructions*

Patchy particle model is included as part of oxDNA simulation pakage, the interaction class is in in directory contrib/romano

```bash
cd oxdna

mkdir build
cd build
cmake ../
make -j 4
make romano
```

the executable will then be located in oxdna/build/bin/oxDNA
