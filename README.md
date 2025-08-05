# Hello World Kubernetes Demo

A simple Kubernetes-based demo app that shows a "hello world, {name}" message, where `{name}` is loaded from a PostgreSQL database.

## Project Structure

```
hello-k8s-demo/
├── frontend/                 # Flask web server
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── database/                 # PostgreSQL initialization
│   ├── init.sql
│   └── Dockerfile
└── k8s/                      # Kubernetes manifests
    ├── namespace.yaml
    ├── postgres-secret.yaml
    ├── postgres-deployment.yaml
    ├── postgres-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

---

## Prerequisites

- Docker and Docker Hub account
- A Kubernetes cluster (e.g., Minikube, kind, or cloud-provided) and `kubectl` configured
- (`jq` CLI, optional, for inspecting Docker config)

---

## 1. Frontend

### `frontend/app.py`

```python
from flask import Flask
import psycopg2
import os

# Read DB settings from environment
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')

# Connect and fetch name
conn = psycopg2.connect(
    host=DB_HOST, port=DB_PORT,
    dbname=DB_NAME, user=DB_USER, password=DB_PASS
)
cur = conn.cursor()
cur.execute("SELECT name FROM users LIMIT 1;")
name = cur.fetchone()[0]

app = Flask(__name__)

@app.route('/')
def hello():
    return f"hello world, {name}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### `frontend/requirements.txt`

```
Flask==2.2.5
psycopg2-binary==2.9.6
```

### `frontend/Dockerfile`

```dockerfile
FROM python:3.9-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

EXPOSE 5000
CMD ["python", "app.py"]
```

---

## 2. Database

### `database/init.sql`

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

INSERT INTO users (name) VALUES ('Your Name');
```

### `database/Dockerfile`

```dockerfile
FROM postgres:13
COPY init.sql /docker-entrypoint-initdb.d/
```

---

## 3. Kubernetes Manifests (k8s/)

### `k8s/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: hello-demo
```

### `k8s/postgres-secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: hello-demo
type: Opaque
stringData:
  POSTGRES_DB: hello_db
  POSTGRES_USER: hello_user
  POSTGRES_PASSWORD: supersecret
```

### `k8s/postgres-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: hello-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: ${DOCKERHUB_USERNAME}/hello-postgres:latest
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: postgres-secret
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: data
          emptyDir: {}
```

### `k8s/postgres-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: hello-demo
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  clusterIP: None
```

### `k8s/frontend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: hello-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: ${DOCKERHUB_USERNAME}/hello-frontend:latest
          ports:
            - containerPort: 5000
          env:
            - name: DB_HOST
              value: postgres.hello-demo.svc.cluster.local
            - name: DB_PORT
              value: "5432"
            - name: POSTGRES_DB
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_DB
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
```

### `k8s/frontend-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: hello-demo
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - port: 5000
      targetPort: 5000
      nodePort: 30007
```

---

## 4. Build & Deploy

From the project root (`hello-k8s-demo`):

```bash
# Set Docker Hub user
export DOCKERHUB_USERNAME=your-dockerhub-username

# 1. Build & push images
cd frontend
docker build -t $DOCKERHUB_USERNAME/hello-frontend:latest .
docker push $DOCKERHUB_USERNAME/hello-frontend:latest

cd ../database
docker build -t $DOCKERHUB_USERNAME/hello-postgres:latest .
docker push $DOCKERHUB_USERNAME/hello-postgres:latest

# 2. Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 3. Access
minikube service frontend -n hello-demo
```

---

## Considerations

- **Secrets**: Stored in K8s Secrets; consider Vault in production.
- **Storage**: `emptyDir` used for demo; replace with PVC for persistence.
- **Scaling**: Adjust replicas and resource requests/limits.
- **CI/CD**: Integrate with GitHub Actions or similar.

---

## References

- [Flask](https://flask.palletsprojects.com/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Kubernetes Docs](https://kubernetes.io/docs/)

---

## Publishing to GitHub

To add this project and README to a GitHub repository:

1. **Create a new repo** on GitHub (e.g., `hello-k8s-demo`).
2. **Initialize your local directory** (if not already a git repo):
   ```bash
   cd path/to/hello-k8s-demo
   git init
   ```
3. **Add all files** and commit:
   ```bash
   git add .
   git commit -m "Initial commit: add Kubernetes hello world demo"
   ```
4. **Add the GitHub remote** (replace with your GitHub username):
   ```bash
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/hello-k8s-demo.git
   ```
5. **Push to GitHub**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

Your `README.md` will now be visible on your GitHub repo’s main page.

