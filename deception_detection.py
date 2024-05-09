import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.special import logit, expit

from Argumentation_Builder import ArgumentationFramework
import Argumentation_logic as arglog
from Initial_Trust_Values import initial_trust_values
from natlang_to_logic import to_logical_form

import warnings
warnings.filterwarnings("ignore")

# build arguments from persons statements
arguments_Norby_yaml = arglog.load_yaml("statement_Norby.yml")
arguments_mre_yaml = arglog.load_yaml("statement_mrE.yml")
arguments_Yob_yaml = arglog.load_yaml("statement_Yob.yml")

arguments_Norby_log, statement_map, negations, current_label = to_logical_form(arguments_Norby_yaml)
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

# create attacks and add them to argumentation framework
arglog.create_attacks(list(overall_arguments.items()), af)

# create agreement and add them to argumentation framework
arglog.create_agreement(list(overall_arguments.items()), af)

# create dataframes for arguments, attacks and agreement
arguments_df = pd.DataFrame(af.trust,columns=['argument', 'trust', 'support', 'conclusion', 'color'])
print(arguments_df)

attacks_df =pd.DataFrame(af.attacks,columns=['attacker', 'target'])
print(attacks_df)

agreement_df =pd.DataFrame(af.agreement,columns=['supporter', 'supported'])
print(agreement_df)

# save initial Graph
arglog.create_network(arguments_df, attacks_df, agreement_df, "initial_trust_network")

## Algorithm trust model

updates_att = {}
updates_agree = {}
new_trust_list = []

# set hyperparameters
lambda_att = 0.008
lambda_def = 0.002
lambda_supp = 0.008
threshold = 0.1
it = 1
iterations = 1000

# Map Probabilities into Logits
for argument in arguments_df["argument"]:
    current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
    new_trust = logit(current_trust)
    arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust
    new_trust_list.append((0, new_trust))
 
history= {a: [] for a in arguments_df["argument"]}
while it <= iterations:
    # set update for all arguments to zero in a dictionary
    for argument in arguments_df["argument"]:
        updates_att["{}".format(argument)] = 0 
        updates_agree["{}".format(argument)] = 0
    # iterate over attacks and changing update value according to attacks
    for i in range(len(attacks_df)):
        attacker = attacks_df.loc[i, "attacker"]
        target = attacks_df.loc[i, "target"]
        # get trust values for attacker and targets
        trust_att = arguments_df[(arguments_df == attacker).any(axis=1)]["trust"].item()
        trust_tar = arguments_df[(arguments_df == target).any(axis=1)]["trust"].item()

        # attack
        updates_att[target] = updates_att[target] + lambda_att * (-np.exp(trust_att-trust_tar))
        # defense
        updates_att[attacker] = updates_att[attacker] + lambda_def * (-np.exp(trust_tar-trust_att))

    # iterate over agreements and changing update value according to agreement
    for i in range(len(agreement_df)):
        supporter = agreement_df.loc[i, "supporter"]
        supported = agreement_df.loc[i, "supported"]
        # get trust values for supporter and supported
        trust_supper = arguments_df[(arguments_df == supporter).any(axis=1)]["trust"].item()
        trust_supp = arguments_df[(arguments_df == supported).any(axis=1)]["trust"].item()

        # supported
        updates_agree[supported] = updates_agree[supported] + lambda_supp * (np.exp(trust_supper-trust_supp))
        # defense: not needed because relation is binary
        #updates_agree[supporter] = updates_agree[supporter] + lambda_supper * (np.exp(trust_supp-trust_supper))

    # update trust value with update values
    for argument in arguments_df["argument"]:
        current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
        new_trust = current_trust + updates_att[argument] + updates_agree[argument]
        # boundary for logit value (specific precision enough)
        if new_trust > 15:
            new_trust = 15
        if new_trust < -15:
            new_trust = -15
        
        arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust   
        new_trust_list.append((it, expit(new_trust)))
    it += 1

    for argument in arguments_df["argument"]:
        history[argument].append(expit(arguments_df.loc[arguments_df['argument'] == argument, 'trust']))

# change logits back into probabilities
for argument in arguments_df["argument"]:
    current_trust = arguments_df[(arguments_df == argument).any(axis=1)]["trust"].item()
    new_trust = expit(current_trust)
    arguments_df.loc[arguments_df['argument'] == argument, 'trust'] = new_trust

print("Number of iterations: ", it-1)
print(arguments_df)

# plot convergence of trust values
#plt.scatter(*zip(*new_trust_list), marker='.', s=3)
#plt.show()

# save final Graph
arglog.create_network(arguments_df, attacks_df, agreement_df, "final_trust_network")
                
                   
for k,v in history.items():
    plt.plot(v)
plt.title("Argument Trust Convergence")
plt.savefig('Argument_trust_convergence.png')
plt.show()