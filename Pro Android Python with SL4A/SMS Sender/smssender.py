import android
import time
import os
from ConfigParser import ConfigParser
import csv
import json
import signal
import urllib2
import zipfile
import StringIO
import shutil
	
BASE_PATH = "/sdcard/sl4a/scripts"

# Change to script directory
if os.path.exists( BASE_PATH ) is False:
	try:
		os.makedirs( BASE_PATH )
	except:
		exit()
os.chdir(BASE_PATH)

# Prepare a log file
# TODO: Would be better thing to use the python logger instead
LOG = "../SMSSender.py.log"
if os.path.exists(LOG) is False:
	f = open(LOG, "w")
	f.close()
LOG = open(LOG, "a")

class CSVReader():
	def __init__(self, filename):
		# Read the delimiter and quotechar using a sniffer
		try:
			csvfile = open( filename, "rb" )
		except:
			raise
		line = csvfile.readline()
		if line == "":
			# TODO: Error handling
			return False
		try:
			dialect = csv.Sniffer().sniff( line )
		except:
			raise
		# keep the dialect for info
		self.dialect = dialect

		# Back to top of file
		csvfile.seek(0)
		try:
			rows = csv.DictReader( csvfile, dialect=dialect )
		except:
			raise
		# Get the field names from the DictReader object
		self.fields = rows.fieldnames
		
		# DictReader to list (is it necessary? Why not keep the iteratable DictReader?
		self.rows = list( rows )
	
	def getFields(self):
		return self.fields
		
	def getRows(self):
		return self.rows
		
	def getColumnCount(self):
		return self.fields.__len__()
		
class MergerConfigParser(ConfigParser):
	descriptions = {
			"locale": {
				"prefix": "International prefix. Used to clean up phone numbers before sending.\nThis will only affect numbers that do not yet have an international code.\nExamples (assuming prefix is +60):\n0123456789 will become +60123456789\n60123456789 will become +60123456789\n+49332211225 remains unchanged",
			},
			"merger": {
				"informevery": "Use TTS to inform you every n messages. Set to 0 if you do not wish to use this feature.",
				"informeveryratio": "Use TTS to inform you every total / n messages. Set to 1 if you do not wish to use this feature.\nExample\nIf you are sending 200 messages and set this value to 5, you will be informed by TTS of the status every 200 / 5 = 40 messages."
			},
			"application" : {
				"showhiddendirectories": "While browsing, hidden directories (stating with '.') will not be shown if this is set to 1.",
				"showonlycsvfiles": "While importing the CSV file, only files with the extension .csv will be shown if this is set to 1.",
				"showonlytextfiles": "While importing template text from a file, only files with the extension .txt will be shown if this is set to 1."
			}
		}
	ignore = ["package"]
	def __init__( self, file ):
		ConfigParser.__init__( self )
		self.filesread = self.read( file )
		self.file = file
	
	def load( self ):
		# Go through all the sections
		sections = {}
		# Some sections are meant to be ignored
		for section in self.sections():
			if section not in self.ignore:
				items = self.items(section)
				options = []
				for item in items:
					options.append( {"name":item[0], "value":item[1], "description": self.descriptions[section][item[0]] } )
				sections[section] = options
		return sections
	
	def save( self, sections ):
		for section in sections:
			options = sections[section]
			for option in options:
				self.set( section, option, options[option] )
		fp = open( self.file, "w" )
		try:
			self.write( fp )
		except Error, e:
			return e
		return ""
	
	def update(self, original):
		parser = ConfigParser()
		parser.read( original )
		newsections = self.sections()
		for section in parser.sections():
			# Is it a section that user can not modify?
			if section not in self.ignore:
				# Does the section still exist?
				if section in newsections:
					items = parser.items(section)
					for item in items:
						# Does the option still exist?
						try:
							self.get( section, item[0] )
						except:
							pass
						else:
							self.set( section, item[0], item[1] )
		
