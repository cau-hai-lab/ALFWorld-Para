"""Run one ALFWorld-Para episode on stock ALFWorld.

No agent, no harness: it opens the episode a record names, swaps the goal
instruction for the paraphrase, and prints what an agent would see. Use it to
check the setup and to see exactly where the paraphrase enters.

    pip install alfworld==0.3.3
    python data/example_run.py                      # a random Same-Polarity record
    python data/example_run.py --id ap_0000
    python data/example_run.py --cell obj_lexical_same_polarity --steps 3

ALFWORLD_DATA defaults to the bundled data/alfworld_data, so nothing needs to be
downloaded.
"""

import argparse
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
os.environ.setdefault("ALFWORLD_DATA", os.path.join(HERE, "alfworld_data"))
CONFIG = os.path.join(os.environ["ALFWORLD_DATA"], "base_config.yaml")


def build_env(config):
    """One env holding one game file, the way the eval harnesses use it."""
    from alfworld.agents.environment.alfred_tw_env import AlfredTWEnv

    class SingleAlfredTWEnv(AlfredTWEnv):
        def __init__(self, config):
            self.config = config
            self.train_eval = "eval_in_distribution"
            self.goal_desc_human_anns_prob = config["env"]["goal_desc_human_anns_prob"]
            self.get_game_logic()
            self.random_seed = 42
            self.game_files = []
            self.num_games = 0

    return SingleAlfredTWEnv(config).init_env(batch_size=1)


def split_observation(text):
    """ALFWorld's reset text is the room description then 'Your task is to: ...'."""
    marker = "Your task is to:"
    if marker not in text:
        return text.strip(), ""
    room, goal = text.split(marker, 1)
    return room.strip(), goal.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", help="record id, e.g. ap_0000")
    ap.add_argument("--cell", default="obj_lexical_same_polarity",
                    help="sample from this cell when --id is not given")
    ap.add_argument("--steps", type=int, default=1, help="how many actions to take")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    records = json.load(open(os.path.join(HERE, "alfworld_para.json")))
    if args.id:
        pool = [r for r in records if r["id"] == args.id]
    else:
        pool = [r for r in records if r["cell"] == args.cell]
    if not pool:
        sys.exit(f"no record matches {args.id or args.cell}")
    record = random.Random(args.seed).choice(pool)

    try:
        import yaml
    except ImportError:
        sys.exit("pip install pyyaml")
    try:
        env = build_env(yaml.safe_load(open(CONFIG)))
    except ImportError:
        sys.exit("pip install alfworld==0.3.3")

    game = os.path.join(os.environ["ALFWORLD_DATA"], "json_2.1.1", "valid_seen",
                        record["gamefile"], "game.tw-pddl")
    if not os.path.isfile(game):
        sys.exit(f"game file missing: {game}")

    env.gamefiles = [game]
    env.seed(args.seed)
    observation, info = env.reset()
    room, goal = split_observation(observation[0])

    match = "t0" if goal.rstrip(".") == record["original"].rstrip(".") else "other template"
    print(f"record      {record['id']}  [{record['cell']}]  {record['template_id']}")
    print(f"game        {record['gamefile']}")
    print(f"env goal    {goal}   <- ALFWorld's own wording ({match})")
    print(f"original    {record['original']}   <- the None condition")
    print(f"paraphrase  {record['paraphrase']}   <- what is evaluated\n")

    # ALFWorld emits only one of its two goal templates per game, and the benchmark
    # covers both, so the instruction is always overridden -- in the None condition
    # too. The success condition is ALFWorld's own and is untouched.
    print(room)
    print(f"Your task is to: {record['paraphrase']}\n")

    for step in range(args.steps):
        actions = info["admissible_commands"][0]
        action = next((a for a in actions if a.startswith("go to")), actions[0])
        observation, score, done, info = env.step([action])
        print(f"[{step + 1}] {len(actions)} admissible, took {action!r}")
        print(f"    {observation[0].strip()}")
        if done[0]:
            print(f"    done, success={bool(score[0])}")
            break


if __name__ == "__main__":
    main()
