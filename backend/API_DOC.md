# DashMap API Documentation

Vehicle routing backend API built with Django. All endpoints return JSON data.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
API uses token-based authentication. All endpoints (except login) require a valid authentication token.

### Login
**POST** `/api/auth/login/`

Request:
```json
{
  "username": "your_username", 
  "password": "your_password"
}
```

Response:
```json
{
  "token": "a1b2c3d4e5f6...",
  "user_id": 1,
  "username": "dispatcher",
  "email": "dispatcher@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "company_id": 1,
  "company_name": "ACME Logistics"
}
```

### Logout
**POST** `/api/auth/logout/`

Requires `Authorization: Token {token}` header. Invalidates the token.

Response:
```json
{
  "message": "Successfully logged out"
}
```

### Update User Profile
**PUT** `/api/auth/profile/`

Updates the current user's profile information. Requires authentication token.

Request:
```json
{
  "username": "new_username",
  "email": "new_email@example.com", 
  "first_name": "NewFirst",
  "last_name": "NewLast"
}
```

Response:
```json
{
  "id": 1,
  "username": "new_username",
  "email": "new_email@example.com",
  "first_name": "NewFirst", 
  "last_name": "NewLast",
  "company_id": 1,
  "company_name": "ACME Logistics"
}
```

### Update Company Settings
**PUT** `/api/auth/company/`

Updates the current user's company information. Requires authentication token.

Request:
```json
{
  "company_name": "New Company Name",
  "company_email": "contact@newcompany.com",
  "company_phone": "555-9999", 
  "company_address": "456 New Business Ave"
}
```

