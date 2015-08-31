import sys,os
f=open(sys.argv[1],'r')
line=f.readline()
words=str.split(line)
num_vars=int(words[2])
f.readline()
#margs=[]
os.system("rm results_ordered.txt")
#os.system("rm temp.txt")
#os.system("echo \"correctMargs := [\" >>  marginalstemp.g");
for i in range(0,num_vars):
	line=f.readline()
	words=str.split(line)
	
	#os.system("java -jar ./wfomc-3.0.jar -q \""+words[2]+"\" "+sys.argv[2]+" >> temp.txt")
	os.system("grep words[2] results.out | cut -d ' '-f2 >> results_ordered.txt") 
	
