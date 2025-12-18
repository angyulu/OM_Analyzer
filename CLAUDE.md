<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

﻿# OM_V0 Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-12-07

## Active Technologies

- Python 3.10+ + PyQt6 (UI framework), OpenCV (cv2), scikit-image, NumPy (array operations), Pandas (CSV export) (001-thin-film-analyzer)

## Project Structure

```text
src/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

Python 3.10+: Follow standard conventions

## Recent Changes

- 001-thin-film-analyzer: Added Python 3.10+ + PyQt6 (UI framework), OpenCV (cv2), scikit-image, NumPy (array operations), Pandas (CSV export)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
