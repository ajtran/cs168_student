"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        self.VECTORS = {} # key = host, value = [next hop port, distance to get to host, timestamp]
        self.HOSTS = {} # key = host, value = [port, latency]
        self.PORTS = {} # key = port, value = latency on that port, host?
        # self.noflyzone = []

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """

        #add port--> latency mapping
        self.PORTS[port] = latency

        #send table to router at other end of the port
        for host, linkInfo in self.VECTORS.items():
            self.send(basics.RoutePacket(host, linkInfo[1] + latency), port)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        # since the link went down we have to remove it from our self.PORTS table
        if self.POISON_MODE:
            self.PORTS[port] = INFINITY
        else:
            del self.PORTS[port]

        # since there may be paths that use this link/port as the next hop, we have to remove all the entries in our distance vector 
        # table that use this port on their path
        for host, linkInfo in self.VECTORS.items():
            if port == linkInfo[0]:
                if self.POISON_MODE:
                    self.VECTORS[host][1] = INFINITY
                else:
                    del self.VECTORS[host]

        for host, linkInfo in self.HOSTS.items():
            if port == linkInfo[0]:
                if self.POISON_MODE:
                    self.HOSTS[host][1] = INFINITY
                else:
                    del self.HOSTS[host]

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        # self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):

            dst, latency = packet.destination, packet.latency #parse dst and latency --> compare it to own vector table, if it's shorter path than change, otherwise nothing
            if dst not in self.VECTORS.keys() or latency <= self.VECTORS[dst][1] or (self.POISON_MODE and latency >= INFINITY):
                self.VECTORS[dst] = [port, latency, api.current_time()]

        elif isinstance(packet, basics.HostDiscoveryPacket):

            host, latency = packet.src, self.PORTS[port] #parse out the host entity and its corresponding latency from self.PORTS
            self.VECTORS[host] = [port, latency, api.current_time()]
            self.HOSTS[host] = [port, latency] #create an entry in the self.VECTORS table 

        else:

            src, dst = packet.src, packet.dst #parse out the src and dst
            if dst in self.VECTORS.keys(): #if we have a path to the dst for this packet, then we find the next hop in the self.VECTORS table which should be an outport
                outport = self.VECTORS[dst][0] 
                if outport != port:
                    if self.POISON_MODE and self.VECTORS[dst][1] >= INFINITY:
                        del self.VECTORS[dst]
                    else:
                        self.send(packet, outport)

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        # so basically this is how the tables keep updating themselves. not sure if we should add the port latency though...
        for host, linkInfo in self.HOSTS.items():
            if host not in self.VECTORS.keys() or api.current_time() - self.VECTORS[host][2] >= self.ROUTE_TIMEOUT:
                self.VECTORS[host] = [linkInfo[0], linkInfo[1], api.current_time()]

        for port, latency in self.PORTS.items():
            for host, linkInfo in self.VECTORS.items():

                if api.current_time() - linkInfo[2] < self.ROUTE_TIMEOUT:

                    if port != linkInfo[0]:
                        if self.POISON_MODE and linkInfo[1] >= INFINITY:
                            self.send(basics.RoutePacket(host, INFINITY), port)
                        else:
                            self.send(basics.RoutePacket(host, linkInfo[1] + latency), port)

                else:

                    del self.VECTORS[host]