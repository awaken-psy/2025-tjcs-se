<!-- filepath: d:\web-p\TimeCapsule\frontend\src\views\TimeLineView.vue -->
<template>
  <div class="timeline-view">
    <!-- 页面标题 -->
    <header class="timeline-header">
      <h1>胶囊时间轴</h1>
    </header>

    <!-- 时间轴容器 -->
    <div class="timeline-container">
      <ul class="timeline">
        <!-- 时间轴项 -->
        <li v-for="(capsule, index) in capsules" :key="index" class="timeline-item">
          <div class="timeline-dot"></div>
          <div class="timeline-content">
            <h2 class="capsule-title">{{ capsule.title }}</h2>
            <p class="capsule-date">{{ capsule.date }}</p>
            <p class="capsule-description">{{ capsule.description }}</p>
            <div v-if="capsule.coverImage" class="capsule-image">
              <img :src="capsule.coverImage" alt="胶囊封面" />
            </div>
            <button class="view-details-btn" @click="viewDetails(capsule.id)">查看详情</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
// 示例数据
const capsules = [
  {
    id: 1,
    title: "胶囊标题 1",
    date: "2025-12-01",
    description: "这是第一个胶囊的描述内容。",
    coverImage: "https://via.placeholder.com/150",
  },
  {
    id: 2,
    title: "胶囊标题 2",
    date: "2025-12-05",
    description: "这是第二个胶囊的描述内容。",
    coverImage: "https://via.placeholder.com/150",
  },
  {
    id: 3,
    title: "胶囊标题 3",
    date: "2025-12-10",
    description: "这是第三个胶囊的描述内容。",
    coverImage: null,
  },
];

// 查看详情的占位逻辑
const viewDetails = (id) => {
  console.log("查看胶囊详情，ID:", id);
};
</script>

<style scoped>
/* 页面整体样式 */
.timeline-view {
  font-family: Arial, sans-serif;
  padding: 20px;
  background-color: #f9f9f9;
}

/* 标题样式 */
.timeline-header {
  text-align: center;
  margin-bottom: 20px;
}

.timeline-header h1 {
  font-size: 24px;
  color: #333;
}

/* 时间轴容器样式 */
.timeline-container {
  position: relative;
  margin: 0 auto;
  padding: 20px 0;
  max-width: 800px;
}

/* 时间轴样式 */
.timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  position: relative;
}

.timeline::before {
  content: "";
  position: absolute;
  top: 0;
  left: 50%;
  width: 4px;
  height: 100%;
  background: #ddd;
  transform: translateX(-50%);
}

/* 时间轴项样式 */
.timeline-item {
  position: relative;
  margin: 20px 0;
  padding-left: 50px;
  padding-right: 50px;
}

.timeline-item:nth-child(odd) {
  text-align: left;
}

.timeline-item:nth-child(even) {
  text-align: right;
}

.timeline-item .timeline-dot {
  position: absolute;
  top: 0;
  left: 50%;
  width: 12px;
  height: 12px;
  background: #007bff;
  border-radius: 50%;
  transform: translate(-50%, 0);
}

.timeline-item .timeline-content {
  background: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.timeline-item .capsule-title {
  font-size: 18px;
  color: #333;
  margin: 0 0 10px;
}

.timeline-item .capsule-date {
  font-size: 14px;
  color: #666;
  margin: 0 0 10px;
}

.timeline-item .capsule-description {
  font-size: 14px;
  color: #555;
  margin: 0 0 10px;
}

.timeline-item .capsule-image img {
  max-width: 100%;
  border-radius: 8px;
  margin: 10px 0;
}

.timeline-item .view-details-btn {
  background: #007bff;
  color: #fff;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.timeline-item .view-details-btn:hover {
  background: #0056b3;
}
</style>