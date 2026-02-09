# CarSales API – P2P Car Dealership Backend

A full-featured **peer-to-peer car marketplace API** built to demonstrate production-grade backend engineering skills.

This personal project implements a modern, scalable REST + GraphQL backend for a used-car buying/selling platform — similar in spirit to a simplified Craigslist Autos or Facebook Marketplace for vehicles.

### Tech Stack & Highlights

- **Language & Framework**  
  Python 3 • [FastAPI](https://fastapi.tiangolo.com) (high-performance async API framework)

- **Database & ORM**  
  PostgreSQL + SQLAlchemy 2.x (with async support)

- **API Styles**  
  Full REST endpoints + GraphQL support (via Strawberry)

- **Authentication**  
  OAuth2 + JWT (industry-standard password & token flows)

- **Other production touches**  
  - Comprehensive test suite (pytest + high coverage)  
  - Redis caching layer  
  - Dependency injection & clean architecture patterns  
  - PEP 8 / modern Python typing & linting compliance  
  - Structured logging & error handling

- **Development & Deployment**  
  Fully containerized with Docker + docker-compose  
  Services:  
  - FastAPI application  
  - PostgreSQL  
  - Redis
  - MinIO (for a local file storage solution compatible with Amazon's S3 API)
  - ClawAV

### Project Status

This is actively used as a portfolio piece to showcase clean, maintainable, and realistic backend code.

**Completed features:**
- [x] User registration, login & token-based authentication (OAuth2/JWT)
- [x] Role-based access (Buyer, Seller, Admin)
- [x] User profiles & personal information management

**In progress / Planned features:**
- [ ] Seller & buyer ratings + review system
- [ ] Create, edit, delete car listings (with photos, specs, price, location…)
- [ ] Advanced car search with multiple filters (make/model/year/price/mileage/location/…)
- [ ] Private buyer ↔ seller messaging/chat
- [ ] (Optional stretch) Basic payment/listing fee checkout flow

### Why this project?

I built CarSales API to go beyond simple CRUD demos and practice real-world backend concerns:

- Clean separation of concerns & modular structure
- Secure authentication & authorization
- Performance optimizations (caching, async I/O)
- Testing strategy for business logic + API endpoints
- Containerized multi-service environment
- Supporting both REST and GraphQL consumers
- Using AI-assisted development productively (a growing industry reality)

### Quick Start (Developers)

```bash
# Clone & start everything with one command
git clone https://github.com/yourusername/carsales-api.git
cd carsales-api
docker compose up -d

# API will be available at http://localhost:8000
# Interactive docs: http://localhost:8000/docs