Response:
```json
{
  "id": 1,
  "name": "New Company Name", 
  "email": "contact@newcompany.com",
  "phone": "555-9999",
  "address": "456 New Business Ave",
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

### Using the Token
Include the token in the `Authorization` header for all API requests:

```
Authorization: Token a1b2c3d4e5f6...
```

## Response Format
All list endpoints return data in this format:
```json
{
  "results": [...]
}
```

## Companies

### List/Create Companies
- **GET** `/api/companies/` - List all companies
- **POST** `/api/companies/` - Create new company

### Company Details
- **GET** `/api/companies/{id}/` - Get company details
- **PUT** `/api/companies/{id}/` - Update company
- **DELETE** `/api/companies/{id}/` - Delete company

**Company Object:**
```json
{
  "id": 1,
  "name": "ACME Logistics",
  "address": "123 Business St",
  "phone": "555-0123", 
  "email": "contact@acme.com",
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

## Vehicles

### List/Create Vehicles
- **GET** `/api/vehicles/` - List all vehicles
- **GET** `/api/vehicles/?company={id}` - Filter by company
- **POST** `/api/vehicles/` - Create new vehicle

### Vehicle Details  
- **GET** `/api/vehicles/{id}/` - Get vehicle details
- **PUT** `/api/vehicles/{id}/` - Update vehicle
- **DELETE** `/api/vehicles/{id}/` - Delete vehicle

**Vehicle Object:**
```json
{
  "id": 1,
  "company": 1,
  "company_name": "ACME Logistics",
  "license_plate": "ABC123",
  "make": "Ford",
  "model": "Transit",
  "year": 2023,
  "capacity": "2.50",
  "driver_name": "John Doe",
  "driver_email": "john@example.com",
  "driver_phone": "555-1234",
  "is_active": true,
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

## Stops

### List/Create Stops
- **GET** `/api/stops/` - List all stops  
- **POST** `/api/stops/` - Create new stop

### Stop Details
- **GET** `/api/stops/{id}/` - Get stop details
- **PUT** `/api/stops/{id}/` - Update stop
- **DELETE** `/api/stops/{id}/` - Delete stop

**Stop Object:**
```json
{
  "id": 1,
  "name": "Loading Dock A",
  "address": "100 Warehouse St",
  "stop_type": "loading",
  "contact_name": "Dock Manager",
  "contact_phone": "555-0001",
  "notes": "Use rear entrance",
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

**Stop Types:** `"loading"` or `"unloading"`

### Get Orders (Generate Random Stops)
- **POST** `/api/stops/get-orders/` - Generate 3-8 random stops with faker data

**Response:**
```json
{
  "message": "Successfully created 5 new orders",
  "created_stops": [
    {
      "id": 10,
      "name": "Warehouse C",
      "address": "789 Industrial Blvd, Springfield, IL 62701",
      "stop_type": "loading",
      "contact_name": "Mike Johnson",
      "contact_phone": "555-0123",
      "notes": "Use loading bay 3",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

This endpoint simulates incoming orders by creating random stops with realistic data including:
- Warehouse/distribution centers for loading stops
- Customer sites/stores for unloading stops  
- Realistic addresses with city, state, zip
- Contact names and phone numbers
- Optional notes

## Trips

### List/Create Trips
- **GET** `/api/trips/` - List all trips
- **GET** `/api/trips/?vehicle={id}` - Filter by vehicle
- **GET** `/api/trips/?company={id}` - Filter by company  
- **POST** `/api/trips/` - Create new trip

### Trip Details
- **GET** `/api/trips/{id}/` - Get trip with stops
- **PUT** `/api/trips/{id}/` - Update trip
- **DELETE** `/api/trips/{id}/` - Delete trip

### Trip Actions
- **POST** `/api/trips/{id}/notify-driver/` - Send email to driver

**Trip Object (List View):**
```json
{
  "id": 1,
  "vehicle": 1,
  "vehicle_license_plate": "ABC123",
  "dispatcher": 1,
  "dispatcher_name": "John Dispatcher",
  "name": "Morning Route",
  "status": "draft",
  "planned_start_date": "2024-01-20",
  "planned_start_time": "08:00:00",
  "actual_start_datetime": null,
  "actual_end_datetime": null,
  "notes": "Standard morning delivery",
  "driver_notified": false,
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

**Trip Object (Detail View):**
Includes all above fields plus:
```json
{
  "trip_stops": [
    {
      "id": 1,
      "stop": {
        "id": 1,
        "name": "Loading Dock A",
        "address": "100 Warehouse St",
        "stop_type": "loading",
        "contact_name": "Dock Manager",
        "contact_phone": "555-0001",
        "notes": "Use rear entrance"
      },
      "order": 1,
      "planned_arrival_time": "09:00:00",
      "actual_arrival_datetime": null,
      "actual_departure_datetime": null,
      "notes": "First pickup",
      "is_completed": false
    }
  ]
}
```

**Trip Status Options:**
- `"draft"` - Being planned
- `"planned"` - Ready to execute
- `"in_progress"` - Currently running
- `"completed"` - Finished
- `"cancelled"` - Cancelled

## Trip Stops

### List/Create Trip Stops
- **GET** `/api/trip-stops/` - List all trip stops
- **GET** `/api/trip-stops/?trip={id}` - Filter by trip
- **POST** `/api/trip-stops/` - Create new trip stop

### Trip Stop Details
- **GET** `/api/trip-stops/{id}/` - Get trip stop details
- **PUT** `/api/trip-stops/{id}/` - Update trip stop  
- **DELETE** `/api/trip-stops/{id}/` - Delete trip stop

**Trip Stop Object:**
```json
{
  "id": 1,
  "trip": 1,
  "stop": {
    "id": 1,
    "name": "Loading Dock A",
    "address": "100 Warehouse St", 
    "stop_type": "loading"
  },
  "order": 1,
  "planned_arrival_time": "09:00:00",
  "actual_arrival_datetime": null,
  "actual_departure_datetime": null,
  "notes": "First pickup",
  "is_completed": false
}
```

## Error Responses

**400 Bad Request:**
```json
{
  "error": "Invalid data"
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication required"
}
```
```json
{
  "error": "Invalid token"
}
```

**404 Not Found:**  
```json
{
  "error": "Company not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Error message details"
}
```

## Date/Time Formats

- **Dates:** `"2024-01-20"` (ISO 8601)
- **Times:** `"08:00:00"` (HH:MM:SS)  
- **DateTimes:** `"2024-01-15T08:00:00Z"` (ISO 8601 with timezone)

## Example Workflow

1. **Login:** POST `/api/auth/login/` (get token)
2. **Create Company:** POST `/api/companies/` (with token)
3. **Create Vehicle:** POST `/api/vehicles/` (with company ID and token)
4. **Create Stops:** POST `/api/stops/` (for loading/unloading locations)
5. **Create Trip:** POST `/api/trips/` (with vehicle and dispatcher)
6. **Add Stops to Trip:** POST `/api/trip-stops/` (with trip, stop, and order)
7. **Notify Driver:** POST `/api/trips/{id}/notify-driver/`
8. **Update Trip Status:** PUT `/api/trips/{id}/` (change status to "planned")
9. **Logout:** POST `/api/auth/logout/` (invalidate token)

## Admin Interface

Django admin available at: `http://localhost:8000/admin/`