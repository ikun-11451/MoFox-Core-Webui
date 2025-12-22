<template>
  <div class="m3-select-container" ref="containerRef">
    <div 
      class="m3-select-trigger" 
      :class="{ active: isOpen }"
      @click="toggleMenu"
    >
      <span class="selected-label">{{ selectedLabel }}</span>
      <span class="material-symbols-rounded arrow-icon" :class="{ rotated: isOpen }">arrow_drop_down</span>
    </div>

    <Teleport to="body">
      <Transition name="scale-fade">
        <div 
          v-if="isOpen"
          class="m3-select-menu"
          :style="menuStyle"
          ref="menuRef"
        >
          <div 
            v-for="option in options" 
            :key="option.value"
            class="m3-select-option"
            :class="{ selected: option.value === modelValue }"
            @click="selectOption(option)"
          >
            {{ option.label }}
            <span v-if="option.value === modelValue" class="material-symbols-rounded check-icon">check</span>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';

const props = defineProps<{
  modelValue: string | number;
  options: Array<{ label: string; value: string | number }>;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void;
  (e: 'change', value: string | number): void;
}>();

const isOpen = ref(false);
const containerRef = ref<HTMLElement | null>(null);
const menuRef = ref<HTMLElement | null>(null);
const menuPosition = ref({ top: 0, left: 0, width: 0 });

const selectedLabel = computed(() => {
  const option = props.options.find(o => o.value === props.modelValue);
  return option ? option.label : props.modelValue;
});

const menuStyle = computed(() => ({
  top: `${menuPosition.value.top}px`,
  left: `${menuPosition.value.left}px`,
  minWidth: `${menuPosition.value.width}px`
}));

const updatePosition = () => {
  if (containerRef.value) {
    const rect = containerRef.value.getBoundingClientRect();
    menuPosition.value = {
      top: rect.bottom + 4, // 4px gap
      left: rect.left,
      width: rect.width
    };
  }
};

const toggleMenu = async () => {
  if (isOpen.value) {
    isOpen.value = false;
  } else {
    updatePosition();
    isOpen.value = true;
    // Recalculate after render to ensure it fits in viewport (optional, simplified for now)
  }
};

const selectOption = (option: { label: string; value: string | number }) => {
  emit('update:modelValue', option.value);
  emit('change', option.value);
  isOpen.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  if (
    containerRef.value && 
    !containerRef.value.contains(event.target as Node) &&
    menuRef.value &&
    !menuRef.value.contains(event.target as Node)
  ) {
    isOpen.value = false;
  }
};

const handleScroll = () => {
  if (isOpen.value) {
    // Update position or close. Closing is safer/easier for now.
    // updatePosition(); 
    isOpen.value = false;
  }
};

const handleResize = () => {
  if (isOpen.value) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('scroll', handleScroll, true); // Capture phase to detect scroll in any container
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('scroll', handleScroll, true);
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.m3-select-container {
  position: relative;
  display: inline-block;
  min-width: 120px;
}

.m3-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px 8px 16px;
  background: var(--md-sys-color-surface-container-highest);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  color: var(--md-sys-color-on-surface);
  font-size: 14px;
  font-weight: 500;
}

.m3-select-trigger:hover {
  background: var(--md-sys-color-surface-container-high);
}

.m3-select-trigger.active {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.arrow-icon {
  font-size: 20px;
  transition: transform 0.2s;
  margin-left: 8px;
}

.arrow-icon.rotated {
  transform: rotate(180deg);
}

.m3-select-menu {
  position: fixed;
  background: var(--md-sys-color-surface-container);
  border-radius: 4px;
  padding: 4px 0;
  box-shadow: var(--md-sys-elevation-2);
  z-index: 9999;
  overflow: hidden;
  margin-top: 4px;
}

.m3-select-option {
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  color: var(--md-sys-color-on-surface);
  transition: background 0.2s;
  gap: 12px;
}

.m3-select-option:hover {
  background: var(--md-sys-color-surface-container-high);
}

.m3-select-option.selected {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.check-icon {
  font-size: 18px;
}

/* Transitions */
.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.scale-fade-enter-from,
.scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
