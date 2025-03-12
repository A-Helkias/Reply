from input_processor import process_single_file

def apply_special_effects(resources, active_resources, turns):
    """ Apply special effects from active resources."""
    for r in active_resources:
        if r["RT"] == "A":
            for res in resources:
                res["RU"] += int(res["RU"] * r["RE"] / 100)
        elif r["RT"] == "B":
            for turn in turns:
                turn[0] += int(turn[0] * r["RE"] / 100)  # Modify TM
                turn[1] += int(turn[1] * r["RE"] / 100)  # Modify TX
        elif r["RT"] == "C":
            for res in resources:
                res["RL"] += int(res["RL"] * r["RE"] / 100)
        elif r["RT"] == "D":
            for turn in turns:
                turn[2] += int(turn[2] * r["RE"] / 100)  # Modify TR

def choose_resources(D, resources, turns):
    active_resources = []
    purchases = []
    budget = D
    accumulator_storage = 0
    
    for t, turn in enumerate(turns):
        apply_special_effects(resources, active_resources, turns)
        
        TM, TX, TR = turn
        powered_buildings = sum(r["RU"] for r in active_resources if r["RW"] > 0)
        
        if powered_buildings < TM and accumulator_storage > 0:
            deficit = TM - powered_buildings
            used = min(deficit, accumulator_storage)
            powered_buildings += used
            accumulator_storage -= used
        
        if powered_buildings > TX:
            accumulator_storage += powered_buildings - TX
            powered_buildings = TX
        
        affordable_resources = [r for r in resources if r["RA"] <= budget]
        affordable_resources.sort(key=lambda r: (-r["RU"], r["RA"]))  
        
        bought = []
        for r in affordable_resources:
            if budget >= r["RA"]:
                budget -= r["RA"]
                active_resources.append(r)
                if r["RT"] == "E":
                    accumulator_storage += r["RE"]  # Add capacity for storage
                bought.append(r["RI"])
                if len(bought) >= 50:
                    break  
        
        if bought:
            purchases.append(f"{t} {len(bought)} " + " ".join(map(str, bought)))
    
    return purchases

def write_output(file_path, purchases):
    with open(file_path, 'w') as file:
        file.write("\n".join(purchases) + "\n")

def process_and_output(input_file, output_file):
    # Process a single input file
    all_data = process_single_file(input_file)
    all_purchases = []
    
    for D, resources, turns in all_data:
        purchases = choose_resources(D, resources, turns)
        all_purchases.extend(purchases)
    
    # Write the output to the specified file
    write_output(output_file, all_purchases)

# Example usage
input_file = "0-demo.txt"  # Path to your input file
output_file = "final_output.txt"  # Output file path
process_and_output(input_file, output_file)

