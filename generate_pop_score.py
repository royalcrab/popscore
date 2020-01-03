import json

json_file = "rects.json"
new_notes = []
# mp4_fps = 58.42 # harmonia
# mp4_fps = 59.95 # mallet
mp4_fps = 73.7565 # heaven
# mp4_fps = 73.7565 # heaven
offset = 3.0 # sayonara heaven

# later -> down
# faster => up

with open( json_file, "r") as fr:
    dat = json.load(fr)
    bpm = dat["bpm"]
    hsp = dat["hsp"]
    notes = dat["notes"]

    for note in notes:
        if note.get("timing") == None: continue
        frame = float(note["frame"])
        pixel = float(note["pixel"])

        n = {}

        n['color'] = note["color"] # modify for popdrow 

        # quantization
        tmp = 12.0 * ( offset + (frame * bpm * hsp / mp4_fps - pixel) \
            / (hsp * mp4_fps ))
        # tmp = 12.0 * (frame * bpm ) - 12.0 * (pixel / (hsp * mp4_fps))
        tmp2 = int(tmp+0.5)

        #if tmp2 % 6 == 1:
        #    tmp2 -= 1
        #if tmp2 % 6 == 5:
        #    tmp2 += 1

        n['timing'] = tmp2 % 48
        n['measure'] = int(tmp2 / 48) + 1 # modify for popdrow 
        
        new_notes.append( n )

data = {
    "version": 3,
    "notes": new_notes,
    "measures": dat["measures"],
    "soflans": dat["soflans"],
    "startMeasureNum": dat["startMeasureNum"]
}

enc = json.dumps(data)
print( enc )
