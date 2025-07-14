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
*Endpoints will be added as implemented*

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
*Updated automatically as endpoints are implemented*