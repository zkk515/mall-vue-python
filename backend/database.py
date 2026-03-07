import sqlite3
import os
import sys
from datetime import datetime

# 数据目录：通过环境变量 MALL_DATA_PATH 配置
# 开发环境（Mac/Linux本地）：默认当前目录的 data 文件夹
# Docker环境：/app/data

if os.environ.get('MALL_DATA_PATH'):
    DB_DIR = os.environ.get('MALL_DATA_PATH')
else:
    # 检测是否在Docker容器内
    if os.path.exists('/.dockerenv') or os.environ.get('DOCKER_CONTAINER'):
        DB_DIR = '/app/data'
    else:
        # 本地开发：使用相对路径
        DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

DB_PATH = os.path.join(DB_DIR, 'mall.db')

def init_db():
    """初始化数据库和表结构"""
    os.makedirs(DB_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 迁移：为products表添加sales_count字段（如果不存在）
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN sales_count INTEGER DEFAULT 0")
    except:
        pass  # 字段已存在

    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            sales_count INTEGER DEFAULT 0,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 购物车表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # 订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            receiver_name TEXT,
            receiver_phone TEXT,
            receiver_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 订单详情表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT,
            price REAL,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # 分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT
        )
    ''')

    # 评论表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 商品表添加分类ID
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'category_id' not in columns:
        cursor.execute("ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id)")

    # 插入示例分类
    cursor.execute('SELECT COUNT(*) FROM categories')
    if cursor.fetchone()[0] == 0:
        sample_categories = [
            ('手机通讯', 'https://picsum.photos/200/100?random=10'),
            ('电脑办公', 'https://picsum.photos/200/100?random=11'),
            ('影音娱乐', 'https://picsum.photos/200/100?random=12'),
            ('智能穿戴', 'https://picsum.photos/200/100?random=13'),
            ('数码配件', 'https://picsum.photos/200/100?random=14'),
        ]
        cursor.executemany(
            'INSERT INTO categories (name, image) VALUES (?, ?)',
            sample_categories
        )

    # 插入示例商品
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('iPhone 15 Pro', '最新款苹果手机，A17 Pro芯片', 7999, 100, 'https://picsum.photos/400/300?random=1', 1),
            ('MacBook Air M3', '轻薄便携，性能强劲', 9499, 50, 'https://picsum.photos/400/300?random=2', 2),
            ('iPad Pro', '专业级平板电脑', 6999, 80, 'https://picsum.photos/400/300?random=3', 1),
            ('AirPods Pro', '主动降噪无线耳机', 1899, 200, 'https://picsum.photos/400/300?random=4', 3),
            ('Apple Watch', '智能手表，健康管理', 2999, 150, 'https://picsum.photos/400/300?random=5', 4),
            ('华为Mate 60', '华为旗舰手机', 5999, 80, 'https://picsum.photos/400/300?random=6', 1),
            ('ThinkPad X1', '商务笔记本电脑', 8999, 40, 'https://picsum.photos/400/300?random=7', 2),
            ('Sony WH-1000XM5', '降噪耳机旗舰', 2699, 120, 'https://picsum.photos/400/300?random=8', 3),
            ('小米手环8', '运动健康手环', 299, 300, 'https://picsum.photos/400/300?random=9', 4),
            ('数据线套装', '快充数据线', 49, 500, 'https://picsum.photos/400/300?random=15', 5),
        ]
        cursor.executemany(
            'INSERT INTO products (name, description, price, stock, image_url, category_id) VALUES (?, ?, ?, ?, ?, ?)',
            sample_products
        )

    # 商品浏览历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS browse_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # 商品收藏表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(user_id, product_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

    # 迁移：检查表是否存在（新增字段）
    cursor.execute("PRAGMA table_info(browse_history)")
    if not cursor.fetchall():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS browse_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
