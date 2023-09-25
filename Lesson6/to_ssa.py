# util files form_blocks, cfg, and briltxt pulled from cs6120 bril repo
import json
from utils.form_blocks import form_blocks
from utils.cfg import block_map, add_terminators, add_entry, edges, reassemble
from utils.briltxt import print_prog, print_label, print_instr
from utils.correct_dom import get_dom, dom_tree, dom_fronts
import json
import sys
import copy


class Phi:
    def __init__(self, old_name):
        self.old_name = old_name
        self.dest = ""
        self.labels = []
        self.args = []

    def __repr__(self):
        return f"{{old_name: {self.old_name}, dest: {self.dest}, labels: {self.labels}, args: {self.args}}}"

    def __hash__(self):
        return hash(self.old_name)
    
    def __eq__(self, other):
        return (type(self) == type(other) and
            self.old_name == other.old_name)

def getDefns(cfg, types = {}):
    #for each variable v gets the blocks where v is assigned (dest)
    defs = {}
    for block in cfg:
        for instr in cfg[block]:
            if "dest" in instr:
                dest = instr['dest']
                if dest in defs:
                    defs[dest].add(block)
                    types[dest] = instr['type']
                else:
                    defs[dest] = set([block])
                    types[dest] = instr['type']
    return defs, types

def phiNodes(cfg):
    # keep track of which blocks have which phi-nodes for which variables, but don't actually insert until I rename the instructions

    defs, _ = getDefns(cfg)
    preds, succs = edges(cfg) 
    entry = next(iter(cfg.keys()))
    dom = get_dom(succs, entry)
    DF = dom_fronts(dom, succs)
    phis = {block: set() for block in cfg} # will be a set of variables that have phi nodes for that block
    for v in defs:
        defs_block_list = list(defs[v])
        for d in defs_block_list:
            for block in DF[d]:
                phis[block].add(Phi(v))
                if block not in defs_block_list:
                    defs_block_list.append(block)
    return phis

def rename(cfg, args = {}):
    types = {}
    for arg in args:
        types[arg['name']] = arg['type']
    defs, types = getDefns(cfg, types)
    entry = next(iter(cfg.keys()))
    stack = {var: [] for var in defs}
    for arg in args: #add arguments to stacks
        stack[arg['name']] = [arg['name']]
    counter = {var: 0 for var in defs}
    preds, succs = edges(cfg)
    dom = get_dom(succs, entry)
    doms_tree = dom_tree(dom)
    phis = phiNodes(cfg)
    #print(dom_tree)
    #print(phis)
    phis = {block : [phi for phi in phis[block]] for block in phis}

    def new_name(var):
        name = f"{var}_num{counter[var]}"
        counter[var] += 1
        return name
    
    def rename_helper(block):
        nonlocal stack
        old_stack = copy.deepcopy(stack)

        for phi in phis[block]:  # first have to rename all the phi nodes and update the stacks 
            phi.dest = new_name(phi.old_name)
            stack[phi.old_name].append(phi.dest)

        for instr in cfg[block]:
            if 'args' in instr: #replace args with stack names
                instr['args'] = [stack[arg][-1] for arg in instr['args']]
            if 'dest' in instr: #replace dest with new name
                name = new_name(instr['dest'])
                stack[instr['dest']].append(name)
                instr['dest'] = name 

        for s in succs[block]:
            for p in phis[s]:
                var = p.old_name
                if stack[var]: # if this variable exists in this execution 
                    p.labels.append(block) # tuple of label and var name
                    p.args.append(stack[var][-1])
                else: # if it doesn't exist say its undefined. 
                    p.labels.append(block)
                    p.args.append("_UNDEFINED_")

        for b in doms_tree[block]:
            rename_helper(b)

        stack.clear() 
        stack = old_stack # double check this pointer logic
    
    rename_helper(entry)

    # add phi instrs to blocks
    for block, phi_list in phis.items():
        for phi in phi_list:
            if phi.dest == '' or len(phi.args) == 0:
                continue
            instr = {
                'op': 'phi',
                'dest': phi.dest,
                'type': types[phi.old_name],
                'labels': phi.labels,
                'args': phi.args
            }
            cfg[block].insert(0, instr)

def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

if __name__ == "__main__":
    # in order to work properly must be run directly from Lesson6 dir

    program = json.load(sys.stdin)
   #print(program)

    for func in program['functions']:
        cfg = block_map(form_blocks(func['instrs']))
        add_terminators(cfg)
        #print(cfg)
        # defs, _ = getDefns(cfg)
        # print(defs)
        if 'args' in func:
            rename(cfg, func['args'])
        else:
            rename(cfg)
        func['instrs'] = reassemble(cfg)
    #print_prog(program)
    print_program(program)
