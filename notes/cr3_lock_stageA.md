# CR-3 stage A lock (2026-10-14)

Source: Drive `DECISION_POINTS/cr3/STAGEA/CR3_stageA_lock.json` (25,514 bytes, canonical JSON), copied byte-for-byte as
`notes/cr3_lock_stageA.json`. The manifest (`CR3_manifest_PRIVATE.json`) stays on Drive only.

- lock_sha256 (pork.cr3.lock_sha256): `7a20da69b9453d80258d2b999ee9a3554fefca5201c27563bb0ff47d945d0247`
- manifest_sha256: `c79aa87fef56fb36a8bb42c594ad75dedb3f9e5dbff5758e6b64b8389b0a68b5`
- prefill_sha256: `54ccc96b13b23e70cbf54b463b2679de0248578f0c5252b09a3bf8539261b371`

## Counts

| W | forks | items with W | U cuts | A1 | A2 | cells | no a1 |
|---|---|---|---|---|---|---|---|
| 264 | 92 | 86 | 426 | 264 | 151 | 841 | 0 |

W = 264 and forks = 92 match the CR-2 exploratory numbers, so lock_record did not stop.

## K_F choice (plan D6, p = $0.00048856, w_max = $0.0029923, max_tokens_cr2 = 770)

| K_F | requests | N·p·1.2 + 500·w_max | ≤ B_stop $21 |
|---|---|---|---|
| **32** | **26,912** | **$17.27** | **yes** |
| 40 | 33,640 | $21.22 | no |
| 48 | 40,368 | $25.16 | no |

K_F = 32 (largest passing). Expected spend for stage B ≈ N·p ≈ $13.1.
