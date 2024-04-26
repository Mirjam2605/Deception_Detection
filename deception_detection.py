import networkx as nx
import matplotlib.pyplot as plt

from Argumentation_Builder import ArgumentationFramework
import Argumentation_logic as arglog
from Initial_Trust_Values import intitial_trust_values


# build arguments
arguments_p1 = arglog.create_arguments("statement_person1.yml")
arguments_p2 = arglog.create_arguments("statement_person2.yml")

#build initial trust values
trust_values = intitial_trust_values("history_persons.yml")
print(trust_values)

## ToDO: automate this for more than one person
# create dictionary with numbers for argument
argument_dict = {}

for j in range(len(arguments_p1)):
    key_j = 'arg{}'.format(j+1)  # a string depending on j
    argument_dict[key_j] = arguments_p1[j]

print("argument names:")
print(argument_dict)
print()

#ToDO: Add Arguments with color depending on Person
# add Arguments to Argumentation framework
af = ArgumentationFramework()
for argument in argument_dict.keys():
    af.add_argument(argument)

# create attacks and add them to argumentation framework
arglog.create_attacks(arguments_p1, af)
print("direct defeater attacks:")
print(af.attacks)

#create argument_graph
argumentation_graph = arglog.create_argumentation_graph(af)

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