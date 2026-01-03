<template>
  <div class="initialization-container">
    <!-- Left Panel: Branding & Decorations -->
    <div class="left-panel animated-background">
      <ParticleBackground :type="greeting.decoration || 'sun-sparkles'" />
      <DecorationStage :step="currentStep" />
      
      <div class="brand-content" :class="{ 'loaded': isLoaded }">
        <div 
          class="logo-wrapper fade-in-stagger" 
          style="--delay: 0.1s"
          @click="handleLogoClick"
          :class="{ 'dizzy': isDizzy, 'celebrating': currentStep === 4 }"
        >
          <img src="/mofox.ico" alt="MoFox Logo" class="logo-img" />
        </div>
        
        <h1 class="brand-name fade-in-stagger" style="--delay: 0.2s">MoFox Bot</h1>
        <p class="brand-slogan fade-in-stagger" style="--delay: 0.3s">Your Personal AI Companion</p>
        
        <div class="fade-in-stagger" style="--delay: 0.4s">
          <transition name="fade-slide" mode="out-in">
            <div :key="greeting.text" class="greeting-card">
              <div class="greeting-icon">{{ greeting.icon }}</div>
              <p class="greeting-text">{{ greeting.text }}</p>
            </div>
          </transition>
        </div>

        <div class="tips-area fade-in-stagger" style="--delay: 0.5s">
          <transition name="fade" mode="out-in">
            <p :key="rotatingText" class="tip-text">
              <span class="tip-icon">💡</span>
              {{ rotatingText }}
            </p>
          </transition>
        </div>
        
        <transition name="pop">
          <div v-if="easterEggMessage" class="easter-egg-toast">
            {{ easterEggMessage }}
          </div>
        </transition>
      </div>
      
      <div class="version-info fade-in-stagger" style="--delay: 0.6s" @click="handleVersionClick">v1.0.0</div>
    </div>

    <!-- Right Panel: Form & Content -->
    <div class="right-panel">
      <div class="content-wrapper">
        <!-- Progress Indicator -->
        <div v-if="currentStep > 0 && currentStep < 4" class="progress-indicator">
          <div
            v-for="step in 3"
            :key="step"
            :class="['step-dot', { active: currentStep >= step, completed: currentStep > step }]"
          >
            <span v-if="currentStep > step" class="material-symbols-rounded">check</span>
            <span v-else>{{ step }}</span>
          </div>
          <div class="progress-line">
            <div class="progress-fill" :style="{ width: `${((currentStep - 1) / 2) * 100}%` }"></div>
          </div>
        </div>
        
        <!-- Step Content -->
        <div class="step-content">
            <component 
              :is="currentComponent"
              :key="currentStep"
              @next="handleNext" 
              @skip="handleSkip" 
              @toast="handleToast"
            />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getInitStatus, completeInitialization, type InitStatusResponse } from '@/api/initialization'
import { clearInitStatusCache } from '@/router'
import ParticleBackground from '@/components/initialization/ParticleBackground.vue'
import DecorationStage from '@/components/initialization/DecorationStage.vue'
import { getGreeting, getRandomTip, funGreetings, tips, getCompletionGreeting } from '@/utils/initialization-easter-eggs'

// 导入各步骤组件
import WelcomePage from './initialization/steps/WelcomePage.vue'
import BotConfigStep from './initialization/steps/BotConfigStep.vue'
import ModelConfigStep from './initialization/steps/ModelConfigStep.vue'
import GitConfigStep from './initialization/steps/GitConfigStep.vue'
import CompletePage from './initialization/steps/CompletePage.vue'

const router = useRouter()

// State
const currentStep = ref(0)
const transitionName = ref('slide-left')
const initStatus = ref<InitStatusResponse | null>(null)
const greeting = ref(getGreeting())
const currentTip = ref(getRandomTip())
const easterEggMessage = ref('')
const isLoaded = ref(false)
const rotatingText = ref('')

// Easter Egg State
const clickCount = ref(0)
const clickTimer = ref<number | null>(null)
const isDizzy = ref(false)
let textRotationInterval: number | null = null

