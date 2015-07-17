import sys, os,random
f = open('sample.bif', 'w')
f.write("network sample {\n}\n")
i=0
a='A'
n=int(sys.argv[1])
for i in range(n):
	f.write("variable "+chr(ord(a)+i)+" {\n"+"  type discrete [ 2 ] { TRUE, FALSE };\n}\n")
f.write("probability ( "+a+" ) {\n")
f.write("  table 0.4, 0.6; \n}\n")
i=0
for i in range(1,n):
	r=random.random()
	#r=0.3
	f.write("probability ( "+chr(ord(a)+i)+" | "+a+" ) {\n"+"  (TRUE) 0.7, 0.3;\n"+"  (FALSE) "+str(r)+", " +str(1-r)+";\n}\n")
f.close()
