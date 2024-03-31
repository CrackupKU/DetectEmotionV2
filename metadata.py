import pandas as pd
import json


metadata = pd.DataFrame(columns=['character', 'frame', "anger","contempt","disgust","fear","happy","neutral","sad","surprise"])


def finding(em,emotions):
    if emotions.find(em) != -1:
        return emotions.split("%")[0].split("(")[1]
    return 0


def write(id,f, emotions):
    _metadata = {
        "character": id, 'frame': f,
                                "anger": finding("anger", emotions),
                                "contempt": finding("contempt", emotions),
                                "disgust": finding("disgust", emotions),
                                "fear": finding("fear", emotions),
                                "happy": finding("happy", emotions),
                                "neutral": finding("neutral", emotions),
                                "sad": finding("sad", emotions),
                                "surprise": finding("surprise", emotions),
    }
    global metadata
    metadata = metadata.append(_metadata,ignore_index=True)

def write2(id,f, predict):
    _metadata = {
        "character": id, 'frame': f,
                                "anger": predict[0],
                                "contempt": predict[1],
                                "disgust": predict[2],
                                "fear": predict[3],
                                "happy": predict[4],
                                "neutral": predict[5],
                                "sad": predict[6],
                                "surprise": predict[7],
    }
    global metadata
    metadata = metadata.append(_metadata,ignore_index=True)

def end(map,total_frame,file_path):
    global metadata
    # for i in range(total_frame):
    #     for k in map.values():
    #         id = int(k.split("_")[1])
    #         if id not in metadata.loc[metadata['frame'] == i+1]["character"]:
    #             _metadata = {
    #                                 "character": id,
    #                                 'frame': i+1,
    #                                 "anger": 0,
    #                                 "contempt": 0,
    #                                 "disgust": 0,
    #                                 "fear": 0,
    #                                 "happy": 0,
    #                                 "neutral": 0,
    #                                 "sad": 0,
    #                                 "surprise": 0,
    #                                 }
    #             metadata = metadata.append(_metadata,ignore_index=True)

    result = metadata.to_json(file_path, orient="records")

def write_emotion(file_path):
    global metadata
    max_sum_column = metadata[['anger','disgust','fear','happy','sad','surprise']].sum().idxmax()
    json_object = json.dumps({"emotion": max_sum_column}, indent=4)
    with open(file_path, "w") as outfile:
        outfile.write(json_object)

def write_json(dict, file_path):
    # Serializing json
    json_object = json.dumps(dict, indent=4)
    
    # Writing to sample.json
    with open(file_path, "w") as outfile:
        outfile.write(json_object)