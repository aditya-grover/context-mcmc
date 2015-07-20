"""
Converts a BIF (Bayesian Interchange Format) File to an MLN (Markov Logic Network) File

Last updated: July 3, 2015

arg1: path of bif file to be converted
arg2: path of mln file where the output is to be dumped
"""

import sys, re, math

def parseBIF():

    # portions of parseBIF inspired from https://github.com/eBay/bayesian-belief-networks/blob/master/bayesian/examples/bif/bif_parser.py

    # Regex patterns for parsing
    infile = open(sys.argv[1], 'r')
    variable_pattern = re.compile(r'  type discrete \[ \d+ \] \{ (.+) \};\s*')
    prior_pattern_1 = re.compile(r'probability \( ([^|]+) \) \{\s*')
    prior_pattern_2 = re.compile(r'  table (.+);\s*')
    cpt_pattern_1 = re.compile(r'probability \( (.+) \| (.+) \) \{\s*')
    cpt_pattern_2 = re.compile(r'  \((.+)\) (.+);\s*')

    # storage data structures
    variables = {}   # key: r.v. nodes, value: values taken by the r.v. eg: 'A': ['TRUE', 'FALSE']
    cpt = {}         # Key: r.v. nodes, value: list of tuples. tuple format: ([(parent1_name, parent1_value), ...], [r.v_value1_prob, r.v_value2_prob ...]) 

    while True:
        line = infile.readline()

        # End of BIF file
        if not line:
            break

        # Variable declarations
        if line.startswith('variable'):
            match = variable_pattern.match(infile.readline())
            if match:
                variables[line[9:-3]] = match.group(1).split(', ')
            else:
                raise Exception('Unrecognised variable declaration:\n' + line)
            infile.readline()

        # Probability entries
        elif line.startswith('probability'):

            match = prior_pattern_1.match(line)
            if match:
                variable = match.group(1)
                line = infile.readline()
                match = prior_pattern_2.match(line)
                if match:
                    parent_assignments = []
                    prob_values = match.group(1).split(', ')
                    cpt[variable] = (parent_assignments, prob_values)
                else:
                    raise Exception('Unrecognised prior probability table entry:\n' + line)
            else:
                match = cpt_pattern_1.match(line)

                if match:
                    variable = match.group(1)
                    parents = match.group(2).split(', ')
                    cpt_table = []
                    line = infile.readline()
                    while line[0] != '}':                        
                        match = cpt_pattern_2.match(line)
                        if match:
                            parent_values = match.group(1).split(', ')
                            parent_assignments = zip(parents, parent_values)
                            prob_values = match.group(2).split(', ')
                            cpt_table.append((parent_assignments, prob_values))
                        else:
                            print line
                            raise Exception('Unrecognised cpt table entry:\n' + line)
                        line = infile.readline()
                    cpt[variable] = cpt_table;
                else:
                    raise Exception('Unrecognised probability declaration:\n' + line)

    infile.close()
    return (variables, cpt)

def addDomain(variables, MLNobject):
    for var in variables.keys():
        MLNline = var.lower() + 'Value = {'
        for domain_val in variables[var]:
             MLNline = MLNline + var.upper() + domain_val.upper() + ', '
        MLNline = MLNline[:-2] + '}'
        MLNobject.append(MLNline)
    MLNobject.append('')

def addUnaryPred(variables, MLNobject):
    for var in variables:
        MLNline = var.upper() + '(' + var.lower() + 'Value)'
        MLNobject.append(MLNline)
    MLNobject.append('')
    return

def addVarConstraints(variables, MLNobject):
    for var in variables:
        if len(variables[var]) == 2:
            domain_values = variables[var]
            MLNline = var.upper() + '(' + var.upper() + domain_values[0].upper() + ') v ' + var.upper() + '(' + var.upper() + domain_values[1].upper() + ').'
            MLNobject.append(MLNline)
            MLNline = '!'+var.upper() + '(' + var.upper() + domain_values[1].upper() + ') v !' + var.upper() + '(' + var.upper() + domain_values[0].upper() + ').'
            MLNobject.append(MLNline)
    MLNobject.append('')
    return

def getBaseMLNline(var, value, prob):
    if (prob == '0.0'):
        MLNline = '!' + var.upper() + '(' + var.upper() + value.upper() + ')'
    elif (prob == '1.0'):
        MLNline = '0 !' + var.upper() + '(' + var.upper() + value.upper() + ')'
    else:
        MLNline = str(-1*math.log(float(prob))) + ' !' + var.upper() + '(' + var.upper() + value.upper() + ')'
    return MLNline

