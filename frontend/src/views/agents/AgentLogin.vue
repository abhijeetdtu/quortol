<template>
  <div class="agent-login">
    <div class="login-container">
      <h1>Agent Access</h1>
      <p class="subtitle">Login to access agent capabilities</p>
      
      <form @submit.prevent="handleSubmit" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="Enter your username"
            required
          >
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="Enter your password"
            required
          >
        </div>
        
        <div v-if="error" class="error">{{ error }}</div>
        
        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="loading">Logging in...</span>
          <span v-else>Login to Agents</span>
        </button>
        
        <div v-if="registrationEnabled" class="register-link">
          New here? <a href="#" @click.prevent="showRegister">Register</a>
        </div>
      </form>
      
      <div v-if="registrationEnabled && showRegisterForm" class="register-form">
        <h2>Register</h2>
        <form @submit.prevent="handleRegister" class="login-form">
          <div class="form-group">
            <label for="reg-username">Username</label>
            <input 
              type="text" 
              id="reg-username" 
              v-model="registerData.username"
              placeholder="Choose a username"
              required
            >
          </div>
          
          <div class="form-group">
            <label for="reg-email">Email</label>
            <input 
              type="email" 
              id="reg-email" 
              v-model="registerData.email"
              placeholder="Enter your email"
              required
            >
          </div>
          
          <div class="form-group">
            <label for="reg-password">Password</label>
            <input 
              type="password" 
              id="reg-password" 
              v-model="registerData.password"
              placeholder="Choose a password"
              required
            >
          </div>
          
          <div v-if="registerError" class="error">{{ registerError }}</div>
          
          <button type="submit" class="submit-btn" :disabled="registerLoading">
            <span v-if="registerLoading">Creating account...</span>
            <span v-else>Register</span>
          </button>
          
          <div class="login-link">
            Already have an account? <a href="#" @click.prevent="showLogin">Login</a>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { auth } from '../../services/api'
import { useAuthStore } from '../../stores/auth.js'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const showRegisterForm = ref(false)
const registrationEnabled = ref(false)
const registerData = reactive({ username: '', email: '', password: '' })
const registerError = ref('')
const registerLoading = ref(false)

const showRegister = () => {
  showRegisterForm.value = true
  error.value = ''
}

const showLogin = () => {
  showRegisterForm.value = false
  registerError.value = ''
}

onMounted(async () => {
  try {
    const response = await auth.getSettings()
    registrationEnabled.value = Boolean(response.data?.registration_enabled)
  } catch (err) {
    registrationEnabled.value = false
  }
})

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await auth.login(username.value, password.value)
    authStore.login(response.data.user)
    
    const redirect = router.currentRoute.value.query?.redirect
    router.push(redirect || '/agent/dashboard')
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registrationEnabled.value) {
    registerError.value = 'Registration is currently disabled.'
    return
  }

  registerLoading.value = true
  registerError.value = ''
  
  try {
    const response = await auth.register(
      registerData.username,
      registerData.email,
      registerData.password
    )
    
    showRegisterForm.value = false
    username.value = registerData.username
    password.value = registerData.password
    
    // Auto login after registration
    await handleSubmit()
  } catch (err) {
    registerError.value = err.response?.data?.error || 'Registration failed. Please try again.'
  } finally {
    registerLoading.value = false
  }
}
</script>

<style>
.agent-login {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  padding: 2rem;
}

.login-container {
  background: none;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
}

.login-container h1 {
  text-align: center;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #333;
}

.form-group input {
  padding: 0.8rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  box-shadow: inset 0 0 0 1px rgba(84, 101, 198, 0.28);
}

.form-group input:focus {
  outline: none;
  box-shadow: inset 0 0 0 2px rgba(84, 101, 198, 0.5);
}

.error {
  color: #e74c3c;
  font-size: 0.9rem;
  text-align: center;
}

.submit-btn {
  background: none;
  color: #fff;
  padding: 1rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.3s;
  box-shadow: inset 0 0 0 1px rgba(102, 126, 234, 0.65);
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-link, .login-link {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.register-link a, .login-link a {
  color: #667eea;
  text-decoration: none;
}

.register-link a:hover, .login-link a:hover {
  text-decoration: underline;
}
</style>
