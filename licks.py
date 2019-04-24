"""#!/usr/bin/env python"""
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import pymysql
import seaborn as sns
from password import database_password as DBpwd
from password import database_user as DBuser
from password import database_host as DBhost
from password import database as DB


analize_licks = False

taglist=[201608466,201608468,201608481,201609114,201609124,201609136,201609336,210608298,210608315,2016080026,
         2016090636,2016090791,2016090793,2016090845,2016090943,2016090948,2016091033,2016091112,2016091172,2016091184,
         2016090629,2016090647,2016090797,2016090882,2016090964,2016090965,2016090985,2016091183,2016090707,
         201608252,201608423,201608474,2016080008,2016080009,2016080104,2016080242,2016080250,
         801010270,801010219,801010044,801010576,801010442,801010205,801010545,801010462,
         801010272,801010278,801010378,801010459,801010534,801010543,801010546]


#????????????????????????????????get data from database and preprocessing functions???????????????????????????????????????????????????

# get data from database. usually no adjustments required
def getFromDatabase(query):
    db2 = pymysql.connect(host=DBhost, user=DBuser, db=DB, password=DBpwd)
    cur2 = db2.cursor()
    try:
        cur2.execute(query) #, (GO,MOUSE)
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


def generateQuery(table):
    if table == "all_outcomes":
        query = """SELECT licks.Mouse,licks.`Timestamp`, licks.Delta_time, headfix_trials_summary.Notes, headfix_trials_summary.Project_ID FROM `licks`
                inner JOIN `headfix_trials_summary` ON `licks`.`Related_trial` = `headfix_trials_summary`.`Trial start`
                WHERE `headfix_trials_summary`.`Fixation` = "fix" and 
        ((Date(headfix_trials_summary.`Trial start`) between "2017-08-28" and "2017-10-12") OR 
        (Date(headfix_trials_summary.`Trial start`) between "2018-02-19" and "2018-04-01") OR 
        (Date(headfix_trials_summary.`Trial start`) between "2018-04-28" and "2018-06-01") OR 
        (Date(headfix_trials_summary.`Trial start`) between "2018-08-08" and "2018-10-23") OR 
        (Date(headfix_trials_summary.`Trial start`) between "2018-11-23" and "2018-12-20")) 
         AND licks.Delta_time between -3 and 5 AND `headfix_trials_summary`.`Licks_within_lickwithhold_time` IS NULL
        """
    elif table == "single_mouse":
        query = """SELECT `licks`.`Mouse`,`licks`.`Timestamp`, `licks`.`Delta_time`, `headfix_trials_summary`.`Notes`,
         `headfix_trials_summary`.`Project_ID`, `headfix_trials_summary`.`Task`  FROM `licks`
                INNER JOIN `headfix_trials_summary` ON `licks`.`Related_trial` = `headfix_trials_summary`.`Trial start`
                WHERE `headfix_trials_summary`.`Fixation` = "fix" AND 
                ((Date(headfix_trials_summary.`Trial start`) BETWEEN "2018-08-08" and "2018-08-11") OR 
                (Date(headfix_trials_summary.`Trial start`) BETWEEN "2018-08-21" and "2018-08-24") OR
                (Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-09-22" and "2018-09-25") OR
                (Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-10-01" and "2018-10-04"))
                AND (licks.Delta_time BETWEEN -3 and 5) AND licks.Mouse IN ("201608423")
                AND `headfix_trials_summary`.`Licks_within_lickwithhold_time` IS NULL
                 """
    elif table == "counts": #days 1-4, 14-17,46-49,55-58
        query = """SELECT `Task`,`Notes`,
         SUM(IF(Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-08-08" and "2018-08-11",1,0)) AS `early`,
         SUM(IF((Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-08-21" and "2018-08-24"),1,0)) AS `nogo`,
         SUM(IF((Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-09-22" and "2018-09-25"),1,0)) AS `late`,
         SUM(IF((Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-10-01" and "2018-10-04"),1,0)) AS `later`
                FROM `headfix_trials_summary` WHERE `Mouse` IN ("201608423")
                 AND `Fixation`="fix"
                 AND `headfix_trials_summary`.`Licks_within_lickwithhold_time` IS NULL
                group BY `Task`,`Notes` WITH ROLLUP"""
    elif table == "times":
        query = """SELECT Date(`Trial start`) AS `Date`, ROUND(MIN(`Lickwithhold time`),1), ROUND(MAX(`Lickwithhold time`),1), ROUND(MIN(`Reaction time`),2),ROUND(MAX(`Reaction time`),2), `Notes`
                FROM `headfix_trials_summary`
                WHERE `Fixation` = "fix" AND
                 (Date(headfix_trials_summary.`Trial start`) BETWEEN "2018-08-08" and "2018-10-23") 
                AND `Notes` IN ("GO=2","GO=1","GO=-4")
                GROUP BY `Date`, `Notes`"""
    elif table == "textfile":
        query = """SELECT `Timestamp`,`Event` FROM `textfilesgroup4` WHERE `Timestamp` BETWEEN "2018-09-25 04:09:54.78" AND "2018-09-25 04:10:43.47"
        """
        #2018-09-15 05:26:53.04, BETWEEN "2018-09-24 23:22:52.51" AND  "2018-09-24 23:23:36.57",  BETWEEN "2018-09-24 23:34:37.65" AND "2018-09-24 23:35:30.06
        #BETWEEN "2018-09-25 04:09:56.78" AND "2018-09-25 04:10:42.47"
    elif table == "single_mouse2":
        query = """SELECT `licks`.`Mouse`,`licks`.`Timestamp`, `licks`.`Delta_time`, `headfix_trials_summary`.`Notes`,
         `headfix_trials_summary`.`Project_ID`, `headfix_trials_summary`.`Task`  FROM `licks`
                INNER JOIN `headfix_trials_summary` ON `licks`.`Related_trial` = `headfix_trials_summary`.`Trial start`
                WHERE `headfix_trials_summary`.`Fixation` = "fix" AND 
                ((Date(headfix_trials_summary.`Trial start`) BETWEEN "2018-08-08" and "2018-08-11") OR 
                (Date(headfix_trials_summary.`Trial start`) BETWEEN "2018-08-24" and "2018-08-27") OR
                (Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-09-13" and "2018-09-16") OR
                (Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-09-25" and "2018-09-28"))
                AND (licks.Delta_time BETWEEN -3 and 5) AND licks.Mouse IN ("201608423")
                AND `headfix_trials_summary`.`Licks_within_lickwithhold_time` IS NULL
                 """
    elif table == "counts2": #days 1-4, 17-20,37-40,49-52
        query = """SELECT `Task`,`Notes`,
         SUM(IF(Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-08-08" and "2018-08-11",1,0)) AS `1`,
         SUM(IF((Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-08-24" and "2018-08-27"),1,0)) AS `2`,
         SUM(IF((Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-09-13" and "2018-09-16"),1,0)) AS `3`,
         SUM(IF((Date(`headfix_trials_summary`.`Trial start`) BETWEEN "2018-09-25" and "2018-09-28"),1,0)) AS `4`
                FROM `headfix_trials_summary` WHERE `Mouse` IN ("201608423")
                 AND `Fixation`="fix"
                 AND `headfix_trials_summary`.`Licks_within_lickwithhold_time` IS NULL
                group BY `Task`,`Notes` WITH ROLLUP"""
    elif table == "licks_within_lickwithholdtime":
        query = """SELECT SUM(IF(`Licks_within_lickwithhold_time` = "yes" AND `Notes`="GO=1",1,0)) / SUM(IF(`Licks_within_lickwithhold_time` is NULL AND `Notes`="GO=1",1,0)) AS "1",
SUM(IF(`Licks_within_lickwithhold_time` = "yes" AND `Notes`="GO=2",1,0)) / SUM(IF(`Licks_within_lickwithhold_time` is NULL AND `Notes`="GO=2",1,0)) AS "2",
SUM(IF(`Licks_within_lickwithhold_time` = "yes" AND `Notes`="GO=-1",1,0)) / SUM(IF(`Licks_within_lickwithhold_time` is NULL AND `Notes`="GO=-1",1,0)) AS "-1",
SUM(IF(`Licks_within_lickwithhold_time` = "yes" AND `Notes`="GO=-3",1,0)) / SUM(IF(`Licks_within_lickwithhold_time` is NULL AND `Notes`="GO=-3",1,0)) AS "-3",
SUM(IF(`Licks_within_lickwithhold_time` = "yes" AND `Notes`="GO=-2",1,0)) / SUM(IF(`Licks_within_lickwithhold_time` is NULL AND `Notes`="GO=-2",1,0)) AS "-2",
SUM(IF(`Licks_within_lickwithhold_time` = "yes" AND `Notes`="GO=-4",1,0)) / SUM(IF(`Licks_within_lickwithhold_time` is NULL AND `Notes`="GO=-4",1,0)) AS "-4"
FROM `headfix_trials_summary` where 1"""
    return query
