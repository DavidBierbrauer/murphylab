#! /usr/bin/python
#-*-coding: utf-8 -*-
from os import path, makedirs, chown
from pwd import getpwnam
from grp import getgrnam
from time import time, localtime,timezone
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymysql
import seaborn as sns
from scipy import stats
from password import database_password as DBpwd


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
    else:
        print("Error in table selection")
    return query, values

def saveToDatabase(table,vals):
    query, values = generate_commands(table,vals)
    db1 = pymysql.connect(host="localhost",user="root",db="murphylab",password=DBpwd)
    cur1 = db1.cursor()
    try:
        cur1.executemany(query, values)
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

class AHF_DataLogger_mysql (AHF_DataLogger):
    # saves data in a myqsl relational database
    # it takes