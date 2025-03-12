class Game:
    def __init__(self, D:int, R:int, T:int, Resources:list):
        # Create the game with the budget, resources and number of turns
        self.D = D
        self.R = R
        self.T = T



class Resource:
    def __init__(self, RN, RI, RA, RP, RW, RM, RL, RU, RT=None):
        """"
        • RI: Resource identifier.
        • RN: Resource name
        • RA: Activation cost (one-time initial expenditure).
        • RP: Periodic cost for each turn of life (maintenance expense).
        • RW: Number of consecutive turns in which the resource is active and
        generates profit.
        • RM: Number of downtime turns required after a full cycle of activity
        (maintenance).
        • RL: Total life cycle of the resource (in turns), including both active and
        downtime periods, after which the resource becomes obsolete.
        • RU: Number of buildings the resource can power in each active turn.
        • RT: Special effect of the resource.
        """
        if RN == "A":
            pass
        elif RN == "B":
            pass
        elif RN == "C":
            pass
        elif RN == "D":
            pass
        elif RN == "E":
            pass
        
        