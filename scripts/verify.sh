#!/bin/bash
set -e

echo "---------------------------------------"
echo "Running Verification Script (GirlfriendGPT 2026)"
echo "---------------------------------------"

echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

echo "Step 2: Running Pre-commit hooks (Linting & Formatting)..."
pre-commit run --all-files

echo "Step 3: Running Type Checks (Mypy)..."
mypy src/

echo "Step 4: Running Security Checks (Bandit)..."
bandit -r src/

echo "Step 5: Running Tests & Coverage (100% Guaranteed)..."
python -m pytest

echo "---------------------------------------"
echo "Verification Complete! All checks passed."
echo "---------------------------------------"
