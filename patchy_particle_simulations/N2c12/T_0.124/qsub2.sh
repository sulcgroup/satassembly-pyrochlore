#!/bin/bash

# declare a name for this job to be sample_job
#PBS -N job_bigpatch
# request the queue (enter the possible names, if omitted, serial is the default)
#PBS -q batch  
# request 1 node
#PBS -l nodes=1
# specify your email address
# By default, PBS scripts execute in your home directory, not the 

# directory from which they were submitted. The following line 
# places you in the directory from which the job was submitted.  

cd $PBS_O_WORKDIR

START_TIME=$SECONDS
# run the program
#/home/petr/projects/venice/SIMULATION/oxDNA_valence_ico/oxDNA/build/bin/oxDNA input_BIG conf_file=tmp.dat restart_step_counter=0  print_conf_interval=5e5

#/home/petr/projects/venice/SIMULATION/oxDNA_valence_ico2/oxdna-code/oxDNA/build/bin/oxDNA input_BIG
/home/petr/projects/venice/SAXS/oxDNA/build/bin/oxDNA  input_BIG 

#input_10x10x10_MD

ELAPSED_TIME=$(($SECONDS - $START_TIME))
echo "Finished in $ELAPSED_TIME s"

exit 0

