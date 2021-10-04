# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 21:37:00 2021

@author: edwin
"""

import pandas as pd
from collections import defaultdict
import statistics

x_healthy = []
x_stroke = []
degrees_healthy = []
degree_forearm_healthy = []
degrees_stroke = []
degree_forearm_stroke = []
## frame 49 to 270, 292 (0-500, 160 frames) and 605
forearm_gyro = pd.read_csv("test(2.23)_stroke_forearm_gyro.csv")
time_forearm = forearm_gyro["Timestamp (microseconds)"]
# print("file time_forearm:", len(time_forearm))

def main():
    stroke_numbers = ["415", "292", "605", "093", "554"]
    # 909 is healthy 60fps
    healthy_numbers = ["750", "402", "389", "819"]
    # 199 not found
    # 819 issue
    sample_size = [stroke_numbers, healthy_numbers]
    for sample in sample_size:
        print(sample)
        # print("count:", count)
        for number in sample:
            print("number: ", number)
            chest_gyro = pd.read_csv(number + "_gyro.csv")
            reference = pd.read_csv(number + "_annotations.csv")
            annotations = pd.read_csv(number + "_all_labels.csv")
    
            # chest accel data
            x_axis = chest_gyro["Gyro X (°/s)"]
            timecodes = chest_gyro["Timestamp (microseconds)"]
            
            for index, row in reference.iterrows():
                if row["EventType"] == "RECORDING":
                    reference_point = row["Start Timestamp (ms)"]*1000
            degree = degrees_traveled(annotations, reference_point, x_axis, timecodes)
            print("gyroscopy data:", degree)
            total = sum(degree)
            print("sum of subject", number, ":", total)
            if sample == stroke_numbers:
                degrees_stroke.append(total)
            elif sample == healthy_numbers:
                degrees_healthy.append(total)
    print("average gyro stroke:", statistics.mean(degrees_stroke))
    print("average degrees healthy:", statistics.mean(degrees_healthy))

def convert(number, annotations):
    for index, row in annotations.iterrows():
        start = row["In"]
        end = row["Out"]
    for marker in start, end:
        start.split(":")


# counter_dict = defaultdict(int)
def finder(point, timecodes):
    counter_dict = defaultdict(int)
    j = 0
    for timecode in timecodes:
        counter_dict[j] = abs(timecode - point)
        j += 1
    key_min = min(counter_dict.keys(), key = lambda k: counter_dict[k])
    return key_min, timecodes[key_min]


def degrees_traveled(annotations, reference_point, x_axis, timecodes):
    gyroscopy = []
    RO = []
    RI = []
    count = 0
    for index, row in annotations.iterrows():
        if count == 0:
            if row["Marker Name"] == "TapC":
                tap_frame = row["In"]
                count += 1
            if row["Marker Name"] == "CupRRCR":
                tap_frame = row["In"]
                count += 1
            if row["Marker Name"] == "pull":
                tap_frame = row["In"]
                count += 1
        if count == 1:
            if row["Marker Name"] == "RO":
                if len(RO) < 20:
                    RO.append(row["In"])
            if row["Marker Name"] == "RI":
                if len(RI) < 20:
                    RI.append(row["Out"])
    print("RO length:", len(RO))
    print("RI length", len(RI))
    print(RO)
    print(RI)
    
    if len(RO) != len(RI):
        print("RO != RI error")
    
    sub_1 = tap_frame.split(";")
    start = [int(i) for i in sub_1]
    # print("sensor tap: ", start)
    start_frame = (start[0]*60*60*30) + (start[1]*60*30) + (start[2]*30) + (start[3])
    
    for i in range(len(RO)):
        roll_frame = RO[i]
        done_frame = RI[i]
        
        sub_2 = roll_frame.split(";")
        end = [int(i) for i in sub_2]
        # print("start RP: ", end)
        end_frame = (end[0]*60*60*30) + (end[1]*60*30) + (end[2]*30) + (end[3])
        
        sub_3 = done_frame.split(";")
        end_1 = [int(i) for i in sub_3]
        # print("end RP: ", end_1)
        end_1_frame = (end_1[0]*60*60*30) + (end_1[1]*60*30) + (end_1[2]*30) + (end_1[3])
        
        frames_passed_start = end_frame - start_frame
        frames_passed_end = end_1_frame - start_frame
        
        # print("timecode length in degrees_traveled:", len(timecodes))
        reference_index, reference_timecode = finder(reference_point, timecodes)
        #print("reference_index:", reference_index)
        #print("reference_timecode:", reference_timecode)
    
        start_ms_passed = (frames_passed_start/30) * 1000000
        #print("start_ms_passed:", start_ms_passed)
        end_ms_passed = (frames_passed_end/30) * 1000000
        #print("end_ms_passed:", end_ms_passed)
    
        final_timecode_start = reference_timecode + start_ms_passed
        #print("final_timecode_start:", final_timecode_start)
        final_timecode_end = reference_timecode + end_ms_passed
        #print("final_timecode_end:", final_timecode_end)
    
        final_index_start, final_start_timecode = finder(final_timecode_start, timecodes)
        final_index_end, final_end_timecode = finder(final_timecode_end, timecodes)
    
        
        #print("start RP index:", final_index_start)
        #print("start RP timecode:", final_start_timecode)
        #print("end RP index:", final_index_end)
        #print("end RP timecode:", final_end_timecode)
        
        #diff = final_index_end - final_index_start
        # print("difference in index:", diff)
        #print("difference in index (seconds):", diff*16000/1000000)
        
        
        gyro_values = []
        for x in range(final_index_end - final_index_start):
            gyro_values.append(abs(x_axis[final_index_start + x]))
        gyro_sum = 0
        for y in range(len(gyro_values)):
            gyro_sum += (gyro_values[y]*0.016)
        gyroscopy.append(gyro_sum)
    print("gyroscopy length:", len(gyroscopy))
    return(gyroscopy)

main()
