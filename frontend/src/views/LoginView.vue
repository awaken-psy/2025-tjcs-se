<template>
  <div class="wrap">
    <!-- 左侧：品牌介绍卡片（BrandCard） -->
    <section class="card brand-card">
      <div
        class="shape-top"
        aria-hidden
      />
      <div
        class="shape-btm"
        aria-hidden
      />
      
      <div class="logo-wrap">
        <div class="logo">
          时光
        </div>
        <div>
          <h1>时光胶囊 · 校园</h1>
          <div class="small muted">
            把校园记忆放进时间与地点里，让未来的你遇见过去的自己
          </div>
        </div>
      </div>

      <p class="lead">
        欢迎使用「时光胶囊·校园」！请登录或注册，开启你的时光之旅。
      </p>
      <div class="feature-list">
        <div>
          <div class="feature-title">
            设计风格
          </div>
          <div class="muted">
            清新渐变、立体卡片、柔和阴影
          </div>
        </div>
        <div>
          <div class="feature-title">
            产品理念
          </div>
          <div class="muted">
            记录、分享、遇见更好的自己
          </div>
        </div>
      </div>
      <div class="map-section">
        <div class="feature-title">
          地图预览
        </div>
        <div class="map-preview">
          校园地图功能即将上线
        </div>
      </div>
      <div class="footer">
        同济大学 2025
      </div>
    </section>

    <!-- 右侧：登录注册卡片（AuthCard） -->
    <section
      class="card auth-card pulse"
      aria-labelledby="auth-heading"
    >
      <div class="auth-header">
        <div>
          <div
            id="auth-heading"
            class="auth-title"
          >
            登录或注册
          </div>
          <div class="auth-subtitle">
            使用校园邮箱登录或注册
          </div>
        </div>
        <div class="links">
          <a
            href="#"
            @click.prevent="openModal('privacy')"
          >隐私政策</a>
          <a
            href="#"
            @click.prevent="openModal('service')"
          >服务条款</a>
        </div>
      </div>

      <!-- 登录/注册标签页（AuthTabs） -->
      <div
        class="tabs"
        role="tablist"
      >
        <button 
          id="tab-login" 
          class="tab" 
          :class="{ active: activeTab === 'login' }" 
          role="tab" 
          :aria-selected="activeTab === 'login'"
          @click="switchToLogin"
        >
          登录
        </button>
        <button 
          id="tab-register" 
          class="tab" 
          :class="{ active: activeTab === 'register' }" 
          role="tab" 
          :aria-selected="activeTab === 'register'"
          @click="switchToRegister"
        >
          注册
        </button>
      </div>

      <!-- 登录表单（LoginForm） -->
      <form 
        v-if="activeTab === 'login'" 
        id="login-form" 
        class="form" 
        autocomplete="on"
        @submit.prevent="handleLogin"
      >
        <div class="field">
          <label for="login-email">邮箱</label>
          <input 
            id="login-email" 
            v-model="loginForm.email" 
            type="email"
            :class="{ 'input-error': formErrors.login.email }"
            placeholder="user@example.com" 
            required
          >
          <p
            v-if="formErrors.login.email"
            class="error-tip"
          >
            {{ formErrors.login.email }}
          </p>
        </div>
        
        <div class="field">
          <label for="login-pw">密码</label>
          <input 
            id="login-pw" 
            v-model="loginForm.password" 
            type="password"
            :class="{ 'input-error': formErrors.login.password }"
            placeholder="请输入密码" 
            required
          >
          <p
            v-if="formErrors.login.password"
            class="error-tip"
          >
            {{ formErrors.login.password }}
          </p>
        </div>
        
        <div class="helper">
          <a
            href="#"
            @click.prevent="openModal('forgot')"
          >忘记密码？</a>
          <a
            href="#"
            title="游客模式"
            @click.prevent="handleGuestLogin"
          >以游客身份体验</a>
        </div>
        
        <div class="btn-group">
          <button 
            id="login-btn" 
            class="btn primary"
            :disabled="isLoading"
          >
            <span
              v-if="isLoading"
              class="loading-spinner small"
            />
            <span>{{ isLoading ? '登录中...' : '登录' }}</span>
          </button>
          <button 
            id="to-register" 
            class="btn ghost"
            @click.prevent="switchToRegister"
          >
            注册
          </button>
        </div>

        <div class="example">
          <div>演示账号：</div>
          <div class="demo-account">
            邮箱：demo@univ.edu<br>密码：123456
          </div>
        </div>
      </form>

      <!-- 注册表单（RegisterForm） -->
      <form 
        v-else 
        id="register-form" 
        class="form" 
        autocomplete="on"
        @submit.prevent="handleRegister"
      >
        <div class="field">
          <label for="reg-email">校内邮箱</label>
          <input 
            id="reg-email" 
            v-model="regForm.email" 
            type="email"
            :class="{ 'input-error': formErrors.reg.email }"
            placeholder="your@univ.edu" 
            required
          >
          <p
            v-if="formErrors.reg.email"
            class="error-tip"
          >
            {{ formErrors.reg.email }}
          </p>
        </div>
        
        <div class="field">
          <label for="reg-pw">设置密码</label>
          <input 
            id="reg-pw" 
            v-model="regForm.password" 
            type="password"
            :class="{ 'input-error': formErrors.reg.password }"
            placeholder="至少6位" 
            required
          >
          <p
            v-if="formErrors.reg.password"
            class="error-tip"
          >
            {{ formErrors.reg.password }}
          </p>
        </div>
        
        <div class="field">
          <label for="reg-pw2">确认密码</label>
          <input 
            id="reg-pw2" 
            v-model="regForm.password2" 
            type="password"
            :class="{ 'input-error': formErrors.reg.password2 }"
            placeholder="再次输入密码" 
            required
          >
          <p
            v-if="formErrors.reg.password2"
            class="error-tip"
          >
            {{ formErrors.reg.password2 }}
          </p>
        </div>
        
        <div class="field">
          <label for="reg-nick">昵称</label>
          <input 
            id="reg-nick" 
            v-model="regForm.nickname" 
            type="text"
            :class="{ 'input-error': formErrors.reg.nickname }"
            placeholder="你的昵称（1-20个字符）"
            required
          >
          <p
            v-if="formErrors.reg.nickname"
            class="error-tip"
          >
            {{ formErrors.reg.nickname }}
          </p>
        </div>

        <div class="field">
          <label for="reg-student-id">学号（可选）</label>
          <input
            id="reg-student-id"
            v-model="regForm.student_id"
            type="text"
            placeholder="2024123456"
          >
        </div>

        <div class="field">
          <label for="reg-verify-code">邮箱验证码</label>
          <div class="verify-code-group">
            <input
              id="reg-verify-code"
              v-model="regForm.verify_code"
              type="text"
              :class="{ 'input-error': formErrors.reg.verify_code }"
              placeholder="请输入6位验证码"
              maxlength="6"
              required
            >
            <button
              type="button"
              class="btn verify-btn"
              :disabled="isLoading || !regForm.email || verifyCodeCooldown > 0"
              @click="handleSendVerifyCode"
            >
              {{ verifyCodeCooldown > 0 ? `${verifyCodeCooldown}s后重发` : '发送验证码' }}
            </button>
          </div>
          <p
            v-if="formErrors.reg.verify_code"
            class="error-tip"
          >
            {{ formErrors.reg.verify_code }}
          </p>
        </div>

        <div class="field checkbox">
          <input 
            id="agree" 
            v-model="regForm.agree" 
            type="checkbox"
            :class="{ 'input-error': formErrors.reg.agree }"
          >
          <label
            for="agree"
            class="small"
          >
            我已阅读并同意<a
              href="#"
              @click.prevent="openModal('privacy')"
            >隐私政策</a>
          </label>
          <p
            v-if="formErrors.reg.agree"
            class="error-tip"
          >
            {{ formErrors.reg.agree }}
          </p>
        </div>
        
        <div class="btn-group">
          <button 
            id="reg-btn" 
            class="btn primary"
            :disabled="isLoading"
          >
            <span
              v-if="isLoading"
              class="loading-spinner small"
            />
            <span>{{ isLoading ? '注册中...' : '注册并登录' }}</span>
          </button>
          <button 
            id="to-login" 
            class="btn ghost"
            @click.prevent="switchToLogin"
          >
            返回登录
          </button>
        </div>
      </form>
    </section>
  </div>

  <!-- 权限说明模态框（PermissionModal） -->
  <div 
    v-if="showPermModal" 
    id="perm-modal" 
    class="modal" 
    role="dialog" 
    aria-modal="true"
    aria-labelledby="perm-title"
  >
    <div class="modal-panel small">
      <div class="modal-header">
        <h3 id="perm-title">
          权限说明
        </h3>
        <button
          id="perm-close"
          class="modal-close"
          @click="closeModal('perm')"
        >
          ✕
        </button>
      </div>
      <p class="muted">
        为保障功能体验，系统可能会请求以下权限：
      </p>
      <ul class="perm-list">
        <li>地理位置：用于记录胶囊位置与解锁</li>
        <li>相机 / 麦克风：用于拍照与录音上传</li>
        <li>通知：用于推送胶囊解锁提醒</li>
      </ul>
      <div class="modal-btn-group">
        <button
          id="perm-later"
          class="btn ghost"
          @click="closeModal('perm')"
        >
          稍后再说
        </button>
        <button
          id="perm-accept"
          class="btn primary"
          @click="handlePermissionAccept"
        >
          同意并继续
        </button>
      </div>
    </div>
  </div>

  <!-- 忘记密码模态框（ForgotPasswordModal） -->
  <div 
    v-if="showForgotModal" 
    id="forgot-modal" 
    class="modal" 
    role="dialog" 
    aria-modal="true"
    aria-labelledby="forgot-title"
  >
    <div class="modal-panel small">
      <div class="modal-header">
        <h3 id="forgot-title">
          找回密码
        </h3>
        <button
          id="forgot-close"
          class="modal-close"
          @click="closeModal('forgot')"
        >
          ✕
        </button>
      </div>
      <p class="muted">
        请输入注册邮箱，系统会发送重置指引。
      </p>
      <div
        class="field"
        style="margin: 16px 0"
      >
        <input 
          id="forgot-email" 
          v-model="forgotForm.email" 
          type="email"
          placeholder="your@univ.edu"
        >
      </div>
      <div class="modal-btn-group">
        <button
          id="forgot-cancel"
          class="btn ghost"
          @click="closeModal('forgot')"
        >
          取消
        </button>
        <button
          id="forgot-send"
          class="btn primary"
          @click="handleForgotSend"
        >
          发送重置邮件
        </button>
      </div>
    </div>
  </div>

  <!-- 条款协议模态框（TermsModal） -->
  <div 
    v-if="showPrivacyModal || showServiceModal" 
    id="doc-modal" 
    class="modal" 
    role="dialog" 
    aria-modal="true"
    aria-labelledby="doc-title"
  >
    <div
      v-if="showPrivacyModal"
      class="modal-panel"
    >
      <div class="modal-header">
        <h3 id="doc-title">
          隐私政策
        </h3>
        <button
          id="doc-close"
          class="modal-close"
          @click="closeModal('privacy')"
        >
          ✕
        </button>
      </div>
      <div class="doc-content">
        <h4>一、信息收集与使用</h4>
        <p>我们仅在实现时光胶囊服务所必需的范围内收集您的个人信息，包括但不限于：注册信息（如邮箱、昵称）、地理位置（用于胶囊定位）、多媒体内容（如照片、音频、视频）等。所有信息仅用于产品功能实现，不会用于任何未经授权的用途。</p>
        <h4>二、信息存储与保护</h4>
        <p>您的数据将被加密存储在安全的服务器上，采取严格的访问控制和技术手段防止数据泄露、损毁或被非法访问。我们承诺不会将您的个人信息出售、出租或以其他方式提供给第三方，除非获得您的明确同意或法律法规要求。</p>
        <h4>三、信息共享与披露</h4>
        <p>除非法律法规要求，或为实现产品核心功能（如胶囊分享、好友互动）所必需，我们不会向任何无关第三方披露您的个人信息。涉及第三方服务时，我们会明确告知并征得您的同意。</p>
        <h4>四、用户权利</h4>
        <p>您有权随时访问、更正、导出或删除您的个人信息。如需注销账号或删除全部数据，可通过"个人中心-设置"页面提交申请，我们将在7个工作日内处理。</p>
        <h4>五、隐私政策变更</h4>
        <p>如本政策有重大变更，我们会通过站内通知、弹窗等方式及时告知。继续使用本服务即视为您同意更新后的政策。</p>
      </div>
    </div>
    <div
      v-if="showServiceModal"
      class="modal-panel"
    >
      <div class="modal-header">
        <h3 id="doc-title">
          服务条款
        </h3>
        <button
          id="doc-close2"
          class="modal-close"
          @click="closeModal('service')"
        >
          ✕
        </button>
      </div>
      <div class="doc-content">
        <h4>一、账号注册与使用</h4>
        <p>用户需使用真实、有效的邮箱注册账号，并妥善保管登录凭证。禁止冒用他人身份注册或恶意注册多个账号。</p>
        <h4>二、内容规范</h4>
        <p>请勿上传、发布、传播任何违法、违规、侵权、低俗或不当内容。对于违反规定的内容，平台有权删除并视情节暂停或封禁账号。</p>
        <h4>三、服务变更与中断</h4>
        <p>我们有权根据运营需要对服务内容进行调整、升级或暂停，并提前通过公告等方式通知用户。因不可抗力或第三方原因导致服务中断的，我们将尽力协助恢复，但不承担由此产生的损失责任。</p>
        <h4>四、用户责任</h4>
        <p>用户应对其账号下的所有行为负责，包括但不限于内容发布、互动评论等。因用户自身原因造成的账号泄露、数据丢失等后果由用户自行承担。</p>
        <h4>五、法律适用</h4>
        <p>本服务条款受中华人民共和国相关法律法规管辖。用户在使用过程中如有争议，可通过协商解决，协商不成时可向平台所在地法院提起诉讼。</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/store/user'
