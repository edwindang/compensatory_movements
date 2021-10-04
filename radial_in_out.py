# -*- coding: utf-8 -*-
"""
Created on Wed Jul 14 23:36:26 2021

@author: edwin
"""

import pandas as pd
from collections import defaultdict
from collections import OrderedDict
import statistics
import numpy as np
import matplotlib.pyplot as plt

#annotations = pd.read_csv("750_all_labels.csv", index_col = "Marker Name")
#hehe = pd.read_csv("605_gyro.csv")
labels = ["90OR", "90IR", "135OR", "135IR", "180OR", "180IR", "225OR", "225IR",
              "270OR", "270IR", "315OR", "315IR", "0OR", "0IR", "45OR", "45IR", 
              "90OL", "90IL", "135OL", "135IL", "180OL", "180IL", "225OL", "225IL",
              "270OL", "270IL", "315OL", "315IL", "0OL", "0IL", "45OL", "45IL"]

def main():
    stroke_numbers = ["554"]
    sample_size = [stroke_numbers]
    for sample in sample_size:
        for number in sample:
            print("number: ", number)
            chest_gyro = pd.read_csv(number + "_gyro.csv")
            reference = pd.read_csv(number + "_annotations.csv")
            annotations = pd.read_csv(number + "_all_labels.csv", index_col = "Marker Name")
            
            # chest gyro data
            x_axis = chest_gyro["Gyro Z (°/s)"]
            timecodes = chest_gyro["Timestamp (microseconds)"]
            
            for index, row in reference.iterrows():
                if row["EventType"] == "RECORDING":
                    reference_point = row["Start Timestamp (ms)"]*1000
            
            degree = degrees_traveled(annotations, reference_point, x_axis, timecodes, number)


def pre_process(annotations):
    thirty_fps = True
    new = pd.DataFrame()
    for keys, values in annotations.iterrows():
        if keys in labels:
            number = int(values["Out"][9:])
            if number > 30:
                thirty_fps = False
            new = new.append(values)
    print("thirty:", thirty_fps)
    return(new, thirty_fps)

# counter_dict = defaultdict(int)
def finder(point, timecodes):
    counter_dict = defaultdict(int)
    j = 0
    for timecode in timecodes:
        counter_dict[j] = abs(timecode - point)
        j += 1
    key_min = min(counter_dict.keys(), key = lambda k: counter_dict[k])
    return key_min, timecodes[key_min]


means_l = []
means_r = []
gyro_r = defaultdict(float)
gyro_l = OrderedDict()

def transform(dictionary, breathe_rate):
    for key in dictionary.keys():
        mean_gyro = 0
        mean_frames = 0
        for value in dictionary[key]:
            gyro = value[0]
            frame = value[1]
            mean_gyro+=gyro
            mean_frames+=frame
        dictionary[key] = [mean_gyro/len(dictionary[key]), (mean_frames/len(dictionary[key]))*breathe_rate]


def order(dictionary):
    dictionary = OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))
    
