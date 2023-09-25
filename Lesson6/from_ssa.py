# util files form_blocks, cfg, and briltxt pulled from cs6120 bril repo
import json
from utils.form_blocks import form_blocks
from utils.cfg import block_map, add_terminators, add_entry, edges, reassemble
from utils.briltxt import print_prog, print_label, print_instr
from utils.correct_dom import get_dom, dom_tree, dom_fronts
import json
import sys
import copy

def from_ssa(cfg):
    preds, succs = edges(cfg)
    new_cfg = copy.deepcopy(cfg)
    for block in cfg:
        for i, instr in enumerate(cfg[block]):
            if instr['op'] == "phi":
                # for each of the argument/label combos, add into the label block at the end an instruction to set the dest to id of the argument
                for (arg, label) in zip(instr['args'], instr['labels']):
                    if arg == "_UNDEFINED_":
                        # insert a new instruction at the end of the label, where if it's int it's const 0 if it's bool then const false
                        new_instr = {
                            'op': 'const',
                            'type': instr['type'],
                            'dest': instr['dest'],
                            'value': 0 if instr['type'] == "int" else False,
                        }
                        new_cfg[label].insert(-1, new_instr) 
                    else: 
                        new_instr = {
                            'op': 'id',
                            'type': instr['type'],
                            'dest': instr['dest'],
                            'args': [arg],
                        }
                        # each block has a terminator so must insert before that
                        new_cfg[label].insert(-1, new_instr)

    # remove all the phi instructions
    for block in new_cfg:
        new_block = []
        for instr in new_cfg[block]:
            if instr['op'] == "phi":
                pass
            else: 
                new_block.append(instr)
        new_cfg[block] = new_block
    return new_cfg
                

def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

if __name__ == "__main__":
    # in order to work properly must be run directly from Lesson6 dir

    program = json.load(sys.stdin)
    #print(program)

    for func in program['functions']:
        cfg = block_map(form_blocks(func['instrs']))
        add_terminators(cfg)
        new_cfg = from_ssa(cfg)
        func['instrs'] = reassemble(new_cfg)
    print_program(program)
    #print_program(program)

