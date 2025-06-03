<template>
  <div class="settings-page">
    <div class="container mt-4 pb-5">
      <h1><b>Настройки</b></h1>

      <div class="row">
        <div class="col-md-3">
          <div class="nav flex-column nav-pills me-3" id="v-pills-tab" role="tablist" aria-orientation="vertical">
            <button class="nav-link active" id="v-pills-profile-tab" data-bs-toggle="pill" data-bs-target="#v-pills-profile" type="button" role="tab" aria-controls="v-pills-profile" aria-selected="true">
              <i class="bi bi-person-circle me-2"></i>Профиль
            </button>
            <button class="nav-link" id="v-pills-account-tab" data-bs-toggle="pill" data-bs-target="#v-pills-account" type="button" role="tab" aria-controls="v-pills-account" aria-selected="false">
               <i class="bi bi-key me-2"></i>Аккаунт
            </button>
            <button class="nav-link premium-tab-link" id="v-pills-premium-tab" data-bs-toggle="pill" data-bs-target="#v-pills-premium" type="button" role="tab" aria-controls="v-pills-premium" aria-selected="false">
               <i class="bi bi-star me-2"></i>Премиум
            </button>
          </div>
        </div>
        <div class="col-md-9">
          <div class="tab-content" id="v-pills-tabContent">
            <!-- Профиль Tab -->
            <div class="tab-pane fade show active" id="v-pills-profile" role="tabpanel" aria-labelledby="v-pills-profile-tab">
              <h2>Настройки профиля</h2>
              <div class="mb-3">
                <label for="nickname" class="form-label">Никнейм</label>
                <input type="text" class="form-control" id="nickname" placeholder="Ваш никнейм">
              </div>
              <div class="mb-3">
                <label for="about" class="form-label">О себе</label>
                <textarea class="form-control" id="about" rows="3" placeholder="Расскажите о себе..."></textarea>
              </div>
              <div class="mb-3">
                <label for="avatar" class="form-label mb-1">Аватар</label>
                <input type="file" class="form-control d-none" id="avatar">
                 <label for="avatar" class="btn btn-outline-secondary">Выберите файл</label>
              </div>
              <button class="btn btn-primary">Сохранить изменения профиля</button>
            </div>

            <!-- Аккаунт Tab -->
            <div class="tab-pane fade" id="v-pills-account" role="tabpanel" aria-labelledby="v-pills-account-tab">
              <h2>Настройки аккаунта</h2>
               <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" placeholder="Ваша почта">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Смена пароля</label>
                <input type="password" class="form-control mb-2" id="password" placeholder="Новый пароль">
                 <input type="password" class="form-control" id="confirmPassword" placeholder="Повторите пароль">
              </div>
               <button class="btn btn-primary me-2">Сохранить изменения аккаунта</button>
               <button class="btn btn-danger">Удалить аккаунт</button>
            </div>

            <!-- Премиум Tab -->
            <div class="tab-pane fade" id="v-pills-premium" role="tabpanel" aria-labelledby="v-pills-premium-tab">
              <h2>Премиум подписка</h2>
              <p>Получите доступ к эксклюзивным функциям!</p>
              <button class="btn btn-warning">Купить Премиум</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Логика для настроек и переключения вкладок будет добавлена позже
</script>

<style scoped>
.settings-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

h1 {
  color: #a8e6cf;
  margin-bottom: 2rem;
}

.nav-pills .nav-link {
  color: #a8e6cf;
  border-radius: 10px;
  margin-bottom: 0.5rem;
  transition: all 0.3s ease;
  padding: 1rem 1.5rem;
  text-align: left;
}

.nav-pills .nav-link:hover {
   background-color: rgba(168, 230, 207, 0.1);
   color: #fff;
}

.nav-pills .nav-link.active {
  background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
  color: #1a1a1a;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(168, 230, 207, 0.3);
}

.tab-content {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
}

.tab-content h2 {
  color: #a8e6cf;
  margin-bottom: 1.5rem;
}

.form-label {
  color: #a8e6cf;
  font-weight: 500;
}

.form-control {
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(168, 230, 207, 0.2);
  color: #fff;
}

.form-control:focus {
  background-color: rgba(255, 255, 255, 0.15);
  border-color: #a8e6cf;
  box-shadow: 0 0 0 0.25rem rgba(168, 230, 207, 0.25);
  color: #fff;
}

.form-control::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.btn-primary {
  background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
  border: none;
  color: #1a1a1a;
}

.btn-primary:hover {
  background: linear-gradient(45deg, #8cd3b0, #a8e6cf);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(168, 230, 207, 0.4);
}

.btn-danger {
   background: linear-gradient(45deg, #e57373, #ef5350);
  border: none;
  color: #1a1a1a;
}

.btn-danger:hover {
   background: linear-gradient(45deg, #ef5350, #e57373);
    transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(229, 115, 115, 0.4);
}

.btn-warning {
  background: linear-gradient(45deg, #ffd700, #ffa500);
  border: none;
  color: #1a1a1a;
}

.btn-warning:hover {
  background: linear-gradient(45deg, #ffa500, #ffd700);
   transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

/* Стиль для золотой кнопки вкладки Премиум */
.nav-pills .premium-tab-link {
    color: #ffb74d;
}

.nav-pills .premium-tab-link:hover {
     background-color: rgba(255, 183, 77, 0.1);
     color: #ffe0b2;
}

.nav-pills .premium-tab-link.active {
  background: linear-gradient(45deg, #ffd700, #ffa500);
  color: #1a1a1a;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
  border-color: #ffa500;
}

/* Добавлены стили для кастомной кнопки загрузки файла */
.btn-outline-secondary {
    color: #a8e6cf;
    border: 1px dashed #a8e6cf;
    background-color: rgba(168, 230, 207, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-block;
}

.btn-outline-secondary:hover {
    color: #1a1a1a;
    background-color: #a8e6cf;
    border-color: #a8e6cf;
    box-shadow: 0 2px 10px rgba(168, 230, 207, 0.2);
}

/* Стиль для надписи Аватар */
.form-label[for="avatar"] {
    margin-right: 1rem; /* Добавляем отступ справа */
    vertical-align: middle; /* Выравниваем по центру с кнопкой */
}

/* Адаптивность */
@media (max-width: 768px) {
  .row {
    flex-direction: column;
  }

  .col-md-3, .col-md-9 {
    width: 100%;
  }

  .nav-pills {
    flex-direction: row !important;
    margin-bottom: 1.5rem;
    justify-content: space-around;
  }
  
  .nav-pills .nav-link {
      margin-right: 0.5rem;
      margin-bottom: 0;
  }

  .tab-content {
      padding: 1.5rem;
  }

}
</style> 