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

    def buildObjectMap(self, droplet):
        try:
            name = self.prepId(droplet.name)
            region = self.prepId(droplet.region.get('name'))
            image = self.prepId(droplet.image.get('name'))
            data = {
                'id': name,
                'created_at': droplet.created_at,
                'backups': droplet.backups,
                'vcpus': droplet.vcpus,
                'disk': droplet.disk,
                'droplet_id': droplet.id,
                'image': image,
                'ip_address': droplet.ip_address,
                'private_ip_address': droplet.private_ip_address,
                'memory': droplet.memory,
                'region': region,
                'status': droplet.status,
                'tags': droplet.tags,
                'price_hourly': droplet.size.get('price_hourly'),
                'price_monthly': droplet.size.get('price_monthly'),
                }
            return(data)
        except Exception, e:
            log.error("Problem encountered: %s", e.message)
            log.error("Droplet data: %s" % droplet)

    @inlineCallbacks
    def collect(self, device, log):
        """Model device and return a deferred."""
        log.info("%s: collecting data", device.id)
        token = getattr(device, 'zDigitalOceanToken', None)
        if not token:
            log.error("zDigitalOceanToken not set.")
            returnValue(None)

        #Setup the Connection to the Digital Ocean API endpoint.
        try:
            manager = digitalocean.Manager(token=token)
            droplets = yield manager.get_all_droplets()
        except Exception, e:
            log.error(
                "Unable to get droplets for %s due to: %s" % (
                    device.id,
                    e.message)
                )
            returnValue(None)

        returnValue(droplets)

    def process(self, device, droplets, log):
        """Process droplets returned from api endpoint.
           Attributes and values that we model:
               id
               created_at
               backups
               vcpus
               disk
               droplet_id
               image
               ip_address
               private_ip_address
               memory
               region
               status
               tags
               price_hourly
               price_monthly
        """
        log.info("Processing %d results for device %s." % (
            len(droplets),
            device.id)
            )

        rm = self.relMap()
        for droplet in droplets:
            if droplet:
                try:
                    rm.append(
                        self.objectMap(buildObjectMap(droplet))
                        )
                except Exception, e:
                    log.error("Problem encountered: %s", e)

        return rm