import { routeJump } from '@/utils/routeUtils'
import { login, register, sendCode } from '@/api/new/authenticationApi'
import { encryptPassword } from '@/utils/encryptionUtils'

// 初始化依赖
const userStore = useUserStore()

// ===== 状态管理 =====
// 标签页状态（登录/注册）
const activeTab = ref('login')
// 加载状态
const isLoading = ref(false)
// 模态框显示状态
const showPermModal = ref(false)
const showForgotModal = ref(false)
const showPrivacyModal = ref(false)
const showServiceModal = ref(false)

// 表单数据
const loginForm = reactive({
  email: '',
  password: ''
})
const regForm = reactive({
  email: '',
  password: '',
  password2: '',
  nickname: '',
  student_id: '',
  verify_code: '',
  agree: false
})
const forgotForm = reactive({
  email: ''
})

// 表单错误提示
const formErrors = reactive({
  login: { email: '', password: '' },
  reg: { email: '', password: '', password2: '', nickname: '', verify_code: '', agree: '' }
})

// 验证码倒计时
const verifyCodeCooldown = ref(0)

// ===== 页面挂载 =====
onMounted(() => {
  // 已登录用户跳转首页
  if (userStore.isLogin) {
    routeJump('/hubviews')
    return
  }

  // 首次访问显示权限模态框
  if (!sessionStorage.getItem('permShown')) {
    sessionStorage.setItem('permShown', '1')
    setTimeout(() => openModal('perm'), 700)
  }

  // 读取记住的邮箱 - 适配新的存储逻辑
  const savedEmail = localStorage.getItem('saved_login_email')
  if (savedEmail) {
    loginForm.email = savedEmail
  }
})

