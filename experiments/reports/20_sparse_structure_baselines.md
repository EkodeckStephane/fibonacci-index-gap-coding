# Simple Sparse-Structure Baselines

Both baselines are complete and exactly decodable. `zero_block_bitmap`
stores a one-bit presence map and the raw nonzero blocks. `zero_trim`
stores each block after removing its leading and trailing zero bytes.

## Weighted corpus ratios

| corpus     |   block_size | method            |   weighted_ratio |
|:-----------|-------------:|:------------------|-----------------:|
| canterbury |           16 | zero_block_bitmap |         0.893581 |
| canterbury |           16 | fisa              |         0.927384 |
| canterbury |           16 | zero_trim         |         0.948158 |
| canterbury |           16 | raw               |         1.000000 |
| canterbury |           32 | zero_trim         |         0.906522 |
| canterbury |           32 | zero_block_bitmap |         0.912352 |
| canterbury |           32 | fisa              |         0.921490 |
| canterbury |           32 | raw               |         1.000000 |
| canterbury |           64 | zero_trim         |         0.894207 |
| canterbury |           64 | fisa              |         0.935432 |
| canterbury |           64 | zero_block_bitmap |         0.940043 |
| canterbury |           64 | raw               |         1.000000 |
| canterbury |          128 | zero_trim         |         0.909932 |
| canterbury |          128 | fisa              |         0.959251 |
| canterbury |          128 | zero_block_bitmap |         0.963570 |
| canterbury |          128 | raw               |         1.000000 |
| canterbury |          256 | zero_trim         |         0.936590 |
| canterbury |          256 | zero_block_bitmap |         0.969320 |
| canterbury |          256 | fisa              |         0.971250 |
| canterbury |          256 | raw               |         1.000000 |
| silesia    |           16 | zero_block_bitmap |         0.978566 |
| silesia    |           16 | fisa              |         0.997784 |
| silesia    |           16 | raw               |         1.000000 |
| silesia    |           16 | zero_trim         |         1.071237 |
| silesia    |           32 | zero_block_bitmap |         0.977364 |
| silesia    |           32 | fisa              |         0.993006 |
| silesia    |           32 | raw               |         1.000000 |
| silesia    |           32 | zero_trim         |         1.019838 |
| silesia    |           64 | zero_block_bitmap |         0.977543 |
| silesia    |           64 | fisa              |         0.990500 |
| silesia    |           64 | zero_trim         |         0.995896 |
| silesia    |           64 | raw               |         1.000000 |
| silesia    |          128 | zero_block_bitmap |         0.979024 |
| silesia    |          128 | fisa              |         0.989998 |
| silesia    |          128 | zero_trim         |         0.991822 |
| silesia    |          128 | raw               |         1.000000 |
| silesia    |          256 | zero_block_bitmap |         0.981422 |
| silesia    |          256 | zero_trim         |         0.983300 |
| silesia    |          256 | fisa              |         0.987821 |
| silesia    |          256 | raw               |         1.000000 |

## Favorable standard-corpus files

| corpus     | file    |     fisa |      raw |   zero_block_bitmap |   zero_trim |
|:-----------|:--------|---------:|---------:|--------------------:|------------:|
| canterbury | ptt5    | 0.842370 | 1.000000 |            0.829545 |    0.609244 |
| silesia    | mozilla | 0.993760 | 1.000000 |            0.975099 |    0.968287 |
| silesia    | mr      | 0.773155 | 1.000000 |            0.753478 |    0.732201 |
