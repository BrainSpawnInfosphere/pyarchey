#!/usr/bin/env python
#
#
# pyarchey is a simple system information tool written in Python.
#
# Copyright 2010 Melik Manukyan <melik@archlinux.us>
# Copyright 2010 David Vazgenovich Shakaryan <dvshakaryan@gmail.com>
#
# ASCII art by Brett Bohnenkamper <kittykatt@silverirc.com>
# Changes Jerome Launay <jerome@projet-libre.org>
# Fedora support by YeOK <yeok@henpen.org>
#
# Distributed under the terms of the GNU General Public License v3.
# See http://www.gnu.org/licenses/gpl.txt for the full license text.
##############################################################################
#
#


# For more info on psutil, see https://pythonhosted.org/psutil/
#

# Import libraries
import os                               # fileCheck, tries to determine distribution
import re                               # used by CPU
from subprocess import Popen, PIPE      # call commandline programs
from sys import platform as _platform   # distribution
import socket                           # ip address
import psutil as ps                     # system info
import datetime as dt                   # uptime
import json                             # json
import argparse                         # handle command line args
import math

#---------------Dictionaries---------------#
#  https://wiki.archlinux.org/index.php/Color_Bash_Prompt
# escape[ x;y   x-{0 normal 1 bold} y-color
CLR="\033[0;0m"   # normal color scheme
BK ="\033[0;30m"   # black
BL ="\033[0;34m"   # blue
GR ="\033[0;32m"   # green
CY ="\033[0;36m"   # cyan
RD ='\033[0;31m'   # red
PL ="\033[0;35m"   # purple
BR ="\033[0;33m"   # brown
GY ="\033[0;30m"   # grey
LG ="\033[0;37m"   # light grey

# Bold colors (note be 'B' before the color name)
BBK ="\033[1;30m"   # black
BBL ="\033[1;34m"   # blue
BGR ="\033[1;32m"   # green
BCY ="\033[1;36m"   # cyan
BRD ='\033[1;31m'   # red
BPL ="\033[1;35m"   # purple
BBR ="\033[1;33m"   # brown
BGY ="\033[1;30m"   # grey
BLG ="\033[1;37m"   # light grey

colorDict = {
    'Arch Linux':       [BL, BBL],
    'Ubuntu':           [RD, BRD, BBR],
    'FreeBSD':          [RD, BRD, BR],
    'Mac OSX':          [CLR, CY],
    'Debian':           [RD, BRD],
    'Raspbian':         [RD, BRD],
    'LinuxMint':        [BLG, BGR],
    'CrunchBang':       [BLG,BLG],
    'Fedora':           [BLG, BBL, BL],
    'openSUSE project': [BLG, BGR],
    'Slackware':        [BLG, BL, BBL],
    'Linux':            [CLR],
    'Sensors':          [BRD, BGR, BBR],
    'Clear':            [CLR]
    }

