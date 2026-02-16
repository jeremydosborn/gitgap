"""
Submit encrypted survey shares to research infrastructure.

CURRENT STATUS: STUB IMPLEMENTATION
Saves shares locally for testing. Real submission not yet implemented.

=============================================================================
SECURITY ARCHITECTURE (planned)
=============================================================================

Submission flow:
  1. Client encrypts payload with research public key
  2. Client splits encrypted blob into 3 Shamir shares (2-of-3 threshold)
  3. Each share POSTed to different infrastructure provider:
     - Shard 1 -> Digital Ocean
     - Shard 2 -> Linode  
     - Shard 3 -> Vultr (or similar)
  4. No single provider can reconstruct the submission
  5. Attacker must compromise 2+ providers AND obtain private key

Aggregation flow:
  1. Research team pulls shares from all providers
  2. Reconstructs encrypted blobs (need 2-of-3 shares)
  3. Decrypts with private key (stored on hardware key / HSM)
  4. Aggregates responses, publishes only aggregate statistics
  5. Deletes individual submissions after aggregation

=============================================================================
UNSOLVED PROBLEMS (TODO)
=============================================================================

1. HOSTILE RESPONDER MITIGATION
   - No mechanism to prevent spam/flooding
   - No mechanism to prevent slow trickle of fake data
   - Rate limiting by IP is insufficient (botnets)
   - Proof of work adds friction but doesn't stop determined attacker
   - Authentication would compromise anonymity
   
   Current stance: Accept the risk for v1. Monitor for anomalies.
   Revisit if tufcheck adoption makes it a worthwhile target.

2. SYBIL RESISTANCE  
   - Same person could submit multiple times
   - Client-side cache is trivially bypassed
   - Server can't dedupe without identifying info
   
   Current stance: Noise averages out at scale. Not a high-integrity vote.

3. LONGITUDINAL TRACKING
   - No repo hash means no cross-time correlation
   - Deliberately sacrificed for anonymity
   - Can only measure cohort trends, not individual project evolution

=============================================================================
"""

from pathlib import Path
from datetime import datetime


SHARD_ENDPOINTS = [
    "https://shard1.tufcheck.dev/submit",
    "https://shard2.tufcheck.dev/submit",
    "https://shard3.tufcheck.dev/submit",
]


def submit_shares(shares: list[bytes]) -> bool:
    pending_dir = Path.home() / ".tufcheck" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "-" * 60)
    print("SUBMISSION (STUB MODE)")
    print("-" * 60)
    print("""
NOTE: Real submission infrastructure not yet implemented.
Shares saved locally for testing.

Planned architecture:
  - 3 shares distributed across independent providers
  - 2-of-3 threshold for reconstruction
  - No single point of compromise
""")
    
    for i, share in enumerate(shares):
        share_path = pending_dir / f"{timestamp}_shard_{i}.enc"
        share_path.write_bytes(share)
        print(f"  Saved: {share_path}")
    
    print(f"""
When submission is implemented, shares will go to:
  - {SHARD_ENDPOINTS[0]}
  - {SHARD_ENDPOINTS[1]}
  - {SHARD_ENDPOINTS[2]}
""")
    
    print("Thank you for participating in this research.\n")
    
    return True