def myround(x, base=5):
    return int(base * math.floor(float(x*100)/base))/100

def drop_some_parameters(df):
    #unfortunately the parameters are not saved, so we use the maximum and minimum values of a few variables to estimate them
    #most of the parameters are redundant or uninteresting: get rid of them
    df = df[(df.Outcome != "GO=-4")]
    df = df[~((df.Outcome == "GO=1") & (df.variable == "lickdelay_max"))]
    df = df[~((df.Outcome == "GO=1") & (df.variable == "Lickwithhold_max"))]
    df = df[~((df.Outcome == "GO=1") & (df.variable == "Lickwithhold_min"))]
    df = df[((df.Outcome == "GO=2") & (df.variable == "lickdelay_min"))]        #this leaves just the delay time of GO=2

    #round them by adjusting them to the minimum, rounded down to either 0.x5 or 0.1 values. iteration over DF is backwards:
    #  idea: we always increase the value and we always have nice numbers. first values are definetely 0.35
    current_minumum = 1.2
    df = df.iloc[::-1]
    for index, row in df.iterrows():
        current_value = row["value"]
        current_minumum = myround(min(current_value, current_minumum))
        df.loc[index,"Lickdelay_time"] = current_minumum
    df = df.iloc[::-1]
    return df

#?????????????????????????????plots?????????????????????????????????????????????????
def draw_parameters():
    query = generateQuery("times")
    data = list(getFromDatabase(query))
    df = pd.DataFrame(data=data, columns=["Date", "Lickwithhold_min", "Lickwithhold_max", "lickdelay_min", "lickdelay_max","Outcome"])
    df["Date"] = pd.to_datetime(df["Date"])
    df["Day"] = (df["Date"] - pd.to_datetime("2018-08-08")).dt.days
    df1 = pd.melt(df,id_vars=["Day","Outcome"], value_vars=["Lickwithhold_min", "Lickwithhold_max", "lickdelay_min", "lickdelay_max"])
    #sns.lineplot(data=df1, x="Day",y="value", hue="variable",size="Outcome")    #all parameters, most of them uninteresting
    #plt.show()  #shows all variables
    df1 = drop_some_parameters(df1)
    #sns.lineplot(data=df1, x="Day", y="value", hue="variable", size="Outcome")
    fig = plt.figure(figsize=(4.4, 2.2))
    sns.set_context("paper", font_scale=1.75, rc={"lines.linewidth": 5})
    a= sns.lineplot(data=df1, x="Day", y="Lickdelay_time", hue="variable", size="Outcome",legend=False)
    a.set(xlabel="", ylabel="")
    sns.despine()
    plt.yticks([0.35,0.7,1.1])
    plt.tight_layout()
    plt.savefig("parameters.svg",bbox_inches=0, transparent=True)
    plt.show()
