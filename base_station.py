from sortedcontainers import SortedList
class BaseStation:
    def __init__(self, station_id : int):
        self.id = station_id
        self.used_resources = 0
        self.is_sleeping = False
        self.sum_of_sleeping_time = 0
    def save_to_file(self):
        pass
    # Funkcje realizujące zdarzenia.  
    def remove_ue(self):
        if self.used_resources > 0:
            self.used_resources -= 1
        else:
            pass
    def wake_up(self):
        self.is_sleeping = False
    def put_to_sleep(self):
        self.is_sleeping = True
        



