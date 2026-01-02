<template>
  <canvas ref="canvasRef" class="particle-canvas"></canvas>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps<{
  type: string
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId: number | null = null
let system: ParticleSystem | null = null

interface ParticleConfig {
  color: string
  alpha: number
  size: number
  speed: number
  glow?: boolean
}

const typeConfigs: Record<string, ParticleConfig> = {
  'sun-sparkles': { color: '#FFD700', alpha: 0.6, size: 3, speed: 0.3, glow: true },
  'sun-rays': { color: '#FFA500', alpha: 0.5, size: 4, speed: 0.4, glow: true },
  'hearts': { color: '#FF69B4', alpha: 0.5, size: 8, speed: 0.5 },
  'starry-sky': { color: '#FFFFFF', alpha: 0.7, size: 2, speed: 0.2, glow: true },
  'moon-stars': { color: '#E6E6FA', alpha: 0.6, size: 2.5, speed: 0.15, glow: true },
  'coffee-steam': { color: '#FFFFFF', alpha: 0.2, size: 6, speed: 0.8 },
  'fireworks': { color: '#FFD700', alpha: 0.8, size: 4, speed: 1.2, glow: true },
  'confetti': { color: '#FF69B4', alpha: 0.7, size: 5, speed: 1.5 },
  'sakura': { color: '#FFB6C1', alpha: 0.6, size: 6, speed: 0.6 },
  'snow': { color: '#FFFFFF', alpha: 0.8, size: 4, speed: 1.0 },
  'default': { color: '#FFFFFF', alpha: 0.3, size: 3, speed: 0.3 }
}

class Particle {
  x: number
  y: number
  size: number
  baseSize: number
  speedX: number
  speedY: number
  alpha: number
  baseAlpha: number
  color: string
  angle: number
  spin: number
  pulse: number
  pulseSpeed: number
  type: string
  canvas: HTMLCanvasElement
  hue: number

  constructor(canvas: HTMLCanvasElement, type: string) {
    this.canvas = canvas
    this.type = type
    const config = typeConfigs[type] ?? typeConfigs['default']!
    
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.baseSize = config.size * (0.5 + Math.random() * 1)
    this.size = this.baseSize
    this.baseAlpha = config.alpha * (0.5 + Math.random() * 0.5)
    this.alpha = this.baseAlpha
    this.color = config.color
    this.angle = Math.random() * Math.PI * 2
    this.spin = (Math.random() - 0.5) * 0.02
    this.pulse = Math.random() * Math.PI * 2
    this.pulseSpeed = 0.02 + Math.random() * 0.03
    this.hue = Math.random() * 60 - 30 // Color variation
    
    // Movement based on type
    const speed = config.speed
    switch (type) {
      case 'snow':
        this.speedX = (Math.random() - 0.5) * speed
        this.speedY = speed * (0.5 + Math.random() * 0.5)
        break
      case 'sakura':
        this.speedX = (Math.random() - 0.3) * speed * 1.5
        this.speedY = speed * (0.3 + Math.random() * 0.4)
        break
      case 'coffee-steam':
        this.speedX = (Math.random() - 0.5) * speed * 0.3
        this.speedY = -speed * (0.5 + Math.random() * 0.5)
        break
      case 'fireworks':
      case 'confetti':
        this.speedX = (Math.random() - 0.5) * speed * 2
        this.speedY = speed * (0.3 + Math.random() * 0.7)
        break
      default:
        // Gentle floating for stars and sparkles
        this.speedX = (Math.random() - 0.5) * speed * 0.5
        this.speedY = (Math.random() - 0.5) * speed * 0.5
    }
  }

  update(time: number) {
    // Smooth movement
    this.x += this.speedX
    this.y += this.speedY
    this.angle += this.spin
    this.pulse += this.pulseSpeed
    
    // Pulsing effect
    const pulseFactor = 0.3 * Math.sin(this.pulse)
    this.size = this.baseSize * (1 + pulseFactor * 0.3)
    this.alpha = this.baseAlpha * (0.7 + pulseFactor * 0.3)
    
    // Boundary handling with smooth wrap
    const margin = 50
    if (this.y > this.canvas.height + margin) {
      this.y = -margin
      this.x = Math.random() * this.canvas.width
    } else if (this.y < -margin) {
      this.y = this.canvas.height + margin
      this.x = Math.random() * this.canvas.width
    }
    
    if (this.x > this.canvas.width + margin) {
      this.x = -margin
    } else if (this.x < -margin) {
      this.x = this.canvas.width + margin
    }
  }

  draw(ctx: CanvasRenderingContext2D) {
    ctx.save()
    ctx.globalAlpha = this.alpha
    ctx.translate(this.x, this.y)
    ctx.rotate(this.angle)
    
    const config = typeConfigs[this.type] ?? typeConfigs['default']!
    
    switch (this.type) {
      case 'hearts':
        this.drawHeart(ctx)
        break
      case 'sakura':
        this.drawSakura(ctx)
        break
      case 'snow':
        this.drawSnowflake(ctx)
        break
      case 'confetti':
        this.drawConfetti(ctx)
        break
      case 'coffee-steam':
        this.drawSteam(ctx)
        break
      default:
        this.drawSparkle(ctx, config.glow || false)
    }
    
    ctx.restore()
  }

  private drawSparkle(ctx: CanvasRenderingContext2D, glow: boolean) {
    if (glow) {
      // Soft glow effect
      const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size * 2)
      gradient.addColorStop(0, this.color)
      gradient.addColorStop(0.4, this.color + '80')
      gradient.addColorStop(1, 'transparent')
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(0, 0, this.size * 2, 0, Math.PI * 2)
      ctx.fill()
    }
    
    // Core sparkle
    ctx.fillStyle = this.color
    ctx.beginPath()
    ctx.arc(0, 0, this.size * 0.5, 0, Math.PI * 2)
    ctx.fill()
  }

  private drawHeart(ctx: CanvasRenderingContext2D) {
    const size = this.size
    ctx.fillStyle = this.color
    ctx.beginPath()
    ctx.moveTo(0, size * 0.3)
    ctx.bezierCurveTo(-size, -size * 0.3, -size, size * 0.6, 0, size)
    ctx.bezierCurveTo(size, size * 0.6, size, -size * 0.3, 0, size * 0.3)
    ctx.fill()
  }

  private drawSakura(ctx: CanvasRenderingContext2D) {
    const size = this.size
    ctx.fillStyle = this.color
    
    // Draw 5 petals
    for (let i = 0; i < 5; i++) {
      ctx.save()
      ctx.rotate((i * Math.PI * 2) / 5)
      ctx.beginPath()
      ctx.ellipse(0, -size * 0.4, size * 0.3, size * 0.5, 0, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    }
    
    // Center
    ctx.fillStyle = '#FFE4E1'
    ctx.beginPath()
    ctx.arc(0, 0, size * 0.15, 0, Math.PI * 2)
    ctx.fill()
  }

  private drawSnowflake(ctx: CanvasRenderingContext2D) {
    ctx.strokeStyle = this.color
    ctx.lineWidth = this.size * 0.15
    ctx.lineCap = 'round'
    
    const size = this.size
    // Draw 6 branches
    for (let i = 0; i < 6; i++) {
      ctx.save()
      ctx.rotate((i * Math.PI) / 3)
      ctx.beginPath()
      ctx.moveTo(0, 0)
      ctx.lineTo(0, -size)
      // Small branches
      ctx.moveTo(0, -size * 0.5)
      ctx.lineTo(-size * 0.25, -size * 0.7)
      ctx.moveTo(0, -size * 0.5)
      ctx.lineTo(size * 0.25, -size * 0.7)
      ctx.stroke()
      ctx.restore()
    }
  }

  private drawConfetti(ctx: CanvasRenderingContext2D) {
    const colors = ['#FFD700', '#FF69B4', '#00BFFF', '#32CD32', '#FF4500', '#9370DB'] as const
    const colorIndex = Math.floor(Math.abs(this.x + this.y) % colors.length)
    ctx.fillStyle = colors[colorIndex]!
    
    // Rectangle confetti
    ctx.fillRect(-this.size * 0.5, -this.size * 0.25, this.size, this.size * 0.5)
  }

  private drawSteam(ctx: CanvasRenderingContext2D) {
    const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, this.size)
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0.3)')
    gradient.addColorStop(1, 'transparent')
    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.arc(0, 0, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
}

class ParticleSystem {
  canvas: HTMLCanvasElement
  ctx: CanvasRenderingContext2D
  particles: Particle[] = []
  type: string
  time: number = 0

  constructor(canvas: HTMLCanvasElement, type: string) {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')!
    this.type = type
    this.init()
  }

  init() {
    this.resizeCanvas()
    this.createParticles()
  }

  resizeCanvas() {
    const parent = this.canvas.parentElement
    if (parent) {
      this.canvas.width = parent.clientWidth
      this.canvas.height = parent.clientHeight
    } else {
      this.canvas.width = window.innerWidth
      this.canvas.height = window.innerHeight
    }
  }

  createParticles() {
    this.particles = []
    // Adjust count based on canvas size
    const area = this.canvas.width * this.canvas.height
    const count = Math.min(80, Math.max(30, Math.floor(area / 15000)))
    
    for (let i = 0; i < count; i++) {
      this.particles.push(new Particle(this.canvas, this.type))
    }
  }

  animate() {
    this.time += 0.016 // ~60fps
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    
    this.particles.forEach(particle => {
      particle.update(this.time)
      particle.draw(this.ctx)
    })
    
    animationId = requestAnimationFrame(() => this.animate())
  }

  updateType(newType: string) {
    this.type = newType
    this.createParticles()
  }

  destroy() {
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }
  }
}

function handleResize() {
  if (system) {
    system.resizeCanvas()
    system.createParticles()
  }
}

onMounted(() => {
  if (canvasRef.value) {
    system = new ParticleSystem(canvasRef.value, props.type)
    system.animate()
    window.addEventListener('resize', handleResize)
  }
})

onUnmounted(() => {
  if (system) {
    system.destroy()
  }
  window.removeEventListener('resize', handleResize)
})

watch(() => props.type, (newType) => {
  if (system) {
    system.updateType(newType)
  }
})
</script>

<style scoped>
.particle-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}
</style>
