import sys, re, math, copy, operator
from copy import deepcopy
global_count=1
global_count_formulas=0
dict_domain_vars={}
predicates={}
formulas={}
var_mappings={}
det_clauses=[]
formula_vars={}
ground_formula_dict={}
var_list=[]

############################  Formula Grounding Generator ##################################################################

def generate_ground_formulas_rec(curr_formula,original_list_vars,curr_list_vars,counter):
	global global_count,var_mappings,dict_domain_vars,predicates,formulas,var_mappings,det_clauses,formula_vars,global_count_formulas
	if counter==len(curr_list_vars):
		temp_formula=curr_formula
		for i in range(len(curr_list_vars)):
			temp_formula=temp_formula.replace(original_list_vars[i],curr_list_vars[i])
		temp_formula=temp_formula.translate(None,' ')
		global_count_formulas=global_count_formulas+1
		ground_formula_dict[temp_formula]=curr_formula
		

	else:
		var_dict=formula_vars[curr_formula]
		domain_var=var_dict[original_list_vars[counter]]
		temp_list=dict_domain_vars[domain_var]
		for i in range(len(temp_list)):
			curr_list_vars[counter]=temp_list[i]
			generate_ground_formulas_rec(curr_formula,original_list_vars,curr_list_vars,counter+1)
	return		



################################      Variable Grounding Generator #########################################################

def generate_ground_vars_rec(base_var,var_types):
	global global_count,var_mappings,dict_domain_vars,predicates,formulas,var_mappings,det_clauses
	if len(var_types)==0:
		temp_var=base_var+")"
		temp_var=temp_var.translate(None,' ')
		var_mappings[temp_var]=global_count
		global_count=global_count+1
		return 
	list2=dict_domain_vars[var_types[0]]
	for i in range(len(list2)):
		
		temp_var=base_var+list2[i]
		if len(var_types)!=1:
			temp_var=temp_var+","
		generate_ground_vars_rec(temp_var,var_types[1:len(var_types)])
	return	


##################################   The core function ######################################################################

def generate_groundings():
	
	
	global global_count,var_mappings,dict_domain_vars,predicates,formulas,var_mappings,det_clauses,global_count_formulas,formula_vars
	infile = open(sys.argv[1],'r')
	lines = infile.readlines()

	if lines[0]!="// domain declarations\n":
		print "Error in format"
	else:
		i=1

############################      Parsing Input File    #######################################################################
		
		while(1):
			if lines[i]=="// predicate declarations\n":
				break
			if lines[i]=="\n":
				i=i+1
				continue
			temp_str=re.split('=',lines[i])
			#print temp_str[1]
			list1=temp_str[1].translate(None, '{}\n')
			list2= list1.split(',')
			temp_str[0]=temp_str[0].translate(None,' ')
			#print list2
			i=i+1			
			dict_domain_vars[temp_str[0]]=list2

		#print dict_domain_vars
		i=i+1
		
		while(1):
			if lines[i]=="// formulas\n":
				break
			if lines[i]=="\n":
				i=i+1
				continue
			temp_str=lines[i].split('(')
			list1=temp_str[1].translate(None,')\n ')
			list2=list1.split(',')
			list
			predicates[temp_str[0]]=list2
			i=i+1
		#print predicates
		i=i+1
		
		while(1):
			if i>=len(lines):
				break
			if lines[i]=="\n":
				i=i+1
				continue
			temp_str=lines[i]
			temp_str=temp_str.strip('\n')
			if temp_str[len(temp_str)-1]=='.':
				temp_str=temp_str.strip('.')
				temp_str=temp_str.replace(" ","")
				temp_str=temp_str.strip('\n')
				det_clauses.append(temp_str)
				print "groundings", temp_str
			else:
				weighted_clause=temp_str.split();
				weight=weighted_clause[0]
				rule=''.join(weighted_clause[1:len(weighted_clause)])
				formulas[rule]=weight
			i=i+1
		num_vars=0
		i=0

################################### Generate Variable Mappings ##########################################################################		
		var_mappings={}
		for key in predicates:
			var_types=predicates[key]
			temp_count=1
			base_var=key
			base_var=base_var+"("
			temp_var=base_var
			ground_vars=[]
			#print base_var
			for j in range(len(var_types)):
				temp_count=temp_count*len(dict_domain_vars[var_types[j]])
			num_vars=num_vars+temp_count
			generate_ground_vars_rec(base_var,var_types)
		#print num_vars