class SMSMerger():
	def __init__( self, droid ):
		# Template text
		self.template = ""
		# Column index in which to find phone numbers
		self.numbercolumn = None
		# Rows of the csv file
		self.items = []
		# Merge fields - including phone number field
		self.fields = ()
		# List of SMS objects
		self.sms = []
		# Droid :)
		self.droid = droid
		
	def merge(self):
		prefix = self.prefix
		actual = self.getUsedMergeFields()
		phonefield = self.fields[self.numbercolumn]
		# Reset SMSs
		self.sms = []
		messages = []
		for item in self.items:
			number = item[phonefield]
			# Use the entire item, there is no harm in having too many values passed to String.format
			# Only too many keys in the text
			print "Using parts: ", item
			success = False
			message = self.template
			while success is False:
				try:
					message = message.format(**item)
				except KeyError, key:
					key = key.args[0]
					message = message.replace( "{%s}" % key, "{{%s}}" % key )
				else:
					success = True
					
			print "Using message ", message
			sms = SMS(number, message, prefix)
			self.sms.append(sms)
			messages.append(sms.dict())
		return messages
		
	# Add items to the list of recipients
	def setItems(self, items):
		self.items = items
		
	def setTemplate(self, template):
		self.template = template
		
	# Get the items
	def getItems(self):
		return self.items
		
	# Get the items
	def getFields(self):
		return self.fields
	
	# Utility set function
	def setFields(self, fields):
		print "As we setFields, fields is ", fields
		self.fields = fields
	
	# Utility set function
	def setNumberColumn(self, column):
		self.numbercolumn = int(column)
	
	# Do the actual merge and send
	def send(self, keys):
		options = self.options
		total = keys.__len__()
		# This is the part where the Droid informs us that it has sent a message
		# The variable every represents how often we want it to speak
		every = int(options["informevery"])
		# If we found a value for every, means we wish to be informed every n messages, otherwise...
		if every == 0:
			# Otherwise, means we wish to be informed every total / n messages (e.g. total messages is 200, ratio=5 will give us a warning every 40 messages)
			ratio = int(options["informeveryratio"])
			# If ratio was set to 0, means we dont want info at all
			if ratio == 0:
				every = False
			else:
				every = total / ratio
				# If every still 0, means total is less than ratio. set to 1
				if every == 0:
					every = 1
		# Start measuring duration
		start = time.time()
		actual = 0
		for k, sms in enumerate(self.sms):
			# Check whether we're supposed to send
			if k in keys:
				# Add 1 to actual starts at 1 (for the ttS part at the end)
				actual = actual + 1
				# Send
				sms.send(self.droid)
				LOG.write("SMS sent to %s\n" % sms.recipient)
				number = sms.recipient
				# Little extra, let the droid speak out every once in a while
				# Announce every n of total number
				if every is not False:
					if actual % every == 0:
						# Last message
						if actual == total:
							self.speakAndWait("Message sent to %s. A total of %d messages have been sent. Process took %d seconds." % (number, total, int(time.time() - start)))
						else:
							self.speakAndWait("Message sent to %s. %d messages remaining" % (number, total - actual))
	
	def getMergeFields(self):
		actual = list(self.fields)
		actual.pop(self.numbercolumn)
		return actual
	
	def getUsedMergeFields(self):
		if self.template != "":
			fields = list(self.fields)
			used = []
			for field in fields:
				if self.template.find("{%s}" % field) != -1:
					used.append(field)
		return used
	
	def validTemplate(self):
		# We now allow all fields to not be included, but a check is done
		# We ignore the number column (although it may be used as a merge field)
		missing = []
		for field in self.getMergeFields():
			if self.template.find("{%s}" % field) == -1:
				missing.append(field)
		return missing
		
	def speakAndWait(self, text):
		self.droid.ttsSpeak(text)
		while self.droid.ttsIsSpeaking()[1] is True:
			time.sleep(1)
	
