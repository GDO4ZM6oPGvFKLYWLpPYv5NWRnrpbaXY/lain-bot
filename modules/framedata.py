import json
import os

class Framedata():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    def search(game, char, move):
        with open("./framedata/"+game+"/"+char+".json", "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            if i["Command"] == move:
                return_move = i
        return return_move
