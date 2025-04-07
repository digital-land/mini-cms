# Mini CMS

A headless git based CMS for managing content.

## Features

- [ ] Add a new content item
- [x] Edit a content item
- [ ] Delete a content item
- [x] View a content item
- [ ] View a content item history
- [ ] Rollback to a previous version of a content item
- [ ] Add a new version of a content item
- [ ] Edit a version of a content item
- [ ] Delete a version of a content item
- [ ] API - Retrieve content item

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

## Setting up a Github Application

The Mini CMS platform uses Github as it's storage and authentication. To ensure that the correct permissions are requested, we require a Github App to be set up.

To set up an application, do the following:
1. Get these from GitHub > Settings > Developer settings > Github Apps (https://github.com/settings/apps)
2. Create a new application with the following configuration:
   - Homepage URL = https://www.your-mini-cms-url/
   - Callback URL = https://www.your-mini-cms-url/auth/callback
   - Request user authorization (OAuth) during installation = CHECKED
   - Permissions & events:
      - Repository Permissions:
         - Metadata = READ ONLY
         - Contents = READ AND WRITE
      - Account Permissions:
         - Email Addresses = READ ONLY
   - Install app = Select `MINI-CMS-DATA` Repo
