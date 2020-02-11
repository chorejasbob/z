##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2019, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Models Digital Ocean DNS."""

import digitalocean
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from logging import getLogger

log = getLogger('zen.DigitalOcean.Dns')

class Dns(PythonPlugin):
    """Digital Ocean Dns modeler plugin."""

    relname = 'dns'
    modname = 'ZenPacks.zenoss.DigitalOcean.Dns'

    requiredProperties = (
        'zDigitalOceanToken',
        'zDigitalOceanApiEndpoint'
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Model Digital Ocean Dns."""

        log.info("%s: collecting data", device.id)
        token = getattr(device, 'zDigitalOceanToken', None)
        if not token:
            log.error("zDigitalOceanToken not set.")
            returnValue(None)

        #Setup the Connection to the Digital Ocean API endpoint.
        try:
            manager = digitalocean.Manager(token=token)
            domains = manager.get_all_domains()
        except Exception, e:
            log.error("Unable to retreive Dns due to: %s" % (
                e.message
                ))
            returnValue(None)
        
        returnValue(domains)

    def process(self, device, domains, log):
        """Process Dns returned from API endpoint."""
        if domains:
            rm = self.relMap()
            for domain in domains:
                try:
                    name = self.prepId(domain.name)
                    ttl = domain.ttl
                    zone_file = domain.zone_file
                    records = len(domain.get_records())
                    rm.append(self.objectMap(
                        data = {
                            'id': name,
                            'records': records,
                            'ttl': ttl,
                            'zone_file': zone_file,
                            }))
                except Exception, e:
                    log.error("Error creating relMap: %s" % e.message)
