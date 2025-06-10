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
                <div class="d-flex align-items-center gap-3">
                  <div class="avatar-preview" v-if="avatarPreview || userData?.avatar_url">
                    <img :src="displayedAvatarUrl" alt="Превью аватара" class="w-32 h-32 rounded-full object-cover border-2 border-gray-300">
                  </div>
                  <div class="d-flex flex-column">
                    <input type="file" class="form-control d-none" id="avatar" @change="handleFileSelect" accept="image/*">
                    <label for="avatar" class="btn btn-outline-secondary">Выберите файл</label>
                    <small class="text-light-50 mt-1">Максимальный размер: 5MB</small>
                    <small v-if="error" class="text-danger mt-1">{{ error }}</small>
                  </div>
                </div>
              </div>
              <button class="btn btn-primary" @click="uploadAvatar">
                {{ loading ? 'Загрузка...' : 'Сохранить изменения профиля' }}
              </button>
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
              <div class="d-flex justify-content-between align-items-center mt-4">
                <div>
                  <button class="btn btn-primary me-2">Сохранить изменения аккаунта</button>
                  <button class="btn btn-danger me-2" @click="deleteAccount">Удалить аккаунт</button>
                  <button class="btn btn-secondary" @click="logout">Выйти из аккаунта</button>
                </div>
              </div>
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
import { ref, computed, onMounted, watch } from 'vue';
import { useUserStore } from '@/stores/user';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const userStore = useUserStore();
const { userData, isLoggedIn } = storeToRefs(userStore);
const { fetchUserData } = userStore;

const selectedFile = ref<File | null>(null);
const avatarPreview = ref<string | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const router = useRouter();
const activeTab = ref('account');

// Добавляем отладочные логи для наблюдения за selectedFile и loading
console.log('SettingsView: selectedFile начальное значение:', selectedFile.value);
console.log('SettingsView: loading начальное значение:', loading.value);

// Вычисляемое свойство для определения URL отображаемого аватара
const displayedAvatarUrl = computed(() => {
  // Используем VITE_BACKEND_URL из env если доступен, иначе дефолт
  const backendBaseUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
  
  if (avatarPreview.value) {
    // Если есть превью, используем его (это Data URL)
    return avatarPreview.value;
  } else if (userData.value?.avatar_url) {
    // Если есть аватар в userData, формируем полный URL
    // Убираем дублирование /media/ в пути (хотя бэкенд теперь должен давать правильный URL)
    const url = userData.value.avatar_url; // Просто используем URL из данных
    console.log('SettingsView: Computed avatar URL:', url);
    return url;
  } else {
    // Возвращаем пустую строку или URL дефолтной аватарки
    console.log('SettingsView: userData.avatar_url is not set.');
    return ''; // Можно заменить на URL дефолтной картинки
  }
});

const handleFileSelect = (event: Event) => {
  console.log('SettingsView: handleFileSelect вызвана');
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    
    // Проверяем тип файла
    if (!file.type.startsWith('image/')) {
      error.value = 'Пожалуйста, выберите изображение';
      selectedFile.value = null; // Очищаем selectedFile при ошибке
      avatarPreview.value = null;
      console.log('SettingsView: Ошибка - не изображение. selectedFile:', selectedFile.value);
      return;
    }
    
    // Проверяем размер файла (максимум 5MB)
    if (file.size > 5 * 1024 * 1024) {
      error.value = 'Размер файла не должен превышать 5MB';
      selectedFile.value = null; // Очищаем selectedFile при ошибке
      avatarPreview.value = null;
      console.log('SettingsView: Ошибка - большой файл. selectedFile:', selectedFile.value);
      return;
    }
    
    selectedFile.value = file;
    error.value = null;
    console.log('SettingsView: Файл успешно выбран. selectedFile:', selectedFile.value);
    
    // Создаем превью
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target?.result as string;
      console.log('SettingsView: Превью аватара создано');
    };
    reader.readAsDataURL(file);
  }
};

const uploadAvatar = async () => {
  console.log('SettingsView: uploadAvatar вызвана');
  if (!selectedFile.value) {
    console.log('SettingsView: uploadAvatar: selectedFile отсутствует, выходим.');
    return;
  }
  
  loading.value = true;
  error.value = null;
   console.log('SettingsView: uploadAvatar: Устанавливаем loading = true.');
  
  try {
    console.log('SettingsView: Вызываем userStore.updateAvatar...');
    await userStore.updateAvatar(selectedFile.value);
    console.log('SettingsView: userStore.updateAvatar успешно выполнен.');
    
    // Очищаем выбранный файл и превью после успешной загрузки
    selectedFile.value = null;
    avatarPreview.value = null;
     console.log('SettingsView: selectedFile и avatarPreview очищены после успеха.');
  } catch (err) {
    error.value = 'Ошибка при загрузке аватара';
    console.error('SettingsView: Ошибка в uploadAvatar:', err);
  } finally {
    loading.value = false;
     console.log('SettingsView: uploadAvatar завершен, устанавливаем loading = false.');
  }
};

const logout = async () => {
  try {
    await userStore.logout();
    router.push('/auth/login');
  } catch (error) {
    console.error('Ошибка при выходе из аккаунта:', error);
  }
};

const deleteAccount = async () => {
  if (confirm('Вы уверены, что хотите удалить аккаунт? Это действие нельзя отменить.')) {
    try {
      await userStore.deleteAccount();
      router.push('/auth/login');
    } catch (error) {
      console.error('Ошибка при удалении аккаунта:', error);
    }
  }
};

onMounted(() => {
  console.log('SettingsView: Mounted');
  if (isLoggedIn.value) {
    console.log('SettingsView: User is logged in, fetching data...');
    fetchUserData();
  }
  console.log('SettingsView: Initial userData in store:', userData.value);
});

watch(userData, (newValue, oldValue) => {
  console.log('SettingsView: userData changed:', { oldValue, newValue });
  console.log('SettingsView: displayedAvatarUrl after userData change:', displayedAvatarUrl.value);
});
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

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #a8e6cf;
  box-shadow: 0 0 20px rgba(168, 230, 207, 0.3);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.text-light-50 {
  color: rgba(255, 255, 255, 0.5);
}

.text-danger {
  color: #e57373;
}
</style> 