python random_smokers_mln.py $1 $2
python dimacs_gen.py $1
 ../alchemy-2/bin/infer -bp -i $1 -e evidence.txt -r results.out -q "smokes(P1)"
python new_marginals.py dimacs.cnf
rm marginals.g
echo "correctMargs := [" > marginals.g  
cat results_ordered.txt | cut -d' ' -f2  > temp.txt
awk '{print $0","}' temp.txt > temp1.txt
sed -i '$ s/.$//' temp1.txt
cat temp1.txt >> marginals.g
echo "];;" >> marginals.g
