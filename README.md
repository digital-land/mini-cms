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

1. Clone the repository
2. Run `source .venv/bin/activate`
3. Run `python -m venv .venv`
4. Run `pip install -r requirements.txt`
5. Run `fastapi dev main.py`

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

