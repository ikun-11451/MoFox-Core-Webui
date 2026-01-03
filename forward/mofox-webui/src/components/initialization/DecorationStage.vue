<template>
  <div class="decoration-stage">
    <transition-group name="float-item">
      <div
        v-for="item in currentItems"
        :key="item.id"
        class="item-wrapper"
        :style="{
          left: '50%',
          top: '50%',
          marginLeft: `${item.x}px`,
          marginTop: `${item.y}px`,
          zIndex: item.zIndex
        }"
      >
        <div 
          class="item-content"
          :style="{
            '--scale': item.scale,
            '--blur': `${item.blur}px`,
            '--duration': `${item.duration}s`,
            '--delay': `${item.delay}s`,
            '--opacity': item.opacity
          }"
        >
          <span class="material-symbols-rounded icon-font">{{ item.icon }}</span>
        </div>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

const props = defineProps<{
  step: number
}>()

interface FloatingItem {
  id: number
  icon: string
  x: number
  y: number
  scale: number
  blur: number
  zIndex: number
  duration: number
  delay: number
  opacity: number
}

// Items configuration for each step (using Material Symbols names)
const stepItems: Record<number, string[]> = {
  0: [
    'auto_awesome', 'smart_toy', 'star', 'waving_hand', 'magic_button',
    'rocket', 'sparkles', 'favorite', 'lightbulb', 'explore',
    'diamond', 'auto_fix_high', 'shutter_speed', 'tips_and_updates'
  ],
  1: [
    'psychology', 'edit_note', 'theater_comedy', 'palette', 'chat_bubble',
    'face', 'fingerprint', 'badge', 'record_voice_over', 'style',
    'mood', 'person_edit', 'sentiment_very_satisfied', 'brush', 'format_paint'
  ],
  2: [
    'bolt', 'power', 'battery_charging_full', 'rocket_launch', 'computer',
    'memory', 'psychology_alt', 'network_intelligence', 'neurology', 'developer_board',
    'speed', 'dns', 'hub', 'lan', 'precision_manufacturing'
  ],
  3: [
    'build', 'package_2', 'sync', 'terminal', 'settings',
    'cloud_sync', 'download', 'update', 'code', 'integration_instructions',
    'construction', 'handyman', 'deployed_code', 'webhook', 'api'
  ],
  4: [
    'celebration', 'party_mode', 'sentiment_satisfied', 'trophy', 'verified',
    'check_circle', 'done_all', 'stars', 'military_tech', 'workspace_premium',
    'cake', 'local_bar', 'festival', 'campaign', 'award_star'
  ]
}

const currentItems = ref<FloatingItem[]>([])

function generateItems(step: number) {
  // Defensive check for step
  if (typeof step !== 'number') {
    console.warn('[DecorationStage] Invalid step:', step)
    return []
  }

  const icons = stepItems[step] || stepItems[0]
  if (!icons || icons.length === 0) {
    console.warn('[DecorationStage] No icons found for step:', step)
    return []
  }

  const items: FloatingItem[] = []
  
  // Generate 8-12 random items (increased from 5-8)
  const count = 8 + Math.floor(Math.random() * 5)
  
  for (let i = 0; i < count; i++) {
    const icon = icons[Math.floor(Math.random() * icons.length)]
    
    // Random position in a circle around the center, avoiding the central content area
    const angle = (Math.random() * 360) * (Math.PI / 180)
    const radius = 250 + Math.random() * 200 // Distance from center (increased to avoid overlap)
    
    items.push({
      id: Date.now() + i,
      icon,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      scale: 0.5 + Math.random() * 1,
      blur: Math.random() * 2,
      zIndex: 1,
      duration: 3 + Math.random() * 4,
      delay: Math.random() * 2,
      opacity: 0.4 + Math.random() * 0.4
    })
  }
  
  return items
}

watch(() => props.step, (newStep) => {
  try {
    currentItems.value = generateItems(newStep)
  } catch (e) {
    console.error('[DecorationStage] Error generating items:', e)
    currentItems.value = []
  }
}, { immediate: true })

</script>

<style scoped>
.decoration-stage {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.item-wrapper {
  position: absolute;
  /* Position is handled by inline styles (left, top, margin) */
  will-change: transform, opacity;
}

.item-content {
  /* font-size handled by icon-font class */
  opacity: var(--opacity);
  filter: blur(var(--blur));
  transform: scale(var(--scale)); /* Base scale */
  animation: float-around var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
  will-change: transform;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-font {
  font-size: 48px; /* Slightly larger for icons */
  color: var(--md-sys-color-on-primary-container); /* Use theme color */
}

@keyframes float-around {
  0%, 100% { 
    transform: scale(var(--scale)) translateY(0) rotate(0deg); 
  }
  50% { 
    transform: scale(var(--scale)) translateY(-20px) rotate(10deg); 
  }
}

/* Transitions - Applied to wrapper */
.float-item-enter-active,
.float-item-leave-active {
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.float-item-enter-from,
.float-item-enter-from,
.float-item-leave-to {
  opacity: 0;
  transform: scale(0);
}
</style>
