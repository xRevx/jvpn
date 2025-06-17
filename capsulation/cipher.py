def xor_cipher(data: bytes, key: bytes) -> bytes:
    if not (0 <= key <= 255):
        raise ValueError("Key must be a single byte (0–255).")
    return bytes([b ^ key for b in data])