logosDict = {'Arch Linux': '''{color[1]}
{color[1]}               +                {results[0]}
{color[1]}               #                {results[1]}
{color[1]}              ###               {results[2]}
{color[1]}             #####              {results[3]}
{color[1]}             ######             {results[4]}
{color[1]}            ; #####;            {results[5]}
{color[1]}           +##.#####            {results[6]}
{color[1]}          +##########           {results[7]}
{color[1]}         ######{color[0]}#####{color[1]}##;         {results[8]}
{color[1]}        ###{color[0]}############{color[1]}+        {results[9]}
{color[1]}       #{color[0]}######   #######        {results[10]}
{color[0]}     .######;     ;###;`\".      {results[11]}
{color[0]}    .#######;     ;#####.       {results[12]}
{color[0]}    #########.   .########`
{color[0]}   ######'           '######
{color[0]}  ;####                 ####;
{color[0]}  ##'                     '##
{color[0]} #'                         `#
\x1b[0m'''
,'FreeBSD':'''{color[0]}
{color[0]}  ```                        `    {results[0]}
{color[0]} s` `.....---.......--.```   -/   {results[1]}
{color[0]} +o   .--`         /y:`      +.   {results[2]}
{color[0]}  yo`:.            :o      `+-    {results[3]}
{color[0]}   y/               -/`   -o/     {results[4]}
{color[0]}  .-                  ::/sy+:.    {results[5]}
{color[0]}  /                     `--  /    {results[6]}
{color[0]} `:                          :`   {results[7]}
{color[0]} `:                          :`   {results[8]}
{color[0]}  /                          /    {results[9]}
{color[0]}  .-                        -.    {results[10]}
{color[0]}   --                      -.     {results[11]}
{color[0]}    `:`                  `:`      {results[12]}
{color[0]}      .--             `--.
{color[0]}         .---.....----.
{color[0]}
{color[0]}
{color[0]}
\x1b[0m'''
,'Debian':'''{color[0]}
{color[1]}           _sudZUZ#Z#XZo=_        {results[0]}
{color[1]}        _jmZZ2!!~---~!!X##wx      {results[1]}
{color[1]}     .<wdP~~            -!YZL,    {results[2]}
{color[1]}    .mX2'       _xaaa__     XZ[.  {results[3]}
{color[1]}    oZ[      _jdXY!~?S#wa   ]Xb;  {results[4]}
{color[1]}   _#e'     .]X2(     ~Xw|  )XXc  {results[5]}
{color[1]}  .2Z`      ]X[.       xY|  ]oZ(  {results[6]}
{color[1]}  .2#;      )3k;     _s!~   jXf`  {results[7]}
{color[0]}   1Z>      -]Xb/    ~    __#2(   {results[8]}
{color[0]}   -Zo;       +!4ZwerfgnZZXY'     {results[9]}
{color[0]}    *#[,        ~-?!!!!!!-~       {results[10]}
{color[0]}     XUb;.                        {results[11]}
{color[0]}      )YXL,,                      {results[12]}
{color[0]}        +3#bc,
{color[0]}          -)SSL,,
{color[0]}             ~~~~~
\x1b[0m'''
,'Raspbian':'''{color[0]}
{color[0]}        .~~.   .~~.      {results[0]}
{color[0]}       '. \ ' ' / .'     {results[1]}
{color[0]}        .~ .~~~..~.      {results[2]}
{color[0]}       : .~.'~'.~. :     {results[3]}
{color[0]}      ~ (   ) (   ) ~    {results[4]}
{color[0]}     ( : '~'.~.'~' : )   {results[5]}
{color[0]}      ~ .~ (   ) ~. ~    {results[6]}
{color[0]}       (  : '~' :  )     {results[7]}
{color[0]}        '~ .~~~. ~'      {results[8]}
{color[0]}            '~'          {results[9]}
{color[0]}                         {results[10]}
{color[0]}                         {results[11]}
{color[0]}                         {results[12]}
\x1b[0m'''
,'Ubuntu':'''{color[0]}
{color[0]}                          .oyhhs:   {results[0]}
{color[1]}                 ..--.., {color[0]}shhhhhh-   {results[1]}
{color[1]}               -+++++++++`:{color[0]}yyhhyo`  {results[2]}
{color[2]}          .--  {color[1]}-++++++++/-.-{color[0]}::-`    {results[3]}
{color[2]}        .::::-   {color[1]}:-----:/+++/++/.   {results[4]}
{color[2]}       -:::::-.          {color[1]}.:++++++:  {results[5]}
{color[1]}  ,,, {color[2]}.:::::-`             {color[1]}.++++++- {results[6]}
{color[1]}./+++/-{color[2]}`-::-                {color[1]}./////: {results[7]}
{color[1]}+++++++ {color[2]}.::-                        {results[8]}
{color[1]}./+++/-`{color[2]}-::-                {color[0]}:yyyyyo {results[9]}
{color[1]}  ``` `{color[2]}-::::-`             {color[0]}:yhhhhh: {results[10]}
{color[2]}       -:::::-.         {color[0]}`-ohhhhhh+  {results[11]}
{color[2]}        .::::-` {color[0]}-o+///+oyhhyyyhy:   {results[12]}
{color[2]}         `.--  {color[0]}/yhhhhhhhy+{color[2]},....
{color[0]}               /hhhhhhhhh{color[2]}-.-:::;
{color[0]}               `.:://::- {color[2]}-:::::;
{color[2]}                         `.-:-'
{color[2]}
\x1b[0m'''
,'LinuxMint':'''{color[0]}
{color[0]} MMMMMMMMMMMMMMMMMMMMMMMMMmds+.      {results[0]}
{color[0]} MMm----::-://////////////oymNMd+`   {results[1]}
{color[0]} MMd      {color[1]}/++                {color[0]}-sNMd:  {results[2]}
{color[0]} MMNso/`  {color[1]}dMM    `.::-. .-::.`{color[0]} .hMN: {results[3]}
{color[0]} ddddMMh  {color[1]}dMM   :hNMNMNhNMNMNh: `{color[0]}NMm {results[4]}
{color[0]}     NMm  {color[1]}dMM  .NMN/-+MMM+-/NMN` {color[0]}dMM {results[5]}
{color[0]}     NMm  {color[1]}dMM  -MMm  `MMM   dMM. {color[0]}dMM {results[6]}
{color[0]}     NMm  {color[1]}dMM  -MMm  `MMM   dMM. {color[0]}dMM {results[7]}
{color[0]}     NMm  {color[1]}dMM  .mmd  `mmm   yMM. {color[0]}dMM {results[8]}
{color[0]}     NMm  {color[1]}dMM`  ..`   ...   ydm. {color[0]}dMM {results[9]}
{color[0]}     hMM-  {color[1]}+MMd/-------...-:sdds {color[0]}MMM {results[10]}
{color[0]}     -NMm-  {color[1]}:hNMNNNmdddddddddy/` {color[0]}dMM {results[11]}
{color[0]}      -dMNs-``{color[1]}-::::-------.``    {color[0]}dMM {results[12]}
{color[0]}       `/dMNmy+/:-------------:/yMMM
{color[0]}          ./ydNMMMMMMMMMMMMMMMMMMMMM
{color[0]}
{color[0]}
{color[0]}
\x1b[0m'''
,'Fedora':'''{color[0]}
{color[2]}           :/------------://        {results[0]}
{color[2]}        :------------------://      {results[1]}
{color[2]}      :-----------{color[0]}/shhdhyo/{color[2]}-://     {results[2]}
{color[2]}    /-----------{color[0]}omMMMNNNMMMd/{color[2]}-:/    {results[3]}
{color[2]}   :-----------{color[0]}sMMMdo:/{color[2]}       -:/   {results[4]}
{color[2]}  :-----------{color[0]}:MMMd{color[2]}-------    --:/  {results[5]}
{color[2]}  /-----------{color[0]}:MMMy{color[2]}-------    ---/  {results[6]}
{color[2]} :------    --{color[0]}/+MMMh/{color[2]}--        ---: {results[7]}
{color[2]} :---     {color[0]}oNMMMMMMMMMNho{color[2]}     -----: {results[8]}
{color[2]} :--      {color[0]}+shhhMMMmhhy++{color[2]}   ------:  {results[9]}
{color[2]} :-      -----{color[0]}:MMMy{color[2]}--------------/  {results[10]}
{color[2]} :-     ------{color[0]}/MMMy{color[2]}-------------:   {results[11]}
{color[2]} :-      ----{color[0]}/hMMM+{color[2]}------------:    {results[12]}
{color[2]} :--{color[0]}:dMMNdhhdNMMNo{color[2]}-----------:
{color[2]} :---{color[0]}:sdNMMMMNds:{color[2]}----------:
{color[2]} :------{color[0]}:://:{color[2]}-----------://
{color[2]} :--------------------://
{color[2]}
\x1b[0m'''
,'openSUSE project':'''{color[0]}
{color[1]}        +########_ #=.    {results[0]}
{color[1]}      ################-#  {results[1]}
{color[1]}    =################ -:+ {results[2]}
{color[1]}   ################+# #~# {results[3]}
{color[1]}  ################## ==#= {results[4]}
{color[1]} :##+:################-_# {results[5]}
{color[1]} ## `_  ##########=###=`  {results[6]}
{color[1]} #._###- ##   .##.        {results[7]}
{color[1]} #`#~ `# ##    `#_^       {results[8]}
{color[1]} ## ## #  #     ^#        {results[9]}
{color[1]}  #=  ##                  {results[10]}
{color[1]}   ####                   {results[11]}
{color[1]}                          {results[12]}
{color[1]}
{color[1]}
{color[1]}
\x1b[0m'''
, 'Slackware':'''{color[0]}
{color[1]}                   :::::::                    {results[0]}
{color[1]}             :::::::::::::::::::              {results[1]}
{color[1]}          :::::::::::::::::::::::::           {results[2]}
{color[1]}        ::::::::{color[0]}cllcccccllllllll{color[1]}::::::        {results[3]}
{color[1]}     :::::::::{color[0]}lc               dc{color[1]}:::::::      {results[4]}
{color[1]}    ::::::::{color[0]}cl   clllccllll    oc{color[1]}:::::::::    {results[5]}
{color[1]}   :::::::::{color[0]}o   lc{color[1]}::::::::{color[0]}co   oc{color[1]}::::::::::   {results[6]}
{color[1]}  ::::::::::{color[0]}o    cccclc{color[1]}:::::{color[0]}clcc{color[1]}::::::::::::  {results[7]}
{color[1]}  :::::::::::{color[0]}lc        cclccclc{color[1]}:::::::::::::  {results[8]}
{color[1]} ::::::::::::::{color[0]}lcclcc          lc{color[1]}:::::::::::: {results[9]}
{color[1]} ::::::::::{color[0]}cclcc{color[1]}:::::{color[0]}lccclc     oc{color[1]}::::::::::: {results[10]}
{color[1]} ::::::::::{color[0]}o    l{color[1]}::::::::::{color[0]}l    lc{color[1]}::::::::::: {results[11]}
{color[1]}  :::::{color[0]}cll{color[1]}:{color[0]}o     clcllcccll     o{color[1]}:::::::::::  {results[12]}
{color[1]}  :::::{color[0]}occ{color[1]}:{color[0]}o                  clc{color[1]}:::::::::::
{color[1]}   ::::{color[0]}ocl{color[1]}:{color[0]}ccslclccclclccclclc{color[1]}:::::::::::::
{color[1]}    :::{color[0]}oclcccccccccccccllllllllllllll{color[1]}:::::
{color[1]}     ::{color[0]}lcc1lcccccccccccccccccccccccco{color[1]}::::
{color[1]}       ::::::::::::::::::::::::::::::::
{color[1]}         ::::::::::::::::::::::::::::
{color[1]}            ::::::::::::::::::::::
{color[1]}                 ::::::::::::
{color[1]}
\x1b[0m'''
, 'Mac OSX':'''
{color[0]}                  ##             {results[0]}
{color[0]}               ####              {results[1]}
{color[0]}               ##                {results[2]}
{color[0]}       #######    #######        {results[3]}
{color[0]}     ######################      {results[4]}
{color[0]}    #####################        {results[5]}
{color[0]}    ####################         {results[6]}
{color[0]}    ####################         {results[7]}
{color[0]}    #####################        {results[8]}
{color[0]}     ######################      {results[9]}
{color[0]}      ####################       {results[10]}
{color[0]}        ################         {results[11]}
{color[0]}          ###     ####           {results[12]}
\x1b[0m'''
, 'Linux':'''
{color[0]}              a8888b.            {results[0]}
{color[0]}             d888888b.           {results[1]}
{color[0]}             8P"YP"Y88           {results[2]}
{color[0]}             8|o||o|88           {results[3]}
{color[0]}             8'    .88           {results[4]}
{color[0]}             8`._.' Y8.          {results[5]}
{color[0]}            d/      `8b.         {results[6]}
{color[0]}          .dP   .     Y8b.       {results[7]}
{color[0]}         d8:'   "   `::88b.      {results[8]}
{color[0]}        d8"           `Y88b      {results[9]}
{color[0]}       :8P     '       :888      {results[10]}
{color[0]}        8a.    :      _a88P      {results[11]}
{color[0]}      ._/"Yaa_ :    .| 88P|      {results[12]}
{color[0]}      \    YP"      `| 8P  `.
{color[0]}      /     \._____.d|    .'
{color[0]}      `--..__)888888P`._.'
\x1b[0m'''

}


