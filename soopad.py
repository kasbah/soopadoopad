import OSC
import math
#import wx
import time
#from wx.lib.pubsub import Publisher
#from pubsub import pub
import mappings
import special_maps
import rtmidi as rtmidi

_port = "7777"
_host = "arch"
_slhost = "arch"
_slport = 9951


#registrations = [
#		             ("loop_pos"         , 100),	
#		             ("loop_len"         , 100),	
#		             ("use_common_outs"  , 100),	
#		             ("state"	           , 100),
#		             ("next_state"       , 100),
#								 ("waiting"          , 100)
#		            ]
#
#global_regs = [("selected_loop_num", 100),
#		           ("dry"              , 100)
#		          ]


class Client(OSC.OSCClient):
	def __init__(self, registrations, midi_bindings):
		global _host,_port,_slhost,_slport
		OSC.OSCClient.__init__(self)
		self.connect((_slhost, _slport))

		self.returl = "osc.udp://" + _host + ":" + _port
		self.registrations = registrations
		self.midi_bindings = midi_bindings

	def ping(self):
		msg = OSC.OSCMessage("/ping")
		msg.append(self.returl)
		msg.append("/pingack")
		try:
			self.send(msg)
		except:
			print "error sending OSC ping"
			
	def register_all(self):
		for item in self.registrations:
			self.register(item[0], item[1], item[2])
		self.bind_all()
		#msg = OSC.OSCMessage("/register")
		#msg.append(self.returl)
		#msg.append("/pingack")
		#self.send(msg)
		msg = OSC.OSCMessage("/register_update")
		msg.append("tap_tempo")
		msg.append(self.returl)
		msg.append("/tap")
		self.send(msg)
		msg = OSC.OSCMessage("/register_update")
		msg.append("tempo")
		msg.append(self.returl)
		msg.append("/tempo")
		self.send(msg)

	def midi_bind(self, binding_serialization):
		msg = OSC.OSCMessage("/add_midi_binding")
		msg.append(binding_serialization)
		msg.append("")
		self.send(msg)
	
	def midi_unbind(self, binding_serialization):
		msg = OSC.OSCMessage("/remove_midi_binding")
		msg.append(binding_serialization)
		msg.append("")
		self.send(msg)

	def unbind_all(self):
		for item in self.midi_bindings:
			self.midi_unbind(item)
	def bind_all(self):
		for item in self.midi_bindings:
			self.midi_bind(item)

	def register(self, loop_num, param, time):
		if (loop_num < 0):
			msg = OSC.OSCMessage("/register_auto_update")
		else:
			msg = OSC.OSCMessage("/sl/" + str(loop_num) + "/register_auto_update")
		msg.append(param)
		msg.append(time)
		msg.append(self.returl)
		msg.append("/generic")
		self.send(msg)

	def unregister_all(self):
		for item in self.registrations:
			self.unregister(item[0], item[1])
		#msg = OSC.OSCMessage("/unregister")
		#msg.append(self.returl)
		#msg.append("/pingack")
		#self.send(msg)
		self.unbind_all()
		msg = OSC.OSCMessage("/unregister_update")
		msg.append("tap_tempo")
		msg.append(self.returl)
		msg.append("/tap")
		self.send(msg)
		msg = OSC.OSCMessage("/unregister_update")
		msg.append("tempo")
		msg.append(self.returl)
		msg.append("/tempo")
		self.send(msg)

	def unregister(self, loop_num, param):
		if (loop_num < 0):
			msg = OSC.OSCMessage("/unregister_auto_update")
		else:
			msg = OSC.OSCMessage("/sl/" + str(loop_num) + "/unregister_auto_update")
		msg.append(param)
		msg.append(self.returl)
		msg.append("/generic")
		self.send(msg)
	
	def init_get(self):
		for item in self.registrations:
			self.get(item[0], item[1])
		msg = OSC.OSCMessage("/get")
		msg.append("tempo")
		msg.append(self.returl)
		msg.append("/tempo")
		self.send(msg)

	def get(self, loop_num, param):
		if (loop_num < 0):
			msg = OSC.OSCMessage("/get")
		else:
			msg = OSC.OSCMessage("/sl/" + str(loop_num) + "/get")
		msg.append(param)
		msg.append(self.returl)
		msg.append("/generic")
		self.send(msg)


