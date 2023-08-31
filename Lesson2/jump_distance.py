# Calculates the total jumping distance of the program. This is how many instructions are jumped over. Assuming jmps don't cross function boudnaries.
# Backwards jumps still count as instructions jumped over and labels count as jumps as well.

# test it with my own custom programs with jumps
import json
import sys

file = sys.argv[1]
f = open(file)

program = json.load(f)


def is_jmp(instr):
    return instr.get('op') == 'jmp'


def find_label(instructions, label):
    for instr in instructions:
        if (instr.get('label') == label):
            return instr


instr_jumped = 0
for func in program["functions"]:
    instructions = func["instrs"]
    for i, instr in enumerate(instructions):
        if is_jmp(instr):
            jmp_label = instr['labels'][0]
            label_instr = find_label(instructions, jmp_label)
            label_idx = instructions.index(label_instr)
            instr_jumped += abs(i - label_idx) - 1

print(f"You have *statically* jumped {instr_jumped} instructions")
