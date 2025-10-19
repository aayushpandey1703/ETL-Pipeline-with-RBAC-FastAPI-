# FastAPI ETL Pipeline with RBAC

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green)](https://fastapi.tiangolo.com/)  
[![License](https://img.shields.io/badge/license-MIT-yellow)](LICENSE)

---

## Table of Contents

- [Project Overview](#project-overview)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Architecture](#architecture)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Usage](#usage)  
- [API Endpoints](#api-endpoints)  
- [RBAC Implementation](#rbac-implementation)  
- [ETL Workflow](#etl-workflow)  
- [Contributing](#contributing)  
- [License](#license)

---

## Project Overview

This project is a **FastAPI-based ETL pipeline** designed to extract, transform, and load data from various sources into a database, with **Role-Based Access Control (RBAC)** for secure user management.  

It is suitable for building scalable, production-ready pipelines with secure APIs and structured workflows.

---

## Features

- FastAPI RESTful API for ETL operations  
- Async SQLAlchemy ORM with PostgreSQL / SQLite support  
- Role-Based Access Control (RBAC) for `admin`, `user`, or custom roles  
- JWT-based authentication  
- CRUD operations for Users and Roles  
- Data validation using Pydantic schemas  
- Modular ETL tasks (Extract → Transform → Load)  
- Logging for ETL execution and errors  
- Swagger UI / OpenAPI documentation  

---

## Tech Stack

- **Backend:** Python 3.11, FastAPI  
- **Database:** PostgreSQL / SQLite (SQLAlchemy Async ORM)  
- **Authentication:** JWT, OAuth2  
- **ETL Tools:** Pandas, NumPy  
- **Task Scheduling:** Celery / Async Background Tasks  
- **DevOps:** Docker, Docker Compose (optional)  

---

## Architecture

Client (Swagger / React) <---> FastAPI API
|
v
RBAC Middleware
|
v
Async SQLAlchemy ORM
|
v
ETL Pipeline: Extract -> Transform -> Load
|
v
Database



---

## Installation

### Clone the repository

```bash
git clone https://github.com/<username>/fastapi-etl-rbac.git
cd fastapi-etl-rbac

python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows

### Install dependencies
pip install -r requirements.txt

## Configuration

### Create a .env file at the project root:

DATABASE_URL=sqlite+aiosqlite:///./db.sqlite3
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

### For PostgreSQL:

DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

## Run the application
uvicorn main:app --reload

## API Endpoints
Method	Endpoint	Description	Roles
GET	/user/me	Get current user info	user, admin
GET	/user/get_users	Get all users	admin
PUT	/user/update_user/{id}	Update user info & roles	admin
POST	/etl/run	Run ETL pipeline	admin
GET	/etl/status	Check ETL task status	admin

## RBAC Implementation

### Each user has one or multiple roles.
### Roles define permissions for API endpoints.
### Middleware dependency required_role_check(roles: List[str]) ensures endpoint access based on role.