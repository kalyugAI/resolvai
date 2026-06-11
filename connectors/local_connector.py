import json


def load_local():

    with open(
        "data/incidents.json"
    ) as f:

        return json.load(f)
