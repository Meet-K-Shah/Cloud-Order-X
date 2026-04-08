# CloudOrderX

> **Cloud-Based Order Management System** — Spring Boot · Angular · Python Microservices · Prometheus/Grafana · Terraform · Ansible

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           CloudOrderX Platform                           │
│                                                                          │
│  ┌──────────────┐    REST/WS    ┌──────────────────┐    JDBC/JPA        │
│  │   Angular    │◄────────────►│  Spring Boot API  │◄──────────────────►│
│  │  Frontend    │              │  (Port 8080)      │   PostgreSQL DB    │
│  │  (Port 4200) │              └──────────────────┘                    │
│  └──────────────┘                       │                               │
│                               ┌─────────┼─────────┐                    │
│                               │         │         │                    │
│                    ┌──────────▼──┐  ┌───▼────┐  ┌▼──────────┐        │
│                    │ ETL Service │  │Reporting│  │Notification│        │
│                    │  (8001)     │  │ (8002)  │  │  (8003)    │        │
│                    └──────────┬──┘  └────────┘  └────────────┘        │
│                               │                                         │
│              ┌────────────────▼──────────────────┐                     │
│              │        Prometheus (9090)           │                     │
│              │  scrapes /metrics from all 4 svc  │                     │
│              └────────────────┬──────────────────┘                     │
│                               │                                         │
│                    ┌──────────▼──────────┐                             │
│                    │   Grafana (3000)    │                             │
│                    │  Pre-built dashboard│                             │
│                    └────────────────────┘                             │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | Java 17, Spring Boot 3.2, Spring Data JPA, Spring WebSocket (STOMP), Spring Security |
| **Frontend** | Angular 17, Angular Material, ng2-charts (Chart.js), RxJS |
| **ETL Service** | Python 3.12, FastAPI, Pandas, SQLAlchemy |
| **Reporting** | Python 3.12, FastAPI, ReportLab (PDF), openpyxl (Excel) |
| **Notifications** | Python 3.12, FastAPI |
| **Database** | PostgreSQL 15 (prod), H2 in-memory (local dev) |
| **Metrics** | Micrometer → Prometheus, Grafana (pre-built dashboard) |
| **Container** | Docker, Docker Compose |
| **IaC** | Terraform (AWS VPC/ECS/RDS/ALB), Ansible (deployment playbooks) |

---

## Project Structure

```
CloudOrderX/
├── backend/                        # Spring Boot 3.2 API
│   ├── pom.xml
│   ├── Dockerfile
│   └── src/
│       ├── main/java/com/cloudorderx/
│       │   ├── config/             # WebSocket, Security, Metrics, ExceptionHandler
│       │   ├── controller/         # Order, Product, Customer REST controllers
│       │   ├── dto/                # Request/Response DTOs
│       │   ├── model/              # JPA entities (Order, OrderItem, Customer, Product)
│       │   ├── repository/         # Spring Data JPA repositories
│       │   └── service/            # Business logic + data seeder
│       └── test/
│           └── service/OrderServiceTest.java
│
├── frontend/                       # Angular 17 SPA
│   ├── src/app/
│   │   ├── components/
│   │   │   ├── dashboard/          # KPIs + charts + recent orders
│   │   │   ├── orders/             # Paginated order table with inline status
│   │   │   ├── order-tracking/     # Visual step-by-step order timeline
│   │   │   └── reports/            # Revenue/distribution charts + CSV export
│   │   ├── models/                 # TypeScript interfaces
│   │   └── services/               # ApiService + WebSocketService
│   ├── nginx.conf
│   └── Dockerfile
│
├── microservices/
│   ├── etl-service/                # Extract→Transform→Load pipeline (FastAPI)
│   ├── reporting-service/          # PDF + Excel report generation (FastAPI)
│   └── notification-service/       # Order event webhooks + in-app inbox
│
├── monitoring/
│   ├── prometheus.yml              # Scrape config for all 4 services
│   ├── rules/order_alerts.yml      # Alerting rules (high errors, ETL failure, etc.)
│   └── grafana/
│       ├── provisioning/           # Auto-provision datasource + dashboard
│       └── dashboards/             # Pre-built CloudOrderX Ops dashboard JSON
│
├── infrastructure/
│   ├── db/init.sql                 # PostgreSQL initialization
│   ├── terraform/                  # AWS IaC (VPC, ECS Fargate, RDS, ALB, ECR)
│   │   ├── provider.tf
│   │   ├── variables.tf
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── terraform.tfvars.example
│   └── ansible/                    # Deployment automation
│       ├── playbook.yml            # Bootstrap + Deploy + Monitoring + Rollback plays
│       ├── inventory.ini
│       ├── group_vars/all.yml
│       └── templates/env.j2
│
├── docker-compose.yml              # One-command full-stack local dev
└── .gitignore
```

