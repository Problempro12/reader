<template>
  <div class="achievements-page">
    <div class="container mt-4 pb-5">
      
      <!-- Индикатор загрузки -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-muted">Загрузка достижений...</p>
      </div>
      
      <!-- Сообщение об ошибке -->
      <div v-else-if="error" class="alert alert-danger text-center" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
        <button @click="loadAchievements" class="btn btn-outline-danger btn-sm ms-3">
          <i class="bi bi-arrow-clockwise me-1"></i>
          Повторить
        </button>
      </div>

      <!-- Фильтры достижений -->
      <section v-else class="achievement-filters mb-4">
         <div class="d-flex flex-wrap justify-content-center gap-3 mb-3">
             <button 
                class="btn" 
                :class="{ 'btn-primary': activeFilter.status === 'all', 'btn-outline-secondary': activeFilter.status !== 'all' }"
                @click="setFilter({ status: 'all' })"
             >
                 Все (статус)
             </button>
              <button 
                class="btn" 
                :class="{ 'btn-primary': activeFilter.status === 'completed', 'btn-outline-secondary': activeFilter.status !== 'completed' }"
                @click="setFilter({ status: 'completed' })"
             >
                 Готово
             </button>
               <button 
                class="btn" 
                :class="{ 'btn-primary': activeFilter.status === 'in-progress', 'btn-outline-secondary': activeFilter.status !== 'in-progress' }"
                @click="setFilter({ status: 'in-progress' })"
             >
                 В процессе
             </button>
         </div>
         <div class="d-flex flex-wrap justify-content-center gap-3">
              <button 
                class="btn" 
                :class="{ 'btn-primary': activeFilter.type === 'all', 'btn-outline-secondary': activeFilter.type !== 'all' }"
                @click="setFilter({ type: 'all' })"
             >
                 Все (тип)
             </button>
              <button 
                class="btn" 
                :class="{ 'btn-primary': activeFilter.type === 'reading', 'btn-outline-secondary': activeFilter.type !== 'reading' }"
                @click="setFilter({ type: 'reading' })"
             >
                 Чтение
             </button>
               <button 
                class="btn" 
                :class="{ 'btn-primary': activeFilter.type === 'voting', 'btn-outline-secondary': activeFilter.type !== 'voting' }"
                @click="setFilter({ type: 'voting' })"
             >
                 Голосование
             </button>

         </div>
      </section>

      <!-- Секция статистики активности -->
      <section class="stats-section mb-5">
         <h2 class="section-title text-center">Твоя статистика</h2>
         <div class="row row-cols-1 row-cols-sm-2 row-cols-md-4 g-4">
            <div class="col">
                 <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-hourglass"></i></div>
                    <div class="stat-content">
                       <h3 class="stat-value">0</h3>
                       <p class="stat-label">часов начитано</p>
                    </div>
                 </div>
            </div>
             <div class="col">
                 <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-star"></i></div>
                    <div class="stat-content">
                       <h3 class="stat-value">0</h3>
                       <p class="stat-label">книг оценено</p>
                    </div>
                 </div>
            </div>

             <div class="col">
                 <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-check-circle"></i></div>
                    <div class="stat-content">
                       <h3 class="stat-value">0</h3>
                       <p class="stat-label">голосов отдано</p>
                    </div>
                 </div>
            </div>

            <div class="col">
                 <div class="stat-card">
                    <div class="stat-icon"><i class="bi bi-trophy"></i></div>
                    <div class="stat-content">
                       <h3 class="stat-value">{{ completedAchievementsCount }}</h3>
                       <p class="stat-label">достижений получено</p>
                    </div>
                 </div>
            </div>
         </div>
      </section>

      <!-- Секция достижений -->
      <section class="achievements-section mb-5">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h1 class="section-title mb-0">Мои достижения</h1>
          <button 
            @click="refreshAchievements" 
            :disabled="loading"
            class="btn btn-outline-primary"
            title="Обновить достижения"
          >
            <i class="bi bi-arrow-clockwise" :class="{ 'spin': loading }"></i>
          </button>
        </div>
        <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
          <!-- Используем v-for для отображения отфильтрованных достижений -->
          <div class="col" v-for="achievement in displayedAchievements" :key="achievement.id">
            <div 
              class="achievement-card" 
              :class="{ 'completed': achievement.completed }" 
              @click="showAchievementDetails(achievement)"
            >
              <div class="achievement-icon">
                 <i :class="achievement.iconClass"></i>
              </div>
              <div class="achievement-info">
                <h3 class="achievement-title">{{ achievement.title }}</h3>
                <p class="achievement-description">{{ achievement.description }}</p>
                <div class="achievement-progress">
                   <div class="progress" v-if="!achievement.completed" role="progressbar" aria-label="Progress" :aria-valuenow="achievement.progress" aria-valuemin="0" aria-valuemax="100">
                    <div class="progress-bar" :style="{ width: achievement.progress + '%' }"></div>
                  </div>
                  <span class="progress-text">{{ achievement.completed ? achievement.completionDate : achievement.progressText }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Кнопка показать больше/меньше -->
        <div class="text-center mt-4" v-if="filteredAchievements.length > 3">
          <button 
            class="btn btn-outline-primary" 
            @click="toggleShowAll"
          >
            {{ showAll ? 'Показать меньше' : 'Показать все' }}
          </button>
        </div>
      </section>

      <!-- Секция прогресса к следующему уровню -->
      <section class="level-progress-section mb-5">
         <h2 class="section-title text-center">Твой уровень</h2>
          <div class="level-card">
             <div class="level-icon">
                 <i class="bi bi-book-fill"></i>
                 <span>1</span>
             </div>
             <div class="level-info">
                 <p class="current-level">Текущий уровень: Читатель 1</p>
                  <div class="level-progress-bar">
                      <div class="progress" role="progressbar" aria-label="Level Progress" aria-valuenow="10" aria-valuemin="0" aria-valuemax="100">
                        <div class="progress-bar" style="width: 10%"></div>
                      </div>
                      <span class="progress-text">10% до уровня 2</span>
                  </div>
                  <p class="level-hint">Сделай больше отметок для следующего уровня.</p>
             </div>
          </div>
      </section>

      <!-- Секция рекомендаций для достижений -->
      <section class="recommendations-section">
         <h2 class="section-title text-center">Бери и делай</h2>
         <div class="row row-cols-1 row-cols-md-3 g-4">
             <div class="col" v-for="recommendation in recommendations" :key="recommendation.id">
                 <div class="recommendation-card">
                     <div class="recommendation-icon"><i :class="recommendation.iconClass"></i></div>
                     <div class="recommendation-info">
                         <h3 class="recommendation-title">{{ recommendation.title }}</h3>
                         <p class="recommendation-description">{{ recommendation.description }}</p>
                         <div v-if="recommendation.progress" class="progress mt-2" style="height: 6px;">
                           <div class="progress-bar" :style="{ width: recommendation.progress + '%' }"></div>
                         </div>
                     </div>
                      <button class="btn btn-primary">{{ recommendation.buttonText }}</button>
                 </div>
             </div>
         </div>
      </section>

    </div>

    <!-- Модальное окно деталей достижения -->
    <div class="achievement-details-modal" v-if="showModal" @click.self="hideAchievementDetails">
      <div class="modal-content" :class="{ 'completed': selectedAchievement?.completed }">
        <button type="button" class="btn-close" aria-label="Close" @click="hideAchievementDetails"></button>
        <div class="modal-icon">
          <i :class="selectedAchievement?.iconClass"></i>
        </div>
        <div class="modal-title">{{ selectedAchievement?.title }}</div>
        <div class="modal-description">{{ selectedAchievement?.description }}</div>
        <div class="modal-progress" v-if="selectedAchievement && !selectedAchievement.completed">
           <div class="progress" role="progressbar" aria-label="Progress" :aria-valuenow="selectedAchievement.progress" aria-valuemin="0" aria-valuemax="100">
            <div class="progress-bar" :style="{ width: selectedAchievement.progress + '%' }"></div>
          </div>
          <div class="progress-text">{{ selectedAchievement.progressText }}</div>
        </div>
         <div class="modal-completion-date" v-if="selectedAchievement?.completed">
             Получено: {{ selectedAchievement?.completionDate }}
         </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { fetchUserAchievements, fetchAllAchievements, checkAchievements } from '@/api/achievements'
import type { Achievement as ApiAchievement, UserAchievement } from '@/api/achievements'

interface Achievement {
  id: number;
  title: string;
  description: string;
  iconClass: string;
  completed: boolean;
  progress?: number; // 0-100 for not completed
  progressText?: string; // e.g. "3/4 отметок"
  completionDate?: string; // e.g. "Получено 01.06.2025"
  type?: 'reading' | 'voting'; // Добавляем тип достижения
}

// Состояние компонента
const loading = ref(false)
const error = ref<string | null>(null)

// Данные достижений
const allAchievements = ref<ApiAchievement[]>([])
const userAchievements = ref<UserAchievement[]>([])

// Преобразованные данные для отображения
const achievements = ref<Achievement[]>([])

const showModal = ref(false);
const selectedAchievement = ref<Achievement | null>(null);
const showAll = ref(false);

const showAchievementDetails = (achievement: Achievement) => {
  selectedAchievement.value = achievement;
  showModal.value = true;
};

const hideAchievementDetails = () => {
  showModal.value = false;
  selectedAchievement.value = null; // Очищаем данные при закрытии
};

// Логика фильтрации
const activeFilter = ref({
  status: 'all', // 'all', 'completed', 'in-progress'
  type: 'all' // 'all', 'reading', 'voting'
});

const setFilter = (filter: { status?: string; type?: string }) => {
  activeFilter.value = { ...activeFilter.value, ...filter };
};

const filteredAchievements = computed(() => {
  return achievements.value.filter(achievement => {
    const statusMatch = activeFilter.value.status === 'all' || 
                        (activeFilter.value.status === 'completed' && achievement.completed) || 
                        (activeFilter.value.status === 'in-progress' && !achievement.completed);
    
    const typeMatch = activeFilter.value.type === 'all' || achievement.type === activeFilter.value.type;

    return statusMatch && typeMatch;
  });
});

// Отображаемые достижения (все или только первые три)
const displayedAchievements = computed(() => {
  return showAll.value ? filteredAchievements.value : filteredAchievements.value.slice(0, 3);
});

// Количество выполненных достижений
const completedAchievementsCount = computed(() => {
  return achievements.value.filter(achievement => achievement.completed).length;
});

// Рекомендации для достижений
const recommendations = computed(() => {
  const incompleteAchievements = achievements.value.filter(a => !a.completed)
  return incompleteAchievements.slice(0, 3).map(achievement => ({
    id: achievement.id,
    title: achievement.title,
    description: achievement.description,
    iconClass: achievement.iconClass,
    progress: 0,
    buttonText: getButtonTextForType(achievement.type)
  }))
})

// Функция получения текста кнопки по типу достижения
const getButtonTextForType = (type?: string): string => {
  const buttonMap: Record<string, string> = {
    'reading': 'К книге',
    'voting': 'Оценить'
  }
  return buttonMap[type || 'reading'] || 'Перейти'
}

// Вычисляемые свойства для статистики
const completedCount = computed(() => {
  return achievements.value.filter(a => a.completed).length
})

const totalCount = computed(() => {
  return achievements.value.length
})

const completionPercentage = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

const currentLevel = computed(() => {
  return Math.floor(completedCount.value / 5) + 1
})

const nextLevelProgress = computed(() => {
  const achievementsForNextLevel = (currentLevel.value * 5) - completedCount.value
  return Math.max(0, 5 - achievementsForNextLevel)
})



const toggleShowAll = () => {
  showAll.value = !showAll.value;
};

// Загрузка данных при монтировании компонента
onMounted(async () => {
  await loadAchievements()
})

// Функция загрузки достижений
const loadAchievements = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Загружаем все данные параллельно
     const [allAchievementsData, userAchievementsData] = await Promise.all([
       fetchAllAchievements(),
       fetchUserAchievements()
     ])
     
     
     
     allAchievements.value = allAchievementsData
     userAchievements.value = userAchievementsData
    
    // Преобразуем данные для отображения
    transformAchievementsData()
    
    // Проверяем новые достижения
    await checkAchievements()
    
  } catch (err) {
    console.error('Ошибка загрузки достижений:', err)
    error.value = 'Не удалось загрузить достижения'
  } finally {
    loading.value = false
  }
}