def autoSize(used, total):
    mem = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    for x in range(1, 5):
        if total > 1000:
            used = math.ceil(used / 1024)
            total = math.ceil(total / 1024)
            size = mem[x]
    return int(used), int(total), size

#---------------Classes---------------#

class Output:
    results = []
    #results.extend(['']*(18-len(output)))

    def __init__(self):
        #dist = self.detectDistro()
        self.distro = self.detectDistro()
        self.json = {}
        #self.dist = dist

    def fileCheck(self,f):
        """
        1. Checks if a file exists, if so, reads it
        2. looks for distribution name in file
        3. returns name and if it was successful or not
        """
        txt = ''

        if os.path.isfile(f):
            txt = open(f).readlines()

        else:
            return False,'Linux'

        linux = ['Arch','Fedora','LinuxMint','Ubuntu','SUSE','Debian','Raspbian','Slackware']
        dist = 'Linux'
        ans = False
        for line in txt:
            for i in linux:
                if line.find(i) >= 0:
                    dist = i
                    ans = True
                    break

        return ans,dist

    def detectDistro(self):
        dist = _platform
        if dist == 'darwin':
            dist = 'Mac OSX'
        elif dist == 'freebsd':
            dist = 'FreeBSD'
        else:
            try:
                dist = Popen(['lsb_release', '-is'], stdout=PIPE).communicate()[0].decode('Utf-8').rstrip('\n')
            except:
                #print 'Error w/ lsb_release'
                ans,dist = self.fileCheck('/etc/os-release')
                if not ans: dist = 'Linux'

        # Correct some distribution names
        if dist == 'Arch':
            dist =  'Arch Linux'
        elif dist == 'openSUSE project':
            dist = 'openSUSE'


        return dist


    def append(self, display):
        self.results.append('%s%s: %s%s' % (colorDict[self.distro][1], display.key, colorDict['Clear'][0], display.value))
        self.json[display.key] = display.value

    def output(self, json=False):
        if json:
            return self.json
        else:
            print(logosDict[self.distro].format(color = colorDict[self.distro], results = self.results))

