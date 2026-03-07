from fastapi import FastAPI, HTTPException, Depends, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import re
from typing import Optional, List
import sqlite3
import hashlib
import os
import json
from datetime import datetime, timedelta
import secrets

from database import init_db, DB_PATH

app = FastAPI(title="Mall API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Token存储（文件持久化）
TOKENS_FILE = os.path.join(os.path.dirname(DB_PATH), 'tokens.json')

def load_tokens():
    """从文件加载tokens"""
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tokens(tokens):
    """保存tokens到文件"""
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f)

tokens = load_tokens()

# ============ 数据模型 ============

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    email: Optional[str] = Field(None, description="邮箱")

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, description="用户名")
    password: str = Field(..., min_length=1, description="密码")

class Token(BaseModel):
    access_token: str
    token_type: str

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]

class CartItem(BaseModel):
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., ge=1, le=999, description="数量")

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    product_image: str
    quantity: int
    checked: bool = False

class OrderCreate(BaseModel):
    receiver_name: str = Field(..., min_length=2, max_length=50, description="收货人姓名")
    receiver_phone: str = Field(..., min_length=7, max_length=20, description="联系电话")
    receiver_address: str = Field(..., min_length=5, max_length=200, description="收货地址")

class OrderItem(BaseModel):
    id: int
    product_name: str
    product_image: str
    price: float
    quantity: int

class Order(BaseModel):
    id: int
    total_amount: float
    status: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    created_at: str
    items: List[OrderItem] = []

class Review(BaseModel):
    id: int
    product_id: int
    user_id: int
    username: str
    rating: int
    comment: Optional[str]
    created_at: str

class ReviewCreate(BaseModel):
    product_id: int = Field(..., gt=0, description="商品ID")
    rating: int = Field(..., ge=1, le=5, description="评分1-5")
    comment: Optional[str] = Field(None, max_length=500, description="评论")

# ============ 辅助函数 ============

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 简单密码加密（SHA256）
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    tokens[token] = {"user_id": user_id, "exp": datetime.now().timestamp() + timedelta(days=7).total_seconds()}
    save_tokens(tokens)
    return token

def get_current_user(authorization: Optional[str] = None) -> int:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    if tokens[token]["exp"] < datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token expired")
    return tokens[token]["user_id"]

# ============ 用户接口 ============

@app.post("/api/user/register", response_model=Token)
def register(user: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (user.username, hash_password(user.password), user.email)
        )
        conn.commit()
        user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        conn.close()
    token = create_token(user_id)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/api/user/login", response_model=Token)
