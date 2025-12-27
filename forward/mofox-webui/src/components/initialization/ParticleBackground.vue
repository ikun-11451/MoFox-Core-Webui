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

type ParticleType = string

class Particle {
  private x: number
  private y: number
  private size: number
  private speedX: number
  private speedY: number
  private type: ParticleType
  private canvas: HTMLCanvasElement

  constructor(canvas: HTMLCanvasElement, type: ParticleType) {
    this.canvas = canvas
    this.type = type
    this.x = Math.random() * canvas.width
    this.y = Math.random() * canvas.height
    this.size = Math.random() * 5 + 2
    this.speedX = Math.random() * 1 - 0.5
    this.speedY = Math.random() * 1 + 0.5
    
    // Adjust speed based on type
    if (type === 'snow') {
      this.speedY = Math.random() * 2 + 1
    } else if (type === 'sakura') {
      this.speedX = Math.random() * 2 - 1
      this.speedY = Math.random() * 1.5 + 0.5
    }
  }

  update() {
    this.x += this.speedX
    this.y += this.speedY

    // Reset if out of bounds
    if (this.y > this.canvas.height) {
      this.y = -10
      this.x = Math.random() * this.canvas.width
    }
    if (this.x > this.canvas.width) {
      this.x = 0
    } else if (this.x < 0) {
      this.x = this.canvas.width
    }
  }

  draw(ctx: CanvasRenderingContext2D) {
    ctx.save()
    switch (this.type) {
      case 'sakura':
        this.drawSakura(ctx)
        break
      case 'snow':
        this.drawSnow(ctx)
        break
      case 'hearts':
        this.drawHeart(ctx)
        break
      case 'sun-rays':
      case 'sun-sparkles':
        this.drawSparkle(ctx, '#FFD700')
        break
      case 'moon-stars':
      case 'starry-sky':
        this.drawSparkle(ctx, '#FFFFFF')
        break
      case 'coffee-steam':
        this.drawSteam(ctx)
        break
      case 'fireworks':
      case 'confetti':
        this.drawConfetti(ctx)
        break
      default:
        this.drawDefault(ctx)
    }
    ctx.restore()
  }

  private drawConfetti(ctx: CanvasRenderingContext2D) {
    const colors = ['#FFD700', '#FF69B4', '#00BFFF', '#32CD32', '#FF4500']
    const color = colors[Math.floor(Math.random() * colors.length)]
    ctx.fillStyle = color
    ctx.globalAlpha = 0.8
    
    ctx.save()
    ctx.translate(this.x, this.y)
    ctx.rotate(this.x * 0.05) // Rotate based on x position for variety
    ctx.fillRect(-this.size / 2, -this.size / 2, this.size, this.size * 0.6)
    ctx.restore()
  }

  private drawSakura(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 182, 193, 0.6)'
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }

  private drawSnow(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)'
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }

  private drawHeart(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 105, 180, 0.6)'
    const size = this.size * 2
    ctx.font = `${size}px Arial`
    ctx.fillText('❤', this.x, this.y)
  }

  private drawSparkle(ctx: CanvasRenderingContext2D, color: string) {
    ctx.fillStyle = color
    ctx.globalAlpha = Math.random() * 0.5 + 0.3
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size / 2, 0, Math.PI * 2)
    ctx.fill()
  }
  
  private drawSteam(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)'
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }

  private drawDefault(ctx: CanvasRenderingContext2D) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)'
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
    ctx.fill()
  }
}

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
    this.createParticles()
    this.animate()
  }

  resizeCanvas() {
    // Use parent container dimensions if possible, otherwise window
    const parent = this.canvas.parentElement
    if (parent) {
      this.canvas.width = parent.clientWidth
      this.canvas.height = parent.clientHeight
    } else {
      this.canvas.width = window.innerWidth
      this.canvas.height = window.innerHeight
    }
  }

  private createParticles() {
    this.particles = []
    const count = 50
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
    
    animationId = requestAnimationFrame(() => this.animate())
  }
  
  updateType(newType: string) {
    this.type = newType
    this.createParticles() // Recreate particles with new type behavior
  }
}

let system: ParticleSystem | null = null

onMounted(() => {
  if (canvasRef.value) {
    system = new ParticleSystem(canvasRef.value, props.type)
    
    window.addEventListener('resize', handleResize)
  }
})

function handleResize() {
  if (system) {
    system.resizeCanvas()
  }
}

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
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
