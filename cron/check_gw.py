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
print("*             Script Restart Gateway Script            *")
print("*             and Detect Multiple Instances.           *")
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
        if ('python ' + pattern in line or 'python3 ' + pattern in line) and ('Sl' in line.rstrip().split()[0] or 'S+' in line.rstrip().split()[0] or 'Rl' in line.rstrip().split()[0] or 'R+' in line.rstrip().split()[0] or 'T' in line.rstrip().split()[0]):
            #get the status, pid, started time and elapse time values
            pids[0].append(line.rstrip().split()[0])
            pids[1].append(line.rstrip().split()[1])
            pids[2].append(line.rstrip().split()[2] + ' ' + line.rstrip().split()[3] + ' ' + line.rstrip().split()[4] + ' ' + line.rstrip().split()[5] + ' ' + line.rstrip().split()[6])
            pids[3].append(line.rstrip().split()[7])

    return pids

try:
    print( "-" * 75)
    print(bc.dtm + time.ctime() + bc.ENDC + ' - Check Gateway Script Started')
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

    search_pattern = '/var/www/cron/gateway.py'
    ps_cmd = ["ps", "-eo", "stat,pid,lstart,etimes,cmd","--sort=start_time"]

    qry = "SELECT * FROM gateway order by id asc LIMIT 1;"
    cur.execute(qry)
    result = cur.fetchone()
    gateway_to_index = dict(
        (d[0], i) for i, d in enumerate(cur.description)
    )
    gw_status = result[gateway_to_index["status"]]
    gw_type = result[gateway_to_index["type"]]
    gw_location = result[gateway_to_index["location"]]
    gw_port = result[gateway_to_index["port"]]
    gw_pid = result[gateway_to_index["pid"]]
    gw_reboot = result[gateway_to_index["reboot"]]
    find_gw = result[gateway_to_index["find_gw"]]

    #if status set to 0 then check if gateway PID is running and if found then kill
    if gw_status == '0':
        pids = get_pids(ps_cmd, search_pattern)
        nopids = len(pids[0])
        if nopids > 1:
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Gateway Script Running, the PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Stopping Python Gateway Script')
            for pid in pids[1]:
                os.kill(int(pid), signal.SIGTERM) #or signal.SIGKILL
        else:
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Gateway is DISABLED')
    else:
        #if reboot set to 1 then kill gateway PID and set reboot status to 0
        if gw_reboot == '1' or gw_status == '0':
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Stopping Python Gateway Script')
            for pid in pids[1]:
                os.kill(int(pid), signal.SIGTERM) #or signal.SIGKILL
                qry = "UPDATE gateway SET reboot = '0' LIMIT 1;"
                try:
                    cur.execute(qry)
                    con.commit()
                except mdb.Error as e:
                    if e.args[0] == 1020:
                        pass
                    else:
                        print("DB Error %d: %s" % (e.args[0], e.args[1]))
                        print(traceback.format_exc())
                        logging.error(e)
                        logging.info(traceback.format_exc())
                        conn.close()
                        print(infomsg)
                        sys.exit(1)
        print( "-" * 75)
        #if find_gw set to 1 then start the search script and set find_gw to 0
        if find_gw == '1':
            if gw_type == 'wifi':
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Checking Python Script Status to Find Smart Home Gateway')
                pids = get_pids(ps_cmd, '/var/www/cron/find_mygw/find_mygw.py')
                nopids = len(pids[0])
                if nopids == 0:
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Search for Smart Home Gateway is ' + bc.fail + 'NOT ' + bc.ENDC + 'Running')
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Starting Search for Smart Home Gateway')
                    os.system('nohup python3 /var/www/cron/find_mygw/find_mygw.py >/dev/null 2>&1 &')
                    pids = get_pids(ps_cmd, '/var/www/cron/find_mygw/find_mygw.py')
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Search Script Started on PID: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                else:
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Search for Smart Home Gateway ' + bc.green + 'Running ' + bc.ENDC )
                    pids = get_pids(ps_cmd, '/var/www/cron/find_mygw/find_mygw.py')
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Search Script Started on PID: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Search Script Running Since: ' + bc.grn + str(pids[2])[2 : -2] + bc.ENDC)

            qry = "UPDATE gateway SET find_gw = '0' LIMIT 1;"
            try:
                cur.execute(qry)
                con.commit()
            except mdb.Error as e:
                if e.args[0] == 1020:
                    pass
                else:
                    print("DB Error %d: %s" % (e.args[0], e.args[1]))
                    print(traceback.format_exc())
                    logging.error(e)
                    logging.info(traceback.format_exc())
                    conn.close()
                    print(infomsg)
                    sys.exit(1)


        #Check Gateway Logs for last 10 minutes and start search for gateway if connected failed.
        qry = "SELECT count(*) as cnt FROM gateway_logs WHERE pid_datetime >= DATE_SUB(NOW(), INTERVAL 10 MINUTE);";
        cur.execute(qry)
        result = cur.fetchone()
        gl_cnt = result[0]
        if gl_cnt > 0:
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Gateway Connection Lost in Last 10 minutes: ' + bc.grn + str( gl_cnt) + bc.ENDC)
        if gl_cnt >= 8 and gw_type == 'wifi':
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Gateway Connection Lost in Last 10 minutes: ' + bc.grn + str( gl_cnt) + bc.ENDC)
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Checking Python Script Status to Find Smart Home Gateway')
            #Check if Search Script already started
            pids = get_pids(ps_cmd, '/var/www/cron/find_mygw/find_mygw.py')
            nopids = len(pids[0])
            if nopids == 0:
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Search for Smart Home Gateway is ' + bc.fail + 'NOT ' + bc.ENDC + 'Running')
                #If Search script isnt started set to database one
                qry = "UPDATE gateway SET find_gw = '1' LIMIT 1;"
                try:
                    cur.execute(qry)
                    con.commit()
                except mdb.Error as e:
                    if e.args[0] == 1020:
                        pass
                    else:
                        print("DB Error %d: %s" % (e.args[0], e.args[1]))
                        print(traceback.format_exc())
                        logging.error(e)
                        logging.info(traceback.format_exc())
                        conn.close()
                        print(infomsg)
                        sys.exit(1)
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Gateway Search Status set to 1')
                print( "-" * 75)

    pids = []
    #search for running process by name
    pids = get_pids(ps_cmd, search_pattern)
    nopids = len(pids[0])
    if nopids == 1:
        elapse_time = int(str(pids[3])[2 : -2])
    else:
        elapse_time = 0
