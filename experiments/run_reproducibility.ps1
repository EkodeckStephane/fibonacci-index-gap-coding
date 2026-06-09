$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Split-Path -Parent $root
Set-Location $project

python -m pytest experiments/tests -q
python experiments/scripts/generate_synthetic_corpus.py
python experiments/scripts/generate_integer_sequence_corpus.py
python experiments/scripts/characterize_integers.py
python experiments/scripts/characterize_integer_scaling.py
python experiments/scripts/compare_numeration_bases.py
python experiments/scripts/run_experiments.py --config experiments/config/experiment.json
python experiments/scripts/run_experiments.py --config experiments/config/canterbury.json
python experiments/scripts/prepare_silesia_sample.py
python experiments/scripts/run_experiments.py --config experiments/config/silesia_sample.json
python experiments/scripts/run_full_baselines.py
python experiments/scripts/run_enwik8_baselines.py
python experiments/scripts/run_ablation.py
python experiments/scripts/compare_universal_codes.py
python experiments/scripts/compare_advanced_codes.py
python experiments/scripts/run_native_fisa.py
python experiments/scripts/analyze_native_fisa.py
python experiments/scripts/analyze_revision_metrics.py
python experiments/scripts/evaluate_sparse_regime.py
python experiments/scripts/analyze_favorable_blocks.py
python experiments/scripts/compare_sparse_baselines.py
python experiments/scripts/analyze_entropy_statistics.py
python experiments/scripts/summarize_all.py
python experiments/scripts/verify_completion.py
