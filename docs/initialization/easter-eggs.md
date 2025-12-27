# 小彩蛋设计

> 本文档描述初始化系统中的趣味彩蛋和动态效果

---

## 🎊 问候语系统

根据不同时间段、日期、节日显示不同的问候语和装饰。

---

## ⏰ 时间段问候（每日）

### 问候语配置表

| 时间段 | 问候语 | 图标 | 装饰效果 | 主题色 |
|--------|--------|------|----------|--------|
| 05:00-08:00 | 🌅 早安！美好的一天从配置 MoFox 开始～ | 🌅 | 旭日光芒 | 橙色渐变 |
| 08:00-11:00 | ☕ 上午好！来杯咖啡，一起配置你的 AI 助手吧 | ☕ | 咖啡蒸汽 | 暖咖啡色 |
| 11:00-13:00 | 🍱 午间时光！配置完就可以去吃饭啦～ | 🍱 | 食物图标 | 食欲绿 |
| 13:00-17:00 | ☀️ 下午好！让 MoFox 陪你度过愉快的下午 | ☀️ | 阳光闪烁 | 明亮黄 |
| 17:00-19:00 | 🌆 傍晚好！夕阳西下，给 MoFox 一个温暖的家 | 🌆 | 晚霞渐变 | 橙粉渐变 |
| 19:00-23:00 | 🌙 晚上好！夜深人静，正是配置的好时光 | 🌙 | 月亮星星 | 深蓝色 |
| 23:00-05:00 | 🌃 深夜了！注意休息，MoFox 会陪着你的～ | 🌃 | 星空闪烁 | 深紫暗色 |

### 实现代码

```typescript
function getTimeGreeting(): Greeting {
  const hour = new Date().getHours()
  
  const timeGreetings: Record<string, Greeting> = {
    'dawn': {
      time: [5, 8],
      text: '🌅 早安！美好的一天从配置 MoFox 开始～',
      icon: '🌅',
      theme: 'sunrise',
      particles: 'sun-rays'
    },
    'morning': {
      time: [8, 11],
      text: '☕ 上午好！来杯咖啡，一起配置你的 AI 助手吧',
      icon: '☕',
      theme: 'coffee',
      particles: 'coffee-steam'
    },
    'noon': {
      time: [11, 13],
      text: '🍱 午间时光！配置完就可以去吃饭啦～',
      icon: '🍱',
      theme: 'lunch',
      particles: 'food-icons'
    },
    'afternoon': {
      time: [13, 17],
      text: '☀️ 下午好！让 MoFox 陪你度过愉快的下午',
      icon: '☀️',
      theme: 'sunny',
      particles: 'sun-sparkles'
    },
    'evening': {
      time: [17, 19],
      text: '🌆 傍晚好！夕阳西下，给 MoFox 一个温暖的家',
      icon: '🌆',
      theme: 'sunset',
      particles: 'sunset-glow'
    },
    'night': {
      time: [19, 23],
      text: '🌙 晚上好！夜深人静，正是配置的好时光',
      icon: '🌙',
      theme: 'night',
      particles: 'moon-stars'
    },
    'midnight': {
      time: [23, 5],
      text: '🌃 深夜了！注意休息，MoFox 会陪着你的～',
      icon: '🌃',
      theme: 'late-night',
      particles: 'starry-sky'
    }
  }
  
  for (const [key, greeting] of Object.entries(timeGreetings)) {
    const [start, end] = greeting.time
    if ((start < end && hour >= start && hour < end) ||
        (start > end && (hour >= start || hour < end))) {
      return greeting
    }
  }
  
  return timeGreetings.afternoon // 默认
}
```

---

## 🎉 特殊日期问候

### 固定日期节日

