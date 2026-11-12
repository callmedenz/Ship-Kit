# 🚀 DevSecOps CI/CD Pipeline with Kubernetes and GitOps

## 📌 Overview
This project demonstrates a complete DevSecOps pipeline by deploying a containerized application using modern cloud-native tools.

A simple static portfolio website (`index.html`) is used as the application.

> ⚠️ Note: This project uses a simple static website for demonstration, but the same pipeline can be applied to any application such as a Node.js app, Python app, or microservices-based system.

---

## ⚙️ Tech Stack
- Docker  
- Kubernetes  
- GitHub Actions (CI/CD)  
- Trivy (Security Scanning)  
- ArgoCD (GitOps)  
- Prometheus & Grafana (Cluster & App Monitoring)  

---

## 🔄 Workflow
Code Push → GitHub Actions → Docker Build → Trivy Scan → Docker Hub → Kubernetes → ArgoCD Sync → Prometheus & Grafana Monitoring

---

## 🐳 Containerization
- Application containerized using Docker  
- Served using Nginx  

---

## ⚙️ CI/CD Pipeline
- Automated build on every push  
- Vulnerability scanning using Trivy  
- Image pushed to Docker Hub  

---

## ☸️ Kubernetes Deployment
- Deployment and Service YAML files  
- Application exposed using NodePort  

---

## 🔄 GitOps with ArgoCD
- Kubernetes manifests stored in GitHub  
- ArgoCD automatically syncs changes to cluster  

---

## 📊 Monitoring & Observability (Prometheus & Grafana)
- **Prometheus**: Collects real-time metrics from the cluster, nodes, and application pods.
- **Grafana**: Pre-configured dashboards for visualizing cluster health, CPU/memory usage, and pod performance.
- Automated deployment via Helm with `kube-prometheus-stack`.

---

## 🧪 How to Run Locally

### 1. Clone repository
```bash
git clone https://github.com/callmedenz/DevSecOps-CICD-Pipeline
cd DevSecOps-CICD-Pipeline
```

### 2. Run using Docker
```bash
docker build -t portfolio-app .
docker run -p 8080:80 portfolio-app
```

### 3. Run on Kubernetes
```bash
kubectl apply -f k8s/
minikube service portfolio-service
```

### 4. Deploy Monitoring Stack (Prometheus & Grafana)

**Via ArgoCD (GitOps):**
```bash
kubectl apply -f argocd/monitoring.yaml
```

**Or via Helm:**
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f k8s/monitoring/values.yaml
```

**Access Dashboards:**
- **Grafana**: Port-forward with `kubectl port-forward -n monitoring svc/monitoring-stack-grafana 3000:80` → `http://localhost:3000` (User: `admin`, Password: `admin`)
- **Prometheus**: Port-forward with `kubectl port-forward -n monitoring svc/monitoring-stack-kube-prom-prometheus 9090:9090` → `http://localhost:9090`

---

## 👨‍💻 Author
Dennis Pradhan