#    print(nopids)
#    print(str(pids[2]))
#    print(str(pids[3]))
#    print(str(elapse_time))
    if nopids == 0 and elapse_time < 10: #not running
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Python Gateway Script is ' + bc.fail + 'NOT ' + bc.ENDC + 'Running')
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Starting Python Gateway Script')
            os.system('nohup python3 /var/www/cron/gateway.py >/dev/null 2>&1 &')

            # loop waiting for process to start
            cnt = 0
            while nopids == 0 and cnt < 10:
                pids = get_pids(ps_cmd, search_pattern)
                nopids = len(pids[0])
                cnt = cnt + 1

            if nopids == 1: # now running
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Script Started, the PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                qry = "UPDATE gateway SET pid = '" + str(pids[1])[2 : -2] + "', pid_running_since = '" + str(pids[2])[2 : -2] + "' LIMIT 1;"
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
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                qry = """INSERT INTO gateway_logs (`sync`, `purge`, type, location, port, pid, pid_start_time, pid_datetime, mqtt_disconnect, mqtt_sent, mqtt_recv, mysensors_sent,
                         mysensors_recv, gpio_sent, gpio_recv, heartbeat)
                         VALUES ({}, {}, '{}', '{}', '{}', '{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, '{}');""".format(
                         0, 0, gw_type, gw_location, gw_port, str(pids[1])[2 : -2], str(pids[2])[2 : -2], timestamp, 0, 0, 0, 0, 0, 0, 0, timestamp
                         )
                try:
                    cur.execute(qry)
                    con.commit()
                except mdb.Error as e:
                    if e.args[0] == 1020:
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
                print(bc.dtm + time.ctime() + bc.ENDC + ' - Multiple Gateway Scripts Detected')
                # check for terminated pids pids[0] will be 'T'
                scripts_killed = 0
                stat = 0
                for pid in pids[1]:
                    if 'T' in pids[0][stat]:
                        os.kill(int(pid), signal.SIGKILL) #or signal.SIGKILL
                        scripts_killed = scripts_killed + 1
                        # wait for scripts to die
                        cnt = 0
                        while psutil.pid_exists(int(pid)) and cnt < 100:
                            cnt = cnt + 1
                    stat = stat + 1

                if scripts_killed != 0:
                        print(bc.dtm + time.ctime() + bc.ENDC + ' - Number of Terminated Scripts Killed: ' + bc.grn + str(scripts_killed) + bc.ENDC)
                if nopids - scripts_killed > 1 or nopids - scripts_killed == 0: # Proceed if none or more than one script runs
                    print(bc.dtm + time.ctime() + bc.ENDC + ' - Multiple Active Gateway Scripts Are Running')
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
                    print(bc.dtm + time.ctime() + bc.fail + ' - ' + str(scrpts_killed) + ' Running Scripts Killed' + bc.ENDC)
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
                        while len(pids[0]) == 0 and cnt < 10:
                            pids = get_pids(ps_cmd, search_pattern)
                            cnt = cnt + 1
                        if nopids == 1:
                            print(bc.dtm + time.ctime() + bc.ENDC + ' - Script Started, the PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)
                            qry = "UPDATE gateway SET pid = '" + str(pids[1])[2 : -2] + "', pid_running_since = '" + str(pids[2])[2 : -2] + "' LIMIT 1"
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
            print(bc.dtm + time.ctime() + bc.ENDC + ' - Python Gateway Script is ' + bc.grn + 'Running' + bc.ENDC)
            print(bc.dtm + time.ctime() + bc.ENDC + ' - The PID is: ' + bc.grn + str(pids[1])[2 : -2] + bc.ENDC)

    if con.open:
        con.close()

    print( "-" * 75)
    print(bc.dtm + time.ctime() + bc.ENDC + ' - Check Gateway Script Ended')
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
