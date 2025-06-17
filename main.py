import argparse
import asyncio

from capsulation.cipher import xor_cipher
from configuration.vpn_config import VPNConfig
from connection.client import VPNClient
from connection.server import VPNServer
from tap_vpn_manager import TapVPNManager


def load_config_from_args() -> VPNConfig:
    parser = argparse.ArgumentParser(description="Start the VPN client/server.")
    parser.add_argument("config", help="Path to the VPN config file (JSON or YAML)")
    args = parser.parse_args()

    path = args.config
    if path.endswith(".json"):
        return VPNConfig.build_json(path)
    elif path.endswith((".yaml", ".yml")):
        return VPNConfig.build_yaml(path)
    else:
        raise ValueError("Unsupported config file type. Use .json or .yaml")

async def main():
    config = load_config_from_args()
    print(config.server_ip)

    manager = TapVPNManager()
    manager.delete_interface("tap0")
    manager.delete_interface("br0")
    #client ens33 server ens37 bridge
    tap_fd = manager.create_tap(config.tap_name)
    manager.create_bridge("br0", config.bridged_interface ,config.tap_name)

    server = VPNServer(config=config, tap_fd=tap_fd)
    client = VPNClient(config=config, tap_fd=tap_fd)

    await asyncio.gather(
        server.run(),
        client.run()
    )

if __name__ == '__main__':
    asyncio.run(main())