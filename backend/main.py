from fastapi import FastAPI, HTTPException, Depends, Header, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
import re
import html

def sanitize_input(text):
    """XSS防护：转义HTML特殊字符"""
    if text is None:
        return text
    return html.escape(str(text))

def success_resp(data=None, msg="success", code=200):
    """统一成功响应格式"""
    return {"code": code, "msg": msg, "data": data}

def error_resp(msg="error", code=400, data=None):
    """统一错误响应格式"""
    return {"code": code, "msg": msg, "data": data}
from typing import Optional, List
import sqlite3
import hashlib
import os
import json
from datetime import datetime, timedelta
import secrets

from database import init_db, DB_PATH

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (future use)

app = FastAPI(title="Mall API", version="1.0.0", lifespan=lifespan)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    print(f"[ERROR] {exc}")
    traceback.print_exc()
    return error_resp(msg=str(exc)[:100], code=500)

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
    category_id: Optional[int] = None

class CartItem(BaseModel):
    product_id: int = Field(..., gt=0, description="商品ID")
    quantity: int = Field(..., ge=0, description="数量")

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

def row_to_product(row) -> dict:
    """将数据库行转换为商品字典"""
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "price": row["price"],
        "stock": row["stock"],
        "image_url": row["image_url"],
        "category_id": row.get("category_id")
    }

# ============ 用户接口 ============

@app.post("/api/user/register", response_model=Token)
def register(user: UserRegister):
    conn = get_db()
    cursor = conn.cursor()
    try:
        # XSS防护
        username = sanitize_input(user.username)
        email = sanitize_input(user.email)
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, hash_password(user.password), email)
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

@app.get("/api/product/list")
def list_products(keyword: str = "", category_id: int = None, page: int = 1, page_size: int = 20):
    conn = get_db()
    cursor = conn.cursor()
    
    # 查询总数
    count_sql = "SELECT COUNT(*) FROM products WHERE 1=1"
    count_params = []
    if keyword:
        count_sql += " AND (name LIKE ? OR description LIKE ?)"
        count_params.extend([f"%{keyword}%", f"%{keyword}%"])
    if category_id:
        count_sql += " AND category_id = ?"
        count_params.append(category_id)
    
    cursor.execute(count_sql, count_params)
    total = cursor.fetchone()[0]
    
    # 查询列表
    sql = "SELECT id, name, description, price, stock, image_url, category_id FROM products WHERE 1=1"
    params = []
    if keyword:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if category_id:
        sql += " AND category_id = ?"
        params.append(category_id)
    
    sql += f" LIMIT {page_size} OFFSET {(page - 1) * page_size}"
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    LOW_STOCK_THRESHOLD = 10
    items = [{"id": r["id"], "name": r["name"], "description": r["description"], 
             "price": r["price"], "stock": r["stock"], "image_url": r["image_url"], 
             "category_id": r["category_id"], "low_stock": r["stock"] < LOW_STOCK_THRESHOLD} for r in rows]
    return {"items": items, "total": total, "page": page, "page_size": page_size}

@app.get("/api/product/search", response_model=List[Product])
def search_products(q: str = Query("", min_length=0, max_length=50, description="搜索关键词")):
    """商品搜索接口 - 支持高亮"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description, price, stock, image_url FROM products WHERE name LIKE ? OR description LIKE ? ORDER BY name",
        (f"%{q}%", f"%{q}%")
    )
    rows = cursor.fetchall()
    conn.close()
    # 返回高亮结果
    highlight = lambda text: text.replace(q, f"<mark>{q}</mark>")
    return [{"id": r["id"], "name": highlight(r["name"]), "description": highlight(r["description"]), 
             "price": r["price"], "stock": r["stock"], "image_url": r["image_url"]} for r in rows]

@app.get("/api/product/ranking")
def get_product_ranking(limit: int = Query(10, ge=1, le=50)):
    """商品销量排行榜"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description, price, stock, sales_count, image_url FROM products WHERE sales_count > 0 ORDER BY sales_count DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "name": r["name"], "description": r["description"], 
             "price": r["price"], "stock": r["stock"], "sales_count": r["sales_count"], 
             "image_url": r["image_url"]} for r in rows]

