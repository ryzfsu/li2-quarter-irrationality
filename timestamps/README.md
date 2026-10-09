# Timestamps

[OpenTimestamps](https://opentimestamps.org) proofs for the assets of release `v2`.
Each proof commits to the SHA-256 of the file below and is anchored in Bitcoin block
970653 (2026-10-09 15:43:29 UTC).

| file | SHA-256 |
|---|---|
| `li2-quarter-irrationality-v2.pdf` | `863c0e5c3d3e4d81f0fec373517a1a414c6e306eab70e67b278794f3c769a5e8` |
| `li2-quarter-irrationality-v2.tar.gz` | `7eac77d9a06fbbe82c122d7368e4a7d26f45a8eed93382ff265f5618d4c8ef37` |

To verify, download the release asset into this directory and run

    pip install opentimestamps-client
    ots verify timestamps/<file>.ots
