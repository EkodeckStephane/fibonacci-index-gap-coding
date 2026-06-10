# Zeckendorf Term-Count Scaling

Seed: `20260610`; exact-bit-length samples per row: `5000`.

Lekkerkerker's theorem gives an average of $n/(\varphi^2+1)+O(1)$ summands for integers in $[F_n,F_{n+1})$. Since $n\sim \ell/\log_2\varphi$, the leading coefficient for an ell-bit integer is `0.398122`.

| Block | Bits | Asymptotic mean | Simulated mean | Std. dev. | Min--max | <=326 | <=392 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 16 | 128 | 50.96 | 51.41 | 4.05 | 36--65 | 5000/5000 | 5000/5000 |
| 32 | 256 | 101.92 | 102.17 | 5.67 | 83--122 | 5000/5000 | 5000/5000 |
| 64 | 512 | 203.84 | 204.28 | 8.11 | 175--238 | 5000/5000 | 5000/5000 |
| 128 | 1024 | 407.68 | 408.31 | 11.48 | 354--453 | 0/5000 | 407/5000 |
| 256 | 2048 | 815.35 | 815.63 | 16.36 | 748--873 | 0/5000 | 0/5000 |

The 256-byte simulation is the direct comparison for the measured
complete-stream thresholds. No sampled generic 2048-bit integer
falls below either threshold.
