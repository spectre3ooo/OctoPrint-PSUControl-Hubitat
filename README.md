# OctoPrint PSU Control - Hubitat
Adds Hubitat support to OctoPrint-PSUControl as a sub-plugin.
This plugin was based on [OctoPrint-PSUControl-HomeAssistant](https://github.com/edekeijzer/OctoPrint-PSUControl-HomeAssistant) by edekeijzer.

## Setup
- Install the plugin using Plugin Manager from Settings
- Configure this plugin
- Select this plugin as Switching *and* Sensing method in [PSU Control](https://github.com/kantlivelong/OctoPrint-PSUControl)
- **Turn off** the *Automatically turn PSU ON* option in the PSU Control settings, leaving this on will ruin your prints when Hubitat becomes unavailable

## Support
Please check your logs first. If they do not explain your issue, open an issue in GitHub. Please set *octoprint.plugins.psucontrol* and *octoprint.plugins.psucontrol_hubitat* to **DEBUG** and include the relevant logs. Feature requests are welcome as well.
