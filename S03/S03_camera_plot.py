# run the cell to plot the camera histograms
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
import numpy as np

def camera_histogram(name,letterbox=False,letterbox_width=10) :
    
    fig = plt.figure(figsize=(15,9))
    
    ylim = 19200
    if letterbox :
        ylim = 160*letterbox_width
        
    x1 = 0
    x2 = 160
    if letterbox :
        x1 = 60-int(letterbox_width/2)
        x2 = 59+int(letterbox_width/2)

    grid = plt.GridSpec(4, 3, wspace=0.1, hspace=0.2, figure=fig)

    b_hist = plt.subplot(grid[2, 0:2])
    b_hist.hist(img[x1:x2,:,2].ravel(), bins=255, range=(0, 255), fc='b', ec='b');
    b_hist.set_ylim(0,ylim)

    g_hist = plt.subplot(grid[1, 0:2],sharex=b_hist)
    g_hist.hist(img[x1:x2,:,1].ravel(), bins=255, range=(0, 255), fc='g', ec='g');
    g_hist.set_ylim(0,ylim)

    r_hist = plt.subplot(grid[0, 0:2],sharex=b_hist)
    r_hist.hist(img[x1:x2,:,0].ravel(), bins=255, range=(0, 255), fc='r', ec='r');
    r_hist.set_ylim(0,ylim)

    b_img = plt.subplot(grid[2, 2])
    plt.imshow(img[x1:x2,:,2], cmap="Blues", vmin=0, vmax=255)
    plt.colorbar()

    plt.subplot(grid[1, 2])
    plt.imshow(img[x1:x2,:,1], cmap="Greens", vmin=0, vmax=255)
    plt.colorbar()

    plt.subplot(grid[0, 2],sharex=b_img)
    plt.imshow(img[x1:x2,:,0], cmap="Reds", vmin=0, vmax=255)
    plt.colorbar()

    ax = plt.subplot(grid[3, 2],sharex=b_img)
    plt.imshow(img)
    plt.colorbar()
    fig = plt.gcf()
    fig.delaxes(fig.get_axes()[-1])
    
    if letterbox:
        # Create a Rectangle patch and Add the patch to the Axes
        rect = patches.Rectangle((0,x1),160,letterbox_width,linewidth=1,edgecolor='k',facecolor='none')
        ax.add_patch(rect)

    plt.savefig(name+'.png')
    plt.show()

img = mpimg.imread('./images_216_blue1/image003.bmp') # do not use the first image as it may be black while the camera gets ready

camera_histogram('histogram')
camera_histogram('histogram_letterbox',letterbox=True)

