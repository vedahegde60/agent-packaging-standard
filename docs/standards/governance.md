---
title: "APS Project Governance"
description: "Defines the governance model, decision process, and maintainer responsibilities for the Agent Packaging Standard (APS)."
version: "0.1"
last_updated: 2025-11-09
---

# APS Project Governance

## 1. Introduction

This document defines the governance model for the **Agent Packaging Standard (APS)** project.  
It establishes transparent processes for community participation, technical decision-making, and release management.

The APS governance model is designed to ensure:
- Open and inclusive participation,
- Technical meritocracy based on consensus,
- Predictable versioning and release cycles, and
- Long-term sustainability independent of any single vendor or organization.

---

## 2. Project Structure

The APS project operates under a **Working Group model**, consisting of:

| Role | Description |
|------|-------------|
| **Maintainers** | Core contributors responsible for technical direction, specification evolution, and release management. |
| **Contributors** | Community members submitting issues, pull requests, or discussions. |
| **Reviewers** | Experienced contributors designated to review proposals or specifications. |
| **Adopters** | Organizations or individuals implementing APS-compliant runtimes, registries, or tools. |

Participation in all roles is open to the community.

---

## 3. Governance Principles

APS governance follows these guiding principles:

1. **Open** — All discussions, proposals, and releases are public.  
2. **Transparent** — Decisions and votes are documented in the public repository.  
3. **Consensus-driven** — Technical direction is based on rough consensus among maintainers and contributors.  
4. **Vendor-neutral** — No single entity may control direction or release gating.  
5. **Stable evolution** — Specification changes follow a versioned, review-based process.

---

## 4. Decision-Making Process

### 4.1 Proposals

Proposals for new features, revisions, or policies **MUST** be submitted as GitHub issues or pull requests in the main APS repository.

Each proposal should include:
- Problem statement  
- Technical rationale  
- Proposed solution  
- Backward-compatibility impact  
- Security and governance considerations  

### 4.2 Review and Consensus

- Proposals are discussed openly via GitHub Issues and Discussions.  
- Maintainers aim for **rough consensus** — defined as general agreement without sustained objection.  
- If consensus cannot be reached, a formal vote may be initiated.

### 4.3 Voting

When voting is required:
- Each maintainer has one vote.  
- A proposal passes with a **2/3 majority** of active maintainers.  
- Votes are recorded in the corresponding GitHub issue or PR.  
- Inactive maintainers (no participation for >90 days) are excluded from quorum calculations.

---

## 5. Release Management

APS follows semantic versioning (`MAJOR.MINOR.PATCH`).

| Type | Example | Description |
|------|----------|-------------|
| **Major** | `v1.0.0` | Incompatible schema or behavior changes. |
| **Minor** | `v0.2.0` | Backward-compatible additions or clarifications. |
| **Patch** | `v0.1.1` | Non-breaking fixes or editorial updates. |

### 5.1 Release Procedure

1. Draft change proposal merged into the main branch.  
2. Maintainer consensus to designate a **Release Candidate (RC)**.  
3. Public review period of at least **7 days**.  
4. Formal version tag and publication at [agentpackaging.org](https://agentpackaging.org).  
5. Announcement via project communication channels.

---

## 6. Specification Evolution

Each APS specification document includes a version header and changelog.  
Changes to normative sections (e.g., manifest schema or registry API) require:

- Maintainer review and approval,  
- Backward-compatibility analysis, and  
- Updated version designation (`v0.x → v0.y` or `v1.x → v2.x`).

Editorial or non-normative changes (grammar, examples) may be merged with maintainer review but do not require version increments.

---

## 7. Working Group Meetings

- Regular working sessions **MAY** be held virtually as needed.  
- Meeting notes and recordings (if any) **MUST** be published in the public repository.  
- Decisions made in meetings **MUST** be recorded in GitHub for transparency.

---

## 8. Security and Disclosure Policy

APS follows a responsible disclosure process for security vulnerabilities.

| Contact | Purpose |
|----------|----------|
| **security@agentpackaging.org** | Confidential security disclosures. |
| **contact@agentpackaging.org** | General inquiries. |

Reports are acknowledged within **72 hours** and handled privately until mitigation is available.  
Security-related updates are communicated publicly once resolved.

---

## 9. Code of Conduct

All contributors are expected to adhere to the **APS Community Code of Conduct**, adapted from the [Contributor Covenant](https://www.contributor-covenant.org/).  
Respectful, inclusive participation is required for all interactions within the community.

Violations may result in removal from communication channels or revocation of maintainer privileges.

---

## 10. Maintainer Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Review proposals** | Evaluate and merge contributions based on technical merit. |
| **Manage releases** | Tag and publish official versions of APS specifications. |
| **Ensure transparency** | Record all decisions and votes publicly. |
| **Uphold neutrality** | Prevent conflicts of interest and ensure open participation. |
| **Onboard contributors** | Help new members understand process and structure. |

Maintainers are listed in `MAINTAINERS.md` in the root of the repository.

---

## 11. Amendment and Ratification

This governance document may be amended by:
1. Opening a pull request with proposed revisions.  
2. Public discussion period of at least 7 days.  
3. Maintainer vote requiring 2/3 majority approval.  

Amendments take effect upon merge and publication at [agentpackaging.org](https://agentpackaging.org).

---

## 12. References

- [APS Specification v0.1](../specs/APS-v0.1.md)  
- [APS Registry API](../registry/api.md)  
- [APS Provenance Specification](../security/provenance.md)  
- [Contributor Covenant v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)

---

## 13. Contact

📬 **General inquiries:** [contact@agentpackaging.org](mailto:contact@agentpackaging.org)  
🧑‍💻 **Community contributions:** [community@agentpackaging.org](mailto:community@agentpackaging.org)  
🧠 **Governance and policy:** [governance@agentpackaging.org](mailto:governance@agentpackaging.org)

---

*© 2025 Agent Packaging Standard (APS) Working Group. All rights reserved.*