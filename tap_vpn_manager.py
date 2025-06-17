import os
import fcntl
import struct
from pyroute2 import IPRoute, NetlinkError

TUNSETIFF = 0x400454ca
IFF_TAP = 0x0002
IFF_NO_PI = 0x1000

class TapVPNManager:
    def __init__(self):
        self.ipr = IPRoute()

    def create_tap(self, name: str) -> int:
        """Creates a TAP interface and returns its file descriptor."""
        if not os.path.exists('/dev/net/tun'):
            raise RuntimeError("/dev/net/tun not found. Is the TUN/TAP driver loaded?")

        # Create the TAP interface using pyroute2
        try:
            self.ipr.link("add", ifname=name, kind="tuntap", mode="tap", user=os.getuid())
            self.ipr.link("set", index=self.ipr.link_lookup(ifname=name)[0], state="up")
            print(f"[+] TAP interface '{name}' created and brought up.")
        except NetlinkError as e:
            raise RuntimeError(f"Failed to create TAP: {e}")

        # Open the interface for reading/writing
        fd = os.open("/dev/net/tun", os.O_RDWR | os.O_NONBLOCK)
        ifr = struct.pack("16sH", name.encode(), IFF_TAP | IFF_NO_PI)
        fcntl.ioctl(fd, TUNSETIFF, ifr)
        return fd

    def create_bridge(self, bridge_name, nic_name, tap_name):
        try:
            # Create bridge
            self.ipr.link('add', ifname=bridge_name, kind='bridge')
            bridge_idx = self.ipr.link_lookup(ifname=bridge_name)[0]
            self.ipr.link('set', index=bridge_idx, state='up')
            print(f"Bridge '{bridge_name}' created and brought up.")

            # Add NIC and TAP to bridge
            for dev in [nic_name, tap_name]:
                idx = self.ipr.link_lookup(ifname=dev)[0]
                self.ipr.link('set', index=idx, master=bridge_idx)
                print(f"Interface '{dev}' added to bridge '{bridge_name}'.")
        except NetlinkError as e:
            raise RuntimeError(f"Failed to set up bridge: {e}")

    def delete_interface(self, name):
        try:
            idx = self.ipr.link_lookup(ifname=name)[0]
            self.ipr.link('del', index=idx)
            print(f"Interface '{name}' deleted.")
        except IndexError:
            print(f"Interface '{name}' not found.")
        except NetlinkError as e:
            print(f"Failed to delete interface: {e}")
