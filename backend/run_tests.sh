#!/bin/bash
# Test Runner Script for Sistema de Laudos

set -e

echo "🚀 Running Tests for Sistema de Laudos API"
echo "=========================================="
echo ""

# Navigate to backend directory
cd /opt/app/sistema_de_laudos/backend

# Check if requirements are installed
echo "📦 Checking dependencies..."
python3 -c "import fastapi" 2>/dev/null || {
    echo "❌ FastAPI not found. Installing dependencies..."
    python3 -m pip install -r requirements.txt --quiet
}

# Run tests
echo ""
echo "🧪 Running pytest..."
python3 -m pytest tests/ -v --tb=short --cov=app --cov-report=html --cov-report=term-missing 2>&1 | tee test_results.log

# Display summary
echo ""
echo "=========================================="
echo "✅ Test run complete!"
echo "📊 Coverage report generated: htmlcov/index.html"
echo "📝 Full results saved to: test_results.log"
