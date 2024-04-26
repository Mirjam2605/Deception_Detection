import yaml
import Argumentation_logic as arglog

def intitial_trust_values(file_path):

    with open(file_path, 'r') as file:
        history =yaml.safe_load(file)
    

    trust_values = {}
    for person in history.keys():
        trust_values[person] = sum(history[person].values())/len(history[person])

    return trust_values
