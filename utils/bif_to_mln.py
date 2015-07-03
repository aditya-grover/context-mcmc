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
    variables = {}
    cpt = {}

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

def addUnary(variables, MLNobject):

    for var in variables:
        MLNline = var.upper() + '(' + var.lower() + 'Value!)'
        MLNobject.append(MLNline)
    MLNobject.append('')
    return

def addCPT(parsedBIF, MLNobject):
    variables = parsedBIF[0]
    cpt = parsedBIF[1]

    for var, cpt_entry in cpt.iteritems():
        if not cpt_entry[0]:
            parent_assignments = cpt_entry[0]
            prob_values = cpt_entry[1]
            for (value, prob) in zip(variables[var], prob_values):
                if (prob != '0.0'):
                    MLNline = str(-1*math.log(float(prob))) + ' !' + var.upper() + '(' + var.upper() + value.upper() + ')'
                    MLNobject.append(MLNline)
        else:
            for entry in cpt_entry:
                parent_assignment = entry[0]
                prob_values = entry[1]
                for (value, prob) in zip(variables[var], prob_values):
                    if (prob != '0.0'):
                        MLNline = str(-1*math.log(float(prob))) + ' !' + var.upper() + '(' + var.upper() + value.upper() + ')'
                        for (parent, parent_val) in parent_assignment:
                            MLNline2 = MLNline + ' v !' + parent.upper() + '(' + parent.upper() + parent_val.upper() + ')'
                            MLNobject.append(MLNline2) 

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
    print cpt
    return

def printMLN(MLNobject):
    for line in MLNobject:
        print line

def main():

    # read BIF file
    parsedBIF = parseBIF()

    MLNobject = []

    # add unary predicates
    addUnary(parsedBIF[0], MLNobject)

    # add disjunction clauses for CPT entries
    addCPT(parsedBIF, MLNobject)

    # write MLN file
    writeMLN(MLNobject)
    return

if __name__ == '__main__':
    main()
#EOF
