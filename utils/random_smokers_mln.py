import sys, re, math, copy, operator,random
def generate_random_MLN():
	out_file=open(sys.argv[1],"w")
	out_file_evid=open("evidence.txt","w")
	num_persons=int(sys.argv[2])
	out_file.write("// domain declarations\n")
	temp_str="person = { P1"
	for i in range(1,num_persons):
		temp_str=temp_str+" ,P"+str(i+1)
	temp_str=temp_str+"}\n"
	out_file.write(temp_str)
	out_file.write("\n")
	out_file.write("// predicate declarations\n")
	out_file.write("friends(person, person)\n")
	out_file.write("smokes(person)\n")
	out_file.write("cancer(person)\n")
	out_file.write("\n")
	out_file.write("// formulas\n")
	out_file.write("1.4	!smokes(v1)\n")
	out_file.write("2.3	!cancer(v1)\n")
	out_file.write("4.6	!friends(v1, v2)\n")
	out_file.write("1.5	!smokes(v1) v cancer(v1)\n")
	out_file.write("1.1	!friends(v1, v2) v !smokes(v1) v smokes(v2)\n")
	random.seed()
	for i in range(num_persons):
		if random.random()<0.1:
			if random.random()<0.5:
				out_file.write("smokes(P"+str(i+1)+").\n")
				out_file_evid.write("smokes(P"+str(i+1)+").\n")
			else:
				out_file.write("!smokes(P"+str(i+1)+").\n")
                                out_file_evid.write("!smokes(P"+str(i+1)+").\n")
	for i in range(num_persons):
		if random.random()<0.1:
			if random.random()<0.5:
				out_file.write("cancer(P"+str(i+1)+").\n")
				out_file_evid.write("cancer(P"+str(i+1)+").\n")
			else:
				out_file.write("!cancer(P"+str(i+1)+").\n")
                                out_file_evid.write("!cancer(P"+str(i+1)+").\n")
	for i in range(num_persons):
		if random.random()<0.1:
			if random.random()<0.5:
				out_file.write("friends(P"+str(int(i/num_persons)+1)+",P"+str(i%num_persons+1)+").\n")
				out_file_evid.write("friends(P"+str(int(i/num_persons)+1)+",P"+str(i%num_persons+1)+").\n")
			else:
				out_file.write("!friends(P"+str(int(i/num_persons)+1)+",P"+str(i%num_persons+1)+").\n")
                                out_file_evid.write("!friends(P"+str(int(i/num_persons)+1)+",P"+str(i%num_persons+1)+").\n")
	out_file.close()
	out_file_evid.close()


def main():
	generate_random_MLN()
	return

if __name__ == '__main__':
	main()
#EOF
