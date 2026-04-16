# Contributing Guidelines

This document describes the **intentional Git workflow** used in this repository. The goal is to keep history clean, minimize merge noise, and reduce unnecessary process overhead while still staying safe and deliberate.

These guidelines assume:

* Short‑lived feature branches
* Primarily independent, non‑overlapping changes
* Emphasis on clarity and intent over automation

***

## Branching Strategy

### Main branch (`main`)

* `main` represents **stable, reviewable history**
* Changes land on `main` via pull requests (PRs)
* Direct commits to `main` should be avoided unless explicitly approved

***

### Feature branches

* New work should be done on feature branches:
  * feat/short-description
  * project/short-description
  * chore/short-description
* Feature branches should be **focused and intentional**
* Avoid mixing unrelated work in the same branch

Example:

```bash
git switch -c feat-reporting-shard
```

***

## Keeping Feature Branches Up to Date

Feature branches are **not required** to be constantly rebased against `main`.

### Default rule (most of the time)

> **Do nothing. Keep working.**

If your branch:

* Is independent
* Is not affected by recent `main` changes
* Is developing cleanly and testing successfully

…then there is no requirement to update it mid‑stream.

Rebasing is considered a **tool**, not a requirement.

***

### When rebasing *is* appropriate

Rebase a feature branch onto `main` when:

* `main` has received changes that affect your branch’s behavior
* You are preparing to open a PR
* You want to reduce integration risk before merging

***

### How to rebase correctly (Option A)

> Rebasing always affects **only the current branch**, not `main`.

From the feature branch:

```bash
git status        # confirm you are on the feature branch
git fetch origin
git rebase origin/main
```

This:

* Replays the feature branch’s commits on top of the latest `main`
* Does **not** modify `main`
* May create new commit hashes for the feature branch only

If there are no new commits on `main`, rebasing is unnecessary and should be skipped.

***

## Decision Check Before Rebasing

Before rebasing, confirm whether it provides value:

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

* If this command shows **no commits**, rebasing offers no benefit
* In that case: **do nothing and continue working**

***

## Pull Requests and Merging

Before opening a PR:

1. Ensure the branch builds and tests cleanly
2. Optionally rebase onto the latest `main`
3. Confirm the branch scope is intentional and self‑contained

After merge:

* Delete the feature branch (local and remote)
* Avoid leaving stale branches behind

***

## Handling Accidental Commits on the Wrong Branch

If a commit is made on the wrong branch:

### If the commit logically belongs to the feature

✅ Leave it — no action needed.

### If the commit belongs on `main`

Use a **cherry‑pick + reset** workflow:

1. Cherry‑pick the commit onto `main`
2. Reset the feature branch back to its remote state

This avoids rebasing or rewriting shared history.

***

## Branch Cleanup

To identify local branches whose upstream no longer exists:

```bash
git branch -vv | grep ': gone]'
```

If confirmed obsolete, delete intentionally:

```bash
git branch -D <branch-name>
```

Branch deletion is considered part of normal repo hygiene.

***

## Guiding Principles

* Prefer **clarity over cleverness**
* Rebasing is optional, intentional, and local
* Doing nothing is a valid decision
* The branch you are *on* is the only branch modified by rebase
* Clean history is valuable, but not at the expense of momentum

***

## Summary

This workflow aims to:

* Reduce cognitive overhead
* Avoid unnecessary Git operations
* Keep history readable and intentional
* Reflect how work is actually done, not how tools are marketed

If you are unsure whether to rebase, merge, or wait:

> **Stop, check the current state, and choose the smallest action that solves the problem.**

***
