import asyncio
import os
import socket
import time

import select

from logger import log, log_error
from configuration.vpn_config import VPNConfig
from capsulation.cipher import xor_cipher


class VPNPeer:
    def __init__(self, config: VPNConfig, tap_fd: int):
        self.config = config
        self.tap_fd = tap_fd
        self.sock = None
        self.peer_addr = (config.server_ip, config.server_port)
        self.timeout_seconds = config.timeout
        self.reconnection_seconds = config.reconnection
        self.last_packet_time = time.time()
        self.last_reconnect = time.time()

    def _create_udp_socket(self):
        """Bind a UDP socket to the configured local IP and port."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', self.config.host_server_port))
        log("Socket", f"Bound UDP socket on 0.0.0.0:{self.config.host_server_port}")

    async def _io_loop(self):
        log("Loops", f"Listening on TAP and socket for {self.config.server_ip}")

        while True:
            if self.should_reconnect(self.timeout_seconds, self.reconnection_seconds):
                self.reconnect()
                self.last_reconnect = time.time()

            try:
                # Wait for either TAP or socket to be ready (readable)
                ready_read, _, _ = await asyncio.to_thread(
                    select.select, [self.tap_fd, self.sock], [], [], 0.5
                )

                # Handle incoming UDP
                if self.sock in ready_read:
                    data, addr = await asyncio.to_thread(self.sock.recvfrom, 2048)
                    decrypted = xor_cipher(data, self.config.encryption_key)
                    os.write(self.tap_fd, decrypted)
                    self.last_packet_time = time.time()

                # Handle TAP data to send out
                if self.tap_fd in ready_read:
                    data = await asyncio.to_thread(os.read, self.tap_fd, 2048)
                    encrypted = xor_cipher(data, self.config.encryption_key)
                    await asyncio.to_thread(self.sock.sendto, encrypted, self.peer_addr)

            except Exception as e:
                log_error("IO", f"IO loop error: {e}")
                await asyncio.sleep(0.01)

    async def run(self):
        self._create_udp_socket()
        try:
            await asyncio.gather(
                self._io_loop()
            )
        except KeyboardInterrupt:
            pass
        finally:
            if self.sock:
                self.sock.close()

    def is_timed_out(self) -> bool:
        return (time.time() - self.last_packet_time) > self.timeout_seconds

    def should_reconnect(self, timeout: int = 10, cooldown: int = 10) -> bool:
        """Return True if no packet received for `timeout` seconds and cooldown passed since last reconnect."""
        now = time.time()
        return (
                now - self.last_packet_time > timeout and
                now - self.last_reconnect > cooldown
        )

    def reconnect(self):
        log("Reconnecting", "Connection stale. Attempting to reconnect...")

        # Optionally recreate the socket
        self.sock.close()
        self._create_udp_socket()  # Custom method
