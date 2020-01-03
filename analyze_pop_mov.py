import cv2
import json
# GNU LGPL
# (c) royalcrab@bbled.org 2020

# fixed values
offset_x = 40
offset_y = 160
width = 120
height = 480

rane_x = [0, 40, 72, 110, 140, 178, 208, 245, 275, 320]
rane_dat = [0,0,0,0,0,0,0,0,0]
mod_h = [6,6,0,0,0,0,0,6,6] # red base 

m = 2 # select song

csv_file = 'rects.csv'
json_file = 'rects.json'
fps = 60
mp4_fps = 59.95 # accuratelly ?? frame rate for mallet
# mp4_fps = 58.42 # accuratelly ?? frame rate for harmonia

if m == 0:
    # mune-kyun mallet
    start_frame = 44 * fps
    # end_frame = 80 * fps
    end_frame = 145 * fps
    reference_frame = 40 * fps
    src = 'POPN/190428-1214.mp4'
    hsp = 3.9
    bpm = 168.0
    mp4_fps = 59.95

elif m == 1:
    # harmonia
    start_frame = 21 * fps
    end_frame = 113 * fps
    reference_frame = 18 * fps
    src = 'POPN/Encode_2351.mp4'
    hsp = 3.7
    bpm = 177.0
    mp4_fps = 58.42

else:
    # sayonara heaven
    start_frame = 18 * fps
    end_frame = 138 * fps
    reference_frame = 17 * fps
    src = 'POPN/190428-1144.mp4'
    hsp = 5.8
    bpm = 111.0
    mp4_fps = 59.95

cap_file = cv2.VideoCapture( src )
cap_file.set(cv2.CAP_PROP_POS_FRAMES, reference_frame)

# json
json_top = []

f = open( csv_file, 'w')

ret, bgframe = cap_file.read()
bg = bgframe[offset_x:width,offset_y:height]

counter = 0
first_frame = -1 # first frame
first_offset = 0
max_measure = 1  # max_measure
# 4 row, 8 colum (max32)

# pixel/frame = hsp * bpm / 60
# 1frame / beat = 3600 / bpm
# x = (frame * bpm * hsp / 60 + pixel ) / (hsp * 60) * quantizer (1920)


notes = [] # all note data
pre_rane = [0,0,0,0,0,0,0,0,0] # flag for pre-note in each rane

for num in range( start_frame, end_frame ):
    cap_file.set(cv2.CAP_PROP_POS_FRAMES, num)
    ret, cur = cap_file.read()
    clipped = cur[offset_x:width,offset_y:height]

    d1 = cv2.absdiff( clipped, bg )
    gray = cv2.cvtColor(d1, cv2.COLOR_BGR2GRAY) 
    ret, img = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for i in range(0,9):
        rane_dat[i] = 0

    
    for i in range(0, len(contours)):
        if len(contours[i]) > 0:

            # remove small objects
            if cv2.contourArea(contours[i]) < 100:
                continue

            rect = contours[i]
            x, y, w, h = cv2.boundingRect(rect)
            cv2.rectangle(clipped, (x, y), (x + w, y + h), (255, 0, 255), 1)

            for k in range(0,9): 
                if ( y + h >= 80 or y + h < 30):
                    continue
                if ( x < rane_x[k+1] and rane_x[k] < x ): 

                    #if ( num - pre_rane[k] == 1 ):
                    #    pre_rane[k] = num # store the frame number of the note in rane k
                    #    continue
                    #else:
                    rane_dat[k] = y + h - mod_h[k]
                    note = {}
                    tmp = 0.0
                    tmp2 = 0

                    if (first_frame < 1 ): # first frame
                        first_frame = num
                        first_offset = y + h - mod_h[k]
                        
                        note['frame'] = 0
                        note['pixel'] = first_offset
                        note['color'] = k+1 # modify for popdrow 
                        note['timing'] = 0
                        note['measure'] = 1 # modify for popdrow 
                        
                    else:
                        note['frame'] = num - first_frame
                        note['pixel'] = (y + h - mod_h[k]) - first_offset
                        note['color'] = k+1 # modify for popdrow 

                        # quantization
                        tmp = 12.0 * (float(note['frame']) * bpm * hsp / mp4_fps + float(note['pixel'])) \
                            / (hsp * mp4_fps )
                        tmp2 = int(tmp+0.5)
                        if tmp2 % 6 == 1:
                            tmp2 -= 1
                        if tmp2 % 6 == 5:
                            tmp2 += 1

                        if not (num - pre_rane[k] == 1):
                            note['timing'] = tmp2 % 48
                            note['measure'] = int(tmp2 / 48) + 1 # modify for popdrow 

                    enc = json.dumps( note )
                    #print( enc )
                    #print( "rane: %d"%k, "val %d"%pre_rane[k])
                    print( "beat: %f"%tmp, "quantized: %d"%(tmp2 % 48), "measure: %d"%(tmp2/48), "rane %d"%k )
                    
                    notes.append(note)

                    pre_rane[k] = num

    # cv2.imwrite( 'out/img_%03d.png'%num, clipped )
    # cv2.imwrite( 'gray/img_%03d.png'%num, img )

    for i in range(0,9):
        
        f.write( "%02d"%rane_dat[i] )
        if ( i < 8 ):
            f.write(",")
        else:
            f.write("\n")

# generate json file for popdraw
m_str0 = '{"split": 0, "x": 0, "y": -125, "w": -125, "h": 0 }'

# constant values
mx = 21
my = 920
mw = 117
mh = 128

mmy = 128
mmx = 130

with open( json_file, "w") as fj:
    fj.write( "{\n\t\"version\": 3,\n\t\"bpm\": 168,\n\t\"hsp\": 3.9,\n\t\"notes\": [\n")
    for note in notes:
        enc = json.dumps( note )
        fj.write( "\t\t")
        fj.write( enc )
        fj.write( ",\n")
    
    fj.write("\t\t{}\n") # for ignoring last camma

    # generate measure
    fj.write( "\t],\n\t\"measures\": [\n")
    fj.write( "\t\t")
    fj.write( m_str0 )

    measures = []

    # generate soflans and startMeasureNum
    for i in range(0,8):
        for j in range(0,8):
            measure = {}
            measure["split"] = 16
            measure["x"] = mx + i * mmx
            measure["y"] = my - j * mmy
            measure["w"] = mw
            measure["h"] = mh

            fj.write( ",\n" )
            enc = json.dumps( measure )
            fj.write( "\t\t")
            fj.write( enc )
            
    fj.write( "\n" )
    fj.write( "\t],\n\t\"soflans\": [],\n\t\"startMeasureNum\": 1\n}\n" )

print( "finishd." )
