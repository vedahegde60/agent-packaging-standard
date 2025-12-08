# APS CLI Reference

The `aps` CLI is the reference implementation of the **Agent Packaging Standard** tooling.

It is responsible for:

- Building APS agent packages
- Running agents locally from a package
- Publishing and pulling from registries
- Inspecting manifests and metadata
- Streaming logs and debugging runs

---

## Installation

From a local clone of this repository:

```bash
# From repo root
cd cli

# Editable install for local development
pip install -e .
````

Once installed, verify:

```bash
aps --help
aps --version
```

---

## CLI Overview

```bash
aps [GLOBAL OPTIONS] <command> [COMMAND OPTIONS]
```

Core commands (v0.1):

* `aps build`   – Package an agent into an APS artifact
* `aps run`     – Run an agent from a packaged or source directory
* `aps publish` – Publish a package to a registry
* `aps pull`    – Pull a package from a registry into local cache
* `aps inspect` – Show manifest, metadata, and capabilities
* `aps logs`    – View or stream logs for a run
* `aps lint`    – Validate an agent package / manifest (where implemented)

> Run `aps <command> --help` for the exact options supported in your installed version.

---

## Global Options

Common global flags (may evolve across versions):

* `-h, --help` – Show help for the CLI or a specific command
* `--version` – Show CLI version
* `--log-level {debug,info,warning,error}` – Control verbosity
* `--registry <url>` – Override default registry endpoint (for publish/pull/run)

Example:

```bash
aps --log-level debug --registry http://localhost:8080 publish dist/echo-agent.aps.tar.gz
```

---

## `aps build`

Builds an APS-compliant package from an agent directory.

**Synopsis:**

```bash
aps build [OPTIONS] <AGENT_PATH>
```

**Typical inputs:**

* `AGENT_PATH` – Path to the agent source directory containing:

  * `aps/agent.yaml` (APS manifest)
  * Code entrypoint (e.g., `src/<agent_name>/main.py`)
  * Any supporting files

**Common options:**

* `-o, --output <path>` – Output file path (e.g., `dist/myagent.aps.tar.gz`)
* `--no-cache` – Do not reuse previous build layers (if applicable)

**Example:**

```bash
aps build examples/echo-agent
```

This creates `examples/echo-agent/dist/dev.echo.aps.tar.gz` by default.

---

## `aps run`

Runs an agent from a local directory or built package.

Agents follow the APS runtime contract (stdin → stdout JSON).

**Synopsis:**

```bash
aps run [OPTIONS] <AGENT_PATH_OR_PACKAGE>
```

**Common options:**

* `--stream` – Stream tokens/responses as they are produced
* `--registry <url>` – If running a package that must be pulled first
* `--env KEY=VALUE` – Inject runtime environment variables (if supported)

**Examples:**

Run directly from source:

```bash
aps run examples/echo-agent --stream
```

Run from a built package:

```bash
aps run examples/echo-agent/dist/dev.echo.aps.tar.gz
```

Using stdin → stdout JSON contract:

```bash
echo '{"text":"hello"}' | aps run examples/echo-agent
```

Or with --input flag:

```bash
aps run examples/echo-agent --input '{"text":"hello"}'
```

---

## `aps publish`

Publishes a built APS package to a registry.

**Synopsis:**

```bash
aps publish [OPTIONS] <PACKAGE_PATH>
```

**Common options:**

* `--registry <url>` – Target registry URL (e.g., `https://registry.aps.dev`)
* `--auth-token <token>` – Registry auth (if required)
* `--force` – Overwrite existing version (if policy allows)

**Example:**

```bash
aps publish dist/dev.echo.aps.tar.gz --registry http://localhost:8080
```

---

## `aps pull`

Pulls an APS package from a registry into the local cache or filesystem.

**Synopsis:**

```bash
aps pull [OPTIONS] <AGENT_REF>
```

Where `AGENT_REF` is the agent ID (e.g., `dev.echo`)

**Common options:**

* `--registry <url>` – Registry URL
* `--version <version>` – Specific version (default: latest)

**Example:**

```bash
aps pull dev.echo --registry http://localhost:8080
```

The agent is cached locally and can be run with:

```bash
aps run dev.echo
```

---

## `aps inspect`

Shows what’s inside a package or agent directory.

**Synopsis:**

```bash
aps inspect <AGENT_PATH_OR_PACKAGE>
```

**What it can display (depending on implementation):**

* Manifest fields (name, version, publisher)
* Capabilities and tools
* Runtime entrypoint
* Declared policies
* Dependencies and environment

**Example:**

```bash
aps inspect dist/echo-agent.aps.tar.gz
```

---

## `aps logs`

Displays logs for local runs (and eventually remote ones).

**Synopsis:**

```bash
aps logs [OPTIONS] <RUN_ID_OR_PATH>
```

**Common options:**

* `-f, --follow` – Stream logs as they are produced
* `--tail <N>` – Show the last N lines
* `--since <duration>` – Filter logs by relative time (e.g., `5m`, `1h`)

**Examples:**

```bash
# Show logs for the most recent run of an agent
aps logs examples/echo-agent

# Follow logs for a given run ID (if your version exposes IDs)
aps logs --follow 2025-11-07T21-03-12Z-echo
```

---

## `aps lint`

Validates a package or agent directory against the APS spec.

**Synopsis:**

```bash
aps lint <AGENT_PATH_OR_PACKAGE>
```

**Checks may include:**

* Required manifest fields present
* Version and ID formatting
* Referenced files exist
* Basic schema compliance

**Example:**

```bash
aps lint examples/echo-agent
```

---

## Exit Codes

* `0` – Success
* `1` – General error (invalid input, runtime failure)
* `2` – Validation / lint error
* `>=10` – Reserved for future, more specific error classes

---

## See Also

* [Getting Started](../getting-started.md)
* [APS v0.1 Spec](../specs/APS-v0.1.md)
* [Publish Workflow](../publish.md)