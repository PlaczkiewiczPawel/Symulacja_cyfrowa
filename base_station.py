from sortedcontainers import SortedList
class BaseStation:
    def __init__(self, station_id : int):
        self.id = station_id
        self.used_resources = 0
        self.is_sleeping = False
        self.sleep_process = False
        self.sum_of_sleeping_time = 0
        self.overflow_process = False
    def save_to_file(self):
        pass
    # Funkcje realizujące zdarzenia.  
    def remove_ue(self):
        if self.used_resources > 0:
            self.used_resources -= 1
        else:
            pass
    def wake_up(self, no_of_users : int):
        self.is_sleeping = False
        self.used_resources = no_of_users
    def put_to_sleep(self):
        self.is_sleeping = True
        self.sleep_process = False
        self.used_resources = 0
    def overflow_H(self, no_of_users : int):
        self.overflow_process = False
        self.used_resources -= no_of_users