################################## Generate Ground Clauses #############################################################################
		for key in var_mappings:
			print key,'in', var_mappings[key]
		for key in formulas:
			curr_formula=key
			preds_curr_formula=re.split("\(|\)",curr_formula)
			temp_dict={}
			for j in xrange(0,len(preds_curr_formula)-1,2):
				present_clause=preds_curr_formula[j]
				if j>0:
					present_clause=present_clause[1:len(present_clause)]
				vars_current_pred=preds_curr_formula[j+1]
				vars_current_pred=vars_current_pred.split(',')
				if present_clause[0]=='!':
					present_clause=present_clause[1:len(present_clause)]
				temp_list=predicates[present_clause]
				#print temp_list
				for k in range(len(vars_current_pred)):
					temp_dict[vars_current_pred[k]]=temp_list[k]
			curr_list_vars=[None]*len(temp_dict)
			k=0
			for key in temp_dict:
				curr_list_vars[k]=key
				k=k+1
				

			formula_vars[curr_formula]=temp_dict
			original_list_vars=copy.deepcopy(curr_list_vars)
			generate_ground_formulas_rec(curr_formula,original_list_vars,curr_list_vars,0)
	
		print global_count_formulas
		######################## Dealing Deterministic Variables ####################################################################

		for j in range(len(det_clauses)):
			formulas[det_clauses[j]]=float("inf")
			if not det_clauses[j] in ground_formula_dict:
				global_count_formulas=global_count_formulas+1
			ground_formula_dict[det_clauses[j]]=det_clauses[j]
			#global_count_formulas=global_count_formulas+1

##################################################### Writing Dimacs File############################################################
		for key in ground_formula_dict:
			print "formulas",key,ground_formula_dict[key]

		out_file1=open("dimacs.cnf","w")
		out_file2=open("temp_dimacs.cnf.saucy","w")
		out_file1.write("p wcnf "+str(num_vars)+" "+str(global_count_formulas)+"\n")
		out_file2.write("p wcnf "+str(num_vars)+" "+str(global_count_formulas)+"\n")
		out_file1.write("c variable mappings:\n")
		sorted_vars = sorted(var_mappings.items(), key=operator.itemgetter(1))
		for j in range(len(sorted_vars)):
			out_file1.write("c "+str(sorted_vars[j][1])+" "+str(sorted_vars[j][0])+"\n")
		out_file1.write("c clauses:\n")
		color_dict={}
		color_formula_dict={}
		color=2		
		omitted_lines=0
		for key in ground_formula_dict:
			original_formula=ground_formula_dict[key]
			weight=formulas[original_formula]
			if weight in color_dict.keys():
				curr_color=color_dict[weight]
			else:
				color_dict[weight]=color
				curr_color=color
				color=color+1
			key_with_spaces=key.replace(")v",") v ")
			out_file1.write("c "+str(weight)+" "+key_with_spaces+"\n")
			clauses_curr_formula=key_with_spaces.split(' ')
			formula_var_number_form=str(weight)
			formula_color_form=str(curr_color)
			var_dupl={}
			omit_line=False
			print clauses_curr_formula,original_formula,key
			for j in range(0,len(clauses_curr_formula),2):
				formula_var_number_form=formula_var_number_form+" "
				formula_color_form=formula_color_form+" "
				flag_positive=True
				if clauses_curr_formula[j][0]=='!':
					flag_positive=False
					clauses_curr_formula[j]=clauses_curr_formula[j][1:len(clauses_curr_formula[j])]	
				var_number=var_mappings[clauses_curr_formula[j]]
				if flag_positive==False:
					var_number=var_number*-1
					if -1*var_number in var_dupl.keys():
						get_sign=var_dupl[-1*var_number]
						if get_sign==True:
							omit_line=True
							omitted_lines=omitted_lines+1
					else:
						var_dupl[-1*var_number]=False
				else:
					if var_number in var_dupl.keys():
						get_sign=var_dupl[var_number]
						if get_sign==False:
							omit_line=True
							omitted_lines=omitted_lines+1
					else:
						var_dupl[var_number]=True		

				formula_var_number_form=formula_var_number_form+str(var_number)
				formula_color_form=formula_color_form+str(var_number)
				
			formula_var_number_form=formula_var_number_form+" 0\n"
			formula_color_form=formula_color_form+" 0\n"
			if omit_line==False:
				color_formula_dict[formula_color_form]=curr_color
			out_file1.write(formula_var_number_form)
		sorted_color_list=sorted(color_formula_dict.items(), key=operator.itemgetter(1))
		for j in range(len(sorted_color_list)):
			out_file2.write(sorted_color_list[j][0])

					
		out_file1.close()
		out_file2.close()
		infile2=open("temp_dimacs.cnf.saucy","r")
		out_file2=open("dimacs.cnf.saucy","w")
		lines=infile2.readlines()
		out_file2.write("p wcnf "+str(num_vars)+" "+str(global_count_formulas-omitted_lines)+"\n")
		for i in range(1,len(lines)):
			out_file2.write(lines[i])
		infile2.close()
		out_file2.close()




	return



	






def main():
	generate_groundings()
	#writeGroundedDimacs()
	return

if __name__ == '__main__':
	main()
#EOF
