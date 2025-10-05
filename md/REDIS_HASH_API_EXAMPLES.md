# Redis Hash API 使用示例

本文档提供了 `/redis/hash` 路由下所有 API 方法的详细使用示例。

## 1. HSET - 设置哈希表字段值

### 设置单个字段值
```bash
curl -X POST "http://localhost:8000/redis/hash/hset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1000",
           "key": "name",
           "value": "Alice"
         }'
```

### 批量设置多个字段值（Redis 4.0.0+ 推荐方式）
```bash
curl -X POST "http://localhost:8000/redis/hash/hset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1001",
           "mapping": {
             "name": "Bob",
             "age": 30,
             "email": "bob@example.com"
           }
         }'
```

### 设置复杂数据类型
```bash
curl -X POST "http://localhost:8000/redis/hash/hset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1000",
           "key": "profile",
           "value": {"age": 25, "email": "alice@example.com"}
         }'
```

## 2. HSETNX - 仅当字段不存在时设置哈希表字段值

### 字段不存在时设置成功
```bash
curl -X POST "http://localhost:8000/redis/hash/hsetnx" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1002",
           "key": "name",
           "value": "Charlie"
         }'
```

### 字段已存在时设置失败
```bash
curl -X POST "http://localhost:8000/redis/hash/hsetnx" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1002",
           "key": "name",
           "value": "Charlie Updated"
         }'
```

## 3. HSCAN - 增量迭代哈希表中的字段

### 基本用法
```bash
curl "http://localhost:8000/redis/hash/hscan?name=user:1001"
```

### 使用游标进行分页
```bash
curl "http://localhost:8000/redis/hash/hscan?name=user:1001&cursor=10"
```

### 使用匹配模式过滤字段
```bash
curl "http://localhost:8000/redis/hash/hscan?name=user:1001&match=name*"
```

### 指定每次迭代返回的元素数量
```bash
curl "http://localhost:8000/redis/hash/hscan?name=user:1001&count=5"
```

## 4. HGET - 获取哈希表字段值

### 基本用法
```bash
curl "http://localhost:8000/redis/hash/hget?name=user:1000&key=name"
```

### 获取复杂数据类型
```bash
curl "http://localhost:8000/redis/hash/hget?name=user:1000&key=profile"
```

## 5. HMGET - 获取哈希表多个字段值

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/hash/hmget" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1001",
           "keys": ["name", "age", "email"]
         }'
```

### 获取部分存在的字段
```bash
curl -X POST "http://localhost:8000/redis/hash/hmget" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1001",
           "keys": ["name", "phone", "email"]
         }'
```

## 6. HGETALL - 获取哈希表所有字段和值

### 基本用法
```bash
curl "http://localhost:8000/redis/hash/hgetall?name=user:1001"
```

### 获取空哈希表
```bash
curl "http://localhost:8000/redis/hash/hgetall?name=user:9999"
```

## 7. HDEL - 删除哈希表一个或多个字段

### 删除单个字段
```bash
curl -X DELETE "http://localhost:8000/redis/hash/hdel" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1000",
           "keys": ["name"]
         }'
```

### 批量删除多个字段
```bash
curl -X DELETE "http://localhost:8000/redis/hash/hdel" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1001",
           "keys": ["name", "age", "email"]
         }'
