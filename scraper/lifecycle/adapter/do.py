from django.conf import settings

import digitalocean as api

from core import logging

from . import models


logger = logging.getLogger(__name__)


class Lifecycle:
    """ Manage mark and sweep to servers using digitalocean """
    name = 'object'

    def __init__(self, token=None):
        self.token = token or settings.DO_TOKEN

    def servers(self):
        manager = api.Manager(token=self.token)

        servers = []
        for d in manager.get_all_droplets():
            if not d.name.startswith(self.name):
                continue
            servers.append(d)

        return servers

    def next_version_number(self):
        versions = []
        for s in self.servers():
            num = s.name.replace(self.name, '')
            versions.append(int(num))

        if not versions:
            return 1

        return sorted(versions)[-1] + 1

    def resurrect(self, size=1, image=None, ssh_keys=None):
        version = self.next_version_number()

        tag = api.Tag(token=self.token, name=self.name)
        tag.create()  # create tag if not already created

        result = []
        for _ in range(0, size):
            server = api.Droplet(
                token=self.token,
                name=f"{self.name}{version}",
                region='sgp1',
                size='512mb',
                private_networking=True,
                ipv6=True,
                backups=False,
                ssh_keys=ssh_keys or settings.DO_SSH_KEYS,
                image=image or settings.DO_OBJECT_IMAGE
                #  tags=[tag],
            )

            r = server.create()
            if r or r is None:
                tag.add_droplets([str(server.id)])

            result.append((server, r))

        return result

    def mark(self):
        qs = models.Node.objects
        node = qs.filter(usable=True).order_by('id').first()
        if not node:
            return

        node.usable = False
        node.save()

    def marked_servers(self):
        qs = models.Node.objects
        qs = qs.filter(usable=False).all()

        servers, marked = [], list(qs)
        for d in self.servers():
            check = [m for m in marked if d.name == m.name]
            if any(check):
                servers.append(d, check)
                continue

            check = [m for m in marked if d.private_ip_address in m.host]
            if any(check):
                servers.append(d, check)
                continue

        return servers

    def sweep(self):
        result = []
        for droplet, nodes in self.marked_servers():
            r = droplet.destroy()
            if r or r is None:
                for n in nodes:
                    n.delete()

            result.append((droplet, r))

        return result

    def samsara(self):
        self.sweep()
        self.resurrect()
        self.mark()
