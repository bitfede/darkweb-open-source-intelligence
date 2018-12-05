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

#
# Runs onionscan as a child process
#
def run_onionscan(onion):
    
    print("[*] Onionscanning %s" % onion)

    #fire up onionscan
    process = subprocess.Popen(["onionscan", "webport=0", "--jsonreport", "--simplereport=false", onion], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    #start the timer for 5 minutes
    process_timer = Timer(300, handle_timeout, args=[process, onion])
    process_timer.start()

    #wait for the onion scan results
    stdout = process.communicate()[0]

    #if the results are valid, kill the timer
    if process_timer.is_alive():
        process_timer.cancel()
        return stdout

    print("[!!] Process timed out!")

    return None

#
# Handles timer timeout from the onionscan proces
#
def handle_timeout(process, onion):
    global session_onions
    global identity_lock
    
    #halt the main thread while we grab a new identity
    identity_lock.clear()
    
    #kill onionscan process
    try:
        process.kill()
        print("[!!] Killed the onionscan process.")
    except:
        pass

    #switch Tor identities to guarantee that we have good connection
    with Controller.from_port(port=9051) as torcontrol:

        #auth
        torcontrol.authenticate(os.environ['ONIONRUNNER_PW'])

        #send the signal for a new identity
        torcontrol.signal(Signal.NEWNYM)

        #wait for initialization of new identity
        time.sleep(torcontrol.get_newnym_wait() )

        print("[!!] Switched Tor identities")

    #push the onion back to the list
    session_onions.append(onion)
    random.shuffle(session_onions)

    #allow the main thread to resum executing
    identity_lock.set()

    return

#
# Processes the JSON result from onionscan
#
def process_results(onion, json_response):
    global onions
    global session_onions

    #create an output folder
    if not os.path.exists("onionscan_results"):
        os.mkdir("onionscan_results")

    #write out the JSON results of the scan
    with open( "%s/%s.json" % ("onionscan_results", onion), "wb") as fd:
        fd.write(json_response)

    #look for additional .onion domains to add to our scan list
    scan_result = ur"%s" % json_response.decode("utf8")
    print(scan_result)
    scan_result = json.loads(scan_result)

    #all possible outcomes covered here
    if scan_result['identifierReport']['linkedOnions'] is not None:
        add_new_onions(scan_result['identifierReport']['linkedOnions'])
    
    if scan_result['identifierReport']['relatedOnionDomains'] is not None:
        add_new_onions(scan_result['identifierReport']['relatedOnionDomains'])

    if scan_result['identifierReport']['relatedOnionServices'] is not None:
        add_new_onions(scan_result['identifierReport']['relatedOnionServices'])

    return

#
# Handle new onions
#
def add_new_onions(new_onion_list):
    
    global onions
    global session_onions

    for linked_onion in new_onion_list:
        if linked_onion not in onions and linked_onion.endswith(".onion"):
            print("[++] Discovered new .onion => %s" % linked_onion)

            onions.append(linked_onion)
            session_onions.append(linked_onion)
            random.shuffle(session_onions)
            store_onion(linked_onion)

    return




##
## MAIN
##

print("-------------")
print("-ONIONRUNNER-")
print("-------------")

#get the list of onions to analyze
onions = get_onion_list()

#randomize the list a bit
random.shuffle(onions)
session_onions = list(onions)

count = 0

while count < len(onions):
    
    #if the event is cleared we will halt here
    #otherwise we continue execution
    identity_lock.wait()

    #grab a new onion to scan
    print("[*] Running %d of %d." % (count, len(onions)) )
    onion = session_onions.pop()

    #check if we already scanned this one
    if os.path.exists("onionscan_results/%s.json" % onion ):

        print("[!] Already retrieved %s. Skipping." % onion)
        count += 1

        continue

    #run the scan
    result = run_onionscan(onion)

    #process reults
    if result is not None:
        if len(result):
            process_results(onion, result)
            count +=1





