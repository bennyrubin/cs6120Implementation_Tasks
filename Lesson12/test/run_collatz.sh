bril2json < test/collatz.bril | brili-trace 7
bril2json < test/collatz.bril | python3 jit.py test/collatz_7.trace | brili -p 3 
