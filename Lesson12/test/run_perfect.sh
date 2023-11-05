bril2json < test/perfect.bril | brili-trace 496
bril2json < test/perfect.bril | python3 jit.py test/perfect_496.trace | brili -p 496
