// mock-server.js
const express = require('express');
const bodyParser = require('body-parser');
const crypto = require('crypto');

const app = express();
const PORT = 4523;

// 中间件
app.use(bodyParser.json());
// CORS 支持，允许所有来源跨域访问
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type,Authorization');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// 模拟数据库（内存存储）
const users = [];
const tokens = [];

// 工具函数
const generateToken = (payload) => {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64');
  const payloadStr = Buffer.from(JSON.stringify(payload)).toString('base64');
  const signature = crypto.createHmac('sha256', 'secret-key')
    .update(`${header}.${payloadStr}`)
    .digest('base64');
  return `${header}.${payloadStr}.${signature}`;
};

const verifyToken = (token) => {
  try {
    const [header, payload, signature] = token.split('.');
    const expectedSignature = crypto.createHmac('sha256', 'secret-key')
      .update(`${header}.${payload}`)
      .digest('base64');
    
    if (signature !== expectedSignature) {
      return null;
    }
    
    const payloadData = JSON.parse(Buffer.from(payload, 'base64').toString());
    return payloadData;
  } catch (error) {
    return null;
  }
};

const encryptPassword = (password) => {
  return crypto.createHash('sha256').update(password).digest('hex');
};

const findUserByEmail = (email) => {
  return users.find(user => user.email === email);
};

const findUserById = (id) => {
  return users.find(user => user.user_id === id);
};

const generateUserId = () => {
  return users.length > 0 ? Math.max(...users.map(u => u.user_id)) + 1 : 1;
};

// 中间件：验证Token
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({
      code: 401,
      message: '未提供认证令牌'
    });
  }

  const payload = verifyToken(token);
  if (!payload) {
    return res.status(401).json({
      code: 401,
      message: '无效的认证令牌'
    });
  }

  const user = findUserById(payload.user_id);
  if (!user) {
    return res.status(401).json({
      code: 401,
      message: '用户不存在'
    });
  }

  req.user = user;
  next();
};

