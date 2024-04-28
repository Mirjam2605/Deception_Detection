import networkx as nx
import matplotlib.pyplot as plt

from Argumentation_Builder import ArgumentationFramework
import Argumentation_logic as arglog
from Initial_Trust_Values import initial_trust_values


# build arguments
arguments_p1 = arglog.create_arguments("statement_person1.yml")
arguments_p2 = arglog.create_arguments("statement_person2.yml")

#build initial trust values
trust_values = initial_trust_values("history_persons.yml")
print(trust_values)

#creating argument_dicts
argument_dict_p1 = arglog.creating_argument_dict(arguments_p1, "p1")
argument_dict_p2 = arglog.creating_argument_dict(arguments_p2, "p2")

overall_arguments = {**argument_dict_p1, **argument_dict_p2}

#test = list(overall_arguments.items())
# print(test)
# print(test[1])
# print(test[1][1])
# print(test[1][1][1])

# for s in test:
#     print (s[0])
# print(len(test))

#ToDO: Add Arguments with color depending on Person
# add Arguments to Argumentation framework
af = ArgumentationFramework()
for argument in overall_arguments.keys():
    af.add_argument(argument)
print(af.arguments)


# create attacks and add them to argumentation framework
arglog.create_attacks(list(overall_arguments.items()), af)
print("direct defeater attacks:")
print(af.attacks)

#create argument_graph
argumentation_graph, color_map = arglog.create_argumentation_graph(af)

"""
# Check if a set of arguments is conflict-free
set_arg = {"p1_arg1", "p1_arg2"}
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
"""

#show argumentation graph
fig = plt.figure()
pos = nx.planar_layout(argumentation_graph)#, seed=42)
nx.draw_networkx(argumentation_graph, pos, with_labels=True, node_size=1000, node_color=color_map,
                  font_size=5, arrowsize=10, label=str("\n".join([str(a) for a in overall_arguments.items()])))
plt.title("Argumentation Graph")
plt.legend(loc='best',fontsize="5", markerscale=0)
plt.savefig('Argumentation_Graph.png')
plt.show()
plt.close()   