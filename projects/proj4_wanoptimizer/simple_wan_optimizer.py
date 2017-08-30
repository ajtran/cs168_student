import wan_optimizer
from tcp_packet import Packet
import utils

class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into fixed-size blocks.

    This WAN optimizer should implement part 1 of project 4.
    """

    # Size of blocks to store, and send only the hash when the block has been
    # sent previously
    BLOCK_SIZE = 8000

    def __init__(self):
        wan_optimizer.BaseWanOptimizer.__init__(self)
        # Add any code that you like here (but do not add any constructor arguments).
        self.blocks = {} # key is src, dst; value is payload?
        self.cache = {} # key is hash; value is block payload (so self.BLOCK_SIZEB)?
        return

    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 1.  You are welcome to implement private
        helper fuctions that you call here. You should *not* be calling any functions
        or directly accessing any variables in the other middlebox on the other side of 
        the WAN; this WAN optimizer should operate based only on its own local state
        and packets that have been received.
        """
        pair = (packet.src, packet.dest)
        if pair not in self.blocks.keys():
            self.blocks[pair] = ""

        if packet.dest in self.address_to_port:
            # The packet is destined to one of the clients connected to this middlebox;
            # send the packet there.
            if packet.is_raw_data:
                self.blocks[pair] += packet.payload
                if len(self.blocks[pair]) >= self.BLOCK_SIZE:
                    payload, self.blocks[pair] = self.blocks[pair][:self.BLOCK_SIZE], self.blocks[pair][self.BLOCK_SIZE:]
                    hashkey = utils.get_hash(payload)
                    self.cache[hashkey] = payload
                    packets = (((len(payload) - 1) / utils.MAX_PACKET_SIZE) + 1)
                    if packet.is_fin and len(payload) == 0:
                        packets = 1
                    for i in range(packets):
                        currPayload = payload[i*utils.MAX_PACKET_SIZE:(i+1)*utils.MAX_PACKET_SIZE]
                        self.send(Packet(pair[0], pair[1], True, packet.is_fin and (i == packets-1), currPayload), self.address_to_port[pair[1]])
                if packet.is_fin and len(self.blocks[pair]) > 0:
                    payload, self.blocks[pair] = self.blocks[pair][:self.BLOCK_SIZE], self.blocks[pair][self.BLOCK_SIZE:]
                    hashkey = utils.get_hash(payload)
                    self.cache[hashkey] = payload
                    packets = (((len(payload) - 1) / utils.MAX_PACKET_SIZE) + 1)
                    if packet.is_fin and len(payload) == 0:
                        packets = 1
                    for i in range(packets):
                        currPayload = payload[i*utils.MAX_PACKET_SIZE:(i+1)*utils.MAX_PACKET_SIZE]
                        self.send(Packet(pair[0], pair[1], True, packet.is_fin and (i == packets-1), currPayload), self.address_to_port[pair[1]])
                elif packet.is_fin and packet.size() == 0:
                    self.send(Packet(pair[0], pair[1], True, True, ""), self.address_to_port[pair[1]])

            else:
                payload = self.cache[packet.payload]
                packets = (((len(payload) - 1) / utils.MAX_PACKET_SIZE) + 1)
                if packet.is_fin and len(payload) == 0:
                    packets = 1
                for i in range(packets):
                    currPayload = payload[i*utils.MAX_PACKET_SIZE:(i+1)*utils.MAX_PACKET_SIZE]
                    self.send(Packet(pair[0], pair[1], True, packet.is_fin and (i == packets-1), currPayload), self.address_to_port[pair[1]])

        else:
            # The packet must be destined to a host connected to the other middlebox
            # so send it across the WAN.
            self.blocks[pair] += packet.payload
            if len(self.blocks[pair]) >= self.BLOCK_SIZE:
                payload, self.blocks[pair] = self.blocks[pair][:self.BLOCK_SIZE], self.blocks[pair][self.BLOCK_SIZE:]
                hashkey = utils.get_hash(payload)
                if hashkey in self.cache.keys():
                    self.send(Packet(pair[0], pair[1], False, packet.is_fin, hashkey), self.wan_port)
                else:
                    self.cache[hashkey] = payload
                    packets = (((len(payload) - 1) / utils.MAX_PACKET_SIZE) + 1)
                    if packet.is_fin and len(payload) == 0:
                        packets = 1
                    for i in range(packets):
                        currPayload = payload[i*utils.MAX_PACKET_SIZE:(i+1)*utils.MAX_PACKET_SIZE]
                        self.send(Packet(pair[0], pair[1], True, packet.is_fin and (i == packets-1), currPayload), self.wan_port)
            if packet.is_fin and len(self.blocks[pair]) > 0:
                payload, self.blocks[pair] = self.blocks[pair][:self.BLOCK_SIZE], self.blocks[pair][self.BLOCK_SIZE:]
                hashkey = utils.get_hash(payload)
                if hashkey in self.cache.keys():
                    self.send(Packet(pair[0], pair[1], False, packet.is_fin, hashkey), self.wan_port)
                else:
                    self.cache[hashkey] = payload
                    packets = (((len(payload) - 1) / utils.MAX_PACKET_SIZE) + 1)
                    if packet.is_fin and len(payload) == 0:
                        packets = 1
                    for i in range(packets):
                        currPayload = payload[i*utils.MAX_PACKET_SIZE:(i+1)*utils.MAX_PACKET_SIZE]
                        self.send(Packet(pair[0], pair[1], True, packet.is_fin and (i == packets-1), currPayload), self.wan_port)
            elif packet.is_fin and packet.size() == 0:
                self.send(Packet(pair[0], pair[1], True, True, ""), self.wan_port)