import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import pandas as pd
import numpy as np
from scipy.special import logit, expit

from Argumentation_Builder import ArgumentationFramework
import Argumentation_logic as arglog
from Initial_Trust_Values import initial_trust_values
from natlang_to_logic import to_logical_form


# build arguments from persons statements
arguments_Norby_yaml = arglog.load_yaml("statement_Norby.yml")
arguments_mre_yaml = arglog.load_yaml("statement_mrE.yml")
arguments_Yob_yaml = arglog.load_yaml("statement_Yob.yml")

arguments_Norby_log, statement_map, negations, current_label = to_logical_form(arguments_Norby_yaml)
print("mrE")
arguments_mre_log, statement_map, negations, current_label = to_logical_form(arguments_mre_yaml, statement_map, negations, current_label)
arguments_yob_log, statement_map, negations, current_label = to_logical_form(arguments_Yob_yaml, statement_map, negations, current_label)
print(arguments_Norby_log, arguments_mre_log, arguments_yob_log)

arguments_Norby = arglog.create_arguments(arguments_Norby_log)
arguments_mre = arglog.create_arguments(arguments_mre_log)
arguments_yob = arglog.create_arguments(arguments_yob_log)
print(arguments_Norby, arguments_mre, arguments_yob)

#define as many colors as persons
color = ['green', 'lightblue', 'orange']

#build initial trust values
trust_values = initial_trust_values("history_persons.yml")
#print("trust-values:")
#print(trust_values)

#creating argument_dicts and a big argument for overall arguments
argument_dict_p1 = arglog.creating_argument_dict(arguments_Norby, "p1")
argument_dict_p2 = arglog.creating_argument_dict(arguments_mre, "p2")
argument_dict_p3 = arglog.creating_argument_dict(arguments_yob, "p3")
overall_arguments = {**argument_dict_p1, **argument_dict_p2, **argument_dict_p3}

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




## Algorithm trust model
updates = {}
new_trust_list = []
# Map Probabilities into Logits
for argument in arguments_df["argument"]:
    current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
    new_trust = logit(current_trust)
    arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust
    new_trust_list.append((0, new_trust))
    # set update for all arguments to zero in a dictionary
    updates["{}".format(argument)] = 0

# set hyperparameters
lambda_att = 0.8
lambda_def = 0.2
threshold = 0.1
it = 1
iterations = 100

new_trust_list = []
while it <= iterations:
    # iterate over attacks and changing update value with logits and e function
    for i in range(len(attacks_df)):
        attacker = attacks_df.loc[i, "attacker"]
        target = attacks_df.loc[i, "target"]
        # get trust values for attacker and targets
        trust_att = arguments_df[(arguments_df == attacker).any(axis=1)]["trust"].item()
        trust_tar = arguments_df[(arguments_df == target).any(axis=1)]["trust"].item()
        # attack
        updates[target] = updates[target] + lambda_att * -np.exp(trust_att-trust_tar)
        # defense
        updates[attacker] = updates[attacker] + lambda_def * -np.exp(trust_tar-trust_att)

    # update trust value with update value
    for argument in arguments_df["argument"]:
        current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
        new_trust = current_trust + updates[argument]
        arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust   
        new_trust_list.append((it, expit(new_trust)))
    it += 1

# change logits back into probabilities
for argument in arguments_df["argument"]:
    current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
    new_trust = expit(current_trust)
    arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust

print("Number of iterations: ", it-1)
print(arguments_df)

# plot convergence of trust values
plt.scatter(*zip(*new_trust_list), marker='.', s=3)
plt.show()




# Evaluate Belief of Arguments in Argumentation Framework based on evidence theory or Dempster–Shafer theory (DST)
# set number of iterations
""" iteration = 10
while i < iteration:
    eminus_H = {}
    eplus_H = {}
    change = 0
    for argument in arguments_df["argument"]:
        # save current trust value
        current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
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
        
        # take degree of belief as new trust value
        new_trust = bel_H
        print("updated Trust:")
        print(argument, current_trust, new_trust)
        # check if convergence
        change += abs(new_trust-current_trust)
        
        # update trust value in dataframe
        arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust
    threshold = 0.1
    print("change: ", change)
    print()
    if change < threshold:
        break
    i += 1
print("iterations: ", i)
print(arguments_df) """
# Todo: Take belief or plausibility or mean (try different parameters) and iterate over the whole algorithm until convergence

                
                   
