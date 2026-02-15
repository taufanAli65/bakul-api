# API cURL Guide

Set base URL and tokens first:

```bash
BASE_URL=http://localhost:8000
# After login, set
USER_TOKEN="replace-with-user-jwt"
ADMIN_TOKEN="replace-with-admin-jwt"

Run the full scripted flow (prints PASSED on success):
```bash
bash test.sh
```
```

## Public cURL

- Register user
```bash
curl -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password","name":"User","role":"user","profile_picture":null}'
```

- Login (get access token)
```bash
curl -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

- List products
```bash
curl "$BASE_URL/api/v1/products?limit=10&offset=0"
```

- Get product by id
```bash
curl "$BASE_URL/api/v1/products/{product_id}"
```

- List expedition services
```bash
curl "$BASE_URL/api/v1/expeditions?limit=10&offset=0"
```

## Admin cURL

- Login as admin
```bash
curl -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"adminpassword"}'
```

- Create product (multipart with optional image)
```bash
curl -X POST "$BASE_URL/api/v1/products" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "name=Sample" -F "price=1000" -F "stock=5" -F "description=Sample product"
```

- Update product
```bash
curl -X PUT "$BASE_URL/api/v1/products/{product_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated","price":1200,"description":"Desc","product_image_url":null}'
```

- Update product stock
```bash
curl -X PUT "$BASE_URL/api/v1/products/{product_id}/stock?stock=25" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- Delete product
```bash
curl -X DELETE "$BASE_URL/api/v1/products/{product_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- List all users
```bash
curl "$BASE_URL/api/v1/users?limit=10&offset=0" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- Create expedition service
```bash
curl -X POST "$BASE_URL/api/v1/expeditions?name=JNE" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- Bulk create expedition services
```bash
curl -X POST "$BASE_URL/api/v1/expeditions/bulk" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["JNE","TIKI"]'
```

- Update expedition service
```bash
curl -X PUT "$BASE_URL/api/v1/expeditions/{service_id}?name=Updated" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- Delete expedition service
```bash
curl -X DELETE "$BASE_URL/api/v1/expeditions/{service_id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- List transactions (admin can query any user)
```bash
curl "$BASE_URL/api/v1/transactions?user_id={user_id}&status_filter=pending&limit=10&offset=0" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

- Update transaction status
```bash
curl -X PUT "$BASE_URL/api/v1/transactions/{transaction_id}/status" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status":"paid"}'
```

## User cURL

- Get profile
```bash
curl "$BASE_URL/api/v1/users/me" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Update profile
```bash
curl -X PUT "$BASE_URL/api/v1/users/me" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"New Name","profile_picture":null}'
```

- Add to cart
```bash
curl -X POST "$BASE_URL/api/v1/carts?product_id={product_id}&quantity=2" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- List my cart
```bash
curl "$BASE_URL/api/v1/carts?limit=10&offset=0" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Update cart item quantity
```bash
curl -X PUT "$BASE_URL/api/v1/carts/{cart_id}?quantity=3" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Delete one cart item
```bash
curl -X DELETE "$BASE_URL/api/v1/carts/item?product_id={product_id}" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Empty cart
```bash
curl -X DELETE "$BASE_URL/api/v1/carts/empty" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Create transaction (uses cart if items omitted)
```bash
curl -X POST "$BASE_URL/api/v1/transactions" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id_expedition_service":"{service_id}","items":[{"id_product":"{product_id}","quantity":1}]}'
```

- List my transactions
```bash
curl "$BASE_URL/api/v1/transactions?limit=10&offset=0" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Get transaction detail
```bash
curl "$BASE_URL/api/v1/transactions/{transaction_id}" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Update transaction expedition (pending only)
```bash
curl -X PUT "$BASE_URL/api/v1/transactions/{transaction_id}/expedition?expedition_service_id={service_id}" \
  -H "Authorization: Bearer $USER_TOKEN"
```

- Simulate payment (sets status to paid if pending)
```bash
curl -X POST "$BASE_URL/api/v1/transactions/simulation/payment" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"transaction_id":"{transaction_id}"}'
```
