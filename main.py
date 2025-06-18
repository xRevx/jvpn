import argparse
import asyncio
import sys

import logger
from configuration.vpn_config import VPNConfig
from connection.server import VPNPeer
from logger import log_error, set_log_file, log
from tap_vpn_manager import TapVPNManager

BRIDGE_NAME = "br0"

def load_config_from_args() -> VPNConfig:
    parser = argparse.ArgumentParser(description="Start the VPN peer.")
    parser.add_argument("config", help="Path to the VPN config file (JSON or YAML)")
    args = parser.parse_args()

    path = args.config
    if path.endswith(".json"):
        return VPNConfig.build_json(path)
    elif path.endswith((".yaml", ".yml")):
        return VPNConfig.build_yaml(path)
    else:
        raise ValueError("Unsupported config file type. Use .json or .yaml")

async def run_peer(config, tap_fd):
    peer = VPNPeer(config=config, tap_fd=tap_fd)
    await peer.run()

def main():
    config = load_config_from_args()
    set_log_file(config.log_file)
    print(f"Log file path: {config.log_file}")
    log("VPN started", "Loaded config")
    logger.log("VPN started", "Loaded config")
    manager = TapVPNManager()
    tap_fd = manager.setup_interfaces(config, BRIDGE_NAME)

    try:
        asyncio.run(run_peer(config, tap_fd))
    except KeyboardInterrupt:
        print("\n[!] Caught KeyboardInterrupt. Cleaning up...")
        manager.cleanup(config,tap_fd, BRIDGE_NAME)
        sys.exit(0)
    except Exception as e:
        log_error("main",f"Unexpected error: e")
        manager.cleanup(config, tap_fd, BRIDGE_NAME)
        sys.exit(1)

if __name__ == "__main__":
    main()
