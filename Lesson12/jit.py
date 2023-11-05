# util files form_blocks, cfg, and briltxt pulled from cs6120 bril repo
import json
from utils.form_blocks import form_blocks
from utils.cfg import block_map, add_terminators, add_entry, edges, reassemble
from utils.briltxt import print_prog, print_label, print_instr
from utils.correct_dom import get_dom, dom_tree, dom_fronts
import json
import sys
import copy


def collapse_calls(ls: list) -> list[dict]:
    st = []
    active_calls = 0
    for instr in ls:
        if active_calls == 0:
            st.append(copy.deepcopy(instr))
        if instr["op"] == "call":
            active_calls += 1
        elif instr["op"] == "ret":
            active_calls -= 1

    return st


def extract_trace(ls: list[dict], num_jmps) -> list[dict]:
    last_branch_jmp = 0
    for idx, e in enumerate(ls):
        if e['op'] == 'jmp' or e['op'] == 'br':
            num_jmps -= 1
            last_branch_jmp = idx
        if e['op'] == "call" or e['op'] == 'print':
            return ls[:idx + 1]
        if num_jmps == 0:
            # include the final jump or branch
            return ls[:idx + 1]
    assert last_branch_jmp > 0
    return ls[:last_branch_jmp + 1]


def remove_jumps(ls: list[dict]):
    for idx, instr in enumerate(ls):
        if instr["op"] == "jmp" and (idx != len(ls) - 1):
            del ls[idx]


def replace_all_branches_guards(ls: list[dict]):
    # example guard instr: {"args":["v3"],"labels":["then.0"],"op":"guard"}
    for idx, instr in enumerate(ls):
        if instr["op"] == "br" and (idx != len(ls) - 1):
            ls[idx] = {"args": instr['args'], "labels": [
                "new_label_main"], "op": "guard"}


def add_speculate_commit(ls: list[dict]):
    ls.insert(0, {"op": "speculate"})
    ls.insert(len(ls) - 1, {"op": "commit"})
    assert (ls[-1]["op"] == "jmp" or ls[-1]["op"] == "br"
            or ls[-1]["op"] == "call" or ls[-1]["op"] == "print")
    return ls


def stitch_trace_program(trace: list[dict], basic_blocks):
    remove_jumps(trace_block)
    replace_all_branches_guards(trace_block)
    add_speculate_commit(trace_block)
    basic_blocks.update({'start_trace': trace_block})
    basic_blocks.move_to_end('start_trace', last=False)


def print_program(prog):
    # pulled from briltxt.py
    json.dump(prog, sys.stdout, indent=2, sort_keys=True)


if __name__ == "__main__":
    # in order to work properly must be run directly from Lesson6 dir
    NUM_JUMPS = 100
    program = json.load(sys.stdin)
    trace_file = sys.argv[1]
    with open(trace_file) as file:
        instrs = file.readlines()
    trace_instr = [json.loads(instr) for instr in instrs]
    trace = collapse_calls(trace_instr)
    trace_block = extract_trace(trace, NUM_JUMPS)

    # print(program)

    for func in program['functions']:
        # print(program['functions'])
        if func['name'] != "main":  # only trace for main
            break
        func['instrs'].insert(0, {"label": "new_label_main"})
        basic_blocks = block_map(form_blocks(func['instrs']))
        add_terminators(basic_blocks)
        stitch_trace_program(trace_block, basic_blocks)
        func['instrs'] = reassemble(basic_blocks)
        # print(basic_blocks.keys())

    print_program(program)
    # print_program(program)
