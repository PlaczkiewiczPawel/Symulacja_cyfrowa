import numpy as np
import json

class Generator():
    def __init__(self, base_beta : float, min_t_zero : int, max_t_zero : int, min_t_past : int, max_t_past : int) -> None:
        self.beta = base_beta
        self.min_t_zero = min_t_zero
        self.max_t_zero = max_t_zero
        self.min_t_past = min_t_past
        self.max_t_past = max_t_past
        self.tau = 0
        self.mi = 0
        self.mi_hist = []
        self.tau_hist = []
    def generate_next_user(self):
        self.tau = round(np.random.default_rng().exponential(scale=self.beta)*60, 3)# funkcja generuje po ilu minutach pojawi się kolejny user, mnożymy przeliczając na sekundy
        self.tau_hist.append(self.tau)
    def generator_UE_time_of_life(self):
        self.mi = round(np.random.uniform(1,31), 3) # czas w sekundach na ile czasu user zajmie miejsce w systemie
        self.mi_hist.append(self.mi)  
    def generate_init_no_users(self):
        return int(np.random.uniform(self.max_t_zero,self.max_t_zero))
    def generate_no_users_in_system(self):
        return int(np.random.uniform(self.min_t_past, self.max_t_past))
    
class Generator_seeded():
    def __init__(self, seed : int, base_beta : float, min_t_zero : int, max_t_zero : int, min_t_past : int, max_t_past : int) -> None:
            self.prng = np.random.RandomState(seed)
            self.beta = base_beta
            self.min_t_zero = min_t_zero
            self.max_t_zero = max_t_zero
            self.min_t_past = min_t_past
            self.max_t_past = max_t_past
            self.tau = 0
            self.mi = 0
            self.mi_hist = []
            self.tau_hist = []
    def generate_next_user(self):
        self.tau = round(self.prng.exponential(scale=self.beta)*60,3)# funkcja generuje po ilu minutach pojawi się kolejny user, mnożymy przeliczając na sekundy
        self.tau_hist.append(self.tau) 
    def generator_UE_time_of_life(self):
        self.mi = round(self.prng.uniform(1,31), 3) # czas w sekundach na ile czasu user zajmie miejsce w systemie
        self.mi_hist.append(self.mi)  
    def generate_init_no_users(self):
        return int(self.prng.uniform(self.max_t_zero,self.max_t_zero))
    def generate_no_users_in_system(self):
        return int(self.prng.uniform(self.min_t_past, self.max_t_past))
