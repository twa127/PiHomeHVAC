#!/usr/bin/python3
class bc:
    hed = '\033[95m'
    dtm = '\033[0;36;40m'
    ENDC = '\033[0m'
    SUB = '\033[3;30;45m'
    WARN = '\033[0;31;40m'
    grn = '\033[0;32;40m'
    wht = '\033[0;37;40m'
    ylw = '\033[93m'
    fail = '\033[91m'
    blu = '\033[36m'


print(bc.hed + " ")
print(r"    __  __                             _         ")
print(r"   |  \/  |                    /\     (_)        ")
print(r"   | \  / |   __ _  __  __    /  \     _   _ __  ")
print(r"   | |\/| |  / _` | \ \/ /   / /\ \   | | | '__| ")
print(r"   | |  | | | (_| |  >  <   / ____ \  | | | |    ")
print(r"   |_|  |_|  \__,_| /_/\_\ /_/    \_\ |_| |_|    ")
print(" ")
print("             " +bc.SUB + "S M A R T   THERMOSTAT " + bc.ENDC)
print("********************************************************")
print("*           Script Restart Controller Script           *")
print("*            and Detect Multiple Instances.            *")
print("*                Build Date: 12/11/2026                *")
print("*      Version 0.05 - Last Modified 19/11/2026         *")
print("*                                 Have Fun - PiHome.eu *")
print("********************************************************")
print(" ")
print(" " + bc.ENDC)

import os
import sys
import signal
from datetime import datetime
import time
import subprocess
import MySQLdb as mdb
import configparser
import logging
import traceback
import psutil

# Debug print to screen configuration
dbgLevel = 3    # 0-off, 1-info, 2-detailed, 3-all
dbgMsgOut = 1   # 0-disabled, 1-enabled, show details of outgoing messages
dbgMsgIn = 1    # 0-disabled, 1-enabled, show details of incoming messages

# Logging exceptions to log file
logfile = '/var/www/logs/main.log'
infomsg = 'More info in log file: '+logfile
logging.basicConfig( filename=logfile,
                     level=logging.DEBUG,
                     format= ('\n### %(asctime)s - %(levelname)s ###')
                   )

# get status and pid for processes which match a given pattern
def get_pids(args, pattern):

    pids = [[], [], [], []]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, bufsize=1, text=True)
    for line in proc.stdout:
        str = line.rstrip().split()
        if ('python ' + pattern in line or 'python3 ' + pattern in line) and ('S' in line.rstrip().split()[0] or 'Sl' in line.rstrip().split()[0] or 'R' in line.rstrip().split()[0] or 'Rl' in line.rstrip().split()[0] or 'T' in line.rstrip().split()[0]):
            #get the status, pid and last started time values
            pids[0].append(line.rstrip().split()[0])
            pids[1].append(line.rstrip().split()[1])
            pids[2].append(line.rstrip().split()[2] + ' ' + line.rstrip().split()[3] + ' ' + line.rstrip().split()[4] + ' ' + line.rstrip().split()[5] + ' ' + line.rstrip().split()[6])
            pids[3].append(line.rstrip().split()[7])

    return pids

