import socket
import re
import json
import functools

def asjson(f):
	"""Decorator: convert result to JSON."""
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		return json.dumps(f(*args, **kwargs))
	return wrapped

def statusasjson(f):
	"""Decorator: discard result, return status() as JSON instead."""
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		f(*args, **kwargs)
		return json.dumps(status())
	return wrapped

class MPC:
	def __init__(self, host = "localhost", port = 6600):
		"""Initialize connection."""
		self.__sock = socket.create_connection( (host, port), None )
		self.__file = self.__sock.makefile()
		
		self.__completionRE = re.compile("^(OK|ACK)")
		self.__initRE = re.compile("^OK MPD ([0-9.]+)$")
		self.__errorRE = re.compile("^ACK \[(\d*)@(\d*)\] {([^}]*)} (.*)$")
		self.__assignmentRE = re.compile("^(.*?):\s*(.*)$")
		self.__version = None
		
		# read init sequence
		line = self.read()
		m = self.__initRE.match(line)
		if m != None:
			self.__version = m.group(1)

	def send(self, cmd):
		"""Send a command to server."""
		self.__file.write(cmd + "\n")
		self.__file.flush()	
	
	def read(self):
		"""Read one line from server."""
		while True:
			res = self.__file.readline().strip()
			if len(res) > 0: 
				return res
	
	def dumpResult(self, cmd):
		"""Execute command and dump full output."""
		self.send(cmd)
		while True:
			line = self.read()
			print("> " + line)
			if self.__completionRE.match(line) != None:
				break
	
	def returnStatus(self, line, res, rest):
		"""Parse last line and return actual result tuple."""
		if line == "OK":
			return ("OK", res, rest)
			
		m = self.__errorRE.match(line)
		if m != None:
			return ("ERROR", {"error": m.group(1), "atcmd": m.group(2), "cmd": m.group(3), "msg": m.group(4)})
		
		return ("UNKOWN", res, rest)
	
	def readSingleReply(self):
		"""Read a reply with a single assignment."""
		res = {}
		rest = []
		
		while True:
			line = self.read()
			if self.__completionRE.match(line) != None:
				return self.returnStatus(line, res, rest)

			m = self.__assignmentRE.match(line)
			if m != None:				res[m.group(1)] = m.group(2)
			else:
				rest.append(line)
	
	def readListReply(self, newKeys = []):
		"""Read a reply with a list of assignments. newKeys should be a list of keys that may start a new item."""
		res = []
		rest = []
		cur = {}
		
		while True:
			line = self.read()
			if self.__completionRE.match(line) != None:
				res.append(cur)
				return self.returnStatus(line, res, rest)

			m = self.__assignmentRE.match(line)
			if m != None:
				if m.group(1) in newKeys:
					if cur != {}:
						res.append(cur)
					cur = {}
				cur[m.group(1)] = m.group(2)
			else:
				rest.append(l)
		
	
__mpc = None
lastStatus = None
__newKeys = {
	"listplaylistinfo": ["file"],
	"lsinfo": ["directory", "file", "playlist"],
	"playlistinfo": ["file"],
	"search": ["file"],
}

def init(host = "localhost", port = 6600):
	"""Initialize singleton mpc instance."""
	global __mpc
	__mpc = MPC(host, port)

def genericSingle(cmd, args = []):
	"""Handle all commands that return an single or no assignment."""
	__mpc.send(cmd + " " + " ".join(map(lambda x: '"' + str(x) + '"', args)))
	return __mpc.readSingleReply()

def genericList(cmd, args = [], newKeys = None):
	"""Handle all commands that return a list of assignments."""
	if newKeys == None:
		if cmd in __newKeys:
			newKeys = __newKeys[cmd]
		else:
			newKeys = []
	
	__mpc.send(cmd + " " + " ".join(map(lambda x: '"' + str(x) + '"', args)))
	return __mpc.readListReply(newKeys)

def status():
	"""Return current status. Combines results of status and currentsong and updates lastStatus variable."""
	res = {
		"status": genericSingle("status")[1],
		"song": genericSingle("currentsong")[1],
	}
	global lastStatus
	lastStatus = res
	return res

if __name__ == "__main__":
	init()
	print(genericSingle("status"))
	