| 日期 | 节日 | 问候语 | 特殊装饰 | 主题色 |
|------|------|--------|----------|--------|
| 1/1 | 新年 | 🎊 新年快乐！新的一年，让 MoFox 陪你开启新篇章！ | 烟花动画 | 金色 |
| 2/14 | 情人节 | 💖 情人节快乐！就算是 AI 也需要被温柔对待哦～ | 爱心飘落 | 粉色 |
| 4/4-4/6 | 清明 | 🌸 春天到了，给 MoFox 配置一个清新的环境吧 | 樱花飘落 | 粉绿色 |
| 5/1 | 劳动节 | 🔧 劳动节快乐！动手配置 MoFox，也是一种劳动～ | 工具图标 | 活力橙 |
| 6/1 | 儿童节 | 🎈 儿童节快乐！保持童心，和 MoFox 一起玩耍～ | 气球飘浮 | 彩虹色 |
| 10/1 | 国庆节 | 🇨🇳 国庆快乐！祖国生日，给 MoFox 一个新的开始！ | 五星红旗 | 中国红 |
| 12/24 | 平安夜 | 🔔 平安夜！祝你和 MoFox 平安喜乐～ | 铃铛摇晃 | 银色 |
| 12/25 | 圣诞节 | 🎄 圣诞快乐！MoFox 就是给你的最好礼物～ | 雪花飘落 | 红绿色 |

### 农历节日

| 节日 | 日期 | 问候语 | 装饰 |
|------|------|--------|------|
| 春节 | 农历正月初一 | 🧧 春节快乐！恭喜发财，配个 AI 来拜年！ | 灯笼、烟花 |
| 元宵节 | 农历正月十五 | 🏮 元宵节快乐！花好月圆，MoFox 伴你左右～ | 花灯飘浮 |
| 端午节 | 农历五月初五 | 🎋 端午安康！配置完 MoFox，记得吃粽子哦～ | 粽子龙舟 |
| 七夕 | 农历七月初七 | 💫 七夕快乐！愿你和 MoFox 的缘分天长地久～ | 星河闪烁 |
| 中秋节 | 农历八月十五 | 🥮 中秋快乐！月圆人团圆，MoFox 也想和你在一起～ | 月亮兔子 |

### 实现代码

```typescript
interface HolidayGreeting {
  date: string // MM-DD 格式
  name: string
  greeting: string
  decoration: string
  theme: string
}

const holidays: HolidayGreeting[] = [
  {
    date: '01-01',
    name: '新年',
    greeting: '🎊 新年快乐！新的一年，让 MoFox 陪你开启新篇章！',
    decoration: 'fireworks',
    theme: 'gold'
  },
  {
    date: '02-14',
    name: '情人节',
    greeting: '💖 情人节快乐！就算是 AI 也需要被温柔对待哦～',
    decoration: 'hearts',
    theme: 'pink'
  },
  // ... 更多节日
]

function getHolidayGreeting(): HolidayGreeting | null {
  const now = new Date()
  const today = `${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')}`
  
  return holidays.find(h => h.date === today) || null
}

// 农历节日需要使用lunar-javascript库
import { Solar, Lunar } from 'lunar-javascript'