// Step Specific Content
const stepContent = {
  0: { // Welcome - Will be overridden by dynamic greeting
    text: '欢迎来到 MoFox！\n让我们开始构建你的专属 AI 伙伴。',
    icon: '👋',
    decoration: 'sun-sparkles',
    tip: 'MoFox 是一个高度可定制的 AI 机器人框架。'
  },
  1: { // Bot Config
    text: '赋予它灵魂。\n名字和性格是 AI 的核心。',
    icon: '🧠',
    decoration: 'hearts',
    tip: '你可以随时在设置中修改机器人的性格设定。'
  },
  2: { // Model Config
    text: '连接智慧大脑。\nSiliconFlow 提供强大的推理能力。',
    icon: '⚡',
    decoration: 'starry-sky',
    tip: 'DeepSeek-V3 是目前性价比极高的模型选择。'
  },
  3: { // Git Config
    text: '保持同步。\nGit 帮助你获取最新功能和插件。',
    icon: '🔧',
    decoration: 'coffee-steam',
    tip: '即使跳过配置，你也可以手动更新系统。'
  },
  4: { // Complete
    text: '一切就绪！\n你的 MoFox 已经准备好陪伴你了。',
    icon: '🎉',
    decoration: 'fireworks',
    tip: '试着对它说"你好"来开始第一次对话吧！'
  }
}

// Components Map
const currentComponent = computed(() => {
  console.log('[InitializationView] currentStep:', currentStep.value)
  let component
  switch (currentStep.value) {
    case 0: component = WelcomePage; break
    case 1: component = BotConfigStep; break
    case 2: component = ModelConfigStep; break
    case 3: component = GitConfigStep; break
    case 4: component = CompletePage; break
    default: component = WelcomePage; break
  }
  console.log('[InitializationView] currentComponent:', component)
  return component
})

// Update greeting based on step
watch(currentStep, (newStep) => {
  if (newStep === 0) {
    // Use dynamic greeting for step 0
    const dynamicGreeting = getGreeting()
    greeting.value = {
      text: dynamicGreeting.text,
      icon: dynamicGreeting.icon || '👋',
      decoration: dynamicGreeting.decoration || 'sun-sparkles',
      theme: dynamicGreeting.theme || 'default'
    }
    // Tip is handled by rotating text
  } else if (newStep === 4) {
    // Use random completion greeting for step 4
    const completion = getCompletionGreeting()
    greeting.value = {
      text: completion.text,
      icon: completion.icon,
      decoration: completion.decoration,
      theme: 'default'
    }
    rotatingText.value = completion.tip
  } else {
    const content = stepContent[newStep as keyof typeof stepContent]
    if (content) {
      greeting.value = {
        text: content.text,
        icon: content.icon,
        decoration: content.decoration,
        theme: 'default'
      }
      // Update tip immediately for context, though rotation continues
      rotatingText.value = content.tip
    }
  }
}, { immediate: true })

// Navigation
async function handleNext() {
  if (currentStep.value === 4) {
    try {
      await completeInitialization()
      clearInitStatusCache()
      router.push('/dashboard')
    } catch (error) {
      console.error('Failed to complete initialization:', error)
    }
    return
  }
  
  transitionName.value = 'slide-left'
  currentStep.value++
  // Tip is updated by watcher
}

function handleSkip() {
  transitionName.value = 'slide-left'
  currentStep.value++
  // Tip is updated by watcher
}

function handleToast(message: string) {
  easterEggMessage.value = message
  setTimeout(() => {
    easterEggMessage.value = ''
  }, 3000)
}

// Initialization Check
async function checkInitStatus() {
  try {
    const result = await getInitStatus()
    if (result.success && result.data) {
      initStatus.value = result.data
      if (result.data.is_initialized) {
        router.push('/dashboard')
      }
    }
  } catch (error) {
    console.error('Failed to get init status:', error)
  }
}

