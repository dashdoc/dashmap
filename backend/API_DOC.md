# DashMap API Documentation

Vehicle routing backend API built with Django. All endpoints return JSON data.

## Base URL
```
http://localhost:8000/api/
```

## Root Endpoint
**GET** `/`

Basic status endpoint that returns API information.

Response:
```json
{
  "status": "ok",
  "message": "Welcome to Dashmap!"
}
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

### User Profile
**GET** `/api/auth/profile/` - Get current user profile information
**PUT** `/api/auth/profile/` - Update user profile information

Both endpoints require authentication token.

#### Get User Profile
**GET** `/api/auth/profile/`

Response:
```json
{
  "id": 1,
  "username": "current_user",
  "email": "user@example.com",
  "first_name": "Current",
  "last_name": "User",
  "company_id": 1,
  "company_name": "ACME Logistics"
}
```

#### Update User Profile
**PUT** `/api/auth/profile/`

Updates the current user's profile information.

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
- **GET** `/api/vehicles/` - List all non-deleted vehicles
- **GET** `/api/vehicles/?company={id}` - Filter by company
- **POST** `/api/vehicles/` - Create new vehicle

### Vehicle Details
- **GET** `/api/vehicles/{id}/` - Get vehicle details
- **PUT** `/api/vehicles/{id}/` - Update vehicle
- **DELETE** `/api/vehicles/{id}/` - Soft delete vehicle (marks as deleted, doesn't remove from database)

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

## Orders

### List/Create Orders
- **GET** `/api/orders/` - List all orders
- **GET** `/api/orders/?available_for_trip=true` - List orders available for trip assignment (pending status, not already assigned to trips)
- **POST** `/api/orders/` - Create new order

### Order Details
- **GET** `/api/orders/{id}/` - Get order details
- **PUT** `/api/orders/{id}/` - Update order
- **DELETE** `/api/orders/{id}/` - Delete order

### Generate Fake Orders
- **POST** `/api/orders/generate-fake/` - Generate random test orders

**Order Object:**
```json
{
  "id": 1,
  "order_number": "ORD-2024-0001",
  "customer_name": "John Smith",
  "customer_company": "ACME Manufacturing",
  "customer_email": "john.smith@acme.com",
  "customer_phone": "+33-1-42-00-1234",
  "pickup_stop": {
    "id": 1,
    "name": "Rungis International Market",
    "address": "1 Rue de la Tour, 94150 Rungis, France",
    "latitude": "48.759000",
    "longitude": "2.352000",
    "stop_type": "pickup",
    "contact_name": "Market Manager",
    "contact_phone": "555-0001",
    "notes": "Use loading dock B"
  },
  "delivery_stop": {
    "id": 15,
    "name": "Carrefour Distribution Paris",
    "address": "93 Avenue de Paris, 94300 Vincennes, France",
    "latitude": "48.847000",
    "longitude": "2.428000",
    "stop_type": "delivery",
    "contact_name": "Receiving Manager",
    "contact_phone": "555-0015",
    "notes": "Ring bell at entrance"
  },
  "goods_description": "Fresh produce and dairy products",
  "goods_weight": "2500.00",
  "goods_volume": "15.00",
  "goods_type": "refrigerated",
  "special_instructions": "Keep temperature at 2-4°C throughout transport",
  "status": "pending",
  "requested_pickup_date": "2024-01-20",
  "requested_delivery_date": "2024-01-21",
  "created_at": "2024-01-15T08:00:00Z",
  "updated_at": "2024-01-15T08:00:00Z"
}
```

**Order Status Options:**
- `"pending"` - Order created, awaiting assignment
- `"assigned"` - Order assigned to a trip
- `"in_transit"` - Order currently being transported
- `"delivered"` - Order completed successfully
- `"cancelled"` - Order cancelled

**Goods Types:**
- `"standard"` - Standard cargo
- `"fragile"` - Fragile items requiring careful handling
- `"hazmat"` - Hazardous materials requiring special permits
- `"refrigerated"` - Temperature-controlled goods
- `"oversized"` - Oversized cargo requiring special equipment

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
- **POST** `/api/trips/{id}/add-order/` - Add complete order (pickup + delivery) to trip

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
  "trip_stops": [
    {
      "id": 1,
      "stop": {
        "id": 1,
        "name": "Loading Dock A",
        "address": "100 Warehouse St",
        "latitude": "41.878113",
        "longitude": "-87.629799",
        "stop_type": "pickup",
        "contact_name": "Dock Manager",
        "contact_phone": "555-0001",
        "notes": "Use rear entrance"
      },
      "sequence": 1,
      "planned_arrival_time": "09:00:00",
      "actual_arrival_datetime": null,
      "actual_departure_datetime": null,
      "notes": "First pickup",
      "is_completed": false,
      "linked_order": {
        "id": 1,
        "order_number": "ORD-2024-0001",
        "customer_name": "John Smith"
      }
    }
  ],
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
        "latitude": "41.878113",
        "longitude": "-87.629799",
        "stop_type": "pickup",
        "contact_name": "Dock Manager",
        "contact_phone": "555-0001",
        "notes": "Use rear entrance"
      },
      "sequence": 1,
      "planned_arrival_time": "09:00:00",
      "actual_arrival_datetime": null,
      "actual_departure_datetime": null,
      "notes": "First pickup",
      "is_completed": false,
      "linked_order": {
        "id": 1,
        "order_number": "ORD-2024-0001",
        "customer_name": "John Smith"
      }
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

### List Trip Stops
- **GET** `/api/trip-stops/` - List all trip stops
- **GET** `/api/trip-stops/?trip={id}` - Filter by trip

### Trip Stop Details
- **GET** `/api/trip-stops/{id}/` - Get trip stop details
- **PUT** `/api/trip-stops/{id}/` - Update trip stop
- **DELETE** `/api/trip-stops/{id}/` - Delete trip stop (automatically reorders remaining stops)

### Trip Stop Reordering
- **POST** `/api/trips/{trip_id}/reorder-stops/` - Bulk reorder trip stops

**Trip Stop Object:**
```json
{
  "id": 1,
  "trip": 1,
  "stop": {
    "id": 1,
    "name": "Loading Dock A",
    "address": "100 Warehouse St",
    "latitude": "41.878113",
    "longitude": "-87.629799",
    "stop_type": "pickup"
  },
  "sequence": 1,
  "planned_arrival_time": "09:00:00",
  "actual_arrival_datetime": null,
  "actual_departure_datetime": null,
  "notes": "First pickup",
  "is_completed": false,
  "linked_order": {
    "id": 1,
    "order_number": "ORD-2024-0001",
    "customer_name": "John Smith"
  }
}
```

**Linked Order Field:**
The `linked_order` field contains the order that uses this stop as either a pickup or delivery location. It includes:
- `id`: Order ID for API references
- `order_number`: Human-readable order number (e.g., "ORD-2024-0001")
- `customer_name`: Name of the customer who placed the order

The field will be `null` if no order is associated with the stop.

#### Trip Stop Sequence Management

**Creating Trip Stops with Sequence Conflicts:**
When creating a trip stop with a sequence that already exists, the system automatically shifts existing stops to higher sequence numbers to make room for the new stop.

Example: If a trip has stops with sequences [1, 2, 3] and you create a new stop with sequence=2, the result will be:
- New stop: sequence=2
- Existing stops: sequences [1, 3, 4] (original sequence=2 and sequence=3 are shifted up)

#### Order Completeness Validation

**Business Rule: Complete Order Journeys**
Trips must contain complete order journeys (both pickup and delivery stops). This ensures you can always deliver what you picked up.

**Validation Rules:**
- When adding a stop to a trip that belongs to an order, the corresponding pickup/delivery stop must also be in the trip
- Adding a pickup stop without its delivery stop will result in a 400 error
- Adding a delivery stop without its pickup stop will result in a 400 error
- Stops without orders (standalone stops) are allowed without restrictions
- Orders must have both pickup and delivery stops defined to be usable in trips

**Error Response Example:**
```json
{
  "error": "Cannot add delivery stop for order ORD-2024-0001 without also including its pickup stop. Trips must contain complete order journeys (both pickup and delivery)."
}
```

**Recommended Workflow:**
1. Ensure orders have both pickup and delivery stops before trip assignment
2. Use **POST** `/api/trips/{id}/add-order/` to add complete orders to trips
3. Individual trip stops can only be viewed/updated via GET/PUT operations

**Adding Complete Orders to Trips:**
**POST** `/api/trips/{id}/add-order/`

Request:
```json
{
  "sequence": 1,
  "pickup_time": "09:00:00",
  "delivery_time": "14:00:00",
  "notes": "Handle with care"
}
```

Response:
```json
{
  "message": "Successfully added order ORD-2024-0001 to trip",
  "pickup_trip_stop": {
    "id": 15,
    "sequence": 3,
    "planned_arrival_time": "09:00:00",
    "stop": {
      "id": 10,
      "name": "Warehouse A",
      "stop_type": "pickup"
    }
  },
  "delivery_trip_stop": {
    "id": 16,
    "sequence": 4,
    "planned_arrival_time": "14:00:00",
    "stop": {
      "id": 11,
      "name": "Customer Site B",
      "stop_type": "delivery"
    }
  }
}
```

**Deleting Trip Stops:**
When a trip stop is deleted, remaining stops with higher sequence numbers are automatically shifted down to close gaps and maintain consecutive sequencing.

Example: If a trip has stops with sequences [1, 2, 3] and you delete the stop with sequence=2, the result will be:
- Remaining stops: sequences [1, 2] (original sequence=3 is shifted down to sequence=2)

**Bulk Reordering:**
Use the reorder endpoint to update multiple trip stop sequences in a single transaction.

**POST** `/api/trips/{trip_id}/reorder-stops/`

Request:
```json
{
  "orders": [
    {"id": 10, "sequence": 1},
    {"id": 11, "sequence": 2},
    {"id": 12, "sequence": 3}
  ]
}
```

Response:
```json
{
  "results": [
    {
      "id": 10,
      "trip": 5,
      "stop": {...},
      "sequence": 1,
      "planned_arrival_time": "09:00:00",
      "actual_arrival_datetime": null,
      "actual_departure_datetime": null,
      "notes": "",
      "is_completed": false
    }
  ]
}
```

All trip stop IDs in the request must belong to the specified trip. The response returns all trip stops for the trip in their new sequence.

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
4. **Create Orders:** POST `/api/orders/` (customers with pickup/delivery locations)
5. **Create Trip:** POST `/api/trips/` (with vehicle and dispatcher)
6. **Add Stops to Trip:** POST `/api/trip-stops/` (with trip, stop, and order)
7. **Notify Driver:** POST `/api/trips/{id}/notify-driver/`
8. **Update Trip Status:** PUT `/api/trips/{id}/` (change status to "planned")
9. **Update Order Status:** PUT `/api/orders/{id}/` (track order progress)
10. **Logout:** POST `/api/auth/logout/` (invalidate token)

## Positions (Telematics Data)

Vehicle position tracking for telematics integration.

### List/Create Positions
- **GET** `/api/positions/` - List all positions (supports `?vehicle={id}` filter)
- **POST** `/api/positions/` - Create new position record

### Latest Vehicle Positions
- **GET** `/api/positions/latest/` - Get the latest position for each vehicle

### Generate Fake Positions
- **POST** `/api/positions/generate-fake/` - Generate fake telematics data for testing

**Position Object:**
```json
{
  "id": 1,
  "vehicle_id": 1,
  "vehicle_license_plate": "ABC-123",
  "vehicle_make_model": "Ford Transit",
  "latitude": "40.7589123",
  "longitude": "-73.9851456",
  "speed": "65.50",
  "heading": "180.00",
  "altitude": "150.25",
  "timestamp": "2024-01-15T14:30:00Z",
  "odometer": "25847.50",
  "fuel_level": "75.30",
  "engine_status": "on",
  "created_at": "2024-01-15T14:30:05Z"
}
```

**Latest Positions Response:**
```json
{
  "results": [
    {
      "id": 1,
      "vehicle_id": 1,
      "vehicle_license_plate": "ABC-123",
      "vehicle_make_model": "Ford Transit",
      "latitude": "40.7589123",
      "longitude": "-73.9851456",
      "speed": "65.50",
      "heading": "180.00",
      "altitude": "150.25",
      "timestamp": "2024-01-15T14:30:00Z",
      "odometer": "25847.50",
      "fuel_level": "75.30",
      "engine_status": "on",
      "created_at": "2024-01-15T14:30:05Z"
    }
  ]
}
```

**Create Position Request:**
```json
{
  "vehicle_id": 1,
  "latitude": "40.7589123",
  "longitude": "-73.9851456",
  "speed": "65.50",
  "heading": "180.00",
  "altitude": "150.25",
  "timestamp": "2024-01-15T14:30:00Z",
  "odometer": "25847.50",
  "fuel_level": "75.30",
  "engine_status": "on"
}
```

**Generate Fake Positions Request:**
```json
{
  "vehicle_id": 1,
  "count": 10,
  "base_latitude": 40.7589,
  "base_longitude": -73.9851
}
```

**Field Details:**
- `latitude`/`longitude`: Decimal degrees (required)
- `speed`: Speed in km/h (required)
- `heading`: Heading in degrees 0-360 (required)
- `altitude`: Altitude in meters (optional)
- `timestamp`: When position was recorded (optional, defaults to current time)
- `odometer`: Vehicle odometer reading in km (optional)
- `fuel_level`: Fuel level percentage 0-100 (optional)
- `engine_status`: One of `"on"`, `"off"`, `"idle"` (defaults to `"off"`)

## Admin Interface

Django admin available at: `http://localhost:8000/admin/`