class User:
    def __init__(self):
        self.key = 'User'
        self.value = os.getenv('USER')

class Hostname:
    def __init__(self):
        hostname = Popen(['uname', '-n'], stdout=PIPE).communicate()[0].decode('Utf-8').rstrip('\n')
        self.key = 'Hostname'
        self.value = hostname


class OS:
    def __init__(self,dist):
        OS = dist

        arch = Popen(['uname', '-m'], stdout=PIPE).communicate()[0].decode('Utf-8').rstrip('\n')
        OS = OS + ' ' + arch

        self.key = 'OS'
        self.value = OS


class Kernel:
    def __init__(self):
        kernel = Popen(['uname', '-r'], stdout=PIPE).communicate()[0].decode('Utf-8').rstrip('\n')
        self.key = 'Kernel'
        self.value = kernel

class Uptime:
    def __init__(self):
        up = ps.boot_time()
        up = dt.datetime.fromtimestamp(up)
        now = dt.datetime.now()
        diff = now - up
        uptime = '%d days %d hrs %d mins' %(diff.days,diff.seconds/3600,(diff.seconds%3600)/60)
        self.key = 'Uptime'
        self.value = uptime

class Shell:
    def __init__(self):
        self.key = 'Shell'
        self.value = os.getenv('SHELL')

