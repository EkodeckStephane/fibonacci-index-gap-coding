# Revision Metrics

## Empirical calibration of the sufficient term threshold

| corpus     |   files |   k_star_min |   k_star_median |   k_star_max |   full_blocks |   k_star_blocks |   k_star_fraction |   all_blocks |   shared_blocks |   shared_block_fraction |
|:-----------|--------:|-------------:|----------------:|-------------:|--------------:|----------------:|------------------:|-------------:|----------------:|------------------------:|
| canterbury |      11 |          390 |      392.000000 |          392 |         10975 |             406 |          0.036993 |        10986 |             412 |                0.037502 |
| silesia    |      12 |          326 |      326.000000 |          326 |        827882 |           16037 |          0.019371 |       827890 |           16048 |                0.019384 |

The threshold is file-specific because each FISA file has its own shared
alphabet and amortized metadata. Fractions count complete 256-byte blocks.

## Complete-file paired statistics

| corpus     |   files |   mean_fisa_ratio |   mean_best_modern_ratio |   median_ratio_factor |   fisa_wins |   ties |   modern_wins |   wilcoxon_statistic |   one_sided_p_value |
|:-----------|--------:|------------------:|-------------------------:|----------------------:|------------:|-------:|--------------:|---------------------:|--------------------:|
| canterbury |      11 |          0.986174 |                 0.231792 |              3.924097 |           0 |      0 |            11 |            66.000000 |            0.000488 |
| silesia    |      12 |          0.980577 |                 0.257961 |              4.231724 |           0 |      0 |            12 |            78.000000 |            0.000244 |

## Aggregate encoding throughput

| corpus     | method    |   weighted_ratio |   aggregate_encode_mib_s |
|:-----------|:----------|-----------------:|-------------------------:|
| canterbury | fisa_1_0  |         0.971250 |                 0.758381 |
| canterbury | zlib_9    |         0.258938 |                 4.050027 |
| canterbury | zstd_19   |         0.183706 |                 2.199658 |
| canterbury | brotli_11 |         0.174564 |                 0.527857 |
| canterbury | lzma_9    |         0.175138 |                 2.468776 |
| canterbury | ppmd_6    |         0.181868 |                 6.433923 |
| silesia    | fisa_1_0  |         0.987821 |                 1.423335 |
| silesia    | zlib_9    |         0.319165 |                10.410295 |
| silesia    | zstd_19   |         0.249718 |                 2.045706 |
| silesia    | brotli_11 |         0.237487 |                 0.488989 |
| silesia    | lzma_9    |         0.230234 |                 2.026187 |
| silesia    | ppmd_6    |         0.236670 |                 5.362392 |

FISA uses the Java implementation. Baselines use their Python bindings on
the same machine and include the configured high-compression settings.

## Fixed-prefix versus complete-file ratios

| file    |   prefix_ratio |   complete_ratio |   absolute_change |   complete_to_prefix_factor |
|:--------|---------------:|-----------------:|------------------:|----------------------------:|
| dickens |       1.000137 |         1.000001 |         -0.000136 |                    0.999864 |
| mozilla |       0.767197 |         0.993760 |          0.226564 |                    1.295314 |
| mr      |       0.791183 |         0.773155 |         -0.018029 |                    0.977213 |
| nci     |       1.000137 |         1.000000 |         -0.000137 |                    0.999863 |
| ooffice |       0.969559 |         1.000002 |          0.030443 |                    1.031399 |
| osdb    |       1.000137 |         1.000001 |         -0.000136 |                    0.999864 |
| reymont |       1.000137 |         1.000002 |         -0.000136 |                    0.999864 |
| samba   |       1.000137 |         1.000000 |         -0.000137 |                    0.999863 |
| sao     |       1.000137 |         1.000001 |         -0.000136 |                    0.999864 |
| webster |       1.000137 |         1.000000 |         -0.000137 |                    0.999863 |
| x-ray   |       1.000137 |         1.000001 |         -0.000136 |                    0.999864 |
| xml     |       1.000137 |         1.000002 |         -0.000135 |                    0.999865 |