try:
    print( "-" * 75)
    print(bc.dtm + time.ctime() + bc.ENDC + ' - Check Controller Script Started')
    print( "-" * 75)

    # Initialise the database access variables
    config = configparser.ConfigParser()
    config.read("/var/www/st_inc/db_config.ini")
    dbhost = config.get("db", "hostname")
    dbuser = config.get("db", "dbusername")
    dbpass = config.get("db", "dbpassword")
    dbname = config.get("db", "dbname")

    con = mdb.connect(dbhost, dbuser, dbpass, dbname)
    cur = con.cursor()

    search_pattern = '/var/www/cron/controller.py'
    ps_cmd = ["ps", "-eo", "stat,pid,lstart,etimes,cmd","--sort=start_time"]

    pids = []

    #search for running process by name
    pids = get_pids(ps_cmd, search_pattern)
    nopids = len(pids[0])
    if nopids == 0: #not running
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Python Controller Script is ' + bc.fail + 'NOT ' + bc.ENDC + 'Running')
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Starting Python Controller Script')
            os.system('nohup python3 /var/www/cron/controller.py >/dev/null 2>&1 &')

            # loop waiting for process to start
            cnt = 0
            while nopids == 0 and cnt < 10:
                pids = get_pids(ps_cmd, search_pattern)
                nopids = len(pids[0])
                cnt = cnt + 1

            if nopids == 1: # now running
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Script Started, the PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                qry = "UPDATE system_controller SET pid = '" + str(pids[1])[2 : -2] + "', pid_running_since = '" + str(pids[2])[2 : -2] + "' LIMIT 1"
                try:
                    cur.execute(qry)
                    con.commit()
                except mdb.Error as e:
                    # skip deadlock error (being caused when mysqldunp runs
                    if e.args[0] == 1213:
                        pass
                    else:
                        print("DB Error %d: %s" % (e.args[0], e.args[1]))
                        print(traceback.format_exc())
                        logging.error(e)
                        logging.info(traceback.format_exc())
                        conn.close()
                        print(infomsg)
                        sys.exit(1)
                qry = """INSERT INTO `controller_zone_logs`(`sync`, `purge`, `zone_id`, `start_datetime`, `start_cause`, `stop_datetime`, `stop_cause`, `expected_end_date_time`)
                      VALUES (0,0,0,CURRENT_TIMESTAMP(),'Controller Script Started',NULL,'',NULL);"""
                try:
                    cur.execute(qry)
                    con.commit()
                except mdb.Error as e:
                    # skip deadlock error (being caused when mysqldunp runs
                    if e.args[0] == 1213:
                        pass
                    else:
                        print("DB Error %d: %s" % (e.args[0], e.args[1]))
                        print(traceback.format_exc())
                        logging.error(e)
                        logging.info(traceback.format_exc())
                        conn.close()
                        print(infomsg)
                        sys.exit(1)
            else:
                print(bc.dtm + time.ctime() + bc.fail + ' - The Script Failed to Start' + bc.ENDC)
    else: #at least 1 copy running
        if nopids > 1: #multiple copies are running
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Multiple Controller Scripts Detected')
                # check for terminated pids pids[0] will be 'T'
                scripts_killed = 0
                stat = 0
                for pid in pids[1]:
                    if 'T' in pids[0][stat]:
                        os.kill(int(pid), signal.SIGKILL) #or signal.SIGTERM
                        scripts_killed = scripts_killed + 1
                        # wait for scripts to die
                        cnt = 0
                        while psutil.pid_exists(int(pid)) and cnt < 100:
                            cnt = cnt + 1
                    stat = stat + 1

                if scripts_killed != 0:
                        print(bc.dtm + time.ctime() + bc.ENDC + ' - Number of Terminated Scripts Killed: ' + bc.grn + str(scripts_killed) + bc.ENDC)
                if nopids - scripts_killed > 1 or nopids - scripts_killed == 0: # Proceed if none or more than one script runs
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Multiple Active Controller Scripts Are Running')
                    # loop killing each pid in turn except the oldest
                    pids = get_pids(ps_cmd, search_pattern)
                    scrpts_killed = 0
                    pid_num = 0
                    for pid in pids[1]:
                        if pid_num > 0:
                            os.kill(int(pid), signal.SIGTERM) #or signal.SIGKILL
                            # wait for scripts to die
                            cnt = 0
                            while psutil.pid_exists(int(pid)) and cnt < 100:
                                cnt = cnt + 1
                            scrpts_killed = scrpts_killed + 1
                        pid_num = pid_num + 1
                    print(bc.dtm + time.ctime() + bc.fail + ' - ' + str(scrpts_killed) + ' Scripts Killed' + bc.ENDC)
                    # verify that we still have 1 script running and if not start a new one
                    pids = get_pids(ps_cmd, search_pattern)
                    nopids = len(pids[0])
                    if nopids == 1: # now running
                        print(bc.dtm + time.ctime() + bc.ENDC + ' - Script Running, the PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                    else :
                        print(bc.dtm + time.ctime() + bc.fail + ' - ALL Scripts Killed, Starting New' + bc.ENDC)
                        os.system('nohup python3 /var/www/cron/controller.py >/dev/null 2>&1 &')
                        # loop waiting for process to start
                        cnt = 0
                        nopids = 0
                        while nopids == 0 and cnt < 10:
                            pids = get_pids(ps_cmd, search_pattern)
                            nopids = len(pids[0])
                            cnt = cnt + 1
                        if nopids == 1:
                            print(bc.dtm + time.ctime() + bc.ENDC + ' - Script Started, the PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                            qry = "UPDATE system_controller SET pid = '" + str(pids[1])[2 : -2] + "', pid_running_since = '" + str(pids[2])[2 : -2] + "' LIMIT 1"
                            try:
                                cur.execute(qry)
                                con.commit()
                            except mdb.Error as e:
                                # skip deadlock error (being caused when mysqldunp runs
                                if e.args[0] == 1213:
                                    pass
                                else:
                                    print("DB Error %d: %s" % (e.args[0], e.args[1]))
                                    print(traceback.format_exc())
                                    logging.error(e)
                                    logging.info(traceback.format_exc())
                                    conn.close()
                                    print(infomsg)
                                    sys.exit(1)
                        else:
                            print(bc.dtm + time.ctime() + bc.fail + ' - The Script Failed to Start' + bc.ENDC)
                else:
                    pids = get_pids(ps_cmd, search_pattern)
                    for pid in pids[1]:
                        print(bc.dtm + time.ctime() + bc.ENDC + ' - Script Running, the PID is: ' + bc.grn + pid + bc.ENDC)
        else:
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Python Controller Script is ' + bc.grn + 'Running' + bc.ENDC)
            print(bc.dtm + time.ctime() + bc.ENDC + ' - The PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)

    if con.open:
        con.close()

    print( "-" * 75)
    print(bc.dtm + time.ctime() + bc.ENDC + ' - Check Controller Script Ended')
    print( "-" * 75)

except configparser.Error as e:
    print("ConfigParser:", format(e))
    print(traceback.format_exc())
    logging.error(e)
    logging.info(traceback.format_exc())
except mdb.Error as e:
    print("DB Error %d: %s" % (e.args[0], e.args[1]))
    print(traceback.format_exc())
    logging.error(e)
    logging.info(traceback.format_exc())
except TypeError as e:
    print("TypeError:", format(e))
    print(traceback.format_exc())
    logging.error(e)
    logging.info(traceback.format_exc())
except Exception as e:
    print(format(e))
    print(traceback.format_exc())
    logging.error(e)
    logging.info(traceback.format_exc())
except ProgramKilled as e:
    print(format(e))
    print(traceback.format_exc())
    logging.error(e)
    logging.info(traceback.format_exc())
finally:
    if con.open:
        con.close()
    print(infomsg)
    sys.exit(1)
