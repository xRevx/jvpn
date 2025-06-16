from configuration.vpn_config import VPNConfig


def main():
    config = VPNConfig.build_json(r"C:\projects\jvpn\configuration\config.json")
    print(config.server_ip)

if __name__ == '__main__':
    main()