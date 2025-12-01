<script setup lang="ts">
import StatCard from '@/components/dashboard/StatCard.vue'
import TerminalWidget from '@/components/dashboard/TerminalWidget.vue'
import { onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref<HTMLElement | null>(null)

onMounted(() => {
  if (chartRef.value) {
    const myChart = echarts.init(chartRef.value)
    const option = {
      grid: { top: 10, right: 10, bottom: 20, left: 30 },
      xAxis: {
        type: 'category',
        data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        axisLine: { lineStyle: { color: '#ccc' } }
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { type: 'dashed' } }
      },
      series: [
        {
          data: [820, 932, 901, 934, 1290, 1330, 1320],
          type: 'line',
          smooth: true,
          lineStyle: { color: '#000', width: 3 },
          itemStyle: { color: '#000' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(0,0,0,0.2)' },
              { offset: 1, color: 'rgba(0,0,0,0)' }
            ])
          }
        }
      ]
    }
    myChart.setOption(option)
    
    window.addEventListener('resize', () => myChart.resize())
  }
})
</script>

<template>
  <div class="dashboard">
    <div class="page-header">
      <div class="title-section">
        <h1>DASHBOARD</h1>
        <p>Welcome back, Operator. System is ready.</p>
      </div>
      <div class="actions">
        <button class="retro-btn secondary">EXPORT LOGS</button>
        <button class="retro-btn primary">+ NEW AGENT</button>
      </div>
    </div>
    
    <!-- Stats Row -->
    <div class="stats-grid">
      <StatCard 
        title="TOTAL CONVERSATIONS" 
        value="24,592" 
        subtext="↗ +12% this week" 
        trend="up"
      />
      <StatCard 
        title="TOKEN USAGE" 
        value="8.2 M" 
        subtext="85% of monthly limit" 
      />
      <StatCard 
        title="ACTIVE USERS" 
        value="1,204" 
        subtext="⚡ 42 online now" 
        trend="up"
      />
      <div class="retro-card server-load">
        <div class="label">SERVER LOAD</div>
        <div class="percentage">32%</div>
        <div class="progress-bar">
          <div class="fill" style="width: 32%"></div>
        </div>
      </div>
    </div>
    
    <!-- Main Content Grid -->
    <div class="main-grid">
      <!-- Left Column: Recent Sessions -->
      <div class="retro-card recent-sessions">
        <div class="card-header">
          <h3>Recent Sessions</h3>
          <a href="#" class="view-all">VIEW ALL</a>
        </div>
        
        <div class="session-list">
          <div class="session-item" v-for="i in 3" :key="i">
            <div class="avatar-box">
              <img src="https://api.dicebear.com/7.x/pixel-art/svg?seed=User{{i}}" alt="avatar" />
            </div>
            <div class="details">
              <div class="user">User_0x8{{i}}</div>
              <div class="query">Explain quantum computing in simple terms...</div>
            </div>
            <div class="time">2m ago</div>
          </div>
        </div>
      </div>
      
      <!-- Right Column: Terminal & Charts -->
      <div class="right-col">
        <div class="terminal-wrapper">
          <TerminalWidget />
        </div>
        <div class="retro-card chart-card">
          <h3>Traffic Analysis</h3>
          <div ref="chartRef" class="chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  
  h1 {
    font-size: 2.5rem;
    margin: 0;
    letter-spacing: -2px;
  }
  
  p {
    margin: 5px 0 0;
    color: #666;
  }
  
  .actions {
    display: flex;
    gap: 15px;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.server-load {
  background: black;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  .label { font-size: 0.8rem; color: #888; margin-bottom: 5px; }
  .percentage { font-size: 2.5rem; font-weight: bold; color: var(--color-accent-green); margin-bottom: 10px; }
  
  .progress-bar {
    height: 6px;
    background: #333;
    border-radius: 3px;
    overflow: hidden;
    
    .fill {
      height: 100%;
      background: var(--color-accent-green);
    }
  }
}

.main-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  min-height: 400px;
}

.recent-sessions {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 { margin: 0; }
    .view-all { color: var(--color-accent-purple); font-weight: bold; text-decoration: none; font-size: 0.8rem; }
  }
  
  .session-item {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px 0;
    border-bottom: 1px solid #eee;
    
    &:last-child { border-bottom: none; }
    
    .avatar-box {
      width: 40px;
      height: 40px;
      border: 2px solid black;
      overflow: hidden;
      img { width: 100%; height: 100%; }
    }
    
    .details {
      flex: 1;
      .user { font-weight: bold; margin-bottom: 3px; }
      .query { color: #666; font-size: 0.9rem; }
    }
    
    .time { color: #aaa; font-size: 0.8rem; }
  }
}

.right-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  .terminal-wrapper {
    height: 250px;
  }
  
  .chart-card {
    flex: 1;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    
    h3 { margin-top: 0; }
    
    .chart-container {
      flex: 1;
      width: 100%;
    }
  }
}
</style>
