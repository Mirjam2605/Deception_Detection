import yaml
import ttg
from itertools import chain, combinations
import networkx as nx
import matplotlib.pyplot as plt
from Argumentation_Builder import ArgumentationFramework

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
    # Load your YAML data (replace 'your_yaml_file.yaml' with your actual file)
    yaml_data = load_yaml(file)

    statements = list(yaml_data.values())
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
    print("Truth-Table:")
    print(truth_table)
    print()

    #check truth for statement combinations
    support_candidates = []
    for statements in statement_combinations:
        boolean = truth_table[statements].all(axis=1)
        for b in boolean:
            if b:
                support_candidates.append(statements) 
                break
    print("support_candidates:")
    print(*support_candidates,sep='\n')  
    print()

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
    print("argument candidates:")   
    print(*argument_candidates,sep='\n')
    print()

    # build truth table
    truth_table_h = ttg.Truths(atoms_for_conclusions, prop_expr, ints=False).as_pandas 
    print("Truth-Table with h:")
    print(truth_table_h)
    print()

    argument_candidates_final = []
    for arguments in argument_candidates:
        boolean = truth_table_h[arguments[0]].all(axis=1)
        conclusion_truth_values = []
        for i, b in enumerate(boolean):
            if b:
                conclusion_truth_values.append(truth_table_h.iloc[i][arguments[1]])
        if all(conclusion_truth_values):
            argument_candidates_final.append(arguments)

    print("final arg candidates:")
    print(*argument_candidates_final,sep='\n')
    print()

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
            
    #arguments_final = {value[0]: key for key, value in arguments_min.items()}



    print("Final arguments:")
    print(*arguments_final,sep='\n')
    print() 
    return arguments_final

#find attacks between arguments
def create_attacks(arguments, framework):
    #determine attacks: direct defeater (DD) attack function:
    #compare every conclusion with support of other elements, check if negation is in it
    for i in range(len(arguments)):
        conclusion = arguments[i][1]
        if conclusion.startswith('not'):
            for j, support in enumerate(arguments):
                if conclusion[4:] in support[0]:
                    framework.add_attack(('arg{}'.format(i+1)), ('arg{}'.format(j+1))) 
        else:
            for j, support in enumerate(arguments):
                if ("not "+conclusion) in support[0]:
                    framework.add_attack(('arg{}'.format(i+1)), ('arg{}'.format(j+1)))
    #print("direct defeater attacks:")
    #print(framework.attacks)   

#Better with defining attack function before?
def create_argumentation_graph(af):
    G = nx.MultiDiGraph()
    for argument in af.arguments:
        G.add_node(argument)
    for attack in af.attacks:
        G.add_edge(attack[0], attack[1])
    # Erstelle ein neues Mapping, das die Knoten als "A1", "A2", "A3", ... benennt
    #new_mapping = {node: f"A{idx}" for idx, node in enumerate(G.nodes(), start=1)}
    #G = nx.relabel_nodes(G, new_mapping)
    return G
    

# build arguments
arguments = create_arguments("statement_v1.yml")


# create dictionary with numbers for argument
argument_dict = {}

for j in range(len(arguments)):
    key_j = 'arg{}'.format(j+1)  # a string depending on j
    argument_dict[key_j] = arguments[j]

print("argument names:")
print(argument_dict)
print()

# add Arguments to Argumentation framework
af = ArgumentationFramework()
for argument in argument_dict.keys():
    af.add_argument(argument)

# create attacks and add them to argumentation framework
create_attacks(arguments, af)
print("direct defeater attacks:")
print(af.attacks)

#create argument_graph
argumentation_graph = create_argumentation_graph(af)

# Check if a set of arguments is conflict-free
set_arg = {"arg1", "arg2"}
if af.is_conflict_free(set_arg):
    print()
    print(f"{set_arg} is conflict free")
else:
    print()
    print(f"{set_arg} is not conflict free")

# Check if a set of arguments is admissible
if af.is_admissible(set_arg):
    print()
    print(f"{set_arg} is admissible")
else:
    print()
    print(f"{set_arg} is not admissible")

#show argumentation graph
fig = plt.figure()
pos = nx.planar_layout(argumentation_graph)#, seed=42)
nx.draw_networkx(argumentation_graph, pos, with_labels=True, node_size=3000, node_color='skyblue',
                  font_size=20, arrowsize=30, label=str("\n".join([str(a) for a in argument_dict.items()])))
plt.title("Argumentation Graph")
plt.legend(loc='best',fontsize="10", markerscale=0)
plt.savefig('Argumentation_Graph.png')
plt.show()
plt.close() 