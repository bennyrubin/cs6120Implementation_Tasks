from form_blocks import form_blocks
from tdce import eliminate_dead_code_program
import json
import sys

class OpTup:

    commutative = ["add","mul"]
    def __init__(self, op, arg1, arg2):
        self.op = op 
        self.arg1 = arg1
        self.arg2 = arg2

    def __repr__(self):
        return f"({self.op}, {self.arg1}, {self.arg2})"

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
    
    def get_arg(self,i):
        if i == 0:
            return self.arg1
        elif i == 1:
            if self.arg2 is not None: 
                return self.arg2
        raise Exception(f"Cannot get instruction argument {i} that doesn't exist for tup {self}")
    
    def create_tup(env, instr):
        op = instr['op']
        if op == "const":
            arg1 = instr['value']
            if arg1 is True:
                arg1 = "true"
            elif arg1 is False:
                arg1 = "false"
            return OpTup(op, arg1, None)
        if len(instr['args']) == 2:
            arg1 = env[instr['args'][0]]
            arg2 = env[instr['args'][1]]
        elif len(instr['args']) == 1:
            arg1 = env[instr['args'][0]]
            arg2 = None
        return OpTup(op, arg1, arg2)


class NumberTable: 
    def __init__(self):
        # map from OpTup to (canonical var, num)
        self.num = 0
        self.mapping = {}
    # TODO: can use dict.items() to go through the values and find the right one. 
    def insert_mapping(self, tup, var):
        self.mapping[tup] = (var, self.num)
        self.num += 1
        return self.num - 1

    def get_num_from_tup(self, tup): 
        if self.mapping.get(tup):
            return self.mapping[tup][1]
        return None
    def get_var_from_tup(self, tup):
        if self.mapping.get(tup):
            return self.mapping[tup][0]
        return None
            
    def get_var_from_num(self, in_num):
        for (tup, (var, num)) in self.mapping.items():
            if in_num == num:
                return var


def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

def overwritten_later(block, i):
    instr = block[i]
    dst = instr['dest']
    for j in range(i+1,len(block)):
        if 'dest' in block[j]:
            if block[j]['dest'] == dst:
                return True
    return False

def read_before_written(block):
    written = set()
    read_before_write = set()
    for instr in block:
        if 'args' in instr:
            for arg in instr['args']:
                if arg not in written:
                    read_before_write.add(arg)
        if 'dest' in instr:
            written.add(instr['dest'])
    return read_before_write

def LVN_block(block, args):
    env = {} # variable to number in table
    table = NumberTable()
    counter = 0
    # Need to add all variables that are read before written to 
    # for arg in args:
    #     num = table.insert_mapping(None, arg['name'])
    #     env[arg['name']] = num
    for var in read_before_written(block):
        num = table.insert_mapping(counter, var)
        counter += 1
        env[var] = num
    for i, instr in enumerate(block):
        if 'dest' in instr: 

            # copy propogation
            # if instr['op'] == 'id':
            #     # get the number where the current var is pointing
            #     num = env[instr['args'][0]]
            #     env[instr['dest']] = num 
            #     instr['args'][0] = table.get_var_from_num(num)
            #     continue
            # uses an arg that wasn't defined (not supported instruciton) then skip
            if 'args' in instr: 
                skip = False
                for arg in instr['args']:
                    if env.get(arg) is None:
                        skip = True
                if skip:
                    continue
            # don't want to value-number calls because they might have side effects
            if instr['op'] in ['ptradd', 'alloc','load']:
                continue
            if instr['op'] == 'call':
                num = table.insert_mapping(counter, instr['dest'])
                counter += 1
                env[instr['dest']] = num
                # replace args
                if 'args' in instr:
                    for i in range(len(instr['args'])):
                            instr['args'][i] = table.get_var_from_num(env[instr['args'][i]])
                continue
            
            tup = OpTup.create_tup(env, instr)
            # if tup in table
            if table.get_var_from_tup(tup): 
                var = table.get_var_from_tup(tup)
                num = table.get_num_from_tup(tup)
                instr['op'] = 'id'
                instr['args'] = [var]
                env[instr['dest']] = num

            # it's a new value
            else:
                overwritten = overwritten_later(block, i)
                if (overwritten):
                    old_dest = instr['dest']
                    instr['dest'] = instr['dest'] + "1"
                num = table.insert_mapping(tup, instr['dest'])
                env[instr['dest']] = num 
                if (overwritten):
                    env[old_dest] = num
                # rewrite instruction to use new canonical variable names
                if 'args' in instr:
                    for i in range(len(instr['args'])):
                        instr['args'][i] = table.get_var_from_num(tup.get_arg(i))
        
        # re-writing arguments in non value operations
        else:
            if 'op' in instr and instr['op'] in ['store', 'free']:
                continue
            if 'args' in instr:
                skip = False
                for arg in instr['args']:
                    if env.get(arg) is None:
                        skip = True
                if skip:
                    continue
                for i in range(len(instr['args'])):
                        instr['args'][i] = table.get_var_from_num(env[instr['args'][i]])


def LVN_program(prog):
    functions = prog['functions']
    for func in functions:
        blocks = list(form_blocks(func['instrs']))
        if func.get('args'):
            args = func['args']
        else:
            args = []
        [LVN_block(block, args) for block in blocks]    
        func['instrs'] = [instr for block in blocks for instr in block]
    eliminate_dead_code_program(prog)

if __name__ == "__main__":
    #command: bril2json < {file}| python3 lvn_solution.py | bril2txt

    program = json.load(sys.stdin)
    #print_program(program)
    LVN_program(program)
    print_program(program)
    #TODO: optimization for copy propogation
    # ISSUE in python with True and 1 hashing to the same value