# 时光胶囊项目 - 前端API接口文档

## 目录

1. [用户认证相关接口](#用户认证相关接口)
2. [用户信息相关接口](#用户信息相关接口)
3. [胶囊相关接口](#胶囊相关接口)
4. [地图相关接口](#地图相关接口)
5. [活动相关接口](#活动相关接口)
6. [中枢页相关接口](#中枢页相关接口)

## 用户认证相关接口

### 发送邮箱验证码

**请求方法**: POST
**请求路径**: `/auth/send-code`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| --- | --- | --- | --- |
| email | String | 是 | 目标邮箱 |
| type | String | 是 | 验证码类型（register/forgot） |

**响应格式**:
```json
{
  "code": 200,
  "message": "验证码发送成功",
  "data": {}
}
```

### 邮箱注册

**请求方法**: POST
**请求路径**: `/auth/register`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| email | String | 是 | 邮箱 |
| code | String | 是 | 验证码 |
| password | String | 是 | 密码 |
| nickname | String | 否 | 昵称 |

**响应格式**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "token": "jwt_token",
    "userInfo": {
      "id": "user_id",
      "email": "user@example.com",
      "nickname": "用户昵称",
      "avatar": "avatar_url",
      "role": "user"
    }
  }
}
```

### 邮箱登录

**请求方法**: POST
**请求路径**: `/auth/login`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| email | String | 是 | 邮箱 |
| password | String | 是 | 密码 |

**响应格式**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "jwt_token",
    "userInfo": {
      "id": "user_id",
      "email": "user@example.com",
      "nickname": "用户昵称",
      "avatar": "avatar_url",
      "role": "user"
    }
  }
}
```

### 发送找回密码邮件

**请求方法**: POST
**请求路径**: `/auth/forgot`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| email | String | 是 | 邮箱 |

**响应格式**:
```json
{
  "code": 200,
  "message": "重置密码邮件已发送",
  "data": {}
}
```

### 重置密码

**请求方法**: POST
**请求路径**: `/auth/reset`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| email | String | 是 | 邮箱 |
| code | String | 是 | 验证码 |
| newPassword | String | 是 | 新密码 |

**响应格式**:
```json
{
  "code": 200,
  "message": "密码重置成功",
  "data": {}
}
```

## 用户信息相关接口

### 获取用户信息

**请求方法**: GET
**请求路径**: `/api/user/{userId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| userId | String | 是 | 用户ID |

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "user_id",
    "email": "user@example.com",
    "nickname": "用户昵称",
    "avatar": "avatar_url"
  }
}
```

## 胶囊相关接口

### 创建胶囊

**请求方法**: POST
**请求路径**: `/capsule/create`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| title | String | 是 | 胶囊标题 |
| content | String | 是 | 胶囊内容 |
| visibility | String | 是 | 可见性（public/private/friend） |
| tags | Array | 否 | 标签列表 |
| location | String | 否 | 地点描述 |
| lat | Number | 否 | 纬度 |
| lng | Number | 否 | 经度 |
| createTime | String | 否 | 创建时间 |
| updateTime | String | 否 | 更新时间 |
| imageUrl | String | 否 | 图片URL |

**响应格式**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": "capsule_id",
    "title": "胶囊标题",
    "content": "胶囊内容",
    ...
  }
}
```

### 获取我的胶囊列表

**请求方法**: GET
**请求路径**: `/capsule/my`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| userId | String | 否 | 用户ID（可选，后端自动识别当前用户） |
| page | Number | 否 | 页码 |
| size | Number | 否 | 每页数量 |

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "list": [
      {
        "id": "capsule_id",
        "title": "胶囊标题",
        "content": "胶囊内容",
        "visibility": "public",
        "tags": ["标签1", "标签2"],
        "createTime": "2024-01-01T00:00:00",
        "likes": 10,
        "views": 100
      },
      ...
    ],
    "total": 20
  }
}
```

### 获取单个胶囊详情

**请求方法**: GET
**请求路径**: `/capsule/detail/{capsuleId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| capsuleId | String/Number | 是 | 胶囊ID |

**响应格式**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": "capsule_id",
    "title": "胶囊标题",
    "content": "胶囊内容",
    "visibility": "public",
    "tags": ["标签1", "标签2"],
    "location": "地点描述",
    "lat": 39.9042,
    "lng": 116.4074,
    "createTime": "2024-01-01T00:00:00",
    "imageUrl": "image_url",
    "likes": 10,
    "views": 100,
    "user": {
      "id": "user_id",
      "nickname": "用户昵称",
      "avatar": "avatar_url"
    }
  }
}
```

### 编辑胶囊

**请求方法**: POST
**请求路径**: `/capsule/edit/{capsuleId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| capsuleId | String/Number | 是 | 胶囊ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| title | String | 否 | 胶囊标题 |
| content | String | 否 | 胶囊内容 |
| visibility | String | 否 | 可见性 |
| tags | Array | 否 | 标签列表 |
| location | String | 否 | 地点描述 |
| lat | Number | 否 | 纬度 |
| lng | Number | 否 | 经度 |
| imageUrl | String | 否 | 图片URL |

**响应格式**:
```json
{
  "code": 200,
  "message": "编辑成功",
  "data": {
    "id": "capsule_id",
    "title": "更新后的标题",
    ...
  }
}
```

### 删除胶囊

**请求方法**: POST
**请求路径**: `/capsule/delete/{capsuleId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| capsuleId | String/Number | 是 | 胶囊ID |

**响应格式**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": {}
}
```

### 上传胶囊图片

**请求方法**: POST
**请求路径**: `/capsule/upload-img`
**请求参数**: 表单数据

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| img | File | 是 | 图片文件 |

**响应格式**:
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "url": "uploaded_image_url"
  }
}
```

## 地图相关接口

### 获取胶囊地理标记数据

**请求方法**: GET
**请求路径**: `/map/capsule-markers`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| lat | Number | 否 | 纬度 |
| lng | Number | 否 | 经度 |
| range | Number | 否 | 范围（米） |

**响应格式**:
```json
[
  {
    "id": 1,
    "title": "胶囊标题",
    "lat": 39.900820,
    "lng": 116.301950,
    "time": "2024-06-15T22:30:00",
    "vis": "public",
    "desc": "胶囊描述",
    "tags": ["标签1", "标签2"],
    "likes": 42,
    "views": 328,
    "location": "地点描述",
    "distance": "100m",
    "img": "image_url",
    "unlockType": "location"
  },
  ...
]
```

### 获取热力图数据

**请求方法**: GET
**请求路径**: `/map/heatmap-data`

**响应格式**:
```json
[
  [116.302, 39.9005, 10],
  [116.303, 39.901, 5],
  ...
]
```

## 活动相关接口

### 获取校园活动列表

**请求方法**: GET
**请求路径**: `/events/list`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| page | Number | 否 | 页码，默认1 |
| size | Number | 否 | 每页数量，默认10 |
| keyword | String | 否 | 关键词搜索 |

**响应格式**:
```json
[
  {
    "id": "event_id",
    "name": "活动名称",
    "date": "2024-01-01T10:00:00",
    "description": "活动描述",
    "tags": ["标签1", "标签2"],
    "cover_img": "cover_image_url",
    "location": "活动地点",
    "participant_count": 50
  },
  ...
]
```

### 获取活动详情

**请求方法**: GET
**请求路径**: `/events/detail/{eventId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| eventId | String/Number | 是 | 活动ID |

**响应格式**:
```json
{
  "id": "event_id",
  "name": "活动名称",
  "time": "2024-01-01T10:00:00",
  "description": "活动描述",
  "tags": ["标签1", "标签2"],
  "coverImg": "cover_image_url",
  "location": "活动地点",
  "participantCount": 50,
  "isRegistered": false
}
```

### 报名活动

**请求方法**: POST
**请求路径**: `/events/register/{eventId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| eventId | String/Number | 是 | 活动ID |

**响应格式**:
```json
{
  "code": 200,
  "message": "报名成功",
  "data": {}
}
```

### 取消报名

**请求方法**: POST
**请求路径**: `/events/cancel/{eventId}`
**路径参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| eventId | String/Number | 是 | 活动ID |

**响应格式**:
```json
{
  "code": 200,
  "message": "取消报名成功",
  "data": {}
}
```

### 获取我的已报名活动

**请求方法**: GET
**请求路径**: `/events/my-registered`
**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| page | Number | 否 | 页码，默认1 |
| size | Number | 否 | 每页数量，默认10 |

**响应格式**:
```json
{
  "list": [
    {
      "id": "event_id",
      "name": "活动名称",
      "time": "2024-01-01T10:00:00",
      "description": "活动描述",
      "tags": ["标签1", "标签2"],
      "coverImg": "cover_image_url",
      "location": "活动地点",
      "participantCount": 50,
      "isRegistered": true
    },
    ...
  ],
  "total": 10
}
```

## 中枢页相关接口

### 获取用户基础信息

**请求方法**: GET
**请求路径**: `/hub/user-info`

**响应格式**:
```json
{
  "id": "u_1001",
  "name": "用户名",
  "avatar": "avatar_url",
  "stats": {
    "totalCapsules": 12,
    "pendingCapsules": 3,
    "followers": 128,
    "activeToday": 124
  },
  "bio": "个人简介"
}
```

### 获取附近胶囊列表

**请求方法**: GET
**请求路径**: `/hub/nearby-capsules`
**请求参数**:


| 参数名 | 类型 | 必填 | 描述 |
| :--- | :--- | :--- | :--- |
| lat | Number | 否 | 纬度 |
| lng | Number | 否 | 经度 |
| range | Number | 否 | 范围（米） |

**响应格式**:
```json
[
  {
    "id": "c_2001",
    "title": "胶囊标题",
    "time": "2024-06-15T22:30:00",
    "vis": "public",
    "desc": "胶囊描述",
    "tags": ["标签1", "标签2"],
    "likes": 42,
    "views": 328,
    "location": "地点描述",
    "distance": "28m",
    "img": "image_url",
    "unlockType": "location"
  },
  ...
]
```

### 获取最近用户动态

**请求方法**: GET
**请求路径**: `/hub/recent-activities`

**响应格式**:
```json
[
  {
    "id": "act_4001",
    "time": "2024-10-24T14:30:00",
    "type": "activity_type",
    "content": "活动内容"
  },
  ...
]
```

## API工具类

前端使用 `request.js` 作为统一的请求工具，封装了 axios 实例，支持全局拦截和错误处理。所有API请求都通过该工具发起。