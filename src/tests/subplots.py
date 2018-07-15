'''
Created on May 16, 2018

@author: Sauron
'''
import matplotlib.pyplot as plt

fig, axes = plt.subplots(nrows=3, ncols=4)

# Set the ticks and ticklabels for all axes
plt.setp(axes, xticks=[0.1, 0.5, 0.9], xticklabels=['a', 'b', 'c'],
        yticks=[1, 2, 3])


# Use the pyplot interface to change just one subplot...

for ax in axes.reshape(-1):
    plt.sca(ax) 
    plt.yticks(fontsize=22)


plt.sca(axes[2, 2])
plt.xticks(range(3), ['A', 'Big', 'Cat'], color='red')
plt.yticks(fontsize=22)

fig.tight_layout()
plt.show()