def degrees_traveled(annotations, reference_point, x_axis, timecodes, ID):
    times_dict_r = defaultdict(list)
    times_dict_l = defaultdict(list)
    gyro_dict_r_o = defaultdict(list)
    gyro_dict_l_o = defaultdict(list)
    gyro_dict_r_i = defaultdict(list)
    gyro_dict_l_i = defaultdict(list)
    breath_dict = defaultdict(list)
    
    df, thirty = pre_process(annotations)
    
    for index, row in df.iterrows():
        side = index[-1]
        in_time = row["In"]
        numbers = in_time.split(";")
        number = [int(i) for i in numbers]
        if thirty:
            in_frame = (number[0]*60*60*30) + (number[1]*60*30) + (number[2]*30) + (number[3])
        else:
            in_frame = (number[0]*60*60*60) + (number[1]*60*60) + (number[2]*60) + (number[3])
            
        out_time = row["Out"]
        digits = out_time.split(";")
        digit = [int(i) for i in digits]
        if thirty:
            out_frame = (digit[0]*60*60*30) + (digit[1]*60*30) + (digit[2]*30) + (digit[3])
        else:
            out_frame = (digit[0]*60*60*60) + (digit[1]*60*60) + (digit[2]*60) + (digit[3])
        
        coordinate = (in_frame, out_frame)
        if side == "R":
            times_dict_r[index].append(coordinate)
        elif side == "L":
            times_dict_l[index].append(coordinate)
    
    # finding baseline breathing noise
    
    coord = []
    breath = annotations.loc["breath"]
    breathe_in = breath["In"]
    breathe_out = breath["Out"]
    q = [breathe_in, breathe_out]
    i = True
    for p in q:
        nummy = p.split(";")
        nummi = [int(i) for i in nummy]
        if thirty:
            frame = (nummi[0]*60*60*30) + (nummi[1]*60*30) + (nummi[2]*30) + (nummi[3])
            coord.append(frame)
            if i:
                in_f = frame
            else:
                out_f = frame
        else:
            frame = (nummi[0]*60*60*60) + (nummi[1]*60*60) + (nummi[2]*60) + (nummi[3])
            coord.append(frame)
            if i:
                in_f = frame
            else:
                out_f = frame
        i = False
    frames = out_f - in_f
    breath_dict[str(frames)].append(coord)
    
    """
    REMEMBER TO CHANGE TAPC OR CUPRCRR
    """
    
    tap = annotations.loc["TapC"]
    #tap = annotations.loc["CupRRCR"]
    if tap.shape[0] == 5:
        pass
    else:
        tap = annotations.loc["TapC"].iloc[0]
        #tap = annotations.loc["CupRRCR"].iloc[0]
    tap_frame = str(tap["In"])
    sub_1 = tap_frame.split(";")
    start = [int(i) for i in sub_1]
    if thirty:
        index_frame = (start[0]*60*60*30) + (start[1]*60*30) + (start[2]*30) + (start[3])
    else:
        index_frame = (start[0]*60*60*60) + (start[1]*60*60) + (start[2]*60) + (start[3])
    times = [times_dict_r, times_dict_l, breath_dict]
    
    right = True
    breathe = False
    gyro_data = []
    reference_index, reference_timecode = finder(reference_point, timecodes)
    for times_dict in times:
        if len(times_dict) == 1:
            breathe = True
            print(times_dict)
            print("breath reached")
        for keys, values in times_dict.items():
            key = keys[:-2]
            #print(key)
            direction = keys[-2]
            for value in values:
                start_frame = value[0]
                finish_frame = value[1]
                if finish_frame - start_frame > 200:
                    break
                frames_passed_start = start_frame - index_frame
                frames_passed_end = finish_frame - index_frame
                
                if thirty:
                    start_ms_passed = (frames_passed_start/30) * 1000000
                    end_ms_passed = (frames_passed_end/30) * 1000000
                else:
                    start_ms_passed = (frames_passed_start/60) * 1000000
                    end_ms_passed = (frames_passed_end/60) * 1000000
            
                final_timecode_start = reference_timecode + start_ms_passed
                final_timecode_end = reference_timecode + end_ms_passed
            
                final_index_start, final_start_timecode = finder(final_timecode_start, timecodes)
                final_index_end, final_end_timecode = finder(final_timecode_end, timecodes)
                frames_traversed = final_index_end - final_index_start
                gyro = abs(x_axis[final_index_start])
                #if breathe:
                    #print(final_index_start, final_start_timecode)
                    #print(final_index_end, final_end_timecode)
                for x in range(final_index_end - final_index_start):
                    gyro_new = abs(x_axis[final_index_start + x + 1])
                    gyro += gyro_new
                
                # I think there's an issue with dividing gyro*0.016/frames_passed.
                # gyro is sampled much faster rate than frames
                # difference between frames is 25101 and 24942 = 159 excel rows
                # instead of dividing by frames passed, divide by excel rows?
                
                if breathe:
                    if thirty:
                        breathe_rate = ((gyro/frames_traversed)*0.016)/30
                        print(breathe_rate)
                        break
                    else:
                        breathe_rate = ((gyro/frames_traversed)*0.016)/60
                        print(breathe_rate)
                        break
                if right:
                    if direction == "O":
                        gyro_dict_r_o[int(key)].append([(gyro*0.016), frames_traversed])
                    elif direction == "I":
                        gyro_dict_r_i[int(key)].append([(gyro*0.016), frames_traversed])
                else:
                    if direction == "O":
                        gyro_dict_l_o[int(key)].append([(gyro*0.016), frames_traversed])
                    elif direction == "I":
                        gyro_dict_l_i[int(key)].append([(gyro*0.016), frames_traversed])
        right = False
    
    gyros = [gyro_dict_r_o, gyro_dict_r_i, gyro_dict_l_o, gyro_dict_l_i]
    gyro_name = ["right out", "right in", "left out", "left in"]
    count = 0
    print("degrees per frame breathing:", breathe_rate)
    for gyro_dict in gyros:
        transform(gyro_dict, breathe_rate)
        order(gyro_dict)
        print(gyro_dict)
        total_average_gyro = 0
        for value in gyro_dict.values():
            total_average_gyro += value[0]
            percent = (value[1]/value[0])*100
            print("percent breathing:", percent)
        print(ID, gyro_name[count], "total average:", total_average_gyro/len(gyro_dict))
        count+=1
        
    
    figure, axis = plt.subplots(2, sharey=True)
    figure.suptitle("Right arm, Out (top) vs. In (bottom): Subj. " + ID)
    #axis[0].bar(gyro_dict_r.keys(), means_r)
    print("This:", list(gyro_dict_r_o.values()))
    new_list_r_o = []
    new_list_r_i = []
    new_list_l_o = []
    new_list_l_i = []
    new = [new_list_r_o, new_list_r_i, new_list_l_o, new_list_l_i]
    meep = 0
    for item in gyros:
        for i in list(item.values()):
            new[meep].append(i[0])
        np.vectorize(item)
        meep+=1
        
    print([int(j) for j in gyro_dict_r_o.keys()])
    print(new_list_r_o)
    
    axis[0].bar(np.vectorize([str(j) for j in gyro_dict_r_o.keys()]), [new_list_r_o])
    axis[0].set_xlabel("board position (degrees)")
    axis[1].set_ylabel("average degrees traversed per repetition")
    axis[1].bar([str(j) for j in gyro_dict_r_i.keys()], [new_list_r_i])
    axis[1].set_xlabel("board position (degrees)")
    
    figure_2, axes = plt.subplots(2, sharey=True)
    figure_2.suptitle("Left arm, Out (top) vs. In (bottom): Subj. " + ID)
    axes[0].bar([str(j) for j in gyro_dict_l_o.keys()], [new_list_l_o])
    axes[0].set_xlabel("board position (degrees)")
    axes[1].set_ylabel("average degrees traversed per repetition")
    axes[1].bar([str(j) for j in gyro_dict_l_i.keys()], [new_list_l_i])
    axes[1].set_xlabel("board position (degrees)")
    
    
main()