// Функция преобразования данных достижений
 const transformAchievementsData = () => {
    
    
    if (!Array.isArray(allAchievements.value)) {
      console.error('allAchievements.value не является массивом:', allAchievements.value)
      achievements.value = []
      return
    }
    
    if (!Array.isArray(userAchievements.value)) {
      console.error('userAchievements.value не является массивом:', userAchievements.value)
      userAchievements.value = []
    }
    
    achievements.value = allAchievements.value.map(achievement => {
      const userAchievement = userAchievements.value.find(ua => ua.achievement.id === achievement.id)
      
      return {
        id: achievement.id,
        title: achievement.title,
        description: achievement.description,
        iconClass: getCategoryIcon(achievement.category),
        completed: !!userAchievement,
        progress: userAchievement ? 100 : 0,
        progressText: userAchievement ? 'Выполнено' : 'Не выполнено',
        completionDate: userAchievement ? 
          new Date(userAchievement.earned_at).toLocaleDateString('ru-RU') : 
          undefined,
        type: mapCategoryToType(achievement.category)
      }
    })
  }

// Функция получения иконки по категории
const getCategoryIcon = (category: string): string => {
  const iconMap: Record<string, string> = {
    'READING': 'bi bi-book',
    'BOOKS': 'bi bi-collection',
    'SOCIAL': 'bi bi-people',
    'OTHER': 'bi bi-award'
  }
  return iconMap[category] || 'bi bi-award'
}