// 1. 用户注册接口
app.post('/m1/7397469-7130026-default/auth/register', (req, res) => {
  try {
    console.log('【注册】收到请求数据:', JSON.stringify(req.body, null, 2));
    const { email, password, nickname, student_id } = req.body;

    // 验证必填字段
    if (!email || !password || !nickname) {
      return res.status(400).json({
        code: 400,
        message: '邮箱、密码和昵称为必填字段'
      });
    }

    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return res.status(400).json({
        code: 400,
        message: '邮箱格式不正确'
      });
    }

    // 验证密码长度
    if (password.length < 6) {
      return res.status(400).json({
        code: 400,
        message: '密码长度不能少于6位'
      });
    }

    // 验证昵称长度
    if (nickname.length < 1 || nickname.length > 20) {
      return res.status(400).json({
        code: 400,
        message: '昵称长度必须在1-20个字符之间'
      });
    }

    // 检查邮箱是否已存在
    if (findUserByEmail(email)) {
      return res.status(400).json({
        code: 400,
        message: '该邮箱已被注册'
      });
    }

    // 创建新用户
    const newUser = {
      user_id: generateUserId(),
      email,
      password: encryptPassword(password), // 存储加密后的密码
      nickname,
      student_id: student_id || null,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${email}`,
      created_at: new Date().toISOString()
    };

    users.push(newUser);

    // 生成token
    const tokenPayload = {
      user_id: newUser.user_id,
      email: newUser.email,
      exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1小时过期
    };

    const access_token = generateToken(tokenPayload);
    const refresh_token = generateToken({
      user_id: newUser.user_id,
      type: 'refresh',
      exp: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60) // 7天过期
    });

    // 存储token
    tokens.push({
      user_id: newUser.user_id,
      access_token,
      refresh_token,
      created_at: new Date().toISOString()
    });

    const resp = {
      code: 200,
      message: '注册成功',
      data: {
        user_id: newUser.user_id,
        email: newUser.email,
        nickname: newUser.nickname,
        avatar: newUser.avatar,
        token: access_token,
        refresh_token: refresh_token
      }
    };
    console.log('【注册】发送响应数据:', JSON.stringify(resp, null, 2));
    res.json(resp);

  } catch (error) {
    console.error('注册错误:', error);
    res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
});

// 2. 用户登录接口
app.post('/m1/7397469-7130026-default/auth/login', (req, res) => {
  try {
    console.log('【登录】收到请求数据:', JSON.stringify(req.body, null, 2));
    const { email, password } = req.body;

    // 验证必填字段
    if (!email || !password) {
      return res.status(400).json({
        code: 400,
        message: '邮箱和密码为必填字段'
      });
    }

    // 查找用户
    const user = findUserByEmail(email);
    if (!user) {
      return res.status(400).json({
        code: 400,
        message: '邮箱或密码错误'
      });
    }

    // 验证密码
    const encryptedPassword = encryptPassword(password);
    if (user.password !== encryptedPassword) {
      return res.status(400).json({
        code: 400,
        message: '邮箱或密码错误'
      });
    }

    // 生成token
    const tokenPayload = {
      user_id: user.user_id,
      email: user.email,
      exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1小时过期
    };

    const access_token = generateToken(tokenPayload);
    const refresh_token = generateToken({
      user_id: user.user_id,
      type: 'refresh',
      exp: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60) // 7天过期
    });

    // 更新token存储
    const existingTokenIndex = tokens.findIndex(t => t.user_id === user.user_id);
    if (existingTokenIndex !== -1) {
      tokens[existingTokenIndex] = {
        user_id: user.user_id,
        access_token,
        refresh_token,
        created_at: new Date().toISOString()
      };
    } else {
      tokens.push({
        user_id: user.user_id,
        access_token,
        refresh_token,
        created_at: new Date().toISOString()
      });
    }

    const resp = {
      code: 200,
      message: '登录成功',
      data: {
        user_id: user.user_id,
        email: user.email,
        nickname: user.nickname,
        avatar: user.avatar,
        token: access_token,
        refresh_token: refresh_token
      }
    };
    console.log('【登录】发送响应数据:', JSON.stringify(resp, null, 2));
    res.json(resp);

  } catch (error) {
    console.error('登录错误:', error);
    res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
});

// 3. 退出登录接口
app.post('/m1/7397469-7130026-default/auth/logout', authenticateToken, (req, res) => {
  try {
    console.log('【退出登录】收到请求头:', JSON.stringify(req.headers, null, 2));
    const userId = req.user.user_id;
    
    // 移除用户的token
    const tokenIndex = tokens.findIndex(t => t.user_id === userId);
    if (tokenIndex !== -1) {
      tokens.splice(tokenIndex, 1);
    }

    const resp = {
      code: 200,
      message: '退出登录成功',
      data: {}
    };
    console.log('【退出登录】发送响应数据:', JSON.stringify(resp, null, 2));
    res.json(resp);

  } catch (error) {
    console.error('退出登录错误:', error);
    res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
});

// 4. 刷新令牌接口
app.post('/m1/7397469-7130026-default/auth/refresh', (req, res) => {
  try {
    console.log('【刷新令牌】收到请求数据:', JSON.stringify(req.body, null, 2));
    const { refresh_token } = req.body;

    if (!refresh_token) {
      return res.status(400).json({
        code: 400,
        message: '刷新令牌为必填字段'
      });
    }

    // 验证刷新令牌
    const payload = verifyToken(refresh_token);
    if (!payload || payload.type !== 'refresh') {
      return res.status(401).json({
        code: 401,
        message: '无效的刷新令牌'
      });
    }

    // 查找用户
    const user = findUserById(payload.user_id);
    if (!user) {
      return res.status(401).json({
        code: 401,
        message: '用户不存在'
      });
    }

    // 检查刷新令牌是否存在
    const tokenRecord = tokens.find(t => t.user_id === user.user_id && t.refresh_token === refresh_token);
    if (!tokenRecord) {
      return res.status(401).json({
        code: 401,
        message: '刷新令牌无效'
      });
    }

    // 生成新的访问令牌
    const newTokenPayload = {
      user_id: user.user_id,
      email: user.email,
      exp: Math.floor(Date.now() / 1000) + (60 * 60) // 1小时过期
    };

    const new_access_token = generateToken(newTokenPayload);

    // 更新token存储
    tokenRecord.access_token = new_access_token;
    tokenRecord.created_at = new Date().toISOString();

    const resp = {
      code: 200,
      message: '令牌刷新成功',
      data: {
        access_token: new_access_token,
        refresh_token: refresh_token, // 返回原刷新令牌（可根据需求生成新的）
        expires_in: 7200,
        token_type: 'Bearer'
      }
    };
    console.log('【刷新令牌】发送响应数据:', JSON.stringify(resp, null, 2));
    res.json(resp);

  } catch (error) {
    console.error('刷新令牌错误:', error);
    res.status(500).json({
      code: 500,
      message: '服务器内部错误'
    });
  }
});

// 健康检查接口
app.get('/m1/7397469-7130026-default/health', (req, res) => {
  res.json({
    code: 200,
    message: '服务运行正常',
    data: {
      server: 'Mock Authentication Server',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      users_count: users.length,
      tokens_count: tokens.length
    }
  });
});

// 获取用户列表（仅用于调试）
app.get('/m1/7397469-7130026-default/debug/users', (req, res) => {
  // 移除密码字段
  const usersWithoutPassword = users.map(user => {
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  });
  
  res.json({
    code: 200,
    message: '用户列表',
    data: {
      users: usersWithoutPassword,
      tokens: tokens
    }
  });
});

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error('未处理的错误:', err);
  res.status(500).json({
    code: 500,
    message: '服务器内部错误'
  });
});

// 404处理（兼容express 4.19+，不能用'*'）
app.use((req, res) => {
  res.status(404).json({
    code: 404,
    message: '接口不存在'
  });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🚀 Mock认证服务器已启动`);
  console.log(`📍 服务地址: http://localhost:${PORT}`);
  console.log(`📚 可用接口:`);
  console.log(`   POST /auth/register - 用户注册`);
  console.log(`   POST /auth/login    - 用户登录`);
  console.log(`   POST /auth/logout   - 退出登录`);
  console.log(`   POST /auth/refresh  - 刷新令牌`);
  console.log(`   GET  /health        - 健康检查`);
  console.log(`   GET  /debug/users   - 调试用户列表`);
  console.log('\n💡 提示: 数据存储在内存中，重启服务器会丢失所有数据');
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n👋 正在关闭服务器...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 正在关闭服务器...');
  process.exit(0);
});