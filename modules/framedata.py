import json
import os

class Framedata():
    def search(game, char, move: str):
        with open(os.getcwd()+"/framedata/"+game+"/"+char+".json", "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            #if i["Command"] == move:
                #return_move = i
            for comm in i["Command"]:
                if comm.lower() == move.lower():
                    return_move = i
                    return return_move
