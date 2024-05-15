import numpy as np
import json
try:
    with open ("config.json") as config_f:
        config = json.load(config_f)
        MIN_T_ZERO = config["NUMBER_OF_USERS_T_ZERO_RAND_MIN"]
        MAX_T_ZERO = config["NUMBER_OF_USERS_T_ZERO_RAND_MAX"]
        MIN_T_PAST  = config["NUMBER_OF_USERS_FROM_PAST_RAND_MIN"]
        MAX_T_PAST = config["NUMBER_OF_USERS_FROM_PAST_RAND_MAX"]    
except FileNotFoundError:
    print("Brak pliku konfiguracyjnego.")
    exit()
    


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
        return int(np.random.uniform(MIN_T_ZERO,MAX_T_ZERO))
    def generate_no_users_in_system(self):
        return int(np.random.uniform(MIN_T_PAST,MAX_T_PAST))
    
class Generator_seeded():
    def __init__(self, seed : int) -> None:
            self.prng = np.random.RandomState(seed)
            self.beta = 0
            self.tau = 0
            self.mi = 0
            self.mi_hist = []
            self.tau_hist = []
    def generate_next_user(self):
        self.tau = round(self.prng.exponential(scale=self.beta)*60,2)# funkcja generuje po ilu minutach pojawi się kolejny user, mnożymy przeliczając na sekundy
        #self.tau_hist.append(self.tau)
        self.mi = round(self.prng.uniform(1,31), 2) # czas w sekundach na ile czasu user zajmie miejsce w systemie
        #self.mi_hist.append(self.mi)  
    def generate_init_no_users(self):
        return int(self.prng.uniform(MIN_T_ZERO,MAX_T_ZERO))
    def generate_no_users_in_system(self):
        return int(self.prng.uniform(MIN_T_PAST,MAX_T_PAST))
