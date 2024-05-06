import yaml
import ttg
from itertools import chain, combinations
import networkx as nx



# Load your YAML data (replace 'your_yaml_file.yaml' with your actual file)
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# find all combinations 
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def create_arguments(file):
    statements = file
    prop_expr = []
    atoms = []

    # divide statements into atoms and propositional expressions
    for statement in statements:
        if len(statement) != 1 :
            prop_expr.append(statement)
        else:
            atoms.append(statement)

    # 1. Find H is consistent: All statements combinations which are true in truth table

    #find all statement combinations
    statement_combinations = list(powerset(statements))
    statement_combinations = [list(ele) for ele in statement_combinations]

    # build truth table
    truth_table = ttg.Truths(atoms, prop_expr, ints=False).as_pandas 

    #check truth for statement combinations
    support_candidates = []
    for statements in statement_combinations:
        boolean = truth_table[statements].all(axis=1)
        for b in boolean:
            if b:
                support_candidates.append(statements) 
                break

    # 2. conclusion entailment

    # find h for every H
    argument_candidates = []
    atoms_for_conclusions = atoms.copy()
    for support in support_candidates:
        for element in support:
            if ("=>" in element):  #h for implies statements
                # Split the string using the arrow symbol
                supp, h = element.split("=>")
                # Remove leading/trailing spaces
                h = h.strip()
                argument = [support, h]
                argument_candidates.append(argument)
                atoms_for_conclusions.append(h)
    atoms_for_conclusions = list(set(atoms_for_conclusions))

    #update support candidates by removing used statements for arguments
    support_candidates_updated = [entry for entry in support_candidates if "=>" not in "".join(entry)]

    #create H,h pair for all basic support candidates without =>
    for support in support_candidates_updated:
        for element in support:          
                argument = [support, element]
                argument_candidates.append(argument)

    # build truth table
    truth_table_h = ttg.Truths(atoms_for_conclusions, prop_expr, ints=False).as_pandas 

    argument_candidates_final = []
    for arguments in argument_candidates:
        boolean = truth_table_h[arguments[0]].all(axis=1)
        conclusion_truth_values = []
        for i, b in enumerate(boolean):
            if b:
                conclusion_truth_values.append(truth_table_h.iloc[i][arguments[1]])
        if all(conclusion_truth_values):
            argument_candidates_final.append(arguments)


    # 3. Find Pairs with H minimal
    arguments_final = []

    # grouping list based on their conclusion
    combined_dict = {}
    for sublist in argument_candidates_final:
        last_arg = sublist[-1]
        other_args = sublist[:-1]

        # Add to the dictionary
        if last_arg not in combined_dict:
            combined_dict[last_arg] = []
        combined_dict[last_arg].extend(other_args)
  
    # take minimal value for conclusion
    # Create a new dictionary with the shortest sublist for each key
    #arguments_min = {key: min(sublists, key=len) for key, sublists in combined_dict.items()}
    arguments_final = []
    for conc in combined_dict.keys():
        possible_supports = combined_dict[conc]
        for supp in possible_supports:
            powerset_supp = list(powerset(supp))
            powerset_supp.remove(tuple(supp))
            minimal = True
            for power in powerset_supp:
                if list(power) in possible_supports:
                    minimal = False
                    break
            if minimal:
                arguments_final.append([supp, conc])
            

    #print(f"Final arguments:{file[10:17]}")
    #print(*arguments_final,sep='\n')
    #print() 
    return arguments_final

# create dictionary with numbers for argument
def creating_argument_dict(arguments, person):
    argument_dict = {}

    for j in range(len(arguments)):
        key_j = person+'_arg{}'.format(j+1)  # a string depending on j
        argument_dict[key_j] = arguments[j]

    print(f"arguments {person}:")
    print(argument_dict)
    print()
    return (argument_dict)
  
#find attacks between arguments
def create_attacks(arguments, framework):
    #determine attacks: direct defeater (DD) attack function:
    #compare every conclusion with support of other elements, check if negation is in it
    for i in range(len(arguments)):
        key1 = arguments[i][0]
        conclusion = arguments[i][1][1]
        if conclusion.startswith('not'):
            for support in arguments:
                key2 = support[0]
                if conclusion[4:] in support[1][0]:
                    framework.add_attack(key1, key2) 
        else:
            for support in arguments:
                key2 = support[0]
                if ("not "+conclusion) in support[0]:
                    framework.add_attack(key1, key2)
    #print("direct defeater attacks:")
    #print(framework.attacks)   

    

