import json

class Framedata():
    def search(game, char, move):
        path = "./frame_data/"+game+"/"+char+".json"
        with open(path, "r") as frame_json:
            json_data = json.load(frame_json)
        for i in json_data:
            if i["Command"] == move:
                return_move = i
        return return_move
