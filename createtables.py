import pymysql
from password import database_password as DBpwd
from password import database_user as DBuser
from password import database_host as DBhost
from password import database as DB

def saveToDatabase(query):
    db1 = pymysql.connect(host=DBhost, user=DBuser, db=DB, password=DBpwd)
    cur1 = db1.cursor()
    try:
        cur1.execute(query)
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

query="""
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `clusters_kde`
--

DROP TABLE IF EXISTS `clusters_kde`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clusters_kde` (
  `Bandwidth` int(4) NOT NULL,
  `Threshold` float NOT NULL,
  `session_count` int(3) NOT NULL,
  `mice_count` int(3) NOT NULL,
  `cluster_duration` float(8,2) NOT NULL,
  `session_time_sum` float(9,2) NOT NULL,
  `delta_time_sum` float(9,2) DEFAULT NULL,
  `max_delta` float(8,2) DEFAULT NULL,
  `gap_length` float(8,2) NOT NULL,
  `timestamp_start` timestamp(2) NULL DEFAULT NULL,
  `cage` varchar(3) NOT NULL DEFAULT 'all',
  `day` int(5) NOT NULL,
  `day_or_night` varchar(5) NOT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Bandwidth` (`Bandwidth`,`Threshold`,`timestamp_start`)
) ENGINE=InnoDB AUTO_INCREMENT=4516 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `early_days_logbook_group4`
--

DROP TABLE IF EXISTS `early_days_logbook_group4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `early_days_logbook_group4` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date DEFAULT NULL,
  `Type` varchar(100) DEFAULT NULL,
  `Event` varchar(100) DEFAULT NULL,
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `entries`
--

DROP TABLE IF EXISTS `entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `entries` (
  `Project_ID` int(3) NOT NULL,
  `Mouse` varchar(20) NOT NULL,
  `Timestamp` timestamp(2) NOT NULL DEFAULT '0000-00-00 00:00:00.00',
  `Duration` float(7,2) NOT NULL,
  `Trial or Entry` varchar(5) NOT NULL,
  `Headfix duration` float(5,2) DEFAULT NULL,
  `Licks` int(11) DEFAULT NULL,
  `Licks_while_headfixed` int(11) DEFAULT NULL,
  `Last Mouse` varchar(20) NOT NULL,
  `Time after last Mouse exits` float(8,2) DEFAULT NULL,
  `Last mouse headfixed` varchar(18) DEFAULT NULL,
  `Time since last headfix` float(8,2) DEFAULT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=282102 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `headfix_trials_summary`
--

DROP TABLE IF EXISTS `headfix_trials_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `headfix_trials_summary` (
  `Project_ID` int(3) NOT NULL,
  `Mouse` varchar(18) DEFAULT NULL,
  `Fixation` varchar(6) NOT NULL,
  `Trial start` timestamp(2) NULL DEFAULT NULL,
  `Trial in session` int(3) DEFAULT NULL,
  `Licks_within_lickwithhold_time` varchar(4) DEFAULT NULL,
  `Lickwithhold time` float(4,2) NOT NULL,
  `Task` varchar(100) NOT NULL,
  `Outcome` varchar(100) NOT NULL,
  `Reward earned` varchar(5) NOT NULL,
  `Licks to trigger reward` int(11) DEFAULT NULL,
  `Delay till reward` float(4,2) DEFAULT NULL,
  `Reaction time` float(4,2) DEFAULT NULL,
  `Licks after reward` int(11) DEFAULT NULL,
  `Lick duration after reward` float(4,2) DEFAULT NULL,
  `Licks after stimulus` int(11) NOT NULL,
  `Lick duration after stimulus` float(4,2) NOT NULL,
  `Trial duration` float(4,2) DEFAULT NULL,
  `Headfix duration at stimulus` float(4,2) DEFAULT NULL,
  `Notes` varchar(1000) DEFAULT NULL,
  `Videofile` varchar(200) DEFAULT NULL,
  `Stimulus` varchar(200) DEFAULT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Trial start` (`Trial start`)
) ENGINE=InnoDB AUTO_INCREMENT=326519 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `interaction_clusters`
--

DROP TABLE IF EXISTS `interaction_clusters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interaction_clusters` (
  `quantile` float(7,3) NOT NULL,
  `gap_threshold` float(9,3) NOT NULL,
  `session_count` int(3) NOT NULL,
  `mice_count` int(3) NOT NULL,
  `cluster_duration` float(8,2) NOT NULL,
  `session_time_sum` float(9,2) NOT NULL,
  `delta_time_sum` float(9,2) DEFAULT NULL,
  `max_delta` float(9,2) DEFAULT NULL,
  `gap_length` float(8,2) NOT NULL,
  `timestamp_start` timestamp(2) NULL DEFAULT NULL,
  `cage` varchar(3) NOT NULL DEFAULT 'all',
  `day` int(5) NOT NULL,
  `day_or_night` varchar(5) NOT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `quantile` (`quantile`,`gap_threshold`,`timestamp_start`,`cage`,`day`)
) ENGINE=InnoDB AUTO_INCREMENT=1083691 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `interaction_clusters_summary`
--

DROP TABLE IF EXISTS `interaction_clusters_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interaction_clusters_summary` (
  `Quantile` float(6,3) NOT NULL,
  `AVG_sessions` float(8,2) NOT NULL,
  `STD_sessions` float(8,2) NOT NULL,
  `AVG_mice` float(4,2) NOT NULL,
  `STD_mice` float(4,2) NOT NULL,
  `AVG_duration` float(8,2) NOT NULL,
  `STD_duration` float(8,2) NOT NULL,
  `AVG_gap` float(8,2) NOT NULL,
  `STD_gap` float(8,2) NOT NULL,
  `threshold_gap` float(9,3) NOT NULL,
  `cage` varchar(3) NOT NULL,
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Quantile` (`Quantile`,`threshold_gap`,`cage`)
) ENGINE=InnoDB AUTO_INCREMENT=301 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `licks`
--

DROP TABLE IF EXISTS `licks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `licks` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Mouse` varchar(18) NOT NULL,
  `Timestamp` timestamp(2) NULL DEFAULT NULL,
  `Related_trial` timestamp(2) NULL DEFAULT NULL,
  `Delta_time` float(4,2) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Mouse` (`Mouse`,`Timestamp`,`Related_trial`,`Delta_time`)
) ENGINE=InnoDB AUTO_INCREMENT=5959060 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `major_dates_headfix_projects`
--

DROP TABLE IF EXISTS `major_dates_headfix_projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `major_dates_headfix_projects` (
  `Project` int(11) NOT NULL,
  `Start date` date DEFAULT NULL,
  `Buzzer & auditory feedback added` date DEFAULT NULL,
  `Start loose headfixation` date DEFAULT NULL,
  `Start full headfixation` date DEFAULT NULL,
  `Start GO task` date DEFAULT NULL COMMENT 'licking response required',
  `Start NO GO task` date DEFAULT NULL,
  `End date` date DEFAULT NULL,
  PRIMARY KEY (`Project`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mice_autoheadfix`
--

DROP TABLE IF EXISTS `mice_autoheadfix`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mice_autoheadfix` (
  `Mouse` varchar(18) NOT NULL,
  `Genotype` varchar(20) NOT NULL DEFAULT 'Ai94-GCaMP6s',
  `Sex` varchar(6) NOT NULL DEFAULT 'male',
  `Date of Recruitment` date NOT NULL DEFAULT '2017-06-30',
  `Start weight` float DEFAULT NULL,
  `cage` int(3) NOT NULL DEFAULT '1',
  `Critical weight` float DEFAULT NULL,
  `Date of retirement` date DEFAULT NULL,
  `Reason_for_retirement` varchar(20) DEFAULT NULL,
  `Activity` varchar(10) NOT NULL DEFAULT 'good',
  `Alive` varchar(3) NOT NULL DEFAULT 'no',
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`Mouse`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `rewards`
--

DROP TABLE IF EXISTS `rewards`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rewards` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Mouse` varchar(18) NOT NULL,
  `Timestamp` timestamp(2) NULL DEFAULT NULL,
  `Reward_type` varchar(10) NOT NULL,
  `Related_trial` timestamp(2) NULL DEFAULT NULL,
  `Related_entry` timestamp(2) NULL DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`)
) ENGINE=InnoDB AUTO_INCREMENT=282382 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `summary_stats`
--

DROP TABLE IF EXISTS `summary_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `summary_stats` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Mouse` varchar(18) NOT NULL,
  `Entries/Day` float NOT NULL,
  `Entry_Duration/Day` float NOT NULL,
  `Fix_Duration/Day` float NOT NULL,
  `Fixes/Day` float NOT NULL,
  `Licks/Day` float NOT NULL,
  `Days_referred` int(3) NOT NULL,
  `Cage` int(2) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `textfilesgroup1`
--

DROP TABLE IF EXISTS `textfilesgroup1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `textfilesgroup1` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(18) DEFAULT NULL,
  `Timestamp` timestamp(3) NULL DEFAULT NULL,
  `Event` varchar(100) NOT NULL,
  `Project_ID` int(11) NOT NULL DEFAULT '1',
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`,`Event`)
) ENGINE=InnoDB AUTO_INCREMENT=2911494 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `textfilesgroup2`
--

DROP TABLE IF EXISTS `textfilesgroup2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `textfilesgroup2` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(18) DEFAULT NULL,
  `Timestamp` timestamp(3) NULL DEFAULT NULL,
  `Event` varchar(200) NOT NULL,
  `Project_ID` int(11) NOT NULL DEFAULT '2',
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`,`Event`)
) ENGINE=InnoDB AUTO_INCREMENT=1615999 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `textfilesgroup3`
--

DROP TABLE IF EXISTS `textfilesgroup3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `textfilesgroup3` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(18) DEFAULT NULL,
  `Timestamp` timestamp(3) NULL DEFAULT NULL,
  `Event` varchar(200) NOT NULL,
  `Project_ID` int(11) NOT NULL DEFAULT '3',
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`,`Event`)
) ENGINE=InnoDB AUTO_INCREMENT=1131357 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `textfilesgroup4`
--

DROP TABLE IF EXISTS `textfilesgroup4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `textfilesgroup4` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(18) DEFAULT NULL,
  `Timestamp` timestamp(3) NULL DEFAULT NULL,
  `Event` varchar(200) NOT NULL,
  `Project_ID` int(11) NOT NULL DEFAULT '4',
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`,`Event`)
) ENGINE=InnoDB AUTO_INCREMENT=969389 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `textfilesgroup5`
--

DROP TABLE IF EXISTS `textfilesgroup5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `textfilesgroup5` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(18) DEFAULT NULL,
  `Timestamp` timestamp(3) NULL DEFAULT NULL,
  `Event` varchar(200) NOT NULL,
  `Project_ID` int(11) NOT NULL DEFAULT '5',
  `Notes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Timestamp` (`Timestamp`,`Event`)
) ENGINE=InnoDB AUTO_INCREMENT=191006 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `videos_list`
--

DROP TABLE IF EXISTS `videos_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `videos_list` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Videofile` varchar(100) NOT NULL,
  `Session start` timestamp(2) NULL DEFAULT NULL,
  `LED_on` timestamp(2) NULL DEFAULT NULL,
  `LED_off` timestamp(2) NULL DEFAULT NULL,
  `Fixation` varchar(6) NOT NULL,
  `Mouse` varchar(18) NOT NULL,
  `Notes` varchar(1000) NOT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `Session start` (`Session start`)
) ENGINE=InnoDB AUTO_INCREMENT=90961 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weights_cage1`
--

DROP TABLE IF EXISTS `weights_cage1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weights_cage1` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `2016080026` float DEFAULT NULL,
  `210608298` float DEFAULT NULL,
  `210608315` float DEFAULT NULL,
  `2016088466` float DEFAULT NULL,
  `201608468` float DEFAULT NULL,
  `201608481` float DEFAULT NULL,
  `201609114` float DEFAULT NULL,
  `201609124` float DEFAULT NULL,
  `201609136` float DEFAULT NULL,
  `201609336` float DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weights_cage3`
--

DROP TABLE IF EXISTS `weights_cage3`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weights_cage3` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `2016090985` float DEFAULT NULL,
  `2016090797` float DEFAULT NULL,
  `2016090629` float DEFAULT NULL,
  `2016090964` float DEFAULT NULL,
  `2016090965` float DEFAULT NULL,
  `2016090647` float DEFAULT NULL,
  `2016090882` float DEFAULT NULL,
  `2016091183` float DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weights_cage4`
--

DROP TABLE IF EXISTS `weights_cage4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weights_cage4` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `201608252` float NOT NULL,
  `201608252 add water` float NOT NULL,
  `201608474` float NOT NULL,
  `201608474 add water` float NOT NULL,
  `2016080009` float DEFAULT NULL,
  `2016080009 add water` float DEFAULT NULL,
  `2016080104` float DEFAULT NULL,
  `2016080104 add water` float DEFAULT NULL,
  `201608423` float NOT NULL,
  `201608423 add water` float NOT NULL,
  `2016080250` float NOT NULL,
  `2016080250 add water` float NOT NULL,
  `2016080008` float DEFAULT NULL,
  `2016080008 add water` float DEFAULT NULL,
  `2016080242` float DEFAULT NULL,
  `2016080242 add water` float DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weights_cage5`
--

DROP TABLE IF EXISTS `weights_cage5`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weights_cage5` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date NOT NULL,
  `Mouse` varchar(18) NOT NULL,
  `baseline_percent` float(4,1) DEFAULT NULL,
  `change_to_yesterday` float(2,1) DEFAULT NULL,
  `manual_control` float(3,1) DEFAULT NULL,
  `additional_water` float(2,1) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=441 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;"""