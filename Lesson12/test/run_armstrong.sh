bril2json < test/armstrong.bril | brili-trace 407 
bril2json < test/armstrong.bril | python3 jit.py test/armstrong_407.trace | brili -p 3 
