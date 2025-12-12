<template>
  <!-- 胶囊表单组件：支持创建和编辑模式，包含完整表单字段 -->
  <div
    class="capsule-form-modal"
    :class="{ active: isShow }"
  >
    <div
      class="modal-overlay"
      @click="handleClose"
    />
    <div class="modal-panel">
      <!-- 模态框头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          {{ isEdit ? '编辑胶囊' : '创建时光胶囊' }}
        </h2>
        <button
          class="modal-close"
          title="关闭"
          @click="handleClose"
        >
          关闭
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="modal-content">
        <!-- 状态提示 -->
        <div
          v-if="showAlert"
          class="form-alert"
          :class="alertType"
        >
          <div class="alert-content">
            <i
              class="alert-icon"
              :class="alertIcon"
            />
            <span>{{ alertText }}</span>
          </div>
          <button
            class="alert-close"
            @click="showAlert = false"
          >
            <i class="fas fa-times" />
          </button>
        </div>

        <form
          class="capsule-form"
          @submit.prevent="handleSubmit"
        >
          <!-- 1. 胶囊标题 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-heading section-icon" />
              <h3 class="section-title">
                胶囊标题
              </h3>
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
              @blur="validateField('title')"
            >
            <div class="form-footer">
              <span class="char-count">{{ formData.title.length }}/50</span>
              <span
                v-if="formErrors.title"
                class="error-text"
              >{{ formErrors.title }}</span>
            </div>
          </div>

          <!-- 2. 胶囊内容 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-edit section-icon" />
              <h3 class="section-title">
                胶囊内容
              </h3>
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
              @blur="validateField('content')"
            />
            <div class="form-footer">
              <span class="char-count">{{ formData.content.length }}/1000</span>
              <span
                v-if="formErrors.content"
                class="error-text"
              >{{ formErrors.content }}</span>
            </div>
          </div>

          <!-- 3. 位置信息 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-map-marker-alt section-icon" />
              <h3 class="section-title">
                位置信息
              </h3>
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
                  maxlength="200"
                >
                <div class="form-footer">
                  <span class="char-count">{{ (formData.address || '').length }}/200</span>
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
                      <div
                        v-if="locationInfo.lat"
                        class="location-coords"
                      >
                        经纬度: {{ locationInfo.lat.toFixed(6) }}, {{ locationInfo.lng.toFixed(6) }}
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    class="location-btn"
                    :disabled="isLocating"
                    @click="getCurrentLocation"
                  >
                    <i
                      class="fas"
                      :class="isLocating ? 'fa-spinner fa-spin' : 'fa-refresh'"
                    />
                    {{ isLocating ? '自动定位' : '重新定位' }}
                  </button>
                </div>
                <div
                  v-if="locationPermission"
                  class="location-status"
                >
                  <i
                    class="fas"
                    :class="locationIcon"
                  />
                  <span>{{ locationMessage }}</span>
                </div>
              </div>

              <!-- 使用自动定位地址按钮 -->
              <div
                v-if="locationInfo.address && locationInfo.address !== '未获取到自动定位'"
                class="use-auto-location"
              >
                <button
                  type="button"
                  class="btn btn-outline"
                  @click="useAutoLocation"
                >
                  <i class="fas fa-copy" />
                  使用自动定位的地址
                </button>
              </div>
            </div>
          </div>

          <!-- 4. 图片上传 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-image section-icon" />
              <h3 class="section-title">
                添加图片
              </h3>
              <span class="optional-badge">选填</span>
            </div>
            <div class="image-upload-section">
              <div
                class="upload-area"
                :class="{ 'has-image': previewImage }"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  accept="image/*"
                  style="display: none"
                  @change="handleImageUpload"
                >
                <div
                  v-if="!previewImage"
                  class="upload-placeholder"
                >
                  <i class="fas fa-cloud-upload-alt upload-icon" />
                  <p class="upload-text">
                    点击上传图片
                  </p>
                  <p class="upload-hint">
                    支持 JPG、PNG 格式，最大 5MB
                  </p>
                </div>
                <div
                  v-else
                  class="image-preview"
                >
                  <img
                    :src="previewImage"
                    alt="预览图片"
                    class="preview-img"
                  >
                  <button
                    type="button"
                    class="remove-image"
                    @click.stop="removeImage"
                  >
                    <i class="fas fa-times" />
                  </button>
                </div>
              </div>
              <div
                v-if="uploadProgress > 0"
                class="upload-progress"
              >
                <div class="progress-bar">
                  <div
                    class="progress-fill"
                    :style="{ width: uploadProgress + '%' }"
                  />
                </div>
                <span class="progress-text">{{ uploadProgress }}%</span>
              </div>
            </div>
          </div>

          <!-- 5. 可见性设置 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-eye section-icon" />
              <h3 class="section-title">
                可见性设置
              </h3>
              <span class="required-badge">必填</span>
            </div>
            <div class="visibility-options">
              <label
                v-for="option in visibilityOptions"
                :key="option.key"
                class="visibility-option"
                :class="{ active: formData.visibility === option.key }"
              >
                <input
                  v-model="formData.visibility"
                  type="radio"
                  name="visibility"
                  :value="option.key"
                  class="vis-radio"
                >
                <div class="option-content">
                  <i
                    class="option-icon"
                    :class="option.icon"
                  />
                  <div class="option-text">
                    <div class="option-title">{{ option.label }}</div>
                    <div class="option-desc">{{ option.desc }}</div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <!-- 6. 标签管理 -->
          <div class="form-section">
            <div class="section-header">
              <i class="fas fa-tags section-icon" />
              <h3 class="section-title">
                添加标签
              </h3>
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
                  @keydown="handleTagInput"
                >
                <span class="tags-count">{{ selectedTags.length }}/5</span>
              </div>
              <div
                v-if="selectedTags.length > 0"
                class="selected-tags"
              >
                <span
                  v-for="(tag, index) in selectedTags"
                  :key="index"
                  class="tag-item"
                >
                  {{ tag }}
                  <button
                    type="button"
                    class="remove-tag"
                    @click="removeTag(index)"
                  >
                    <i class="fas fa-times" />
                  </button>
                </span>
              </div>
              <div
                v-if="suggestedTags.length > 0"
                class="suggested-tags"
              >
                <span class="suggested-label">推荐标签：</span>
                <span
                  v-for="tag in suggestedTags"
                  :key="tag"
                  class="suggested-tag"
                  @click="addSuggestedTag(tag)"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>

          <!-- 表单操作 -->
          <div class="form-actions">
            <button
              type="button"
              class="btn btn-secondary"
              :disabled="isSubmitting"
              @click="handleClose"
            >
              取消
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting || !isFormValid"
            >
              <i
                v-if="isSubmitting"
                class="fas fa-spinner fa-spin"
              />
              <i
                v-else
                class="fas fa-paper-plane"
              />
              {{ isSubmitting ? '提交中...' : (isEdit ? '更新胶囊' : '创建胶囊') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onUnmounted, reactive, ref, watch } from 'vue'
import { createCapsule,updateCapsule } from '../api/new/capsulesApi.js'
import { uploadFile } from '../api/new/uploadApi.js'

// Props
const props = defineProps({
  isShow: {
    type: Boolean,
    default: false
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  editData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['close', 'submit'])

// 表单数据
const formData = reactive({
  title: '',
  content: '',
  visibility: 'public',
  location: '',
  address: '',  // 添加地址字段
  lat: null,
  lng: null,
  image: null,
  imageUrl: '',
  imageFileId: ''
})

// 表单错误
const formErrors = reactive({
  title: '',
  content: '',
  visibility: ''
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
const suggestedTags = ref(['校园生活', '毕业季', '图书馆', '操场', '食堂', '宿舍', '课堂', '友谊'])

// 图片上传
const fileInput = ref(null)
const previewImage = ref('')
const uploadProgress = ref(0)

// 位置信息
const locationInfo = reactive({
  address: '',
  lat: null,
  lng: null
})
const locationPermission = ref('')
const locationMessage = ref('等待位置授权...')

// 转换函数：将后端返回的可见性值转换为前端表单期望的值
const convertVisibilityToForm = (visibility) => {
  if (!visibility) return 'public'
  switch (visibility) {
    case 'campus': return 'public'  // 后端campus -> 前端public
    case 'public': return 'public'
    case 'friends': return 'friends'
    case 'private': return 'private'
    default: return 'public'
  }
}

// 常量定义
const visibilityOptions = [
  {
    key: 'public',
    label: '校园公开',
    desc: '所有校园用户可见',
    icon: 'fas fa-globe-americas'
  },
  {
    key: 'friends',
    label: '好友可见',
    desc: '仅你的好友可见',
    icon: 'fas fa-user-friends'
  },
  {
    key: 'private',
    label: '仅自己可见',
    desc: '完全私密，仅自己可见',
    icon: 'fas fa-lock'
  }
]

// 计算属性
const isFormValid = computed(() => {
  return formData.title.trim() && 
         formData.content.trim() && 
         formData.visibility &&
         !formErrors.title && 
         !formErrors.content
})

const locationIcon = computed(() => {
  switch (locationPermission.value) {
  case 'granted': return 'fa-check-circle text-success'
  case 'denied': return 'fa-exclamation-circle text-danger'
  default: return 'fa-info-circle text-warning'
  }
})

// 滚动锁定函数
const lockBodyScroll = () => {
  document.body.style.overflow = 'hidden'
}

const unlockBodyScroll = () => {
  document.body.style.overflow = ''
}

// 监听模态框显示状态
watch(() => props.isShow, (show) => {
  if (show) {
    lockBodyScroll()
    // 重置表单状态
    if (!props.isEdit) {
      resetForm()
    }
    // 重置定位相关状态
    locationPermission.value = ''
    locationMessage.value = '正在获取位置...'
    isLocating.value = false
    // 自动获取位置
    nextTick(() => {
      getCurrentLocation()
    })
  } else {
    unlockBodyScroll()
  }
})

// 组件卸载时解锁滚动
onUnmounted(() => {
  unlockBodyScroll()
})

// 监听编辑数据变化
watch(() => props.editData, (newData) => {
  if (props.isEdit && newData) {
    Object.assign(formData, {
      title: newData.title || '',
      content: newData.content || '',
      visibility: convertVisibilityToForm(newData.visibility) || 'public',
      // 注意：location、lat、lng 是表单提交的核心数据
      location: newData.location || '',
      lat: newData.lat || null,
      lng: newData.lng || null,
      imageUrl: newData.imageUrl || newData.img || '',
      imageFileId: newData.imageFileId || ''
    })

    // 同步到 locationInfo 用于界面展示 (这是关键)
    Object.assign(locationInfo, {
      address: newData.location || '已加载历史位置',
      lat: newData.lat || null,
      lng: newData.lng || null
    })

    if (newData.tags) {
      selectedTags.value = Array.isArray(newData.tags) ? [...newData.tags] : []
    }

    // 这里需要根据你的后端返回判断：如果后端返回的是 URL 而不是 File 对象
    if (newData.imageUrl) { // 假设后端返回的字段是 imageUrl
      previewImage.value = newData.imageUrl
      formData.imageUrl = newData.imageUrl // 保持 formData.imageUrl 用于提交
    } else if (newData.image) {
       // 如果 newData.image 是一个文件 URL
      previewImage.value = newData.image 
      formData.imageUrl = newData.image
    }
    // 注意：formData.image 应该只在用户上传新文件时设置 File 对象
  }
}, { immediate: true })

// 方法定义
const resetForm = () => {
  Object.assign(formData, {
    title: '',
    content: '',
    visibility: 'public',
    location: '',
    address: '',  // 重置地址字段
    lat: null,
    lng: null,
    image: null,
    imageUrl: '',
    imageFileId: ''
  })
  selectedTags.value = []
  tagInput.value = ''
  previewImage.value = ''
  uploadProgress.value = 0
  Object.keys(formErrors).forEach(key => {
    formErrors[key] = ''
  })
}

const handleClose = () => {
  emit('close')
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
    async(position) => {
      const lat = position.coords.latitude
      const lng = position.coords.longitude
      locationInfo.lat = lat
      locationInfo.lng = lng
      locationPermission.value = 'granted'
      locationMessage.value = '位置获取成功'
      // 尝试获取详细地址
      try {
        const address = await getAddressFromCoords(lat, lng)
        locationInfo.address = address
      } catch (error) {
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
        showAlertMessage('位置权限被拒绝，已使用默认位置，您仍可提交胶囊', 'warning')
        break
      case 2:
        locationMessage.value = '位置信息不可用，已使用默认位置'
        showAlertMessage('无法获取位置信息，已使用默认位置，您仍可提交胶囊', 'warning')
        break
      case 3:
        locationMessage.value = '位置请求超时，已使用默认位置'
        showAlertMessage('位置请求超时，已使用默认位置，您仍可提交胶囊', 'warning')
        break
      default:
        locationMessage.value = '位置获取失败，已使用默认位置'
        showAlertMessage('位置获取失败，已使用默认位置，您仍可提交胶囊', 'warning')
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  )
}

const useAutoLocation = () => {
  if (locationInfo.address && locationInfo.address !== '未获取到自动定位') {
    formData.address = locationInfo.address
    showAlertMessage('已使用自动定位的地址', 'success')
  }
}

const getAddressFromCoords = async(lat, lng) => {
  // 这里可以集成腾讯地图或高德地图的逆地理编码服务
  // 暂时返回简单的位置描述
  return `位置 (${lat.toFixed(6)}, ${lng.toFixed(6)})`
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件类型和大小
  if (!file.type.startsWith('image/')) {
    showAlertMessage('请选择图片文件', 'error')
    return
  }

  if (file.size > 5 * 1024 * 1024) {
    showAlertMessage('图片大小不能超过5MB', 'error')
    return
  }

  // 显示上传进度
  uploadProgress.value = 20

  try {
    // 创建预览（立即显示，不等待上传完成）
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target.result
    }
    reader.readAsDataURL(file)

    uploadProgress.value = 50

    // 上传图片到服务器
    const uploadResult = await uploadFile(file)

// 上传成功，保存图片URL
      formData.imageUrl = uploadResult.data?.url || uploadResult.data?.access_url
      formData.image = file  // 保留File对象以备后用

      showAlertMessage('图片上传成功', 'success')
      console.log('保存的图片信息:', {
        fileId: formData.imageFileId,
        url: formData.imageUrl,
        size: uploadResult.size
      })

    uploadProgress.value = 100

  } catch (error) {
    console.error('图片上传失败:', error)
    showAlertMessage(`图片上传失败: ${error.message || error}`, 'error')

    // 上传失败时，清除预览
    previewImage.value = ''
    formData.image = null
    formData.imageUrl = ''
    formData.imageFileId = ''

    // 重置文件输入
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } finally {
    // 延迟清除进度条，让用户看到完成状态
    setTimeout(() => {
      uploadProgress.value = 0
    }, 1000)
  }
}

const removeImage = () => {
  previewImage.value = ''
  formData.image = null
  formData.imageUrl = ''
  formData.imageFileId = ''
  uploadProgress.value = 0
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

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

const showAlertMessage = (message, type = 'error') => {
  alertText.value = message
  alertType.value = type
  alertIcon.value = type === 'success' ? 'fas fa-check-circle' : 
    type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-exclamation-circle'
  showAlert.value = true
  
  setTimeout(() => {
    showAlert.value = false
  }, 5000)
}

const handleSubmit = async() => {
  // 验证表单
  validateField('title')
  validateField('content')
  validateField('visibility')
  
  // 检查是否有错误
  const hasErrors = Object.values(formErrors).some(error => error !== '')
  if (hasErrors) {
    showAlertMessage('请检查表单中的错误', 'error')
    return
  }

  // 检查必填字段
  if (!formData.title.trim() || !formData.content.trim() || !formData.visibility) {
    showAlertMessage('请填写所有必填字段', 'error')
    return
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

    // 构造完整的提交数据 (匹配后端期望的格式)
    const submitData = {
      title: formData.title.trim(),
      content: formData.content.trim(),
      visibility: formData.visibility || 'public', // 确保有默认值
      tags: [...selectedTags.value],

      // 位置信息 - 按照后端期望的格式构造
      location: {
        latitude: lat,
        longitude: lng,
        address: location
      },

      // 图片信息 (使用 imageUrl 或 image，取决于后端接收方式)
      // 注意：如果后端只接受 URL，你需要在上传成功后将 formData.imageUrl 设置为最终 URL。
      // 如果 formData.imageUrl 已经存在 (编辑模式下加载的)，则直接使用。
      imageUrl: formData.imageUrl || previewImage.value,

      // 其他统计信息 (通常只在创建时初始化)
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
        id: props.editData.id 
      }
      
      // 调用更新 API
      result = await updateCapsule(props.editData.id, updatePayload) // 假设 updateCapsule 接收 ID 和 payload
      successMessage = '胶囊更新成功！'
      console.log('更新胶囊结果:', result)
    } else {
      // 调用创建 API
      result = await createCapsule(submitData)
      successMessage = '胶囊创建成功！'
      // 性能优化：移除多余的控制台输出
    }


  // 立即处理结果，提升响应速度
    if (result && (result.id || Object.keys(result).length > 0)) {
      // 先显示表单内的成功提示
      showAlertMessage(successMessage, 'success')

      // 同时弹出确认对话框，让用户点击确定
      setTimeout(() => {
        alert(`${successMessage}\n\n胶囊标题：${submitData.title}\n\n点击确定返回胶囊列表`)

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
      fullResponse: error.fullResponse
    })
    showAlertMessage(error.message || '提交失败，请稍后重试', 'error')
  } finally {
    isSubmitting.value = false
  }
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

.form-input, .form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.3s ease;
  background: white;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #6c8cff;
  box-shadow: 0 0 0 3px rgba(108, 140, 255, 0.1);
}

.form-input.input-error, .form-textarea.input-error {
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

.text-success { color: #10b981; }
.text-danger { color: #ef4444; }
.text-warning { color: #f59e0b; }

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
</style>