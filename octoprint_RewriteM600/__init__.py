# coding=utf-8
from __future__ import absolute_import
import re

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin

class Rewritem600Plugin(octoprint.plugin.AssetPlugin, octoprint.plugin.TemplatePlugin, octoprint.plugin.SettingsPlugin):
	cached_position = {"x": "NOT SET", "y": "NOT SET", "z": "NOT SET", "e": "NOT SET"}
	listening = False
	waiting = False
	waitingForPause = False;
	waitingForResume = False;
	resumeScript = None;
	
	def on_settings_initialized(self):
		scripts = self._settings.listScripts("gcode")
		if not "rewrite_m600_pause" in scripts:
			self._settings.saveScript("gcode", "rewrite_m600_pause", u'' + self._settings.get(["pauseCommand"]))
		if not "rewrite_m600_resume" in scripts:
			self._settings.saveScript("gcode", "rewrite_m600_resume", u'' + self._settings.get(["resumeCommand"]))
			
	def on_settings_save(self, data):
		if 'pauseCommand' in data:
			script = data["pauseCommand"]
			self._settings.saveScript("gcode", "rewrite_m600_pause", u'' + script.replace("\r\n", "\n").replace("\r", "\n"))
			# data.pop('pauseCommand')
		if 'resumeCommand' in data:
			script = data["resumeCommand"]
			self._settings.saveScript("gcode", "rewrite_m600_resume", u'' + script.replace("\r\n", "\n").replace("\r", "\n"))
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

	def rewrite_m600(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if gcode and gcode == "M600":
			self._logger.info("rewrite_m600")
			self._plugin_manager.send_plugin_message(self._identifier,
			                                         dict(type = "popup",
			                                              msg = "Please change the filament and resume the print"))
			self.listening = True
			cmd = ["G4 S" + str(self._settings.get(["timeG4"])), "M114", "G4 S" + str(self._settings.get(["timeG4"])), "@setpause"]
			self._logger.info(cmd)
			self._logger.info(self.cached_position)
			self.waiting = True
			self.waitingForPause = True;
		return cmd
	
	def toggle_pause(self, comm_instance, phase, command, parameters, tags=None, *args, **kwargs):
		if command == "setpause" and self.waitingForPause:
			self._logger.info("setpause")
			if self._settings.get(["defaultPause"]):
				comm_instance.setPause(True)
			else:
				comm_instance.setPause(True, local_handling = False) # sorgt dafür, dass das Pause-Script nicht ausgeführt wird!
				self._printer.script("rewrite_m600_pause", must_be_set=False)
			self.waitingForPause = False
		if command == "afterResumed" and self.waitingForResume:
			self._logger.info("afterResumed")
			self._settings.saveScript("gcode", "beforePrintResumed", u'' + self.resumeScript)
			self.waitingForResume = False

	def detect_position(self, comm_instance, line, *args, **kwargs):
		#	ok X:20.0 Y:20.0 Z:0.6 E:20.01306 Count: A:2000 B:2000 C:60
		# match = re.match("X:([0-9.]+) Y:([0-9.]+) Z:([0-9.]+) E:-?([0-9.]+) Count X|A:([0-9]+) Y|B:([0-9]+) Z|C:([0-9]+)", line)
		match = re.search(self._settings.get(["regularExpression"]), line)
		if match is not None and self.listening:
			self._logger.info("DetectPosition: " + line)
			self.cached_position["x"] = match.group(self._settings.get(["x"]))
			self.cached_position["y"] = match.group(self._settings.get(["y"]))
			self.cached_position["z"] = match.group(self._settings.get(["z"]))
			self.cached_position["e"] = match.group(self._settings.get(["e"]))
			self._logger.info("CachedPosition: " + self.cached_position["x"])
			self._plugin_manager.send_plugin_message(self._identifier, dict(type="popup", msg = "Saved location at X:" +
								self.cached_position["x"] + " Y:" + self.cached_position["y"] +
								" Z:" + self.cached_position["z"]))
			self.listening = False  # Reset so we don't listen to the update called on print pause
			self._logger.info(self.cached_position)
		return line

	def after_resume(self, comm_instance, script_type, script_name, *args, **kwargs):
		self._logger.info("Received queued command: " + script_name)
		if self.waiting and script_type == "gcode" and script_name == "beforePrintResumed":
			self._logger.info("Resuming from Filament Change")
			self.waiting = False
			self._plugin_manager.send_plugin_message(self._identifier, dict(type = "popup", msg = "Resuming to location at X:" +
								self.cached_position["x"] + " Y:" + self.cached_position["y"] +
								" Z:" + self.cached_position["z"]))
			variables = dict(cached=self.cached_position)
			if not self._settings.get(["defaultResume"]):
				# Script ausführen
				self._printer.script("rewrite_m600_resume", context=variables, must_be_set=False)
				# script laden & leeren
				self.resumeScript = self._settings.loadScript("gcode", "beforePrintResumed", source=True)
				self._settings.saveScript("gcode", "beforePrintResumed", u'')
				self.waitingForResume = True
			self.cached_position = {"x": "NOT SET", "y": "NOT SET", "z": "NOT SET", "e": "NOT SET"}
			return None, ["@afterResumed"], variables

	def get_settings_defaults(self):
		return dict(x = 1, y = 2, z = 3, e = 4, timeG4 = 5, pauseCommand = "", resumeCommand = "", defaultPause = True, defaultResume = True, regularExpression = "X:([0-9.]+) Y:([0-9.]+) Z:([0-9.]+) E:-?([0-9.]+) Count:? (X|A):([0-9]+) (Y|B):([0-9]+) (Z|C):([0-9]+)")

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js = ["js/RewriteM600.js"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			RewriteM600=dict(
				displayName="Rewritem600 Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="wgcv",
				repo="RewriteM600",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/wgcv/RewriteM600/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Filament Change - M600 Rewriter"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
#__plugin_pythoncompat__ = ">=2.7,<3" # only python 2
#__plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = Rewritem600Plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.rewrite_m600,
		"octoprint.comm.protocol.scripts": __plugin_implementation__.after_resume,
		"octoprint.comm.protocol.gcode.received": __plugin_implementation__.detect_position,
		"octoprint.comm.protocol.atcommand.queuing": __plugin_implementation__.toggle_pause,
	}