// ===== 标签页切换 =====
const switchToLogin = () => {
  activeTab.value = 'login'
  // 清空登录表单错误
  formErrors.login.email = ''
  formErrors.login.password = ''
}

const switchToRegister = () => {
  activeTab.value = 'register'
  // 清空注册表单错误
  Object.keys(formErrors.reg).forEach(key => {
    formErrors.reg[key] = ''
  })
}

// ===== 模态框控制 =====
const openModal = (modalType) => {
  if (modalType === 'perm') showPermModal.value = true
  if (modalType === 'forgot') showForgotModal.value = true
  if (modalType === 'privacy') {
    showPrivacyModal.value = true
    showServiceModal.value = false
  }
  if (modalType === 'service') {
    showServiceModal.value = true
    showPrivacyModal.value = false
  }
}

const closeModal = (modalType) => {
  if (modalType === 'perm') showPermModal.value = false
  if (modalType === 'forgot') showForgotModal.value = false
  if (modalType === 'privacy') showPrivacyModal.value = false
  if (modalType === 'service') showServiceModal.value = false
}

// ===== 表单验证 =====
const validateLoginForm = () => {
  let isValid = true
  // 邮箱验证
  if (!loginForm.email.trim()) {
    formErrors.login.email = '请输入邮箱'
    isValid = false
  } else if (!/^[\w.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/.test(loginForm.email.trim())) {
    formErrors.login.email = '请输入有效的邮箱地址'
    isValid = false
  } else {
    formErrors.login.email = ''
  }

  // 密码验证
  if (!loginForm.password) {
    formErrors.login.password = '请输入密码'
    isValid = false
  } else if (loginForm.password.length < 6) {
    formErrors.login.password = '密码长度不能少于6位'
    isValid = false
  } else {
    formErrors.login.password = ''
  }

  return isValid
}

const validateRegForm = () => {
  let isValid = true
  const emailReg = /^[\w.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/

  // 邮箱验证
  if (!regForm.email.trim()) {
    formErrors.reg.email = '请输入校内邮箱'
    isValid = false
  } else if (!emailReg.test(regForm.email.trim())) {
    formErrors.reg.email = '请输入有效的邮箱地址'
    isValid = false
  } else {
    formErrors.reg.email = ''
  }

  // 密码验证
  if (!regForm.password) {
    formErrors.reg.password = '请设置密码'
    isValid = false
  } else if (regForm.password.length < 6) {
    formErrors.reg.password = '密码长度不能少于6位'
    isValid = false
  } else {
    formErrors.reg.password = ''
  }

  // 确认密码验证
  if (!regForm.password2) {
    formErrors.reg.password2 = '请确认密码'
    isValid = false
  } else if (regForm.password2 !== regForm.password) {
    formErrors.reg.password2 = '两次密码不一致'
    isValid = false
  } else {
    formErrors.reg.password2 = ''
  }

  // 昵称验证
  if (!regForm.nickname.trim()) {
    formErrors.reg.nickname = '请输入昵称'
    isValid = false
  } else if (regForm.nickname.trim().length > 20) {
    formErrors.reg.nickname = '昵称不能超过20个字符'
    isValid = false
  } else {
    formErrors.reg.nickname = ''
  }

  // 验证码验证
  if (!regForm.verify_code.trim()) {
    formErrors.reg.verify_code = '请输入验证码'
    isValid = false
  } else if (regForm.verify_code.trim().length !== 6) {
    formErrors.reg.verify_code = '验证码必须是6位数字'
    isValid = false
  } else {
    formErrors.reg.verify_code = ''
  }

  // 同意条款验证
  if (!regForm.agree) {
    formErrors.reg.agree = '请先同意隐私政策'
    isValid = false
  } else {
    formErrors.reg.agree = ''
  }

  return isValid
}

// ===== 事件处理 =====
// 登录处理 - 适配新的响应结构
const handleLogin = async() => {
  if (!validateLoginForm()) return
  try {
    isLoading.value = true
    
    // 加密密码
    const encryptedPassword = await encryptPassword(loginForm.password)
    
    // 注意：请求适配层会处理响应，这里直接得到处理后的数据
    const responseData = await login({
      email: loginForm.email.trim(),
      password: encryptedPassword
    })

    console.log('登录响应数据:', responseData)
    
    // 由于请求适配层已经处理了响应，responseData 直接就是后端返回的 data 字段
    // 但我们需要检查是否有错误，因为成功时返回 data，错误时抛出异常
    
    // 如果执行到这里说明登录成功，responseData 包含完整响应
    console.log('📊 [LOGIN DEBUG] 完整响应结构:', responseData)

    // 从responseData.data中提取用户信息
    const { token, refresh_token, user_id, email, nickname, avatar } = responseData.data
    
    // 存储token和用户信息 - 适配拦截器的token读取逻辑
    userStore.login(token, {
      user_id,
      email,
      nickname,
      avatar,
      role: 'user'
    }, refresh_token)
    
    // 关键修改：统一token存储key，适配请求拦截器
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user_token', token) // 新增：适配请求拦截器的读取逻辑
    localStorage.setItem('user_info', JSON.stringify({
      user_id,
      email,
      nickname,
      avatar,
      role: 'user'
    }))
    localStorage.setItem('saved_login_email', loginForm.email)
    
    routeJump('/hubviews')
    
  } catch (error) {
    console.error('登录错误详情:', error)
    // 错误信息已经由请求适配层处理，直接显示
    formErrors.login.password = error.message || '登录失败，请检查邮箱和密码'
  } finally {
    isLoading.value = false
  }
}

// 注册处理 - 适配新的响应结构
const handleRegister = async() => {
  if (!validateRegForm()) return
  try {
    isLoading.value = true
    
    // 加密密码
    const encryptedPassword = await encryptPassword(regForm.password)
    
    const registerData = {
      email: regForm.email.trim(),
      password: encryptedPassword,
      nickname: regForm.nickname.trim(),
      verify_code: regForm.verify_code.trim()
    }

    // 如果有学号，添加到注册数据中
    if (regForm.student_id.trim()) {
      registerData.student_id = regForm.student_id.trim()
    }
    
    console.log('发送注册数据:', registerData)
    
    // 注意：请求适配层会处理响应，这里直接得到处理后的数据
    const responseData = await register(registerData)
    
    console.log('注册响应数据:', responseData)
    
    // 由于请求适配层返回完整响应，从data字段中提取用户信息
    console.log('📊 [REGISTER DEBUG] 完整响应结构:', responseData)
    const { token, refresh_token, user_id, email, nickname, avatar } = responseData.data
    
    // 注册成功后自动登录
    userStore.login(token, {
      user_id,
      email,
      nickname,
      avatar,
      role: 'user'
    }, refresh_token)
    
    // 关键修改：统一token存储key，适配请求拦截器
    localStorage.setItem('access_token', token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user_token', token) // 新增：适配请求拦截器的读取逻辑
    localStorage.setItem('user_info', JSON.stringify({
      user_id,
      email,
      nickname,
      avatar,
      role: 'user'
    }))
    
    routeJump('/hubviews')
    
  } catch (error) {
    console.error('注册错误详情:', error)
    // 错误信息已经由请求适配层处理，直接显示
    formErrors.reg.email = error.message || '注册失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

// 游客登录
const handleGuestLogin = () => {
  // TODO: 游客模式逻辑
  alert('游客模式功能开发中...')
}

// 权限同意
const handlePermissionAccept = () => {
  closeModal('perm')
}

// 发送验证码
const handleSendVerifyCode = async() => {
  if (!regForm.email.trim()) {
    formErrors.reg.email = '请先输入邮箱'
    return
  }

  const emailReg = /^[\w.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
  if (!emailReg.test(regForm.email.trim())) {
    formErrors.reg.email = '请输入有效的邮箱地址'
    return
  }

  try {
    const responseData = await sendCode({ email: regForm.email.trim() })
    console.log('验证码发送响应:', responseData)

    // 开始倒计时
    verifyCodeCooldown.value = 60
    const countdown = setInterval(() => {
      verifyCodeCooldown.value--
      if (verifyCodeCooldown.value <= 0) {
        clearInterval(countdown)
      }
    }, 1000)

    formErrors.reg.email = ''
    // 可以添加成功提示
    alert('验证码已发送，请查收邮件')
  } catch (error) {
    console.error('发送验证码失败:', error)
    formErrors.reg.email = error.message || '发送验证码失败，请稍后重试'
  }
}

// 忘记密码发送邮件
const handleForgotSend = async() => {
  try {
    // TODO: 对接忘记密码API
    alert('密码重置功能开发中...')
    closeModal('forgot')
  } catch (error) {
    closeModal('forgot')
  }
}
</script>
<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { 
  height: 100%; 
  font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Microsoft Yahei"; 
  background: linear-gradient(180deg, #f3f6ff 0%, #fff 60%); 
  color: #0f1724; 
  -webkit-font-smoothing: antialiased; 
}
a { color: var(--accent); text-decoration: none; transition: color 0.2s; }
a:hover { color: var(--accent-2); }

/* ===== 页面布局 ===== */
.wrap { 
  max-width: 1180px; 
  margin: 36px auto; 
  padding: 20px; 
  display: grid; 
  grid-template-columns: 1fr 1fr; 
  gap: 28px; 
  min-height: calc(100vh - 72px); 
  align-items: stretch;
}

.brand-card, .auth-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* ===== 通用组件样式 ===== */
.card {
  background: var(--card);
  border-radius: var(--radius);
  padding: 28px;
  box-shadow: var(--shadow);
  position: relative;
  overflow: hidden;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 16px;
  border-radius: var(--radius-sm);
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  font-size: 14px;
}

.btn.primary {
  background: linear-gradient(90deg, var(--accent), #9a6cff);
  color: #fff;
  box-shadow: 0 8px 20px rgba(124,87,255,0.14);
}

.btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(124,87,255,0.2);
}

.btn.ghost {
  background: transparent;
  border: 1px solid #eef2ff;
  color: var(--muted);
}

.btn.ghost:hover {
  background: rgba(124,87,255,0.05);
  border-color: var(--accent);
  color: var(--accent);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

/* ===== 左侧品牌卡片样式 ===== */
.brand-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 10px;
}

.logo-wrap {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}

.logo {
  width: 86px;
  height: 86px;
  border-radius: 18px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 20px;
  box-shadow: 0 8px 30px rgba(124,87,255,0.18);
}

.brand-card h1 {
  margin: 0;
  font-size: 28px;
  color: var(--accent);
}

.lead {
  color: var(--muted);
  max-width: 42ch;
  line-height: 1.6;
  margin-bottom: 24px;
  font-size: 14px;
}

.feature-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 18px;
  margin-bottom: 18px;
}

.feature-list > div {
  min-width: 200px;
}

.feature-title {
  font-weight: 700;
  margin-bottom: 4px;
  font-size: 14px;
}

.map-section {
  margin-top: 18px;
}

.map-preview {
  width: 100%;
  height: 180px;
  border-radius: var(--radius-sm);
  background: linear-gradient(180deg, #eef6ff, #f9faff);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #e6eefc;
  color: var(--muted);
  margin-top: 8px;
}

.brand-card .footer {
  margin-top: 24px;
  text-align: center;
  color: #98a0b4;
  font-size: 13px;
  width: 100%;
}

/* 装饰形状 */
.shape-top {
  position: absolute;
  right: -60px;
  top: -60px;
  width: 260px;
  height: 260px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  opacity: 0.08;
  border-radius: 54px;
  transform: rotate(20deg);
}

.shape-btm {
  position: absolute;
  left: -40px;
  bottom: -40px;
  width: 200px;
  height: 200px;
  background: linear-gradient(90deg, #ffe6d9, #f8f1ff);
  opacity: 0.06;
  border-radius: 34px;
}

/* ===== 右侧登录注册卡片样式 ===== */
.auth-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.auth-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.auth-title {
  font-size: 18px;
  font-weight: 800;
  margin: 0;
}

.auth-subtitle {
  color: var(--muted);
  margin-top: 6px;
  font-size: 14px;
}

.links {
  display: flex;
  gap: 10px;
}

.links a {
  font-size: 13px;
  color: var(--muted);
  transition: color 0.2s;
}

.links a:hover {
  color: var(--accent);
}

/* 标签页样式 */
.tabs {
  display: flex;
  background: transparent;
  border-radius: 12px;
  padding: 6px;
  gap: 6px;
  margin-bottom: 8px;
}

.tab {
  flex: 1;
  padding: 12px;
  border-radius: var(--radius-sm);
  border: none;
  background: transparent;
  font-weight: 700;
  color: #5b6170;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.tab.active {
  background: linear-gradient(90deg, var(--accent), #9a6cff);
  color: #fff;
  box-shadow: 0 8px 20px rgba(124,87,255,0.14);
}

.tab:hover:not(.active) {
  background: rgba(124,87,255,0.05);
}

/* 表单样式 */
.form {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

label {
  display: block;
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 6px;
  font-weight: 500;
}

input[type="text"],
input[type="password"],
input[type="email"] {
  width: 100%;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid #e7ecf6;
  background: #fbfcff;
  font-size: 14px;
  transition: all 0.2s;
}

input:focus {
  outline: none;
  box-shadow: 0 8px 24px rgba(124,87,255,0.06);
  border-color: rgba(124,87,255,0.22);
  background: #fff;
}

/* 错误输入样式 */
.input-error {
  border-color: var(--error) !important;
}

.error-tip {
  margin: 0;
  font-size: 12px;
  color: var(--error);
  margin-top: 4px;
}

.helper {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 13px;
}

.small {
  font-size: 12px;
  color: var(--muted);
}

.btn-group {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

/* 演示信息样式 */
.example {
  background: #f9fbff;
  padding: 16px;
  border-radius: var(--radius-sm);
  border: 1px solid #f1f6ff;
  color: var(--muted);
  font-size: 13px;
  margin-top: 16px;
}

.demo-account {
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.5;
}

/* 验证码输入组样式 */
.verify-code-group {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.verify-code-group input {
  flex: 1;
}

.verify-btn {
  background: var(--accent);
  color: #fff;
  border: 1px solid var(--accent);
  white-space: nowrap;
  min-width: 100px;
  font-size: 13px;
  padding: 12px 16px;
}

.verify-btn:disabled {
  background: #e7ecf6;
  color: var(--muted);
  border-color: #e7ecf6;
  cursor: not-allowed;
}

.verify-btn:hover:not(:disabled) {
  background: var(--accent-2);
  border-color: var(--accent-2);
}

/* 复选框样式 */
.checkbox {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.checkbox input {
  width: 16px;
  height: 16px;
  margin-top: 2px;
  accent-color: var(--accent);
}

.checkbox label {
  margin: 0;
  line-height: 1.4;
}

/* 动画效果 */
.pulse {
  animation: pulse 2.8s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

/* ===== 模态框样式 ===== */
.modal {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(6,10,18,0.36);
  z-index: 50;
  backdrop-filter: blur(4px);
}

.modal-panel {
  background: #fff;
  padding: 24px;
  border-radius: var(--radius);
  max-width: 720px;
  width: 90%;
  box-shadow: 0 16px 48px rgba(8,12,40,0.2);
  animation: modalSlideIn 0.2s ease;
}

.modal-panel.small {
  max-width: 420px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.modal h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.modal-close {
  background: transparent;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--muted);
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.modal-close:hover {
  background: rgba(0,0,0,0.05);
  color: #1f2937;
}

.perm-list {
  margin: 12px 0;
  padding-left: 20px;
  color: var(--muted);
  line-height: 1.6;
  font-size: 14px;
}

.doc-content {
  margin-top: 8px;
  color: var(--muted);
  line-height: 1.6;
  font-size: 14px;
}

.doc-content h4 {
  margin: 16px 0 8px 0;
  color: #1f2937;
  font-size: 16px;
}

.modal-btn-group {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 模态框动画 */
@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* ===== 加载动画 ===== */
.loading-spinner.small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.7);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== 响应式设计 ===== */
@media (max-width: 960px) {
  .wrap {
    grid-template-columns: 1fr;
    padding: 12px;
    gap: 20px;
  }
  
  .card {
    padding: 20px;
  }
  
  .logo-wrap {
    flex-direction: column;
    text-align: center;
  }
  
  .auth-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .links {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .helper {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .btn-group {
    flex-direction: column;
  }
}

/* ===== 无障碍支持 ===== */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 焦点样式 */
button:focus-visible,
input:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
</style>