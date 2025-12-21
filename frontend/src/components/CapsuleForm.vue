<template>
  <!-- 胶囊表单组件：支持创建和编辑模式，包含完整表单字段 -->
  <div class="capsule-form-modal" :class="{ active: isShow }">
    <div class="modal-overlay" @click="handleClose" />
    <div class="modal-panel">
      <!-- 模态框头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          {{ isEdit ? '编辑胶囊' : '创建时光胶囊' }}
        </h2>
        <button class="modal-close" title="关闭" @click="handleClose">
          关闭
        </button>
      </div>

      <!-- 表单内容 -->
      <div ref="scrollContainer" class="modal-content">
        <!-- 状态提示 -->
        <div v-if="showAlert" class="form-alert" :class="alertType">
          <div class="alert-content">
            <i class="alert-icon" :class="alertIcon" />
            <span>{{ alertText }}</span>
          </div>
          <button class="alert-close" @click="showAlert = false">
            <i class="fas fa-times" />
          </button>
        </div>

        <form class="capsule-form" @submit.prevent="handleSubmit">
          <!-- 1. 胶囊标题 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-heading section-icon" />
              <h3 class="section-title">胶囊标题</h3>
              <span class="required-badge">必填</span>
            </div>
            <input
              v-model="formData.title"
              type="text"
              class="form-input"
              placeholder="给你的胶囊起个温暖的名字..."
              :class="{ 'input-error': formErrors.title }"
              maxlength="50"
              @input="validateField('title')"
              @blur="validateField('title')" />
            <div class="form-footer">
              <span class="char-count">{{ formData.title.length }}/50</span>
              <span v-if="formErrors.title" class="error-text">{{
                formErrors.title
              }}</span>
            </div>
          </div>

          <!-- 2. 胶囊内容 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-edit section-icon" />
              <h3 class="section-title">胶囊内容</h3>
              <span class="required-badge">必填</span>
            </div>
            <textarea
              v-model="formData.content"
              class="form-textarea"
              placeholder="写下你想珍藏的回忆..."
              :class="{ 'input-error': formErrors.content }"
              rows="5"
              maxlength="1000"
              @input="validateField('content')"
              @blur="validateField('content')" />
            <div class="form-footer">
              <span class="char-count">{{ formData.content.length }}/1000</span>
              <span v-if="formErrors.content" class="error-text">{{
                formErrors.content
              }}</span>
            </div>
          </div>

          <!-- 3. 可见性设置 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-eye section-icon" />
              <h3 class="section-title">可见性设置</h3>
              <span class="required-badge">必填</span>
            </div>
            <div class="visibility-options">
              <label
                v-for="option in visibilityOptions"
                :key="option.key"
                class="visibility-option"
                :class="{ active: formData.visibility === option.key }">
                <input
                  v-model="formData.visibility"
                  type="radio"
                  name="visibility"
                  :value="option.key"
                  class="vis-radio" />
                <div class="option-content">
                  <i class="option-icon" :class="option.icon" />
                  <div class="option-text">
                    <div class="option-title">{{ option.label }}</div>
                    <div class="option-desc">{{ option.desc }}</div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <!-- 4. 位置信息 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-map-marker-alt section-icon" />
              <h3 class="section-title">位置信息</h3>
              <span class="optional-badge">选填</span>
            </div>
            <div class="location-section">
              <!-- 地址输入框 -->
              <div class="address-input-wrapper">
                <input
                  v-model="formData.address"
                  type="text"
                  class="form-input"
                  placeholder="请输入地址信息（如：北京市朝阳区某某大学）"
                  maxlength="200" />
                <div class="form-footer">
                  <span class="char-count"
                    >{{ (formData.address || '').length }}/200</span
                  >
                </div>
              </div>

              <!-- 自动定位区域 -->
              <div class="auto-location-wrapper">
                <div class="location-display">
                  <div class="location-info">
                    <i class="fas fa-location-dot location-icon" />
                    <div class="location-text">
                      <div class="location-address">
                        {{ locationInfo.address || '未获取到自动定位' }}
                      </div>
                      <div v-if="locationInfo.lat" class="location-coords">
                        经纬度: {{ locationInfo.lat.toFixed(6) }},
                        {{ locationInfo.lng.toFixed(6) }}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    class="location-btn"
                    :disabled="isLocating"
                    @click="getCurrentLocation">
                    <i
                      class="fas"
                      :class="
                        isLocating ? 'fa-spinner fa-spin' : 'fa-refresh'
                      " />
                    {{ isLocating ? '自动定位' : '重新定位' }}
                  </button>
                </div>
                <div v-if="locationPermission" class="location-status">
                  <i class="fas" :class="locationIcon" />
                  <span>{{ locationMessage }}</span>
                </div>
              </div>

              <!-- 使用自动定位地址按钮 -->
              <div
                v-if="
                  locationInfo.address &&
                  locationInfo.address !== '未获取到自动定位'
                "
                class="use-auto-location">
                <button
                  type="button"
                  class="btn btn-outline"
                  @click="useAutoLocation">
                  <i class="fas fa-copy" />
                  使用自动定位的地址
                </button>
              </div>
            </div>
          </div>

          <!-- 5. 解锁条件 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-lock section-icon" />
              <h3 class="section-title">解锁条件</h3>
              <span class="required-badge">必填</span>
            </div>
            <div class="unlock-conditions-section">
              <div class="form-group">
                <label class="form-label">解锁类型</label>
                <select v-model="unlockConditions.type" class="form-select">
                  <option value="public">公开 (Public) - 所有人可解锁</option>
                  <option value="password">
                    密码 (Password) - 输入密码解锁
                  </option>
                  <option value="private">
                    私密 (Private) - 只有自己可解锁
                  </option>
                </select>
              </div>

              <div
                v-if="unlockConditions.type === 'password'"
                class="form-group dynamic-input">
                <label class="form-label">解锁密码</label>
                <input
                  v-model="unlockConditions.password"
                  type="text"
                  class="form-input"
                  placeholder="请输入解锁密码（必填）"
                  maxlength="50" />
              </div>

              <div class="form-group dynamic-input">
                <label class="form-label">解锁半径 (米)</label>
                <div class="input-with-unit">
                  <input
                    v-model.number="unlockConditions.radius"
                    type="number"
                    min="1"
                    max="1000"
                    class="form-input"
                    placeholder="请输入解锁半径 (米)" />
                  <span class="input-unit">米 (1-1000)</span>
                </div>
              </div>

              <div class="form-group dynamic-input">
                <label class="form-label">
                  {{ unlockTimeLabel }}
                </label>
                <input
                  v-model="unlockConditions.unlockable_time"
                  type="datetime-local"
                  class="form-input"
                  :min="minDateTime" />
              </div>

              <!-- <div v-if="isEdit" class="form-group">
                <label class="form-label">当前是否已解锁</label>
                <div style="display: flex; align-items: center; gap: 12px">
                  <input
                    v-model="unlockConditions.is_unlocked"
                    type="checkbox"
                    id="isUnlocked"
                    style="width: auto"
                    :disabled="!isEdit" />
                  <label for="isUnlocked" style="font-weight: normal">
                    {{
                      unlockConditions.is_unlocked
                        ? '是 (已解锁)'
                        : '否 (未解锁)'
                    }}
                  </label>
                </div>
              </div>

              <div class="form-footer">
                <span class="char-count">{{ unlockHintText }}</span>
              </div> -->
            </div>
          </div>

          <!-- 6. 媒体文件上传 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-image section-icon" />
              <h3 class="section-title">媒体文件</h3>
              <span class="optional-badge">选填</span>
            </div>

            <div class="form-group upload-container">
              <label class="form-label">上传图片/音频 (最多 5 个)</label>

              <div
                class="upload-drop-area"
                :class="{
                  'is-disabled': isUploading || mediaFiles.length >= 5,
                  'is-active': isDragging,
                  'has-error': uploadErrorStatus,
                }"
                @click="triggerFileInput"
                @dragover.prevent="isDragging = true"
                @dragleave.prevent="isDragging = false"
                @drop.prevent="handleFileDrop">
                <i
                  :class="[
                    'fas',
                    'upload-icon',
                    uploadErrorStatus
                      ? 'fa-exclamation-circle'
                      : 'fa-cloud-upload-alt',
                  ]" />

                <p class="upload-text">
                  <span class="upload-link">{{
                    mediaFiles.length >= 5 ? '已达上限' : '点击此处上传文件'
                  }}</span>
                  或拖拽文件到这里
                </p>
                <p class="upload-hint">
                  支持图片 (JPG/PNG) 和音频 (MP3/WAV)，最多 {{ 5 }} 个
                </p>
              </div>

              <input
                ref="fileInputRef"
                type="file"
                id="media-upload"
                @change="handleFileUpload"
                accept="image/*,audio/*"
                multiple
                style="display: none"
                :disabled="isUploading || mediaFiles.length >= 5" />
            </div>

            <div v-if="mediaFiles.length > 0" class="uploaded-files-list">
              <div
                v-for="(file, index) in mediaFiles"
                :key="file.id"
                class="uploaded-file-item">
                <div class="file-preview-wrapper">
                  <img
                    v-if="file.type === 'image'"
                    :src="file.local_url || file.thumbnail || file.url"
                    alt="预览图"
                    class="file-preview-img" />
                  <div
                    v-else-if="file.type === 'audio'"
                    class="file-preview-audio">
                    <i class="fas fa-file-audio audio-icon" />
                  </div>
                </div>

                <span class="file-name">
                  {{
                    file.url.substring(file.url.lastIndexOf('/') + 1).length >
                    30
                      ? file.url
                          .substring(file.url.lastIndexOf('/') + 1)
                          .slice(0, 15) +
                        '...' +
                        file.url
                          .substring(file.url.lastIndexOf('/') + 1)
                          .slice(-10)
                      : file.url.substring(file.url.lastIndexOf('/') + 1)
                  }}
                </span>

                <button
                  type="button"
                  class="file-remove-btn"
                  :disabled="isUploading"
                  @click="removeMediaFile(index)">
                  <i class="fas fa-times" />
                </button>
              </div>
            </div>
          </div>

          <!-- 7. 标签管理 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-tags section-icon" />
              <h3 class="section-title">添加标签</h3>
              <span class="optional-badge">选填</span>
            </div>
            <div class="tags-section">
              <div class="tags-input-wrapper">
                <input
                  v-model="tagInput"
                  type="text"
                  class="tags-input"
                  placeholder="输入标签后按回车或逗号添加..."
                  maxlength="20"
                  @keydown="handleTagInput" />
                <span class="tags-count">{{ selectedTags.length }}/5</span>
              </div>
              <div v-if="selectedTags.length > 0" class="selected-tags">
                <span
                  v-for="(tag, index) in selectedTags"
                  :key="index"
                  class="tag-item">
                  {{ tag }}
                  <button
                    type="button"
                    class="remove-tag"
                    @click="removeTag(index)">
                    <i class="fas fa-times" />
                  </button>
                </span>
              </div>
              <div v-if="suggestedTags.length > 0" class="suggested-tags">
                <span class="suggested-label">推荐标签：</span>
                <span
                  v-for="tag in suggestedTags"
                  :key="tag"
                  class="suggested-tag"
                  @click="addSuggestedTag(tag)">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- 表单操作 -->
          <div class="form-actions">
            <button
              v-if="!isEdit"
              type="button"
              class="btn btn-draft"
              :disabled="isSubmitting"
              @click="saveDraft">
              <i class="fas fa-save" /> 保存草稿
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              :disabled="isSubmitting"
              @click="handleClose">
              取消
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting || !isFormValid">
              <i v-if="isSubmitting" class="fas fa-spinner fa-spin" />
              <i v-else class="fas fa-paper-plane" />
              {{
                isSubmitting ? '提交中...' : isEdit ? '更新胶囊' : '创建胶囊'
              }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// #region import
import { onMounted } from 'vue'
import { computed, nextTick, onUnmounted, reactive, ref, watch } from 'vue'
import { createCapsule, updateCapsule } from '../api/new/capsulesApi.js'
import { uploadFile } from '../api/new/uploadApi.js'
// #endregion

// #region props and emits
// Props
const props = defineProps({
  isShow: {
    type: Boolean,
    default: false,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
  editData: {
    type: Object,
    default: () => ({}),
  },
})
// Emits
const emit = defineEmits(['close', 'submit'])
// #endregion

// #region 状态管理
// 表单数据
const formData = reactive({
  title: '',
  visibility: 'public',
  content: '',
  lat: null,
  lng: null,
})

// 表单错误
const formErrors = reactive({
  title: '',
  content: '',
  visibility: '',
})

// 状态管理
const isSubmitting = ref(false)
const isLocating = ref(false)
const showAlert = ref(false)
const alertText = ref('')
const alertType = ref('success')
const alertIcon = ref('fas fa-check-circle')

// 标签相关
const tagInput = ref('')
const selectedTags = ref([])
const suggestedTags = ref([
  '校园生活',
  '毕业季',
  '图书馆',
  '操场',
  '食堂',
  '宿舍',
  '课堂',
  '友谊',
])

// 图片上传
const mediaFiles = ref([]) // Array of { id, type, url, thumbnail }
const isUploading = ref(false)

// 🚀 新增：用于自定义上传区域
const fileInputRef = ref(null) // 引用隐藏的 input[type="file"]
const isDragging = ref(false) // 拖拽状态
const uploadErrorStatus = ref(false)

// 位置信息
const locationInfo = reactive({
  address: '',
  lat: null,
  lng: null,
})
const locationPermission = ref('')
const locationMessage = ref('等待位置授权...')

// 解锁条件相关状态
const unlockConditions = reactive({
  type: 'public', // 默认解锁类型：private, password, public
  password: '', // 对应 'password' 的密码值
  radius: 50, // 对应 'location' 的半径 (默认 50米)，改为始终存在
  is_unlocked: false, // 对应是否已解锁状态
  unlockable_time: '', // 对应最早可解锁时间
})

// 可见性常量定义
const visibilityOptions = [
  {
    key: 'public',
    label: '校园公开',
    desc: '所有校园用户可见',
    icon: 'fas fa-globe-americas',
  },
  {
    key: 'friends',
    label: '好友可见',
    desc: '仅你的好友可见',
    icon: 'fas fa-user-friends',
  },
  {
    key: 'private',
    label: '仅自己可见',
    desc: '完全私密，仅自己可见',
    icon: 'fas fa-lock',
  },
]

// 滚动容器引用
const scrollContainer = ref(null)
// #endregion

// #region 辅助函数
// 转换函数：将后端返回的可见性值转换为前端表单期望的值
const convertVisibilityToForm = (visibility) => {
  if (!visibility) return 'public'
  switch (visibility) {
    case 'campus':
      return 'public' // 后端campus -> 前端public
    case 'public':
      return 'public'
    case 'friends':
      return 'friends'
    case 'private':
      return 'private'
    default:
      return 'public'
  }
}

// 计算属性
const isFormValid = computed(() => {
  return (
    formData.title.trim() &&
    formData.content.trim() &&
    formData.visibility &&
    !formErrors.title &&
    !formErrors.content
  )
})

const locationIcon = computed(() => {
  switch (locationPermission.value) {
    case 'granted':
      return 'fa-check-circle text-success'
    case 'denied':
      return 'fa-exclamation-circle text-danger'
    default:
      return 'fa-info-circle text-warning'
  }
})
// #endregion

// #region 解锁条件
const unlockTypeLabel = computed(() => {
  // 🔓 修改：适配新的解锁类型
  switch (unlockConditions.type) {
    case 'private':
      return '私密胶囊'
    case 'password':
      return '解锁密码'
    case 'public':
      return '公开胶囊'
    default:
      return '值'
  }
})

const unlockHintText = computed(() => {
  // 🔓 修改：适配新的解锁类型
  switch (unlockConditions.type) {
    case 'private':
      return '只有你自己可以解锁此胶囊。'
    case 'password':
      return '用户需输入正确密码才可解锁。'
    case 'public':
      return '所有用户都可解锁此胶囊。'
    default:
      return ''
  }
})

// 🔓 新增：用于最早可解锁时间的标签
const unlockTimeLabel = computed(() => {
  return '最早可解锁时间'
})
// #endregion

// #region 滚动条方法定义
// 滚动锁定函数
const lockBodyScroll = () => {
  document.body.style.overflow = 'hidden'
}

const unlockBodyScroll = () => {
  document.body.style.overflow = ''
}
// #endregion

// #region 监听和生命周期
// 监听模态框显示状态
watch(
  () => props.isShow,
  (show) => {
    if (show) {
      lockBodyScroll()
      // 重置表单状态
      if (!props.isEdit) {
        resetForm()
        loadDraft()
      }
      // 重置定位相关状态
      locationPermission.value = ''
      locationMessage.value = '正在获取位置...'
      isLocating.value = false

      // 🔓 修改：重置解锁条件状态 (使用新的结构)
      Object.assign(unlockConditions, {
        type: 'public',
        password: '',
        radius: 50,
        is_unlocked: false,
        unlockable_time: '',
      })

      // 自动获取位置
      nextTick(() => {
        getCurrentLocation()
      })
    } else {
      unlockBodyScroll()
    }
  }
)

// 组件卸载时解锁滚动
onUnmounted(() => {
  unlockBodyScroll()
})

// 监听编辑数据变化
watch(
  () => props.editData,
  (newData) => {
    if (props.isEdit && newData) {
      Object.assign(formData, {
        title: newData.title || '',
        content: newData.content || '',
        visibility: convertVisibilityToForm(newData.visibility) || 'public',
        // 注意：location、lat、lng 是表单提交的核心数据
        location: newData.location || '',
        lat: newData.lat || null,
        lng: newData.lng || null,
      })

      // 🔓 修改：加载编辑模式下的解锁条件 (适配新的结构)
      if (newData.unlock_conditions) {
        const { type, password, radius, is_unlocked, unlockable_time } =
          newData.unlock_conditions

        let localTimeForInput = ''
        if (unlockable_time) {
          const d = new Date(unlockable_time)
          // 关键：将任何时区的时间转换为本地 YYYY-MM-DDTHH:mm 格式
          const year = d.getFullYear()
          const month = String(d.getMonth() + 1).padStart(2, '0')
          const day = String(d.getDate()).padStart(2, '0')
          const hours = String(d.getHours()).padStart(2, '0')
          const minutes = String(d.getMinutes()).padStart(2, '0')
          localTimeForInput = `${year}-${month}-${day}T${hours}:${minutes}`
        }

        Object.assign(unlockConditions, {
          type: type || 'public',
          password: password || '',
          radius: radius || 50,
          is_unlocked: is_unlocked || false,
          unlockable_time: unlockable_time || '',
        })
      }

      // 🔓 加载编辑模式下的媒体文件
      mediaFiles.value.splice(0, mediaFiles.value.length) // 先清空
      if (newData.media_files && Array.isArray(newData.media_files)) {
        newData.media_files.forEach((file) => {
          if (file.id && file.type && file.url) {
            mediaFiles.value.push(file)
          }
        })
      }

      // 同步到 locationInfo 用于界面展示 (这是关键)
      Object.assign(locationInfo, {
        address: newData.location || '已加载历史位置',
        lat: newData.lat || null,
        lng: newData.lng || null,
      })

      if (newData.tags) {
        selectedTags.value = Array.isArray(newData.tags)
          ? [...newData.tags]
          : []
      }

      // 这里需要根据你的后端返回判断：如果后端返回的是 URL 而不是 File 对象
      if (newData.imageUrl) {
        // 假设后端返回的字段是 imageUrl
        previewImage.value = newData.imageUrl
        formData.imageUrl = newData.imageUrl // 保持 formData.imageUrl 用于提交
      } else if (newData.image) {
        // 如果 newData.image 是一个文件 URL
        previewImage.value = newData.image
        formData.imageUrl = newData.image
      }
      // 注意：formData.image 应该只在用户上传新文件时设置 File 对象
    }
  },
  { immediate: true }
)

// #endregion

// #region 草稿相关
const DRAFT_KEY = 'capsule_form_draft'

// 保存草稿到 localStorage
const saveDraft = () => {
  const draftData = {
    formData: { ...formData },
    unlockConditions: { ...unlockConditions },
    selectedTags: [...selectedTags.value],
    // 注意：文件对象(File)无法直接存入 localStorage，通常只存元数据
    mediaFiles: mediaFiles.value.map((f) => ({
      id: f.id,
      type: f.type,
      url: f.url,
    })),
    timestamp: Date.now(),
  }

  localStorage.setItem(DRAFT_KEY, JSON.stringify(draftData))
  showAlertMessage('草稿已保存到本地', 'success')
}

// 加载草稿
const loadDraft = () => {
  const saved = localStorage.getItem(DRAFT_KEY)
  if (!saved) return

  try {
    const draft = JSON.parse(saved)
    // 将数据恢复到响应式对象中
    Object.assign(formData, draft.formData)
    Object.assign(unlockConditions, draft.unlockConditions)
    selectedTags.value = draft.selectedTags || []
    mediaFiles.value = draft.mediaFiles || []

    showAlertMessage('已自动恢复上次填写的草稿内容', 'success')
  } catch (e) {
    console.error('加载草稿失败', e)
  }
}

// 清除草稿 (在提交成功后调用)
const clearDraft = () => {
  localStorage.removeItem(DRAFT_KEY)
}

// #endregion

// #region 表单重制/关闭/提交
const resetForm = () => {
  Object.assign(formData, {
    title: '',
    content: '',
    visibility: 'public',
    location: '',
    address: '', // 重置地址字段
    lat: null,
    lng: null,
  })

  // 🔓 修改：重置解锁条件 (使用新的结构)
  Object.assign(unlockConditions, {
    type: 'public',
    password: '',
    radius: 50,
    is_unlocked: false,
    unlockable_time: '',
  })

  selectedTags.value = []

  tagInput.value = ''
  // 🔓 重置媒体文件
  mediaFiles.value.splice(0, mediaFiles.value.length)

  Object.keys(formErrors).forEach((key) => {
    formErrors[key] = ''
  })
}

const handleClose = () => {
  emit('close')
}
const handleSubmit = async () => {
  // 验证表单
  validateField('title')
  validateField('content')
  validateField('visibility')

  // 检查是否有错误
  const hasErrors = Object.values(formErrors).some((error) => error !== '')
  if (hasErrors) {
    showAlertMessage('请检查表单中的错误', 'error')
    return
  }

  // 检查必填字段
  if (
    !formData.title.trim() ||
    !formData.content.trim() ||
    !formData.visibility
  ) {
    showAlertMessage('请填写所有必填字段', 'error')
    return
  }

  // 🔓 额外验证：解锁条件 (仅验证密码类型)
  if (
    unlockConditions.type === 'password' &&
    !unlockConditions.password.trim()
  ) {
    showAlertMessage('密码解锁类型必须输入密码', 'error')
    return
  }

  // 🔓 额外验证：解锁时间
  if (!unlockConditions.unlockable_time) {
    showAlertMessage('请设置最早可解锁时间', 'error')
    return
  }
  if (unlockConditions.unlockable_time) {
    const selected = new Date(unlockConditions.unlockable_time)
    if (selected < new Date()) {
      showAlertMessage('解锁时间不能早于当前时间', 'error')
      return
    }
  }

  isSubmitting.value = true

  try {
    // ... (位置信息处理逻辑不变)
    let location = formData.location || locationInfo.address || '未知位置'
    let lat = formData.lat || locationInfo.lat
    let lng = formData.lng || locationInfo.lng

    if (!location || location === '正在获取位置...') {
      location = '默认位置'
    }
    if (lat === null || lat === undefined || isNaN(lat)) {
      lat = 39.9005
    }
    if (lng === null || lng === undefined || isNaN(lng)) {
      lng = 116.302
    }

    // 🔓 修改：构造 unlock_conditions 对象 (新结构)
    const unlockConditionsPayload = {
      type: unlockConditions.type,
      password:
        unlockConditions.type === 'password'
          ? unlockConditions.password.trim()
          : null, // 仅密码类型携带密码
      radius: parseInt(unlockConditions.radius) || 50, // 始终携带半径
      is_unlocked: unlockConditions.is_unlocked, // 始终携带状态

      // 将 datetime-local 格式 'YYYY-MM-DDTHH:mm' 转换为 ISO 8601 (UTC)
      unlockable_time: unlockConditions.unlockable_time
        ? (() => {
            const d = new Date(unlockConditions.unlockable_time)
            const offset = d.getTimezoneOffset() // 获取分钟偏移，北京时间为 -480
            // 将时间调整为本地时间对应的“看起来像UTC”的时间，或者直接发送带偏移的字符串
            const localDate = new Date(d.getTime() - offset * 60 * 1000)
            return localDate.toISOString().replace('Z', '') // 移除 Z，后端将作为本地时间处理
          })()
        : null,
    }

    // 构造完整的提交数据 (匹配后端期望的格式)
    const submitData = {
      title: formData.title.trim(),
      content: formData.content.trim(),
      visibility: formData.visibility,
      tags: selectedTags.value,

      location: {
        latitude: lat,
        longitude: lng,
        address: location,
      },

      unlock_conditions: unlockConditionsPayload,

      media_files: mediaFiles.value.map((file) => ({
        id: file.id,
        type: file.type,
        url: file.url,
        thumbnail: file.thumbnail,
      })),
    }

    // 移除调试日志，转换逻辑已完成
    let result = null
    let successMessage = ''

    // 🚨 修改点 3：根据 isEdit 状态选择调用创建或更新 API
    if (props.isEdit) {
      if (!props.editData.id) {
        throw new Error('编辑模式下缺少胶囊 ID')
      }
      // 添加 ID 到提交数据 (如果 API 要求 ID 在 body 中)
      const updatePayload = {
        ...submitData,
        id: props.editData.id,
      }

      // 调用更新 API
      result = await updateCapsule(props.editData.id, updatePayload) // 假设 updateCapsule 接收 ID 和 payload
      successMessage = '胶囊更新成功！'
      console.log('更新胶囊结果:', result)
    } else {
      // 调用创建 API
      result = await createCapsule(submitData)
      successMessage = '胶囊创建成功！'
      clearDraft() // 👈 提交成功后清除草稿
      // 性能优化：移除多余的控制台输出
    }

    // 立即处理结果，提升响应速度
    if (result && (result.id || Object.keys(result).length > 0)) {
      setTimeout(() => {
        // 传递结果数据给父组件
        emit('submit', result)
        handleClose()
      }, 300) // 进一步减少延迟时间，提升响应速度
    } else {
      // 如果没有返回有效的数据，这可能是API的问题
      showAlertMessage('胶囊创建成功但数据异常，请检查列表', 'warning')

      setTimeout(() => {
        alert('胶囊创建成功，但数据可能不完整。\n\n请检查胶囊列表确认。')
        emit('submit', { title: submitData.title }) // 至少传递标题用于识别
        handleClose()
      }, 300)
    }
  } catch (error) {
    console.error('表单提交错误:', error)
    console.error('错误详情:', {
      message: error.message,
      code: error.code,
      data: error.data,
      fullResponse: error.fullResponse,
    })
    showAlertMessage(error.message || '提交失败，请稍后重试', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const validateField = (field) => {
  formErrors[field] = ''

  if (field === 'title') {
    if (!formData.title.trim()) {
      formErrors.title = '标题不能为空'
    } else if (formData.title.length > 50) {
      formErrors.title = '标题不能超过50个字符'
    }
  }

  if (field === 'content') {
    if (!formData.content.trim()) {
      formErrors.content = '内容不能为空'
    } else if (formData.content.length > 1000) {
      formErrors.content = '内容不能超过1000个字符'
    }
  }

  if (field === 'visibility') {
    if (!formData.visibility) {
      formErrors.visibility = '请选择可见性设置'
    }
  }
}

// #endregion

// #region 4.位置信息
const getCurrentLocation = () => {
  if (!navigator.geolocation) {
    showAlertMessage('浏览器不支持地理位置功能', 'error')
    return
  }

  // 每次定位前重置状态，保证可以多次尝试
  isLocating.value = true
  locationPermission.value = ''
  locationMessage.value = '正在获取位置...'

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const lat = position.coords.latitude
      const lng = position.coords.longitude
      locationInfo.lat = lat
      locationInfo.lng = lng
      locationPermission.value = 'granted'
      locationMessage.value = '位置获取成功'
      console.log('位置获取成功：', position)
      // 尝试获取详细地址
      try {
        console.log('开始解析地址...')
        const address = await getAddressFromCoords(lat, lng) //TODO
        console.log('解析到的地址：', address)
        locationInfo.address = address
      } catch (error) {
        console.error('地址解析失败的错误:', error.message)
        locationInfo.address = `位置 (${lat.toFixed(6)}, ${lng.toFixed(6)})`
      }
      // 不再自动设置formData.location，让用户手动决定
      formData.lat = lat
      formData.lng = lng
      isLocating.value = false
    },
    (error) => {
      isLocating.value = false
      locationPermission.value = 'denied'

      // 设置默认位置信息，确保可以提交
      const defaultLat = 39.9005
      const defaultLng = 116.302
      locationInfo.lat = defaultLat
      locationInfo.lng = defaultLng
      locationInfo.address = '默认位置（定位失败）'
      formData.lat = defaultLat
      formData.lng = defaultLng

      // 只提示，不阻塞表单提交
      switch (error.code) {
        case 1:
          locationMessage.value = '位置权限被拒绝，已使用默认位置'
          showAlertMessage(
            '位置权限被拒绝，已使用默认位置，您仍可提交胶囊',
            'warning'
          )
          break
        case 2:
          locationMessage.value = '位置信息不可用，已使用默认位置'
          showAlertMessage(
            '无法获取位置信息，已使用默认位置，您仍可提交胶囊',
            'warning'
          )
          break
        case 3:
          locationMessage.value = '位置请求超时，已使用默认位置'
          showAlertMessage(
            '位置请求超时，已使用默认位置，您仍可提交胶囊',
            'warning'
          )
          break
        default:
          locationMessage.value = '位置获取失败，已使用默认位置'
          showAlertMessage(
            '位置获取失败，已使用默认位置，您仍可提交胶囊',
            'warning'
          )
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    }
  )
}

const useAutoLocation = () => {
  if (locationInfo.address && locationInfo.address !== '未获取到自动定位') {
    formData.address = locationInfo.address
    showAlertMessage('已使用自动定位的地址', 'success')
  }
}

/**
 * 使用高德地图 API 将经纬度转换为详细地址
 * @param {number} lat - 纬度
 * @param {number} lng - 经度
 * @returns {Promise<string>} 详细地址字符串
 */
const getAddressFromCoords = (lat, lng) => {
  return new Promise((resolve, reject) => {
    if (typeof AMap === 'undefined') {
      return reject(new Error('高德地图 AMap 对象未初始化，请检查 HTML 引入'))
    }

    // 核心修改：使用 AMap.plugin 确保 Geocoder 插件已加载
    AMap.plugin(['AMap.Geocoder'], () => {
      try {
        // 1. 在插件加载成功回调中创建 Geocoder 实例
        // @ts-ignore
        const geocoder = new AMap.Geocoder({
          radius: 1000,
          extensions: 'all',
        })

        // 2. 调用逆地理编码服务
        geocoder.getAddress([lng, lat], (status, result) => {
          if (status === 'complete' && result.regeocode) {
            // 成功获取地址
            const address = result.regeocode.formattedAddress
            resolve(address)
          } else {
            // 失败处理
            console.error('逆地理编码失败:', result)
            reject(
              new Error('未能解析到详细地址: ' + (result?.info || '未知原因'))
            )
          }
        })
      } catch (error) {
        reject(new Error('创建 AMap.Geocoder 实例失败: ' + error.message))
      }
    })
  })
}

// #endregion

// #region 5.解锁条件
const minDateTime = computed(() => {
  const now = new Date()
  // 补零函数
  const pad = (n) => String(n).padStart(2, '0')

  const year = now.getFullYear()
  const month = pad(now.getMonth() + 1)
  const day = pad(now.getDate())
  const hours = pad(now.getHours())
  const minutes = pad(now.getMinutes())

  // 返回格式：2023-10-27T15:30
  return `${year}-${month}-${day}T${hours}:${minutes}`
})
// #endregion

// #region 6. 媒体文件上传

/**
 * 触发隐藏的文件输入框点击事件
 */
const triggerFileInput = () => {
  if (fileInputRef.value && !isUploading.value && mediaFiles.value.length < 5) {
    fileInputRef.value.click()
  }
}

/**
 * 处理文件拖放事件
 * @param {DragEvent} event - 拖放事件
 */
const handleFileDrop = (event) => {
  isDragging.value = false
  if (isUploading.value || mediaFiles.value.length >= 5) return

  const droppedFiles = event.dataTransfer.files
  if (droppedFiles && droppedFiles.length > 0) {
    // 将文件列表传递给 handleFileUpload 进行处理
    // 注意：这里需要模拟 event.target.files 结构
    handleFileUpload({ target: { files: droppedFiles, value: null } })
  }
}

/**
 * 移除媒体文件
 * @param {number} index - 媒体文件在数组中的索引
 */
const removeMediaFile = (index) => {
  const fileToRemove = mediaFiles[index]

  // 释放本地 Object URL，防止内存泄漏
  if (fileToRemove && fileToRemove.local_url) {
    URL.revokeObjectURL(fileToRemove.local_url)
  }

  mediaFiles.value.splice(index, 1)
}

/**
 * 处理多文件选择和上传
 * 使用导入的 uploadFile API
 * @param {Event} event - change 事件
 */
const handleFileUpload = async (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return

  uploadErrorStatus.value = false

  const filesToUpload = Array.from(files).filter((file) => {
    const isImage = file.type.startsWith('image/')
    const isVideo = file.type.startsWith('video/')
    const isAudio = file.type.startsWith('audio/') 
    return isImage || isVideo || isAudio
  })

  if (filesToUpload.length === 0) {
    showAlertMessage('未识别到有效的图片或视频文件', 'warning')
    return
  }

  isUploading.value = true
  console.log('🚀 开始进入上传循环...')

  try {
    for (const file of filesToUpload) {
      // 检查大小限制（例如 100MB）
      if (file.size > 100 * 1024 * 1024) {
        showAlertMessage(`文件 ${file.name} 过大，超过100MB限制`, 'error')
        continue
      }

      // 3. 【优化】只有小文件才生成预览，大文件直接上传，减少内存压力
      let localPreviewUrl = ''
      if (file.size < 10 * 1024 * 1024) {
        localPreviewUrl = URL.createObjectURL(file)
      }

      console.log(`📤 正在调用 API 上传: ${file.name}`)

      try {
        const uploadResult = await uploadFile(file)

        let finalType = 'image'
        if (file.type.startsWith('video/')) {
          finalType = 'video'
        } 
        else if (file.type.startsWith('audio/')) {
          finalType = 'audio'
        }

        mediaFiles.value.push({
          id: uploadResult.file_id || uploadResult.id,
          url: uploadResult.url || uploadResult, // 兼容不同的返回格式
          type: finalType,
          name: file.name,
          tempUrl: localPreviewUrl,
        })
      } catch (uploadError) {
        console.error(`❌ ${file.name} 上传失败:`, uploadError)
        uploadErrorStatus.value = true
        showAlertMessage(
          `${file.name} 上传失败: ${uploadError.message || '服务器响应异常'}`,
          'error'
        )
      }
    }
  } catch (globalError) {
    console.error('🔥 全局循环崩溃:', globalError)
  } finally {
    isUploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = null
    console.log('--- 上传流程结束 ---')
  }
}
// #endregion

// #region 7. 标签管理
const handleTagInput = (event) => {
  if (['Enter', ','].includes(event.key)) {
    event.preventDefault()
    addTag(tagInput.value.trim())
  }
}

const addTag = (tag) => {
  if (!tag) return

  if (selectedTags.value.length >= 5) {
    showAlertMessage('最多只能添加5个标签', 'error')
    return
  }

  if (selectedTags.value.includes(tag)) {
    showAlertMessage('标签已存在', 'error')
    return
  }

  selectedTags.value.push(tag)
  tagInput.value = ''
}

const removeTag = (index) => {
  selectedTags.value.splice(index, 1)
}

const addSuggestedTag = (tag) => {
  if (selectedTags.value.length < 5 && !selectedTags.value.includes(tag)) {
    selectedTags.value.push(tag)
  }
}
// #endregion

const showAlertMessage = (message, type = 'error') => {
  alertText.value = message
  alertType.value = type
  alertIcon.value =
    type === 'success'
      ? 'fas fa-check-circle'
      : type === 'warning'
      ? 'fas fa-exclamation-triangle'
      : 'fas fa-exclamation-circle'
  showAlert.value = true

  // --- 新增滚动代码 ---
  // 使用 nextTick 确保 DOM 更新后（即提示框显示后）再滚动
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTo({
        top: 0,
        behavior: 'smooth', // 平滑滚动
      })
    }
  })

  setTimeout(() => {
    showAlert.value = false
  }, 7000)
}
</script>

<style scoped>
/* 原有的所有样式保持不变 */
.capsule-form-modal {
  position: fixed;
  inset: 0;
  display: none;
  z-index: 1000;
}

.capsule-form-modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(8, 12, 20, 0.6);
  backdrop-filter: blur(8px);
}

