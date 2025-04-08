.PHONY: setup run clean

setup:
	@echo "🐍 Setting up virtual environment..."
	python3 -m venv venv
	@echo "📦 Installing dependencies..."
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

run:
	@echo "🚀 Running ETL script..."
	./venv/bin/python read_and_transform.py

clean:
	@echo "🧹 Cleaning up..."
	rm -rf venv
