# Redis List API 使用示例

本文档提供了 `/redis/list` 路由下所有 API 方法的详细使用示例。

## 1. LPUSH - 将一个或多个值插入到列表头部

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/list/lpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "values": ["value1", "value2", "value3"]
         }'
```

### 插入复杂数据类型
```bash
curl -X POST "http://localhost:8000/redis/list/lpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user_actions",
           "values": [
             {"action": "login", "timestamp": 1623456789},
             {"action": "view_page", "timestamp": 1623456795}
           ]
         }'
```

## 2. RPUSH - 将一个或多个值插入到列表尾部

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/list/rpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "values": ["value1", "value2", "value3"]
         }'
```

## 3. LLEN - 获取列表长度

### 基本用法
```bash
curl "http://localhost:8000/redis/list/llen?name=mylist"
```

### 空列表
```bash
curl "http://localhost:8000/redis/list/llen?name=empty_list"
```

## 4. LINDEX - 获取列表中指定索引的元素

### 获取第一个元素
```bash
curl "http://localhost:8000/redis/list/lindex?name=mylist&index=0"
```

### 获取最后一个元素
```bash
curl "http://localhost:8000/redis/list/lindex?name=mylist&index=-1"
```

### 获取中间元素
```bash
curl "http://localhost:8000/redis/list/lindex?name=mylist&index=2"
```

## 5. LSET - 设置列表中指定索引的元素值

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/list/lset" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "index": 0,
           "value": "new_value"
         }'
```

## 6. LRANGE - 获取列表中指定范围的元素

### 获取所有元素
```bash
curl "http://localhost:8000/redis/list/lrange?name=mylist&start=0&end=-1"
```

### 获取前3个元素
```bash
curl "http://localhost:8000/redis/list/lrange?name=mylist&start=0&end=2"
```

### 获取最后3个元素
```bash
curl "http://localhost:8000/redis/list/lrange?name=mylist&start=-3&end=-1"
```

## 7. LPUSHX - 仅当列表存在时，将值插入到列表头部

### 列表存在时插入
```bash
curl -X POST "http://localhost:8000/redis/list/lpushx" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "value": "new_value"
         }'
```

## 8. RPUSHX - 仅当列表存在时，将值插入到列表尾部

### 列表存在时插入
```bash
curl -X POST "http://localhost:8000/redis/list/rpushx" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "value": "new_value"
         }'
```

## 9. LINSERT - 在列表中指定元素的前后插入元素

### 在指定元素前插入
```bash
curl -X POST "http://localhost:8000/redis/list/linsert" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "position": "BEFORE",
           "pivot": "existing_value",
           "value": "new_value"
         }'
```

### 在指定元素后插入
```bash
curl -X POST "http://localhost:8000/redis/list/linsert" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "position": "AFTER",
           "pivot": "existing_value",
           "value": "new_value"
         }'
```

## 10. LPOP - 移除并返回列表的第一个元素

### 移除并返回单个元素
```bash
curl -X POST "http://localhost:8000/redis/list/lpop" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist"
         }'
```

### 批量移除并返回多个元素
```bash
curl -X POST "http://localhost:8000/redis/list/lpop" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "count": 3
         }'
```

## 11. RPOP - 移除并返回列表的最后一个元素

### 移除并返回单个元素
```bash
curl -X POST "http://localhost:8000/redis/list/rpop" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist"
         }'
```

### 批量移除并返回多个元素
```bash
curl -X POST "http://localhost:8000/redis/list/rpop" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "count": 3
         }'
```

## 12. BLPOP - 移除并返回第一个非空列表的第一个元素（阻塞式）

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/list/blpop" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["list1", "list2", "list3"],
           "timeout": 10
         }'
```

## 13. BRPOP - 移除并返回第一个非空列表的最后一个元素（阻塞式）

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/list/brpop" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["list1", "list2", "list3"],
           "timeout": 10
         }'
```

## 14. BRPOPLPUSH - 从源列表弹出最后一个元素并推入目标列表头部（阻塞式）

### 基本用法
```bash
curl -X POST "http://localhost:8000/redis/list/brpoplpush" \
     -H "Content-Type: application/json" \
     -d '{
           "source": "source_list",
           "destination": "destination_list",
           "timeout": 10
         }'
```

## 15. LREM - 移除列表中指定值的元素

### 移除前2个匹配的元素
```bash
curl -X POST "http://localhost:8000/redis/list/lrem" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "count": 2,
           "value": "value_to_remove"
         }'
```

### 移除后2个匹配的元素
```bash
curl -X POST "http://localhost:8000/redis/list/lrem" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "count": -2,
           "value": "value_to_remove"
         }'
```

### 移除所有匹配的元素
```bash
curl -X POST "http://localhost:8000/redis/list/lrem" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "count": 0,
           "value": "value_to_remove"
         }'
```

## 16. LTRIM - 修剪列表，只保留指定范围内的元素

### 保留前5个元素
```bash
curl -X POST "http://localhost:8000/redis/list/ltrim" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "start": 0,
           "end": 4
         }'
```

### 保留最后5个元素
```bash
curl -X POST "http://localhost:8000/redis/list/ltrim" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "mylist",
           "start": -5,
           "end": -1
         }'
```

## 实际应用场景示例

### 场景1: 消息队列
```bash
# 生产者：向队列中添加消息
curl -X POST "http://localhost:8000/redis/list/rpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "message_queue",
           "values": [
             {"id": 1, "content": "Hello World"},
             {"id": 2, "content": "Redis is awesome"}
           ]
         }'

# 消费者：从队列中取出消息进行处理
curl -X POST "http://localhost:8000/redis/list/lpop" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "message_queue"
         }'

# 查看队列长度
curl "http://localhost:8000/redis/list/llen?name=message_queue"
```

### 场景2: 最新N条记录缓存
```bash
# 添加新记录
curl -X POST "http://localhost:8000/redis/list/lpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "latest_logs",
           "values": ["Log entry 1"]
         }'

# 保持只缓存最新的100条记录
curl -X POST "http://localhost:8000/redis/list/ltrim" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "latest_logs",
           "start": 0,
           "end": 99
         }'

# 获取最新的10条记录
curl "http://localhost:8000/redis/list/lrange?name=latest_logs&start=0&end=9"
```

### 场景3: 社交网络时间线
```bash
# 用户发布新动态
curl -X POST "http://localhost:8000/redis/list/lpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:123:timeline",
           "values": [{
             "id": 1001,
             "content": "Just had a great coffee!",
             "timestamp": 1623456789
           }]
         }'

# 限制时间线只保留最近的50条动态
curl -X POST "http://localhost:8000/redis/list/ltrim" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "user:123:timeline",
           "start": 0,
           "end": 49
         }'

# 获取用户的前10条动态
curl "http://localhost:8000/redis/list/lrange?name=user:123:timeline&start=0&end=9"
```

### 场景4: 任务队列
```bash
# 添加任务到队列
curl -X POST "http://localhost:8000/redis/list/rpush" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "task_queue",
           "values": [
             {"task_id": "task_001", "type": "email", "payload": "send_welcome_email"},
             {"task_id": "task_002", "type": "notification", "payload": "send_push_notification"}
           ]
         }'

# 工作进程获取任务（阻塞式）
curl -X POST "http://localhost:8000/redis/list/brpop" \
     -H "Content-Type: application/json" \
     -d '{
           "keys": ["task_queue"],
           "timeout": 30
         }'

# 查看剩余任务数量
curl "http://localhost:8000/redis/list/llen?name=task_queue"
```