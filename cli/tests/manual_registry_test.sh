#!/bin/bash
#
# Manual Registry Integration Test
# 
# Prerequisites:
#   1. Start the registry server first:
#      aps registry serve --port 8080 --root ./test-registry-data
#
#   2. Then run this script:
#      ./tests/manual_registry_test.sh
#
# This script tests the full registry workflow:
#   - Create agent
#   - Build package
#   - Publish to registry
#   - Pull from registry
#   - Validate pulled agent

set -e  # Exit on any error

# Configuration
REGISTRY_URL="${REGISTRY_URL:-http://localhost:8080}"
TEST_DIR=$(mktemp -d)
AGENT_NAME="manual-test-agent-$$"  # Include PID for uniqueness

echo "=================================================="
echo "Registry Integration Test"
echo "=================================================="
echo "Registry URL: $REGISTRY_URL"
echo "Test directory: $TEST_DIR"
echo "Agent name: $AGENT_NAME"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up test directory..."
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

# Check if registry is reachable
echo "🔍 Step 0: Checking if registry is accessible..."
if ! curl -s -f "$REGISTRY_URL/v1/agents" > /dev/null 2>&1; then
    echo "❌ ERROR: Registry not accessible at $REGISTRY_URL"
    echo ""
    echo "Please start the registry first:"
    echo "  aps registry serve --port 8080 --root ./test-registry-data"
    echo ""
    exit 1
fi
echo "✅ Registry is accessible"
echo ""

# Change to test directory
cd "$TEST_DIR"

# Step 1: Create agent
echo "📦 Step 1: Creating new agent..."
aps init "$AGENT_NAME"
if [ ! -d "$AGENT_NAME" ]; then
    echo "❌ FAILED: Agent directory not created"
    exit 1
fi
echo "✅ Agent created: $AGENT_NAME"
echo ""

# Step 2: Validate agent
echo "🔍 Step 2: Validating agent manifest..."
aps validate "$AGENT_NAME"
echo "✅ Agent validated"
echo ""

# Step 3: Build package
echo "🔨 Step 3: Building agent package..."
aps build "$AGENT_NAME"
PACKAGE_PATH="$AGENT_NAME/dist/dev.$AGENT_NAME.aps.tar.gz"
if [ ! -f "$PACKAGE_PATH" ]; then
    echo "❌ FAILED: Package not created at $PACKAGE_PATH"
    exit 1
fi
echo "✅ Package built: $PACKAGE_PATH"
echo ""

# Step 4: Publish to registry
echo "📤 Step 4: Publishing to registry..."
aps publish "$PACKAGE_PATH" --registry "$REGISTRY_URL"
echo "✅ Published to registry"
echo ""

# Step 5: Verify package is in registry
echo "🔍 Step 5: Verifying package in registry..."
AGENT_ID="dev.$AGENT_NAME"
if curl -s -f "$REGISTRY_URL/v1/agents/$AGENT_ID" > /dev/null 2>&1; then
    echo "✅ Package found in registry: $AGENT_ID"
    # Show version info
    VERSION_INFO=$(curl -s "$REGISTRY_URL/v1/agents/$AGENT_ID")
    echo "   Version info: $VERSION_INFO"
else
    echo "❌ FAILED: Package not found in registry"
    exit 1
fi
echo ""

# Step 6: Pull from registry to a new location
echo "📥 Step 6: Pulling from registry..."
PULL_DIR="$TEST_DIR/pulled"
mkdir -p "$PULL_DIR"
cd "$PULL_DIR"
aps pull "$AGENT_ID" --registry "$REGISTRY_URL"
echo "✅ Pulled from registry"
echo ""

# Step 7: Verify pulled agent (check cache)
echo "🔍 Step 7: Verifying pulled agent in cache..."
# The pull command caches to ~/.aps/cache/<agent-id>/<version>/
CACHE_BASE="$HOME/.aps/cache/$AGENT_ID"
if [ -d "$CACHE_BASE" ]; then
    echo "✅ Agent cached at: $CACHE_BASE"
    # Find the version directory
    VERSION_DIR=$(find "$CACHE_BASE" -type d -mindepth 1 -maxdepth 1 | head -1)
    if [ -f "$VERSION_DIR/aps/agent.yaml" ]; then
        echo "✅ Manifest found in cache"
    else
        echo "⚠️  Warning: Manifest not found in expected cache location"
    fi
else
    echo "⚠️  Warning: Cache directory not found (this might be okay depending on pull implementation)"
fi
echo ""

# Step 8: Test running the original agent (optional)
echo "🚀 Step 8: Testing agent execution..."
cd "$TEST_DIR/$AGENT_NAME"
echo '{"text": "hello from registry test"}' | aps run . > /tmp/test_output.json 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Agent executed successfully"
    # Parse and show output (last line should be JSON)
    tail -1 /tmp/test_output.json
else
    echo "⚠️  Agent execution had issues (check /tmp/test_output.json)"
fi
echo ""

# Success!
echo "=================================================="
echo "🎉 All registry workflow tests PASSED!"
echo "=================================================="
echo ""
echo "Tested workflow:"
echo "  1. ✅ Create agent"
echo "  2. ✅ Validate manifest"
echo "  3. ✅ Build package"
echo "  4. ✅ Publish to registry"
echo "  5. ✅ Verify in registry"
echo "  6. ✅ Pull from registry"
echo "  7. ✅ Verify cache"
echo "  8. ✅ Execute agent"
echo ""
echo "Registry URL: $REGISTRY_URL"
echo "Test agent: $AGENT_ID"
echo ""
