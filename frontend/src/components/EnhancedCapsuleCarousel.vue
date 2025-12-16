<template>
  <div class="enhanced-capsule-carousel">
    <!-- 轮播图标题和指示器 -->
    <div class="carousel-header">
      <h3 class="carousel-title">
        <i class="fas fa-map-marker-alt"></i>
        附近胶囊
      </h3>
      <div class="carousel-indicators" v-if="totalPages > 1">
        <span 
          v-for="i in totalPages" 
          :key="i"
          class="indicator"
          :class="{ active: currentSlide === i - 1 }"
          @click="goToSlide(i - 1)"
        ></span>
      </div>
    </div>

    <!-- 轮播图容器 -->
    <div class="carousel-container" :class="{ 'single-item': capsules.length === 1 }">
      <!-- 当只有一个胶囊时的特殊处理 -->
      <div v-if="capsules.length === 1" class="single-capsule-container">
        <div class="single-capsule-card">
          <CapsuleCard 
            :capsule="capsules[0]" 
            view-mode="carousel" 
            @view="handleViewCapsule" 
            @like="handleLikeCapsule" 
          />
          <div class="single-card-decoration">
            <div class="decoration-circle"></div>
            <div class="decoration-circle"></div>
            <div class="decoration-circle"></div>
          </div>
        </div>
      </div>

      <!-- 多个胶囊时的轮播图 -->
      <div v-else class="multi-capsule-container">
        <div 
          class="carousel-track" 
          :style="{ transform: `translateX(-${currentSlide * 100}%)` }"
        >
          <!-- 按页面显示胶囊 -->
          <div 
            v-for="pageIndex in totalPages" 
            :key="pageIndex" 
            class="carousel-page"
          >
            <div 
              v-for="(capsule, capsuleIndex) in getCapsulesForPage(pageIndex - 1)" 
              :key="capsule.id || capsuleIndex" 
              class="carousel-slide"
            >
              <CapsuleCard 
                :capsule="capsule" 
                view-mode="carousel" 
                @view="handleViewCapsule" 
                @like="handleLikeCapsule" 
                @click="handleCapsuleClick"
              />
            </div>
          </div>
        </div>

        <!-- 轮播控制按钮 -->
        <div class="carousel-controls" v-if="totalPages > 1">
          <button 
            class="carousel-btn prev" 
            @click="prevSlide"
          >
            <i class="fas fa-chevron-left"></i>
          </button>
          <button 
            class="carousel-btn next" 
            @click="nextSlide"
          >
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态提示 -->
    <div v-if="capsules.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-map-marker-alt"></i>
      </div>
      <h4 class="empty-title">附近暂无胶囊</h4>
      <p class="empty-description">去其他地方探索更多时光胶囊吧！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import CapsuleCard from './CapsuleCard.vue'

