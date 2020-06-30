import os
import json
from .fgalias import FgAlias

class FgInfo():

    def searchFd(game, char, move: str):
        alias = FgAlias.move(move, "Command")
        aliasChar = FgAlias.char(game, char, "String")
        with open(os.getcwd()+"/modules/fighting/"+game+"/fd/"+aliasChar+".json", "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            if i["Command"].lower() == alias.lower():
                return i
                
    def searchChar(game, char: str):
        alias = FgAlias.char(game, char, "String")
        with open(os.getcwd()+"/modules/fighting/"+game+"/characters.json", "r") as char_json:
            json_data = json.load(char_json)
        for i in json_data:
            #if name.lower().startswith(char):
            if alias == i["Character"]:
                return_char = i
                return return_char
