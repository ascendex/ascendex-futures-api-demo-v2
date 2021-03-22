import json
import yaml


def load_config(fname, exchange): 
    with open(fname, "r") as config_file:
        if fname.endswith(".yaml"):
            return yaml.load(config_file, Loader=yaml.FullLoader)[exchange]
        else:
            return json.load(config_file)[exchange]


def parse_response(res):
    if res is None:
        return None 
    elif res.status_code == 200:
        obj = json.loads(res.text)
        return obj
    else:
        print(f"request failed, error code = {res.status_code}")
        print(res.text)
