import json
import digitalocean
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from Products.DataCollector.plugins.CollectorPlugins import PythonPlugin

class Droplets(PythonPlugin):
    """Digital Ocean Droplet modeler plugin."""

    relname = 'Droplets'
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

        if not zDigitalOceanToken:
            log.error("zDigitalOceanToken not set.")

            returnValue(None)

        #Setup the Connection to Digital Oceans API endpoint.
        manager = digitalocean.Manager(token=zDigitalOceanToken)
        try:
            droplets = yield manager.get_all_droplets()
        except Exception as err:
            log.error(
                "Unable to get droplets for %s due to: %s", 
                device.id, err)
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
                'region': droplet.region,
                'price_hourly': droplet.price_hourly,
                'price_monthly': droplet.price_monthly
            }))
        return rm
