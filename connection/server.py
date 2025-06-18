import asyncio
import os
import socket

from configuration.vpn_config import VPNConfig
from capsulation.cipher import xor_cipher


class VPNPeer:
    def __init__(self, config: VPNConfig, tap_fd: int):
        self.config = config
        self.tap_fd = tap_fd
        self.sock = None
        self.peer_addr = (config.server_ip, config.server_port)

    def _create_udp_socket(self):
        """Bind a UDP socket to the configured local IP and port."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.config.host_server_port))

    async def _receive_loop(self):
        while True:
            try:
                data, addr = await asyncio.to_thread(self.sock.recvfrom, 2048)
                decrypted = xor_cipher(data, self.config.encryption_key)
                os.write(self.tap_fd, decrypted)
            except BlockingIOError:
                await asyncio.sleep(0.01)  # Avoid tight loop on empty recv
            except Exception as e:
                print(f"[!] Receive error: {e}")
                await asyncio.sleep(0.01)

    async def _send_loop(self):
        """Read from TAP, encrypt, and send to the peer."""
        while True:
            try:
                data = await asyncio.to_thread(os.read, self.tap_fd, 2048)
                encrypted = xor_cipher(data, self.config.encryption_key)
                await asyncio.to_thread(self.sock.sendto, encrypted, self.peer_addr)
                print(f"sent to {self.peer_addr[0]} {encrypted}")
            except Exception as e:
                print(f"[!] Send loop error: {e}")

    async def run(self):
        self._create_udp_socket()
        try:
            await asyncio.gather(
                self._receive_loop(),
                self._send_loop()
            )
        except KeyboardInterrupt:
            pass
        finally:
            if self.sock:
                self.sock.close()
