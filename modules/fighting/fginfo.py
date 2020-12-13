import os, json
from .fgalias import FgAlias

class FgInfo():

    def searchFd(game, char, move: str):
        aliasChar = FgAlias.char(game, char, "String")
        alias = FgAlias.move(game, aliasChar, move, "Command")
        with open(os.getcwd()+"/modules/fighting/"+game+"/fd/"+aliasChar+".json", "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            if i["Command"].lower() == alias.lower():
                return i
            try:
                for x in i["Name"]:
                    nameLower = x.lower()
                    print(nameLower)
                    if nameLower.startswith(move.lower()):
                        return i
            except:
                pass

    def searchChar(game, char: str):
        alias = FgAlias.char(game, char, "String")
        with open(os.getcwd()+"/modules/fighting/"+game+"/characters.json", "r") as char_json:
            json_data = json.load(char_json)
        for i in json_data:
            #if name.lower().startswith(char):
            if alias == i["Character"]:
                return_char = i
                return return_char
