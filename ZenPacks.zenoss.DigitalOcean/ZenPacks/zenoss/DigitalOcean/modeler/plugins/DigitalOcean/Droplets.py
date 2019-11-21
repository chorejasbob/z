##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2019, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Models Digital Ocean Droplets."""

import digitalocean
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from logging import getLogger

log = getLogger('zen.DigitalOcean')

class Droplets(PythonPlugin):
    """Digital Ocean Droplet modeler plugin."""

    relname = 'droplets'
    modname = 'ZenPacks.zenoss.DigitalOcean.Droplet'

    requiredProperties = (
        'zDigitalOceanToken',
        'zDigitalOceanApiEndpoint'
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Model device and return a deferred."""
        log.info("%s: collecting data", device.id)
        token = getattr(device, 'zDigitalOceanToken', None)
        if not token:
            log.error("zDigitalOceanToken not set.")
            returnValue(None)

        #Setup the Connection to Digital Oceans API endpoint.
        manager = digitalocean.Manager(token=token)
        try:
            droplets = yield manager.get_all_droplets()
        except Exception as err:
            log.error(
                "Unable to get droplets for %s due to: %s" % (
                    device.id,
                    err
                ))
            returnValue(None)

        returnValue(droplets)

    def process(self, device, droplets, log):
        """Process droplets returned from api endpoint.
           Attributes and values that we model:
               created_at
               backups
               vcpus
               disk
               id
               image
               ip_address
               private_ip_address
               memory
               name
               region
               price_hourly
               price_monthly 
        """
        log.info("Processing results for device %s." % device.id)
        rm = self.relMap()
        for droplet in droplets:
            rm.append(self.objectMap({
                'created_at': droplet.created_at,
                'backups': droplet.backups,
                'vcpus': droplet.vcpus,
                'disk': droplet.disk,
                'id': droplet.id,
                'image': droplet.image,
                'ip_address': droplet.ip_address,
                'private_ip_address': droplet.private_ip_address,
                'memory': droplet.memory,
                'name': droplet.name,
                'region': droplet.region
            }))

        return rm