.modal-panel {
  position: relative;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  min-height: 320px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  z-index: 1001;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
}

.modal-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  flex: 1;
}

.modal-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.form-alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  margin: 16px 20px;
  border-radius: 12px;
  font-size: 14px;
}

.form-alert.success {
  background: rgba(16, 185, 129, 0.1);
  color: #065f46;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.form-alert.error {
  background: rgba(239, 68, 68, 0.1);
  color: #991b1b;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.form-alert.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.alert-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  opacity: 0.7;
}

.alert-close:hover {
  opacity: 1;
}

.capsule-form {
  padding: 0 20px 20px;
}

.form-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.section-icon {
  font-size: 18px;
  color: #6c8cff;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.required-badge {
  background: #ef4444;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.optional-badge {
  background: #6b7280;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #6c8cff;
  box-shadow: 0 0 0 3px rgba(108, 140, 255, 0.1);
}

.form-input.input-error,
.form-textarea.input-error {
  border-color: #ef4444;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.char-count {
  font-size: 12px;
  color: #6b7280;
}

.error-text {
  font-size: 12px;
  color: #ef4444;
  font-weight: 500;
}

.location-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.address-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auto-location-wrapper {
  padding: 16px;
  background: rgba(108, 140, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(108, 140, 255, 0.1);
}

.location-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.use-auto-location {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.btn-outline {
  background: transparent;
  color: #6c8cff;
  border: 1px solid #6c8cff;
}

.btn-outline:hover:not(:disabled) {
  background: #6c8cff;
  color: white;
  transform: translateY(-1px);
}

.location-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.location-icon {
  font-size: 20px;
  color: #6c8cff;
}

.location-text {
  flex: 1;
}

.location-address {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.location-coords {
  font-size: 12px;
  color: #6b7280;
}

.location-btn {
  background: #6c8cff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.location-btn:hover:not(:disabled) {
  background: #5a7cff;
  transform: translateY(-1px);
}

.location-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.location-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
}

.text-success {
  color: #10b981;
}
.text-danger {
  color: #ef4444;
}
.text-warning {
  color: #f59e0b;
}

.image-upload-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-area {
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.upload-area:hover {
  border-color: #6c8cff;
  background: #f8faff;
}

.upload-area.has-image {
  padding: 0;
  border-style: solid;
  overflow: hidden;
}

.upload-placeholder {
  color: #6b7280;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: #cbd5e1;
}

.upload-text {
  font-weight: 500;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 12px;
  color: #9ca3af;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-image:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6c8cff, #5a7cff);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #6b7280;
  min-width: 40px;
}

.visibility-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.visibility-option {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.visibility-option:hover {
  border-color: #cbd5e1;
}

.visibility-option.active {
  border-color: #6c8cff;
  background: rgba(108, 140, 255, 0.05);
}

.vis-radio {
  display: none;
}

.option-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.option-icon {
  font-size: 20px;
  color: #6c8cff;
}

.option-text {
  flex: 1;
}

.option-title {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 2px;
}

.option-desc {
  font-size: 12px;
  color: #6b7280;
}

.tags-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tags-input-wrapper {
  position: relative;
}

.tags-input {
  width: 100%;
  padding: 12px 16px;
  padding-right: 60px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

.tags-input:focus {
  outline: none;
  border-color: #6c8cff;
  box-shadow: 0 0 0 3px rgba(108, 140, 255, 0.1);
}

.tags-count {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #6b7280;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #6c8cff, #5a7cff);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.remove-tag {
  background: none;
  border: none;
  color: white;
  font-size: 10px;
  cursor: pointer;
  opacity: 0.8;
  padding: 2px;
}

.remove-tag:hover {
  opacity: 1;
}

.suggested-tags {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.suggested-label {
  font-size: 12px;
  color: #6b7280;
}

.suggested-tag {
  background: #f1f5f9;
  color: #475569;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.suggested-tag:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 20px 0 0;
  margin-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.btn-primary {
  background: linear-gradient(135deg, #6c8cff, #5a7cff);
  color: white;
  box-shadow: 0 4px 12px rgba(108, 140, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 140, 255, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-panel {
    width: 95%;
    margin: 20px;
  }

  .modal-header {
    padding: 20px;
  }

  .modal-title {
    font-size: 20px;
  }

  .capsule-form {
    padding: 0 16px 16px;
  }

  .form-section {
    padding: 16px;
  }

  .location-display {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .form-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }
}

/* 滚动条样式 */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.modal-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.unlock-conditions-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  background: white
    url("data:image/svg+xml,%3csvg xmlns='[http://www.w3.org/2000/svg](http://www.w3.org/2000/svg)' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23334155' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3e%3c/svg%3e")
    no-repeat right 16px center;
  background-size: 12px 12px;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #6c8cff;
  box-shadow: 0 0 0 3px rgba(108, 140, 255, 0.1);
}

.dynamic-input {
  /* 确保动态输入部分有足够的空间 */
  min-height: 80px;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-with-unit .form-input {
  flex: 1;
}

.input-unit {
  white-space: nowrap;
  font-size: 14px;
  color: #6b7280;
  padding-right: 8px;
}
.upload-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-drop-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 20px;
  border: 2px dashed #cbd5e1; /* 默认虚线边框 */
  border-radius: 12px;
  background-color: #f8fafc;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-drop-area:hover,
.upload-drop-area.is-active {
  border-color: #6c8cff; /* 鼠标悬停或拖拽时的颜色 */
  background-color: #f8faff;
}

.upload-drop-area.is-active {
  background-color: #eef2ff;
}

.upload-drop-area.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
  border-color: #e2e8f0;
  background-color: #f1f5f9;
}

/* 错误状态下的样式 */
.upload-drop-area.has-error {
  border-color: #ef4444 !important; /* 强制显示红色 */
  background-color: rgba(239, 68, 68, 0.05);
  animation: shake 0.4s ease-in-out; /* 增加抖动动画 */
}

.upload-drop-area.has-error .upload-icon,
.upload-drop-area.has-error .upload-text {
  color: #ef4444;
}

/* 抖动动画定义 */
@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-6px);
  }
  75% {
    transform: translateX(6px);
  }
}

.upload-icon {
  font-size: 36px;
  color: #6c8cff;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  color: #475569;
  font-weight: 500;
  margin: 0 0 4px 0;
}

.upload-link {
  color: #6c8cff;
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.upload-drop-area.is-disabled .upload-link {
  color: #6b7280;
  text-decoration: none;
}

.upload-hint {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
}

.uploaded-files-list {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  background-color: #f8fafc;
}

.uploaded-file-item {
  display: flex;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 14px;
}

.uploaded-file-item:last-child {
  border-bottom: none;
}

.file-icon {
  color: #64748b;
  margin-right: 8px;
  width: 16px;
  text-align: center;
}

.file-name {
  flex-grow: 1;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.remove-file-button {
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0 4px;
  margin-left: 12px;
}

.uploaded-files-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
  padding: 10px;
  background-color: #f8f8f8;
  border-radius: 8px;
}

.uploaded-file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 10px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background-color: #fff;
  transition: all 0.2s ease;
}

.uploaded-file-item:hover {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.file-preview-wrapper {
  width: 40px;
  height: 40px;
  flex-shrink: 0; /* 防止被挤压 */
  border-radius: 4px;
  overflow: hidden;
  background-color: #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-preview-audio {
  color: #6c8cff;
  font-size: 18px;
}

.file-name {
  flex-grow: 1; /* 占据剩余空间 */
  font-size: 14px;
  color: #334155;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis; /* 文本过长时显示省略号 */
}

.file-remove-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  transition: color 0.2s ease;
  flex-shrink: 0; /* 防止被挤压 */
}

.file-remove-btn:hover {
  color: #ef4444; /* 红色删除图标 */
}

.file-remove-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.audio-icon {
  font-size: 20px;
}

/* CapsuleForm.vue <style> */
.btn-draft {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  margin-right: auto; /* 将保存草稿按钮推向最左侧 */
}

.btn-draft:hover {
  background-color: #e5e7eb;
}
</style>
