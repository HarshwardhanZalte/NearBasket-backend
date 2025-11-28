# NearBasket API Documentation

## Base URL
```
https://nearbasket-backend.onrender.com/api
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🔐 Authentication & User Management

### 1. Register User
**POST** `/users/register/`

Register a new user. Shopkeepers must provide shop information.

#### Request Body - Customer
```json
{
  "mobile_number": "9876543210",
  "name": "Priya Sharma",
  "email": "priya@example.com",
  "address": "123 Main St, Mumbai",
  "profile_image_url": "https://example.com/image.jpg",
  "role": "CUSTOMER"
}
```

#### Request Body - Shopkeeper (Shop Info Required)
```json
{
  "mobile_number": "9123456789",
  "name": "Suresh Gupta",
  "email": "suresh@example.com",
  "address": "10 Commercial St, Mumbai",
  "profile_image_url": "https://example.com/image.jpg",
  "role": "SHOPKEEPER",
  "shop_info": {
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg"
  }
}
```

#### Required Fields
- `mobile_number` (string, 10 digits)
- `name` (string, min 2 characters)
- `role` ("CUSTOMER" or "SHOPKEEPER")
- `shop_info` (object, required only for SHOPKEEPER)

#### Response - Customer
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "mobile_number": "9876543210",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "address": "123 Main St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": null
  }
}
```

#### Response - Shopkeeper
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "mobile_number": "9123456789",
    "name": "Suresh Gupta",
    "email": "suresh@example.com",
    "address": "10 Commercial St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "SHOPKEEPER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": {
      "id": 1,
      "name": "Suresh General Store",
      "address": "10 Commercial Street, Mumbai",
      "description": "Your neighborhood grocery store",
      "shop_logo_url": "https://example.com/logo.jpg",
      "shop_id": "SGS12345",
      "created_at": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### Error Responses
- **400** - Validation errors or missing shop_info for shopkeeper
- **400** - Duplicate mobile number

---

### 2. Send OTP
**POST** `/users/send-otp/`

Send OTP to registered mobile number for login.

#### Request Body
```json
{
  "mobile_number": "9876543210"
}
```

#### Response
```json
{
  "message": "OTP sent successfully",
  "otp": "123456"
}
```

**Note:** OTP included in response for development only.

#### Error Responses
- **404** - User with mobile number not found
- **400** - Invalid mobile number format

---

### 3. Verify OTP & Login
**POST** `/users/verify-otp/`

Verify OTP and receive JWT tokens.

#### Request Body
```json
{
  "mobile_number": "9876543210",
  "otp_code": "123456"
}
```

