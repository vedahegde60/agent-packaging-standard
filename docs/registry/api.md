---
title: "APS Registry API — Specification v0.1"
description: "REST API specification defining the endpoints, data models, and expected behaviors for APS-compliant registries."
version: "0.1"
last_updated: 2025-11-09
---

# APS Registry API — Specification v0.1

## 1. Introduction

This document defines the **Registry API** for the **Agent Packaging Standard (APS)**.  
An APS registry is a service responsible for storing, versioning, and distributing agent packages conforming to the APS specification.

The API allows clients (CLI tools, runtimes, or build systems) to:

- Publish (`push`) agent packages to a registry.  
- Retrieve (`pull`) agent packages from a registry.  
- Query registry metadata and available packages.

The interface is REST-based and designed to be minimal, predictable, and compatible with modern HTTP clients.

---

## 2. Base URL and Versioning

All endpoints are served under a versioned path prefix:

```

/v1/

```

Future versions of the API **MUST NOT** introduce breaking changes within the same version number.  
Clients and registries **SHOULD** advertise supported API versions via an `X-APS-API-Version` header.

---

## 3. Authentication

Authentication mechanisms are implementation-defined.  
Registries **SHOULD** support at least one of the following:

- Bearer token authentication via `Authorization: Bearer <token>`  
- Basic authentication (`Authorization: Basic <credentials>`)  
- Anonymous (read-only) access for public packages  

Private registries **MUST** implement access control for `push` and `delete` operations.

---

## 4. Endpoints Overview

| Method | Path | Operation | Description |
|---------|------|------------|-------------|
| `POST` | `/v1/publish` | **Publish package** | Upload a new APS package (`.aps.tar.gz`) to the registry. |
| `GET` | `/v1/agents/{id}/download` | **Retrieve package** | Download an existing APS package by identifier. |
| `GET` | `/v1/packages` | **List packages** | Enumerate available agent packages and metadata. |
| `DELETE` | `/v1/agents/{id}` | **Delete package** *(optional)* | Remove a package from the registry (if supported). |

All responses **MUST** be JSON-encoded and include standard metadata fields.

---

## 5. Endpoint Definitions

### 5.1 `POST /v1/push`

**Purpose:** Publish a signed APS package to the registry.

**Request**

| Parameter | Type | Description |
|------------|------|-------------|
| `file` | binary | The APS package archive (`.aps.tar.gz`). |
| `metadata` | JSON | Optional metadata including version, digest, and provenance. |

**Example**

```bash
curl -X POST https://registry.agentpackaging.org/v1/push \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@examples/echo-agent.aps.tar.gz" \
  -F 'metadata={"id": "examples.echo-agent", "version": "0.1.0"}'
```

**Response**

```json
{
  "id": "examples.echo-agent",
  "version": "0.1.0",
  "digest": "sha256:ab349...",
  "status": "uploaded"
}
```

**Status Codes**

| Code               | Meaning                                   |
| ------------------ | ----------------------------------------- |
| `201 Created`      | Package accepted and stored successfully. |
| `400 Bad Request`  | Invalid package or metadata.              |
| `401 Unauthorized` | Authentication failed.                    |
| `409 Conflict`     | Package version already exists.           |

---

### 5.2 `GET /v1/agents/{id}/download`

**Purpose:** Retrieve an APS package by identifier.

**Example**

```bash
curl -L https://registry.agentpackaging.org/v1/pull/examples.echo-agent \
  -o examples.echo-agent.aps.tar.gz
```

**Response (Headers)**

```
Content-Type: application/gzip
X-APS-Digest: sha256:ab349...
```

If the package does not exist:

```json
{
  "error": "package not found",
  "id": "examples.echo-agent"
}
```

**Status Codes**

| Code            | Meaning                         |
| --------------- | ------------------------------- |
| `200 OK`        | Package retrieved successfully. |
| `404 Not Found` | Package does not exist.         |

---

### 5.3 `GET /v1/packages`

**Purpose:** Enumerate available packages and metadata.

**Example**

```bash
curl https://registry.agentpackaging.org/v1/packages
```

**Response**

```json
{
  "packages": [
    {
      "id": "examples.echo-agent",
      "version": "0.1.0",
      "digest": "sha256:ab349...",
      "updated_at": "2025-11-09T08:00:00Z"
    },
    {
      "id": "examples.rag-agent",
      "version": "0.1.0",
      "digest": "sha256:b118a...",
      "updated_at": "2025-11-09T08:30:00Z"
    }
  ]
}
```

**Status Codes**

| Code                        | Meaning                               |
| --------------------------- | ------------------------------------- |
| `200 OK`                    | List retrieved successfully.          |
| `500 Internal Server Error` | Registry malfunction or unresponsive. |

---

### 5.4 `DELETE /v1/agents/{id}` *(optional)*

**Purpose:** Remove a package from the registry.
Implementations **MAY** restrict or disable deletion for immutability.

**Example**

```bash
curl -X DELETE https://registry.agentpackaging.org/v1/packages/examples.echo-agent \
  -H "Authorization: Bearer $TOKEN"
```

**Response**

```json
{
  "id": "examples.echo-agent",
  "status": "deleted"
}
```

**Status Codes**

| Code            | Meaning                       |
| --------------- | ----------------------------- |
| `200 OK`        | Package deleted successfully. |
| `403 Forbidden` | Operation not permitted.      |
| `404 Not Found` | Package does not exist.       |

---

## 6. Metadata Schema

Each APS registry **MUST** maintain metadata describing all stored packages.
Metadata records **SHALL** include the following fields:

| Field        | Type   | Description                           |
| ------------ | ------ | ------------------------------------- |
| `id`         | string | Unique package identifier.            |
| `version`    | string | Semantic version of the package.      |
| `digest`     | string | SHA256 digest of the package file.    |
| `created_at` | string | ISO-8601 timestamp of creation.       |
| `updated_at` | string | ISO-8601 timestamp of last update.    |
| `provenance` | object | Optional signature or build metadata. |

Example record:

```json
{
  "id": "examples.echo-agent",
  "version": "0.1.0",
  "digest": "sha256:ab349...",
  "created_at": "2025-11-09T08:00:00Z",
  "updated_at": "2025-11-09T08:00:00Z",
  "provenance": {
    "signature": "sha256:abc123...",
    "signer": "aps@agentpackaging.org"
  }
}
```

---

## 7. Error Handling

All error responses **MUST** include the following structure:

```json
{
  "error": "string",
  "code": "string",
  "details": "optional diagnostic text"
}
```

Example:

```json
{
  "error": "invalid manifest",
  "code": "APS-4001",
  "details": "Field 'entrypoint' missing in manifest."
}
```

---

## 8. Implementation Notes

* Registries **SHOULD** support both HTTPS and OCI-compatible APIs for interoperability.
* Clients **MAY** cache registry responses to reduce network overhead.
* Registries **MAY** include metadata extensions for organizational policies or access control.
* All date/time fields **MUST** use UTC (`Z`) timestamps.

---

## 9. References

* [APS Specification v0.1](../specs/APS-v0.1.md)
* [Security and Provenance](../security/provenance.md)
* [Governance](../standards/governance.md)
* [RFC 7231: HTTP/1.1 Semantics and Content](https://datatracker.ietf.org/doc/html/rfc7231)

---

## 10. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*