# Compiled Full-Corpus FISA Evaluation

The Java implementation uses `BigInteger`, serializes the complete FISA
stream, and verifies exact decode-after-encode equality for every file.
Measurements use 256-byte blocks and no benchmark warmup.

## Corpus summary

| corpus     |   files |   original_bytes |   encoded_bytes |   weighted_ratio |   compressed_files |   encode_mib_s |   decode_mib_s |
|:-----------|--------:|-----------------:|----------------:|-----------------:|-------------------:|---------------:|---------------:|
| canterbury |      11 |          2810784 |         2729973 |         0.971250 |                  1 |       0.758381 |     113.324280 |
| silesia    |      12 |        211938580 |       209357301 |         0.987821 |                  2 |       1.423335 |    1305.906550 |
| enwik8     |       1 |        100000000 |       100000010 |         1.000000 |                  0 |       1.331478 |    2418.958317 |

## Per-file results

| corpus     | file         |   original_bytes |    ratio |   encode_mib_s |   decode_mib_s |
|:-----------|:-------------|-----------------:|---------:|---------------:|---------------:|
| canterbury | alice29.txt  |           152089 | 1.000059 |       0.553110 |    1283.569674 |
| canterbury | asyoulik.txt |           125179 | 1.000072 |       0.509398 |    2446.311419 |
| canterbury | cp.html      |            24603 | 1.000366 |       0.218192 |     570.881976 |
| canterbury | fields.c     |            11150 | 1.000717 |       0.081350 |     389.504345 |
| canterbury | grammar.lsp  |             3721 | 1.002150 |       0.035131 |      85.303417 |
| canterbury | kennedy.xls  |          1029744 | 1.000009 |       1.067568 |    1267.476001 |
| canterbury | lcet10.txt   |           426754 | 1.000021 |       0.872637 |    2441.417692 |
| canterbury | plrabn12.txt |           481861 | 1.000019 |       0.869470 |    3359.199267 |
| canterbury | ptt5         |           513216 | 0.842370 |       0.988709 |      22.067266 |
| canterbury | sum          |            38240 | 1.000235 |       0.192791 |     449.119530 |
| canterbury | xargs.1      |             4227 | 1.001893 |       0.040407 |      96.903397 |
| silesia    | dickens      |         10192446 | 1.000001 |       1.173215 |    3204.204236 |
| silesia    | mozilla      |         51220480 | 0.993760 |       1.459803 |     646.402353 |
| silesia    | mr           |          9970564 | 0.773155 |       1.984697 |     311.363603 |
| silesia    | nci          |         33553445 | 1.000000 |       1.454727 |    3409.450713 |
| silesia    | ooffice      |          6152192 | 1.000002 |       1.564840 |    5735.276149 |
| silesia    | osdb         |         10085684 | 1.000001 |       1.499657 |    1934.563807 |
| silesia    | reymont      |          6627202 | 1.000002 |       1.612100 |    4488.135447 |
| silesia    | samba        |         21606400 | 1.000000 |       1.465427 |    4058.191777 |
| silesia    | sao          |          7251944 | 1.000001 |       1.509573 |     933.219007 |
| silesia    | webster      |         41458703 | 1.000000 |       1.270351 |    3462.968823 |
| silesia    | x-ray        |          8474240 | 1.000001 |       1.322367 |    2441.295626 |
| silesia    | xml          |          5345280 | 1.000002 |       1.452841 |    3131.430831 |
| enwik8     | enwik8       |        100000000 | 1.000000 |       1.331478 |    2418.946046 |

Ratios slightly above one correspond to the stream-level raw fallback
plus its magic, mode, and length framing. The complete Silesia results
supersede conclusions drawn from the fixed 64 KiB samples.
