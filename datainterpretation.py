"""#!/usr/bin/env python"""
import pandas as pd
import pymysql
import re
import glob
from password import database_password as DBpwd
from password import database_user as DBuser
from password import database_host as DBhost
from password import database as DB

###  Program reads out the stored raw data of the textfiles saved in the database , extracts information and saves them in various tables  ###
#  capital VARIABLES are used to be stored in tables via pymsql. lowercase variables are temporary helper variables
#  trials are single stimuli and their responses, sessions are (potential) headfix sessions, videos saves the base information (file names) about the video, rewards saves the water consumption and can be used for daily monitoring
#  entries describe everything between an entry and an exit, with one exeption:
#  if a mouse decides to stay for more than one session without leaving, another entry is statet when the next session begins, this is a necessary workaround to sum up what a mouse is doing with an entry.
#  absolute correct entry counts, if really needed, can always be looked up in the raw data tables

#  the program is based on the knowledge how a textfile will look like. changes in the documentation that are saved in the textfiles will of course disturb this program !
#  here global variables and if conditions are used. it may seem like not the most elegant approach,
#  but it is easy to read, easy to extend and also avoids mistakes. Mice do weird things and using too many loops might result in mistakes when executing the code

###############################################################################
###############################################################################     !!
#      there are two major options                                                  !!
#   reading the data from the raw files in the database                             !!
#   or using the textfiles directly. at the very end of the program                 !!
#   it needs to be clarified which one to use                                       !!
#   double entries will be prohibited by the database
#   in case processing the same data twice                                          !!
###############################################################################     !!
###############################################################################


#  initiating globals
#  variables that get saved in the Database are capital
NOTES = ""
PROJECT = 1

SESSION_START = 0
FIXATION ="fix"
TRIAL_START = 0
TRIAL_IN_SESSION =0
TASK =""
STIMULUS = ""
OUTCOME = ""
LICKS_AFTER_STIM =0
TRIAL_DURATION = 0
HEADFIX_DURATION = 0
VIDEO = ""
LICKWITHHOLD_TIME=0
LED_ON = None
LED_OFF = None
VIDEO_NOTES = ""
LICK_DURATION = 0                                             # Lick duration after stimulus
REACTION_TIME = 0                                             # time till first lick after stimulus
LICKS_TO_TRIGGER_REWARD = 0                                   # number of licks between stimulus and reward given
REWARD_DELAY = 0                                              # time between a trial start and release of water in a trial
LICKS_AFTER_REWARD = 0                                        # number of licks to drink water
LICK_DURATION_AFTER_REWARD = 0                                # time spent licking after reward
REWARD = "NO"                                                 # indicator if reward was earned
LICKS_WHILE_HEADFIXED = 0
LICKS_WITHIN_LICKWITHHOLD_TIME = None
REWARD_TIME = 0

LICKTIME = 0
DELTA_TIME = 0
TRIAL_START_LICKS = 0

trial_in_session_counter=0                                    # counts up how many trials are done in a session, increases with every trial
lick_counter_trials =0                                        # counts the number of licks in a trial, counts up during a the time frame of a trial
last_lick_time=0                                              # timestamp of the last occuring lick
lick_time_start=0                                             # timestamp of the first lick after reward
reaction_time_started = False                                 # gets true at the moment a stimulus gets presented
reaction_time_start = 0                                       # keeps timestamp of the last presented stimulus
result = 0                                                    # the number code of the last trial outcome
reward = False                                                # keep track if a reward was earned
real_trial = False                                            # is true if a trial is currently in progress. mostly to avoid missing statements due to RFID missreadings
previous_outcome = -2                                         # previous outcome. problem with textfiles: lcikwithhold statement sums up a trial with timestamp of stimulus. a trial coonot be saved at this point because all corresponding/following licks are not analyzed yet
previous_outcome_licked = False                               # boolean to keep track if a mouse was active during the previous trial. needed to identify if a mouse is paying attention to trials
lick_counter_headfix = 0                                      # licks while headfixed. most important to identify mice that can't (bad headbar) or don't want to lick while headfixed
trial_event_list = []

TAG = "zero"
ENTRY_TIME = 0
ENTRY_DURATION = 0
ENTRY_TYPE = "entry"
HEADFIX_DURATION_ENTRIES = 0
LICKS = 0
LAST_MOUSE = "zero"
LAST_MOUSE_TIME = 0
LAST_MOUSE_HEADFIX = None
LAST_MOUSE_TIME_HEADFIX = 0
lick_counter_entries =0
started = False
last_mouse_time_start = 0
last_mouse_time_headfix_start = 0
headfix_start = 0

water_available = False

