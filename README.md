# NatWest Hack4aCause Submission

PROJECT GITHUB (Direct Link): https://github.com/finos-labs/learnaix-h-2025-tech-titans/tree/aniket/push-setup


FOR Codes (PATH_TO_FOLLOW): https://github.com/finos-labs/learnaix-h-2025-tech-titans/tree/aniket/push-setup/example/plugin-development-templates/with-php/plugin-local-aicompanion/python


![badge-labs](https://user-images.githubusercontent.com/327285/230928932-7c75f8ed-e57b-41db-9fb7-a292a13a1e58.svg)

This repository was forked from [finos-labs/learnaix-h-2025](https://github.com/finos-labs/learnaix-h-2025).

Please complete this README per the hackathon template. Keep the sections below concise.

## 📄 Summary of Our Solution (≤150 words)
AI Learning Companion that personalizes support for students on Moodle. It delivers context-aware assistance, explains course content in simple terms, generates quizzes, and provides progress insights for learners and instructors. The companion integrates as a Moodle local plugin backed by a lightweight Python/Flask AI service. It uses LLMs (e.g., Google Gemini or OpenAI) for conversational help and optional analytics via Snowflake or local mock data. The system is modular, easy to deploy locally, and designed for privacy by keeping institution data within controlled environments.

## 👥 Team Information
| Field            | Details (edit these)                    |
| ---------------- | --------------------------------------- |
| Team Name        | team name                               |
| Title            | AI Learning Companion                   |
| Theme            | AI companion                            |
| Contact Email    | arya.aniket9835@gmail.com, archita26basutkar@gmail.com |
| Participants     | Aniket Arya, Archita, Vani Verma, Nisarga |
| GitHub Usernames | [@aryaaniket008](https://github.com/aryaaniket008), [@Archita0304](https://github.com/Archita0304), [@Vaani64](https://github.com/Vaani64), [@Nisarga253](https://github.com/Nisarga253) |

## 🎥 Submission Video
- 📹 Video Link: https://drive.google.com/file/d/1nxHZRMMX7C2mg1a9rZnkVXuj-hABP12V/view?usp=sharing

## 🌐 Hosted App / Solution URL
- 🌍 Deployed URL: <add link if deployed>

## 📦 What’s in this repo
- Moodle plugin templates under `example/plugin-development-templates/`
- Our AI service (Flask) in `example/.../plugin-local-aicompanion/python/`
- Local Moodle setup guides under `example/moodle-local-setup/`

## ⚙️ How to run the AI service locally
1. cd `example/plugin-development-templates/with-php/plugin-local-aicompanion/python`
2. Create `.env` from `.env.example` and set keys
3. Install deps: `pip install -r simple_requirements.txt` or `requirements.txt`
4. Run: `python simple_ai_service.py`
5. Open http://localhost:5000 and test `/test`, `/chat`, `/analytics/1`

Notes:
- Gemini/OpenAI key required for live AI responses.
- Snowflake is optional; mock analytics work without it.

## 🔗 Integrations
- AI: Google Gemini via `simple_ai_service.py` (env `GEMINI_API_KEY`)
- Optional: OpenAI + Snowflake via `ai_service.py` (env variables; see `INSTALLATION.md`)

## 📝 License
Copyright 2025 FINOS

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)
