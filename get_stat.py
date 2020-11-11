import numpy as np
import matplotlib.pyplot as plt
from timeit import default_timer as timer
from download import DataDownloader
from collections import defaultdict

def plot_stat(data_source, fig_location = None, show_figure = False):

    data = defaultdict(dict)
    for i in range(data_source[1][0].size):

        
        keyA = str(data_source[1][3][i].astype(object).year)
        keyB = data_source[1][64][i]
        
        if (keyA in data) and (keyB in data[keyA]):
            data[keyA][keyB] += 1
        else:
            data[keyA][keyB] = 0

    for kraj in data['2020']:
        print(data['2020'][kraj])


    i = 1
    plt.figure(figsize=(10,7))
    plt.title("Graf počtu dopravných nehôd v ČR, podľa kraju")
    for year in data:
        print(data[year].values())
        plt.subplot(len(data),1,i)
        plt.spines("top").set_visible(False)
        plt.title(str(year))
        plt.bar(range(len(data[year])), data[year].values(), align='center')
        plt.xticks(range(len(data[year])), list(data[year].keys()))
        
        i += 1
    

    plt.show()

start = timer()
d = DataDownloader()
plot_stat(data_source = d.get_list(), fig_location = None, show_figure = False)
end = timer()
print(end - start)
