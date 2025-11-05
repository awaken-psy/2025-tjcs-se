<template>
  <!-- 胶囊打开动画组件：触发式动画，支持胶囊展开、内容浮现效果，动画结束后返回原页面 -->
  <div
    class="capsule-animation-modal"
    :class="{ active: isActive }"
  >
    <!-- 动画容器 -->
    <div class="animation-container">
      <!-- 胶囊外壳 -->
      <div
        class="capsule-shell"
        :class="{ open: animationStep >= 1 }"
      >
        <!-- 胶囊顶部 -->
        <div class="shell-top" />
        <!-- 胶囊底部 -->
        <div class="shell-bottom" />
        <!-- 胶囊锁（动画前期显示，后期消失） -->
        <div
          class="capsule-lock"
          :class="{ unlock: animationStep >= 2 }"
        />
      </div>

      <!-- 胶囊内容（动画后期浮现） -->
      <div
        class="capsule-content"
        :class="{ show: animationStep >= 3 }"
      >
        <!-- 内容图标 -->
        <div class="content-icon">
          {{ capsuleData.icon || '📦' }}
        </div>
        <!-- 内容标题 -->
        <h3 class="content-title">
          {{ capsuleData.title || '时光胶囊' }}
        </h3>
        <!-- 内容描述 -->
        <p class="content-desc">
          {{ capsuleData.desc || '珍藏的回忆已解锁' }}
        </p>
        <!-- 关闭按钮（动画结束后显示） -->
        <button 
          class="btn close-btn"
          :class="{ show: animationStep >= 4 }"
          @click="handleClose"
        >
          返回原页面
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'

/**
 * 组件作用：
 * 1. 实现胶囊打开的触发式动画（外壳展开 → 锁解锁 → 内容浮现 → 显示关闭按钮）
 * 2. 动画结束后支持手动关闭，关闭后返回原页面（通过路由或历史记录）
 * 3. 可在任何页面触发（如地图页、我的胶囊页），传入胶囊基础数据即可
 * 
 * 组件接口（Props）：
 * @param {Boolean} isActive - 是否触发动画（true=播放，false=隐藏）
 * @param {Object} capsuleData - 胶囊基础数据（动画中显示的内容）
 *   {
 *     id: String, // 胶囊ID（可选，用于后续定位原胶囊）
 *     title: String, // 胶囊标题（动画中显示）
 *     desc: String, // 胶囊描述（动画中显示）
 *     icon: String // 胶囊图标（可选，默认"📦"）
 *   }
 * 
 * 组件事件（Emits）：
 * @emit close - 动画关闭后触发，参数为胶囊ID（用于原页面定位）
 */
const props = defineProps({
  isActive: {
    type: Boolean,
    default: false
  },
  capsuleData: {
    type: Object,
    default: () => ({
      id: '',
      title: '时光胶囊',
      desc: '珍藏的回忆已解锁',
      icon: '📦'
    }),
    validator: (val) => val.title && val.desc // 至少需要标题和描述
  }
})

const emit = defineEmits(['close'])

// 动画状态：0=未触发，1=外壳展开，2=锁解锁，3=内容浮现，4=动画结束（显示关闭按钮）
const animationStep = ref(0)
// 动画定时器（用于控制步骤切换）
let animationTimer = null
// 原页面路径（动画结束后返回）
const originalPath = ref(window.location.hash || '/')

/**
 * 监听isActive变化：触发/停止动画
 */
watch(() => props.isActive, (newVal) => {
  if (newVal) {
    startAnimation()
  } else {
    stopAnimation()
  }
}, { immediate: true })

/**
 * 组件挂载时：记录原页面路径
 */
onMounted(() => {
  originalPath.value = window.location.hash || window.location.pathname
})

/**
 * 组件卸载时：清除定时器，避免内存泄漏
 */
onUnmounted(() => {
  stopAnimation()
})

/**
 * 开始动画：分步骤控制动画进度
 */
