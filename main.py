import os
import urllib2
import json

from flask import Flask, render_template, request
app = Flask(__name__)
app.debug = True

__mutedVolume = 0

import pympc
pympc.init()

##### index file
@app.route('/')
def http_index():
	return render_template("index.html", status = pympc.status(), hostname = os.uname()[1])

##### ajax interface

# playback controls
@app.route('/next')
@pympc.statusasjson
def ajax_next():
	pympc.genericSingle("next")

@app.route('/previous')
@pympc.statusasjson
def ajax_prev():
	pympc.genericSingle("previous")

@app.route('/pause/<int:pause>')
@pympc.statusasjson
def ajax_pause(pause):
	pympc.genericSingle("pause", [pause])

@app.route('/play/<int:track>')
@pympc.statusasjson
def ajax_play(track):
	pympc.genericSingle("play", [track])

@app.route('/stop')
@pympc.statusasjson
def ajax_stop():
	pympc.genericSingle("stop")

@app.route("/toggle/<flag>")
@pympc.statusasjson
def ajax_toggle(flag):
	val = 1 - int(pympc.lastStatus["status"][flag])
	pympc.genericSingle(flag, [val])

# status
@app.route('/status')
@pympc.statusasjson
def ajax_status():
	pass

# volume controls
@app.route('/volume/<cmd>')
@pympc.statusasjson
def ajax_volume(cmd):
	vol = int(pympc.lastStatus["status"]["volume"])
	if cmd == "down": pympc.genericSingle("setvol", [vol - 5])
	elif cmd == "up": pympc.genericSingle("setvol", [vol + 5])
	elif cmd == "mute":
		global __mutedVolume
		__mutedVolume = vol
		pympc.genericSingle("setvol", [0])
	elif cmd == "unmute": pympc.genericSingle("setvol", [vol])

# playlist controls
@app.route("/playlist/get")
def ajax_pl_get():
	return json.dumps({"aaData" : pympc.genericList("playlistinfo")[1]})
	
@app.route("/playlist/delete/<int:track>")
@pympc.statusasjson
def ajax_pl_delete(track):
	pympc.genericSingle("delete", [track])

@app.route("/playlist/addstream", methods=["POST"])
def ajax_pl_addStream():
	pympc.genericSingle("add", [request.form["stream"]])
	return ""

@app.route("/playlist/save", methods=["POST"])
def ajax_pl_save():
	pympc.genericSingle("save", [request.form["name"]])
	return ""

@app.route("/playlist/add/<path:uri>")
def ajax_pl_add(uri):
	pympc.genericSingle("add", [uri])
	return ""

@app.route("/playlist/load/<name>")
def ajax_pl_load(name):
	pympc.genericSingle("load", [name])
	return ""

@app.route("/playlist/show/<name>")
def ajax_pl_show(name):
	return json.dumps({"aaData": pympc.genericList("listplaylistinfo", [name])[1]})

@app.route("/playlist/replace/<name>")
def ajax_pl_replace(name):
	pympc.genericSingle("clear")
	pympc.genericSingle("load", [name])
	return ""

# search
@app.route("/search/<tag>/<query>")
def ajax_search(tag, query):
	return json.dumps({"aaData": pympc.genericList("search", [tag, query])[1]})

# database browsing
@app.route("/database/ls/", defaults={'folder': ''})
@app.route("/database/ls/<path:folder>")
def ajax_dbload(folder):
	return json.dumps(pympc.genericList("lsinfo", [folder])[1])

if __name__ == '__main__':
	app.run(host='0.0.0.0')
