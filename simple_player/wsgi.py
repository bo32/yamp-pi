"""
WSGI config for simple_player project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_player.settings')

application = get_wsgi_application()

# Load global properties
import player.global_properties
from player.global_properties import get_boolean_property_value

# TODO Add option to auto turn off

if get_boolean_property_value('server', 'enable_gamepads'):
    print('Enabling gamepads service...')
    from devices.services.gamepad_service import GamepadService
    GamepadService().attach_gamepad()

if get_boolean_property_value('server', 'enable_nfc_scanning'):
    print('Enabling NFC service...')
    from nfc_reader.services.nfc_service import NfcService
    NfcService().start()
