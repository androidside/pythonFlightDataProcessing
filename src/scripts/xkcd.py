'''XKCD'''

import matplotlib.pyplot as plt
import numpy as np

with plt.xkcd():

    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.xticks([])
    plt.yticks([])
    ax.set_ylim([-30, 10])
    
    N=100
    data = 10*np.power(np.arange(N)*1.0/N,3)+np.arange(N)*1.0/N*np.sin(np.arange(N)*1.0/N*2*np.pi*4)
    i=np.argmax(data[:int(0.99*N)])
    data[i:] -= N*np.arange(N-i)

    plt.annotate(
        'FLIGHT DAY',
        xy=(i, data[i]), arrowprops=dict(arrowstyle='->'), xytext=(int(0.5*i), -10))

    plt.plot(data)

    plt.xlabel('time')
    plt.ylabel('BETTII readiness')
    
    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    #ax.axhline(0,linestyle='--')
    plt.xticks([])
    plt.yticks([0])
    
    N=100
    data = np.zeros(N)
    data[10:25] = 0.3
    data[80:85] = -np.arange(5)**2
    #data[85]=np.nan
    plt.plot(data)


    plt.xlabel('time')
    plt.ylabel('vertical speed')
    
    fig = plt.figure()
    ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    plt.xticks([])
    plt.yticks([])
    
    N=25
    std=0.9
    x=(1-np.random.rand(N))**(1/(-std+1))+0.1
    y=(x**-0.3)+0.1*np.random.randn(N)
    plt.plot(x,y,'o')

    plt.xlabel('star cameras alignment')
    plt.ylabel('press attention')



plt.show()
