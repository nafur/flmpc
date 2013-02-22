import subprocess
import re
import json

__lastStatus = None

# decorator for all commands that return the current status
# this will be basically all :-)
def returnsStatus(f):
	def wrapped(*args, **kwargs):
		f(*args, **kwargs)
		return json.dumps(getStatus())
	return wrapped

def returnsOK(f):
	def wrapped(*args, **kwargs):
		f(*args, **kwargs)
		return json.dumps("OK")
	return wrapped


# prepare the status parsing
def compileStatusRe():
	track = "(.+)$"
	status = "\[(\w+)\]"
	tracknum = "#(\d+)/(\d+)"
	time = "(\d+:\d+)/(\d+:\d+)"
	percent = "\((\d+)\%\)"
	update = "(?:Updating DB \(#1\) ...)?"
	volume = "volume:\s+(\d+)\%"
	flags = "(?:\s*(\w+):\s*(\w+)\s*)"
	
	complete = "\s*".join([track, status, tracknum, time, percent, update, volume, flags, flags, flags, flags])
	
	return re.compile(complete, re.MULTILINE)
__statusre = compileStatusRe()

# call mpc with given option
def call(options):
	return subprocess.check_output("mpc " + options, shell = True).decode("utf-8")

# call mpc and generate status dict
def getStatus():
	s = call("status")
	m = __statusre.match(s)
	if m == None:
		return {}
	else:
		g = m.groups()
		d = {
			"track": g[0],
			"status": g[1],
			"tracknum": g[2],
			"trackcnt": g[3],
			"elapsed": g[4],
			"length": g[5],
			"percent": g[6],
			"volume": g[7],
		}
		for i in range(8,len(g),2):
			d[g[i]] = g[i+1] == "on"
		global __lastStatus
		__lastStatus = d
		return d

# actual commands

@returnsStatus
def pause():
	call("pause")
@returnsStatus
def play(track):
	if (track == None):
		call("play")
	else:
		call("play " + str(track))

@returnsStatus
def next():
	call("next")
@returnsStatus
def prev():
	call("prev")

@returnsStatus
def volume(mod):
	call("volume " + str(mod))
	
@returnsStatus
def toggleFlag(flag):
	call(flag)

def getPlaylist():
	l = []
	temp = call("playlist").split("\n")
	for i in range(0,len(temp)):
		if len(temp[i]) == 0:
			continue
		l.append([temp[i],i+1])
	return json.dumps({"aaData": l})

@returnsOK
def delete(track):
	call("del " + str(track))

@returnsOK
def addStream(stream):
	call("add " + stream)

def ls(folder):
	return json.dumps(filter(lambda s: len(s)>0, call("ls \"" + folder + "\"").split("\n")))

@returnsStatus
def status():
	pass

def lastStatus():
	return __lastStatus
