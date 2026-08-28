

**Adaptive-Depth Minimax for 3D Connect Four with Depth-Aware Experience Reuse and SMC-Inspired Time Control**

The code was developed incrementally during the project. Different experimental
agent configurations were retained as separate Python files rather than being
refactored into a single software framework, so that the implementations used
during experimentation could be preserved directly.

## Recommended Reading Order

The easiest way to inspect the implementation is:

1. `bit_coding.py`
   - Core Improved minimax agent.
   - Contains the main 64-bit bitboard representation, symmetry reduction,
     improved heuristic evaluation, alpha-beta search and move ordering.
   - This is the recommended starting point for understanding the shared search
     framework.

2. `bit_coding_test_SMCOnly.py`
   - SMC-inspired adaptive-depth extension.
   - The shared minimax implementation is largely repeated from the core agent.
   - For the SMC-specific implementation, go directly to:
     - `choose_best_move_dict()` — iterative deepening and the within-decision
       continuation rule.
     - `smc_update_time_limit()` — between-decision SMC-inspired time-budget
       update.

3. `bit_coding_test_reinOnly.py`
   - Depth-aware experience-reuse agent.
   - For the experience-specific implementation, go directly to
     `minimax_new_alphabeta()`, where the stored search value, remaining search
     depth and visit count are used for reuse, smoothing and replacement.

4. `bit_coding_test.py`
   - Combined SMC + depth-aware experience-reuse configuration.

5. `battle.py`
   - Main head-to-head experimental runner.
   - Imports the different agent implementations and is used to configure
     pairwise experimental comparisons.


## Interactive Demonstrations

The repository also includes browser-based interactive demonstrations of the
3D Connect Four agents:

- `connect4_minimax_newtest.html` — interactive demonstration of the minimax agent.
- `connect4_minimax_smc.html` — interactive demonstration of the SMC-inspired
  adaptive-depth agent.

These demonstrations were developed to provide an accessible way to interact
with the implemented agents and were also used during project presentation/demo
activities.

They are supplementary to the experimental Python implementations used to
generate the dissertation results.


## Agent Implementations

| Function in `battle.py` | Implementation | Purpose |
| --- | --- | --- |
| `minimax_choose_basic_score_function()` | `bit_coding_battle.py` | Basic fixed-depth minimax baseline |
| `minimax_choose_Improve_score_function()` | `bit_coding.py` | Main Improved fixed-depth minimax agent |
| `min_new()` | `bit_coding_new.py` | Functionally equivalent copy of the Improved agent, retained for internal parameter tuning and debugging |
| `minimax_pure_smc_odd()` | `bit_coding_test_SMCOnly.py` | SMC-only adaptive-depth agent beginning at depth 3 |
| `minimax_pure_smc_even()` | `bit_coding_test_SMCOnly_even.py` | SMC-only adaptive-depth agent beginning at depth 4 |
| `minimax_pure_rein()` | `bit_coding_test_reinOnly.py` | Depth-aware experience-reuse agent |
| `minimax_choose_rein_smc()` | `bit_coding_test.py` | Combined experience-reuse + SMC agent |
| `minimax_fix_time()` | `bit_coding_basic_time_control.py` | Earlier experimental time-control implementation; retained for development history but not used in the final dissertation experiments |

### Improved and `min_new`

`minimax_choose_Improve_score_function()` and `min_new()` implement the same
agent behaviour. The second copy was created during development to allow
internal parameter changes and debugging without modifying the main Improved
agent used as the experimental reference implementation.

It should therefore not be interpreted as an additional agent configuration.

### Odd- and Even-Depth SMC Variants

Two SMC-only implementations are retained:

- `minimax_pure_smc_odd()` begins iterative deepening at depth 3 and subsequently
  searches odd depths.
- `minimax_pure_smc_even()` begins at depth 4 and subsequently searches even
  depths.

They are stored as separate modules because the corresponding experimental
versions also used different internal SMC parameter settings. They should
therefore be regarded as two experimental SMC configurations rather than simply
the same controller with a different initial depth.

### Earlier Fixed-Time Variant

`minimax_fix_time()` is an earlier time-control experiment developed during the
project. Its behaviour was not sufficiently useful for the final investigation,
and it was not used for the dissertation results. The implementation is retained
only as part of the development history.

## Head-to-Head Experiments

`battle.py` acts as the main experimental runner. Agent configurations are
selected by enabling the corresponding function call for each player.

The first-player assignment is alternated between games to reduce systematic
first/second-mover effects. Experimental outputs include game outcome,
game length, achieved search depth, computation time and, where required,
explored-node count.

Intermediate experimental data are periodically stored as pickle files.

## Notes on Research Code

This repository contains research software developed incrementally for
experimental evaluation rather than a general-purpose software package.

Several agent files therefore contain duplicated underlying minimax code.
This was intentional during development: separate experimental implementations
made it possible to modify and test individual mechanisms without changing the
reference agent used in other experiments.

Some files also contain exploratory implementations or commented development
code that was not used in the final dissertation experiments. These sections
are retained where useful for traceability and are identified in the source
comments.
