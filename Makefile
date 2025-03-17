.PHONY: all clean assets css js

# Output directories
STATIC_DIR = src/static
DIST_DIR = $(STATIC_DIR)/dist
ASSETS_DIR = $(STATIC_DIR)/assets

# Source files
SCSS_SRC = $(STATIC_DIR)/scss/main.scss
JS_SRC = $(STATIC_DIR)/js/main.js

# Output files
CSS_OUT = $(DIST_DIR)/css/main.css
JS_OUT = $(DIST_DIR)/js/main.js

# Default target
all: clean assets css js install

# Clean build files
clean:
	rm -rf $(DIST_DIR)
	mkdir -p $(DIST_DIR)/css
	mkdir -p $(DIST_DIR)/js

# Copy GOV.UK Frontend assets
assets:
	./copy-assets.sh

# Compile SCSS to CSS
css:
	npm run build:css

# Bundle JavaScript
js:
	npm run build:js

# Watch for changes (development)
watch:
	npm run watch:css & npm run watch:js

# Install dependencies
install:
	pip install -r requirements.txt

# Run the FastAPI application
run:
	uvicorn src.main:app --reload
