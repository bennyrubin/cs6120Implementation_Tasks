# util files form_blocks, cfg, and briltxt pulled from cs6120 bril repo
import json
from utils.form_blocks import form_blocks
from utils.cfg import block_map, add_terminators, add_entry, edges, reassemble
from utils.briltxt import print_prog, print_label, print_instr
import json
import sys
import copy


def print_program(prog):
    json.dump(prog, sys.stdout, indent=2, sort_keys=True) # pulled from briltxt.py

def print_block(block):
    for instr_or_label in block:
        if 'label' in instr_or_label:
            print_label(instr_or_label)
        else:
            print_instr(instr_or_label)

def compute_dominators(cfg):
    preds, succs = edges(cfg)
    blocks = list(cfg.keys())
    doms = {name: list(cfg.keys()) for name in cfg.keys()} # should map all blocks to all other blocks
    entry = next(iter(cfg.keys()))
    doms[entry] = set([entry])
    old_doms = {}
    while old_doms != doms:
        old_doms = copy.deepcopy(doms)
        for block in blocks:
            if block == entry:
                continue
            dominators = [doms[p] for p in preds[block]]
            doms[block] = set.intersection(*dominators) | set([block])
    return doms

def dominator_tree(cfg):
    # child of block are blocks that are immediately dominated (dominated and child in CFG)
    # can use an adjacency list
    # need to find out the immediate dominator of every node. Look at list of dominators and every other dominator should dominate the idom
    doms = compute_dominators(cfg)
    entry = next(iter(cfg.keys()))
    idom_edges = {name: [] for name in doms}
    for node in doms:
        if node == entry:
            continue
        idom_candidates = doms[node] 
        idom_candidates.remove(node) # remove self from list
        # if one of the dominators dominates another dominator, then it's not the idom 
        # idom must also be dominated by all other dominators
        for cand in idom_candidates:
            cand_doms = doms[cand] # must contain all idom_candidates 
            if set(cand_doms) <= set(idom_candidates): # candidate is dominated by all other candidates
                #print(f"candidate: {cand} dominates node: {node}")
                idom_edges[cand].append(node)
                break
        else: # if it doesn't break then throw an error because that shouldn't be possible to not have an idom
            raise Exception(f"not possible for block {node} to not have an idom")
        
    return idom_edges

def dominance_frontier(cfg):
    # go through children of all the nodes A dominates, and if A does not dominate a node, then that is in A's frontier
    # another way to think about it:
        # if some (but not all) of a node's preds are dominated by A, then it is in A's frontier 
    preds, succs = edges(cfg)
    doms = compute_dominators(cfg)
    frontier = {name: [] for name in doms}
    for node in doms:
        # the union of all the doms of the predesessors minus the intersection of all the doms of the predesessors makes up 
        # the list of nodes who have `node` in their frontier 
        pred_doms = [doms[pred] for pred in preds[node]]
        if len(pred_doms) == 0:
            continue
        intersection = set.intersection(*map(set,pred_doms))
        union = set.union(*map(set,pred_doms))
        frontier_set = union - intersection
        for block in frontier_set:
            frontier[block].append(node)
    return frontier
    


def enumPathsHelper(succs, curr, dest, visited, path, paths):

    # Mark the current node as visited and store in path
    visited[curr] = True
    path.append(curr)

    # If current vertex is same as destination, then print
    # current path[]
    if curr == dest:
        paths.append(copy.deepcopy(path))
    else:
        # If current vertex is not destination
        # Recur for all the vertices adjacent to this vertex
        #print(curr, succs[curr])
        for node in succs[curr]:
            #print(visited)
            if visited[node] == False:
                enumPathsHelper(succs, node, dest, visited, path, paths)
                    
    # Remove current vertex from path[] and mark it as unvisited
    path.pop()
    visited[curr]= False


def enumPaths(cfg, dest):

    # Mark all the vertices as not visited
    visited = {name: False for name in cfg}

    # Create an array to store paths
    path = []
    paths = []
    entry = next(iter(cfg.keys()))

    preds, succs = edges(cfg)

    # Call the recursive helper function to print all paths
    enumPathsHelper(succs, entry, dest, visited, path, paths)

    return paths

def test_dominance(cfg):
    doms = compute_dominators(cfg)
    entry = next(iter(cfg.keys()))
    for node in cfg:
        dominators = doms[node]
        paths = enumPaths(cfg, node) # paths from entry to node
        for path in paths:
            for dominator in dominators:
                assert (dominator in path)
    print("All dominators in all paths for every node")
    # for each dominator A of node B, check all paths from entry to B and make sure A is in the path
    # can do a DFS, but just don't end when I reach the node. Keep going until all paths are exhausted. At each point keep track of if A is visited. 


if __name__ == "__main__":
    # in order to work properly must be run directly from Lesson4 dir

    program = json.load(sys.stdin)
    for func in program['functions']:
        cfg = block_map(form_blocks(func['instrs']))
        add_terminators(cfg)
        doms = compute_dominators(cfg)
        dom_tree = dominator_tree(cfg)
        #print(dom_tree)
        frontier = dominance_frontier(cfg)
        #print(f"frontier: {frontier}")
        #doms = compute_dominators(cfg)
        #print(doms)
        test_dominance(cfg)

        # TOOD: test with example from Adrian's video 

