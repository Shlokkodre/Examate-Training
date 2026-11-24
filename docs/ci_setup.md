# CI Setup — HealthLabelCheck

GitHub Actions CI runs on every push and pull request to `main`.

## Badge

[![CI](https://github.com/Shlokkodre/Examate-Training/actions/workflows/ci.yml/badge.svg)](https://github.com/Shlokkodre/Examate-Training/actions/workflows/ci.yml)

## What runs

- **202 tests** across 6 test files
- `test_pdf_parser.py` — 27 tests (PDF extraction pipeline)
- `test_label_checker.py` — 32 tests (OCR regex rules)
- `test_translations.py` — 32 tests (EN/MR/HI translations)
- `test_whatsapp_bot.py` — 51 tests (WhatsApp bot logic)
- `test_integration.py` — 40 tests (FastAPI endpoints end-to-end)
- `test_feedback.py` — 20 tests (feedback stats)

## Workflow file

`.github/workflows/ci.yml` — triggers on push and PR to `main`.

## Live deploy

API: https://healthlabelcheck-api-latest.onrender.com/docs
