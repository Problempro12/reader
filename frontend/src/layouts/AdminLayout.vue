<template>
  <div class="admin-layout">
    <nav class="admin-nav">
      <div class="admin-nav-header">
        <h1>Админ-панель</h1>
      </div>
      <div class="admin-nav-menu">
        <router-link to="/admin" class="admin-nav-item" active-class="active">
          <i class="bi bi-book"></i>
          <span>Книги</span>
        </router-link>
        <!-- Здесь будут другие пункты меню -->
      </div>
    </nav>
    <main class="admin-content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
// Здесь будет логика авторизации админа
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: #1a1a1a;
}

.admin-nav {
  width: 250px;
  background: #2a2a2a;
  color: #fff;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  z-index: 1000;
}

.admin-nav-header {
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1rem;
}

.admin-nav-header h1 {
  font-size: 1.5rem;
  margin: 0;
  color: #fff;
}

.admin-nav-menu {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.admin-nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.admin-nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.admin-nav-item.active {
  background: #0d6efd;
  color: #fff;
}

.admin-nav-item i {
  font-size: 1.2rem;
}

.admin-content {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
  background: #1a1a1a;
}

@media (max-width: 768px) {
  .admin-layout {
    flex-direction: column;
  }

  .admin-nav {
    width: 100%;
    height: auto;
    position: relative;
  }

  .admin-content {
    margin-left: 0;
    padding: 1rem;
  }
}
</style> 