---

## Quick Start (Local Dev)

### Prerequisites
- Docker Desktop ≥ 24.x
- Java 17+ (for running backend tests locally)
- Node 20+ (for Angular dev server)
- Python 3.12+ (optional, for microservice development)

### 1. Clone and start everything

```bash
git clone https://github.com/your-username/cloudorderx.git
cd cloudorderx
docker compose up -d --build
```

Wait ~60 seconds for the Spring Boot container to finish starting.

### 2. Access the services

| Service | URL | Credentials |
|---------|-----|-------------|
| Angular Frontend | http://localhost:4200 | — |
| Spring Boot API | http://localhost:8080/api/v1 | — |
| H2 Console (dev) | http://localhost:8080/h2-console | sa / (blank) |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| ETL Service | http://localhost:8001/docs | — |
| Reporting | http://localhost:8002/docs | — |
| Notifications | http://localhost:8003/docs | — |

### 3. Trigger a manual ETL run

```bash
curl -X POST http://localhost:8001/run
```

### 4. Download a PDF report

```bash
curl -o report.pdf http://localhost:8002/report/pdf
```

---

## API Reference

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/orders` | List all orders (optional `?status=PENDING`) |
| GET    | `/api/v1/orders/{id}` | Get order by ID |
| GET    | `/api/v1/orders/number/{orderNumber}` | Get order by number |
| GET    | `/api/v1/orders/customer/{customerId}` | Orders by customer |
| POST   | `/api/v1/orders` | Create new order |
| PATCH  | `/api/v1/orders/{id}/status` | Update order status / tracking |
| DELETE | `/api/v1/orders/{id}` | Delete order |
| GET    | `/api/v1/orders/reports/summary` | Report KPIs |
| GET    | `/api/v1/orders/reports/range?from=…&to=…` | Orders in date range |

### Products & Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/v1/products` | List products (`?search=name`) |
| POST   | `/api/v1/products` | Create product |
| PUT    | `/api/v1/products/{id}` | Update product |
| GET    | `/api/v1/customers` | List customers |
| POST   | `/api/v1/customers` | Create customer |

### WebSocket (real-time)

Connect to `ws://localhost:8080/ws` via STOMP + SockJS, then subscribe:

- `/topic/orders` — all order creates/updates
- `/topic/orders/{id}` — updates for a specific order

---

## Running Tests (Backend)

```bash
cd backend
./mvnw test
```

---

## Infrastructure Deployment (AWS)

### Terraform

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Fill in your values, especially db_password
terraform init
terraform plan
terraform apply
```

### Ansible (after Terraform)

```bash
cd infrastructure/ansible
# Edit inventory.ini with your server IPs
ansible-playbook -i inventory.ini playbook.yml --tags bootstrap
ansible-playbook -i inventory.ini playbook.yml --tags deploy
ansible-playbook -i inventory.ini playbook.yml --tags monitoring

# Rollback to a previous image
ansible-playbook -i inventory.ini playbook.yml --tags rollback -e "rollback_tag=v1.0.1"
```

---

## Metrics & Alerting

Prometheus scrapes metrics from all four services every 10–15 seconds. The Grafana dashboard at **http://localhost:3000** (auto-provisioned) shows:

- **Orders Created / Delivered / ETL Records** — stat panels
- **HTTP Request Rate by Endpoint** — time series
- **API Latency P50 / P95 / P99** — time series
- **ETL Pipeline Runs** (success vs. error)
- **JVM Heap vs. Non-Heap**
- **Service Up Status** — gauge panel for all 4 services

Alert rules in `monitoring/rules/order_alerts.yml` fire on: high error rate, ETL failure, service down, JVM heap > 85%, and API P95 > 2 s.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PASS` | `cloudorderx_dev` | PostgreSQL password |
| `JWT_SECRET` | dev key | JWT signing secret (min 256-bit) |
| `GRAFANA_PASS` | `admin` | Grafana admin password |
| `ETL_INTERVAL_MINUTES` | `15` | ETL schedule interval |
| `IMAGE_TAG` | `latest` | Docker image tag for deployments |

---

## License

MIT — free to use, modify, and distribute.