// Функция преобразования категории в тип
const mapCategoryToType = (category: string): 'reading' | 'voting' => {
  const typeMap: Record<string, 'reading' | 'voting'> = {
    'READING': 'reading',
    'BOOKS': 'reading',
    'SOCIAL': 'reading',
    'OTHER': 'voting'
  }
  return typeMap[category] || 'reading'
}

// Функция обновления достижений
const refreshAchievements = async () => {
  await loadAchievements()
}

</script>

<style scoped>
.achievements-page {
   min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

.section-title {
  color: #a8e6cf;
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 2.5rem;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: #a8e6cf;
}

/* Achievement Cards */
.achievement-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(168, 230, 207, 0.1);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    gap: 1rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    height: 100%; /* Убедимся, что карточки имеют одинаковую высоту в ряду */
    cursor: pointer; /* Добавляем курсор-указатель */
}

.achievement-card:hover {
    transform: translateY(-8px); /* Чуть больше подпрыгивание */
     box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
}

.achievement-card.completed {
   background: linear-gradient(45deg, rgba(168, 230, 207, 0.2), rgba(140, 211, 176, 0.2));
   border-color: rgba(168, 230, 207, 0.3);
   position: relative; /* Для псевдоэлемента */
   overflow: hidden; /* Скрыть градиент свечения за пределами карточки */
}

