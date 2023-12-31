## Summarize what you did 
Benny Rubin and Stephen Verderame worked together on this. 
We implemented a tracing JIT for bril. 

Our code and examples can be found [here](link). 

## Implementation details

For this task, we decided to trace at basic block boundaries. This is simply because we did not want to deal with inserting new labels and jumps for stitching the trace into the program. We also stopped tracing at prints and function calls, because prints induce a side effect and we did not want to inline functions for this assignment. We first run the program to completion in the interpreter and trace the entire output. Our JIT allow the user to specify how many basic blocks they want to trace and will create a trace up to that many basic blocks (stopping of course at prints and calls). Because we start tracing at the beginning of main, we always start the program at the trace. We created a new label that points to the beginning of main, and all conditionals turn to guards with that label so that if we abort we just run the program normally. Because of the way we formulated the trace to always stop at basic block boundaries, the last instruction of the trace will always be a jump to the correct basic block in the original program, allowing us to do no modifications to either the trace or the original programs in order to stitch them together. 

## Testing

For testing, we ran armstrong, collatz, perfect, and loopfact with and without tracing,
while performing the same optimizations (LVN, DCE, aggressive copy coalescing). 
We ensured that the results produced were the same for both.

We also tested each program with different arguments such that we tested runs
that can follow the trace and runs that must abort the trace before committing. There were some scenarios when a different argument (other than the one used to generate the trace) was also able to take advantage of certain traces. 

We summarized the results of the number of dynamic instructions in the following
table where we traced perfect with an argument of 496 and loopfact with an argument
of 3. We only show perfect and loopfact since collatz and armstrong had calls early on,
which caused us to stop tracing.

| Test Name | Args | Traced | Regular | Speedup |
| --------- | ---- | -------| --------| ------- |
| Perfect   | 496  | 237    | 230     | 0.971   |
| Perfect   | 500  | 238    | 231     | 0.971   |
| Perfect   | 128  | 124    | 117     | 0.944   |
| Loopfact  | 10   | 68     | 75      | 1.102   |
| Loopfact  | 3    | 26     | 26      | 1.000   |
| Loopfact  | 1    | 21     | 12      | 0.571   |

## what was challenging

When we started, we thought this task would be very difficult. It seemed like there were a lot of uncertainties for how to do things like stitching the trace back into the program, especially in the middle of a basic block or in the middle of a function. In the end, we formulated the tracing to follow basic blocks so that the stitching was extremely straightforward and easy to reason about. 

We ran into a number of challenges along the way:

* We allowed calls/prints in the trace originally, but calls are not allowed in speculate mode and print changes the state in a way that can't be rolled back. We tinkered with the idea of changing the interpreter to keep track of a list of printed values and print at a commit or throw it away at abort, but decided not to implement this. Instead of stopping the trace right at a call or print, we instead stop at the previous basic block boundary for the reasons stated above.

* Because we decided not to implement function inlining, so this introduced a new challenge of trying to find a good benchmark that had lots we could trace without any function calls or print statements. We eventually settled on perfect (which was perfect for our usecase) and loopfact. 

* One final thing we briefly overlooked, wondering why our tracing wasn't working at all, was that we had to look at which branch was taken for each conditional and insert a negation to the guard condition if the false branch was taken. 