// Easter Egg Logic
function handleLogoClick() {
  clickCount.value++
  
  if (clickTimer.value) {
    clearTimeout(clickTimer.value)
  }
  
  if (clickCount.value >= 10) {
    triggerDizzyEasterEgg()
    clickCount.value = 0
  } else {
    clickTimer.value = setTimeout(() => {
      if (clickCount.value === 5) {
        handleToast('再点我就要晕啦！😵')
      }
      clickCount.value = 0
    }, 2000)
  }
}

function handleVersionClick() {
  handleToast('MoFox WebUI - Made with ❤️ by You')
}

function triggerDizzyEasterEgg() {
  isDizzy.value = true
  easterEggMessage.value = '别点了别点了，我都转晕了 @_@'
  
  setTimeout(() => {
    isDizzy.value = false
    easterEggMessage.value = ''
  }, 3000)
}

function startTextRotation() {
  // Initial text - if step 0, use random fun greeting, else use step tip
  if (currentStep.value === 0) {
    const index = Math.floor(Math.random() * funGreetings.length)
    const greeting = funGreetings[index]
    rotatingText.value = `${greeting.icon} ${greeting.text}`
  } else {
    rotatingText.value = stepContent[currentStep.value as keyof typeof stepContent].tip
  }

  textRotationInterval = setInterval(() => {
    // Only rotate if in step 0 or randomly occasionally in other steps
    if (currentStep.value === 0) {
      // In Step 0: Mostly show fun greetings (80% chance), occasionally show tips (20%)
      if (Math.random() > 0.2) {
        const index = Math.floor(Math.random() * funGreetings.length)
        const greeting = funGreetings[index]
        rotatingText.value = `${greeting.icon} ${greeting.text}`
      } else {
        const index = Math.floor(Math.random() * tips.length)
        rotatingText.value = tips[index]
      }
    } else if (Math.random() > 0.8) {
      // In other steps: Only show tips (no fun greetings), occasionally rotate
      const index = Math.floor(Math.random() * tips.length)
      rotatingText.value = tips[index]
    }
  }, 3000)
}

// Lifecycle
let greetingInterval: number

onMounted(() => {
  // Trigger entrance animation
  setTimeout(() => {
    isLoaded.value = true
  }, 100)

  checkInitStatus()
  startTextRotation()
  
  // Update greeting periodically only if on Welcome step (0)
  greetingInterval = setInterval(() => {
    if (currentStep.value === 0) {
      greeting.value = getGreeting()
    }
  }, 60000 * 60) // Every hour
})

onUnmounted(() => {
  clearInterval(greetingInterval)
  if (textRotationInterval) clearInterval(textRotationInterval)
})
</script>

<style scoped>
.initialization-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  background: var(--md-sys-color-surface);
  overflow: hidden;
}

/* Left Panel */
.left-panel {
  width: 40%;
  height: 100%;
  background: linear-gradient(135deg, 
    var(--md-sys-color-primary-container) 0%, 
    var(--md-sys-color-secondary-container) 50%,
    var(--md-sys-color-tertiary-container) 100%);
  background-size: 200% 200%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--md-sys-color-on-primary-container);
  overflow: hidden;
}

.animated-background {
  animation: gradient-move 15s ease infinite;
}

@keyframes gradient-move {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Staggered Entrance */
.fade-in-stagger {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1), 
              transform 0.8s cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: var(--delay, 0s);
}

.brand-content.loaded .fade-in-stagger {
  opacity: 1;
  transform: translateY(0);
}

.brand-content {
  position: relative;
  z-index: 2; /* Ensure content is above decorations */
  text-align: center;
  width: 100%;
  max-width: 400px;
}

/* Decoration Stage styles moved to DecorationStage.vue */

.logo-wrapper {
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  backdrop-filter: blur(10px);
  cursor: pointer;
  transition: transform 0.3s ease;
  position: relative;
  z-index: 10;
}

.logo-wrapper:hover {
  transform: scale(1.05);
}

.logo-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
  user-select: none;
}

