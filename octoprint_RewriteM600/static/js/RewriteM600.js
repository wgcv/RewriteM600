/*
 * View model for RewriteM600
 *
 * Author: Gustavo Cevallos
 * License: MIT
 */
$(function() {
    function Rewritem600ViewModel(parameters) {
        var self = this;
		
		self.settings = parameters[0];
		self.defaultPause = ko.observable();
		self.defaultResume = ko.observable();

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];
		
		self.onBeforeBinding = function() {
			console.log(self.settings);
            self.defaultPause(self.settings.settings.plugins.RewriteM600.defaultPause());
			self.defaultResume(self.settings.settings.plugins.RewriteM600.defaultResume());
        }

        // TODO: Implement your plugin's view model here.
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin !== "RewriteM600") {
				return;
			}
			if(data.type == "popup") {
				console.log(data.msg);
					new PNotify({
						title: 'M600',
						text: data.msg,
						type: "info",
						hide: true
						});
				}
            }
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: Rewritem600ViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ "settingsViewModel"/* "loginStateViewModel", "settingsViewModel" */ ],
        // Elements to bind to, e.g. #settings_plugin_RewriteM600, #tab_plugin_RewriteM600, ...
        elements: [  ]
    });
});