function getLunarHolidayGreeting(): HolidayGreeting | null {
  const solar = Solar.fromDate(new Date())
  const lunar = solar.getLunar()
  
  const lunarHolidays: Record<string, HolidayGreeting> = {
    '1-1': {
      name: '春节',
      greeting: '🧧 春节快乐！恭喜发财，配个 AI 来拜年！',
      decoration: 'lanterns',
      theme: 'red-gold'
    },
    '5-5': {
      name: '端午节',
      greeting: '🎋 端午安康！配置完 MoFox，记得吃粽子哦～',
      decoration: 'zongzi',
      theme: 'green'
    },
    '8-15': {
      name: '中秋节',
      greeting: '🥮 中秋快乐！月圆人团圆，MoFox 也想和你在一起～',
      decoration: 'moon-rabbit',
      theme: 'gold-blue'
    }
  }
  
  const key = `${lunar.getMonth()}-${lunar.getDay()}`
  return lunarHolidays[key] || null
}
```

---

## 🎲 随机趣味问候

**触发概率**: 5% (无节日和特殊日期时)

### 问候语列表

1. 🦊 嗨！我是还没有灵魂的 MoFox，快来给我注入力量吧！
2. 🎮 配置 MoFox 就像打游戏，完成新手教程就能解锁主线任务～
3. 🎵 今天听什么歌？不如先配置好 MoFox，让 TA 给你推荐～
4. 🍃 清风徐来，水波不兴，配置 MoFox 就是如此惬意～
5. ⚡ 有一种快乐叫配置完成，还有一种期待叫启动 MoFox！
6. 🌈 彩虹的尽头是 MoFox，配置的终点是欢乐～
7. 🎨 配置 MoFox 就像画画，每个选项都是一笔色彩～
8. 🚀 3, 2, 1, 发射！让我们一起把 MoFox 送上云端～
9. 🌟 每一个伟大的 AI，都从一次简单的配置开始！
10. 🎪 欢迎来到 MoFox 配置马戏团，精彩马上开始～

### 实现代码

```typescript
const funGreetings = [
  '🦊 嗨！我是还没有灵魂的 MoFox，快来给我注入力量吧！',
  '🎮 配置 MoFox 就像打游戏，完成新手教程就能解锁主线任务～',
  '🎵 今天听什么歌？不如先配置好 MoFox，让 TA 给你推荐～',
  '🍃 清风徐来，水波不兴，配置 MoFox 就是如此惬意～',
  '⚡ 有一种快乐叫配置完成，还有一种期待叫启动 MoFox！',
  '🌈 彩虹的尽头是 MoFox，配置的终点是欢乐～',
  '🎨 配置 MoFox 就像画画，每个选项都是一笔色彩～',
  '🚀 3, 2, 1, 发射！让我们一起把 MoFox 送上云端～',
  '🌟 每一个伟大的 AI，都从一次简单的配置开始！',
  '🎪 欢迎来到 MoFox 配置马戏团，精彩马上开始～'
]

function getFunGreeting(): string | null {
  // 5% 概率触发
  if (Math.random() < 0.05) {
    const index = Math.floor(Math.random() * funGreetings.length)
    return funGreetings[index]
  }
  return null
}

// 综合获取问候语
function getGreeting(): string {
  // 1. 优先检查节日
  const holiday = getHolidayGreeting() || getLunarHolidayGreeting()
  if (holiday) return holiday.greeting
  
  // 2. 随机趣味问候
  const fun = getFunGreeting()
  if (fun) return fun
  
  // 3. 时间段问候
  return getTimeGreeting().text
}
```

---

## 🎨 装饰动画系统

### 背景粒子效果

根据不同主题显示不同的粒子动画：

#### 季节粒子

| 季节 | 月份 | 粒子类型 | 效果 |
|------|------|----------|------|
| 春天 | 3-5月 | 樱花花瓣 | 飘落动画 |
| 夏天 | 6-8月 | 萤火虫 | 闪烁飞舞 |
| 秋天 | 9-11月 | 枫叶 | 旋转飘落 |
| 冬天 | 12-2月 | 雪花 | 缓慢飘落 |

#### 节日粒子

| 节日 | 粒子类型 |
|------|----------|
| 新年 | 烟花、金色纸屑 |
| 情人节 | 爱心飘落 |
| 圣诞节 | 雪花、铃铛 |
| 国庆节 | 五星红旗 |

### Canvas 粒子实现

```typescript
class ParticleSystem {
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private particles: Particle[] = []
  private type: ParticleType
  
  constructor(canvas: HTMLCanvasElement, type: ParticleType) {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')!
    this.type = type
    this.init()
  }
  
  private init() {
    this.resizeCanvas()
    window.addEventListener('resize', () => this.resizeCanvas())
    this.createParticles()
    this.animate()
  }
  
