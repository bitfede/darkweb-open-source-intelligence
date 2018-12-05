#######
## AUTHOR:  Federico G. De Faveri
## DATE:    December 2018
## PURPOSE: This program takes a list of onion web addresses and performs
##          a detailed scan for each.
## NOTES:   Thank you to automatingosint.com for the inspiration
#######


#import stem to communicate with the tor process 
from stem.control import Controller
from stem import Signal

#import dependencies
from threading import Timer
from threading import Event
import codecs
import json
import os
import random
import subprocess
import sys
import time

#initialize two empty lists that will contain onion addresses
onions = []
session_onions = []

#set Event object to coordinate later the two threads
identity_lock = Event()
identity_lock.set()

#
# grab the list of onions from our list file
#
def get_onion_list():
    
    #open the file
    if os.path.exists("onion_list.txt"):
        with open("onion_list.txt", "rb") as fd:
            stored_onions = fd.read().splitlines()
    else:
        print "[!] No onion list file 'onion_list.txt' found"
        sys.exit(1)

    print("[*] Total onions for scanning: %d" % len(stored_onions) )

    return stored_onions

#
# Stores an onion in the list of onions
#
def store_onion(onion):
    print("[++] Storing %s in master list." % onion)

    with codecs.open("onion_list.txt", "ab", encoding="utf8") as fd:
        fd.write("%s\n" % onion)

    return




print("Hello welcome")
get_onion_list()





