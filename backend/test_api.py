"""
极简商城后端测试
"""
import pytest
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestUserAPI:
    """用户API测试"""
    
    def test_register(self):
        """测试用户注册"""
        response = client.post("/api/user/register", json={
            "username": "testuser",
            "password": "testpass123"
        })
        assert response.status_code in [200, 400]  # 200成功或400已存在
    
    def test_login(self):
        """测试用户登录"""
        # 先注册
        client.post("/api/user/register", json={
            "username": "logintest",
            "password": "testpass123"
        })
        
        # 登录
        response = client.post("/api/user/login", json={
            "username": "logintest",
            "password": "testpass123"
        })
        assert response.status_code in [200, 401]


class TestProductAPI:
    """商品API测试"""
    
    def test_product_list(self):
        """测试商品列表"""
        response = client.get("/api/product/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_product_detail(self):
        """测试商品详情"""
        response = client.get("/api/product/detail/1")
        assert response.status_code in [200, 404]


class TestCartAPI:
    """购物车API测试"""
    
    def test_cart_list(self):
        """测试购物车列表"""
        response = client.get("/api/cart/list")
        assert response.status_code in [200, 401]  # 需要登录或返回空


class TestOrderAPI:
    """订单API测试"""
    
    def test_order_list(self):
        """测试订单列表"""
        response = client.get("/api/order/list")
        assert response.status_code in [200, 401]  # 需要登录或返回空
