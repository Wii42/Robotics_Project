# run the code to plot the ground sensor results 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## OBJECT DETECTION

# get data from CSV file
data = pd.read_csv('object_recog.csv', index_col=0)

palette = {
    'Red Block': 'red',
    'Green Block': 'green',
    'Blue Block': 'blue',
    'Black Block': 'black',
    'Black Ball': 'violet',
    'Epuck': 'orange',
}


data['color'] = data['label'].map(palette)

#ax.legend(list(palette.keys()),bbox_to_anchor=(1.02,1),loc="upper left",borderaxespad=0)

threshold = [0,0.7,0.8,0.9,0.95,0.97]
for thresh in threshold:
    
    #https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_with_legend.html
    fig, ax = plt.subplots() 
    for c in palette.keys():
        data[(data["conf"] >= thresh) & (data['label'] == c)].plot.scatter(x='x_center',y='y_center',c=palette[c],s=2,ax=ax)

    plt.legend(list(palette.keys()),bbox_to_anchor=(1.02,1),loc="upper left",borderaxespad=0)

    ax.set_title("Object detection with threshold = {}".format(thresh))

    plt.ylim(0,120)
    plt.xlim(0,160)
    ax.invert_yaxis()
    plt.gca().set_aspect('equal')
    fig.tight_layout()

    save = "object_detection_thresh_{}.png".format(thresh)
    # save plot
    plt.savefig(save)
    plt.show()
    

## COLOR DETECTION
    
# get data from CSV file
data = pd.read_csv('color_recog.csv', index_col=0)

colorpalette = {
    'Red': 'red',
    'Green': 'green',
    'Blue': 'blue',
    'Black': 'black',
}

data['color'] = data['label'].map(colorpalette)

#ax.legend(list(palette.keys()),bbox_to_anchor=(1.02,1),loc="upper left",borderaxespad=0)

area = [100,500,1000,5000,10000]
for a in area:

    #https://matplotlib.org/stable/gallery/lines_bars_and_markers/scatter_with_legend.html
    fig, ax = plt.subplots() 
    for c in colorpalette.keys():
        data[(data["area"] >= a) & (data['label'] == c)].plot.scatter(x='x_center',y='y_center',c=colorpalette[c],s=2,ax=ax)

    plt.legend(list(colorpalette.keys()),bbox_to_anchor=(1.02,1),loc="upper left",borderaxespad=0)

    ax.set_title("Color detection with area = {}".format(a))

    plt.ylim(0,120)
    plt.xlim(0,160)
    ax.invert_yaxis()
    plt.gca().set_aspect('equal')
    fig.tight_layout()

    save = "color_detection_area_{}.png".format(a)
    # save plot
    plt.savefig(save)
    plt.show()