#### Response
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "mobile_number": "9876543210",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "address": "123 Main St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": null
  }
}
```

#### Error Responses
- **400** - Invalid OTP or expired (10-minute validity)

---

### 4. Get User Profile
**GET** `/users/me/`

**Requires Authentication**

Get current user's profile. Includes shop information for shopkeepers.

#### Response - Customer
```json
{
  "id": 1,
  "mobile_number": "9876543210",
  "name": "Priya Sharma",
  "email": "priya@example.com",
  "address": "123 Main St, Mumbai",
  "profile_image_url": "https://example.com/image.jpg",
  "role": "CUSTOMER",
  "created_at": "2024-01-15T10:30:00Z",
  "shop": null
}
```

#### Response - Shopkeeper
```json
{
  "id": 2,
  "mobile_number": "9123456789",
  "name": "Suresh Gupta",
  "email": "suresh@example.com",
  "address": "10 Commercial St, Mumbai",
  "profile_image_url": "https://example.com/image.jpg",
  "role": "SHOPKEEPER",
  "created_at": "2024-01-15T10:30:00Z",
  "shop": {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 5. Update User Profile
**PUT** `/users/me/update/`

**Requires Authentication**

Update current user's profile. Cannot change role or shop information.

#### Request Body
```json
{
  "name": "Priya Sharma Updated",
  "email": "priya.new@example.com",
  "address": "456 New St, Mumbai",
  "profile_image_url": "https://example.com/newimage.jpg"
}
```

#### Response
```json
{
  "id": 1,
  "mobile_number": "9876543210",
  "name": "Priya Sharma Updated",
  "email": "priya.new@example.com",
  "address": "456 New St, Mumbai",
  "profile_image_url": "https://example.com/newimage.jpg",
  "role": "CUSTOMER",
  "created_at": "2024-01-15T10:30:00Z",
  "shop": null
}
```

---

## 🪧 Shop Management

### 6. Get My Shop
**GET** `/shops/my-shop/`

**Requires Authentication**

- **Shopkeeper:** Returns their single shop
- **Customer:** Returns list of shops they've joined

#### Response - Shopkeeper
```json
{
  "id": 1,
  "name": "Suresh General Store",
  "address": "10 Commercial Street, Mumbai",
  "description": "Your neighborhood grocery store",
  "shop_logo_url": "https://example.com/logo.jpg",
  "shop_id": "SGS12345",
  "created_at": "2024-01-15T10:30:00Z",
  "owner_name": "Suresh Gupta"
}
```

#### Response - Customer
```json
[
  {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_name": "Suresh Gupta"
  }
]
```

#### Error Responses
- **404** - No shop found for shopkeeper
- **400** - Invalid user role

---

### 7. Update My Shop
**PUT** `/shops/my-shop/update/`

**Requires Authentication - Shopkeeper Only**

Update shopkeeper's shop information.

#### Request Body
```json
{
  "name": "Suresh Super Store",
  "address": "10 Commercial Street, Mumbai, Maharashtra",
  "description": "Premium grocery store with fresh products",
  "shop_logo_url": "https://example.com/newlogo.jpg"
}
```

#### Response
```json
{
  "id": 1,
  "name": "Suresh Super Store",
  "address": "10 Commercial Street, Mumbai, Maharashtra",
  "description": "Premium grocery store with fresh products",
  "shop_logo_url": "https://example.com/newlogo.jpg",
  "shop_id": "SGS12345",
  "created_at": "2024-01-15T10:30:00Z",
  "owner_name": "Suresh Gupta"
}
```

#### Error Responses
- **403** - Only shopkeepers can update shop information
- **404** - No shop found for shopkeeper

---

### 8. Get Shop Details
**GET** `/shops/details/{shop_id}/`

**Public Access**

Get shop details by shop_id. Used by customers to view shop before joining.

#### Response
```json
{
  "id": 1,
  "name": "Suresh General Store",
  "address": "10 Commercial Street, Mumbai",
  "description": "Your neighborhood grocery store",
  "shop_logo_url": "https://example.com/logo.jpg",
  "shop_id": "SGS12345",
  "created_at": "2024-01-15T10:30:00Z",
  "owner_name": "Suresh Gupta"
}
```

#### Error Responses
- **404** - Shop not found

---

### 9. Join Shop
**POST** `/shops/join/{shop_id}/`

**Requires Authentication - Customer Only**

Customer joins a shop using the shop's unique shop_id.

#### Response
```json
{
  "message": "Successfully joined shop",
  "shop": {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_name": "Suresh Gupta"
  }
}
```

#### Error Responses
- **403** - Only customers can join shops
- **400** - Already a customer of this shop
- **404** - Shop not found

---

### 10. Add Customer to Shop
**POST** `/shops/add-customer/`

**Requires Authentication - Shopkeeper Only**

Shopkeeper adds a customer to their shop by mobile number.

#### Request Body
```json
{
  "mobile_number": "9876543210"
}
```

#### Response
```json
{
  "message": "Customer added successfully",
  "customer": {
    "id": 1,
    "mobile_number": "9876543210",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "address": "123 Main St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": null
  }
}
```

#### Error Responses
- **403** - Only shopkeepers can add customers
- **404** - No shop found for shopkeeper or customer not found
- **400** - Customer already linked or invalid mobile number

---

### 11. List Shop Customers
**GET** `/shops/customers/`

**Requires Authentication - Shopkeeper Only**

Get list of all customers for shopkeeper's shop.

#### Response
```json
[
  {
    "id": 1,
    "customer": {
      "id": 1,
      "mobile_number": "9876543210",
      "name": "Priya Sharma",
      "email": "priya@example.com",
      "address": "123 Main St, Mumbai",
      "profile_image_url": "https://example.com/image.jpg",
      "role": "CUSTOMER",
      "created_at": "2024-01-15T10:30:00Z",
      "shop": null
    },
    "shop_name": "Suresh General Store",
    "joined_at": "2024-01-15T12:00:00Z"
  }
]
```

#### Error Responses
- **403** - Only shopkeepers can view shop customers
- **404** - No shop found for shopkeeper

---

### 12. Remove Customer from Shop
**DELETE** `/shops/customers/{user_id}/remove/`

**Requires Authentication - Shopkeeper Only**

Remove a customer from the shopkeeper's shop.

#### Response
```json
{
  "message": "Customer removed successfully"
}
```

#### Error Responses
- **403** - Only shopkeepers can remove customers
- **404** - No shop found or customer not found in shop

---

### 13. My Joined Shops
**GET** `/shops/my-joined-shops/`

**Requires Authentication - Customer Only**

Get list of shops the customer has joined.

#### Response
```json
[
  {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_name": "Suresh Gupta"
  }
]
```

#### Error Responses
- **403** - Only customers can view joined shops

---

## 📦 Product Management

### 14. List/Create Products
**GET** `/products/shops/{shop_id}/products/` - List shop products  
**POST** `/products/shops/{shop_id}/products/` - Create product (shopkeeper only)

**Requires Authentication**

#### GET Response
```json
[
  {
    "id": 1,
    "name": "Fresh Tomatoes",
    "price": "50.00",
    "stock": 30,
    "product_image_url": "https://example.com/products/tomatoes.jpg",
    "description": "Fresh red tomatoes from local farms",
    "created_at": "2024-01-15T10:30:00Z",
    "shop_name": "Suresh General Store"
  }
]
```

#### POST Request Body (Shopkeeper only)
```json
{
  "name": "Fresh Apples",
  "price": 80.00,
  "stock": 25,
  "product_image_url": "https://example.com/products/apples.jpg",
  "description": "Crispy red apples from Kashmir"
}
```

#### POST Response
```json
{
  "id": 2,
  "name": "Fresh Apples",
  "price": "80.00",
  "stock": 25,
  "product_image_url": "https://example.com/products/apples.jpg",
  "description": "Crispy red apples from Kashmir",
  "created_at": "2024-01-15T10:30:00Z",
  "shop_name": "Suresh General Store"
}
```

#### Error Responses
- **403** - Access denied or only shopkeepers can create products
- **400** - Validation errors (duplicate name, invalid price/stock)

---

### 15. Product Details
**GET** `/products/shops/{shop_id}/products/{product_id}/` - Get product details  
**PUT** `/products/shops/{shop_id}/products/{product_id}/` - Update product (owner only)  
**DELETE** `/products/shops/{shop_id}/products/{product_id}/` - Delete product (owner only)

**Requires Authentication**

#### GET Response
```json
{
  "id": 1,
  "name": "Fresh Tomatoes",
  "price": "50.00",
  "stock": 30,
  "product_image_url": "https://example.com/products/tomatoes.jpg",
  "description": "Fresh red tomatoes from local farms",
  "created_at": "2024-01-15T10:30:00Z",
  "shop_name": "Suresh General Store"
}
```

#### PUT Request Body (Partial updates allowed)
```json
{
  "price": 55.00,
  "stock": 35,
  "description": "Premium fresh tomatoes from local farms"
}
```

#### DELETE Response
```json
{
  "message": "Product deleted successfully"
}
```

#### Error Responses
- **403** - Access denied or only shop owner can modify
- **404** - Product not found

---

## 🛒 Order Management

### 16. Place Order
**POST** `/orders/shops/{shop_id}/orders/`

**Requires Authentication - Customer Only**

Customer places an order from a shop they've joined.

#### Request Body
```json
{
  "items": [
    {
      "product_id": "1",
      "quantity": "2"
    },
    {
      "product_id": "3",
      "quantity": "1"
    }
  ]
}
```

#### Response
```json
{
  "id": 1,
  "customer": {
    "id": 1,
    "mobile_number": "9876543210",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "address": "123 Main St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": null
  },
  "shop": {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_name": "Suresh Gupta"
  },
  "status": "PENDING",
  "total_amount": "165.00",
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "order_items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Fresh Tomatoes",
      "quantity": 2,
      "price": "50.00"
    },
    {
      "id": 2,
      "product": 3,
      "product_name": "Amul Fresh Milk",
      "quantity": 1,
      "price": "65.00"
    }
  ]
}
```

#### Error Responses
- **403** - Only customers can place orders or not a customer of this shop
- **400** - Validation errors (insufficient stock, invalid quantities)

---

### 17. My Orders
**GET** `/orders/my-orders/`

**Requires Authentication - Customer Only**

Get list of all orders placed by the customer.

#### Response
```json
[
  {
    "id": 1,
    "customer": {
      "id": 1,
      "mobile_number": "9876543210",
      "name": "Priya Sharma",
      "email": "priya@example.com",
      "address": "123 Main St, Mumbai",
      "profile_image_url": "https://example.com/image.jpg",
      "role": "CUSTOMER",
      "created_at": "2024-01-15T10:30:00Z",
      "shop": null
    },
    "shop": {
      "id": 1,
      "name": "Suresh General Store",
      "address": "10 Commercial Street, Mumbai",
      "description": "Your neighborhood grocery store",
      "shop_logo_url": "https://example.com/logo.jpg",
      "shop_id": "SGS12345",
      "created_at": "2024-01-15T10:30:00Z",
      "owner_name": "Suresh Gupta"
    },
    "status": "PENDING",
    "total_amount": "165.00",
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:30:00Z",
    "order_items": [
      {
        "id": 1,
        "product": 1,
        "product_name": "Fresh Tomatoes",
        "quantity": 2,
        "price": "50.00"
      }
    ]
  }
]
```

#### Error Responses
- **403** - Only customers can view orders

---

### 18. Order Details
**GET** `/orders/{order_id}/`

**Requires Authentication**

Get details of a specific order. Accessible by order customer or shop owner.

#### Response
```json
{
  "id": 1,
  "customer": {
    "id": 1,
    "mobile_number": "9876543210",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "address": "123 Main St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": null
  },
  "shop": {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_name": "Suresh Gupta"
  },
  "status": "PENDING",
  "total_amount": "165.00",
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "order_items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Fresh Tomatoes",
      "quantity": 2,
      "price": "50.00"
    }
  ]
}
```

#### Error Responses
- **403** - Access denied (not order owner or shop owner)
- **404** - Order not found

---

### 19. Shop Orders
**GET** `/orders/shops/{shop_id}/orders/list/`

**Requires Authentication - Shopkeeper Only**

Get list of all orders for a shop (shopkeeper's own shop only).

#### Response
```json
[
  {
    "id": 1,
    "customer": {
      "id": 1,
      "mobile_number": "9876543210",
      "name": "Priya Sharma",
      "email": "priya@example.com",
      "address": "123 Main St, Mumbai",
      "profile_image_url": "https://example.com/image.jpg",
      "role": "CUSTOMER",
      "created_at": "2024-01-15T10:30:00Z",
      "shop": null
    },
    "shop": {
      "id": 1,
      "name": "Suresh General Store",
      "address": "10 Commercial Street, Mumbai",
      "description": "Your neighborhood grocery store",
      "shop_logo_url": "https://example.com/logo.jpg",
      "shop_id": "SGS12345",
      "created_at": "2024-01-15T10:30:00Z",
      "owner_name": "Suresh Gupta"
    },
    "status": "PENDING",
    "total_amount": "165.00",
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:30:00Z",
    "order_items": [
      {
        "id": 1,
        "product": 1,
        "product_name": "Fresh Tomatoes",
        "quantity": 2,
        "price": "50.00"
      }
    ]
  }
]
```

#### Error Responses
- **403** - Only shopkeepers can view shop orders or access denied

---

### 20. Update Order Status
**PUT** `/orders/{order_id}/status/`

**Requires Authentication - Shopkeeper Only**

Update order status. Only shop owner can update.

#### Request Body
```json
{
  "status": "ACCEPTED"
}
```

#### Valid Status Values
- **PENDING** - Initial status
- **ACCEPTED** - Shop accepts the order (reduces product stock)
- **REJECTED** - Shop rejects the order
- **DELIVERED** - Order completed

#### Response
```json
{
  "id": 1,
  "customer": {
    "id": 1,
    "mobile_number": "9876543210",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "address": "123 Main St, Mumbai",
    "profile_image_url": "https://example.com/image.jpg",
    "role": "CUSTOMER",
    "created_at": "2024-01-15T10:30:00Z",
    "shop": null
  },
  "shop": {
    "id": 1,
    "name": "Suresh General Store",
    "address": "10 Commercial Street, Mumbai",
    "description": "Your neighborhood grocery store",
    "shop_logo_url": "https://example.com/logo.jpg",
    "shop_id": "SGS12345",
    "created_at": "2024-01-15T10:30:00Z",
    "owner_name": "Suresh Gupta"
  },
  "status": "ACCEPTED",
  "total_amount": "165.00",
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T14:35:00Z",
  "order_items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Fresh Tomatoes",
      "quantity": 2,
      "price": "50.00"
    }
  ]
}
```

#### Error Responses
- **403** - Only shop owner can update order status
- **400** - Cannot modify delivered/rejected orders or insufficient stock