def addCPTConstraints(parsedBIF, MLNobject):
    variables = parsedBIF[0]
    cpt = parsedBIF[1]

    for var, cpt_entry in cpt.iteritems():
        if not cpt_entry[0]:  # no parents
            parent_assignments = cpt_entry[0]
            prob_values = cpt_entry[1]
            for (value, prob) in zip(variables[var], prob_values):
                MLNline = getBaseMLNline(var, value, prob)
                if (prob == '0.0'):
                    MLNline = MLNline + '.'
                MLNobject.append(MLNline)
        else:
            for entry in cpt_entry:
                parent_assignment = entry[0]
                prob_values = entry[1]
                for (value, prob) in zip(variables[var], prob_values):
                    MLNline = getBaseMLNline(var, value, prob)
                    for (parent, parent_val) in parent_assignment:
                        MLNline = MLNline + ' v !' + parent.upper() + '(' + parent.upper() + parent_val.upper() + ')'
                    if (prob == '0.0'):
                        MLNline = MLNline + '.'
                    MLNobject.append(MLNline) 
    return

def addDomainBinary(variables, MLNobject):
    for var in variables.keys():
        MLNline = var.lower() + 'Value = {' + var.upper() + '_VAL}' 
        MLNobject.append(MLNline)
    MLNobject.append('')

def getVariableState(var, value):
    if value[-4:] == 'TRUE':
        var_print = '!' + var.upper()
    elif value[-5:] == 'FALSE':
        var_print = var.upper()
    else:
        raise Exception('Binary variable value names do not have true or false')    
    return var_print

def getBaseMLNlineBinary(var, value, prob):

    var_print = getVariableState(var, value)

    if (prob == '0.0'):
        MLNline = var_print + '(' + var.upper() + '_VAL)'
    elif (prob == '1.0'):
        MLNline = '0 ' + var_print + '(' + var.upper() + '_VAL)'
    else:
        MLNline = str(-1*math.log(float(prob))) + ' ' + var_print + '(' + var.upper() + '_VAL)'

    return MLNline

def addCPTConstraintsBinary(parsedBIF, MLNobject):
    variables = parsedBIF[0]
    cpt = parsedBIF[1]

    for var, cpt_entry in cpt.iteritems():
        if len(variables[var]) != 2:
            raise Exception('Non-binary variables\n')
            
        if not cpt_entry[0]:  # no parents
            parent_assignments = cpt_entry[0]
            prob_values = cpt_entry[1]
            for (value, prob) in zip(variables[var], prob_values):
                MLNline = getBaseMLNlineBinary(var, value, prob)
                if (prob == '0.0'):
                    MLNline = MLNline + '.'
                MLNobject.append(MLNline)
        else:
            for entry in cpt_entry:
                parent_assignment = entry[0]
                prob_values = entry[1]
                for (value, prob) in zip(variables[var], prob_values):
                    MLNline = getBaseMLNlineBinary(var, value, prob)
                    for (parent, parent_val) in parent_assignment:
                        parent_var_print = getVariableState(parent, parent_val)
                        MLNline = MLNline + ' v ' + parent_var_print + '(' + parent.upper() + '_VAL)'
                    if (prob == '0.0'):
                        MLNline = MLNline + '.'
                    MLNobject.append(MLNline) 

    return

def writeMLN(MLNobject):
    with open(sys.argv[2], 'wb') as outfile:
        for line in MLNobject:
            outfile.write(line + '\n')
    return

# helper print functions
def printParsedBIF(parsedBIF):
    variables = parsedBIF[0]
    cpt = parsedBIF[1]

    print variables
    print "\n\n"
    print cpt
    return

def printMLN(MLNobject):
    for line in MLNobject:
        print line

def main():

    # read BIF file
    parsedBIF = parseBIF()

    MLNobject = []

    # add domains of variables
    addDomainBinary(parsedBIF[0], MLNobject)

    # add unary predicates for each variable
    addUnaryPred(parsedBIF[0], MLNobject)

    # add disjunction clauses for CPT entries
    addCPTConstraintsBinary(parsedBIF, MLNobject)


    """
    # add domains of variables
    addDomain(parsedBIF[0], MLNobject)

    # add unary predicates for each variable
    addUnaryPred(parsedBIF[0], MLNobject)

    # Values assumed by variables are mutually exclusive and exhaustive
    addVarConstraints(parsedBIF[0], MLNobject)

    # add disjunction clauses for CPT entries
    addCPTConstraints(parsedBIF, MLNobject)

    """

    # write MLN file
    writeMLN(MLNobject)
    return

if __name__ == '__main__':
    main()
#EOF
