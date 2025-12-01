<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')

const handleLogin = () => {
  // Mock login
  if (username.value && password.value) {
    router.push('/')
  }
}
</script>

<template>
  <div class="login-container">
    <div class="retro-card login-card">
      <div class="brand">
        <div class="logo-square">AI</div>
        <h1>NEXUS<span class="thin">UI</span></h1>
      </div>
      
      <div class="form-group">
        <label>OPERATOR ID</label>
        <input v-model="username" type="text" placeholder="ENTER ID..." />
      </div>
      
      <div class="form-group">
        <label>ACCESS KEY</label>
        <input v-model="password" type="password" placeholder="ENTER KEY..." />
      </div>
      
      <button class="retro-btn primary w-full" @click="handleLogin">
        INITIALIZE SESSION
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-app);
}

.login-card {
  width: 400px;
  border-width: 3px;
  box-shadow: 8px 8px 0 var(--color-border);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 2rem;
  
  .logo-square {
    background: var(--color-dark);
    color: white;
    background: black;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
  }
  
  h1 {
    margin: 0;
    font-size: 1.5rem;
    letter-spacing: -1px;
    
    .thin {
      font-weight: normal;
      color: #666;
    }
  }
}

.form-group {
  margin-bottom: 1.5rem;
  
  label {
    display: block;
    font-weight: bold;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
  }
  
  input {
    width: 100%;
    padding: 12px;
    border: 2px solid var(--color-border);
    font-family: var(--font-main);
    font-size: 1rem;
    outline: none;
    
    &:focus {
      background-color: #f0f0f0;
    }
  }
}
</style>