const startAnimation = () => {
  // 重置动画状态
  animationStep.value = 0
  // 清除现有定时器
  if (animationTimer) clearInterval(animationTimer)

  // 步骤1：外壳展开（0.8秒后）
  setTimeout(() => {
    animationStep.value = 1
  }, 300)

  // 步骤2：锁解锁（1.5秒后）
  setTimeout(() => {
    animationStep.value = 2
  }, 1500)

  // 步骤3：内容浮现（2.2秒后）
  setTimeout(() => {
    animationStep.value = 3
  }, 2200)

  // 步骤4：动画结束，显示关闭按钮（3秒后）
  setTimeout(() => {
    animationStep.value = 4
  }, 3000)
}

/**
 * 停止动画：重置状态，清除定时器
 */
const stopAnimation = () => {
  animationStep.value = 0
  if (animationTimer) {
    clearInterval(animationTimer)
    animationTimer = null
  }
}

/**
 * 关闭动画：触发close事件，返回原页面
 */
const handleClose = () => {
  // 触发关闭事件，传递胶囊ID
  emit('close', props.capsuleData.id)
  // 重置动画状态
  animationStep.value = 0
  // 返回原页面（通过历史记录，避免刷新）
  window.location.hash = originalPath.value
  // 若原页面有定位胶囊需求，可在父页面监听close事件后处理
}
</script>

<style scoped>
/* 动画模态框：全屏覆盖，背景半透明 */
.capsule-animation-modal {
  position: fixed;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(8, 12, 20, 0.8);
  backdrop-filter: blur(8px);
  z-index: 2000; /* 确保在所有弹窗之上 */
}

.capsule-animation-modal.active {
  display: flex;
}

/* 动画容器：居中显示 */
.animation-container {
  position: relative;
  width: 320px;
  height: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 胶囊外壳：默认闭合状态 */
.capsule-shell {
  position: relative;
  width: 240px;
  height: 360px;
  transition: all 0.8s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* 外壳展开状态 */
.capsule-shell.open {
  width: 300px;
  height: 420px;
}

/* 胶囊顶部：弧形顶部 */
.shell-top {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 180px;
  background: linear-gradient(180deg, #6c8cff, #5a7cff);
  border-radius: 120px 120px 0 0;
  box-shadow: 0 -4px 12px rgba(108, 140, 255, 0.3);
  transition: all 0.8s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* 外壳展开时顶部变化 */
.capsule-shell.open .shell-top {
  height: 210px;
  border-radius: 150px 150px 0 0;
}

/* 胶囊底部：弧形底部 */
.shell-bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 180px;
  background: linear-gradient(0deg, #6c8cff, #5a7cff);
  border-radius: 0 0 120px 120px;
  box-shadow: 0 4px 12px rgba(108, 140, 255, 0.3);
  transition: all 0.8s cubic-bezier(0.25, 0.1, 0.25, 1);
}

/* 外壳展开时底部变化 */
.capsule-shell.open .shell-bottom {
  height: 210px;
  border-radius: 0 0 150px 150px;
  transform: translateY(-60px); /* 底部上移，露出内容 */
}

/* 胶囊锁：居中显示，默认锁定状态 */
.capsule-lock {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #6c8cff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
  z-index: 10;
}

/* 锁解锁状态：上移并消失 */
.capsule-lock.unlock {
  transform: translate(-50%, -150%);
  opacity: 0;
  visibility: hidden;
}

/* 胶囊内容：默认隐藏，动画后期浮现 */
.capsule-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 220px;
  text-align: center;
  color: white;
  opacity: 0;
  visibility: hidden;
  transition: all 0.6s cubic-bezier(0.25, 0.1, 0.25, 1);
  z-index: 5;
}

/* 内容浮现状态 */
.capsule-content.show {
  opacity: 1;
  visibility: visible;
  transform: translate(-50%, -80%); /* 上移至展开的外壳中间 */
}

/* 内容图标 */
.content-icon {
  font-size: 48px;
  margin-bottom: 16px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 内容标题 */
.content-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 内容描述 */
.content-desc {
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 24px;
  opacity: 0.9;
}

/* 关闭按钮：默认隐藏，动画结束后显示 */
.close-btn {
  background: white;
  color: #6c8cff;
  padding: 10px 24px;
  border-radius: 24px;
  font-weight: 600;
  transition: all 0.2s;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
}

.close-btn.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.close-btn:hover {
  background: #f0f4ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 140, 255, 0.2);
}
</style>