def draw_single_session():
    sns.set_context("talk")
    liste = list(getFromDatabase(generateQuery("textfile")))
    df_trials = pd.DataFrame(data=liste, columns=["Timestamp", "Event"])
    df_trials["Time"] = (df_trials["Timestamp"] - df_trials["Timestamp"].iloc[0]).dt.total_seconds()
    print(df_trials)
    fig = plt.figure(figsize=(15,5))
    #entry exit
    a = df_trials.loc[df_trials['Event'].isin(["exit", "entry"]), "Time"]
    b = sns.rugplot(a=a, height=0.1, color="limegreen", linewidth=4,label="Entry/Exit",linestyle = "-")
    #reward
    a = df_trials.loc[df_trials['Event'].isin(["reward","entryReward"]), "Time"]
    b = sns.rugplot(a=a, height=0.18,color="royalblue",linewidth=4,label="Water reward")
    #stimulus
    a = df_trials.loc[df_trials['Event'].str.contains("GO=-1|GO=1|GO=-3"), "Time"]
    b = sns.rugplot(a=a, height=0.24, color="darkred", linewidth=4,label="NO GO stimulus",linestyle = "--")
    a = df_trials.loc[df_trials['Event'].str.contains("GO=-2|GO=2|GO=-4"), "Time"]
    b = sns.rugplot(a=a, height=0.24, color="darkred", linewidth=4,label="GO stimulus")
    #licks
    a = df_trials.loc[df_trials['Event'].isin(["lick:1", "lick:2"]), "Time"]
    b = sns.rugplot(a=a, height=0.06, color="black", linewidth=1.5,label="Licks")
    b.legend(frameon=False)
    #headfix times
    a = df_trials.loc[df_trials['Event'].isin(["check+","complete"]), "Time"]
    b = sns.rugplot(a=a, height=0.02, color="r",linewidth=0.5,alpha=1)
    #LED
    a = df_trials.loc[df_trials['Event'].isin(["BrainLEDON", "BrainLEDOFF"]), "Time"]
    b = sns.rugplot(a=a, height=0.02, color="r", linewidth=0.5,alpha=1)
    #plot
    sns.set(style="white")
    sns.despine(left=True)
    plt.tick_params(labelsize=20,size=25)
    plt.xlabel("Time [s]",fontsize=20)
    plt.ylim(0.2)
    plt.xlim(-2,52)
    plt.tight_layout()
    plt.yticks([])
    plt.savefig("fullsession.svg",bbox_inches=0, transparent=True)
    plt.show()

