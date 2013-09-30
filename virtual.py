import wx
import math
import threading,time
#import pygame.midi as midi
from wx.lib.pubsub import Publisher
import rtmidi as rtmidi
import osc2midi
import mappings

map_num = 0

class mainFrame(wx.Frame):
	def __init__(self,parent,title):
		wx.Frame.__init__(self,None,title=title, size=(250, 250)) # size=(800,500), style = wx.FRAME_SHAPED | wx.SIMPLE_BORDER)
		self.SetMinSize((250,250))

		self.bgpanel = wx.Panel(self)
		self.bgpanel.SetMinSize((400,250))
		self.bgsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(self.bgsizer)
		self.bgsizer.Add(self.bgpanel,1, wx.EXPAND)

		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.bgpanel.SetSizer(self.sizer)
		launch_pad = launchPad(self.bgpanel)
		#settings_panel = settingsPanel(self.bgpanel)
		self.sizer.Add(launch_pad,5, wx.EXPAND)
		#self.sizer.Add(settings_panel,3, wx.EXPAND) 

		self.Show(True)

class settingsPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)# -1, size=(300,500))
		self.SetBackgroundColour(wx.BLUE)
		self.SetMinSize((150,250))

class launchPad(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)# -1, size=(500,500))
		self.SetBackgroundColour(wx.BLACK)
		self.SetMinSize((250,250))

		self.midi_out = rtmidi.MidiOut("SoopadooPad VirtualPad Out")
		self.midi_out.open_virtual_port("SoopadooPad VirtualPad Out")
		#for port in range(self.midi_out.get_port_count()):
		#	if self.midi_out.get_port_name(port) == "sooperlooper:0":
		#		self.midi_out.open_port(port)

		self.logo = wx.EmptyBitmap(1,1)
		self.logo.LoadFile("logo.png", wx.BITMAP_TYPE_ANY)

		self.menu_list = []
		for key in mappings.colour_map:
			self.menu_list.append((mappings.colour_map[key][1], key))
		self.menu_list.sort()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.border = 30

		self.leds = []
		for j in range(0,8):
			self.leds.append(led(self, (0, j), circle=True))
		for i in range(1,4):
			for j in range(0,8):
				self.leds.append(led(self, (i, j)))
			self.leds.append(led(self, (i,8), circle=True))
		for j in range(0,3):
			self.leds.append(led(self, (4, j)))
		self.leds.append(led(self, (4, 3), cut_edge=3))
		self.leds.append(led(self, (4, 4), cut_edge=4))
		for j in range(5,8):
			self.leds.append(led(self, (4, j)))
		self.leds.append(led(self, (4,8), circle=True))
		for j in range(0,3):
			self.leds.append(led(self, (5, j)))
		self.leds.append(led(self, (5, 3), cut_edge=2))
		self.leds.append(led(self, (5, 4), cut_edge=1))
		for j in range(5,8):
			self.leds.append(led(self, (5, j)))
		self.leds.append(led(self, (5,8), circle=True))
		for i in range(6,9):
			for j in range(0,8):
				self.leds.append(led(self, (i, j)))
			self.leds.append(led(self, (i,8), circle=True))

		self.SetSizer(self.sizer)

		self.SetFocus()

		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_RIGHT_DOWN, self.onRightClick)
		self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick)
		self.Bind(wx.EVT_LEFT_UP, self.onLeftRelease)
		self.Bind(wx.EVT_MOTION, self.onMotion)
		self.Bind(wx.EVT_KEY_DOWN, self.onKey)

		Publisher().subscribe(self.onMidi, "midi_out")
	
		self.timer = wx.Timer(self)
		self.timer.Start(500)

		self.check_bpm_timer = wx.Timer(self)
		#self.check_bpm_timer.Start(10)

		self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
		#self.Bind(wx.EVT_TIMER, self.onCheckBPM, self.check_bpm_timer)
		self.flash = False

		self.write_bufnum = 0
		self.display_bufnum = 0

	#def onCheckBPM(self, event):
	#	wx.CallAfter(osc_server.checkBPM)

	def onTimer(self, event):
		if self.flash:
			self.display_bufnum = not self.display_bufnum
			self.Refresh()

	def onMidi(self, msg):
		if msg.data[0:2] == mappings.dbl_buf:
			if (msg.data[2] & mappings.midiflags["default"]) == mappings.midiflags["default"]: #ignore if right bit's aren't set
				if self.display_bufnum ^ ((msg.data[2] >> mappings.midiflags["display"]) & 0b1):
					self.display_bufnum = not self.display_bufnum
				self.write_bufnum = (msg.data[2] >> mappings.midiflags["update"]) & 0b1
				self.flash = (msg.data[2] >> mappings.midiflags["flash"]) & 0b1
				if (msg.data[2] >> mappings.midiflags["copy"]) & 0b1:
					for item in self.leds:
						item.copy(1)
		elif (msg.data[0] == 176) or (msg.data[0] == 144):
			for item in self.leds:
				if item.midi_message == msg.data[0:2]:
					item.setMessage(msg.data[2])
		self.Refresh()
	def onLeftClick(self, event):
		if event.CmdDown():
			for item in self.leds:
				if item.rect.Contains(event.GetPosition()):
						self.deselect = item.selected 
						item.select(not item.selected)
		else:
			for item in self.leds:
				if item.rect.Contains(event.GetPosition()):
					self.midi_out.send_message((item.midi_message[0], item.midi_message[1], 127))	
					item.midi_sent = True
					break

	def onLeftRelease(self, event):
			for item in self.leds:
				if item.midi_sent:
					if (item.midi_message[0] >> 4) == 0b1001:
						note_off = item.midi_message[0] & 0b11101111
						self.midi_out.send_message((note_off, item.midi_message[1], 0))	
					else:
						self.midi_out.send_message((item.midi_message[0], item.midi_message[1], 0))	
					item.midi_sent = False
					break

	def onMotion(self, event):
		if event.CmdDown():
			if event.Dragging():
				for item in self.leds:
					if item.rect.Contains(event.GetPosition()):
						item.select(not self.deselect)

	def onRightClick(self, event):
		for item in self.leds:
			if item.rect.Contains(event.GetPosition()):
				item.select(1)
		menu = wx.Menu()
		for item in self.menu_list:
			menu.Append(item[1], item[0])
			wx.EVT_MENU(menu, item[1], self.menuSelection)
		self.PopupMenu(menu, event.GetPosition())
		for item in self.leds:
				item.select(0)
		menu.Destroy()

	def menuSelection(self, event):
		for item in self.leds:
			if item.selected:
				item.setMessage(event.GetId())
				item.select(0)

	def onKey(self, event):
		if event.GetUnicodeKey() == 65: #a
			if event.CmdDown():
				for item in self.leds:
						item.select(1)
		elif event.GetUnicodeKey() == 68: #d
			if event.CmdDown():
				for item in self.leds:
						item.select(0)

	def onSize(self, event):
		self.size =  self.GetSize()[0]
		self.led_size = (self.size - (self.border * 2.0))/9.0
		self.led_border =  self.led_size / 10.0
		for item in self.leds:
			ox,oy,ow,oh = (self.border + item.col * self.led_size, self.border + item.row * self.led_size, self.led_size, self.led_size)
			x,y,w,h = (ox + self.led_border, oy + self.led_border , ow - self.led_border * 2.0, oh - self.led_border * 2.0)
			item.setRect(x,y,w,h,ox,oy,ow,oh)
		self.scale = self.led_size/float(self.logo.GetSize()[1])
		self.logo_pos = (self.leds[7].rect[0] + self.led_size, self.leds[7].rect[1])
		self.Refresh()
		event.Skip()

	def onPaint(self, event):
		dc = wx.PaintDC(self)
		gc = wx.GraphicsContext.Create(dc)
		gc.DrawBitmap(self.logo,self.logo_pos[0],self.logo_pos[1], self.logo.GetSize()[0] * self.scale, self.logo.GetSize()[1] * self.scale)
		for item in self.leds:
			x,y,w,h = item.inner_rect.Get() 
			gc.SetBrush(wx.Brush(wx.WHITE))
			if item.circle:
				gc.DrawEllipse(x + self.led_border/4.0,y + self.led_border/4.0,w - self.led_border/2.0,h - self.led_border/2.0)
			else:
				gc.DrawRoundedRectangle(x,y,w,h, 3)
			gc.SetBrush(wx.Brush(item.colours[self.display_bufnum]))
			if item.circle:
				gc.DrawEllipse(x + self.led_border/4.0,y + self.led_border/4.0,w - self.led_border/2.0,h - self.led_border/2.0)
			else:
				gc.DrawRoundedRectangle(x,y,w,h, 3)
			if item.cut_edge:
				gc.PushState()
				gc.SetBrush(wx.Brush(wx.BLACK))
				path = gc.CreatePath()
				gc.Translate(x,y)
				path.AddLineToPoint(w/8.0,0)
				path.AddLineToPoint(0,h/8.0)
				path.AddLineToPoint(0,0)
				gc.Rotate(math.radians(90 * (item.cut_edge - 1)))
				if item.cut_edge == 2:
					gc.Translate(0,-w)
				elif item.cut_edge == 3:
					gc.Translate(-w,-h)
				elif item.cut_edge == 4:
					gc.Translate(-h,0)
				gc.FillPath(path)
				gc.PopState()
			if item.selected:
				x,y,w,h = item.rect.Get() 
				gc.SetBrush(wx.Brush("#26466D7F"))
				if item.circle:
					gc.DrawEllipse(x,y,w,h)
				else:
					gc.DrawRectangle(x+1,y+1,w-2,h-2)

