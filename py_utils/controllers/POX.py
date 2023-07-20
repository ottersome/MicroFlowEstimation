from mininet.node import Controller
from os import environ

POXDIR = environ[ 'HOME' ] + '/pox'
# Learning Controller taken from:
# http://mininet.org/blog/2013/06/03/automating-controller-startup/

class POX( Controller ):
    def __init__( self, name, cdir=POXDIR,
                  command='python pox.py',
                  cargs=( 'openflow.of_01 --port=%s '
                          'forwarding.l2_learning' ),
                  **kwargs ):
        Controller.__init__( self, name, cdir=cdir,
                             command=command,
                             cargs=cargs, **kwargs )

