class Resource:
    """
    Represents a single resource definition (from the R lines in input).
    """
    def __init__(self, RIr, RAr, RPr, RWr, RMr, RLr, RUr, RTr, REr):
        self.RI = RIr  # Resource ID
        self.RA = RAr  # Activation cost
        self.RP = RPr  # Periodic (maintenance) cost
        self.RW = RWr  # Number of consecutive active turns
        self.RM = RMr  # Number of downtime turns required after active cycle
        self.RL = RLr  # Total life in turns
        self.RU = RUr  # Buildings powered when active
        self.RT = RTr  # Special effect type
        self.RE = REr  # Special effect parameter (percentage or capacity)


class Turn:
    """
    Represents a single turn's constraints: min building (TM), max building (TX), profit per building (TR).
    """
    def __init__(self, TM, TX, TR):
        self.TM = TM
        self.TX = TX
        self.TR = TR


class PurchasedResource:
    """
    Represents a resource instance that has been purchased, tracking where it is in its
    active/downtime life cycle.
    """
    def __init__(self, resource_index, life_left, active_left, downtime_left):
        self.resource_index = resource_index  # index into the 'resources' list
        self.life_left = life_left
        self.active_left = active_left
        self.downtime_left = downtime_left


class GreenRevolutionGame:
    """
    Manages all data (budget, resources, turns), runs the simulation turn by turn,
    and decides which resources to purchase (naively).
    """
    def __init__(self, data_tokens):
        # Parse the data from a list of tokens (strings).
        self.parse_input(data_tokens)
        self.budget = self.D
        self.purchased_resources = []  # list of PurchasedResource
        self.output_lines = []         # lines to write into output file

    def parse_input(self, data):
        idx = 0
        # First line: D, R, T
        self.D = int(data[idx]); idx += 1
        self.R = int(data[idx]); idx += 1
        self.T = int(data[idx]); idx += 1

        self.resources = []
        for _ in range(self.R):
            RIr = int(data[idx]); idx += 1
            RAr = int(data[idx]); idx += 1
            RPr = int(data[idx]); idx += 1
            RWr = int(data[idx]); idx += 1
            RMr = int(data[idx]); idx += 1
            RLr = int(data[idx]); idx += 1
            RUr = int(data[idx]); idx += 1

            RTr = data[idx];      idx += 1
            if RTr in ['A', 'B', 'C', 'D', 'E']:
                REr = int(data[idx])
                idx += 1
            else:
                REr = 0

            self.resources.append(Resource(RIr, RAr, RPr, RWr, RMr, RLr, RUr, RTr, REr))

        self.turns = []
        for _ in range(self.T):
            TMt = int(data[idx]); idx += 1
            TXt = int(data[idx]); idx += 1
            TRt = int(data[idx]); idx += 1
            self.turns.append(Turn(TMt, TXt, TRt))

    def decide_which_resource_to_buy(self):
        """
        Naive: picks a single resource with the best RU/(RA+RP) ratio,
        if affordable. Returns its index in self.resources, or None if no resource is affordable.
        """
        best_idx = None
        best_score = -1.0

        for i, r in enumerate(self.resources):
            if r.RA <= self.budget:
                cost = float(r.RA + r.RP) if (r.RP > 0) else float(r.RA)
                ratio = float(r.RU) / cost if cost > 0 else r.RU
                if ratio > best_score:
                    best_score = ratio
                    best_idx = i
        return best_idx

    def run(self):
        """
        Simulate T turns. On each turn:
          1) Possibly buy resources (if affordable).
          2) Pay maintenance costs.
          3) Compute powered buildings, check if >= TM => compute profit.
          4) Update budget, reduce lifecycles, remove obsolete resources.
        """
        for turn_idx in range(self.T):
            turn_data = self.turns[turn_idx]

            # -- 1) Purchase Phase (naive) --
            chosen_idx = self.decide_which_resource_to_buy()
            if chosen_idx is not None:
                cost_needed = self.resources[chosen_idx].RA
                if cost_needed <= self.budget:
                    # Buy this resource
                    self.budget -= cost_needed
                    r = self.resources[chosen_idx]
                    # Add a new purchased resource
                    self.purchased_resources.append(
                        PurchasedResource(
                            resource_index=chosen_idx,
                            life_left=r.RL,
                            active_left=r.RW,
                            downtime_left=0
                        )
                    )
                    # Record purchase in output (turn, count=1, resourceID)
                    line = f"{turn_idx} 1 {r.RI}"
                    self.output_lines.append(line)

            # -- 2) Pay maintenance + track total powered buildings --
            maintenance_cost = 0
            powered_buildings = 0

            for pr in self.purchased_resources:
                if pr.life_left > 0:
                    # Maintenance cost
                    r_idx = pr.resource_index
                    maintenance_cost += self.resources[r_idx].RP
                    # If in active phase, add RU
                    if pr.active_left > 0:
                        powered_buildings += self.resources[r_idx].RU

            # Subtract maintenance cost from budget
            self.budget -= maintenance_cost

            # -- 3) Compute profit (if TM is met) --
            if powered_buildings >= turn_data.TM:
                profit = min(powered_buildings, turn_data.TX) * turn_data.TR
            else:
                profit = 0

            # Update budget
            self.budget += profit

            # -- 4) Decrement resource lifecycles --
            for pr in self.purchased_resources:
                if pr.life_left > 0:
                    # If active
                    if pr.active_left > 0:
                        pr.active_left -= 1
                        # If just ended active phase, set downtime
                        if pr.active_left == 0:
                            r_idx = pr.resource_index
                            pr.downtime_left = self.resources[r_idx].RM
                    else:
                        # In downtime
                        if pr.downtime_left > 0:
                            pr.downtime_left -= 1
                            if pr.downtime_left == 0:
                                r_idx = pr.resource_index
                                pr.active_left = self.resources[r_idx].RW

                    # Decrease total life
                    pr.life_left -= 1

            # Remove dead resources
            self.purchased_resources = [pr for pr in self.purchased_resources if pr.life_left > 0]

    def write_output(self, filename):
        """
        Writes the recorded purchase lines to the given file.
        Each line is "turn Rcount RI1 RI2 ...".
        """
        with open(filename, "w") as f:
            for line in self.output_lines:
                f.write(line + "\n")


def solve(input_filename="0-demo.txt", output_filename="output.txt"):
    """
    Reads all tokens from `input_filename`, runs the naive solver,
    and writes the output to `output_filename`.
    """
    # Read the entire input file into a string, then split into tokens
    with open(input_filename, "r") as f:
        data = f.read().strip().split()
    
    # Create and run the game simulation
    game = GreenRevolutionGame(data)
    game.run()
    
    # Save the purchase decisions to output
    game.write_output(output_filename)


if __name__ == "__main__":
    # Example usage:
    # python solver.py  (it will read from "input.txt" and write to "output.txt")
    solve("0-demo.txt", "output.txt")
