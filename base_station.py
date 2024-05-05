class BaseStation:
    def __init__(self, station_id : int):
        self.id = station_id
        self.used_resources = 0
        self.is_sleeping = False
        self.sum_of_sleeping_time = 0
    def save_to_file(self):
        pass
    # Funkcje realizujące zdarzenia
    def add_ue(self):
        pass
    def remove_ue(self):
        pass
    def wake_up(self):
        pass
    def put_to_sleep(self):
        pass