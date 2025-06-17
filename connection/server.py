import asyncio
import os
import socket

from configuration.vpn_config import VPNConfig
from capsulation.cipher import xor_cipher


class VPNServer:
    def __init__(self, config: VPNConfig, tap_fd: int):
        self.config = config
        self.tap_fd = tap_fd
        self.sock = None

    def _create_udp_socket(self):
        """Bind a UDP socket to the configured IP and port, on a specific interface."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((self.config.server_ip, self.config.server_port))
        self.sock.setblocking(False)

        #log("SocketBind", f"Listening on {self.config.server_ip}:{self.config.server_port}")

    async def _receive_loop(self):
        """Receive UDP packets, decrypt and write to TAP."""
        loop = asyncio.get_running_loop()
        while True:
            try:
                data, addr = await loop.sock_recvfrom(self.sock, 2048)
                decrypted = xor_cipher(data, self.config.encryption_key)
                os.write(self.tap_fd, decrypted)
                #log("PacketReceived", f"{len(data)} bytes from {addr}, written to TAP")
            except Exception as e:
                pass
                #log("ReceiveError", str(e))

    async def run(self):
        self._create_udp_socket()

        try:
            #log("ServerStart", "VPN server started")
            await self._receive_loop()
        except KeyboardInterrupt:
            pass
            #log("Shutdown", "Server shutting down on keyboard interrupt")
        finally:
            if self.sock:
                self.sock.close()
            #log("ServerStop", "VPN server stopped")
