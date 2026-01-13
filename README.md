# AutoDeployHub 🚀

**AutoDeployHub** is a self-hosted CI/CD and deployment platform. It automates the process of building Docker images and deploying them to Kubernetes clusters whenever code is pushed to GitHub.

## 🏗️ Architecture
- **Backend:** FastAPI (Python 3.13)
- **Database:** PostgreSQL (with SQLAlchemy & Alembic)
- **Containerization:** Docker
- **Orchestration:** Kubernetes (Official Python Client)
- **Security:** HMAC Webhook Signature Verification
- **UI:** Jinja2 + Bootstrap 5 Dashboard

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Desktop (with Kubernetes enabled)
- Git

### Setup
1. Clone this repository.
2. Navigate to the root directory.
3. Start the services:
   ```bash
   docker-compose up -d
   ```
4. Run migrations:
   ```bash
   cd backend
   # Ensure your virtual env is active
   alembic upgrade head
   ```

## 🛠️ How to use
1. **Register a Project**:
   Open the API docs at `http://localhost:8000/docs` and use the `POST /projects/` endpoint to register your GitHub repository.
2. **Setup Webhook**:
   Go to your GitHub Repo -> Settings -> Webhooks.
   - Payload URL: `http://<your-server>/webhooks/github`
   - Content type: `application/json`
   - Secret: (Check `GITHUB_WEBHOOK_SECRET` in `config.py`)
3. **Push Code**:
   Push to your specified branch. AutoDeployHub will:
   - Clone the repo.
   - Build a Docker image using the `Dockerfile` in the repo root.
   - Deploy/Update the service in your Kubernetes cluster.

## 📊 Dashboard
Access the visual dashboard at `http://localhost:8000/` to monitor your projects and see logs of recent deployments.

### 🔐 Authentication Setup (Optional for Local)
To enable GitHub OAuth:
1. Go to your [GitHub Developer Settings](https://github.com/settings/developers) and create a "New OAuth App".
2. Set **Homepage URL** to `http://localhost:8000`
3. Set **Authorization callback URL** to `http://localhost:8000/auth/callback`
4. Copy the **Client ID** and **Client Secret**.
5. Update `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` in your `backend/.env` file.
6. Restart your backend.
