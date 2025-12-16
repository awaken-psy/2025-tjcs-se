<template>
  <div class="event-edit-modal" :class="{ active: show }">
    <div class="modal-overlay" @click="handleClose"></div>
    <div class="modal-content">
      <!-- 头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas fa-edit"></i>
          编辑活动
        </h2>
        <button class="close-btn" @click="handleClose">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <!-- 表单 -->
      <form class="edit-form" @submit.prevent="handleSubmit">
        <div class="form-body">
          <!-- 活动名称 -->
          <div class="form-group">
            <label class="form-label">
              <span class="required">*</span> 活动名称
            </label>
            <input
              v-model="formData.name"
              type="text"
              class="form-input"
              placeholder="请输入活动名称（1-100字符）"
              maxlength="100"
              required
              :class="{ error: errors.name }"
            />
            <div class="form-footer">
              <span class="char-count">{{ formData.name.length }}/100</span>
              <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
            </div>
          </div>
          
          <!-- 活动描述 -->
          <div class="form-group">
            <label class="form-label">
              <span class="required">*</span> 活动描述
            </label>
            <textarea
              v-model="formData.description"
              class="form-textarea"
              rows="4"
              placeholder="请输入活动描述"
              required
              :class="{ error: errors.description }"
            ></textarea>
            <div class="form-footer">
              <span class="char-count">{{ formData.description.length }}/500</span>
              <span v-if="errors.description" class="error-text">{{ errors.description }}</span>
            </div>
          </div>
          
          <!-- 时间地点 -->
          <div class="form-row">
            <div class="form-group half">
              <label class="form-label">
                <span class="required">*</span> 活动时间
              </label>
              <input
                v-model="formData.date"
                type="datetime-local"
                class="form-input"
                required
                :class="{ error: errors.date }"
              />
              <div class="form-footer">
                <span v-if="errors.date" class="error-text">{{ errors.date }}</span>
              </div>
            </div>
            
            <div class="form-group half">
              <label class="form-label">
                <span class="required">*</span> 活动地点
              </label>
              <input
                v-model="formData.location"
                type="text"
                class="form-input"
                placeholder="请输入活动地点"
                required
                :class="{ error: errors.location }"
              />
              <div class="form-footer">
                <span v-if="errors.location" class="error-text">{{ errors.location }}</span>
              </div>
            </div>
          </div>
          
          <!-- 标签 -->
          <div class="form-group">
            <label class="form-label">
              活动标签（可选）
            </label>
            <div class="tags-input-wrapper">
              <input
                v-model="tagInput"
                type="text"
                class="form-input"
                placeholder="输入标签后按回车添加"
                @keydown.enter.prevent="addTag"
              />
              <span class="tags-count">{{ formData.tags.length }}/5</span>
            </div>
            
            <!-- 已选标签 -->
            <div class="selected-tags" v-if="formData.tags.length > 0">
              <div class="tag-item" v-for="(tag, index) in formData.tags" :key="index">
                <span class="tag-text">{{ tag }}</span>
                <button type="button" class="remove-tag" @click="removeTag(index)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <!-- 推荐标签 -->
            <div class="suggested-tags">
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
          
          <!-- 封面图片 -->
          <div class="form-group">
            <label class="form-label">
              封面图片（可选）
            </label>
            <div 
              class="upload-area"
              :class="{ 'has-image': formData.cover_img }"
              @click="$refs.fileInput.click()"
            >
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                style="display: none"
                @change="handleFileSelect"
              />
              
              <div v-if="!formData.cover_img" class="upload-placeholder">
                <i class="fas fa-cloud-upload-alt upload-icon"></i>
                <p class="upload-text">点击上传封面图片</p>
                <p class="upload-hint">支持 JPG、PNG、GIF，建议大小不超过2MB</p>
              </div>
              
              <div v-else class="image-preview">
                <img :src="formData.cover_img" alt="预览" class="preview-img" />
                <button type="button" class="remove-image" @click.stop="removeImage">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
            
            <!-- 图片链接输入 -->
            <div class="link-input-container" v-if="!formData.cover_img">
              <input
                v-model="imageLink"
                type="url"
                class="form-input link-input"
                placeholder="或者输入图片链接"
                @keydown.enter.prevent="addImageFromLink"
              />
              <button type="button" class="btn small" @click="addImageFromLink">
                使用链接
              </button>
            </div>
          </div>
          
          <!-- 错误提示 -->
          <div v-if="formAlert.show" class="form-alert" :class="formAlert.type">
            <div class="alert-content">
              <i :class="formAlert.icon"></i>
              <span>{{ formAlert.message }}</span>
            </div>
            <button type="button" class="alert-close" @click="hideAlert">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        
        <!-- 底部操作 -->
        <div class="form-actions">
          <button type="button" class="btn secondary" @click="handleClose" :disabled="isSubmitting">
            <i class="fas fa-times"></i> 取消
          </button>
          <button type="submit" class="btn primary" :disabled="!isFormValid || isSubmitting">
            <i class="fas fa-save"></i>
            {{ isSubmitting ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  event: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close', 'save'])

// 表单数据
const formData = reactive({
  name: '',
  description: '',
  date: '',
  location: '',
  tags: [],
  cover_img: ''
})

// 表单错误
const errors = reactive({
  name: '',
  description: '',
  date: '',
  location: ''
})

// 标签输入
const tagInput = ref('')
const imageLink = ref('')

// 状态
const isSubmitting = ref(false)

// 表单提示
const formAlert = reactive({
  show: false,
  type: 'error',
  message: '',
  icon: 'fas fa-exclamation-circle'
})

// 推荐标签
const suggestedTags = ref(['校园活动', '音乐节', '体育比赛', '学术讲座', '文化节', '社团活动', '志愿者', '招聘会'])

// 文件输入引用
const fileInput = ref(null)

// 表单验证
const isFormValid = computed(() => {
  return (
    formData.name.trim().length >= 1 &&
    formData.name.trim().length <= 100 &&
    formData.description.trim().length >= 1 &&
    formData.date !== '' &&
    formData.location.trim().length >= 1 &&
    !errors.name &&
    !errors.description &&
    !errors.date &&
    !errors.location
  )
})

// 监听表单变化
watch(() => formData.name, validateName)
watch(() => formData.description, validateDescription)
watch(() => formData.date, validateDate)
watch(() => formData.location, validateLocation)

// 组件挂载时初始化表单数据
onMounted(() => {
  if (props.event && props.event.id) {
    formData.name = props.event.name || ''
    formData.description = props.event.description || ''
    formData.date = formatDateForInput(props.event.date)
    formData.location = props.event.location || ''
    formData.tags = props.event.tags || []
    formData.cover_img = props.event.cover_img || ''
  }
})

// 监听props.event变化，当编辑不同活动时更新表单
watch(() => props.event, (newEvent) => {
  if (newEvent && newEvent.id) {
    formData.name = newEvent.name || ''
    formData.description = newEvent.description || ''
    formData.date = formatDateForInput(newEvent.date)
    formData.location = newEvent.location || ''
    formData.tags = newEvent.tags || []
    formData.cover_img = newEvent.cover_img || ''
  }
}, { deep: true })

// 格式化日期为input格式
function formatDateForInput(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// 验证函数
function validateName() {
  if (!formData.name.trim()) {
    errors.name = '活动名称不能为空'
  } else if (formData.name.length > 100) {
    errors.name = '活动名称不能超过100个字符'
  } else {
    errors.name = ''
  }
}

function validateDescription() {
  if (!formData.description.trim()) {
    errors.description = '活动描述不能为空'
  } else if (formData.description.length > 500) {
    errors.description = '活动描述不能超过500个字符'
  } else {
    errors.description = ''
  }
}

function validateDate() {
  if (!formData.date) {
    errors.date = '活动时间不能为空'
  } else {
    errors.date = ''
  }
}

function validateLocation() {
  if (!formData.location.trim()) {
    errors.location = '活动地点不能为空'
  } else if (formData.location.length > 200) {
    errors.location = '活动地点不能超过200个字符'
  } else {
    errors.location = ''
  }
}

// 标签操作
function addTag() {
  const tag = tagInput.value.trim()
  if (tag && !formData.tags.includes(tag) && formData.tags.length < 5) {
    formData.tags.push(tag)
    tagInput.value = ''
  }
}

function removeTag(index) {
  formData.tags.splice(index, 1)
}

function addSuggestedTag(tag) {
  if (!formData.tags.includes(tag) && formData.tags.length < 5) {
    formData.tags.push(tag)
  }
}

// 图片操作
function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return

  // 检查文件类型
  if (!file.type.startsWith('image/')) {
    showAlert('请选择图片文件', 'error')
    return
  }

  // 检查文件大小 (2MB)
  if (file.size > 2 * 1024 * 1024) {
    showAlert('图片大小不能超过2MB', 'error')
    return
  }

  // 读取文件
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.cover_img = e.target.result
  }
  reader.onerror = () => {
    showAlert('图片读取失败，请重试', 'error')
  }
  reader.readAsDataURL(file)
}

function removeImage() {
  formData.cover_img = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function addImageFromLink() {
  const link = imageLink.value.trim()
  if (link && (link.startsWith('http://') || link.startsWith('https://'))) {
    formData.cover_img = link
    imageLink.value = ''
  } else {
    showAlert('请输入有效的图片链接', 'error')
  }
}

// 表单操作
function handleClose() {
  if (!isSubmitting.value) {
    resetForm()
    emit('close')
  }
}

async function handleSubmit() {
  // 验证所有字段
  validateName()
  validateDescription()
  validateDate()
  validateLocation()

  // 检查是否有错误
  if (Object.values(errors).some(error => error !== '') || !isFormValid.value) {
    showAlert('请检查表单中的错误', 'error')
    return
  }

  isSubmitting.value = true
  
  try {
    // 准备提交数据 - 包含图片的base64数据
    const submitData = {
      name: formData.name.trim(),
      description: formData.description.trim(),
      date: formatDateForAPI(formData.date),
      location: formData.location.trim(),
      tags: formData.tags,
      ...(formData.cover_img.trim() && { cover_img: formData.cover_img.trim() })
    }

    console.log('提交编辑活动数据:', submitData)
    emit('save', submitData)
  } catch (error) {
    console.error('表单提交错误:', error)
    showAlert(error.message || '表单提交失败', 'error')
    isSubmitting.value = false
  }
}

function resetForm() {
  formData.name = ''
  formData.description = ''
  formData.date = ''
  formData.location = ''
  formData.tags = []
  formData.cover_img = ''
  tagInput.value = ''
  imageLink.value = ''
  Object.keys(errors).forEach(key => errors[key] = '')
  isSubmitting.value = false
  hideAlert()
}

// 格式化日期为API格式
function formatDateForAPI(dateString) {
  const date = new Date(dateString)
  return date.toISOString()
}

// 提示信息
function showAlert(message, type = 'error') {
  formAlert.show = true
  formAlert.type = type
  formAlert.message = message
  formAlert.icon = type === 'success' ? 'fas fa-check-circle' :
    type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-exclamation-circle'
}

function hideAlert() {
  formAlert.show = false
}
</script>

<style scoped>
.event-edit-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 1003;
  padding: 20px;
}

.event-edit-modal.active {
  display: flex;
  animation: fadeIn 0.3s ease;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 600px;
  height: auto;
  max-height: 90vh;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 30px;
  border-bottom: 1px solid rgba(230, 236, 240, 0.6);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  flex-shrink: 0;
}

.modal-title {
  font-size: 22px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.close-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #718096;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  transform: rotate(90deg);
}

.edit-form {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.form-body {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
  max-height: calc(90vh - 140px); /* 减去头部和底部的高度 */
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.form-label .required {
  color: #e53e3e;
  margin-right: 4px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  font-size: 15px;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  background: white;
  color: #2d3748;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.1);
  transform: translateY(-1px);
}

.form-input.error,
.form-textarea.error {
  border-color: #e53e3e;
  box-shadow: 0 0 0 4px rgba(229, 62, 62, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  max-height: 200px;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  font-size: 13px;
}

.char-count {
  color: #718096;
}

.error-text {
  color: #e53e3e;
  font-weight: 500;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row .form-group {
  margin-bottom: 0;
  flex: 1;
  min-width: 0; /* 防止flex项目溢出 */
}

/* 标签相关样式 */
.tags-input-wrapper {
  position: relative;
}

.tags-input-wrapper .form-input {
  padding-right: 50px;
}

.tags-count {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 13px;
  color: #a0aec0;
  background: white;
  padding: 2px 6px;
  border-radius: 10px;
  pointer-events: none;
}

.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(66, 153, 225, 0.1);
  color: #4299e1;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  max-width: 100%;
}

.tag-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-tag {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 12px;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.remove-tag:hover {
  background: rgba(255, 255, 255, 0.3);
}

.suggested-tags {
  margin-top: 12px;
  max-height: 120px;
  overflow-y: auto;
  padding: 12px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  width: 100%;
  box-sizing: border-box;
}

/* 自定义滚动条样式 */
.suggested-tags::-webkit-scrollbar {
  width: 8px;
}

.suggested-tags::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.suggested-tags::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.suggested-tags::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.suggested-tags::-webkit-scrollbar-corner {
  background: transparent;
}

/* Firefox 滚动条样式 */
.suggested-tags {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f1f5f9;
}

.suggested-label {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
  margin-right: 8px;
  margin-bottom: 8px;
  display: inline-block;
}

.suggested-tag {
  display: inline-block;
  margin-right: 8px;
  margin-bottom: 8px;
  padding: 4px 12px;
  background: rgba(26, 138, 152, 0.08);
  color: #2c7a8f;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggested-tag:hover {
  background: #38b2ac;
  color: white;
  transform: translateY(-1px);
}

/* 上传区域 */
.upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 16px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f8fafc;
  position: relative;
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.upload-area:hover {
  border-color: #4299e1;
  background: rgba(66, 153, 225, 0.02);
}

.upload-area.has-image {
  border-color: #4299e1;
  background: rgba(66, 153, 225, 0.02);
  padding: 0;
  min-height: 200px;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  max-width: 100%;
  padding: 10px;
}

.upload-icon {
  font-size: 40px;
  color: #a0aec0;
}

.upload-text {
  font-size: 16px;
  font-weight: 500;
  color: #4a5568;
  margin: 0;
  word-break: break-word;
  text-align: center;
}

.upload-hint {
  font-size: 13px;
  color: #a0aec0;
  margin: 0;
  word-break: break-word;
  text-align: center;
}

.image-preview {
  width: 100%;
  height: 200px;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: all 0.2s ease;
  z-index: 2;
}

.remove-image:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

.link-input-container {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  width: 100%;
}

.link-input {
  flex: 1;
  min-width: 0;
}

.btn.small {
  flex-shrink: 0;
  white-space: nowrap;
}

.btn {
  padding: 12px 24px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  font-size: 15px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-sizing: border-box;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn.primary {
  background: linear-gradient(90deg, #4299e1, #38b2ac);
  color: white;
  box-shadow: 0 6px 16px rgba(66, 153, 225, 0.2);
}

.btn.primary:hover:not(:disabled) {
  background: linear-gradient(90deg, #3182ce, #319795);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(66, 153, 225, 0.25);
}

.btn.secondary {
  background: transparent;
  color: #718096;
  border: 1px solid #e2e8f0;
}

.btn.secondary:hover:not(:disabled) {
  background: rgba(66, 153, 225, 0.05);
  border-color: #4299e1;
  color: #4299e1;
  transform: translateY(-2px);
}

.btn.small {
  padding: 8px 16px;
  font-size: 14px;
}

/* 表单提示 */
.form-alert {
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

.form-alert::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 4px;
}

.form-alert.success {
  background: rgba(72, 187, 120, 0.1);
  color: #2f855a;
  border: 1px solid rgba(72, 187, 120, 0.2);
}

.form-alert.success::before {
  background: #48bb78;
}

.form-alert.error {
  background: rgba(229, 62, 62, 0.1);
  color: #c53030;
  border: 1px solid rgba(229, 62, 62, 0.2);
}

.form-alert.error::before {
  background: #e53e3e;
}

.form-alert.warning {
  background: rgba(251, 191, 36, 0.1);
  color: #d69e2e;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.form-alert.warning::before {
  background: #f6e05e;
}

.alert-content {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.alert-content span {
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.alert-close {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.alert-close:hover {
  background: rgba(0, 0, 0, 0.05);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 20px 30px;
  border-top: 1px solid rgba(230, 236, 240, 0.6);
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  flex-shrink: 0;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 表单主体滚动条美化 */
.form-body::-webkit-scrollbar {
  width: 8px;
}

.form-body::-webkit-scrollbar-track {
  background: rgba(230, 236, 240, 0.3);
  border-radius: 4px;
  margin: 4px 0;
}

.form-body::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
  border: 2px solid transparent;
  background-clip: padding-box;
}

.form-body::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

@media (max-width: 768px) {
  .event-edit-modal {
    padding: 10px;
  }
  
  .modal-content {
    max-width: 100%;
    max-height: 95vh;
    border-radius: 20px;
    margin: 0;
  }
  
  .modal-header {
    padding: 20px;
  }
  
  .modal-title {
    font-size: 20px;
  }
  
  .form-body {
    padding: 20px;
    max-height: calc(95vh - 130px); /* 移动端调整高度 */
  }
  
  .form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .form-actions {
    padding: 16px 20px;
  }
  
  .btn {
    padding: 10px 20px;
    font-size: 14px;
  }
  
  .upload-area {
    padding: 30px 15px;
  }
  
  .form-input,
  .form-textarea {
    padding: 10px 14px;
    font-size: 14px;
  }
  
  .tags-input-wrapper .form-input {
    padding-right: 45px;
  }
  
  .tags-count {
    font-size: 12px;
    right: 10px;
  }
}

@media (max-width: 480px) {
  .form-body {
    padding: 16px;
  }
  
  .modal-header {
    padding: 18px 16px;
  }
  
  .modal-title {
    font-size: 18px;
  }
  
  .form-actions {
    padding: 14px 16px;
    gap: 12px;
  }
  
  .btn {
    padding: 10px 14px;
    font-size: 13px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .upload-area {
    min-height: 140px;
    padding: 25px 10px;
  }
  
  .upload-area.has-image {
    min-height: 180px;
  }
  
  .image-preview {
    height: 180px;
  }
  
  .upload-icon {
    font-size: 32px;
  }
  
  .upload-text {
    font-size: 14px;
  }
  
  .upload-hint {
    font-size: 12px;
  }
  
  .close-btn {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }
}

/* 防止在小屏幕上溢出 */
@media (max-height: 600px) {
  .form-body {
    max-height: calc(90vh - 120px);
  }
  
  .modal-content {
    max-height: 90vh;
  }
}

/* 更好的滚动条体验 */
.form-body {
  scroll-behavior: smooth;
}

/* 修复移动端点击区域 */
@media (hover: none) and (pointer: coarse) {
  .btn,
  .close-btn,
  .remove-tag,
  .remove-image,
  .alert-close,
  .suggested-tag {
    min-height: 44px;
    min-width: 44px;
  }
  
  .form-input,
  .form-textarea {
    font-size: 16px; /* 防止iOS缩放 */
  }
  
  input[type="datetime-local"] {
    min-height: 44px;
  }
}
</style>