/* Эффект свечения для выполненных достижений */
.achievement-card.completed::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(168, 230, 207, 0.3) 0%, transparent 70%);
    opacity: 0;
    animation: pulse-shine 2s ease-out infinite;
    z-index: 0;
}

@keyframes pulse-shine {
    0% { opacity: 0; transform: scale(0.5); }
    50% { opacity: 1; transform: scale(1); }
    100% { opacity: 0; transform: scale(0.5); }
}

.achievement-icon {
    font-size: 3.5rem; /* Увеличим размер значка */
    text-align: center;
    margin-bottom: 1rem;
    position: relative; /* Для z-index */
    z-index: 1; /* Убедимся, что значок поверх свечения */
}

.achievement-card.completed .achievement-icon i {
    color: #a8e6cf; /* Яркий цвет для выполненных */
    filter: drop-shadow(0 0 12px rgba(168, 230, 207, 0.6)); /* Усилим свечение */
    transition: transform 0.3s ease;
}

.achievement-card.completed:hover .achievement-icon i {
    animation: bounce 0.5s ease infinite alternate;
}

@keyframes bounce {
    0% { transform: translateY(0); }
    100% { transform: translateY(-8px); }
}

.achievement-card.not-completed .achievement-icon i {
    color: rgba(255, 255, 255, 0.3); /* Тусклый цвет для не выполненных */
}

.achievement-info {
    flex-grow: 1;
}