def draw_facetgrid(purpose,purpose2):
    # get lick data
    rownames = {"range1":"Day 1-4","range2":"Day 14-17","range3":"Day 46-49","range4":"Day 55-58"}
    data = list(getFromDatabase(query = generateQuery(purpose)))
    df = pd.DataFrame(data=data,columns=["Mouse", "Timestamp", "Delta_time", "Outcome", "Cage","Task"])
    df["Training"]= "range1"
    df.loc[df["Timestamp"] > "2018-08-12 00:00:00.01", "Training"] = "range2"
    df.loc[df["Timestamp"] > "2018-08-30 00:00:00.01", "Training"] = "range3"
    df.loc[df["Timestamp"] > "2018-09-26 00:00:00.01", "Training"] = "range4"

    #get number of involved trials
    data1 = list(getFromDatabase(query=generateQuery(purpose2)))
    df1 = pd.DataFrame(data=data1, columns=["Task","Outcome","range1","range2","range3","range4"])
    print(df1)
    #bin data
    bins = np.linspace(-3,5,81,endpoint=True)
    labels = np.linspace(-2.9,5,80,endpoint=True)
    t = df.groupby(["Training", "Task", "Outcome", pd.cut(df['Delta_time'], bins=bins, labels=labels)])["Cage"].size(). \
        reset_index().rename(columns={"Cage": "Licks"})
    t.loc[:, "Licks"] *= 10
    t = t.sort_values(by=["Training"])

    # rescale data by number of involved trials due to Outcome
    for outcome in ["GO=2", "GO=1", "GO=-4", "GO=-2", "GO=-1","GO=-3"]:
        for days in ["range1","range2","range3","range4"]:
            t.loc[(t["Training"] == days) & (t["Outcome"] == outcome), "Licks"] /= int(
                df1.loc[(df1["Outcome"] == outcome), days])
    t.replace({"Training": rownames}, inplace=True)
    sns.set_context("paper",font_scale=1.75)
    gr = sns.catplot("Delta_time", y="Licks", alpha=0.6, col="Task", row="Training", hue="Outcome", legend_out=True,
                     margin_titles=True, aspect=3.5, height=2.2,sharey=True,sharex=True,col_order=["GO in time window","NO GO"],
                     hue_order=["GO=2", "GO=-4", "GO=-2", "GO=1", "GO=-1"], data=t, kind="bar", dodge=False)
    gr.set(xmargin=0.0, ymargin=0.0)
    gr.set_xticklabels(step=10)
    gr.set_xticklabels(labels=range(-3, 6, 1))
    gr.set_axis_labels("", "")
    [plt.setp(ax.texts, text="") for ax in gr.axes.flat]  # remove the original texts, important!
    gr.set_titles(row_template = '{row_name}', col_template='{col_name}')
    sns.despine()
    plt.subplots_adjust(hspace=0.2,wspace=0.1)
    plt.savefig("development.svg",  transparent=True)
    plt.show()



    # grid = sns.FacetGrid(s, col="Task",row="Training", hue="Outcome",legend_out= True, margin_titles  = False,aspect=2.5, height=2.5,
    #                     hue_order=["GO=2","GO=-4","GO=-2","GO=1","GO=-1"])
    #grid.set(xmargin=0, ymargin=0)
    #grid = (grid.map(sns.barplot,"Delta_time","Licks",alpha=0.5,order= labels,dodge=True).add_legend())
    # grid1 = sns.FacetGrid(df, col="Task", row="Training", hue="Outcome", legend_out=True, margin_titles=False, aspect=2.5,height=2.5)
    # grid1.set(xmargin=0, ymargin=0)
    # grid1 =(grid1.map(sns.distplot, "Delta_time",bins=100, kde=False, hist=True, norm_hist=False,
    #                hist_kws={"alpha":0.5},kde_kws={"label": "licks"}).add_legend().set(xlim=(-5, 5)))
    # order=["First days","Addition of NO GO task","After 2 weeks with both tasks"]



