#!/bin/bash

# Create assets directories
mkdir -p src/static/assets/fonts
mkdir -p src/static/assets/images

# Copy fonts and images from govuk-frontend
cp -r node_modules/govuk-frontend/dist/govuk/assets/fonts/* src/static/assets/fonts/
cp -r node_modules/govuk-frontend/dist/govuk/assets/images/* src/static/assets/images/