import numpy as np
class Generator():
    def __init__(self) -> None:
        self.beta = 0
        self.tau = 0
        self.mi = 0
        self.mi_hist = []
        self.tau_hist = []
    def generate_next_user(self):
        self.tau = round(np.random.default_rng().exponential(scale=self.beta)*60,2)# funkcja generuje po ilu minutach pojawi się kolejny user, mnożymy przeliczając na sekundy
        self.tau_hist.append(self.tau)
        self.mi = round(np.random.uniform(1,31), 2) # czas w sekundach na ile czasu user zajmie miejsce w systemie
        self.mi_hist.append(self.mi)  
    def generate_init_no_users(self):
        return int(np.random.uniform(1,31))
    def generate_no_users_in_system(self):
        return int(np.random.uniform(1,31))
