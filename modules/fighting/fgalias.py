import os
import json

class FgAlias():

    def move(move: str, part: str):
        with open(os.getcwd()+"/modules/fighting/movealiases.json", "r") as alias_json:
            json_data = json.load(alias_json)
        for i in json_data:
            for alias in i["Alias"]:
                if alias.lower() == move.lower():
                    return_move = i[part]
                    return return_move

    def char(game, char: str, part: str):
        with open(os.getcwd()+"/modules/fighting/"+game+"/charalias.json", "r") as alias_json:
            json_data = json.load(alias_json)
        for i in json_data:
            for alias in i["Alias"]:
                aliaslower = alias.lower()
                if aliaslower.startswith(char.lower()):
                    return_char = i[part] #"Name" or "String"
                    return return_char
