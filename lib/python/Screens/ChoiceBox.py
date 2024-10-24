from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.config import config, ConfigSubsection, ConfigText
from Components.Label import Label
from Components.ChoiceList import ChoiceEntryComponent, ChoiceList
from Components.Sources.StaticText import StaticText
from Tools.BoundFunction import boundFunction
from enigma import ePoint, eSize, getDesktop
from skin import applySkinFactor

config.misc.pluginlist = ConfigSubsection()
config.misc.pluginlist.eventinfo_order = ConfigText(default="")
config.misc.pluginlist.extension_order = ConfigText(default="")


class ChoiceBox(Screen):
	def __init__(self, session, title="", list=None, keys=None, selection=0, skin_name=None, text="", reorderConfig="", windowTitle=None, var="", callbackList=None, *args, **kwargs):
		# list is in the format (<display text>, [<parameters to pass to close callback>,])
		# callbackList is in the format (<display text>, <callback func>, [<parameters>,])
		self.isCallbackList = bool(callbackList)
		list = list or callbackList
		if not list:
			list = []
		if not skin_name:
			skin_name = []
		Screen.__init__(self, session)

		if isinstance(skin_name, str):
			skin_name = [skin_name]
		self.skinName = skin_name + ["ChoiceBox"]

		self.reorderConfig = reorderConfig
		self["text"] = Label()
		self.var = ""
		if reorderConfig:
			self["key_menu"] = StaticText(_("MENU"))
			self["key_previous"] = StaticText(_("PREVIOUS"))
			self["key_next"] = StaticText(_("NEXT"))

		if title:
			title = _(title)
			if len(title) < 55 and title.find('\n') == -1:
				self.setTitle(title)
			elif title.find('\n') != -1:
				temptext = title.split('\n')
				if len(temptext[0]) < 55:
					self.setTitle(temptext[0])
					count = 2
					labeltext = ""
					while len(temptext) >= count:
						if labeltext:
							labeltext += '\n'
						labeltext = labeltext + temptext[count - 1]
						count += 1
					self["text"].setText(labeltext)
				else:
					self["text"].setText(title)
			else:
				self["text"].setText(title)
		elif text:
			self["text"].setText(_(text))
		self["description"] = Label()
		self.list = []
		self.summarylist = []
		if keys is None:
			self.__keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "red", "green", "yellow", "blue"] + (len(list) - 14) * [""]
		else:
			self.__keys = keys + (len(list) - len(keys)) * [""]

		self.keymap = {}
		pos = 0
		if self.reorderConfig:
			self.config_type = getattr(config.misc.pluginlist, self.reorderConfig)
			if self.config_type.value:
				prev_list = [i for i in zip(list, self.__keys)]
				new_list = []
				for x in self.config_type.value.split(","):
					for entry in prev_list:
						if entry[0][0] == x:
							new_list.append(entry)
							prev_list.remove(entry)
				list = [i for i in zip(*(new_list + prev_list))]
				list, self.__keys = list[0], list[1]
				number = 1
				new_keys = []
				for x in self.__keys:
					if (not x or x.isdigit()) and number <= 10:
						new_keys.append(str(number % 10))
						number += 1
					else:
						new_keys.append(not x.isdigit() and x or "")
				self.__keys = new_keys
		for x in list:
			if x:
				strpos = str(self.__keys[pos])
				self.list.append(ChoiceEntryComponent(key=strpos, text=x))
				if self.__keys[pos] != "":
					self.keymap[self.__keys[pos]] = list[pos]
				self.summarylist.append((self.__keys[pos], x[0]))
				pos += 1

		self["list"] = ChoiceList(list=self.list, selection=selection)
		self["summary_list"] = StaticText()
		self["summary_selection"] = StaticText()
		self.updateSummary(selection)

		self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions", "MenuActions"],
		{
			"ok": self.go,
			"1": self.keyNumberGlobal,
			"2": self.keyNumberGlobal,
			"3": self.keyNumberGlobal,
			"4": self.keyNumberGlobal,
			"5": self.keyNumberGlobal,
			"6": self.keyNumberGlobal,
			"7": self.keyNumberGlobal,
			"8": self.keyNumberGlobal,
			"9": self.keyNumberGlobal,
			"0": self.keyNumberGlobal,
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"up": self.up,
			"down": self.down,
			"left": self.left,
			"right": self.right,
			"shiftUp": self.additionalMoveUp,
			"shiftDown": self.additionalMoveDown,
			"menu": self.setDefaultChoiceList,
			"back": self.cancel
		}, prio=-2)

	def autoResize(self):
		margin = applySkinFactor(4)
		separator = applySkinFactor(10)
		desktop_w = getDesktop(0).size().width()
		desktop_h = getDesktop(0).size().height()
		itemheight = self["list"].getItemHeight()
		textsize = (0, 0)
		if self["text"].text:
			textsize = self["text"].getSize()
			if textsize[0] < textsize[1]:
				textsize = (textsize[1], textsize[0] + 10)
		listLen = len(self.list)
		listMaxItems = int(desktop_h * 0.8 - textsize[1]) // itemheight
		scrollbar = self["list"].instance.getScrollbarWidth() + 5 if listLen > listMaxItems else 0
		listWidth = int(min(self["list"].instance.getMaxItemTextWidth() + scrollbar, desktop_w * 0.9))
		count = min(listLen, listMaxItems)
		if textsize[1] and textsize[0] < listWidth:
			textsize = (listWidth, textsize[1])
		width = max(listWidth, textsize[0])
		listsize = (width, listMaxItems * itemheight)
		listPos = separator + textsize[1] if textsize[1] > 0 else margin
		# resize label
		self["text"].instance.resize(eSize(*textsize))
		self["text"].instance.move(ePoint(margin, margin))
		# move list
		self["list"].instance.resize(eSize(*listsize))
		self["list"].instance.move(ePoint(margin, listPos))

		wsizex = margin * 2 + width
		wsizey = listPos + (count * itemheight) + margin
		wsize = (wsizex, wsizey)
		self.instance.resize(eSize(*wsize))

		# center window
		self.instance.move(ePoint((desktop_w - wsizex) // 2, (desktop_h - wsizey) // 2))

	def left(self):
		if len(self["list"].list) > 0:
			while True:
				self["list"].instance.moveSelection(self["list"].instance.pageUp)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def right(self):
		if len(self["list"].list) > 0:
			while True:
				self["list"].instance.moveSelection(self["list"].instance.pageDown)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def up(self):
		if len(self["list"].list) > 0:
			while True:
				self["list"].instance.moveSelection(self["list"].instance.moveUp)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == 0:
					break

	def down(self):
		if len(self["list"].list) > 0:
			while True:
				self["list"].instance.moveSelection(self["list"].instance.moveDown)
				self.updateSummary(self["list"].l.getCurrentSelectionIndex())
				if self["list"].l.getCurrentSelection()[0][0] != "--" or self["list"].l.getCurrentSelectionIndex() == len(self["list"].list) - 1:
					break

	# runs a number shortcut
	def keyNumberGlobal(self, number):
		self.goKey(str(number))

	# runs the current selected entry
	def go(self):
		cursel = self["list"].l.getCurrentSelection()
		if cursel:
			self.goEntry(cursel[0])
		else:
			self.cancel()

	# runs a specific entry
	def goEntry(self, entry):
		if self.isCallbackList:
			if entry and len(entry) > 1 and entry[1]:
				# stuff the selected item's callback function into the dialog's session callback
				# (callers shouldn't need to be using the session callback)
				# This allows the ChoiceBox to close itself and schedule the selected item's
				# callback to happen on the next poll execution
				self.callback = boundFunction(*entry[1:])
			self.close()
		elif entry and len(entry) > 3 and isinstance(entry[1], str) and entry[1] == "CALLFUNC":
			arg = entry[3]
			entry[2](arg)
		elif entry and len(entry) > 2 and isinstance(entry[1], str) and entry[1] == "CALLFUNC":
			entry[2](None)
		else:
			self.close(entry)

	# lookups a key in the keymap, then runs it
	def goKey(self, key):
		if key in self.keymap:
			entry = self.keymap[key]
			self.goEntry(entry)

	# runs a color shortcut
	def keyRed(self):
		self.goKey("red")

	def keyGreen(self):
		self.goKey("green")

	def keyYellow(self):
		self.goKey("yellow")

	def keyBlue(self):
		self.goKey("blue")

	def updateSummary(self, curpos=0):
		self.displayDescription(curpos)
		pos = 0
		summarytext = ""
		for entry in self.summarylist:
			if curpos - 2 < pos < curpos + 5:
				if pos == curpos:
					summarytext += ">"
					self["summary_selection"].setText(entry[1])
				else:
					summarytext += entry[0]
				summarytext += ' ' + entry[1] + '\n'
			pos += 1
		self["summary_list"].setText(summarytext)

	def displayDescription(self, curpos=0):
		if self.list and len(self.list[curpos][0]) > 2 and isinstance(self.list[curpos][0][2], str):
			self["description"].setText(self.list[curpos][0][2])
		else:
			self["description"].setText("")

	def cancel(self):
		self.close(None)

	def setDefaultChoiceList(self):
		if self.reorderConfig:
			if len(self.list) > 0 and self.config_type.value != "":
				self.session.openWithCallback(self.setDefaultChoiceListCallback, MessageBox, _("Sort list to default and exit?"), MessageBox.TYPE_YESNO)
		else:
			self.cancel()

	def setDefaultChoiceListCallback(self, answer):
		if answer:
			self.config_type.value = ""
			self.config_type.save()
			self.cancel()

	def additionalMoveUp(self):
		if self.reorderConfig:
			self.additionalMove(-1)

	def additionalMoveDown(self):
		if self.reorderConfig:
			self.additionalMove(1)

	def additionalMove(self, direction):
		if len(self.list) > 1:
			currentIndex = self["list"].getSelectionIndex()
			swapIndex = (currentIndex + direction) % len(self.list)
			if currentIndex == 0 and swapIndex != 1:
				self.list = self.list[1:] + [self.list[0]]
			elif swapIndex == 0 and currentIndex != 1:
				self.list = [self.list[-1]] + self.list[:-1]
			else:
				self.list[currentIndex], self.list[swapIndex] = self.list[swapIndex], self.list[currentIndex]
			self["list"].l.setList(self.list)
			if direction == 1:
				self["list"].down()
			else:
				self["list"].up()
			self.config_type.value = ",".join(x[0][0] for x in self.list)
			self.config_type.save()


# This choicebox overlays the current screen
class PopupChoiceBox(ChoiceBox):
	def __init__(self, session, title="", list=None, keys=None, selection=0, skin_name=None, closeCB=None):
		ChoiceBox.__init__(self, session, title, None, keys, selection, skin_name, callbackList=list)
		self.closeCB = closeCB

	def show(self):
		self["actions"].execBegin()
		ChoiceBox.show(self)

	def hide(self):
		self["actions"].execEnd()
		ChoiceBox.hide(self)

	def goEntry(self, entry):
		self.cancel()
		if entry and len(entry) > 1:
			entry[1](*entry[2:])

	def cancel(self):
		# doClose will remove all properties so grab the callback function first
		cb = self.closeCB
		self.doClose()
		cb()
