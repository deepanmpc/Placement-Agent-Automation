#!/bin/bash
# run_website.sh - Starts the React Demo Website

echo "Starting React Frontend Server..."

# Go to the react website directory
cd "$(dirname "$0")/react-website"

# Run the Vite dev server
npm run dev
