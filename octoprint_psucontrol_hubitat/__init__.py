# coding=utf-8
from __future__ import absolute_import

__author__ = "Troy Stephens <stephens.ta@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2023 Troy Stephens - Released under terms of the AGPLv3 License"

import octoprint.plugin
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class PSUControl_Hubitat(octoprint.plugin.StartupPlugin,
                         octoprint.plugin.RestartNeedingPlugin,
                         octoprint.plugin.TemplatePlugin,
                         octoprint.plugin.SettingsPlugin):

    def __init__(self):
        self.config = dict()

    def get_settings_defaults(self):
        return dict(
            address = '',
            access_token = '',
            app_id = '',
            device_id = '',
        )

    def on_settings_initialized(self):
        self.reload_settings()

    def reload_settings(self):
        for k, v in self.get_settings_defaults().items():
            if type(v) == str:
                v = self._settings.get([k])
            elif type(v) == int:
                v = self._settings.get_int([k])
            elif type(v) == float:
                v = self._settings.get_float([k])
            elif type(v) == bool:
                v = self._settings.get_boolean([k])

            self.config[k] = v
            self._logger.debug("{}: {}".format(k, v))

    def on_startup(self, host, port):
        psucontrol_helpers = self._plugin_manager.get_helpers("psucontrol")
        if not psucontrol_helpers or 'register_plugin' not in psucontrol_helpers.keys():
            self._logger.warning("The version of PSUControl that is installed does not support plugin registration.")
            return

        self._logger.debug("Registering plugin with PSUControl")
        psucontrol_helpers['register_plugin'](self)

    def send(self, cmd=None):
        
        url = None
        if(cmd):
            # http://192.168.10.44/apps/api/73/devices/[Device ID]/[Command]/[Secondary value]?access_token=a95c5a5e-5007-433d-9f4e-fbae7b3ef373
            url = 'http://{}/apps/api/{}/devices/{}/{}?access_token={}'.format(self.config['address'], self.config['app_id'], self.config['device_id'], cmd, self.config['access_token'])
        else:
            # http://192.168.10.44/apps/api/73/devices/[Device ID]?access_token=a95c5a5e-5007-433d-9f4e-fbae7b3ef373
            url = 'http://{}/apps/api/{}/devices/{}?access_token={}'.format(self.config['address'], self.config['app_id'], self.config['device_id'], self.config['access_token'])

        response = None
        try:
            response = requests.get(url)
        except (
                requests.exceptions.InvalidURL,
                requests.exceptions.ConnectionError
        ):
            self._logger.error("Unable to communicate with server. Check settings.")
        except Exception:
            self._logger.exception("Exception while making API call")
        else:
            self._logger.debug("cmd={}, status_code={}, text={}".format(cmd, response.status_code, response.text))

            if response.status_code == 401:
                self._logger.warning("Server returned 401 Unauthorized. Check access token.")
                response = None
            elif response.status_code == 404:
                self._logger.warning("Server returned 404 Not Found. Check App and Device ID.")
                response = None

        return response

    def change_psu_state(self, state):
        self.send(state)

    def turn_psu_on(self):
        self._logger.debug("Switching PSU On")
        self.change_psu_state('on')

    def turn_psu_off(self):
        self._logger.debug("Switching PSU Off")
        self.change_psu_state('off')

    def get_psu_state(self):
        
        response = self.send()
        if not response:
            return False
        data = response.json()

        status = None
        try:
            status = (data['attributes'][0]['currentValue'] == 'on')
        except KeyError:
            pass

        if status == None:
            self._logger.error("Unable to determine status. Check settings.")
            status = False

        return status

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.reload_settings()

    def get_settings_version(self):
        return 1

    def on_settings_migrate(self, target, current=None):
        pass

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_update_information(self):
        return dict(
            psucontrol_hubitat=dict(
                displayName="PSU Control - Hubitat",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="spectre3ooo",
                repo="OctoPrint-PSUControl-Hubitat",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/spectre3ooo/OctoPrint-PSUControl-Hubitat/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "PSU Control - Hubitat"
__plugin_pythoncompat__ = ">=3,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PSUControl_Hubitat()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }