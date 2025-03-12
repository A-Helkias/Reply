# input_processor.py

import os

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Read initial values
    D, R, T = map(int, lines[0].split())
    
    # Read resources
    resources = []
    for i in range(1, R + 1):
        data = list(map(str, lines[i].split()))
        resources.append({
            "RI": int(data[0]), "RA": int(data[1]), "RP": int(data[2]),
            "RW": int(data[3]), "RM": int(data[4]), "RL": int(data[5]),
            "RU": int(data[6]), "RT": data[7], "RE": int(data[8]) if len(data) > 8 else 0
        })
    
    # Read turns
    turns = []
    for i in range(R + 1, R + 1 + T):
        turns.append(list(map(int, lines[i].split())))
    
    return D, resources, turns

def process_multiple_files(input_folder):
    all_data = []
    
    for file_name in sorted(os.listdir(input_folder)):
        input_path = os.path.join(input_folder, file_name)
        D, resources, turns = read_input(input_path)
        all_data.append((D, resources, turns))
    
    return all_data
