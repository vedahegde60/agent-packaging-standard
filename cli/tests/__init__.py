import os
from pathlib import Path

# Ensure tests don't inadvertently read the real ~/.aps during import-time
# This provides a safe repo-local default before pytest fixtures run.
repo_root = Path.cwd()
os.environ.setdefault("APS_CACHE_DIR", str(repo_root / ".test_cache_default"))
os.environ.setdefault("APS_LOGS_DIR", str(repo_root / ".test_logs_default"))

# Limit BLAS/parallel threads to avoid nondeterministic slowdowns in CI/tests
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
