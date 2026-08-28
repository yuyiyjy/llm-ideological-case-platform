<template>
  <div class="app">
    <NavBar v-if="showNav" />
    <div class="main" :class="{ admin: isAdmin, full: !showNav }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
// 登录页与 404 页不显示顶部导航
const showNav = computed(() => !['/login', '/404'].includes(route.path))
const isAdmin = computed(() => route.path.startsWith('/admin'))
</script>

<style scoped>
.main {
  padding-top: 64px;
  min-height: 100vh;
  background: #f5f7fa;
}
.main.full {
  padding-top: 0;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
