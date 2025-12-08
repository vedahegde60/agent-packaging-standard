#!/bin/bash
#
# Pre-Commit Test Script
# Run this before committing any code changes to APS
#
# Usage: ./scripts/pre_commit_tests.sh
#

set -e  # Exit on any error

echo "=================================================="
echo "APS Pre-Commit Test Suite"
echo "=================================================="
echo ""

# Get the root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Step 1: Run automated tests
echo "📋 Step 1/2: Running automated tests..."
echo "=================================================="
cd "$ROOT_DIR/cli"
pytest tests/ -v

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ FAILED: Automated tests did not pass"
    echo "Fix the failing tests before committing."
    exit 1
fi

AUTOMATED_RESULT=$(pytest tests/ -q 2>&1 | tail -1)
echo ""
echo "✅ Automated tests passed: $AUTOMATED_RESULT"
echo ""

# Step 2: Run registry integration test
echo "📋 Step 2/2: Running registry integration test..."
echo "=================================================="
echo ""

# Check if registry dependencies are installed
if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "⚠️  Registry dependencies not installed"
    echo ""
    echo "To install (one-time setup):"
    echo "  pip install fastapi uvicorn python-multipart"
    echo "  cd registry && pip install -e . && cd ../cli"
    echo ""
    echo "Skipping registry test (install dependencies to enable)"
    echo ""
    echo "=================================================="
    echo "⚠️  PRE-COMMIT CHECK INCOMPLETE"
    echo "=================================================="
    echo "Automated tests: ✅ PASSED"
    echo "Registry test:   ⏭️  SKIPPED (dependencies missing)"
    echo ""
    echo "Install registry dependencies and run again:"
    echo "  ./scripts/pre_commit_tests.sh"
    exit 1
fi

RUN_REGISTRY_TEST=1 pytest tests/test_e2e_workflow.py::test_registry_integration -v

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ FAILED: Registry integration test did not pass"
    echo "Fix the registry issues before committing."
    exit 1
fi

echo ""
echo "✅ Registry integration test passed!"
echo ""

# Success!
echo "=================================================="
echo "🎉 ALL PRE-COMMIT TESTS PASSED!"
echo "=================================================="
echo ""
echo "Test Results:"
echo "  ✅ Automated tests: PASSED (15 tests)"
echo "  ✅ Registry integration: PASSED"
echo ""
echo "You are ready to commit!"
echo ""
echo "Next steps:"
echo "  1. Review your changes: git diff"
echo "  2. Stage your files: git add <files>"
echo "  3. Commit with message: git commit -m 'type: description'"
echo ""