class SMS():
	def __init__(self, recipient, message, prefix):
		self.prefix = prefix
		self.setRecipient(recipient)
		self.message = message.replace( "\u000A", "\n" )
		
	def dict(self):
		return {"number":self.recipient, "message": self.message}
		
	def setRecipient(self, recipient):
		recipient = str(recipient)
		if recipient[0] == "0":
			recipient = recipient.replace("0", self.prefix, 1)
		elif recipient.find(self.prefix.replace("+", "")) == 0:
			recipient = "+%s" % recipient
		elif recipient[0] != "+":
			recipient = "%s%s" % (self.prefix, recipient)
		else:
			# Should be the ok case with a well constructed international phone number
			pass
		self.recipient = recipient
	
	def send(self, droid):
		droid.smsSend(self.recipient, self.message)
		
class UIHandler():
	def __init__(self, waitfor=None, post=None):
		# Name of the event to wait for - default python
		if waitfor is None:
			self.waitfor = "python"
		else:
			self.waitfor = waitfor
		# Name of the event to post
		if post is None:
			self.post = "javascript"
		else:
			self.post = post
		self.droid = android.Android()
		self.dispatch = {}
			
	def wait(self):
		droid = self.droid
		event = droid.waitForEvent(self.waitfor)
		# This is currently needed because if the waitForEvent is too fast, the event is missed
		start = time.time()
		data = event.result["data"]
		print data, type(data)
		if type(data) in [str, unicode]:
			data = str(data)
			try:
				data = json.loads(data)
				print "ok...", data
			except:
				self.log("Unable to parse Json data upon receiving event. Data passed: %s" % data)
				data = {}
		else:
			self.log("Data received from event is not a string, using empty dict")
			data = {}
		print data["task"]
		feedback = self.dispatch[data["task"]](data)
		passing = json.dumps(feedback)
		self.log(passing)
		howlong = time.time() - start
		min = 0.2
		if howlong < min:
			time.sleep(min - howlong)
			self.log("Had to wait cause process was only %f second" % howlong)
		droid.postEvent(self.post, passing)
		
	def log(self, message):
		print message
	
	def startLoad(self, title="", message=""):
		droid = self.droid
		droid.dialogCreateSpinnerProgress(title, message)
		droid.dialogShow()
		
	def stopLoad(self):
		self.droid.dialogDismiss()
		
