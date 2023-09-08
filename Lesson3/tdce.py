from form_blocks import form_blocks
import json
import sys

def should_keep_instr(used, instr):
    # do not remove effect instructions
    side_effect_ops = ["jmp","br","call","ret"]
    op = instr.get('op')
    if not op or op in side_effect_ops: 
        return True
    dest = instr.get('dest')
    return (not dest) or (dest in used)


def eliminate_dead_code(blocks): 
    used_vars = set()
    # Add arguments of instructions to the used set of variables
    for block in blocks:
        for instr in block: 
            args = instr.get('args')
            if args:
                used_vars.update(args)
    for block in blocks:
        while True:
            before_length = len(block)
        # filter through instructions and remove ones whose destination is never used 
            block[:] = list(filter(lambda instr: should_keep_instr(used_vars, instr), block))
            if before_length == len(block):
                break
            

def eliminate_dead_code_program(prog):
    functions = prog['functions']
    for func in functions:
        blocks = list(form_blocks(func['instrs']))    
        eliminate_dead_code(blocks)
        func['instrs'] = [instr for block in blocks for instr in block]

def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

if __name__ == "__main__":
    #command: bril2json < {file}| python3 tdce.py | bril2txt
    program = json.load(sys.stdin)
    eliminate_dead_code_program(program)
    print_program(program)