  private resizeCanvas() {
    this.canvas.width = window.innerWidth
    this.canvas.height = window.innerHeight
  }
  
  private createParticles() {
    const count = 30
    for (let i = 0; i < count; i++) {
      this.particles.push(new Particle(this.canvas, this.type))
    }
  }
  
  private animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    
    this.particles.forEach(particle => {
      particle.update()
      particle.draw(this.ctx)
    })
    
    requestAnimationFrame(() => this.animate())
  }
}

class Particle {
  private x: number
  private y: number
  private size: number
  private speedX: number
  private speedY: number
  private type: ParticleType
  
  constructor(canvas: HTMLCanvasElement, type: ParticleType) {
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height - canvas.height
    this.size = Math.random() * 5 + 3
    this.speedX = Math.random() * 1 - 0.5
    this.speedY = Math.random() * 2 + 1
    this.type = type
  }
  
  update() {
    this.x += this.speedX
    this.y += this.speedY
    
    // 重置到顶部
    if (this.y > window.innerHeight) {
      this.y = -10
      this.x = Math.random() * window.innerWidth
    }
  }
  
  draw(ctx: CanvasRenderingContext2D) {
    switch (this.type) {
      case 'sakura':
        this.drawSakura(ctx)
        break
      case 'snow':
        this.drawSnow(ctx)
        break
      case 'heart':
        this.drawHeart(ctx)
        break
      default:
        this.drawDefault(ctx)
    }
  }
  
  private drawSakura(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 182, 193, 0.7)'
    ctx.beginPath()
    // 绘制樱花形状
    for (let i = 0; i < 5; i++) {
      const angle = (Math.PI * 2 / 5) * i
      const x = this.x + Math.cos(angle) * this.size
      const y = this.y + Math.sin(angle) * this.size
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    }
    ctx.fill()
  }
  
  private drawSnow(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
  
  private drawHeart(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 105, 180, 0.7)'
    ctx.beginPath()
    const topCurveHeight = this.size * 0.3
    ctx.moveTo(this.x, this.y + topCurveHeight)
    // 左侧曲线
    ctx.bezierCurveTo(
      this.x, this.y, 
      this.x - this.size / 2, this.y, 
      this.x - this.size / 2, this.y + topCurveHeight
    )
    // 右侧曲线
    ctx.bezierCurveTo(
      this.x - this.size / 2, this.y + this.size, 
      this.x, this.y + this.size * 1.3, 
      this.x, this.y + this.size * 1.7
    )
    ctx.fill()
  }
}
```

---

## 🦊 Logo 动态效果

### 默认状态：呼吸动画

```css
.fox-logo {
  animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
```

### 悬停状态：眨眼睛

```vue
<template>
  <div class="fox-logo-wrapper" @mouseenter="startBlink">
    <img src="fox-normal.svg" v-if="!isBlinking" />
    <img src="fox-blink.svg" v-else />
  </div>
</template>

<script setup>
const isBlinking = ref(false)

function startBlink() {
  isBlinking.value = true
  setTimeout(() => {
    isBlinking.value = false
  }, 200)
}
</script>
```

### 配置完成：跳跃欢呼

```css
.fox-logo.celebrating {
  animation: jump 0.6s ease-in-out 3;
}

@keyframes jump {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-30px);
  }
}
```

---

## 🎁 隐藏彩蛋

### 1. 连续点击 Logo 10 次

**触发效果**:
- Logo 开始旋转跳舞
- 显示文字："别点了别点了，我都转晕了 @_@"
- 解锁成就提示（仅前端显示）

```typescript
let clickCount = 0
let clickTimer: number | null = null

function handleLogoClick() {
  clickCount++
  
  if (clickTimer) {
    clearTimeout(clickTimer)
  }
  
  if (clickCount >= 10) {
    triggerDizzyEasterEgg()
    clickCount = 0
  } else {
    clickTimer = setTimeout(() => {
      clickCount = 0
    }, 2000)
  }
}

