##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2019, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

"""Models Digital Ocean Domains."""

import digitalocean
from twisted.internet.defer import inlineCallbacks, returnValue, DeferredList
from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from logging import getLogger

log = getLogger('zen.DigitalOcean.Domains')

class Domains(PythonPlugin):
    """Digital Ocean Domains modeler plugin."""

    relname = 'domains'
    modname = 'ZenPacks.zenoss.DigitalOcean.Domain'

    requiredProperties = (
        'zDigitalOceanToken',
        'zDigitalOceanApiEndpoint'
    )

    deviceProperties = PythonPlugin.deviceProperties + requiredProperties

    @inlineCallbacks
    def collect(self, device, log):
        """Model Digital Ocean Domains."""

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
            log.error("Unable to retreive Domains due to: %s" % (
                e.message
                ))
            returnValue(None)
        
        returnValue(domains)

    def process(self, device, domains, log):
        """Process Domains returned from API endpoint."""
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
