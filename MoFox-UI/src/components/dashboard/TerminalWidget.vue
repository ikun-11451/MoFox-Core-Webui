<script setup lang="ts">
</script>

<template>
  <div class="terminal-widget">
    <div class="header">
      <span class="dots">
        <span class="dot red"></span>
        <span class="dot yellow"></span>
        <span class="dot green"></span>
      </span>
      <span class="title">TERMINAL.EXE</span>
    </div>
    <div class="content">
      <div class="line muted">Last login: Mon Oct 24 10:23:12 on ttys001</div>
      <div class="line">> init_core_modules...</div>
      <div class="line info">[INFO] Loading language model v4.2</div>
      <div class="line info">[INFO] Connecting to vector database...</div>
      <div class="line success">[SUCCESS] Connection established (12ms)</div>
      <div class="line">> monitoring_stream --active</div>
      <div class="line warn">[WARN] High latency detected in region: ap-northeast</div>
      <div class="line info">[INFO] Scaling up instances...</div>
      <div class="line cursor">> <span class="blink">_</span></div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.terminal-widget {
  background: black;
  color: #00ff00;
  border-radius: 6px;
  overflow: hidden;
  font-family: 'Courier New', Courier, monospace;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .header {
    background: #222;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    
    .dots {
      display: flex;
      gap: 6px;
      margin-right: 15px;
      
      .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        
        &.red { background: #ff5f56; }
        &.yellow { background: #ffbd2e; }
        &.green { background: #27c93f; }
      }
    }
    
    .title {
      color: #888;
      font-size: 0.8rem;
    }
  }
  
  .content {
    padding: 15px;
    font-size: 0.85rem;
    line-height: 1.5;
    
    .line { margin-bottom: 4px; }
    .muted { color: #666; }
    .info { color: #4facfe; }
    .success { color: #00c853; }
    .warn { color: #ffbd2e; }
    
    .blink {
      animation: blink 1s infinite;
    }
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