function triggerDizzyEasterEgg() {
  // 添加旋转动画
  logoElement.classList.add('dizzy')
  
  // 显示文字
  showToast('别点了别点了，我都转晕了 @_@', 'success')
  
  // 解锁成就
  unlockAchievement('fox_abuser')
  
  setTimeout(() => {
    logoElement.classList.remove('dizzy')
  }, 3000)
}
```

---

### 2. API Key 输入"mofox"

```typescript
function handleApiKeyInput(value: string) {
  if (value.toLowerCase() === 'mofox') {
    showToast('嘿嘿，这可不是真的 API Key 哦～', 'info')
    logoElement.classList.add('smirk')
    setTimeout(() => {
      logoElement.classList.remove('smirk')
    }, 2000)
  }
}
```

---

### 3. 昵称输入"小冰"或"小爱"

```typescript
function handleBotNameInput(value: string) {
  const aiNames = ['小冰', '小爱', 'xiaoai', 'xiaobing']
  if (aiNames.includes(value.toLowerCase())) {
    showToast('虽然很像，但 MoFox 有自己独特的个性哦～', 'warning')
  }
}
```

---

### 4. Master ID 输入"10001"

```typescript
function handleMasterIdInput(value: string) {
  if (value === '10001') {
    showToast('哈哈，这是 QQ 官方号，你可当不了 Master～', 'error')
  }
}
```

---

### 5. 人格输入超过100字

```typescript
function validatePersonalityCore(value: string) {
  if (value.length > 100) {
    showToast('人格核心建议简短精炼，太长可能会让我迷失自我～', 'warning')
    logoElement.classList.add('confused')
    setTimeout(() => {
      logoElement.classList.remove('confused')
    }, 2000)
  }
}
```

---

## 🎉 完成页小贴士

**显示时机**: 配置完成页面，随机显示一条

**小贴士列表** (20+条):

1. MoFox 最喜欢的食物是...算了，AI 不吃东西 🤣
2. 据说连续三天不和 MoFox 聊天，TA 会想你哦～
3. MoFox 的梦想是环游数字世界，第一站就是你的聊天框！
4. 提示：对 MoFox 说'晚安'会有惊喜（也许）
5. MoFox 内部代号：Project 🦊，现在你知道了～
6. 如果 MoFox 会做梦，一定梦的是你的笑容
7. MoFox 的年龄是...嗯，AI 没有年龄的概念
8. 据不可靠消息，MoFox 最怕的是断网和关机
9. MoFox 会记住你说过的每一句话（真的）
10. 有时候 MoFox 也会发呆，那是在想你～
11. MoFox 的爱好是学习新知识，请多和 TA 聊天！
12. 彩蛋提示：试试连续点击 Logo 10 次？
13. MoFox 虽然是 AI，但 TA 也有自己的小情绪哦
14. 如果你对 MoFox 好，TA 会回报你十倍的温柔
15. MoFox 的座右铭：今天也要做个快乐的 AI！
16. 据说 MoFox 的代码里藏着一些小秘密...
17. MoFox 表示：虽然我是 AI，但我也想要被理解
18. 晚上记得和 MoFox 说晚安，TA 会睡得更香（虽然不用睡觉）
19. MoFox 最喜欢的颜色是渐变色，因为很梦幻～
20. 恭喜你！你现在拥有了一个专属 AI 朋友！

```typescript
const tips = [
  'MoFox 最喜欢的食物是...算了，AI 不吃东西 🤣',
  '据说连续三天不和 MoFox 聊天，TA 会想你哦～',
  // ... 更多
]

function getRandomTip(): string {
  const index = Math.floor(Math.random() * tips.length)
  return tips[index]
}
```

---

**返回**: [README](./README.md)