class Processes:
    def __init__(self):
        self.key = 'Processes'
        self.value =  str(len(ps.pids())) + ' running'

class Packages:
    def __init__(self,dist):
        try:
            if dist == 'Mac OSX':
                p1 = Popen(['brew', 'list', '-1'], stdout=PIPE).communicate()[0].decode("Utf-8")
            elif dist == 'FreeBSD':
                p1 = Popen(['pkg', 'info'], stdout=PIPE).communicate()[0].decode("Utf-8")
            elif dist == 'Arch':
                p1 = Popen(['pacman', '-Q'], stdout=PIPE).communicate()[0].decode("Utf-8")
            elif dist == 'Fedora' or dist == 'openSUSE project':
                p1 = Popen(['rpm', '-qa'], stdout=PIPE).communicate()[0].decode("Utf-8")
            elif dist == 'Ubuntu' or dist == 'Debian' or dist == 'LinuxMint' or dist == 'Raspbian':
                p0 = Popen(['dpkg', '--get-selections'], stdout=PIPE)
                p1 = Popen(['grep', '-v', 'deinstall'], stdin=p0.stdout, stdout=PIPE).communicate()[0].decode("Utf-8")
            elif dist == 'Slackware':
                 p1 = Popen(['ls', '/var/log/packages/'], stdout=PIPE).communicate()[0].decode("Utf-8")
            packages = len(p1.rstrip('\n').split('\n'))
        except:
            packages = 0
        self.key = 'Packages'
        self.value = packages