class led():
	def __init__(self, parent,pos, colour=wx.Colour(0,0,0,0), circle=False, cut_edge=0):
		self.parent = parent
		self.selected = 0
		self.colours = [colour, colour]
		self.row, self.col = pos
		self.rect = wx.Rect(0,0,0,0)
		self.inner_rect = wx.Rect(0,0,0,0)
		self.circle = circle
		self.cut_edge = cut_edge
		self.midi_sent = False

		if not self.row: #row 0 are CC buttons
			self.midi_message = (176, 104 + self.col)
		else:
			self.midi_message =  (144, (self.row - 1) * 16 + self.col)

	def setRect(self, x, y, w, h, ox, oy, ow, oh):
		self.inner_rect = wx.Rect(x, y, w, h)
		self.rect = wx.Rect(ox, oy, ow, oh)
	def copy(self, val):
		if val:
			self.colours[self.parent.write_bufnum] = self.colours[self.parent.display_bufnum]
	def setMessage(self, message):
		copy  = (message >> 2 ) & 0b1
		clear = (message >> 3 ) & 0b1
		colour = mappings.getColour(message)
		if copy:
			self.colours[not self.parent.write_bufnum] = colour
		elif clear:
			self.colours[not self.parent.write_bufnum] = (0,0,0,0)
		self.colours[self.parent.write_bufnum] = colour
		if self.parent.write_bufnum == self.parent.display_bufnum:
			self.parent.RefreshRect(self.inner_rect)
	def select(self, val):
		if val < 2 and val > -1:
			self.selected = val
		else:
			self.selected = not self.selected
		self.parent.RefreshRect(self.rect)


	
