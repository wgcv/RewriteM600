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

	def rewrite_m600(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if gcode and gcode == "M600":
			self._plugin_manager.send_plugin_message(self._identifier,
			                                         dict(type = "popup",
			                                              msg = "Please change the filament and resume the print"))
			comm_instance.setPause(True)
			self.listening = True  # We need to listen to the first result of M114, so we can cache position
			cmd = ["M114", ("M117 Filament Change",), "G91", "M83", "G1 Z+" + str(self._settings.get(["zDistance"])) + " E-0.8 F4500", "M82", "G90", "G1 X0 Y0 F4500"]
			self._logger.info(self.cached_position)
			self.waiting = True
		elif gcode and gcode == "M601":
			self._plugin_manager.send_plugin_message(self._identifier, dict(type="popup", msg = self.cached_position))
			if self.cached_position["x"] != "NOT SET":
				cmd = [
					# We'll assume that the user manually inserted and purged the new filament, so no new extrusion
					# is required here
					# "M83", "G1 E-0.8 F4500", "G1 E0.8 F4500", "G1 E0.8 F4500",
					"M82", "G90",  # Reset to absolute positioning
					# I don't think we really need the extrusion to be set here?
					# The gcode that follows will set it itself.
					# "G92 E" + str(self.cached_position["e"]),
					"M83",  # Reset our extruder mode to absolute
					# Reset our position to pre-M600 positions
					"G1 Z" + str(self.cached_position["z"]),
					"G1 X" + str(self.cached_position["x"]) +
					" Y" + str(self.cached_position["y"]) + " F4500"]
				if comm_instance.pause_position.f:
					cmd.append("G1 F" + str(comm_instance.pause_position.f))
				self.cached_position = {"x": "NOT SET", "y": "NOT SET", "z": "NOT SET", "e": "NOT SET"}
				comm_instance.setPause(False)

		return cmd

	def detect_position(self, comm_instance, line, *args, **kwargs):
		match = re.match("X:([0-9.]+) Y:([0-9.]+) Z:([0-9.]+) E:-?([0-9.]+) Count X:([0-9]+) Y:([0-9]+) Z:([0-9]+)", 0line)
		if match is not None and self.listening:
			self.cached_position["x"] = match.group(1)
			self.cached_position["y"] = match.group(2)
			self.cached_position["z"] = match.group(3)
			self.cached_position["e"] = match.group(4)
			self._plugin_manager.send_plugin_message(self._identifier, dict(type="popup", msg = "Saved location at X:" +
								self.cached_position["x"] + " Y:" + self.cached_position["y"] +
								" Z:" + self.cached_position["z"]))
			self.listening = False  # Reset so we don't listen to the update called on print pause
			self._logger.info(self.cached_position)
		return line

	def after_resume(self, comm_instance, line, action, *args, **kwargs):
		self._logger.info("Received queued command: " + action)
		if self.waiting and cmd == "resume":
			self._logger.info("Resuming from Filament Change")
			self.waiting = False
			self._plugin_manager.send_plugin_message(self._identifier, dict(type = "popup", msg = "Resuming to location at X:" +
								self.cached_position["x"] + " Y:" + self.cached_position["y"] +
								" Z:" + self.cached_position["z"]))
			if self.cached_position["x"] != "NOT SET":  # use our cached position
				tmp = cmd
				cmd = [
					# We'll assume that the user manually inserted and purged the new filament, so no new extrusion
					# is required here
					# "M83", "G1 E-0.8 F4500", "G1 E0.8 F4500", "G1 E0.8 F4500",
					"M83", "G1 Z-" + str(self._settings.get(["zDistance"])) + " F4500",
					"M82", "G90",  # Reset to absolute positioning
					# I don't think we really need the extrusion to be set here?
					# The gcode that follows will set it itself.
					# "G92 E" + str(self.cached_position["e"]),
					"M83",  # Reset our extruder mode to absolute
					# Reset our position to pre-M600 position
					"G1 Z" + str(self.cached_position["z"]),
					"G1 X" + str(self.cached_position["x"]) +
					" Y" + str(self.cached_position["y"]) + " F4500"]
				cmd.extend(tmp)
				if comm_instance.pause_position.f:
					cmd.append("G1 F" + str(comm_instance.pause_position.f))
				self.cached_position = {"x": "NOT SET", "y": "NOT SET", "z": "NOT SET", "e": "NOT SET"}
			comm_instance.commands(cmd)
			comm_instance.setPause(False)
		return

	def get_settings_defaults(self):
		return dict(zDistance = 80)

	def get_template_configs(self):
		return [
			dict(type = "navbar", custom_bindings = False),
			dict(type = "settings", custom_bindings = False)
		]

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js = ["js/RewriteM600.js"],
			css = ["css/RewriteM600.css"],
			less = ["less/RewriteM600.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			RewriteM600 = dict(
				displayName = "Rewritem600 Plugin",
				displayVersion = self._plugin_version,

				# version check: github repository
				type = "github_release",
				user = "wgcv",
				repo = "RewriteM600",
				current = self._plugin_version,

				# update method: pip
				pip = "https://github.com/wgcv/RewriteM600/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Filament Change - M600 Rewriter"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
# __plugin_pythoncompat__ = ">=3,<4" # only python 3
__plugin_pythoncompat__ = ">=2.7,<4"  # python 2 and 3


def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = Rewritem600Plugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.rewrite_m600,
		"octoprint.comm.protocol.atcommand.queuing": __plugin_implementation__.after_resume,
		"octoprint.comm.protocol.gcode.received": __plugin_implementation__.detect_position,
	}
