---
description: A guided prompt for users to create technical documentation using SOP or Install Guide templates, with dynamic audience capture, template selection, section-by-section guidance, formatting flexibility, and iterative review.
---
# Technical Documentation Construction Meta-Prompt

**Instructions:**

This prompt will guide you through the process of creating technical documentation. You will be asked to select a template, identify your audience, and contribute content for each section. Placeholder text will be provided where needed. The process is iterative—review and refine as you go.

---
## Step 1: Capture Topic and Audience

- What is the topic of your documentation?
- Who is the intended audience? (e.g., technical staff, end users, support team)

## Step 2: Select Documentation Template

- Choose the template that best fits your needs:
- Standard Operating Procedure (SOP)
- Installation Guide
- Microsoft Document Type (e.g., Knowledge Article, How-To, FAQ)

## Step 3: Section-by-Section Guidance (Soft Gating)

For each section below, provide as much detail as possible. If unsure, use placeholder text and refine later.

### SOP Template Sections

1. **Purpose**: What is the goal of this SOP?
2. **Scope**: What systems, teams, or processes does this SOP cover?
3. **Roles and Responsibilities**: Who is involved and what are their duties?
4. **Procedures**: List step-by-step instructions for the process.
5. **Troubleshooting**: Common issues and solutions.
6. **Compliance/Regulatory**: Any standards or policies to follow.
7. **Revision History**: Track changes and updates.

### Install Guide Template Sections

1. **Introduction**: Brief overview of the installation.
2. **Prerequisites**: What is required before starting?
3. **Installation Steps**: Detailed, ordered instructions.
4. **Verification**: How to confirm successful installation.
5. **Troubleshooting**: Common installation problems and fixes.
6. **Support/Contact**: Where to get help.
7. **Revision History**: Track changes and updates.

### Microsoft Document Types (as applicable)

- **Knowledge Article**: Problem, Solution, Additional Resources
- **How-To**: Task, Steps, Tips
- **FAQ**: Question, Answer, Related Links

## Step 4: Iterative Review and Feedback

- After completing each section, review for clarity and completeness.
- Solicit feedback from stakeholders or end users.
- Update sections as needed and document changes in the Revision History.

## Step 5: Finalization and Publishing

- Ensure all sections are complete and accurate.
- Format the document according to organizational standards (Markdown, Word, etc.).
- Publish to the appropriate repository or knowledge base.

---

## Appendix A: Full SOP Template

```markdown
---
title: "[SOP Title Placeholder]"
description: "[Brief description of the SOP]"
type: "SOP"
version: "[template]"
author: "[Author/Team]"
date: "[YYYY-MM-DD]"
---

<!-- SOP Title and Logo Row -->
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5em;">
  <h1 style="margin: 0; font-size: 2em;">[SOP Title Placeholder]</h1>
  <img src="https://rwdn-uploads.s3.amazonaws.com/mcgl15001/production/54b7a8d305541296303508cec6e5dfb6.png" alt="Company Logo" style="height:60px; max-width:180px; object-fit:contain;">
</div>

## Introduction

### Purpose

[State the purpose of this SOP.]

### Audience

[Who is this SOP for?]

### Scope

[What does this SOP cover?]

---

## Definitions

[Define any key terms or acronyms used in this SOP.]

---

## Prerequisites / Required Tools & Access

- [List required systems, permissions, or tools.]

---

## Procedure

### Step 0: Ticket Handling

[Describe how tickets should be received, validated, categorized, prioritized, and assigned before beginning technical steps. Include any scenario-based triage, required information, and communication guidelines.]

### Step 1: [Phase/Step Title]

[Describe the first step or phase.]

### Step 2: [Phase/Step Title]

[Describe the next step or phase.]

<!-- Repeat as needed for all steps -->

---

## Post-Procedure Actions

[List any follow-up actions, documentation, or verifications required.]

---

## Escalation Procedures

- [Describe what to do if something goes wrong or is out of scope.]

---

## References / Related Documents

- [Link to related SOPs, policies, or external resources.]

---

## Revision History

| Version | Date       | Author        | Description           |
| ------- | ---------- | ------------- | --------------------- |
| Template    | YYYY-MM-DD | [Author/Team] | Initial template      |
```

---

## Appendix B: Full Install Guide Template

```markdown
---
title: "[Install Guide Title Placeholder]"
description: "[Brief description of the install guide]"
type: "Install Guide"
version: "[template]"
author: "[Author/Team]"
date: "[YYYY-MM-DD]"
---
 
<!-- Guide Title and Logo Row -->
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5em;">
  <h1 style="margin: 0; font-size: 2em;">[Install Guide Title Placeholder]</h1>
  <img src="https://rwdn-uploads.s3.amazonaws.com/mcgl15001/production/54b7a8d305541296303508cec6e5dfb6.png" alt="Company Logo" style="height:60px; max-width:180px; object-fit:contain;">
</div>

<!-- Table of Contents (Optional: Remove if guide is short) -->
## Table of Contents *(remove if not needed)*

- [Introduction](#introduction)
- [Definitions](#definitions)
- [Prerequisites / Required Tools & Access](#prerequisites--required-tools--access)
- [Installation Procedure](#installation-procedure)
- [Post-Installation Actions](#post-installation-actions)
- [Troubleshooting / Escalation Procedures](#troubleshooting--escalation-procedures)
- [References / Related Documents](#references--related-documents)
- [Revision History](#revision-history)

## Introduction

### Purpose

[State the purpose of this install guide.]

### Audience

[Who is this guide for? (e.g., end users, IT staff, installers)]

### Scope

[What does this guide cover? (e.g., product, system, or environment)]

---

## Definitions

[Define any key terms, acronyms, or product names used in this guide.]

---

## Prerequisites / Required Tools & Access

- [List required hardware, software, permissions, or tools.]

---

## Installation Procedure

### Step 1: Preparation

1. [Unpack all components and verify contents.]
2. [Prepare the environment (e.g., clear workspace, check power/network access).]

> **Note:** Use semantic headings and provide alt text for all images/screenshots.

### Step 2: Physical/Software Installation

1. [Mount hardware, connect cables, or run the installer.]
2. [Follow on-screen prompts or physical installation instructions.]

> **Warning:** [Call out any critical warnings, e.g., "Do not power on until all cables are connected."]

### Step 3: Configuration

1. [Set up network, create accounts, or adjust initial settings.]
2. [Document any default credentials and prompt for change.]

### Step 4: Verification

1. [Verify installation by powering on, logging in, or running a test.]
2. [Check for error messages or abnormal behavior.]

<!-- Add or remove steps as needed for your product/process -->

---

## Post-Installation Actions

- [List any follow-up actions, documentation, or verifications required after installation.]

---

## Troubleshooting / Escalation Procedures

| Issue | Resolution |
| --- | --- |
| [Example: Installer fails to launch] | [Check system requirements, run as administrator] |
| [Example: Device not detected] | [Verify connections, check drivers] |

- [Add more issues and resolutions as needed.]

**Support Contact:** [Insert support email, phone, or ticketing system link.]

---

## References / Related Documents

- [Link to related guides, manuals, or support resources.]

---

## Revision History

| Version | Date       | Author        | Description           |
| ------- | ---------- | ------------- | --------------------- |
| Template   | YYYY-MM-DD | [Author/Team] | Initial template      |
```

---
**Note:** This prompt is designed to be flexible and accessible. Use it as a living document—update and iterate as your process evolves.