class SMSSenderHandler(UIHandler):
	""" Handler class for this particular application. Extends UIHandler """
	def __init__(self):
		UIHandler.__init__(self)
		# Create the dispatch dictionnary which maps tasks to methods
		self.dispatch = { 
			"loadfile": self.loadfile,
			"validate": self.validate,
			"loadfilecontent": self.loadfilecontent,
			"loadconfig": self.loadconfig,
			"send": self.send,
			"merge": self.merge,
			"listdir":self.listdir,
			"saveconfig":self.saveconfig
		}
		
	def saveconfig( self, data ):
		""" Saves the configuration into config file
		
		data -- dict which contains the sections, each of them containing a dict representing the options / value
		
		Example of data received: {"application":{"hang":"0","rule":"1"}, "package": {"version":"1.02"}}
		
		"""
		parser = self.parser
		sections = data["sections"]
		error = parser.save( sections )
		return {"error":error}
		
		
	def loadconfig( self, data ):
		""" Loads the configuration sections and options
		
		data -- dict which only contains the task
		
		"""
		parser = self.parser
		return {"sections": parser.load()}

	def listdir(self, data):
		""" Creates two lists of files and folders in the path found in data
		
		data -- dict containing path and type (for filtering)
		
		"""
		self.log("Loading directory content")
		base = data["path"]
		type = data["type"]
		# Check in the config whether we want to show only a certain type of content
		showHiddenDirectories = self.parser.getboolean( "application", "showhiddendirectories" )
		
		if type == "txt":
			if self.parser.getboolean( "application", "showonlytextfiles" ) is True:
				filter = ".{0}".format( type )
			else:
				filter = None
		elif type == "csv":
			if self.parser.getboolean( "application", "showonlycsvfiles" ) is True:
				filter = ".{0}".format( type )
			else:
				filter = None
		else:
			filter = None

		# List all directories and files, then filter
		all = os.listdir(base)
		files = []
		folders = []
		for file in all:
			# Separate files and folders
			abs = "{0}/{1}".format( base, file )
			if os.path.isdir( abs ):
				# Are we filtering hidden directories?
				if showHiddenDirectories is True or file[0] != ".":
					folders.append( str( file ) )
			elif os.path.isfile( abs ):
				# Are we filtering by type?
				if filter is None or os.path.splitext( file )[1] == filter:
					files.append( str( file ) )
					
		# Sort alphabetically
		files.sort( key=str.lower )
		folders.sort( key=str.lower )
		return {"files":files,"folders":folders}
		
	def loadfile(self, data):
		self.log("Loading file")
		merger = self.merger
		filename = data["path"]
		if filename != "":
			self.log("Selected filename %s " % filename)
			try:
				reader = CSVReader( filename )
			except csv.Error, e:
				return { "error": "Unable to open CSV: %s" % e }
			fields = reader.getFields()
			self.log("Found fields: %s" % ''.join(fields))
			merger.setFields(fields)
			rows = reader.getRows()
			merger.setItems(rows)
			# Rows are now dicts, for preview, want them as list of values only
			values = []
			for row in rows:
				values.append( row.values() )
		else:
			self.log("No file name")
			return {"filename":"","fields":[], "error": ""}
		# Success and new file, return all info
		return {"filename":filename, "fields":fields, "delimiter":reader.dialect.delimiter, "quotechar":reader.dialect.quotechar, 
		"lineterminator": reader.dialect.lineterminator, "error": "", "rows":values }
		
	def send(self, data):
		self.startLoad("Processing", "Sending")
		options = {"informevery":self.parser.get("merger","informevery"),"informeveryratio":self.parser.get("merger","informeveryratio")}
		self.merger.options = options
		self.merger.send(data["which"])
		self.stopLoad()
		return {"count":data["which"].__len__()}
		
	def merge(self, data):
		droid = self.droid
		merger = self.merger
		merger.prefix = parser.get( "locale", "prefix" )
		merger.setNumberColumn(int(data["phone"]))
		merger.setTemplate(data["text"])
		ret = {"success":False, "error":"", "messages":[]}
		# Valid template returns a list of merge fields that are not used by the given template
		missing = merger.validTemplate()
		if missing.__len__() == 0:
			ret["messages"] = merger.merge()
			ret["success"] = True
		else:
			droid.dialogCreateAlert("Incomplete text", "The following merge fields are not being used by the template: %s.\r\n Would you like to edit the template text?" % ",".join(missing))
			droid.dialogSetPositiveButtonText("Yes")
			droid.dialogSetNegativeButtonText("No")
			droid.dialogShow()
			resp = droid.dialogGetResponse()
			# User wishes to load now
			if resp.result["which"] == "positive" :
				return {"task":"edittext"}
			else:
				ret["messages"] = merger.merge()
				ret["success"] = True
		return ret
		
	def loadfilecontent(self, data):
		content = open( data["path"], "r" ).read()
		return { "content": content }
		
	def validate(self, data):
		merger = self.merger
		merger.setNumberColumn(data["phone"])
		merger.setTemplate(data["text"])
		# Valid template returns a list of fields that are not being used by the current template
		missing = merger.validTemplate()
		return { "missing": missing }
		
	def exit(self, data):
		""" An attempt at killing pid instead of simple exit so as to also kill webview (failed) """
		pid = os.getpid()
		os.kill(pid, signal.SIGTERM)
		
	def log(self, message):
		""" Log and print messages
		
		message -- Message to log
		"""
		LOG.write(message)
		print message
			

