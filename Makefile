.PHONY: help install test lint clean cli ui serve

# Default command when just running 'make'
help:
	@echo "🧠 Epistemic Forge - Developer Experience"
	@echo "----------------------------------------"
	@echo "Available commands:"
	@echo "  make install    - Install the package locally in editable mode with dev dependencies"
	@echo "  make test       - Run the Toulmin claim-lattice benchmark suite"
	@echo "  make lint       - Run Ruff to check code formatting and errors"
	@echo "  make clean      - Remove __pycache__, .pytest_cache, and build files"
	@echo "  make cli        - Test the CLI interface directly"
	@echo "  make serve      - Launch the RESTful FastAPI backend server"

install:
	@echo "Installing Epistemic Forge..."
	pip install --upgrade pip
	pip install -e .[dev]

test:
	@echo "Running evaluation benchmarks..."
	pytest tests/ -v

lint:
	@echo "Linting with Ruff..."
	ruff check .

clean:
	@echo "Cleaning cache and build artifacts..."
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +

cli:
	@echo "Running CLI test query..."
	epistemic-forge --title "RAG vs Long-Context" --question "Is RAG strictly better than Long-Context LLMs?"

ui:
	@echo "Launching Streamlit dashboard (requires the 'ui' extra)..."
	pip install -e ".[ui]"
	streamlit run epistemic_forge/ui/app.py

serve:
	@echo "Booting Enterprise API Server..."
	uvicorn epistemic_forge.ui.api:app --host 0.0.0.0 --port 8000 --reload