def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (user.username,))
    row = cursor.fetchone()
    conn.close()
    if not row or not verify_password(user.password, row["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(row["id"])
    return {"access_token": token, "token_type": "bearer"}

# ============ 商品接口 ============

@app.get("/api/product/list", response_model=List[Product])
def list_products(keyword: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    if keyword:
        cursor.execute(
            "SELECT id, name, description, price, stock, image_url FROM products WHERE name LIKE ? OR description LIKE ?",
            (f"%{keyword}%", f"%{keyword}%")
        )
    else:
        cursor.execute("SELECT id, name, description, price, stock, image_url FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "description": r["description"], 
             "price": r["price"], "stock": r["stock"], "image_url": r["image_url"]} for r in rows]

@app.get("/api/product/detail/{product_id}", response_model=Product)
def get_product(product_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, stock, image_url FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"id": row["id"], "name": row["name"], "description": row["description"],
            "price": row["price"], "stock": row["stock"], "image_url": row["image_url"]}

# ============ 购物车接口 ============

@app.post("/api/cart/add")
def add_to_cart(item: CartItem, authorization: Optional[str] = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT stock FROM products WHERE id = ?", (item.product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    if product["stock"] < item.quantity:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    cursor.execute("SELECT id, quantity FROM carts WHERE user_id = ? AND product_id = ?", (user_id, item.product_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("UPDATE carts SET quantity = ? WHERE id = ?", (existing["quantity"] + item.quantity, existing["id"]))
    else:
        cursor.execute("INSERT INTO carts (user_id, product_id, quantity) VALUES (?, ?, ?)", (user_id, item.product_id, item.quantity))
    
    conn.commit()
    conn.close()
    return {"message": "Added to cart"}

@app.post("/api/cart/update")
def update_cart(item: CartItem, authorization: Optional[str] = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    if item.quantity <= 0:
        cursor.execute("DELETE FROM carts WHERE user_id = ? AND product_id = ?", (user_id, item.product_id))
    else:
        cursor.execute("UPDATE carts SET quantity = ? WHERE user_id = ? AND product_id = ?", (item.quantity, user_id, item.product_id))
    conn.commit()
    conn.close()
    return {"message": "Cart updated"}

@app.get("/api/cart/list", response_model=List[CartItemResponse])
def list_cart(authorization: Optional[str] = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.id, c.product_id, p.name as product_name, p.price as product_price, 
               p.image_url as product_image, c.quantity
        FROM carts c JOIN products p ON c.product_id = p.id WHERE c.user_id = ?
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "product_id": r["product_id"], "product_name": r["product_name"],
             "product_price": r["product_price"], "product_image": r["product_image"], "quantity": r["quantity"]} for r in rows]

# ============ 订单接口 ============

@app.post("/api/order/create")
def create_order(order: OrderCreate, authorization: Optional[str] = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.product_id, p.name, p.price, c.quantity, p.stock
        FROM carts c JOIN products p ON c.product_id = p.id WHERE c.user_id = ?
    ''', (user_id,))
    items = cursor.fetchall()
    
    if not items:
        conn.close()
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total = 0
    for item in items:
        if item["stock"] < item["quantity"]:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {item['name']}")
        total += item["price"] * item["quantity"]
    
    cursor.execute('''
        INSERT INTO orders (user_id, total_amount, receiver_name, receiver_phone, receiver_address)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, total, order.receiver_name, order.receiver_phone, order.receiver_address))
    order_id = cursor.lastrowid
    
    for item in items:
        cursor.execute(
            "INSERT INTO order_items (order_id, product_id, product_name, price, quantity) VALUES (?, ?, ?, ?, ?)",
            (order_id, item["product_id"], item["name"], item["price"], item["quantity"])
        )
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item["quantity"], item["product_id"]))
    
    cursor.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "Order created", "order_id": order_id}

@app.get("/api/order/list", response_model=List[Order])
def list_orders(authorization: Optional[str] = Header(None)):
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, total_amount, status, receiver_name, receiver_phone, receiver_address, created_at
        FROM orders WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    orders = cursor.fetchall()
    
    result = []
    for o in orders:
        cursor.execute('''SELECT oi.id, oi.product_name, p.image_url as product_image, oi.price, oi.quantity 
                          FROM order_items oi JOIN products p ON oi.product_id = p.id 
                          WHERE oi.order_id = ?''', (o["id"],))
        items = cursor.fetchall()
        result.append({
            "id": o["id"], "total_amount": o["total_amount"], "status": o["status"],
            "receiver_name": o["receiver_name"], "receiver_phone": o["receiver_phone"],
            "receiver_address": o["receiver_address"], "created_at": o["created_at"],
            "items": [{"id": i["id"], "product_name": i["product_name"], "product_image": i["product_image"], "price": i["price"], "quantity": i["quantity"]} for i in items]
        })
    
    conn.close()
    return result