@app.get("/api/product/detail/{product_id}", response_model=Product)
def get_product(product_id: int, authorization: Optional[str] = Header(None)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price, stock, image_url FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 自动记录浏览历史
    try:
        user_id = get_current_user(authorization) if authorization else None
        if user_id:
            cursor.execute("DELETE FROM browse_history WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            cursor.execute("INSERT INTO browse_history (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
            conn.commit()
    except:
        pass  # 未登录不记录
    
    conn.close()
    # 添加分享链接
    share_url = f"/product/{row['id']}"
    return {"id": row["id"], "name": row["name"], "description": row["description"],
            "price": row["price"], "stock": row["stock"], "image_url": row["image_url"], "share_url": share_url}

# ============ 购物车接口 ============

@app.post("/api/cart/add")
def add_to_cart(item: CartItem, authorization: Optional[str] = Header(None)):
    user_id = get_current_user(authorization)
    
    # 校验数量
    if item.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
    if item.quantity > 9999:
        raise HTTPException(status_code=400, detail="Quantity too large")
    
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
    return success_resp(msg="Added to cart")

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
    return success_resp(msg="Cart updated")

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
        # 扣减库存，增加销量
        cursor.execute("UPDATE products SET stock = stock - ?, sales_count = sales_count + ? WHERE id = ?", 
                     (item["quantity"], item["quantity"], item["product_id"]))
    
    cursor.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return success_resp({"order_id": order_id}, "Order created")

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
    return success_resp({"order_id": order_id}, "Payment successful")

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
    return success_resp({"order_id": order_id}, "Order cancelled")

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
    cursor.execute("SELECT id, username, email, avatar_url FROM users WHERE id = ?", (user_id,))
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
    # XSS防护
    username = sanitize_input(profile.username)
    email = sanitize_input(profile.email)
    # 支持头像URL
    avatar_url = getattr(profile, 'avatar_url', None)
    if avatar_url:
        cursor.execute("UPDATE users SET username = ?, email = ?, avatar_url = ? WHERE id = ?", 
                      (username, email, avatar_url, user_id))
    else:
        cursor.execute("UPDATE users SET username = ?, email = ? WHERE id = ?", 
                      (username, email, user_id))
    conn.commit()
    conn.close()
    return success_resp(msg="Profile updated")

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
    return success_resp(msg="Password changed")

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
def get_products_by_category(category_id: int, keyword: str = "", page: int = 1, page_size: int = 20):
    """获取分类下的商品"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查分类是否存在
    cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Category not found")
    
    # 查询总数
    count_sql = "SELECT COUNT(*) FROM products WHERE category_id = ?"
    count_params = [category_id]
    if keyword:
        count_sql += " AND (name LIKE ? OR description LIKE ?)"
        count_params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    cursor.execute(count_sql, count_params)
    total = cursor.fetchone()[0]
    
    # 查询列表
    if keyword:
        cursor.execute('''
            SELECT id, name, description, price, stock, image_url, category_id
            FROM products WHERE category_id = ? AND (name LIKE ? OR description LIKE ?)
            LIMIT ? OFFSET ?
        ''', (category_id, f'%{keyword}%', f'%{keyword}%', page_size, (page - 1) * page_size))
    else:
        cursor.execute('''
            SELECT id, name, description, price, stock, image_url, category_id
            FROM products WHERE category_id = ?
            LIMIT ? OFFSET ?
        ''', (category_id, page_size, (page - 1) * page_size))
    
    products = cursor.fetchall()
    conn.close()
    
    items = [{"id": p["id"], "name": p["name"], "description": p["description"],
              "price": p["price"], "stock": p["stock"], "image_url": p["image_url"],
              "category_id": p["category_id"]} for p in products]
    return {"items": items, "total": total, "page": page, "page_size": page_size}

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

# ============ 浏览历史接口 ============

@app.get("/api/history")
def get_browse_history(authorization: Optional[str] = Header(None)):
    """获取用户浏览历史"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT h.id, h.product_id, h.viewed_at, p.name, p.price, p.image_url
        FROM browse_history h
        JOIN products p ON h.product_id = p.id
        WHERE h.user_id = ?
        ORDER BY h.viewed_at DESC
        LIMIT 50
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "product_id": r["product_id"], "name": r["name"], 
             "price": r["price"], "image_url": r["image_url"], "viewed_at": r["viewed_at"]} for r in rows]

@app.post("/api/history/{product_id}")
def add_browse_history(product_id: int, authorization: Optional[str] = Header(None)):
    """记录商品浏览历史"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    # 删除同商品旧记录，保留最新
    cursor.execute("DELETE FROM browse_history WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    cursor.execute("INSERT INTO browse_history (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
    conn.commit()
    conn.close()
    return success_resp(msg="History recorded")

# ============ 收藏接口 ============

@app.get("/api/favorites")
def get_favorites(authorization: Optional[str] = Header(None)):
    """获取用户收藏列表"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.id, f.product_id, f.created_at, p.name, p.price, p.image_url
        FROM favorites f
        JOIN products p ON f.product_id = p.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "product_id": r["product_id"], "name": r["name"], 
             "price": r["price"], "image_url": r["image_url"]} for r in rows]

@app.post("/api/favorites/{product_id}")
def add_favorite(product_id: int, authorization: Optional[str] = Header(None)):
    """添加商品收藏"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favorites (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
        conn.commit()
        msg = "Added to favorites"
    except sqlite3.IntegrityError:
        msg = "Already in favorites"
    conn.close()
    return success_resp(msg=msg)

@app.delete("/api/favorites/{product_id}")
def remove_favorite(product_id: int, authorization: Optional[str] = Header(None)):
    """取消商品收藏"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()
    return success_resp(msg="Removed from favorites")

@app.get("/api/favorites/{product_id}/check")
def check_favorite(product_id: int, authorization: Optional[str] = Header(None)):
    """检查商品是否已收藏"""
    user_id = get_current_user(authorization)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM favorites WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    exists = cursor.fetchone() is not None
    conn.close()
    return {"favorited": exists}

# ============ 评论接口 ============

@app.post("/api/product/{product_id}/review")
def add_review(product_id: int, review: ReviewCreate, authorization: Optional[str] = Header(None)):
    """添加评论（需已购买）"""
    # 未登录返回401
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
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
    
    # 添加评论 - XSS防护
    comment = sanitize_input(review.comment)
    cursor.execute(
        "INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)",
        (product_id, user_id, review.rating, comment)
    )
    conn.commit()
    conn.close()
    return success_resp(msg="Review added")

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
# 已移至 lifespan 管理

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