# define RFID taglist to avoid missread tags
taglist=[201608466,201608468,201608481,201609114,201609124,201609136,201609336,210608298,210608315,2016080026,
         2016090636,2016090791,2016090793,2016090845,2016090943,2016090948,2016091033,2016091112,2016091172,2016091184,
         2016090629,2016090647,2016090797,2016090882,2016090964,2016090965,2016090985,2016091183,2016090707,
         201608252,201608423,201608474,2016080008,2016080009,2016080104,2016080242,2016080250,
         801010270,801010219,801010044,801010576,801010442,801010205,801010545,801010462,
         801010272,801010278,801010378,801010459,801010534,801010543,801010546]

#  the most present buzzer stimuli. at a certain point in the textfiles the displayed stimuli were exchanged for a small time. this ensures to use the right one
#  go stimulus is at first position in the list and no go stimulus at second
stimulus_list=["Buzz:N=1,length=0.50,period=0.60","Buzz:N=3,length=0.10,period=0.20"]

# extracting data from database. this is just the database connection function. Shouldn't be touched
def getFromDatabase(query):
    db2 = pymysql.connect(host=DBhost, user=DBuser, db=DB, password=DBpwd)
    cur2 = db2.cursor()
    try:
        cur2.execute(query)
        rows = cur2.fetchall()
    except pymysql.Error as e:
        try:
            print("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            return None
        except IndexError:
            print("MySQL Error: %s" % str(e))
            return None
    except TypeError as e:
        print("MySQL Error: TypeError: %s" % str(e))
        return None
    except ValueError as e:
        print("MySQL Error: ValueError: %s" % str(e))
        return None
    db2.close()
    return rows

## generate save queries and collect corresponding values for different tables. licks are saved in another program
def generate_commands(table):
    if table == "trials_headfixation":
        query="""INSERT INTO `headfix_trials_summary`
        (`Project_ID`, `Mouse`, `Fixation`, `Trial start`, `Trial in session`,`Lickwithhold time`, `Task`, `Stimulus`,
        `Outcome`,`Reaction time`,`Licks after stimulus`, `Lick duration after stimulus`,`Trial duration`,
        `Headfix duration at stimulus`, `Videofile`,`Notes`,`Licks to trigger reward`,`Delay till reward`,`Licks after reward`,
         `Lick duration after reward`,`Reward earned`,`Licks_within_lickwithhold_time`)
            VALUES(%s,%s,%s,FROM_UNIXTIME(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        values= (PROJECT,TAG,FIXATION,TRIAL_START,TRIAL_IN_SESSION,LICKWITHHOLD_TIME,TASK, STIMULUS,OUTCOME,REACTION_TIME,
                 LICKS_AFTER_STIM,LICK_DURATION,TRIAL_DURATION,HEADFIX_DURATION,VIDEO, NOTES, LICKS_TO_TRIGGER_REWARD,
                 REWARD_DELAY, LICKS_AFTER_REWARD, LICK_DURATION_AFTER_REWARD, REWARD,LICKS_WITHIN_LICKWITHHOLD_TIME)

    elif table == "videos":
        query = """INSERT INTO `videos_list`
        (`Videofile`,`Session start`,`LED_on`,`LED_off`,`Fixation`,`Mouse`,`Notes`)
            VALUES(%s,FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),%s,%s,%s)"""
        values= (VIDEO,SESSION_START,LED_ON,LED_OFF,FIXATION,TAG,VIDEO_NOTES)

    elif table == "entries":
        query = """INSERT INTO `entries`
                (`Project_ID`, `Mouse`, `Timestamp`, `Duration`,`Trial or Entry`, `Headfix duration`, `Licks`,`Licks_while_headfixed`,
                `Last Mouse`,`Time after last Mouse exits`,`Last mouse headfixed`,`Time since last headfix`)
                    VALUES(%s,%s,FROM_UNIXTIME(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        values = (PROJECT, TAG, ENTRY_TIME, ENTRY_DURATION, ENTRY_TYPE, HEADFIX_DURATION_ENTRIES, LICKS,LICKS_WHILE_HEADFIXED, LAST_MOUSE, LAST_MOUSE_TIME,LAST_MOUSE_HEADFIX,LAST_MOUSE_TIME_HEADFIX)
    elif table == "rewards":
        query = """INSERT INTO `Rewards`
                (`Mouse`,`Timestamp`,`Reward_type`,`Related_trial`,`Related_entry`)
                VALUES(%s,FROM_UNIXTIME(%s),%s,FROM_UNIXTIME(%s),FROM_UNIXTIME(%s))"""
        values = (TAG,REWARD_TIME, ENTRY_TYPE,TRIAL_START,ENTRY_TIME)
    elif table == "licks":
        query = """INSERT INTO `licks`
                (`Mouse`,`Timestamp`,`Related_trial`,`Delta_time`)
                VALUES(%s,FROM_UNIXTIME(%s),FROM_UNIXTIME(%s),%s)"""
        values = (TAG,LICKTIME,TRIAL_START_LICKS, DELTA_TIME)
    else:
        print("Error in table selection")
    return query, values

## database connection to save. no need to touch
def saveToDatabase(table):
    query, values = generate_commands(table)
    db1 = pymysql.connect(host="localhost",user="root",db="murphylabtest",password=DBpwd)
    cur1 = db1.cursor()
    try:
        cur1.execute(query, values)
        db1.commit()
    except pymysql.Error as e:
        try:
            print( "MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
            return None
        except IndexError:
            print( "MySQL Error: %s" % str(e))
            return None
    except TypeError as e:
        print("MySQL Error: TypeError: %s" % str(e))
        return None
    except ValueError as e:
        print("MySQL Error: ValueError: %s" % str(e))
        return None
    db1.close()

## clean the textfile.
def clean_table(df):
    # licks don't have a displayed tag (0) in the textfile, so we use the previous tag instead
    #  in rare cases the textfiles print the event in the date column, we put everything in right order
    #  sort by timestamp, drop the ambigous date column
    for idx, row in df.iterrows():
        if df.loc[idx, 'Event'] == "SeshStart" or df.loc[idx, 'Event'] == "SeshEnd":
            df.loc[idx, 'Tag'] = "NULL"
        if df.loc[idx, 'Tag'] == 0:
            df.loc[idx, 'Tag'] = df.loc[idx - 1, 'Tag']
        if df.loc[idx, 'Date'] == "reward":
            df.loc[idx,['Tag', 'Unix', 'Event', 'Date']] = df.loc[idx,['Tag', 'Event','Date', 'Unix']].values
    df = df[df.Tag != "NULL"]  # kick all rows with Tag: NULL
    df = df.sort_values(by=['Unix'])
    df = df.drop(labels="Date", axis=1)
    return df

##  processing the result of a trial
def check_result(result,event,trial_event_list):
    global TASK
    global OUTCOME
    global STIMULUS
    global previous_outcome_licked
    global previous_outcome


    if "uzz:N=1" in event:                                       # update stimulus list because of currupted textfiles.
        stimulus_list[0] = ','.join([i for i in trial_event_list if "uzz" in i or "length" in i or "period" in i])  # first entry in list is for go trials and we use either 1 or 2 buzzes
    elif "uzz:N=2" in event:
        stimulus_list[0] = ','.join([i for i in trial_event_list if "uzz" in i or "length" in i or "period" in i])
    elif "uzz:N=3" in event:
        stimulus_list[1] = ','.join([i for i in trial_event_list if "uzz" in i or "length" in i or "period" in i])  # no go trials use 3 buzzes and are at stimulus_list[1]


    if result % 2 == 0:                                           # even numbers are related to GO trials
        TASK = "GO in time window"
        STIMULUS = stimulus_list[0]
    else:                                                         # odd numbers are NO GO trials
        TASK = "NO GO"
        STIMULUS = stimulus_list[1]

    if "laser" in event:                                          # overwrite STIMULUS if laser is stimulation is used
        STIMULUS = ','.join([i for i in trial_event_list if "laser" in i or "x=" in i or "y=" in i])

    if result == 0:                                               # overwrite with the special case of GO=0
        TASK = "GO and no licking required"
    if result > 0:                                                # correct trials are positive
        OUTCOME = "correct"
    else:                                                         # name the outcomes of the fail trials
        if result == -4:
            OUTCOME = "fail: licked too early"
        elif result == -1:
            OUTCOME = "fail: licked, but right time window"
        elif result == -3:
            OUTCOME = "fail: licked and also too early"
        elif result == 0:
            OUTCOME = "no licking required"

# saving the trial. problem is that we just know that we have to save a trial when the summary of the new one appears
def save_previous_trial(result, next_outcome,unix,lw2):
    global LICKS_AFTER_STIM
    global LICK_DURATION
    global REACTION_TIME
    global OUTCOME
    global TRIAL_DURATION
    global lick_counter_trials
    global NOTES
    global LICKS_AFTER_REWARD
    global LICKS_TO_TRIGGER_REWARD
    global LICK_DURATION_AFTER_REWARD
    global REWARD_DELAY
    global REWARD
    global reward
    global previous_outcome_licked
    global previous_outcome


    LICKS_AFTER_STIM = lick_counter_trials                                                 #finalyze the count of licks after stimulus
    LICK_DURATION = last_lick_time - lick_time_start                                       #time between last lick and first lick after reward, might be overwritten of no licks occur
    # if trial was correct
    if reward == True:                                                                     #only rewarded trials. they contain licks, otherwise they wouldn't be rewarded
        LICKS_AFTER_REWARD = LICKS_AFTER_STIM - LICKS_TO_TRIGGER_REWARD                    #calculate count of licks after rewards
        if LICKS_AFTER_REWARD != 0:                                                        #if there were licks after reward calculate the lick duration
            try:                                                                           #program will fail if one of the variables is None
                LICK_DURATION_AFTER_REWARD = LICK_DURATION + REACTION_TIME - REWARD_DELAY
            except:
                LICK_DURATION_AFTER_REWARD = None                                          #in case of program failure there won't be a lick time to calculate, because of missing licks
        else:
            LICK_DURATION_AFTER_REWARD = None                                              #no licks no lick time
        REWARD = "YES"                                                                     #this marks if the reward was earned, not if it was taken
    # trial not correct
    else:
        LICKS_AFTER_REWARD = None
        LICKS_TO_TRIGGER_REWARD = None
        LICK_DURATION_AFTER_REWARD = None
        REWARD_DELAY = None
        REWARD = "NO"
    reward = False                                                                         #after the previous evaluation reset the parameter

    if reaction_time_started == True:                                                      #mouse did not lick in between, it may be not active
        REACTION_TIME = None
        LICKS_AFTER_STIM = 0
        LICK_DURATION = 0
        if result == -2:                                                                   #two options: correct NO GO trial or incorrect GO trial
            OUTCOME = "fail: did nothing"                                                  #finalyze the outcome for DB
            previous_outcome_licked = False                                                #mark the trial as a trial without licking for activity evaluation
        elif result == 1:                                                                  #correct no go trial mus be further investigated
            if (previous_outcome != -2 and previous_outcome !=1) and (next_outcome != -2 and next_outcome !=1):   #activity prooven
                OUTCOME = "correct: is active"
            elif (previous_outcome == -2 or previous_outcome ==1) and (next_outcome == -2 or next_outcome ==1):   #both surrounding trials had no licks
                OUTCOME = "correct: probably inactive"
            else:                                                                                                 #one of the surrounding trials had no licks
                OUTCOME = "correct: maybe inactive"
    else:                                                                                   #mouse licked
        if result == -2:
            OUTCOME = "fail: licked too late"
            previous_outcome_licked = True
        if result == 1:
            OUTCOME = "correct: is active"                                                  #mouse wasn't supposed to lick, but licked late enough to get a correct NO GO trial
    TRIAL_DURATION = unix - TRIAL_START + LICKWITHHOLD_TIME - lw2                           #lw2 is the lickwithhold time of the current trial
    previous_outcome = result
    saveToDatabase("trials_headfixation")                                                   #save trial information in trials table
    clear_variables("trials",unix)                                                          #reset trial related variables

#function to reset the variables for the new trial
def clear_variables(variableset,unix):
    #trial related globals
    global LICKS_AFTER_STIM
    global LICK_DURATION
    global REACTION_TIME
    global OUTCOME
    global TRIAL_DURATION
    global lick_counter_trials
    global NOTES
    global LICKS_AFTER_REWARD
    global LICKS_TO_TRIGGER_REWARD
    global LICK_DURATION_AFTER_REWARD
    global REWARD_DELAY
    global REWARD
    global reward
    #entry related globals
    global lick_counter_entries
    global LAST_MOUSE
    global LAST_MOUSE_HEADFIX
    global started
    global HEADFIX_DURATION_ENTRIES
    global last_mouse_time_start
    global last_mouse_time_headfix_start
    global LAST_MOUSE_TIME
    global LAST_MOUSE_TIME_HEADFIX
    global headfix_start
    global water_available
    global lick_counter_headfix
    global LICKS_WHILE_HEADFIXED
    global LICKS_WITHIN_LICKWITHHOLD_TIME
    global trial_event_list
    # during one entry there can be multiple trials. since we save trials and entries we have to specify which vriables to reset.
    if variableset == "trials":
        lick_counter_trials = 0
        LICKS_AFTER_STIM = 0
        LICKS_TO_TRIGGER_REWARD = 0
        NOTES = ""
        LICKS_AFTER_REWARD = 0
        LICK_DURATION_AFTER_REWARD = 0
        REWARD_DELAY = 0
        TRIAL_DURATION = 0
        REWARD = "NO"
        reward = False
        LICKS_WITHIN_LICKWITHHOLD_TIME = None
    elif variableset == "entries":
        headfix_start = 0
        lick_counter_entries = 0
        LAST_MOUSE = TAG
        if ENTRY_TYPE == "fix" or ENTRY_TYPE == "nofix":
            LAST_MOUSE_HEADFIX = TAG
            LAST_MOUSE_TIME_HEADFIX = 0
            last_mouse_time_headfix_start = unix
        started = False
        HEADFIX_DURATION_ENTRIES = None
        LAST_MOUSE_TIME = 0
        last_mouse_time_start = unix
        lick_counter_headfix = 0
        LICKS_WHILE_HEADFIXED = 0
        trial_event_list = []

def standardize_trial_event_string(event_string):
    #done because of older textfiles which have another syntax. if possible keep the same syntax all the time
    if event_string[54:57] == "GO=":                                          #up to date syntax
        event = event_string
    if event_string[:4] == "Buzz":                                            #lickwithhold statement is missing mostly problem of early cage 1 and 5
        event = "lickWitholdTime=1.00,"                                       #manually adding this statement and an ARTIFICIAL time!
                                                                              # this is not ideal but measuring it can be tricky. it would be the time between the last lick and the stimulus, but mice don't always lick
                                                                              # the best way to avoid that this procedure comes to use is to make sure that the textfiles are always generated the same
    if len(event_string) == 53:
        event = event_string + ",GO=0"                                        #this issue occured in cage 5 when licking wasn't required, yet.
    elif len(event) == 21:
        event = event + "Buzz:N=2,length=0.10,period=0.20,GO=0"               #this issue occured at the very beginning of cage 1 when stimulus was implemented
    elif len(event+event_string) == 53:
        event = event + event_string + ",GO=0"                                #this issue occured in cage 1 when licking wasn't required, yet.
    return event

### directly using textfiles ###
# datainterpretation is called at the end of preprocessing
def use_textfiles():
    global PROJECT
    # a few example paths, need to be adjusted. A TO-DO folder might become handy
    # the asterisk is a placeholder and *.txt means here: all files that are textfiles

    #allfiles = glob.glob('D:/Cagedata/textfiles/Group5_textFiles/todo/*.txt')                 # queue up all files in a to do folder
    allfiles = glob.glob('D:/Cagedata/textfiles/Group[2-5]_textFiles/*.txt')                 # queue up all data
    #allfiles = glob.glob('D:/Cagedata/textfiles/Group1_textFiles/headFix_2_20170717.txt')    # run a single file
    print(allfiles)
    for f in allfiles:
        #  using dataframe to process the textfiles
        df = pd.read_csv(f, sep="\t",header=None, names = ["Tag", "Unix", "Event", "Date"])
        print(f)
        PROJECT = int(''.join([i for i in re.split('_', f) if "Group" in i])[-1:])        #careful, requires similar folder structure in the path of allfiles and will change whereever your textfiles are saved
        print(PROJECT)
        # the next lines are a workaround of some strange things that might happen during cleaning the dataframe
        # saving and reloading it is a quick and dirty way to avoid this kind of things
        df = clean_table(df)
        df.to_csv("temp.csv",sep="\t",header=None)
        df1 = pd.read_csv("temp.csv", sep="\t",header=None,names = ["Tag", "Unix", "Event"])
        array = df1.values.tolist()
        df1.to_csv("testi.csv")
        print(len(array))
        analyze_trials_and_entries(array)
        analyze_licks(array)

def use_database():
    # import data from raw data. ADJUST THE DATES.
    # I wouldn't overdo with loading too many data at once, but a few days should be fine
    # Daily updates are common, since this is used while cages run
    query = """SELECT `Tag`,UNIX_TIMESTAMP(`Timestamp`),`Event` FROM `textfilesgroup1`   
    ORDER BY `Timestamp`  ASC"""
    data = list(getFromDatabase(query=query))
    df = pd.DataFrame(data=data, columns=["Tag", "Unix", "Event"])
    df["Unix"] = df["Unix"].astype(float)
    array = df.values.tolist()
    print(len(array))
    # our data are already preprocessed, so we just call our interpretation function line by line
    analyze_trials_and_entries(array)
    analyze_licks(array)


def analyze_trials_and_entries(array):
    # tell python that we are aware that we are messing around with globals now.
    global NOTES
    global PROJECT

    global SESSION_START
    global FIXATION
    global TRIAL_START
    global TRIAL_IN_SESSION
    global TASK
    global STIMULUS
    global OUTCOME
    global LICKS_AFTER_STIM
    global TRIAL_DURATION
    global HEADFIX_DURATION
    global VIDEO
    global LICKWITHHOLD_TIME
    global LED_ON
    global LED_OFF
    global VIDEO_NOTES
    global LICK_DURATION
    global REACTION_TIME
    global LICKS_TO_TRIGGER_REWARD
    global REWARD_DELAY
    global LICKS_AFTER_REWARD
    global LICK_DURATION_AFTER_REWARD
    global REWARD
    global LICKS_WHILE_HEADFIXED
    global LICKS_WITHIN_LICKWITHHOLD_TIME
    global REWARD_TIME

    global trial_in_session_counter
    global lick_counter_trials
    global last_lick_time
    global lick_time_start
    global reaction_time_started
    global reaction_time_start
    global result
    global reward
    global real_trial
    global previous_outcome
    global previous_outcome_licked
    global lick_counter_headfix
    global trial_event_list

    global TAG
    global ENTRY_TIME
    global ENTRY_DURATION
    global ENTRY_TYPE
    global HEADFIX_DURATION_ENTRIES
    global LICKS
    global LAST_MOUSE
    global LAST_MOUSE_TIME
    global LAST_MOUSE_HEADFIX
    global LAST_MOUSE_TIME_HEADFIX
    global lick_counter_entries
    global started
    global last_mouse_time_start
    global last_mouse_time_headfix_start
    global headfix_start
    global water_available


    ### here we start,we process now every event line by line
    for i in range(len(array)):                                               #read in a line. each line conisists of a mouse-TAG, a unix timestamp and an event
        TAG = int(array[i][0])
        unix = array[i][1]
        event = str(array[i][2])
        #filter mouse and currupted files
        if TAG not in taglist:
            continue                                                          #get rid of nonsense tags
        if unix < 1008915797:
            continue                                                          #get rid of (hopefully all) currupted timestamps
        #start analyzing
        else:
            if "uzz" in event:
                event = standardize_trial_event_string(event)                 #deal with old textfiles that had different documentation
            if event == "entry":
                had_session = False                                           #indicates that mouse had no session yet. important for detection of double sessions
                ENTRY_TIME = unix                                             #catches time when the mouse enters
                started = True                                                #boolean to prevent irritation for the rest of the program if an entry is missing
                ENTRY_TYPE = "entry"                                          #type will be overwritten when headfixing attempt occurs
                if last_mouse_time_start != 0:                                #condition prevents weird things after restarts
                    LAST_MOUSE_TIME = unix - last_mouse_time_start            #calculate how long it has been since the last mouse left the chamber
                if last_mouse_time_headfix_start != 0:                        #calculate how long it has been since the last mouse left the chamber after a headfix session (including no fix trials)
                    LAST_MOUSE_TIME_HEADFIX = unix - last_mouse_time_headfix_start
            if event == "entryReward":
                water_available = True
            if event == "check No Fix Trial" or event == "check+":            #start of headfixation
                if had_session == True:                                       #condition indicates a double trial without leaving. simulating new entry for documentation
                    ENTRY_DURATION = unix - ENTRY_TIME
                    LICKS = lick_counter_entries
                    saveToDatabase("entries")
                    clear_variables("entries", unix)
                    ENTRY_TIME = unix
                    started = True                                            # indicator that a trial started
                    if last_mouse_time_start != 0:                            # condition to avoid false behaviour at the beginning of the loop when there are no previous mice
                        LAST_MOUSE_TIME = unix - last_mouse_time_start        # this is the previous entry, previous headfixation is monitored below
                    if last_mouse_time_headfix_start != 0:
                        LAST_MOUSE_TIME_HEADFIX = unix - last_mouse_time_headfix_start
                trial_in_session_counter = 0                                  # tracks the number of trials in a session, needs to be reseted at this point
                SESSION_START = unix                                          # time when the mouse get's headfixed
                previous_outcome = -2                                         # initializes this variable . prevents program error during first trial in session. will be overwritten when second trial is in line
                previous_outcome_licked = False                               # initializes this variable. variable is there to track activity of the mouse and if its paying attention
                if event == "check+":                                         # textfile code for and active headfixation
                    FIXATION = "fix"
                    headfix_start = unix                                      # time when headfixing starts
                    ENTRY_TYPE = "fix"                                        # overwrite type from entry to fix
                if event == "check No Fix Trial":                             # textfile code for a trial  without headfixation
                    FIXATION = "no fix"
                    ENTRY_TYPE = "nofix"                                      #overwrite type from entry to no fix. don't change spelling, though it seems like there is a typo
                    HEADFIX_DURATION_ENTRIES = None                           #this varaiable is the complete headfix duration of the session and is stored in the entries table. differs from HEADFIX_DURATION which is the time how long the mouse is fixed at this moment
            if event == "check-" and ENTRY_TYPE == "entry":
                ENTRY_TYPE = "away"                                           #overwrite type from entry to symbolyze that the mouse fled when it heard the motor. sometimes they first make a trial and then get a check-, to avoid overwriting good trials we just replace it when it was a bare entry before
                HEADFIX_DURATION_ENTRIES = None                               # no headfixation, no headfix time
            if event == "BrainLEDON":
                LED_ON = unix
            if event == "BrainLEDOFF":
                LED_OFF = unix
            if "video" in event:
                VIDEO = "M"+event[6:]                                         #reconstructs the video filename for the videos table
            if event == "reward":                                             #these parameters are only not None when there is a successful GO trial
                LICKS_TO_TRIGGER_REWARD = lick_counter_trials                 #number of licks the mouse made between stimulus and reward
                REWARD_DELAY = unix - TRIAL_START                             #time between reward and stimulus, should be a fixed interval due to the code
                reward = True
                water_available = True                                        # we will later on look if a lick occurs after water is available to keep track of the real drinking behaviour
            #trial summaries: this get's complicated. biggest problem is that most variables for the trial are calculated after the summary was printed in the textfile
            # this requires a careful management of the flow of the code, by first saving the previous trial and then actualizing the variables for the next trial
            # it requires to partly save some variable values of the trial summary of the textfile in temporary variables
            if "lickWith" in event:
                trial_event_list = re.split(',', event)
                real_trial = True                                             #marker for the program to pay attention that a trial is in progress
                #next_outcome = int(event[57:])                               #store the outcome of trial in a temporary variable
                next_outcome = ''.join([i for i in trial_event_list if "GO" in i])#store the outcome of trial in a temporary variable
                # save the previous trial
                if trial_in_session_counter !=0:                              #if there was a previous trial then save it now. afterwards textfile entry will be used to save the corrosponding trial
                    save_previous_trial(result, next_outcome,unix,float(''.join([i for i in trial_event_list if "lickWith" in i])[-4:]))   # float join statement extracts the lickwitholdtime as number
                #start documentation the new trial
                clear_variables("trials",unix)                                #reset trial related values
                lickwithhold_time = round(unix - last_lick_time,2) + 1        # calculate how long the mouse really withholds its licks, add 1ms to avoid false negatives due to rounding
                last_trial_time = round(unix - TRIAL_START)
                compare_variable = min(lickwithhold_time,last_trial_time)     # in case of no licks compare with beginning of last trial
                LICKWITHHOLD_TIME = float(''.join([i for i in trial_event_list if "lickWith" in i])[-4:])
                if (LICKWITHHOLD_TIME <= compare_variable):                   # evaluate if the program made a mistake and overlooked a lick during the lickwithold time
                    LICKS_WITHIN_LICKWITHHOLD_TIME = None                     # program works correct
                else:
                    LICKS_WITHIN_LICKWITHHOLD_TIME = "yes"                    # program overlooked a lick

                TRIAL_START = unix
                result = int(''.join([i for i in trial_event_list if "GO" in i])[3:])       #outcome of the trial
                #STIMULUS = event[21:53]                                       #save stimulus, this might be overwritten later due to bad textfiles
                #NOTES = event[54:]                                            #NOTES saves the GO-code we use for the trial outcomes
                NOTES = ''.join([i for i in trial_event_list if "GO" in i])
                check_result(result,event,trial_event_list)
                VIDEO_NOTES = VIDEO_NOTES + NOTES+ "\n"                  #saves all trial outcomes of a session for the video table
                if FIXATION == "fix":
                    HEADFIX_DURATION = unix - headfix_start                   #duration how long the mouse is headfixed at this timepoint
                else:
                    HEADFIX_DURATION = None                                   #no headfix time on no fix trials
                reaction_time_start = unix                                    #tracks the beginning of the reaction time variable
                reaction_time_started = True                                  #tracks the beginning of the reaction time variable
                trial_in_session_counter += 1                                 #counts the number of trials in the headfix session
                TRIAL_IN_SESSION = trial_in_session_counter                   #variable for the DB that saves the current trial in session


            if "lick:" in event:
                lick_counter_entries += 1                                     #counts licks for the entries table, so all the licks that happen during the mouse is in the chamber
                if FIXATION == "fix":
                    lick_counter_headfix += 1                                 #seperately keep track of licks made under headfixation
                # other licks than first
                if water_available == True:
                    # document if mouse got water
                    if started == False:
                        ENTRY_TYPE = "pass"                                   #mouse has probably passed the RFID reader because the lick occurs after exit
                    water_available = False                                   #assume that mouse drank all water after one lick
                    REWARD_TIME = unix                                        #save the time when the mouse got the reward for the rewards table
                    saveToDatabase("rewards")                                 #save to DB that mouse got a reward
                if reaction_time_started == False:                            #look at licks that are NOT the first lick after stimulus
                    lick_counter_trials += 1                                  #count licks
                    last_lick_time = unix                                     #keep track of the timestamp of the last recent lick
                    #determine if mouse pays attention. Important to evaluate if there are GO and NO GO trials. This can be roughly done by looking at trials before and after the current trial
                    previous_outcome_licked = True                            #marks that the mouse licked just recently. the variable will be evaluated when the next trial is saved
                    previous_outcome = 0                                      #initialize and reset the previous outcome
                # first lick after stimulus
                elif reaction_time_started == True:                           #first lick after stimulus
                    REACTION_TIME = unix - reaction_time_start                #calculate the time between stimulus and first lick
                    reaction_time_started = False                             #mark for the next lick that they are not the first after stimulus
                    lick_time_start = unix                                    #keep track of the timepoint when the mouse started licking after stimulus
                    last_lick_time = unix                                     #keep track of the timestamp of the last recent lick
                    lick_counter_trials = 1                                   #set the lick counter to 1, this is more a security than necessary
                    previous_outcome_licked = True                            #marks that the mouse licked just recently.

            # end of headfix and session
            if event == "complete":                                           #marks the time when the mouse gets released.
                had_session = True                                            #marks if a mouse exited yet acfter a session. important to process double sessions
                if headfix_start != 0:                                        #marks that a headfixation took place. headfix_start is 0 for no fix trials
                    HEADFIX_DURATION_ENTRIES = unix - headfix_start           #finalyze the variable for the DB and entries table. Displays how long the mouse was headfixed during this session
                    LICKS_WHILE_HEADFIXED = lick_counter_headfix              #finalyze the lick counts while headfixed
                else:
                    HEADFIX_DURATION_ENTRIES = None
                    LICKS_WHILE_HEADFIXED = None                              #no headfixation, no licks under headfixation

                if real_trial == True:
                    next_outcome = 0                                          #reset variable
                    save_previous_trial(result,next_outcome,unix,0)           #save the last trial
                    saveToDatabase("videos")                                  #save video information
                    VIDEO_NOTES = ""                                          #reset variable
                    trial_in_session_counter=0                                #reset variable
                    real_trial = False                                        #reset variable

            if event == "exit" and started == True:                           #double check if there was an entry before exit
                ENTRY_DURATION = unix - ENTRY_TIME                            #calculate time in chamber
                LICKS = lick_counter_entries                                  #finalyze count of licks while in chamber - entries table
                saveToDatabase("entries")                                     #save the information of the entry
                clear_variables("entries",unix)                               #reset variables related with the entries table
                had_session = False                                           #marker boolean to detect double sessions, will be used when checking bean break (check+-, check no fix) look 100 lines earlier
            if event == "exit" and started == False:
                clear_variables("entries",unix)
                had_session = False
    print("entries and trials done")


def analyze_licks(array):
    #  this analyzes the licks. this unfortunately takes some time
    #  basic idea: we go through the raw data and save all lick event timestamps in a list
    #  we also save the surrounding stimulus timestamp (or entry or exit for the borders)
    #  then we go through the list and calculate the time difference for each lick and the stimulus
    #  so most of the licks have two delta t because they are before and after a stimulus
    #  we save them and their corresponding trial timestamp for joins in the database
    global DELTA_TIME
    global TRIAL_START_LICKS
    global LICKTIME
    global TAG
    trial_in_session_count = 0
    analize_licks = False

    for i in range(len(array)):                                               #read in a line. each line conisists of a mouse-TAG, a unix timestamp and an event
        TAG = int(array[i][0])
        unix = array[i][1]
        event = str(array[i][2])
        if TAG not in taglist:
            continue  # get rid of nonsense tags
        if unix < 1008915797:
            continue  # get rid of currupted timestamps
        else:
            if "uzz" in event:
                event = standardize_trial_event_string(event)
            if event == "check+" or event == "check No Fix Trial":  # there might be a few more licks before headfixing, but they are not related to a trial and therefore of no real use. if they are needed use entry event
                analize_licks = True
                lick_timestamp_array = []
                trial_in_session_count = 0
                current_trial_start = 0
            if "lick:" in event and analize_licks == True:
                lick_timestamp_array.append(unix)
            if "lickWith" in event and analize_licks == True:     # textfile command for a stimulus
                trial_in_session_count += 1
                previous_trial_start = current_trial_start        # shift from previous trial
                current_trial_start = unix
                if len(lick_timestamp_array) == 0:                #will not be saved but to avoid any mistake we proceed like it is a normal trial even without licks
                    LICKTIME = unix
                    DELTA_TIME = 99.99                            # a dummy delta. it can show up in earlier versions of the database but can be easily ignored by a query
                    TRIAL_START_LICKS = current_trial_start
                    if trial_in_session_count > 1:
                        TRIAL_START_LICKS = previous_trial_start
                else:
                    for k in range(len(lick_timestamp_array)):     # process all licks that are saved till the current stimulus
                        LICKTIME = lick_timestamp_array[k]         # timestamp of the lick
                        DELTA_TIME = LICKTIME - current_trial_start# negative deltas
                        TRIAL_START_LICKS = current_trial_start    # timestamp of the corresponding stimulus
                        saveToDatabase("licks")
                        if trial_in_session_count > 1:             # positive deltas of the previous trial are calculated when (at least)  the second trial shows up.
                            DELTA_TIME = LICKTIME - previous_trial_start #positive deltas
                            TRIAL_START_LICKS = previous_trial_start     # timestamp of the corresponding previous trial
                            saveToDatabase("licks")
                lick_timestamp_array = []
            if event == "exit" and analize_licks == True:
                if len(lick_timestamp_array) == 0:
                    LICKTIME = unix
                    DELTA_TIME = 99.99
                    if trial_in_session_count > 1:
                        TRIAL_START_LICKS = previous_trial_start
                else:
                    for k in range(len(lick_timestamp_array)):
                        LICKTIME = lick_timestamp_array[k - 1]
                        DELTA_TIME = LICKTIME - current_trial_start   # positive deltas. this seems a bit counter intuitive, but a exit doesn't overwrite the last trial. so our current trial is still in use but the stored licks have a higher timestamp
                        if trial_in_session_count > 0:                # as long as there is at least one trial we save now the positive deltas of the last trial
                            TRIAL_START_LICKS = current_trial_start
                            saveToDatabase("licks")
                analize_licks = False

    print("licks done")


####     MAIN FUNCTION      #####
# choose whether to use textfiles or uploaded raw data from the database
# comment the other.

#use_database()
use_textfiles()
