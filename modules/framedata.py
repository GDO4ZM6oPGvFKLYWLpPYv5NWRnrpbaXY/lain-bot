import json
import os

class Framedata():

    print(os.getcwd())

    def search(game, char, move):
        with open(os.getcwd()+"/framedata/"+game+"/"+char+".json", "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            if i["Command"] == move:
                return_move = i
        return return_move
