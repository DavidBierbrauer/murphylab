"""#!/usr/bin/env python"""
import pandas as pd
import pymysql
import glob
import re
from password import database_password as DBpwd
from password import database_user as DBuser
from password import database_host as DBhost
from password import database as DB

notes = ""

###  the program stores the textfiles in the database   ###

# Textfiles are at some points not ordered by timestamp and the licks are without a tag, also some rare errors in the textfiles need to be resolved #

## save commands. specify the table for the textfile!  ##
# we add the project ID to the textfile copy in the DB to introduce a powerful foreign key we might need #
# most powerful keys for this database are timestamps, rfid tags and project ID #
# notes are just for the possibility of manual adding notes later on

# PLEASE ADJUST TARGET TABLE HERE `textfilesgroupX`
# YOU ALSO HAVE TO ADJUST THE SOURCE FOLDER AT allfiles at the beginning of the main function
# UPLOAD ALL CAGES SEPERATELY
def generate_commands(vals):
    query="""INSERT INTO `textfilesgroup4`
    (`Tag`, `Timestamp`, `Event`, `Project_ID`, `Notes`)
        VALUES(%s,FROM_UNIXTIME(%s),%s,%s,%s)"""
    values= vals
    return query, values

# database storage function, we use executemany, since we have a long list
def saveToDatabase(query, values):
    db1 = pymysql.connect(host=DBhost, user=DBuser, db=DB, password=DBpwd)
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

#MAIN FUNCTION

#choose files PLEASE ADJUST THE SOURCE FOLDER
allfiles = glob.glob('D:/Cagedata/textfiles/Group4_textFiles/*.txt')            # the code needs a folder Group5_textFiles where the textfiles are in for this group, because we extract the group number from the path,
                                                                                     # the to-do subfolder is just convenient when you have a cage in progress and update your DB daily with new textfiles, but not necessary

for f in allfiles:
    df = pd.read_csv(f, sep="\t",header=None, names = ["Tag", "Unix", "Event", "Date"])
    print(f)
    project = int(''.join([i for i in re.split('_', f) if "Group" in i])[-1:])        #careful, requires similar folder structure in the path of allfiles and will change whereever your textfiles are saved                                              # we don't need the timestamp, the unix timestamp is enough

    #replace zero tags for the licks
    for idx, row in df.iterrows():
        if  df.loc[idx,'Event'] == "SeshStart" or df.loc[idx,'Event'] == "SeshEnd":
            df.loc[idx,'Tag'] = "NULL"
        if df.loc[idx, 'Tag'] == 0:
             df.loc[idx, 'Tag'] = df.loc[idx - 1, 'Tag']
        if df.loc[idx, 'Date'] == "reward":
            df.loc[idx, ['Tag', 'Unix', 'Event', 'Date']] = df.loc[idx, ['Tag', 'Event', 'Date', 'Unix']].values
    df = df[df.Tag != "NULL"]  # kick all rows with Tag: NULL
    df = df.sort_values(by=['Unix'])
    df = df.drop(labels="Date", axis=1)
    df.drop_duplicates(['Unix', 'Event'],inplace=True)                                                         # we drop all entries that are
    df["Project_ID"] = project                                                        # add project ID
    df["Notes"] = ""                                                                  # add empty notes column (at least by default)
    # we make a list out of it, because that's the easiest way to save it in the DB.
    #  there is also a way to directly save pandas Dataframes in the DB
    array = df.values.tolist()
    print(len(array))
    query, values = generate_commands(array)
    saveToDatabase(query, values)
print("done")
