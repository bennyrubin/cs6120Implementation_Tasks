bril2json < test/loopfact.bril | brili-trace 3
bril2json < test/loopfact.bril | python3 jit.py test/loopfact_3.trace | brili -p 3 
bril2json < test/loopfact.bril | python3 jit.py test/loopfact_3.trace | brili -p 1 
bril2json < test/loopfact.bril | brili -p 3 