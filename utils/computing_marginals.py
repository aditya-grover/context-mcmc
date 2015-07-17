import sys,os
f=open(sys.argv[1],'r')
line=f.readline()
words=str.split(line)
num_vars=int(words[2])
f.readline()
margs=[]
os.system("rm marginals*.g")
os.system("rm temp.txt")
os.system("echo \"correctMargs := [\" >>  marginalstemp.g");
for i in range(0,num_vars):
	line=f.readline()
	words=str.split(line)
	
	os.system("java -jar ./wfomc-3.0.jar -q \""+words[2]+"\" "+sys.argv[2]+" >> temp.txt")
	if(i==num_vars-1):
		os.system("tail -3 temp.txt | head -1 | awk '{print $5 }' >> marginalstemp.g") 
	else:	
		os.system("tail -3 temp.txt | head -1 | awk '{print $5,\",\"}' >> marginalstemp.g")
	
	print("java -jar ./wfomc-3.0.jar -q \""+words[2]+"\" "+sys.argv[2]+" >> temp.txt")
f.close()
os.system("echo \"];;\" >>  marginalstemp.g");
os.system("cat marginalstemp.g | tr -d \" \" > marginals.g"); 
