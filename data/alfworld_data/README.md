# Bundled ALFWorld data

The 113 ALFWorld game files that ALFWorld-Para evaluates, plus the PDDL domain and grammar
needed to build them. Point `ALFWORLD_DATA` here and nothing else has to be downloaded.

```bash
export ALFWORLD_DATA=/path/to/ALFWorld-Para/data/alfworld_data
```

```
base_config.yaml                      ALFWorld's own config, verbatim
logic/alfred.pddl                     world dynamics
logic/alfred.twl2                     text feedback grammar
json_2.1.1/valid_seen/<113 games>/    game.tw-pddl, traj_data.json, initial_state.pddl
```

Every file under `logic/` and `json_2.1.1/` is byte-identical to what `alfworld-download`
produces; the game directories are complete, not trimmed. The 113 games are the subset of
`valid_seen` that ALFWorld-Para covers, one per task spec.

`logic/` and `traj_data.json` are not optional. `get_game_logic()` reads the two logic files,
and `AlfredTWEnv` walks the split looking for `traj_data.json` to read each game's task type.

## What is not here

The full `alfworld-download` is 2.5 GB. These parts are left out because nothing in a
text-only evaluation reads them:

| | Size | Used by |
|:--|--:|:--|
| `json_2.1.1/train`, `valid_train`, `valid_unseen` | 2.1 GB | training and the out-of-distribution split |
| `agents/pretrained_checkpoints` | 178 MB | the seq2seq agent |
| `detectors/mrcnn_*.pth` | 170 MB | the vision agent |
| `seq2seq_data` | 63 MB | seq2seq training |

`base_config.yaml` still names `json_2.1.1/train` and `valid_unseen`, because it is ALFWorld's
file unedited. Those paths are read only when the matching `train_eval` mode is requested, so
`eval_in_distribution` works as is. Run `alfworld-download` if you need the other splits.

## Attribution

These files come from [ALFWorld](https://github.com/alfworld/alfworld) (MIT, Copyright (c) 2020
Mohit Shridhar and others), which builds its games from
[ALFRED](https://github.com/askforalfred/alfred) (MIT). They are redistributed here unmodified
so the benchmark runs from a clone. Please cite ALFWorld and ALFRED alongside this work.
