---
title: HealthLabelCheck
emoji: 🥘
colorFrom: green
colorTo: orange
sdk: streamlit
sdk_version: "1.30.0"
app_file: app.py
pinned: false
license: mit
short_description: FSSAI food label compliance checker for small food makers
---

# HealthLabelCheck

**FSSAI Food Labelling Advisor for Small Food Businesses**

Helps home-based snack makers (chakli, laddoo, farsan) check what must
be printed on their food packet labels before they go to press.

## Features

- 💬 **Ask a Question** — RAG-powered answers with regulation citations
- 📐 **Font Size Calculator** — instant Regulation 6.1 result from panel dimensions  
- ✅ **Mandatory Checklist** — all 10 mandatory label items with exemptions
- 📋 **Browse Regulations** — keyword-searchable view of all 14 FSSAI regulations

## Setup

Set `GROQ_API_KEY` in Spaces Secrets for LLM-powered answers.
Without a key the app falls back to rule-based answers from retrieved regulation text.

## Data

Based on FSSAI Labelling and Display Regulations 2020–2022.
For educational purposes only — always verify with official FSSAI documents.