/* Animations */
.dizzy {
  animation: spin 0.5s linear infinite;
}

.celebrating {
  animation: jump 0.6s ease-in-out infinite;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

@keyframes jump {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.brand-name {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 8px;
  letter-spacing: -1px;
}

.brand-slogan {
  font-size: 18px;
  opacity: 0.8;
  margin: 0 0 48px;
}

.greeting-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.greeting-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.greeting-text {
  font-size: 16px;
  line-height: 1.5;
  margin: 0;
}

.tips-area {
  font-size: 15px;
  opacity: 0.9;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 24px;
  padding: 0 16px;
  width: 100%;
}

.tip-text {
  display: flex;
  align-items: center;
  gap: 8px;
  line-height: 1.6;
  white-space: nowrap;
}

.tip-icon {
  font-size: 18px;
}

.easter-egg-toast {
  position: absolute;
  bottom: 100px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--md-sys-color-error);
  color: var(--md-sys-color-on-error);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Animations */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.pop-enter-active {
  animation: pop-in 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.pop-leave-active {
  transition: all 0.3s ease;
}

.pop-leave-to {
  opacity: 0;
  transform: translateX(-50%) scale(0.8);
}

@keyframes pop-in {
  from { transform: translateX(-50%) scale(0.8); opacity: 0; }
  to { transform: translateX(-50%) scale(1); opacity: 1; }
}

.version-info {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  opacity: 0.5;
  cursor: pointer;
  transition: opacity 0.3s;
}

.version-info:hover {
  opacity: 1;
}

/* Right Panel */
.right-panel {
  width: 60%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.content-wrapper {
  width: 100%;
  height: 100%;
  max-width: 800px;
  padding: 48px;
  display: flex;
  flex-direction: column;
}

.step-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px;
  margin: 0 -16px;
  /* Hide scrollbar for Chrome, Safari and Opera */
  &::-webkit-scrollbar {
    display: none;
  }
  /* Hide scrollbar for IE, Edge and Firefox */
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

/* Progress Indicator */
.progress-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  position: relative;
  margin: 0 auto 48px;
  max-width: 300px;
}

.step-dot {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  background: var(--md-sys-color-surface-variant);
  color: var(--md-sys-color-on-surface-variant);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 2;
}

.step-dot.active {
  background: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.step-dot.completed {
  background: var(--md-sys-color-tertiary);
  color: var(--md-sys-color-on-tertiary);
}

.step-dot .material-symbols-rounded {
  font-size: 24px;
}

.progress-line {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 80px);
  height: 4px;
  background: var(--md-sys-color-surface-variant);
  border-radius: 2px;
  z-index: 1;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--md-sys-color-primary);
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}

/* Responsive */
@media (max-width: 1024px) {
  .initialization-container {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
    overflow-y: auto;
  }
  
  .left-panel {
    width: 100%;
    height: auto;
    min-height: 300px;
    padding: 32px 16px;
    flex-shrink: 0;
  }
  
  .right-panel {
    width: 100%;
    height: auto;
    padding: 0;
    overflow: visible;
  }
  
  .content-wrapper {
    padding: 32px 16px;
    height: auto;
  }

  .step-content {
    overflow-y: visible;
    margin: 0;
    padding: 0;
  }
  
  .brand-name {
    font-size: 32px;
  }
  
  .logo-wrapper {
    width: 80px;
    height: 80px;
    margin-bottom: 16px;
  }
  
  .logo {
    font-size: 40px;
  }

  .brand-slogan {
    margin-bottom: 24px;
  }

  .greeting-card {
    padding: 16px;
    margin-bottom: 16px;
  }
}

@media (max-width: 480px) {
  .left-panel {
    min-height: 240px;
    padding: 24px 16px;
  }

  .brand-name {
    font-size: 28px;
  }

  .brand-slogan {
    font-size: 14px;
  }

  .greeting-text {
    font-size: 14px;
  }

  .logo-wrapper {
    width: 64px;
    height: 64px;
  }

  .logo {
    font-size: 32px;
  }
}
</style>