if __name__ == '__main__':
	
	# Create android object
	droid = android.Android()
	# Create the Handler 
	handler = SMSSenderHandler()
	""" 
	Handle some stuff like checking of files, version, before actually starting
	"""
	
	# Check that the html file, js, etc all exist. This should only happen the first time
	files = ("html/SMSSender.html","css/zest.css","js/mootools.js","images/tab-bg.png","images/tab-bg-current.png","images/text-tab.png","images/text-tab-current.png","images/merge-tab.png","images/merge-tab-current.png","images/setup-tab.png","images/setup-tab-current.png","images/file-tab.png","images/file-tab-current.png","images/folder.png","images/txt.png","etc/SMSSender.conf")
	missing = []
	for required in files:
		if os.path.exists( "{0}/{1}".format(BASE_PATH, required) ) is False:
			missing.append( required )
	# Some files missing...
	if missing.__len__() > 0:
		# All files, so download the zip file
		# for now always download the whole zip file
		#if missing.__len__() == files.__len__():
		droid.dialogCreateAlert("Download required", "Some components of the User Interface are not present on the device. Download from the internet?" )
		droid.dialogSetPositiveButtonText("Yes")
		droid.dialogSetNegativeButtonText("Exit")
		droid.dialogShow()
		resp = droid.dialogGetResponse()
		# User wishes to load now
		if resp.result["which"] == "positive" :
			handler.startLoad()
			uri = "https://sites.google.com/site/androidscriptingexperiments/smssender.zip?attredirects=0&d=1"
			try:
				response = urllib2.urlopen(uri)
			except:
				droid.dialogCreateAlert("Connection failed", "Unable to connect to server. Please check your internet connection. Exiting" )
				droid.dialogSetPositiveButtonText("Ok")
				droid.dialogShow()
				resp = droid.dialogGetResponse()
				exit()
			zip = zipfile.ZipFile(StringIO.StringIO(response.read()))
			zip.extractall()
			handler.stopLoad()
		else:
			exit()
		
		
	# Get config file
	config = "{0}/etc/SMSSender.conf".format( BASE_PATH )
			
	parser = MergerConfigParser( config )
	
	# If readfile is an empty list, there was a problem reading the config file
	if parser.filesread.__len__() > 0:
		# Check that we have the latest version of files
		version = droid.getPackageVersion( "com.zest.smssender" ).result
		
		# If parser throws an error means this option didnt exist, ie old version
		try:
			filesversion = parser.get("package","version")
		except:
			filesversion = "0"

		if float(version) > float(filesversion):
			# Do a backup of the config file so as not to lose user's setup
			backup = "{0}.bu".format( config )
			shutil.copyfile( config, backup )
			droid.dialogCreateAlert("Download required", "Some components of the User Interface have been updated. Download from the internet?" )
			droid.dialogSetPositiveButtonText("Yes")
			droid.dialogSetNegativeButtonText("Exit")
			droid.dialogShow()
			resp = droid.dialogGetResponse()
			# User wishes to load now
			if resp.result["which"] == "positive" :
				handler.startLoad()
				uri = "https://sites.google.com/site/androidscriptingexperiments/smssender.zip?attredirects=0&d=1"
				try:
					response = urllib2.urlopen(uri)
				except:
					droid.dialogCreateAlert("Connection failed", "Unable to connect to server. Please check your internet connection. Exiting" )
					droid.dialogSetPositiveButtonText("Ok")
					droid.dialogShow()
					resp = droid.dialogGetResponse()
					exit()
				zip = zipfile.ZipFile(StringIO.StringIO(response.read()))
				zip.extractall()
				# Re-read the config file now that it's the new version
				parser = MergerConfigParser( config )
				# TODO: Put back the user's setup into the new config file
				parser.update( backup )
				handler.stopLoad()
			else:
				exit()
	else:
		LOG.write("Could not open config file. Exiting.")
		exit()
		
	"""
	Start instanciating the actual objects and showing the application
	"""
	# Create SMSMerger. Throughout the process we will set the object preferences
	merger = SMSMerger( droid )
	
	LOG.write( "Starting SMSSender\n" )
	
	# Create the Webview
	wv = droid.webViewShow("{0}/html/SMSSender.html".format( BASE_PATH ) )
	print wv

	
	# Add the needed objects to Handler
	handler.merger = merger
	handler.parser = parser
	
	# Loop
	while True:
		handler.wait()
	exit()
