# Advanced Fibonacci and Integer-Sequence Baselines

All rows labelled `complete` include their local codebook or parameter metadata and are decoded in the test suite. The entropy-oracle row is payload-only and is reported solely as a lower bound.

## Fibonacci-derived gap streams

| corpus         |   block_size | method                 |   mean_ratio |   weighted_ratio |
|:---------------|-------------:|:-----------------------|-------------:|-----------------:|
| canterbury     |          256 | entropy_oracle_payload |     0.968113 |         0.941454 |
| canterbury     |          256 | shared_alphabet_hybrid |     0.986174 |         0.97125  |
| canterbury     |          256 | huffman_complete       |     1.12324  |         1.09256  |
| canterbury     |          256 | rice_complete          |     1.18248  |         1.15052  |
| canterbury     |          256 | fipb_per_block         |     1.62791  |         1.5849   |
| silesia_sample |          256 | entropy_oracle_payload |     0.948311 |         0.948311 |
| silesia_sample |          256 | shared_alphabet_hybrid |     0.960765 |         0.960765 |
| silesia_sample |          256 | huffman_complete       |     1.09844  |         1.09844  |
| silesia_sample |          256 | rice_complete          |     1.15859  |         1.15859  |
| silesia_sample |          256 | fipb_per_block         |     1.59547  |         1.59547  |

## Monotone integer sequences

| dataset       |   count |    maximum | method               |   encoded_bytes |   bits_per_integer |   ratio_to_u64 |
|:--------------|--------:|-----------:|:---------------------|----------------:|-------------------:|---------------:|
| dense         |  100000 |      99999 | raw_u64              |          800000 |           64       |      1         |
| dense         |  100000 |      99999 | elias_fano_complete  |           25011 |            2.00088 |      0.0312637 |
| dense         |  100000 |      99999 | gap_huffman_complete |           12508 |            1.00064 |      0.015635  |
| dense         |  100000 |      99999 | gap_rice_complete    |           12506 |            1.00048 |      0.0156325 |
| dense         |  100000 |      99999 | gap_leb128           |          100000 |            8       |      0.125     |
| geometric_p20 |  100000 |     499876 | raw_u64              |          800000 |           64       |      1         |
| geometric_p20 |  100000 |     499876 | elias_fano_complete  |           53135 |            4.2508  |      0.0664187 |
| geometric_p20 |  100000 |     499876 | gap_huffman_complete |           45595 |            3.6476  |      0.0569938 |
| geometric_p20 |  100000 |     499876 | gap_rice_complete    |           46185 |            3.6948  |      0.0577312 |
| geometric_p20 |  100000 |     499876 | gap_leb128           |          100000 |            8       |      0.125     |
| geometric_p50 |  100000 |     200033 | raw_u64              |          800000 |           64       |      1         |
| geometric_p50 |  100000 |     200033 | elias_fano_complete  |           37515 |            3.0012  |      0.0468937 |
| geometric_p50 |  100000 |     200033 | gap_huffman_complete |           25047 |            2.00376 |      0.0313088 |
| geometric_p50 |  100000 |     200033 | gap_rice_complete    |           25012 |            2.00096 |      0.031265  |
| geometric_p50 |  100000 |     200033 | gap_leb128           |          100000 |            8       |      0.125     |
| posting_like  |  100000 |     304116 | raw_u64              |          800000 |           64       |      1         |
| posting_like  |  100000 |     304116 | elias_fano_complete  |           44020 |            3.5216  |      0.055025  |
| posting_like  |  100000 |     304116 | gap_huffman_complete |           22749 |            1.81992 |      0.0284362 |
| posting_like  |  100000 |     304116 | gap_rice_complete    |           32821 |            2.62568 |      0.0410263 |
| posting_like  |  100000 |     304116 | gap_leb128           |          100030 |            8.0024  |      0.125037  |
| quadratic     |  100000 | 9999800001 | raw_u64              |          800000 |           64       |      1         |
| quadratic     |  100000 | 9999800001 | elias_fano_complete  |          231588 |           18.527   |      0.289485  |
| quadratic     |  100000 | 9999800001 | gap_huffman_complete |          600365 |           48.0292  |      0.750456  |
| quadratic     |  100000 | 9999800001 | gap_rice_complete    |          225431 |           18.0345  |      0.281789  |
| quadratic     |  100000 | 9999800001 | gap_leb128           |          291742 |           23.3394  |      0.364677  |