def draw_outcome_patterns():
    data = list(getFromDatabase(query = generateQuery("all_outcomes")))
    df = pd.DataFrame(data=data, columns=["Mouse", "Timestamp", "Delta_time", "Outcome", "Cage"])
    grid = sns.FacetGrid(df, col="Outcome", hue="Outcome")
    grid.map(sns.distplot, "Delta_time", bins=100, kde=False, hist=True, norm_hist=True, kde_kws={"label": "licks"})
    sns.despine()
    plt.xlim(-4, 4)
    # plt.ylim(0, 600)
    plt.tight_layout()
    plt.show()


#//////////////////////////////////////////////////////////////////////////////////////

#draw_facetgrid("single_mouse","counts")
#draw_outcome_patterns()
#draw_parameters()
#draw_single_session()

#??????????????????????????????????????? single outcome ?????????????????????????????????

#specify query in the last lines of the query with mice and outcomes(Notes)
#better use just one outcome, otherwise grid is drawn, remove mouse statement if not necessary
query = """
        SELECT licks.Mouse,licks.`Timestamp`, licks.Delta_time, headfix_trials_summary.Notes,
         headfix_trials_summary.Project_ID,`headfix_trials_summary`.`Task` FROM `licks`
                INNER JOIN `headfix_trials_summary` ON `licks`.`Related_trial` = `headfix_trials_summary`.`Trial start`
                WHERE `headfix_trials_summary`.`Fixation` = "fix" and (
                (Date(`licks`.`Timestamp`) BETWEEN "2018-02-14" and "2018-04-01")
                OR (Date(`licks`.`Timestamp`) BETWEEN "2018-04-23" AND "2018-06-01")
                OR (Date(`licks`.`Timestamp`) BETWEEN "2018-07-24" and "2018-10-24")
                OR (Date(`licks`.`Timestamp`) BETWEEN "2018-11-15" AND "2018-12-20")) 
        AND licks.Delta_time between -5 and 5
         AND `headfix_trials_summary`.`Licks_within_lickwithhold_time` IS NULL
         AND `headfix_trials_summary`.`Notes` IN ("GO=2","GO=-4","GO=-2")
                """
data = list(getFromDatabase(query))
df = pd.DataFrame(data=data, columns=["Mouse", "Timestamp", "Delta_time", "Outcome", "Cage","Task"])
sns.set_style("white")
grid = sns.FacetGrid(df, col="Outcome", hue="Outcome",aspect=2,height=3)
grid.map(sns.distplot, "Delta_time", bins=80, kde=False, hist=True, norm_hist=True, kde_kws={"label": "licks"})

sns.despine()
plt.xlim(-5, 5)
plt.tight_layout()
plt.show()

sns.set(style="ticks", font_scale=2, context="paper")
grid1 = sns.FacetGrid(df,hue="Outcome",aspect=1.5,height=4.5,legend_out=False)
grid1.map(sns.distplot, "Delta_time", bins=100, kde=False, hist=True, norm_hist=False,
          hist_kws={'alpha':0.6}, kde_kws={"label": "licks"}).add_legend(frameon=False)
sns.despine()
plt.xlim(-5, 5)
plt.xlabel("")
plt.tight_layout()
plt.savefig("poollicks.svg", bbox_inches=0, transparent=True)
plt.show()

#AND `headfix_trials_summary`.`Notes` IN ("GO=2","GO=-4","GO=-2")