.achievement-title {
    font-size: 1.3rem; /* Чуть крупнее */
    font-weight: bold;
    margin-bottom: 0.5rem;
    color: #a8e6cf;
}

.achievement-description {
    font-size: 1rem; /* Чуть крупнее */
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 1rem;
}

.achievement-progress .progress {
   height: 10px; /* Чуть толще */
   background-color: rgba(255, 255, 255, 0.1);
   border-radius: 5px; /* Чуть больше скругление */
   margin-bottom: 0.5rem;
   overflow: hidden; /* Скрыть переполнение полосы */
}

.achievement-progress .progress-bar {
    background: linear-gradient(45deg, #a8e6cf, #8cd3b0); /* Градиентная полоса прогресса */
    transition: width 0.5s ease; /* Плавное заполнение */
}

.achievement-card.completed .achievement-progress .progress-bar {
     background: linear-gradient(45deg, #ffd700, #ffa500); /* Золотой градиент для выполненных */
}

.achievement-progress .progress-text {
    font-size: 0.9rem; /* Чуть крупнее */
    color: rgba(255, 255, 255, 0.7);
    text-align: right; /* Выравнивание текста прогресса */
    display: block; /* Чтобы текст был на отдельной строке */
}

.achievement-card.completed .achievement-progress .progress-text {
     color: #a8e6cf;
     font-weight: 500;
}

/* Stats Cards */
.stats-section .stat-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(168, 230, 207, 0.1);
    border-radius: 15px;
    padding: 1.5rem;
    padding-right: 0.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
     transition: transform 0.3s ease;
}

.stats-section .stat-card:hover {
     transform: translateY(-5px);
}

.stats-section .stat-icon {
    font-size: 2rem;
    color: #a8e6cf;
}

.stats-section .stat-value {
     font-size: 1.8rem;
    font-weight: bold;
    margin: 0;
    color: #fff;
}

.stats-section .stat-label {
     font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
}

/* Level Progress Section */
.level-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(168, 230, 207, 0.1);
    border-radius: 15px;
    padding: 1.5rem;
    padding-right: 0.5rem;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    gap: 2rem;
}

.level-icon {
    font-size: 3.5rem;
    color: #a8e6cf;
    position: relative;
}

.level-icon span {
    position: absolute;
    top: 46%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.5rem;
    font-weight: bold;
    color: #38424e; /* Цвет текста на иконке */
}

.level-info {
    flex-grow: 1;
}

.current-level {
    font-size: 1.5rem;
    font-weight: bold;
    color: #a8e6cf;
    margin-bottom: 1rem;
}

.level-progress-bar .progress {
   height: 12px;
   background-color: rgba(255, 255, 255, 0.1);
   border-radius: 6px;
   margin-bottom: 0.5rem;
}

.level-progress-bar .progress-bar {
    background: linear-gradient(90deg, #a8e6cf, #8cd3b0); /* Горизонтальный градиент */
    transition: width 0.5s ease; /* Плавное заполнение */
}

.level-progress-bar .progress-text {
     font-size: 1rem;
    color: rgba(255, 255, 255, 0.7);
}

.level-hint {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 1rem;
}

/* Recommendations Section */
.recommendation-card {
   background: rgba(168, 230, 207, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(168, 230, 207, 0.2);
    border-radius: 15px;
    padding: 1.5rem;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    gap: 1rem;
     transition: transform 0.3s ease;
    height: 100%; /* Убедимся, что карточки имеют одинаковую высоту в ряду */
}

.recommendation-card:hover {
     transform: translateY(-5px);
}

.recommendation-icon {
    font-size: 2.5rem;
    color: #a8e6cf;
    text-align: center;
}

.recommendation-info {
     flex-grow: 1;
}

.recommendation-title {
     font-size: 1.3rem;
    font-weight: bold;
    color: #a8e6cf;
    margin-bottom: 0.5rem;
}

.recommendation-description {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 1rem;
}

.recommendation-card .btn {
     width: 100%;
}

/* Адаптивность */
@media (max-width: 768px) {
    .section-title {
        font-size: 2rem;
    }

    .level-card {
        flex-direction: column;
        text-align: center;
    }

    .level-icon {
        margin-bottom: 1rem;
    }

    .level-icon span {
         font-size: 1.2rem;
    }

     .achievement-icon {
         font-size: 3rem; /* Скорректируем размер для мобильных */
     }

      .stats-section .stat-icon {
         font-size: 1.5rem; /* Скорректируем размер для мобильных */
      }

      .achievement-card {
          padding: 1rem; /* Меньший отступ на мобильных */
      }

       .achievement-title {
           font-size: 1.1rem;
       }

        .achievement-description {
            font-size: 0.85rem;
        }

         .achievement-progress .progress-text {
             font-size: 0.8rem;
         }

          .stats-section .stat-value {
             font-size: 1.6rem;
          }

          .stats-section .stat-label {
             font-size: 0.8rem;
          }

    .achievement-filters .btn {
        padding: 0.4rem 1rem;
        font-size: 0.9rem;
    }
}

/* Styles for the Achievement Details Modal */
.achievement-details-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6); /* Полупрозрачный темный фон */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050; /* Поверх всего */
  backdrop-filter: blur(5px); /* Небольшое размытие фона */
}

