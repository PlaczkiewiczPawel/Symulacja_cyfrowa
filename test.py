class Test:
    def __init__(self, value, is_now) -> None:
        self.value = value
        self.is_now = is_now
        
list_test = [Test(1, True), Test(2, True), Test(3, True)]

minValue = min(list_test, key = lambda obj: (obj.value) and obj.value==True).value
print(minValue)