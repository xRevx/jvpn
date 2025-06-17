import asyncio
import os
import socket

from capsulation.cipher import xor_cipher
from configuration.vpn_config import VPNConfig


class VPNClient:
    def __init__(self, config: VPNConfig, tap_fd: int):
        self.config = config
        self.tap_fd = tap_fd
        self.sock = None

    def _create_udp_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        print("[+] UDP socket ready")

    async def _forward_loop(self):
        loop = asyncio.get_running_loop()
        while True:
            try:
                packet = await loop.run_in_executor(None, os.read, self.tap_fd, 2048)
                encrypted = xor_cipher(packet, self.config.encryption_key)
                await loop.sock_sendto(
                    self.sock, encrypted,
                    (self.config.server_ip, self.config.server_port)
                )
                print(f"[>] Sent {len(packet)} bytes to {self.config.server_ip}:{self.config.server_port}")
            except BlockingIOError:
                await asyncio.sleep(0.01)

    async def run(self):
        print(f"[+] VPN client running...")
        print(f"[+] Sending to {self.config.server_ip}:{self.config.server_port}")
        self._create_udp_socket()

        try:
            await self._forward_loop()
        except KeyboardInterrupt:
            print("[-] Client shutting down.")
        finally:
            if self.tap_fd:
                os.close(self.tap_fd)
            if self.sock:
                self.sock.close()
