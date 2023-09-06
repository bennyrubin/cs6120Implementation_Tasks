from form_blocks import form_blocks
import json
import sys

class OpTup:

    commutative = ["add","mul"]
    def __init__(self, op, arg1, arg2):
        self.op = op 
        self.arg1 = arg1
        self.arg2 = arg2

    def __eq__(self, obj):
        if not isinstance(obj, OpTup):
            return False
        if not self.op == obj.op:
            return False 
        if self.op in self.commutative:
            return (self.arg1 == obj.arg1 and self.arg2 == obj.arg2) or (self.arg1 == obj.arg2 and self.arg2 == obj.arg1)
        return self.arg1 == obj.arg1 and self.arg2 == obj.arg2
    
    def __hash__(self):
        # canonocolize if commutative
        if self.op in self.commutative:
            if self.arg1 < self.arg2:
                return hash((self.op, self.arg1, self.arg2))
            else:
                return hash((self.op, self.arg2, self.arg1))
        return hash((self.op, self.arg1, self.arg2))

class NumberTable: 
    def __init__(self):
        # map from OpTup to (canonical var, num)
        self.num = 0
        self.mapping = {}
    # TODO: can use dict.items() to go through the values and find th right one. 
    def insert_mapping(tup):
        pass

    def get_num_from_tup(tup): 
        pass

    def get_var_from_num(num):
        pass
        

def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

if __name__ == "__main__":
    #program = json.load(sys.stdin)
    #print_program(program)
    tup = OpTup("add", 3, 2)
    tup2 = OpTup("add", 2, 3)
    tup3 = OpTup("min", 3, 2)
    tup4 = OpTup("min", 2, 3)

    print(f"true: {tup == tup2}")
    print(f"false: {tup3 == tup4}")

    x = {}
    x[tup] = "hello"
    print(x[tup2])