class CPU:
    def __init__(self,dist):
        #file = open('/proc/cpuinfo').readlines()
        try:
            if dist == 'Mac OSX':
                cpu = Popen(['sysctl', '-n','machdep.cpu.brand_string'], stdout=PIPE).communicate()[0].decode('Utf-8').split('\n')[0]
                c = cpu.replace('(R)','').replace('(TM)','').replace('CPU','').split()
                cpuinfo = ' '.join(c)
            elif dist == 'FreeBSD':
                file = Popen(['sysctl', '-n','hw'], stdout=PIPE).communicate()[0].decode('Utf-8').split('\n')
                cpuinfo = re.sub('  +', ' ', file[1].replace('model name\t: ', '').rstrip('\n'))
            else:
                file = Popen(['grep', '-i', 'model name\t: ', '/proc/cpuinfo'], stdout=PIPE).communicate()[0].decode('Utf-8').split('\n')
                cpuinfo = re.sub('  +', ' ', file[0].replace('model name\t: ', ''))
        except:
            cpuinfo = 'unknown'
        self.key = 'CPU'
        self.value = cpuinfo

class RAM:
    def __init__(self):
        ram = ps.virtual_memory()
        used = ram.used
        total = ram.total

        used,total,size = autoSize(used,total)
        ramdisplay = '%s %s/ %s %s' % (used, size, total,size)

        self.key = 'RAM'
        self.value = ramdisplay

class Disk:
    def __init__(self,json=False):
        p = ps.disk_usage('/')
        total = p.total
        used = p.used

        used,total,size = autoSize(used,total)

        usedpercent = int(float(used)/float(total)*100.0)

        if json:
            disk = '%s / %s %s' % (used, total, size)
        else:
            if usedpercent <= 33:
                disk = '%s%s %s/ %s %s' % (colorDict['Sensors'][1], used, colorDict['Clear'][0], total, size)
            if usedpercent > 33 and usedpercent < 67:
                disk = '%s%s %s/ %s %s' % (colorDict['Sensors'][2], used, colorDict['Clear'][0], total, size)
            if usedpercent >= 67:
                disk = '%s%s %s/ %s %s' % (colorDict['Sensors'][0], used, colorDict['Clear'][0], total, size)
        self.key = 'Disk'
        self.value = disk

class IP:
    def __init__(self, zeroconfig=False):
        """
        This tries to get the host name and deterine the IP address from it.
        It also tries to handle zeroconfig well.
        """
        ip = '127.0.0.1'
        try:
            host = socket.gethostname()
            if zeroconfig:
                if host.find('.local') < 0:
                    host=host + '.local'

            ip = socket.gethostbyname(host)
        except:
            pass

        self.key = 'IP'
        self.value = ip

class CPU2:
    def __init__(self):
        cpu = ps.cpu_percent(interval=1, percpu=True)
        self.key = 'CPU Usage'
        self.value = str(cpu)

def handleArgs():
	parser = argparse.ArgumentParser('Displays system info and a logo for OS')
	#parser.add_argument('-a', '--art', help='not implemented yet')
	parser.add_argument('-d', '--display', help='displays all ascii logos', action='store_true')
	parser.add_argument('-z', '--zeroconfig', help='assume a zeroconfig network and adds .local to the hostname', action='store_true')
	parser.add_argument('-j', '--json', help='instead of printing to screen, returns system as json', action='store_true')

	args = vars(parser.parse_args())

	return args

def main():
    args = handleArgs()

    if args['display']:
        for i in logosDict:
            print(i)
            print(logosDict[i].format(color = colorDict[i],results=list(xrange(0,13))) )
        return 0

    out = Output()
    out.append( User() )
    out.append( Hostname() )
    out.append( IP(args['zeroconfig']) )
    out.append( OS(out.distro) )
    out.append( Kernel() )
    out.append( Uptime() )
    out.append( Shell() )
    out.append( Processes() )
    out.append( Packages(out.distro) )
    out.append( CPU(out.distro) )
    out.append( CPU2() )
    out.append( RAM() )
    out.append( Disk(args['json']) )

    jsn = out.output(args['json'])


    if args['json']:
        return json.dumps(jsn)



if __name__ == '__main__':
    main()
