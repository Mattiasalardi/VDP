# VDP API Reference

## Overview
Quick reference for all FastAPI endpoints, request/response schemas, and authentication requirements.

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: TBD

## Authentication
All protected endpoints require JWT token in header:
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Authentication

#### POST /api/v1/auth/login
Login endpoint for organizations.
- **Request**: Form data with `username` (email) and `password`
- **Response**: JWT token, token type, organization ID and name
- **Status**: 200 (success), 401 (unauthorized)

#### POST /api/v1/auth/logout
Logout endpoint (stateless - token invalidation handled client-side).
- **Requires**: Valid JWT token
- **Response**: Success message
- **Status**: 200 (success), 401 (unauthorized)

#### GET /api/v1/auth/me
Get current authenticated organization details.
- **Requires**: Valid JWT token
- **Response**: Organization ID, name, email, creation date
- **Status**: 200 (success), 401 (unauthorized)

### Health Check

#### GET /health
Health check endpoint with database connectivity test.
- **Response**: Status and database connection status
- **Status**: 200 (healthy), 500 (unhealthy)

### Organizations
*Endpoints will be added as implemented*

### Programs
*Endpoints will be added as implemented*

### Questionnaires
*Endpoints will be added as implemented*

### Applications
*Endpoints will be added as implemented*

### AI Processing
*Endpoints will be added as implemented*

### Reports
*Endpoints will be added as implemented*

## Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {...}
}
```

### Error Response
```json
{
  "status": "error",
  "message": "Error description",
  "code": "ERROR_CODE"
}
```

## Rate Limiting
*Will be documented when implemented*

---
*Last Updated: 2025-07-16 - Authentication endpoints implemented*