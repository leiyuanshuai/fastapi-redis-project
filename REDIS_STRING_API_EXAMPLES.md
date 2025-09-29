# Redis String API 使用示例

本文档提供了 `/redis/string` 路由下所有 API 方法的详细使用示例。

## 1. SET - 设置键值对

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "username", "value": "john_doe"}'
```

### 设置过期时间
```bash
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "session_token", "value": "abc123xyz", "expire": 3600}'
```

### 使用 NX 选项（仅当键不存在时设置）
```bash
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "lock:resource1", "value": "locked", "expire": 30, "nx": true}'
```

### 使用 XX 选项（仅当键存在时设置）
```bash
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "user:last_login:123", "value": "2023-10-20T10:30:00Z", "xx": true}'
```

### 使用 KEEPTTL 选项（保持原有过期时间）
```bash
# 首先设置一个有过期时间的键
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "cached_data", "value": "old_value", "expire": 1800}'

# 更新值但保持原有过期时间
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "cached_data", "value": "new_value", "keep_ttl": true}'
```

## 2. SET-MULTIPLE - 批量设置键值对

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/string/set-multiple" \
     -H "Content-Type: application/json" \
     -d '{
           "key_value_pairs": {
             "user:1:name": "Alice",
             "user:1:email": "alice@example.com",
             "user:2:name": "Bob",
             "user:2:email": "bob@example.com"
           }
         }'
```

### 批量设置并指定过期时间
```bash
curl -X POST "http://localhost:8000/redis/string/set-multiple" \
     -H "Content-Type: application/json" \
     -d '{
           "key_value_pairs": {
             "temp:token:1": "token1",
             "temp:token:2": "token2",
             "temp:token:3": "token3"
           },
           "expire": 300
         }'
```

### 使用 NX 选项批量设置
```bash
curl -X POST "http://localhost:8000/redis/string/set-multiple" \
     -H "Content-Type: application/json" \
     -d '{
           "key_value_pairs": {
             "lock:resource1": "process1",
             "lock:resource2": "process1",
             "lock:resource3": "process1"
           },
           "nx": true
         }'
```

## 3. GET - 获取键值

### 基本用法
```bash
curl "http://localhost:8000/redis/string/get?key=username"
```

### 获取复杂数据类型
```bash
# 设置一个复杂对象
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "user_profile", "value": {"id": 123, "name": "John", "roles": ["admin", "user"]}}'

# 获取复杂对象
curl "http://localhost:8000/redis/string/get?key=user_profile"
```

## 4. GET-MULTIPLE - 批量获取键值

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/string/get-multiple" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["user:1:name", "user:1:email", "user:2:name", "user:2:email"]
         }'
```

### 获取混合存在的键
```bash
curl -X POST "http://localhost:8000/redis/string/get-multiple" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["existing_key", "nonexistent_key", "another_existing_key"]
         }'
```

## 5. STRLEN - 获取字符串长度

### 基本用法
```bash
# 设置一个字符串
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "message", "value": "Hello, World!"}'

# 获取字符串长度
curl "http://localhost:8000/redis/string/strlen?key=message"
```

### 获取不存在键的长度
```bash
curl "http://localhost:8000/redis/string/strlen?key=nonexistent_key"
```

## 6. GETRANGE - 获取字符串范围

### 基本用法
```bash
# 获取字符串的前5个字符
curl "http://localhost:8000/redis/string/getrange?key=message&start=0&end=4"

# 获取字符串的最后5个字符
curl "http://localhost:8000/redis/string/getrange?key=message&start=-5&end=-1"

# 获取整个字符串
curl "http://localhost:8000/redis/string/getrange?key=message&start=0&end=-1"
```

### 获取不存在键的范围
```bash
curl "http://localhost:8000/redis/string/getrange?key=nonexistent&start=0&end=5"
```

## 7. SETRANGE - 设置字符串范围

### 基本用法
```bash
# 从偏移量7开始覆写字符串
curl -X POST "http://localhost:8000/redis/string/setrange" \
     -H "Content-Type: application/json" \
     -d '{"key": "message", "offset": 7, "value": "Redis"}'
```

### 扩展字符串长度
```bash
# 在偏移量10处写入内容（中间会用零字节填充）
curl -X POST "http://localhost:8000/redis/string/setrange" \
     -H "Content-Type: application/json" \
     -d '{"key": "short", "offset": 10, "value": "extension"}'
```

## 8. EXISTS - 检查键是否存在

### 基本用法
```bash
curl "http://localhost:8000/redis/string/exists?key=username"
```

### 检查不存在的键
```bash
curl "http://localhost:8000/redis/string/exists?key=nonexistent"
```

## 9. EXISTS-MULTIPLE - 批量检查键是否存在

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/string/exists-multiple" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["username", "email", "nonexistent_key"]
         }'
```

## 10. DELETE - 删除键

### 删除单个键
```bash
curl -X DELETE "http://localhost:8000/redis/string/delete" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["username"]
         }'
```

