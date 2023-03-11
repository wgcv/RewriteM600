# RewriteM600

Implement M600 for pinters that can't support M600 by default (TFT with out Marlin Mode support, like the Artillery Sidewinder X1 and Genius). You can use M600, it will stop and wait until you change and press resume. If you have a TFT 28 (like the Artillery) I would recomend you check out [Rawr TFT Firmware](https://github.com/wgcv/RAWR-TFT-Firmware-Artillery3D) to implement M600 direct in the TFT then do not need Octoprint.

## Setup

Install via the bundled [Plugin Manager](https://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html).

OctoPrint Settings (Wrench) -> Plugin Mananger -> Get More -> Page the url in From URL and press Install. 

After install restart the instance.

Copy or manually using this URL:

    https://github.com/wgcv/RewriteM600/archive/master.zip

## Configuration

As this plugin only tries to recognize the correct pausing position as a response to the `M114`-marlin-command, it is possible to change the default behaviour.
The plugin provides the dict `cached_position` (with members `x`, `y`, `z` and `e`) to the GCODE-Script `beforePrintResumed`. You can access them via `{{plugins.RewriteM600.cached_position.(x|y|z|e)}}`.

## Screenshots

![Screenshot](https://github.com/wgcv/plugins.octoprint.org/raw/gh-pages/assets/img/plugins/RewriteM600/M600-in-action.png
)

## Support

You can help this project by reporting issues, making PR or Sponsor it [PayPal](https://paypal.me/wgcv).
