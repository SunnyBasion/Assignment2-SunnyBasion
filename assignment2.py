#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py
Author: Sunny Basion | 107827172
Semester: Fall 2024

The python code in this file is original work written by
"". No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: OPS Assignment 2

'''

import argparse
import os, sys

def parse_command_args() -> argparse.Namespace:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", epilog="Copyright 2023")
    #Parses command line arguments
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Enable human-readable memory usage format.")
    parser.add_argument("program", type=str, nargs='?', help="If a program is specified, show memory use of all associated processes. Show only total use if not.")
    parser.add_argument("-r", "--running-only", action="store_true", help="Only show memory usage of currently running processes.")
   
    args = parser.parse_args()
    return args

def percent_to_graph(percent: float, length: int = 20) -> str:
    "Convert percentage to a visual bar of specified length."
    conversion = int(length * (percent / 100))
    visual_bar = '#' * conversion + ' ' * (length - conversion)
    return '[' + visual_bar[:length-2] + ']'

def get_sys_mem() -> int:
    "Returns total system memory in KiB (kibibytes)."
    total_sys_mem  = 0
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemTotal:'):
                total_sys_mem  = int(line.split()[1])
                break
    return total_sys_mem 

def get_avail_mem() -> int:
    "Returns total available memory in KiB (kibibytes)."
    total_avail_mem = 0
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith('MemAvailable:'):
                total_avail_mem = int(line.split()[1])
                break
    return total_avail_mem  

def pids_of_prog(app_name: str) -> list:
   "Given an app name, return all PIDs associated with the app."
  
   associated_PID = os.popen(f'pidof {app_name}').read().strip() #obtaining PID that is associated with the app name 
   
  
   if not associated_PID: #If it does not have an associated PID with app name it will return an empty list 
       return []
   
   pids = associated_PID.split() #Split associated PID into a list 
   return pids

def rss_mem_of_pid(proc_id: str) -> int:
    "Returns RSS memory usage of a process in KiB (kibibytes) given its PID."
    rss = 0

    try:
            with open(f"/proc/{proc_id}/smaps", "r") as f: #Opening the smaps file for PID and extracting RSS KiB value 
                for line in f:
                    if line.startswith("Rss:"):
                        rss += int(line.split()[1]) 
    except FileNotFoundError: 
        print(f"Error: The file '/proc/{proc_id}/smaps' does not exist.")
    except PermissionError: 
        print(f"Error: Insufficient permissions to read '/proc/{proc_id}/smaps'.")
    return rss

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "Converts memory size from KiB to human-readable format."
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_count = 0
    result_size = kibibytes
    
    while result_size > 1024 and suf_count < len(suffixes) - 1: 
        result_size /= 1024
        suf_count += 1  
   
    str_result = f'{result_size:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result



if __name__ == "__main__":
    args = parse_command_args() #process args 
   
    if not args.program: #if no program is specified 
        
        total_memory = get_sys_mem()  #total system memory
        available_memory = get_avail_mem()  #available system memory
        used_memory = total_memory - available_memory  # Calculation of memory usage 

        # Conversion of memory to human readability 
        if args.human_readable:
            total_memory_h = bytes_to_human_r(total_memory)
            used_memory_h = bytes_to_human_r(used_memory)
            print(f"Total Memory: {total_memory_h}")
            print(f"Used Memory: {used_memory_h}")
        else:
            print(f"Total Memory: {total_memory} KiB")
            print(f"Used Memory: {used_memory} KiB")

        # Bar --> percent to graph 
        used_percent = (used_memory / total_memory) * 100
        print("Memory Usage:")
        print(percent_to_graph(used_percent, args.length))
    else:
        
        pids = pids_of_prog(args.program)
       
        if not pids: #if it cant find associated PID for the program/app name 
            print(f"No associated program located for program '{args.program}'.")
        else:
            total_rss = 0
            for pid in pids:
                total_rss += rss_mem_of_pid(pid)

            # Convert values to human-readable format
            if args.human_readable:
                total_rss_h = bytes_to_human_r(total_rss)
                print(f"Total RSS Memory Used by {args.program}: {total_rss_h}")
            else:
                print(f"Total RSS Memory Used by {args.program}: {total_rss} KiB")

            # Display bar graph for RSS memory percentage relative to system memory
            rss_percent = (total_rss / get_sys_mem()) * 100
            print("RSS Memory Usage:")
            print(percent_to_graph(rss_percent, args.length))
