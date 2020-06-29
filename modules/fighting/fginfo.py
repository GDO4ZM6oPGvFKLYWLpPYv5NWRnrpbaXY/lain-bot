import os
import json


class FgInfo():
    def searchFd(game, char, move: str):
        with open(os.getcwd()+"/modules/fighting/"+game+"/fd/"+char+".json", "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            #if i["Command"] == move:
                #return_move = i
            for comm in i["Command"]:
                if comm.lower() == move.lower():
                    return_move = i
                    return return_move


    def searchChar(game, char: str):
        with open(os.getcwd()+"/modules/fighting/"+game+"/characters.json", "r") as char_json:
            json_data = json.load(char_json)
        for i in json_data:
            #if name.lower().startswith(char):
            name = i["Character"]
            if name.lower() == char.lower():
                return_char = i
                return return_char
