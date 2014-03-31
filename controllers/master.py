# -*- coding: utf-8 -*-

"""
    Master Data - Controllers

    @author: Fran
"""

module = request.controller

if module not in deployment_settings.modules:
    raise HTTP(404, body="Module disabled: %s" % module)

# Options Menu (available in all Functions' Views)
shn_menu(module)

def index():
    "Module's Home Page"

    module_name = deployment_settings.modules[module].name_nice
    response.title = module_name
    return dict(module_name=module_name)
