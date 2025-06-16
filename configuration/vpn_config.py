import json
import yaml  # Requires `pip install pyyaml`

class VPNConfig:
    def __init__(self, data):
        server = data.get('server', {})
        self.server_ip = server.get('ip')
        self.server_port = server.get('port')
        self.encryption_key = int(data.get('encryption_key', '0'), 16)
        self.log_file = data.get('log_file')
        self.timeout = data.get('timeout')
        self.reconnection = data.get('reconnection')
        self.bridged_interface = data.get('bridged_interface')

    @classmethod
    def build_json(cls, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(data)

    @classmethod
    def build_yaml(cls, path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(data)

    def __repr__(self):
        return (
            "VPNConfig(\n"
            f"  server_ip={self.server_ip},\n"
            f"  server_port={self.server_port},\n"
            f"  encryption_key=0x{self.encryption_key:X},\n"
            f"  log_file='{self.log_file}',\n"
            f"  timeout={self.timeout},\n"
            f"  reconnection={self.reconnection},\n"
            f"  bridged_interface='{self.bridged_interface}'\n"
            ")"
        )
