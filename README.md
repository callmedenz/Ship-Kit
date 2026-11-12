# ShipKit 🚀
**Production-Ready DevSecOps Automation & CI/CD Pipeline for FastAPI Applications**

ShipKit is a lightweight, reusable DevSecOps automation platform designed to streamline security scanning, containerization, and Kubernetes deployment for FastAPI services. It bridges the gap between raw application code and a secure, scalable production environment with zero manual infrastructure overhead.

---

## 🏗️ System Architecture

The following diagram illustrates the complete end-to-end data flow from code commit to local Kubernetes ingress routing:

```mermaid
graph TD
    A[Developer Push] -->|GitHub Actions| B(CI/CD Pipeline)
    subgraph Security & Quality Gates
        B -->|Gitleaks| C[Secret & Leak Scan]
        B -->|Pytest + Httpx| D[Unit Test Suite]
        B -->|Trivy| E[Container Vulnerability Scan]
    end
    E -->|Push Image| F[(GitHub Container Registry\n`ghcr.io/callmedenz/shipkit`)]
    F -->|Pull Image| G[Kubernetes Cluster\n`docker-desktop` / VPS]
    subgraph Kubernetes Environment
        G --> H[Deployment Pods\n`FastAPI /health`]
        H --> I[NodePort Service\nPort 8000]
        I --> J[NGINX Ingress Controller\n`shipkit.local`]
    end
    J -->|HTTP Request| K([Client / Browser])
```

---

## 🛠️ Tech Stack

* **Application Framework:** FastAPI (Python), tested via `pytest` and `httpx`
* **Security & Compliance:** 
  * **Gitleaks:** Automated secret and credential leak scanning
  * **Trivy:** Container vulnerability scanning
* **Containerization:** Docker, optimized with `.dockerignore` contexts and hosted securely on GitHub Container Registry (`ghcr.io`)
* **Orchestration:** Kubernetes (Local via Docker Desktop / K3s compatible)
* **Traffic Routing:** NGINX Ingress Controller with custom local DNS mapping (`shipkit.local`)
* **CI/CD Automation:** GitHub Actions workflows configured with granular permissions (`contents: read`, `packages: write`, `security-events: write`)

---

## 📂 Repository File Structure

```text
D:\ShipKit\
├── .github\
│   └── workflows\
│       └── ci-cd.yml      # Automated build, security scan, and GHCR push pipeline
├── k8s\
│   ├── deployment.yaml    # Kubernetes Deployment manifest with health probes
│   ├── service.yaml       # Kubernetes Service manifest (NodePort mapping)
│   └── ingress.yaml       # NGINX Ingress controller routing rule
├── app\
│   └── main.py            # FastAPI application entrypoint with /health endpoint
├── test_main.py           # Pytest suite utilizing TestClient and httpx
├── Dockerfile             # Multi-stage container build definition
├── requirements.txt       # Python dependencies (FastAPI, Uvicorn, Httpx)
└── README.md              # Project documentation
```

---

## ⚙️ Core Features & Workflow

1. **Automated Security Gates:** Every push triggers Gitleaks to inspect code for accidental secret leaks and runs unit tests using `pytest` with `httpx`.
2. **Vulnerability Scanning:** Container images are scanned for vulnerabilities via Trivy before being published.
3. **Registry Publication:** Verified images are automatically tagged and pushed to GitHub Container Registry (`ghcr.io/callmedenz/shipkit:latest`).
4. **Resilient Kubernetes Deployment:** Deploys with readiness and liveness probes targeting the `/health` endpoint on port `8000` to ensure high availability.
5. **Seamless Traffic Management:** Handled locally through NGINX Ingress mapping to `http://shipkit.local/health`.

---

## 🚀 Quick Start & Verification

### 1. Run Tests Locally
```powershell
python -m pytest test_main.py
```

### 2. Build and Test Docker Image Locally
```powershell
docker build -t ghcr.io/callmedenz/shipkit:latest .
docker run -d -p 8000:8000 --name shipkit-app ghcr.io/callmedenz/shipkit:latest
curl http://localhost:8000/health
```

### 3. Deploy to Kubernetes Cluster
Apply your manifests to your active cluster context (`docker-desktop` or your remote VPS):
```powershell
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Live Ingress Route
Make sure your Windows hosts file (`C:\Windows\System32\drivers\etc\hosts`) includes:
```text
127.0.0.1 shipkit.local
```
Then, open your browser or run:
```powershell
curl http://shipkit.local/health
```
*(Expected response: `{"status": "healthy", "version": "1.0.0"}`)*