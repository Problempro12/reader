<template>
  <div class="terms-page">
    <div class="container mt-4 pb-5">
      <div class="policy-content">
        <h1>Условия пользования</h1>
        <p>Добро пожаловать в KpitReading! Пожалуйста, внимательно ознакомьтесь с настоящими условиями пользования перед использованием нашего сервиса.</p>

        <h2>1. Общие положения</h2>
        <ul>
          <li>Используя наш сервис, вы соглашаетесь соблюдать настоящие условия.</li>
          <li>Администрация оставляет за собой право изменять условия в любое время.</li>
        </ul>

        <h2>2. Регистрация и аккаунт</h2>
        <ul>
          <li>Для доступа к некоторым функциям требуется регистрация.</li>
          <li>Вы обязуетесь предоставлять достоверную информацию при регистрации.</li>
          <li>Вы несёте ответственность за сохранность своих данных для входа.</li>
        </ul>

        <h2>3. Использование сервиса</h2>
        <ul>
          <li>Запрещено использовать сервис для противоправных целей.</li>
          <li>Запрещено размещать оскорбительный, вредоносный или запрещённый законом контент.</li>
          <li>Администрация вправе ограничить доступ к сервису при нарушении условий.</li>
        </ul>

        <h2>4. Персональные данные</h2>
        <ul>
          <li>Мы соблюдаем политику конфиденциальности и защищаем ваши данные.</li>
          <li>Подробнее см. <router-link to="/privacy-policy">Политику конфиденциальности</router-link>.</li>
        </ul>

        <h2>5. Ответственность</h2>
        <ul>
          <li>Сервис предоставляется «как есть» без гарантий.</li>
          <li>Администрация не несёт ответственности за возможные сбои или потерю данных.</li>
        </ul>

        <h2>6. Связь с администрацией</h2>
        <ul>
          <li>По вопросам и предложениям пишите на <a href="mailto:support@kpitreading.ru">support@kpitreading.ru</a>.</li>
        </ul>

        <p class="mt-4 text-secondary">Последнее обновление: {{ new Date().toLocaleDateString('ru-RU') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.terms-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  padding-top: var(--header-height, 60px);
  color: #fff;
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
}

.policy-content {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(168, 230, 207, 0.1);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
}

.policy-content h1, .policy-content h2 {
  color: #a8e6cf;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.policy-content h1:first-child {
  margin-top: 0;
}

.policy-content p {
  margin-bottom: 1rem;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
}

.policy-content ul {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.policy-content li {
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.8);
}

.policy-content strong {
  color: #a8e6cf;
}

.policy-content a {
  color: #a8e6cf;
  text-decoration: none;
  transition: color 0.3s ease;
}

.policy-content a:hover {
  color: #8cd3b0;
  text-decoration: underline;
}
</style> 