import json


def load_json(json_file: str):
    with open(json_file) as f:
        data = json.load(f)

    return data


def export_to_json(data, json_file: str):
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
