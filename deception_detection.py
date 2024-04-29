import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd

from Argumentation_Builder import ArgumentationFramework
import Argumentation_logic as arglog
from Initial_Trust_Values import initial_trust_values


# build arguments from persons statements
arguments_p1 = arglog.create_arguments("statement_person1.yml")
arguments_p2 = arglog.create_arguments("statement_person2.yml")

#define as many colors as persons
color = ['green', 'lightblue']

#build initial trust values
trust_values = initial_trust_values("history_persons.yml")
#print("trust-values:")
#print(trust_values)

#creating argument_dicts and a big argument for overall arguments
argument_dict_p1 = arglog.creating_argument_dict(arguments_p1, "p1")
argument_dict_p2 = arglog.creating_argument_dict(arguments_p2, "p2")
overall_arguments = {**argument_dict_p1, **argument_dict_p2}

# add Arguments to Argumentation framework
af = ArgumentationFramework()
for argument in overall_arguments.keys():
    af.add_argument(argument)
#print(af.arguments)

# add initial Trust Values to arguments
for argument in overall_arguments.keys():
     for i, (p, trust) in enumerate(trust_values.items()):
         c = color[i]
         if argument[:2] == p:
             af.add_trust(argument, trust,c)

#print("trust arguments:")
#print(af.trust)

# create attacks and add them to argumentation framework
arglog.create_attacks(list(overall_arguments.items()), af)
#print("direct defeater attacks:")
#print(af.attacks)

# idea: put all data in pandas dataframe (nodes,attacks,color,trust/weight) and visualize with pyviz
# update trust of arguments by adding attack level based on number of attacks and weights of attacking nodes
arguments_df = pd.DataFrame(af.trust,columns=['argument', 'trust', 'color'])
print(arguments_df)

attacks_df =pd.DataFrame(af.attacks,columns=['attacker', 'target'])
print(attacks_df)

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


#show argumentation graph with networkx
#create argument_graph
argumentation_graph, color_map = arglog.create_argumentation_graph(af)

fig = plt.figure()
pos = nx.planar_layout(argumentation_graph)#, seed=42)
nx.draw_networkx(argumentation_graph, pos, with_labels=True, node_size=1000, node_color=color_map,
                  font_size=5, arrowsize=10, label=str("\n".join([str(a) for a in overall_arguments.items()])))
plt.title("Argumentation Graph")
plt.legend(loc='best',fontsize="5", markerscale=0)
plt.savefig('Argumentation_Graph.png')
plt.show()
plt.close() """

# visualization with pyvis
got_net = Network(
    notebook=True,
    cdn_resources="remote",
    bgcolor="white",
    font_color="black",
    directed =True,
)

# set the physics layout of the network
got_net.repulsion()
got_data = attacks_df

sources = got_data["attacker"]
targets = got_data["target"]
#weights = got_data["weight"]
print(sources)
edge_data = zip(sources, targets)#, weights)

got_net.add_nodes(arguments_df["argument"],title=arguments_df["argument"],color=arguments_df["color"],value=arguments_df["trust"])
for e in edge_data:
    src = e[0]
    dst = e[1]
    #w = e[2]
    #print(src)
    #got_net.add_node(src, src, title=src)
    #got_net.add_node(dst, dst, title=dst)
    got_net.add_edge(src, dst)#, value=w)

got_net.show("network.html")
print(got_net.get_nodes())