class Server(OSC.OSCServer):
	def __init__(self):
		receive_address = "", int(_port) # url empty for localhost
		OSC.OSCServer.__init__(self,receive_address)
		
		self.map_number = 0
		self.registrations = []


		for key in mappings.oscToMIDI[self.map_number]:
			for item in mappings.osc[key[0]][1]:
				self.registrations.append((mappings.oscToMIDI[self.map_number][key][0], item, 10))

		self.registrations = set(self.registrations)
		
		self.sent_colour = {}
		self.prev_vals = {}

		self.reset()


		self.initialize_leds()

		#send midi bindings
		self.midi_bindings = []
		for key in mappings.midi[self.map_number]:
			if mappings.bindables[mappings.midi[self.map_number][key][0]][0] == "cmd":
				cmd_or_ctrl = "note"
				tog_or_norm = "norm"
			elif mappings.bindables[mappings.midi[self.map_number][key][0]][0] == "ctrl":
				cmd_or_ctrl = "set"
				tog_or_norm = "toggle"
			if mappings.bindables[mappings.midi[self.map_number][key][0]][1]: #g.ctrl
				tog_or_norm = "norm"
				targ_range = "-1 " + mappings.midi[self.map_number][key][1] 
				loop_num = "-2"
			else:
				loop_num = mappings.midi[self.map_number][key][1]
				targ_range = "0 1"
			self.midi_bindings.append( "0 " + 
			                           mappings.midi_type[(key[0], mappings.bindables[mappings.midi[self.map_number][key][0]][0])] + " " + 
			                           str(key[1]) + " " + 
			                           cmd_or_ctrl + " " + 
			                           mappings.midi[self.map_number][key][0] + " " +
			                           loop_num + " " +
			                           targ_range + " " +
			                           tog_or_norm + " 0 127"
                                                                           )

		self.addMsgHandler("/generic", self.genericHandler)
		self.addMsgHandler("/pingack", self.pingackHandler)
		self.addMsgHandler("/tap", self.tapHandler)
		self.addMsgHandler("/tempo", self.tempoHandler)
		self.diff = 0

		self.flash_message_o = (mappings.dbl_buf[0], mappings.dbl_buf[1], mappings.midiflags["default"] | 0b1)
		self.flash_message_i = (mappings.dbl_buf[0], mappings.dbl_buf[1], mappings.midiflags["default"])
		self.enable_LP_flash = (mappings.dbl_buf[0], mappings.dbl_buf[1], mappings.midiflags["default"] | (1 << mappings.midiflags["flash"]))

		#wx.CallAfter(Publisher().sendMessage, "midi_out", self.enable_LP_flash)
		midi_sender.midi_out.send_message(self.enable_LP_flash)
		self.LP_flash_enabled = True

		self.client = Client(self.registrations, self.midi_bindings)
		self.client.ping()

		self.thread_is_ready = False
	
		#Publisher().subscribe(self.onSwitchMap, "switch_map")

	def initialize_leds(self):
	  for item in mappings.ledToMIDI:
		self.sent_colour[item] = mappings.colourStrToMIDI("Off")
	  for key in mappings.init_colours[self.map_number]:
	  	self.sent_colour[key] = mappings.init_colours[self.map_number][key]
	  	#wx.CallAfter(Publisher().sendMessage, "midi_out", (key[0], key[1], mappings.init_colours[self.map_number][key]))
		midi_sender.midi_out.send_message((key[0], key[1], mappings.init_colours[self.map_number][key]))
	def switch_map(self, map_number):
		self.map_number = map_number
		if self.map_number:
			self.client.unregister_all()
			for item in mappings.ledToMIDI:
				self.sent_colour[item] = mappings.colourStrToMIDI("Off")
		else:
			self.initialize_leds()
			self.client.register_all()
			self.client.init_get() 
	def onSwitchMap(self, msg):
	  self.switch_map(msg.data)

	def reset (self): 
		#wx.CallAfter(Publisher().sendMessage, "midi_out", (176, 0, 0))
		midi_sender.midi_out.send_message((176, 0, 0))

	def tempoHandler(self, addr, tags, data, source):
		if (data[2] <= 0.0 or data[2] > 240.0) and not self.LP_flash_enabled:
			self.LP_flash_enabled = True
			#wx.CallAfter(Publisher().sendMessage, "midi_out", self.enable_LP_flash)
			#pub.sendMessage("midi_out", self.enable_LP_flash)
			midi_sender.midi_out.send_message(self.enable_LP_flash)
		elif self.LP_flash_enabled:
			#wx.CallLater(100,Publisher().sendMessage, "midi_out", self.flash_message_o)
			self.LP_flash_enabled = False


	def pingackHandler(self, addr, tags, data, source):
		self.is_ready = False
		self.prev_pos = []	
		self.next_state = []	
		self.waiting = []
		self.state = []
		for i in range(int(data[2])):
			self.prev_pos.append(0.0)
			self.next_state.append(-1.0)
			self.waiting.append(0.0)
			self.state.append(-1.0)
		self.threadIsReady(True) # normally invoked from another thread saying it has dealt with the loop nums and can now do it's thing
	def tapHandler(self, addr, tags, data, source):
		if not self.LP_flash_enabled:
		  #wx.CallAfter(Publisher().sendMessage, "midi_out", self.flash_message_i)
			midi_sender.midi_out.send_message(self.flash_message_i)
			time.sleep(0.1)
			midi_sender.midi_out.send_message(self.flash_message_o)
			#TODO: #wx.CallLater(100,Publisher().sendMessage, "midi_out", self.flash_message_o)

	def threadIsReady(self, val):
		self.thread_is_ready = val
		self.client.init_get() 
		self.client.register_all()
	def genericHandler(self, addr, tags, data, source):
    #i:loop_index  s:control  f:value
		loop_index = data[0]
		control = data[1]
		value = data[2]
		if self.thread_is_ready:
			#for each binding
			for key in mappings.oscToMIDI[self.map_number]: 
				key_osc = key[0]
				key_midi = key[1]
				# check if it is the right loop
				if mappings.oscToMIDI[self.map_number][key][0] == loop_index:

					# check if the OSC message is relevant
					if control in mappings.osc[key_osc][1]: 

						# deal with multiple OSC arguments
						if len(mappings.osc[key_osc][1]) > 1:
							variables = []
							temp_list = list(mappings.osc[key_osc][1])
							try:
								for item in temp_list:
									variables.append(self.prev_vals[(item, loop_index)])

							#if prev_val hasn't been set
							except KeyError:
								continue
								#osc_return = False
							else:
							  variables[mappings.osc[key_osc][1].index(control)] = value
							#osc lambda
							osc_return = mappings.osc[key_osc][2](variables)
						else:
							#osc lambda
							osc_return = mappings.osc[key_osc][2](value)

						#deal with comparisons of local variables to OSC values
						try:
							extra_val = mappings.oscToMIDI[self.map_number][key][3]
						except IndexError:
							pass
						else:
							#oscToMIDI lambda
							#print "osc_return: ", osc_return, " extra_val: ", extra_val
							osc_return = mappings.oscToMIDI[self.map_number][key][4]((osc_return, extra_val))
							#print osc_return
						if type(osc_return) is not bool:
							raise TypeError(data)

						#switch between the two colour controlling values
						midi_val_key = 2 - osc_return

						#don't send if no value is specified in the oscToMIDI map
						if mappings.oscToMIDI[self.map_number][key][midi_val_key] is not None:

							#don't send if the previous value sent is the same
							if self.sent_colour[key_midi] != mappings.oscToMIDI[self.map_number][key][midi_val_key]:
								self.sent_colour[key_midi] = mappings.oscToMIDI[self.map_number][key][midi_val_key]
								#wx.CallAfter(Publisher().sendMessage, "midi_out", (key_midi[0], key_midi[1], self.sent_colour[key_midi]))
								midi_sender.midi_out.send_message((key_midi[0], key_midi[1], self.sent_colour[key_midi]))

		else:
			print "skipped OSC packet"
		self.prev_vals[(control, loop_index)] = value

