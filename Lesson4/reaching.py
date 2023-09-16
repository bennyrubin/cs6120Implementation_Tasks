# util files form_blocks, cfg, and briltxt pulled from cs6120 bril repo
import json
from utils.form_blocks import form_blocks
from utils.cfg import block_map, add_terminators, add_entry, edges, reassemble
from utils.briltxt import print_prog, print_label, print_instr
import json
import sys

def get_line(cfg, instr):
    #get the instruction number of a given instruction
    instrs = reassemble(cfg)
    for i, ins in enumerate(instrs):
        if instr == ins:
            return i 
    raise Exception(f"instr {instr} not in program")

def merge(outs, preds):
    union = set()
    for pred in preds:
        union = outs[pred] | union
    return union

def transfer(cfg, b_instrs, b_in):
    defns = set()
    # calculate kills
    # for each dest, remove all of the defns in b_in with that var name
    for instr in b_instrs:
        if 'dest' in instr:
            dest = instr['dest']
            # kill all previous defns of this variable
            to_remove = []
            for el in b_in:
                if el[0] == dest:
                    to_remove.append(el)
            b_in = b_in - set(to_remove)
            defns.add((dest, get_line(cfg, instr)))
    return b_in | defns

def worklist(cfg):
    preds, succs = edges(cfg)
    fst_block = next(iter(cfg.keys()))
    outs = {name: set() for name in cfg.keys()}
    ins = dict()
    ins[fst_block] = set()
    worklist = list(cfg.keys())
    while worklist:
        block = worklist.pop(0)
        currOut = outs[block]
        ins[block] = merge(outs, preds[block])
        outs[block] = transfer(cfg, cfg[block], ins[block])
        if outs[block] != currOut:
            worklist += succs[block]
    return (ins, outs)
    print(f"outs: {outs}")
    print(f"ins: {ins}")

def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

def print_block(block):
    for instr_or_label in block:
        if 'label' in instr_or_label:
            print_label(instr_or_label)
        else:
            print_instr(instr_or_label)



if __name__ == "__main__":
    # in order to work properly must be run directly from Lesson4 dir

    program = json.load(sys.stdin)
    for func in program['functions']:
        cfg = block_map(form_blocks(func['instrs']))
        add_terminators(cfg)
        add_entry(cfg)
        ins, outs = worklist(cfg)

        # reinsert labels
        for name, block in cfg.items():
            block.insert(0, {'label': name})
        
        for key in cfg:
            print(f"in ({key}): {ins[key]}")
            print_block(cfg[key])
            print(f"out ({key}): {outs[key]}")
            #print(cfg[key])

    #print_program(program)