const props = defineProps({
  capsules: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view', 'like'])

const router = useRouter()

const currentSlide = ref(0)

// 计算每页显示的胶囊数量
const getCapsulesPerPage = () => {
  const total = props.capsules.length
  if (total <= 4) return total // 4个或以下胶囊，全部显示在一页
  if (total <= 6) return 4     // 5-6个胶囊，每页显示4个
  return 3                      // 7个以上胶囊，每页显示3个
}

// 计算总页数
const totalPages = computed(() => {
  if (props.capsules.length <= 1) return 1
  const perPage = getCapsulesPerPage()
  return Math.ceil(props.capsules.length / perPage)
})

// 获取指定页面的胶囊
const getCapsulesForPage = (pageIndex) => {
  const perPage = getCapsulesPerPage()
  const startIndex = pageIndex * perPage
  const endIndex = startIndex + perPage
  return props.capsules.slice(startIndex, endIndex)
}

// 监听胶囊数量变化，重置轮播位置
watch(() => props.capsules.length, (newLength) => {
  if (newLength === 0) {
    currentSlide.value = 0
  } else if (currentSlide.value >= totalPages.value) {
    currentSlide.value = totalPages.value - 1
  }
})

// 上一张 - 支持循环
const prevSlide = () => {
  if (totalPages.value <= 1) return
  
  if (currentSlide.value === 0) {
    // 如果是第一页，循环到最后一页
    currentSlide.value = totalPages.value - 1
  } else {
    currentSlide.value--
  }
}

// 下一张 - 支持循环
const nextSlide = () => {
  if (totalPages.value <= 1) return
  
  if (currentSlide.value === totalPages.value - 1) {
    // 如果是最后一页，循环到第一页
    currentSlide.value = 0
  } else {
    currentSlide.value++
  }
}

// 跳转到指定位置
const goToSlide = (index) => {
  if (index >= 0 && index < totalPages.value) {
    currentSlide.value = index
  }
}

// 处理胶囊查看
const handleViewCapsule = (capsule) => {
  emit('view', capsule)
}

// 处理胶囊点赞
const handleLikeCapsule = (capsule) => {
  emit('like', capsule)
}

// 处理胶囊点击 - 跳转到地图页面
const handleCapsuleClick = (capsuleId) => {
  router.push('/map')
}

// 自动轮播（可选功能）
// const startAutoPlay = () => {
//   if (totalPages.value > 1) {
//     setInterval(() => {
//       nextSlide()
//     }, 5000)
//   }
// }

// onMounted(() => {
//   startAutoPlay()
// })
</script>

<style scoped>
.enhanced-capsule-carousel {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.carousel-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.carousel-title i {
  color: #4299e1;
}

.carousel-indicators {
  display: flex;
  gap: 8px;
}

.indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #cbd5e0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.indicator.active {
  background: #4299e1;
  transform: scale(1.2);
}

.carousel-container {
  position: relative;
  overflow: hidden;
  border-radius: 12px;
}

.carousel-container.single-item {
  display: flex;
  justify-content: center;
}

.single-capsule-container {
  position: relative;
  width: 100%;
  max-width: 320px;
}

.single-capsule-card {
  position: relative;
  z-index: 2;
}

.single-card-decoration {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120%;
  height: 120%;
  z-index: 1;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  border: 2px dashed #4299e1;
  opacity: 0.3;
  animation: pulse 3s ease-in-out infinite;
}

.decoration-circle:nth-child(1) {
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  animation-delay: 0s;
}

.decoration-circle:nth-child(2) {
  width: 80%;
  height: 80%;
  top: 10%;
  left: 10%;
  animation-delay: 1s;
}

.decoration-circle:nth-child(3) {
  width: 60%;
  height: 60%;
  top: 20%;
  left: 20%;
  animation-delay: 2s;
}

.multi-capsule-container {
  position: relative;
}

.carousel-track {
  display: flex;
  transition: transform 0.5s ease-in-out;
  width: 100%;
}

.carousel-page {
  display: flex;
  flex: 0 0 100%;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 16px;
}

.carousel-slide {
  flex: 0 0 calc(25% - 12px);
  box-sizing: border-box;
  transition: transform 0.3s ease, opacity 0.3s ease;
  opacity: 0.7;
}

.carousel-slide.active-slide {
  opacity: 1;
  transform: scale(1.02);
}

.carousel-controls {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  transform: translateY(-50%);
  display: flex;
  justify-content: space-between;
  padding: 0 16px;
  pointer-events: none;
}

.carousel-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  pointer-events: all;
}

.carousel-btn:hover:not(:disabled) {
  background: #4299e1;
  color: white;
  transform: scale(1.1);
}

.carousel-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #718096;
}

.empty-icon {
  font-size: 3rem;
  color: #cbd5e0;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #4a5568;
}

.empty-description {
  font-size: 0.875rem;
  margin: 0;
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .enhanced-capsule-carousel {
    padding: 16px;
    border-radius: 12px;
  }
  
  .carousel-slide {
    flex: 0 0 calc(50% - 8px); /* 移动端显示2个 */
  }
  
  .carousel-controls {
    padding: 0 8px;
  }
  
  .carousel-btn {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 480px) {
  .carousel-slide {
    flex: 0 0 100%; /* 移动端小屏幕显示1个 */
  }
  
  .carousel-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>