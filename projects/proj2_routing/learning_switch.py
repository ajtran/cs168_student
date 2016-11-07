"""
Your learning switch warm-up exercise for CS-168.

Start it up with a commandline like...

  ./simulator.py --default-switch-type=learning_switch topos.rand --links=0

"""

import sim.api as api
import sim.basics as basics


class LearningSwitch(api.Entity):
    """
    A learning switch.

    Looks at source addresses to learn where endpoints are.  When it doesn't
    know where the destination endpoint is, floods.

    This will surely have problems with topologies that have loops!  If only
    someone would invent a helpful poem for solving that problem...

    """

    def __init__(self):
        """
        Do some initialization.

        You probablty want to do something in this method.

        """
        ## dictionary for the table of dst (which will be the src) and link it came from?
        self.table = {}

    def handle_link_down(self, port):
        """
        Called when a port goes down (because a link is removed)

        You probably want to remove table entries which are no longer
        valid here.

        """
        for dst, out_port in self.table.items():
            if out_port == port:
                del self.tables[dst]

    def handle_rx(self, packet, in_port):
        """
        Called when a packet is received.

        You most certainly want to process packets here, learning where
        they're from, and either forwarding them toward the destination
        or flooding them.

        """

        # Not sure if this should be before or after the discovery messages, but
        # this is about whether the src is in the table... later on, we got to make
        # these lists? for cycles?
        if packet.src not in self.table.keys():
            self.table[packet.src] = in_port

        # The source of the packet can obviously be reached via the input port, so
        # we should "learn" that the source host is out that port.  If we later see
        # a packet with that host as the *destination*, we know where to send it!
        # But it's up to you to implement that.  For now, we just implement a
        # simple hub.
        if isinstance(packet, basics.HostDiscoveryPacket):
            # Don't forward discovery messages
            return

        # we already know the dst of the packet, so we can just grab it from the table
        # and send it along its way.
        if packet.dst in self.table.keys():
            out_port = self.table[packet.dst]
            self.send(packet, out_port, flood=False)
        else:
            # Flood out all ports except the input port
            self.send(packet, in_port, flood=True)
