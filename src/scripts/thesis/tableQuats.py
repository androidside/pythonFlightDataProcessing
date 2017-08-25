'''
Created on 3 june 2017

Main script

@author: Marc Casalprim
'''

print 'Imports...'
from utils.quat import Quat


if __name__ == '__main__':
    qI2S=Quat((100,20,30))
    qG2T=Quat((0,60,0))
    qS2G= Quat([-0.00552599,  0.38242355, -0.0058404 ,  0.92395265])
    #qS2G= Quat((0,-45,0))
    qI2T=qG2T*qS2G*qI2S
    print qI2S
    print qS2G
    print qI2T
    row=['qi','q_j','q_k','q_r']
    roweq=['RA','DEC','ROLL']
    quats=[qI2T,qG2T,qS2G,qI2S]
    print(" & $\prescript{T}{I}{\\textbf{q}}$ & $\prescript{T}{G}{\\textbf{q}}$ & $\prescript{G}{S}{\\textbf{q}}$ & $\\prescript{S}{I}{\\textbf{q}}$ \\\\ \hline")
    for i,r in enumerate(row):
        s="$"+r+"$"
        for q in quats:
            s=s+(" & $%0.3f$" %q.q[i])
        print s+" \\\\"
    
    print(" & $\prescript{T}{I}{\\textbf{q}}$ & $\prescript{T}{G}{\\textbf{q}}$ & $\prescript{G}{S}{\\textbf{q}}$ & $\\prescript{S}{I}{\\textbf{q}}$ \\\\ \hline")
    for i,r in enumerate(roweq):
        s="$"+r+"$"
        for q in quats:
            s=s+(" & $%0.3f$" %q.equatorial[i])
        print s+" \\\\"