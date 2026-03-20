# Project Guidelines

## 1. General Architecture & Configuration

### Configuration Management

- Use a unified configuration system with defaults and environment‑variable overrides
- All configuration must be runtime‑adjustable without code changes
- Provide a local `.env` mechanism for development

### Feature Flags

- Implement feature toggling using a centralized feature‑flag framework (e.g., LaunchDarkly, Azure App Configuration feature flags, or custom DB‑based implementation)
- All new features must be disabled by default unless explicitly activated

### 12‑Factor Principles

- Follow 12‑factor app standards for configuration, build isolation, and environment parity

## 2. Tech Stack & Infrastructure

### Infrastructure

#### Terraform

- Infrastructure must be fully managed via Terraform
- Code should reside in the repository `genai-platform-terraform`
- Module structure should follow our standard separation: networking, identity, compute, database, observability

#### Compute

- For each new component, create a separate Azure App Service
- Ensure consistent naming, tagging, and resource group conventions across environments

#### Docker

- Use hardened base images from `dhi.io` whenever available
- Container images must follow:
  - Multi‑stage builds
  - Non‑root execution
  - Vulnerability scanning pipeline integration
- Do not use Docker Compose for deployment (not supported on App Service); compose may be allowed locally but must not be part of deployment artifacts

## 3. Application Architecture

### Frontend

- Built with React
- Must support Azure AD authentication and token forwarding
- Hosted together with backend on the same App Service (shared environment)

### Backend

- Python + FastAPI
- Expose OpenAPI documentation
- Enforce structured logging (JSON format)
- Support health endpoints (`/healthz`, `/readyz`)
- Follow layered architecture (routers → services → repositories)

### Frontend + Backend Deployment

- Both must be served from the same App Service (backend as default app, frontend served as static files or via reverse proxy)
- Ensure correct routing rules (e.g., `/api/*` forwarded to FastAPI)

## 4. Database

### PostgreSQL

- Hosted in Azure Database for PostgreSQL
- Require:
  - Strict SSL enforcement
  - Managed Identity access when possible (preview/using Entra integration)

### Local Development

- Provide a local PostgreSQL container or local instance runner (e.g., DevContainer or simple `docker run` command)

### Database Migrations

- Use Alembic for:
  - Schema definition
  - Automated migrations per environment
  - Migration versioning discipline (one migration per feature unless justified)

## 5. Authentication

### Service-to-Service (Backend Components)

- Always use Managed Identity for internal communication:
  - DB access
  - Storage
  - Key Vault
  - API calls to internal services
- No secrets stored directly in the code or environment variables

### User Authentication

- Assume Azure AD Authentication is enabled on the App Service
- Retrieve user information from:
  - Injected ID token
  - App Service authentication headers (e.g., `X-MS-CLIENT-PRINCIPAL`)

### Local Development

- Provide a mechanism to:
  - Load a dev token from configuration, or
  - Bypass authentication with a development flag (never enabled in production)

## 6. Authorization

- Follow least‑privilege principle for all components and identities
- Define a minimum permissions matrix for:
  - App Services
  - Database users/roles
  - Storage accounts
  - Other dependent services
- Introduce an administrative role with additional privileges for solution governance
- Non-admin users should only access allowed entities based on explicit rules

## 7. Operational Requirements (Standard Across Projects)

### Logging & Monitoring

- Unified logging format (JSON)
- Integrate with Azure Application Insights:
  - Distributed tracing
  - Request/response metrics
  - Exception tracking

### Alerting

- Standard alerts:
  - CPU
  - Memory
  - Error rate
  - Failed requests
  - DB connection saturation

### Security Baseline

- OWASP standards for frontend and backend
- Regular container vulnerability scans
- Dependency scanning in CI

### CI/CD

- GitHub Actions or Azure Pipelines
- Steps:
  1. Lint & format
  2. Unit tests
  3. Build container
  4. Security scan
  5. Deployment via Terraform + App Service slot swap

## 8. Non-Functional Requirements (Standard)

- **High availability**: App Service Standard or Premium tier
- **Scalability**: enable autoscaling rules
- **Performance**: backend must respond <300ms for standard lightweight API calls
- **Compliance**: logs and data must follow our standard retention and GDPR guidelines