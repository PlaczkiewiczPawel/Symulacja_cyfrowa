import random
import csv
import os


if not os.path.exists('seeds'):
    os.mkdir('seeds')
    
for i in range (30):
        for j in range(1000):
            with open(f'seeds/seed_{i}.csv', 'a+', newline='') as file:
                rand = int(random.uniform(random.uniform(500,900),random.uniform(1000, 1400)))
                file.write(str(rand)+'\n')