<template>
  <div class="complete-page">
    <div class="card m3-card">
      <div class="complete-content">
        <!-- 成功图标 -->
        <div class="success-icon">
          <div class="icon-circle">
            <span class="material-symbols-rounded">check_circle</span>
          </div>
          <div class="confetti">
            <div v-for="i in 20" :key="i" class="confetti-piece" :style="confettiStyle(i)"></div>
          </div>
        </div>
        
        <!-- 标题和描述 -->
        <div class="text-content">
          <h2 class="title">🎉 配置完成！</h2>
          <p class="subtitle">MoFox Bot 已准备就绪</p>
        </div>
        
        <!-- 摘要信息 -->
        <div class="summary">
          <div class="summary-item">
            <span class="material-symbols-rounded">smart_toy</span>
            <span>机器人配置已保存</span>
            <span class="material-symbols-rounded check">done</span>
          </div>
          <div class="summary-item">
            <span class="material-symbols-rounded">psychology</span>
            <span>AI 模型已配置</span>
            <span class="material-symbols-rounded check">done</span>
          </div>
          <div class="summary-item">
            <span class="material-symbols-rounded">deployed_code</span>
            <span>Git 已配置</span>
            <span class="material-symbols-rounded check">done</span>
          </div>
        </div>
        
        <!-- 提示信息 -->
        <div class="tips">
          <h3>💡 接下来可以做什么？</h3>
          <ul>
            <li>在<strong>主控台</strong>查看机器人运行状态</li>
            <li>在<strong>配置管理</strong>中调整更多高级设置</li>
            <li>在<strong>插件市场</strong>安装更多功能插件</li>
            <li>查看<strong>日志</strong>了解机器人运行详情</li>
          </ul>
        </div>
        
        <!-- 进入主页按钮 -->
        <button class="m3-button filled large" @click="$emit('next')">
          <span>进入主控台</span>
          <span class="material-symbols-rounded">arrow_forward</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineEmits<{
  next: []
}>()

// 生成彩纸样式
function confettiStyle(index: number) {
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
  const randomColor = colors[index % colors.length]
  const randomDelay = Math.random() * 0.5
  const randomX = (Math.random() - 0.5) * 200
  const randomRotate = Math.random() * 720
  
  return {
    '--confetti-color': randomColor,
    '--confetti-delay': `${randomDelay}s`,
    '--confetti-x': `${randomX}px`,
    '--confetti-rotate': `${randomRotate}deg`
  }
}
</script>

<style scoped>
.complete-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 500px;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.card {
  width: 100%;
  max-width: 600px;
  padding: 48px;
  background: var(--md-sys-color-surface);
  border-radius: 28px;
  box-shadow: var(--md-sys-elevation-3);
}

.complete-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

/* 成功图标 */
.success-icon {
  position: relative;
  width: 120px;
  height: 120px;
}

.icon-circle {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--md-sys-color-tertiary-container);
  border-radius: 50%;
  animation: scaleIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.icon-circle .material-symbols-rounded {
  font-size: 72px;
  color: var(--md-sys-color-tertiary);
  animation: checkIn 0.6s ease-out 0.3s backwards;
}

@keyframes checkIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 彩纸效果 */
.confetti {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.confetti-piece {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 8px;
  height: 12px;
  background: var(--confetti-color);
  animation: confettiFall 1.5s ease-out var(--confetti-delay) forwards;
  opacity: 0;
}

@keyframes confettiFall {
  0% {
    opacity: 1;
    transform: translate(0, 0) rotate(0deg);
  }
  100% {
    opacity: 0;
    transform: translate(var(--confetti-x), 200px) rotate(var(--confetti-rotate));
  }
}

/* 文本内容 */
.text-content {
  text-align: center;
}

.title {
  font-size: 32px;
  font-weight: 600;
  color: var(--md-sys-color-on-surface);
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 18px;
  color: var(--md-sys-color-on-surface-variant);
  margin: 0;
}

/* 摘要 */
.summary {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--md-sys-color-surface-variant);
  border-radius: 12px;
  animation: slideIn 0.5s ease-out backwards;
}

.summary-item:nth-child(1) { animation-delay: 0.6s; }
.summary-item:nth-child(2) { animation-delay: 0.7s; }
.summary-item:nth-child(3) { animation-delay: 0.8s; }

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.summary-item > .material-symbols-rounded:first-child {
  font-size: 24px;
  color: var(--md-sys-color-primary);
}

.summary-item > span:nth-child(2) {
  flex: 1;
  font-size: 14px;
  color: var(--md-sys-color-on-surface);
}

.summary-item .check {
  font-size: 20px;
  color: var(--md-sys-color-tertiary);
}

/* 提示 */
.tips {
  width: 100%;
  padding: 20px;
  background: var(--md-sys-color-primary-container);
  border-radius: 16px;
  animation: fadeIn 0.5s ease-out 0.9s backwards;
}

.tips h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--md-sys-color-on-primary-container);
  margin: 0 0 12px 0;
}

.tips ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tips li {
  font-size: 14px;
  line-height: 1.6;
  color: var(--md-sys-color-on-primary-container);
  padding-left: 20px;
  position: relative;
}

.tips li::before {
  content: '•';
  position: absolute;
  left: 8px;
  color: var(--md-sys-color-primary);
}

.tips strong {
  font-weight: 600;
  color: var(--md-sys-color-primary);
}

/* 按钮 */
.m3-button {
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 100px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  animation: fadeIn 0.5s ease-out 1s backwards;
}

.m3-button.filled {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  box-shadow: var(--md-sys-elevation-1);
}

.m3-button.filled:hover {
  box-shadow: var(--md-sys-elevation-3);
  transform: scale(1.05);
}

.m3-button.filled:active {
  transform: scale(0.98);
}

.m3-button.large {
  padding: 16px 40px;
  font-size: 18px;
}

.m3-button .material-symbols-rounded {
  font-size: 24px;
}

/* 响应式 */
@media (max-width: 768px) {
  .card {
    padding: 32px 24px;
  }
  
  .success-icon {
    width: 100px;
    height: 100px;
  }
  
  .icon-circle .material-symbols-rounded {
    font-size: 60px;
  }
  
  .title {
    font-size: 28px;
  }
  
  .subtitle {
    font-size: 16px;
  }
}
</style>