def onMidiIn(msg, time_stamp):
  #print msg
  if msg[2] == 127:
		if tuple(msg[:2]) in special_midi:
			for key in special_midi:
				if tuple(msg[:2]) == key:
					special_midi[key]()

class midiReceiver():
	def __init__(self):
		self.midi_in = rtmidi.MidiIn("SooPadooPad In");
		self.midi_in.set_callback(onMidiIn)
		self.map_num = 0
		for port in range(self.midi_in.get_port_count()):
			if self.midi_in.get_port_name(port) == "Launchpad:0":
				self.midi_in.open_port(port)
	def switch_map(self):
		self.map_num = not self.map_num
		midi_sender.reset()
		print "switching map_num to: ", int(self.map_num)
		wx.CallAfter(Publisher().sendMessage, "switch_map", self.map_num)



class midiSender():
	def __init__(self):
		self.midi_out = rtmidi.MidiOut("SooPadooPad Out");
		for port in range(self.midi_out.get_port_count()):
			if self.midi_out.get_port_name(port) == "Launchpad:0":
				self.midi_out.open_port(port)
		Publisher().subscribe(self.onMidiOut, "midi_out")
	def onMidiOut(self, msg):
		self.midi_out.send_message(msg.data)	
	def reset(self):
		self.midi_out.send_message((176, 0, 0))

app = wx.App(0)

osc_server = osc2midi.Server()
osc_server_thread = threading.Thread(target = osc_server.serve_forever)
osc_server_thread.start()

midi_sender = midiSender()
midi_receiver = midiReceiver()

special_midi = {
  mappings.coordToMIDI[(8,8)] : midi_receiver.switch_map
}


frame = mainFrame(None, "SooPadooPad")


app.MainLoop()


midi_sender.reset()
osc_server.client.unregister_all()
osc_server.close()
osc_server_thread.join()