class midiSender():
	def __init__(self):
		self.midi_out = rtmidi.MidiOut("SoopadooPad Out");
		for port in range(self.midi_out.get_port_count()):
			if self.midi_out.get_port_name(port) == "Launchpad:0":
				self.midi_out.open_port(port)
		#Publisher().subscribe(self.onMidiOut, "midi_out")
	#def onMidiOut(self, msg):
	#	self.midi_out.send_message(msg.data)	
	def reset(self):
		self.midi_out.send_message((176, 0, 0))

def onMidiIn(msg, time_stamp):
  #print msg
  if msg[2] == 127:
		if tuple(msg[:2]) in special_maps.midi:
			for key in special_maps.midi:
				if tuple(msg[:2]) == key:
						midi_receiver.switch_map(special_maps.midi[key](midi_receiver.map_num))

class midiReceiver():
	def __init__(self):
		self.midi_in = rtmidi.MidiIn("SoopadooPad In");
		self.midi_in.set_callback(onMidiIn)
		self.map_num = 0
		for port in range(self.midi_in.get_port_count()):
			if self.midi_in.get_port_name(port) == "Launchpad:0":
				self.midi_in.open_port(port)
	def switch_map(self, map_num):
		self.map_num = map_num 
		midi_sender.reset()
		print "switching map_num to: ", int(self.map_num)
		osc_server.switch_map(self.map_num)
		#wx.CallAfter(Publisher().sendMessage, "switch_map", self.map_num)

midi_sender = midiSender()
midi_receiver = midiReceiver()

osc_server = Server()
#osc_server_thread = threading.Thread(target = osc_server.serve_forever)
#osc_server_thread.start()
try:
	osc_server.serve_forever()
except:
	midi_sender.reset()
	osc_server.client.unregister_all()
	osc_server.close()
#osc_server_thread.join()
