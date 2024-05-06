import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import numpy as np

from Argumentation_Builder import ArgumentationFramework
import Argumentation_logic as arglog
from Initial_Trust_Values import initial_trust_values
from natlang_to_logic import to_logical_form


# build arguments from persons statements
arguments_Norby_yaml = arglog.load_yaml("statement_Norby.yml")
arguments_mre_yaml = arglog.load_yaml("statement_mrE.yml")

arguments_Norby_log, statement_map, negations = to_logical_form(arguments_Norby_yaml)
arguments_mre_log, statement_map, negations = to_logical_form(arguments_mre_yaml, statement_map, negations)
print(arguments_Norby_log, arguments_mre_log)

arguments_Norby = arglog.create_arguments(arguments_Norby_log)
arguments_mre = arglog.create_arguments(arguments_mre_log)
print(arguments_Norby, arguments_mre)

#define as many colors as persons
color = ['green', 'lightblue']

#build initial trust values
trust_values = initial_trust_values("history_persons.yml")
#print("trust-values:")
#print(trust_values)

#creating argument_dicts and a big argument for overall arguments
argument_dict_p1 = arglog.creating_argument_dict(arguments_Norby, "p1")
argument_dict_p2 = arglog.creating_argument_dict(arguments_mre, "p2")
overall_arguments = {**argument_dict_p1, **argument_dict_p2}

# add Arguments to Argumentation framework
af = ArgumentationFramework()
for argument in overall_arguments.keys():
    af.add_argument(argument)
# print(af.arguments)

# add initial Trust Values to arguments
for (argument, content) in overall_arguments.items():
     for i, (p, trust) in enumerate(trust_values.items()):
         c = color[i]
         if argument[:2] == p:
             af.add_trust(argument, trust, str(content[0]), content[1], c)

# print("trust arguments:")
# print(af.trust)

# create attacks and add them to argumentation framework
arglog.create_attacks(list(overall_arguments.items()), af)
#print("direct defeater attacks:")
#print(af.attacks)

# idea: put all data in pandas dataframe (nodes,attacks,color,trust/weight) and visualize with pyviz
# update trust of arguments by adding attack level based on number of attacks and weights of attacking nodes
arguments_df = pd.DataFrame(af.trust,columns=['argument', 'trust', 'support', 'conclusion', 'color'])
print(arguments_df)

attacks_df =pd.DataFrame(af.attacks,columns=['attacker', 'target'])
print(attacks_df)

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

edge_data = zip(sources, targets)#, weights)
print(edge_data)

got_net.add_nodes(arguments_df["argument"],title=arguments_df["argument"],color=arguments_df["color"],value=arguments_df["trust"])
for e in edge_data:
    src = e[0]
    dst = e[1]
    #w = e[2]

    got_net.add_edge(src, dst)#, value=w)

# add trust data to node hover data
for node in got_net.nodes:
                node["title"] += ", Trust:" + str(node["value"])
                
got_net.show("network.html")
argument_nodes = got_net.get_nodes()



# Evaluate Belief of Arguments in Argumentation Framework based on evidence theory or Dempster–Shafer theory (DST)

eminus_H = {}
eplus_H = {}
for argument in arguments_df["argument"]:
    # Find for every argument: attackers
    arg_attack = attacks_df.loc[attacks_df['target'] == argument]
    if not arg_attack.empty:
        # get all trust values of attackers
        evidence_minus = []
        for attacker in arg_attack["attacker"]:
            trust = arguments_df[(arguments_df == attacker).any(axis=1)]["trust"]
            trust = trust.item()
            evidence_minus.append(1-trust)
    #compute evidence against argument by dempster shafer
        bel_H_minus = 1 - np.prod(evidence_minus)
    else:
        bel_H_minus = 0 # zero if no attacks = no evidence against hypothesis
    eminus_H[argument] = bel_H_minus

    # Find supporters for every argument: Same argument from different person
    supp_arg = arguments_df[(arguments_df == argument).any(axis=1)]["support"].item()
    conc_arg = arguments_df[(arguments_df == argument).any(axis=1)]["conclusion"].item()
    # check if conclusion and support is same for other arguments
    supporters_candidates = arguments_df.loc[arguments_df['support'] == supp_arg]
    supporters = supporters_candidates.loc[supporters_candidates['conclusion'] == conc_arg]

    evidence_plus = []
    # find truth values of supporters, argument/hypothesis always supports its own 
    for index, row in supporters.iterrows():
        trust = row["trust"]
        evidence_plus.append(1-trust)
        #compute evidence for argument by dempster shafer
    bel_H_plus = 1 - np.prod(evidence_plus)
    eplus_H[argument] = bel_H_plus
    # Calculating belief intervall for argument based on Dempster and Shafer
    if bel_H_minus == 1 and bel_H_plus == 1: # no evidence for or against a hypothesis
         pro_H = 0
         con_H = 0

    else:
        pro_H = (bel_H_plus*(1-bel_H_minus)) / (1-bel_H_plus*bel_H_minus)
        con_H = (bel_H_minus*(1-bel_H_plus)) / (1-bel_H_plus*bel_H_minus)

        # only one hypothesis in focus
        bel_H = pro_H   # degree of belief (lower boundary)
        pl = 1 - con_H  # plausibility (upper boundary)
    print(argument, bel_H, pl)


# Todo: Take belief or plausibility or mean (try different parameters) and iterate over the whole algorithm until convergence

                
                   
