# Mini CMS

A headless git based CMS for managing content for guidance pages.

## Features

- [ ] Add a new page
- [ ] Edit a page
- [ ] Delete a page
- [ ] View a page
- [ ] View a page history
- [ ] Rollback to a previous version of a page
- [ ] Add a new version of a page
- [ ] Edit a version of a page
- [ ] Delete a version of a page

## Getting Started

### Option 1: Local Development

1. Clone the repository
2. Run `python -m venv .venv`
3. Run `source .venv/bin/activate`
4. Run `pip install -r requirements.txt`
5. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your values:
   - Get GitHub OAuth credentials from GitHub > Settings > Developer settings > OAuth Apps
   - Generate a secure random key for APP_KEY
   - Update APP_HOST if not running on localhost:8000
6. Run `npm run dev`

### Option 2: Using Docker (Recommended)

1. Clone the repository
2. Make sure you have Docker and Docker Compose installed
3. Set up environment variables (same as in Option 1):
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your GitHub OAuth credentials
4. Build and start the containers:
   ```bash
   docker compose up --build
   ```
5. For subsequent runs, simply use:
   ```bash
   docker compose up
   ```
6. To stop the containers:
   ```bash
   docker compose down
   ```

The application will be available at `http://localhost:8000` in both cases.

### Development with Docker

- The application uses hot-reload, so any changes you make to the code will automatically trigger a reload
- Application logs can be viewed using `docker compose logs -f`
- To run commands inside the container:
  ```bash
  docker compose exec web <command>
  ```

## API

The API is available at `http://localhost:8000`

### Collections

#### Get all collections

```bash
curl -X GET "http://localhost:8000/collections"
```

#### Get a collection by id

```bash
curl -X GET "http://localhost:8000/collections/{collection_id}"
```

### Collection Content Items

#### Get all content items for a collection

```bash
curl -X GET "http://localhost:8000/collections/{collection_id}/content-items"
```

#### Get a content item by id

```bash
curl -X GET "http://localhost:8000/collections/{collection_id}/content-items/{content_item_id}"
```

#### Create a new content item

```bash
curl -X POST "http://localhost:8000/collections/{collection_id}/content-items" -H "Content-Type: application/json" -d '{"title": "My Content Item", "body": "This is my content item"}'
```

#### Update a content item

```bash
curl -X PUT "http://localhost:8000/collections/{collection_id}/content-items/{content_item_id}" -H "Content-Type: application/json" -d '{"title": "My Content Item", "body": "This is my content item"}'
```

#### Delete a content item

```bash
curl -X DELETE "http://localhost:8000/collections/{collection_id}/content-items/{content_item_id}"
```
