import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st


import csv

def csv_no_of_cols(path : str):
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
           number_of_cols = len(row) - 1
           return number_of_cols
    csvfile.close()
    
def read_col(path : str):
    title = True
    L = 0
    data = []
    with open(path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if title == True:
                title = False
                L = round(float(row[col]), 3)
            else:
                data.append(float(row[col]))
    csvfile.close()
    return L, data

if __name__ == '__main__':
    path = r'Wyniki\seed_12\L_seed_12.csv'      
    number_of_cols = csv_no_of_cols(path)
    plot_data = {"L" : [], "mean" : [], "mean-conf_low" : [], "conf_high-mean" : []}
    col = 1
    for i in range(number_of_cols):
        L, data = read_col(r'Wyniki\seed_12\L_seed_12.csv')
        col+=1
        mean = round(np.mean(data), 3)
        confidence_interval = 0.1
        confidence_interval_values = st.t.interval(confidence_interval, len(data)-1, loc=mean, scale=st.sem(data))
        confidence_low = mean - confidence_interval_values[0] 
        confidence_high = confidence_interval_values[1] - mean
        plot_data["L"].append(L)
        plot_data["mean"].append(mean)
        plot_data["mean-conf_low"].append(mean - confidence_low)
        plot_data["conf_high-mean"].append(mean + confidence_high)
    plt.rc('figure', figsize=(10, 7))
    plt.figure()
    plot_data["L"] = [elem*100 for elem in plot_data["L"]]
    plot_data["mean"] = [elem*100 for elem in plot_data["mean"]]
    plot_data["conf_high-mean"] = [elem*100 for elem in plot_data["conf_high-mean"]]
    plot_data["mean-conf_low"] = [elem*100 for elem in plot_data["mean-conf_low"]]
    plt.plot(plot_data["L"], plot_data["mean-conf_low"], 'o', label="Dolny przedział ufności")
    plt.plot(plot_data["L"], plot_data["conf_high-mean"], 'o', label="Górny przedział ufności")
    plt.plot(plot_data["L"], plot_data["mean"], 'o', label="Średnia dobowa ilość traconych zgłoszeń")
    plt.axhline(y=5, color='red', label="Szukany próg 5%")
    plt.yticks(np.arange(min(plot_data["mean"]), max(plot_data["mean"]), 1))
    xticks = [round(elem) for elem in plot_data["L"]]
    plt.xticks(xticks)
    plt.title(f"Średnia dobowa ilość traconych zgłoszeń w funkcji progu uśpienia L dla 10 symulacji.")
    plt.ylabel("Średnia dobowa liczba traconych zgłoszeń. [%]")
    plt.xlabel("Próg L wyłączania stacji bazowej [%]")
    plt.legend(loc = 'upper left')
    plt.savefig(r'Wyniki\seed_12\L_seed_12.png')
    plt.show()      
        
   