@app.post("/api/order/{order_id}/pay")
def pay_order(order_id: int, authorization: Optional[str] = Header(None)):
    """支付订单"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id))
    order = cursor.fetchone()
    if not order:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
    if order["status"] != "pending":
        conn.close()
        raise HTTPException(status_code=400, detail="Order cannot be paid")
    
    cursor.execute("UPDATE orders SET status = 'paid' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return {"message": "Payment successful", "order_id": order_id}

@app.post("/api/order/{order_id}/cancel")
def cancel_order(order_id: int, authorization: Optional[str] = Header(None)):
    """取消订单"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id))
    order = cursor.fetchone()
    if not order:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
    if order["status"] not in ["pending", "paid"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Order cannot be cancelled")
    
    # 恢复库存
    cursor.execute("SELECT product_id, quantity FROM order_items WHERE order_id = ?", (order_id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (item["quantity"], item["product_id"]))
    
    cursor.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return {"message": "Order cancelled", "order_id": order_id}

# ============ 用户中心 ============

class UserProfile(BaseModel):
    username: str
    email: Optional[str] = None

@app.get("/api/user/profile")
def get_profile(authorization: Optional[str] = Header(None)):
    """获取用户信息"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/user/profile")
def update_profile(profile: UserProfile, authorization: Optional[str] = Header(None)):
    """更新用户信息"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", 
                  (profile.username, profile.email, user_id))
    conn.commit()
    conn.close()
    return {"message": "Profile updated"}

@app.put("/api/user/password")
def change_password(
    passwords: dict = Body(...),
    authorization: Optional[str] = Header(None)
):
    old_password = passwords.get("old_password", "")
    new_password = passwords.get("new_password", "")
    """修改密码"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not verify_password(old_password, user["password"]):
        conn.close()
        raise HTTPException(status_code=400, detail="Incorrect old password")
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_password), user_id))
    conn.commit()
    conn.close()
    return {"message": "Password changed"}

# ============ 商品分类 ============

@app.get("/api/category/list")
def list_categories():
    """获取分类列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, image FROM categories ORDER BY id")
    categories = cursor.fetchall()
    conn.close()
    return categories

@app.get("/api/category/{category_id}/products")
def get_products_by_category(category_id: int, keyword: str = ""):
    """获取分类下的商品"""
    conn = get_db()
    cursor = conn.cursor()
    if keyword:
        cursor.execute('''
            SELECT id, name, description, price, stock, image_url 
            FROM products WHERE category_id = ? AND (name LIKE ? OR description LIKE ?)
        ''', (category_id, f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute('''
            SELECT id, name, description, price, stock, image_url 
            FROM products WHERE category_id = ?
        ''', (category_id,))
    products = cursor.fetchall()
    conn.close()
    return products

# ============ 轮播图 ============

@app.get("/api/carousel")
def get_carousel():
    """获取轮播图列表"""
    return [
        {"id": 1, "image": "https://picsum.photos/800/350?random=101", "link": "/product/1", "title": "新品上市"},
        {"id": 2, "image": "https://picsum.photos/800/350?random=102", "link": "/product/2", "title": "电脑专场"},
        {"id": 3, "image": "https://picsum.photos/800/350?random=103", "link": "/product/3", "title": "智能穿戴"},
        {"id": 4, "image": "https://picsum.photos/800/350?random=104", "link": "/product/5", "title": "音频狂欢"},
    ]

# ============ 评论接口 ============

@app.post("/api/product/{product_id}/review")
def add_review(product_id: int, review: ReviewCreate, authorization: Optional[str] = Header(None)):
    """添加评论（需已购买）"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查商品是否存在
    cursor.execute("SELECT id FROM products WHERE id = ?", (product_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 检查用户是否已购买该商品
    cursor.execute('''
        SELECT COUNT(*) FROM orders o 
        JOIN order_items oi ON o.id = oi.order_id 
        WHERE o.user_id = ? AND oi.product_id = ? AND o.status = 'paid'
    ''', (user_id, product_id))
    if cursor.fetchone()[0] == 0:
        conn.close()
        raise HTTPException(status_code=403, detail="You can only review after purchasing this product")
    
    # 添加评论
    cursor.execute(
        "INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
        (product_id, user_id, review.rating, review.comment)
    )
    conn.commit()
    conn.close()
    return {"message": "Review added"}

@app.get("/api/product/{product_id}/reviews", response_model=List[Review])
def get_reviews(product_id: int):
    """获取商品评论列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.id, r.product_id, r.user_id, u.username, r.rating, r.comment, r.created_at
        FROM reviews r JOIN users u ON r.user_id = u.id
        WHERE r.product_id = ?
        ORDER BY r.created_at DESC
    ''', (product_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{
        "id": r["id"],
        "product_id": r["product_id"],
        "user_id": r["user_id"],
        "username": r["username"],
        "rating": r["rating"],
        "comment": r["comment"],
        "created_at": r["created_at"]
    } for r in rows]

@app.get("/api/product/{product_id}/reviews/count")
def get_review_count(product_id: int):
    """获取商品评论统计"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as total, AVG(rating) as avg_rating
        FROM reviews WHERE product_id = ?
    ''', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return {
        "total": row["total"] or 0,
        "avg_rating": round(row["avg_rating"], 1) if row["avg_rating"] else 0
    }

# ============ 启动 ============

@app.on_event("startup")
def startup():
    init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
