import yaml
from yaml.loader import SafeLoader
import os

working_directory = os.getcwd() + "/novels"


def read_novel_info(directory):
    try:
        with open(directory + "/info.yaml", 'r') as file:
            data = yaml.load(file, Loader=SafeLoader)
    except:
        print("Problem Getting file")
    return data


def write_novel_info(directory, information):
    with open(directory + "/info.yaml", 'w+') as file:
        data = yaml.dump(information, file, sort_keys=False, default_flow_style=False)
    return data


def structure_novel_data(title, alternative_title, last_url, author):
    return {"title": title, "alt_title": alternative_title, "last_url": last_url, "author": author}


def save_info(title, alternative_title, last_url, author):
    path = working_directory + f'/{alternative_title}'
    if not os.path.exists(path):
        os.makedirs(path)
    novel_data = structure_novel_data(title, alternative_title, last_url, author)
    write_novel_info(path, novel_data)
