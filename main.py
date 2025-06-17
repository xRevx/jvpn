from configuration.vpn_config import VPNConfig
from tap_vpn_manager import TapVPNManager


def main():
    config = VPNConfig.build_json(r"/mnt/hgfs/jvpn/configuration/config.json")
    print(config.server_ip)

    manager = TapVPNManager()
    manager.delete_interface("tap0")
    manager.delete_interface("bridge0")

    # Create a TAP device named tap0
    #manager.create_tap("tap0")

    #manager.create_bridge("bridge0", "ens33", "tap0")

if __name__ == '__main__':
    main()