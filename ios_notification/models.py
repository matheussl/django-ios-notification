"""
django-ios-push - Django Application for doing iOS Push Notifications
Originally written by Lee Packham (http://leenux.org.uk/ http://github.com/leepa)
Updated by Wojtek 'suda' Siudzinski <wojtek@appsome.co>

(c)2009 Lee Packham - ALL RIGHTS RESERVED
May not be used for commercial applications without prior concent.
"""

from django.db import models
from django.conf import settings

import socket

import datetime
import struct
import ssl
import binascii
import math

import exceptions

# Handle Python 2.5 / 2.6 seamlessly
try:
    import json
except ImportError:
    import simplejson as json


class Device(models.Model):
    """
    Represents an iPhone used to push

    device_token - the Device's token (64 chars of hex)
    last_notified_at - when was a notification last sent to the phone
    is_test_device - is this a phone that should be included in test runs
    notes - just a small notes field so that we can put in things like "Lee's iPhone"
    failed_phone - Have we had feedback about this phone? If so, flag it.
    """
    device_token = models.CharField(blank=False, max_length=64)
    last_notified_at = models.DateTimeField(
        blank=True, default=datetime.datetime.now)
    is_test_device = models.BooleanField(default=False)
    notes = models.CharField(blank=True, max_length=100)
    failed = models.BooleanField(default=False)
    platform = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = (('device_token', 'is_test_device'),)
        abstract = True

    def _get_apn_hostname(self):
        """
        Get the relevant hostname for the instance of the phone
        """
        if self.is_test_device:
            return settings.APN_SANDBOX_HOST
        else:
            return settings.APN_LIVE_HOST

    def _get_apn_cert_path(self):
        """
        Get the relevant certificate for the instance of the phone
        """
        cert = None
        if self.is_test_device:
            try:
                cert = getattr(settings, 'APN_SANDBOX_PUSH_CERT')
            except exceptions.AttributeError:
                raise exceptions.NotImplementedError(
                    'Configure the APN_SANDBOX_PUSH_CERT setting')
        else:
            try:
                cert = getattr(settings, 'APN_LIVE_PUSH_CERT')
            except exceptions.AttributeError:
                raise exceptions.NotImplementedError(
                    'Configure the APN_LIVE_PUSH_CERT setting')
        return cert


    def _send_push_message(self, token, payload,):
        """
        Send message to socket.
        """
        certfile = self._get_apn_cert_path()
        apn_hostname = self._get_apn_hostname()

        apns_address = (apn_hostname, 2195)

        # create socket and connect to APNS server using SSL
        s = socket.socket()
        sock = ssl.wrap_socket(
            s, ssl_version=ssl.PROTOCOL_SSLv3, certfile=certfile)
        sock.connect(apns_address)

        # generate APNS notification packet
        token = binascii.unhexlify(token)
        fmt = "!cH32sH{0:d}s".format(len(payload))
        cmd = '\x00'
        msg = struct.pack(fmt, cmd, len(token), token, len(payload), payload)
        sock.write(msg)
        sock.close()


    def send_push(self, message, extra={}):
        """
        Send push notification to device.
        """
        aps = {"alert": message, "badge": 9, "sound": "bingbong.aiff"}
        aps.update(extra)
        payload = {"aps": aps}
        self._send_push_message(self.device_token, json.dumps(payload))


def send_push_group(message, devices=[], extra={}):
    """
        Send push notification to device group.
    """
    for device in devices:
        device.send_push(message, extra=extra)
