#!/bin/bash
set -e

echo "---------------------------------------"
echo "Running Verification Script (GirlfriendGPT 2026)"
echo "---------------------------------------"

echo "Step 1: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Step 2: Running Pre-commit hooks (Linting, Formatting, Types, Security)..."
pre-commit run --all-files

echo "Step 3: Running Tests & Coverage (100% Guaranteed)..."
python -m pytest

echo "---------------------------------------"
echo "Verification Complete! All checks passed."
echo "---------------------------------------"
