# LLM-Powered Code Review Assistant

This project provides a GitHub Actions workflow to automatically review code in pull requests using a Large Language Model (LLM). It acts as an AI-powered assistant to help maintain code quality, identify potential issues, and enforce best practices.

## How It Works

1.  **Trigger**: The workflow is automatically triggered on any `pull_request` to the repository.
2.  **File Detection**: It uses the `tj-actions/changed-files` action to identify all files that have been modified in the pull request.
3.  **Code Analysis**: The list of changed files is passed to the core Python script, `.github/scripts/llm_review.py`.
4.  **LLM Review**: The script is responsible for sending the content of the changed files to an LLM, guided by a detailed prompt that instructs the AI to act as a senior software engineer. The prompt directs the LLM to check for:
    - Security vulnerabilities
    - Architectural and design principles
    - Performance issues
    - Code style and readability
    - Best practices

## Setup

To use this workflow, you must configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

-   `LLM_PROVIDER`: The name of the LLM provider you are using (e.g., `gemini`, `openai`).
-   `LLM_API_KEY`: Your API key for the chosen provider.

## Current Status & Future Work

This repository contains the foundational structure for the workflow. The `llm-review.yml` workflow is fully configured.

The core logic in `.github/scripts/llm_review.py` is currently a **placeholder**. It correctly parses arguments and reads the changed files but does not yet make an actual API call to an LLM. The next step is to implement the `analyze_code_with_llm` function to send the code and the built-in prompt to your chosen LLM provider's API.

## The `agents/` Directory

The `.github/agents/` directory contains specialized "persona" files (e.g., `fastapi-expert.md`). These are detailed prompts that define different expert AI agents. This suggests a future vision where the workflow could dynamically select a specialized agent based on the type of code being reviewed.
