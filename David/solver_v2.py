import optuna

class Resource:
    def __init__(self, RIr, RAr, RPr, RWr, RMr, RLr, RUr, RTr, REr):
        self.RI = RIr
        self.RA = RAr
        self.RP = RPr
        self.RW = RWr
        self.RM = RMr
        self.RL = RLr
        self.RU = RUr
        self.RT = RTr
        self.RE = REr

class Turn:
    def __init__(self, TM, TX, TR):
        self.TM = TM
        self.TX = TX
        self.TR = TR

class PurchasedResource:
    def __init__(self, resource_index, life_left, active_left, downtime_left):
        self.resource_index = resource_index
        self.life_left = life_left
        self.active_left = active_left
        self.downtime_left = downtime_left

class GreenRevolutionGame:
    def __init__(self, data_tokens):
        self.parse_input(data_tokens)
        self.budget = self.D
        self.purchased_resources = []
        self.output_lines = []
        self.total_profit = 0

    def parse_input(self, data):
        idx = 0
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
            if RTr in ['A','B','C','D','E']:
                REr = int(data[idx]); idx += 1
            else:
                REr = 0

            self.resources.append(Resource(RIr, RAr, RPr, RWr, RMr, RLr, RUr, RTr, REr))

        self.turns = []
        for _ in range(self.T):
            TMt = int(data[idx]); idx += 1
            TXt = int(data[idx]); idx += 1
            TRt = int(data[idx]); idx += 1
            self.turns.append(Turn(TMt, TXt, TRt))

    def run_with_plan(self, purchase_plan):
        self.budget = self.D
        self.purchased_resources.clear()
        self.output_lines.clear()
        self.total_profit = 0

        for turn_idx in range(self.T):
            turn_data = self.turns[turn_idx]
            chosen = purchase_plan[turn_idx]
            if chosen is not None:
                # If you allow multiple resources in a single turn, 
                # ensure 'chosen' is a list. For now assume single resource or None.
                if not isinstance(chosen, list):
                    chosen = [chosen]
                total_activation_cost = 0
                for resource_idx in chosen:
                    total_activation_cost += self.resources[resource_idx].RA
                if total_activation_cost <= self.budget:
                    self.budget -= total_activation_cost
                    for resource_idx in chosen:
                        r = self.resources[resource_idx]
                        self.purchased_resources.append(
                            PurchasedResource(resource_idx, r.RL, r.RW, 0)
                        )
                    if len(chosen) > 0:
                        line = f"{turn_idx} {len(chosen)}"
                        for resource_idx in chosen:
                            line += f" {self.resources[resource_idx].RI}"
                        self.output_lines.append(line)

            maintenance_cost = 0
            powered_buildings = 0
            for pr in self.purchased_resources:
                if pr.life_left > 0:
                    r_idx = pr.resource_index
                    maintenance_cost += self.resources[r_idx].RP
                    if pr.active_left > 0:
                        powered_buildings += self.resources[r_idx].RU

            self.budget -= maintenance_cost

            if powered_buildings >= turn_data.TM:
                profit = min(powered_buildings, turn_data.TX) * turn_data.TR
            else:
                profit = 0

            self.budget += profit
            self.total_profit += profit

            for pr in self.purchased_resources:
                if pr.life_left > 0:
                    if pr.active_left > 0:
                        pr.active_left -= 1
                        if pr.active_left == 0:
                            r_idx = pr.resource_index
                            pr.downtime_left = self.resources[r_idx].RM
                    else:
                        if pr.downtime_left > 0:
                            pr.downtime_left -= 1
                            if pr.downtime_left == 0:
                                r_idx = pr.resource_index
                                pr.active_left = self.resources[r_idx].RW
                    pr.life_left -= 1
            self.purchased_resources = [p for p in self.purchased_resources if p.life_left > 0]

        return self.total_profit

    def write_output(self, filename):
        with open(filename, "w") as f:
            for line in self.output_lines:
                f.write(line + "\n")


def create_purchase_plan(trial, T, R):
    plan = []
    for turn_idx in range(T):
        choice = trial.suggest_categorical(
            f"buy_turn_{turn_idx}",
            [None] + list(range(R))
        )
        plan.append(choice)
    return plan

def objective(trial, data_tokens):
    game = GreenRevolutionGame(data_tokens)
    plan = create_purchase_plan(trial, T=game.T, R=game.R)
    score = game.run_with_plan(plan)
    return score

def run_optuna_optimization(input_filename="input.txt", n_trials=100):
    # Read input
    with open(input_filename, "r") as f:
        data = f.read().strip().split()

    # Wrap objective
    def optuna_objective(trial):
        return objective(trial, data)

    # Create the study and run
    study = optuna.create_study(direction="maximize")
    study.optimize(optuna_objective, n_trials=n_trials)

    print("Best Value (Score):", study.best_value)
    print("Best Params:", study.best_params)

    # Reconstruct best plan
    game_for_best = GreenRevolutionGame(data)
    best_plan = []
    for t in range(game_for_best.T):
        param_key = f"buy_turn_{t}"
        best_plan.append(study.best_params[param_key])

    final_score = game_for_best.run_with_plan(best_plan)
    game_for_best.write_output("./outputs/output.txt")
    print("Final plan’s score:", final_score)


if __name__ == "__main__":
    run_optuna_optimization("./inputs/0-demo.txt", n_trials=500)
