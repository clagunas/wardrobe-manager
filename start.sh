#!/bin/bash

echo "Starting MongoDB..."
brew services start mongodb-community

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting FastAPI server..."
uvicorn main:app --reload