.modal-content {
  background: #2c3e50; /* Цвет фона модального окна */
  color: #fff; /* Цвет текста */
  border-radius: 15px;
  padding: 2rem;
  max-width: 400px; /* Максимальная ширина */
  width: 90%; /* Ширина на меньших экранах */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  position: relative;
  text-align: center;
  transform: scale(0.95); /* Начальный размер для анимации */
  opacity: 0; /* Начальная прозрачность */
  animation: scaleIn 0.3s ease forwards; /* Анимация появления */
}

@keyframes scaleIn {
  to { transform: scale(1); opacity: 1; }
}

.modal-content.completed {
    background: linear-gradient(45deg, #2c3e50, #34495e); /* Немного другой фон для выполненных */
    border: 1px solid rgba(168, 230, 207, 0.3);
}

.modal-content .btn-close {
  position: absolute;
  top: 15px;
  right: 15px;
  filter: invert(1); /* Делаем крестик белым */
  opacity: 0.7; /* Немного прозрачности */
  transition: opacity 0.3s ease;
}

.modal-content .btn-close:hover {
  opacity: 1;
}

.modal-icon {
  font-size: 4rem;
  color: #a8e6cf;
  margin-bottom: 1rem;
}

.modal-content.completed .modal-icon i {
    filter: drop-shadow(0 0 15px rgba(168, 230, 207, 0.7)); /* Свечение иконки в модалке */
}

.modal-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #a8e6cf;
  margin-bottom: 0.5rem;
}

.modal-description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
}

.modal-progress {
  margin-bottom: 1rem;
}

.modal-progress .progress {
    height: 10px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 5px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

.modal-progress .progress-bar {
     background: linear-gradient(45deg, #a8e6cf, #8cd3b0);
     transition: width 0.5s ease;
}

.modal-progress .progress-text {
     font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
}

.modal-completion-date {
     font-size: 1rem;
    color: #a8e6cf;
    font-weight: 500;
}

/* Achievement Filters */
.achievement-filters .btn {
   border-radius: 20px; /* Круглые кнопки */
    padding: 0.5rem 1.5rem;
     transition: all 0.3s ease;
}

.achievement-filters .btn-primary {
    background: linear-gradient(45deg, #a8e6cf, #8cd3b0); /* Градиент для активной кнопки */
    border-color: #a8e6cf;
    color: #1a1a1a; /* Темный текст на светлом градиенте */
    font-weight: bold;
}

.achievement-filters .btn-outline-secondary {
    border-color: rgba(168, 230, 207, 0.5);
    color: rgba(168, 230, 207, 0.8); /* Полупрозрачный цвет текста */
    background-color: transparent; /* Прозрачный фон */
}

.achievement-filters .btn-outline-secondary:hover {
     background-color: rgba(168, 230, 207, 0.1); /* Легкий фон при наведении */
     color: #a8e6cf; /* Ярче текст при наведении */
     border-color: #a8e6cf;
}

/* Добавим стили для кнопки показать больше/меньше */
.btn-outline-primary {
  border-color: #a8e6cf;
  color: #a8e6cf;
  padding: 0.5rem 2rem;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  background-color: #a8e6cf;
  color: #2c3e50;
  border-color: #a8e6cf;
}

/* Анимация вращения для кнопки обновления */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>