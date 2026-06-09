# Universal-Code Baselines

These are optimistic payload-only lengths on the same reduced-gap sequences. They exclude block framing and, for the Rice oracle, the parameter signalling cost. They therefore cannot be reported as complete compressor sizes.

| corpus         |   block_size | method                     |    ratio |
|:---------------|-------------:|:---------------------------|---------:|
| canterbury     |           64 | fixed_binary_no_delimiters | 0.918896 |
| canterbury     |           64 | rice_oracle_k1             | 1.13041  |
| canterbury     |           64 | elias_gamma                | 1.46078  |
| canterbury     |           64 | fibonacci_universal        | 1.47533  |
| canterbury     |           64 | elias_delta                | 1.71481  |
| canterbury     |           64 | leb128                     | 3.01611  |
| canterbury     |          256 | fixed_binary_no_delimiters | 0.943866 |
| canterbury     |          256 | rice_oracle_k1             | 1.16119  |
| canterbury     |          256 | elias_gamma                | 1.50073  |
| canterbury     |          256 | fibonacci_universal        | 1.51523  |
| canterbury     |          256 | elias_delta                | 1.7612   |
| canterbury     |          256 | leb128                     | 3.09604  |
| canterbury     |          512 | fixed_binary_no_delimiters | 0.949562 |
| canterbury     |          512 | rice_oracle_k1             | 1.16812  |
| canterbury     |          512 | elias_gamma                | 1.50983  |
| canterbury     |          512 | fibonacci_universal        | 1.52426  |
| canterbury     |          512 | elias_delta                | 1.77173  |
| canterbury     |          512 | leb128                     | 3.11437  |
| silesia_sample |           64 | fixed_binary_no_delimiters | 0.915063 |
| silesia_sample |           64 | rice_oracle_k1             | 1.12483  |
| silesia_sample |           64 | elias_gamma                | 1.45464  |
| silesia_sample |           64 | fibonacci_universal        | 1.46879  |
| silesia_sample |           64 | elias_delta                | 1.70717  |
| silesia_sample |           64 | leb128                     | 3.00387  |
| silesia_sample |          256 | fixed_binary_no_delimiters | 0.925228 |
| silesia_sample |          256 | rice_oracle_k1             | 1.1378   |
| silesia_sample |          256 | elias_gamma                | 1.47094  |
| silesia_sample |          256 | fibonacci_universal        | 1.48519  |
| silesia_sample |          256 | elias_delta                | 1.7264   |
| silesia_sample |          256 | leb128                     | 3.03613  |
| silesia_sample |          512 | fixed_binary_no_delimiters | 0.945184 |
| silesia_sample |          512 | rice_oracle_k1             | 1.16262  |
| silesia_sample |          512 | elias_gamma                | 1.50273  |
| silesia_sample |          512 | fibonacci_universal        | 1.51724  |
| silesia_sample |          512 | elias_delta                | 1.76359  |
| silesia_sample |          512 | leb128                     | 3.10113  |