```

## 8. HEXISTS - 检查哈希表字段是否存在

### 字段存在
```bash
curl "http://localhost:8000/redis/hash/hexists?name=user:1001&key=email"
```

### 字段不存在
```bash
curl "http://localhost:8000/redis/hash/hexists?name=user:1001&key=phone"
```

## 9. HLEN - 获取哈希表字段数量

### 基本用法
```bash
curl "http://localhost:8000/redis/hash/hlen?name=user:1001"
```

### 空哈希表
```bash
curl "http://localhost:8000/redis/hash/hlen?name=empty_hash"
```

## 10. HKEYS - 获取哈希表所有字段名

### 基本用法
```bash
curl "http://localhost:8000/redis/hash/hkeys?name=user:1001"
```

### 空哈希表
```bash
curl "http://localhost:8000/redis/hash/hkeys?name=empty_hash"
```

## 11. HVALS - 获取哈希表所有字段值

### 基本用法
```bash
curl "http://localhost:8000/redis/hash/hvals?name=user:1001"
```

### 空哈希表
```bash
curl "http://localhost:8000/redis/hash/hvals?name=empty_hash"
```

## 12. HINCRBY - 哈希表字段值增加指定整数

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/hash/hincrby" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1000",
           "key": "login_count",
           "increment": 1
         }'
```

### 增加负数（减少）
```bash
curl -X POST "http://localhost:8000/redis/hash/hincrby" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1000",
           "key": "balance",
           "increment": -50
         }'
```

## 实际应用场景示例

### 场景1: 用户信息管理
```bash
# 创建用户信息（推荐使用HSET的mapping参数）
curl -X POST "http://localhost:8000/redis/hash/hset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1234",
           "mapping": {
             "name": "John Doe",
             "email": "john@example.com",
             "age": 28,
             "login_count": 0
           }
         }'

# 获取用户信息
curl "http://localhost:8000/redis/hash/hgetall?name=user:1234"

# 更新用户登录次数
curl -X POST "http://localhost:8000/redis/hash/hincrby" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1234",
           "key": "login_count",
           "increment": 1
         }'

# 获取特定字段
curl "http://localhost:8000/redis/hash/hget?name=user:1234&key=login_count"

# 更新用户邮箱
curl -X POST "http://localhost:8000/redis/hash/hset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1234",
           "key": "email",
           "value": "john.doe@example.com"
         }'

# 检查字段是否存在
curl "http://localhost:8000/redis/hash/hexists?name=user:1234&key=email"

# 删除用户年龄信息
curl -X DELETE "http://localhost:8000/redis/hash/hdel" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:1234",
           "keys": ["age"]
         }'
```

### 场景2: 商品库存管理
```bash
# 创建商品信息
curl -X POST "http://localhost:8000/redis/hash/hset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "product:sku5000",
           "mapping": {
             "name": "Wireless Headphones",
             "price": 99.99,
             "stock": 100,
             "sold": 0
           }
         }'

# 获取商品信息
curl "http://localhost:8000/redis/hash/hgetall?name=product:sku5000"

# 减少库存
curl -X POST "http://localhost:8000/redis/hash/hincrby" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "product:sku5000",
           "key": "stock",
           "increment": -1
         }'

# 增加销量
curl -X POST "http://localhost:8000/redis/hash/hincrby" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "product:sku5000",
           "key": "sold",
           "increment": 1
         }'

# 检查库存
curl "http://localhost:8000/redis/hash/hget?name=product:sku5000&key=stock"
```

### 场景3: 分布式锁实现
```bash
# 尝试获取锁（设置成功表示获取到锁）
curl -X POST "http://localhost:8000/redis/hash/hsetnx" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "lock:resource1",
           "key": "owner",
           "value": "process_12345"
         }'

# 检查锁是否已存在
curl "http://localhost:8000/redis/hash/hexists?name=lock:resource1&key=owner"

# 释放锁
curl -X DELETE "http://localhost:8000/redis/hash/hdel" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "lock:resource1",
           "keys": ["owner"]
         }'
```

### 场景4: 大型哈希表遍历
```bash
# 遍历大型哈希表（分页方式）
# 第一次迭代
curl "http://localhost:8000/redis/hash/hscan?name=large_hash&count=10"

# 根据返回的游标进行后续迭代
curl "http://localhost:8000/redis/hash/hscan?name=large_hash&cursor=10&count=10"

# 使用匹配模式过滤字段
curl "http://localhost:8000/redis/hash/hscan?name=large_hash&match=user:*&count=10"
```