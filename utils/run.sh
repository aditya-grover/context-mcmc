#!/bin/sh


python bif_generator.py $1 $2.bif
python bif_to_mln.py $2.bif $2.mln
java -jar wfomc-3.0.jar --ground --dimacs-out dimacs.cnf $2.mln
python computing_marginals.py dimacs.cnf $2.mln 
