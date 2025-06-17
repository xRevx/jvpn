from pyroute2 import IPRoute, NetlinkError
import os

class TapVPNManager:
    def __init__(self):
        self.ipr = IPRoute()

    def create_tap(self, name):
        # Use /dev/net/tun to create a TAP interface
        if not os.path.exists('/dev/net/tun'):
            raise RuntimeError("/dev/net/tun not found. Is the TUN/TAP driver loaded?")

        try:
            self.ipr.link('add',
                          ifname=name,
                          kind='tuntap',
                          mode='tap',
                          user=os.getuid())  # assign to current user
            self.ipr.link('set', index=self.ipr.link_lookup(ifname=name)[0], state='up')
            print(f"TAP interface '{name}' created and brought up.")
        except NetlinkError as e:
            raise RuntimeError(f"Failed to create TAP: {e}")

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
