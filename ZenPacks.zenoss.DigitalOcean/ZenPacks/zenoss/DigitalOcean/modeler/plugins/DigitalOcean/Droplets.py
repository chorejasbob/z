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

log = getLogger('zen.DigitalOcean.Droplets')

class Droplets(PythonPlugin):
    """Digital Ocean Droplet modeler plugin.

 |  Attributes returned by API:
 |      id (int): droplet id
 |      memory (str): memory size
 |      vcpus (int): number of vcpus
 |      disk (int): disk size in GB
 |      status (str): status
 |      locked (bool): True if locked
 |      created_at (str): creation date in format u'2014-11-06T10:42:09Z'
 |      status (str): status, e.g. 'new', 'active', etc
 |      networks (dict): details of connected networks
 |      kernel (dict): details of kernel
 |      backup_ids (:obj:`int`, optional): list of ids of backups of this droplet
 |      snapshot_ids (:obj:`int`, optional): list of ids of snapshots of this droplet
 |      action_ids (:obj:`int`, optional): list of ids of actions
 |      features (:obj:`str`, optional): list of enabled features. e.g.
 |                [u'private_networking', u'virtio']
 |      image (dict): details of image used to create this droplet
 |      ip_address (str): public ip addresses
 |      private_ip_address (str): private ip address
 |      ip_v6_address (:obj:`str`, optional): list of ipv6 addresses assigned
 |      end_point (str): url of api endpoint used
 |      volume_ids (:obj:`str`, optional): list of blockstorage volumes"""

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
                'backup_ids': droplet.backup_ids,
                'next_backup': droplet.next_backup_window.get('start'),
                'snapshot_ids': droplet.snapshot_ids,
                'features': droplet.features,
                'networks': droplet.networks,
                'vcpus': droplet.vcpus,
                'disk': droplet.disk,
                'volume_ids': droplet.volume_ids,
                'droplet_id': droplet.id,
                'image': image,
                'public_ip': droplet.ip_address,
                'private_ip': droplet.private_ip_address,
                'memory': droplet.memory,
                'region': region,
                'droplet_status': droplet.status,
                'droplet_locked': droplet.locked,
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
        """Model the Digital Ocean Droplets."""

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
                "Unable to retreive droplets for %s due to: %s" % (
                    device.id,
                    e.message
                ))
            returnValue(None)

        returnValue(droplets)

    def process(self, device, droplets, log):
        """Process droplets returned from api endpoint.
           Attributes and values that we model:
               id
               created_at
               backups
               backup_ids
               next_backup
               snapshot_ids
               features
               networks
               vcpus
               disk
               volume_ids
               droplet_id
               image
               public_ip
               private_ip
               memory
               region
               droplet_status
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