### 批量删除多个键
```bash
curl -X DELETE "http://localhost:8000/redis/string/delete" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["user:1:name", "user:1:email", "user:2:name", "user:2:email"]
         }'
```

## 11. INCR - 递增键值

### 基本用法
```bash
# 递增计数器
curl -X POST "http://localhost:8000/redis/string/incr" \
     -H "Content-Type: application/json" \
     -d '{"key": "page_views"}'
```

### 递增并设置过期时间
```bash
# 递增临时计数器
curl -X POST "http://localhost:8000/redis/string/incr" \
     -H "Content-Type: application/json" \
     -d '{"key": "temp_counter", "expire": 60}'
```

## 12. DECR - 递减键值

### 基本用法
```bash
# 递减计数器
curl -X POST "http://localhost:8000/redis/string/decr" \
     -H "Content-Type: application/json" \
     -d '{"key": "remaining_items"}'
```

### 递减并设置过期时间
```bash
# 递减临时计数器
curl -X POST "http://localhost:8000/redis/string/decr" \
     -H "Content-Type: application/json" \
     -d '{"key": "temp_counter", "expire": 60}'
```

## 13. INCRBY - 按指定值递增

### 基本用法
```bash
# 按指定值递增
curl -X POST "http://localhost:8000/redis/string/incrby" \
     -H "Content-Type: application/json" \
     -d '{"key": "score", "increment": 100}'
```

### 递增并设置过期时间
```bash
# 按指定值递增并设置过期时间
curl -X POST "http://localhost:8000/redis/string/incrby" \
     -H "Content-Type: application/json" \
     -d '{"key": "temp_score", "increment": 50, "expire": 300}'
```

## 14. DECRBY - 按指定值递减

### 基本用法
```bash
# 按指定值递减
curl -X POST "http://localhost:8000/redis/string/decrby" \
     -H "Content-Type: application/json" \
     -d '{"key": "balance", "decrement": 25}'
```

### 递减并设置过期时间
```bash
# 按指定值递减并设置过期时间
curl -X POST "http://localhost:8000/redis/string/decrby" \
     -H "Content-Type: application/json" \
     -d '{"key": "temp_balance", "decrement": 10, "expire": 300}'
```

## 实际应用场景示例

### 场景1: 用户会话管理
```bash
# 创建会话
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "session:abc123", "value": {"user_id": 123, "username": "john_doe"}, "expire": 3600}'

# 检查会话是否存在
curl "http://localhost:8000/redis/string/exists?key=session:abc123"

# 获取会话信息
curl "http://localhost:8000/redis/string/get?key=session:abc123"

# 延长会话过期时间
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "session:abc123", "value": {"user_id": 123, "username": "john_doe"}, "expire": 7200, "xx": true}'

# 删除会话
curl -X DELETE "http://localhost:8000/redis/string/delete" \
     -H "Content-Type: application/json" \
     -d '{"keys": ["session:abc123"]}'
```

### 场景2: 计数器系统
```bash
# 页面浏览计数
curl -X POST "http://localhost:8000/redis/string/incr" \
     -H "Content-Type: application/json" \
     -d '{"key": "page_views:/home", "expire": 86400}'

# 获取当前计数
curl "http://localhost:8000/redis/string/get?key=page_views:/home"

# 用户积分增加
curl -X POST "http://localhost:8000/redis/string/incrby" \
     -H "Content-Type: application/json" \
     -d '{"key": "user_points:123", "increment": 10}'

# 商品库存减少
curl -X POST "http://localhost:8000/redis/string/decrby" \
     -H "Content-Type: application/json" \
     -d '{"key": "product_stock:sku123", "decrement": 1}'
```

### 场景3: 分布式锁
```bash
# 获取锁 (30秒过期)
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "lock:resource1", "value": "process_id_12345", "expire": 30, "nx": true}'

# 检查是否获得锁
curl "http://localhost:8000/redis/string/exists?key=lock:resource1"

# 释放锁
curl -X DELETE "http://localhost:8000/redis/string/delete" \
     -H "Content-Type: application/json" \
     -d '{"keys": ["lock:resource1"]}'
```

### 场景4: 缓存系统
```bash
# 设置缓存数据
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "cache:user:123", "value": {"name": "John", "email": "john@example.com"}, "expire": 300}'

# 获取缓存数据
curl "http://localhost:8000/redis/string/get?key=cache:user:123"

# 更新缓存但保持原有过期时间
curl -X POST "http://localhost:8000/redis/string/set" \
     -H "Content-Type: application/json" \
     -d '{"key": "cache:user:123", "value": {"name": "John Doe", "email": "john@example.com"}, "keep_ttl": true}'

# 批量检查缓存是否存在
curl -X POST "http://localhost:8000/redis/string/exists-multiple" \
     -H "Content-Type: application/json" \
     -d '{"keys": ["cache:user:123", "cache:user:456", "cache:user:789"]}'
```