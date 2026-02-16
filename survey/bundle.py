"""
Bundle survey responses for secure transmission.

Security architecture:
1. Payload contains ONLY: version + single score (no identifying info)
2. Padded to fixed size (prevents length fingerprinting)
3. Encrypted with research team's public key (age)
4. Split into shares via Shamir secret sharing (2-of-3 threshold)
5. Each share destined for different infrastructure provider

Even if an attacker compromises one provider AND obtains the private key,
they cannot reconstruct submissions without a second provider.
"""

import json
import secrets
from pathlib import Path

# TODO: Replace with actual age encryption once keys are generated
# from age import encrypt

# TODO: Replace with actual Shamir implementation
# from secretsharing import split_secret


# Placeholder public key - replace with real key before deployment
RESEARCH_PUBKEY_PATH = Path(__file__).parent.parent / "keys" / "research.pub"

# Fixed payload size to prevent length fingerprinting
PADDED_SIZE = 4096


def pad_payload(data: bytes) -> bytes:
    """
    Pad payload to fixed size with random bytes.
    
    This prevents attackers from inferring anything about the payload
    based on encrypted blob size.
    """
    if len(data) > PADDED_SIZE - 32:  # Reserve space for length prefix
        raise ValueError(f"Payload too large: {len(data)} bytes")
    
    # Prefix with length so we can unpad later
    length_prefix = len(data).to_bytes(4, 'big')
    padding_needed = PADDED_SIZE - 4 - len(data)
    padding = secrets.token_bytes(padding_needed)
    
    return length_prefix + data + padding


def encrypt_payload(padded_data: bytes, pubkey: str) -> bytes:
    """
    Encrypt payload with research team's public key.
    
    Uses age encryption - recipient needs private key to decrypt.
    
    TODO: Implement actual age encryption
    """
    # STUB: In production, this would be:
    # return age.encrypt(padded_data, pubkey)
    
    # For now, just mark it as "encrypted" for testing
    return b"ENCRYPTED:" + padded_data


def shamir_split(data: bytes, n: int = 3, threshold: int = 2) -> list[bytes]:
    """
    Split data into n shares where threshold shares are needed to reconstruct.
    
    TODO: Implement actual Shamir secret sharing
    """
    # STUB: In production, this would use a real Shamir implementation
    # return secretsharing.split(data, n, threshold)
    
    # For now, just duplicate with shard markers for testing
    return [
        f"SHARD_{i}:".encode() + data
        for i in range(n)
    ]


def prepare_submission(payload: dict) -> list[bytes]:
    """
    Full pipeline: serialize -> pad -> encrypt -> split
    
    Args:
        payload: Dict with survey response (v, internal_score)
        
    Returns:
        List of encrypted shares ready for transmission
    """
    # Serialize
    json_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    
    # Pad to fixed size
    padded = pad_payload(json_bytes)
    
    # Load public key
    # TODO: Actually load and validate the key
    pubkey = "AGE_PUBKEY_PLACEHOLDER"
    
    # Encrypt
    encrypted = encrypt_payload(padded, pubkey)
    
    # Split into shares
    shares = shamir_split(encrypted, n=3, threshold=2)
    
    return shares