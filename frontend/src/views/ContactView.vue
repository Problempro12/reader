<template>
  <div class="contacts-page position-relative">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-lg-8">
          <div class="contact-hero text-center mb-5 fade-in">
            <div class="contact-avatar mx-auto mb-3">
              <i class="bi bi-person-circle"></i>
            </div>
            <h1 class="display-5 fw-bold text-gradient mb-2">Связаться с нами</h1>
            <p class="lead text-light-50 mb-0">Мы всегда рады обратной связи, предложениям и новым знакомствам!</p>
          </div>

          <div class="contact-card p-4 mb-4 fade-in" style="border-image: linear-gradient(90deg, #a8e6cf 0%, #8cd3b0 100%) 1; border-width: 2px; border-style: solid;">
            <div class="row align-items-center">
              <div class="col-md-3 text-center mb-3 mb-md-0">
                <div class="contact-icon bg-accent text-white mx-auto">
                  <i class="bi bi-envelope-at"></i>
                </div>
              </div>
              <div class="col-md-9">
                <h2 class="h4 fw-bold mb-2 text-accent">Электронная почта</h2>
                <p class="mb-2">Пишите по любым вопросам, предложениям и сотрудничеству:</p>
                <a :href="'mailto:alexankochergin@yandex.ru'" class="btn btn-accent btn-lg px-4 py-2" data-bs-toggle="tooltip" title="Написать на почту">
                  <i class="bi bi-send me-2"></i>alexankochergin@yandex.ru
                </a>
              </div>
            </div>
          </div>

          <div class="section-divider my-4 fade-in"><span>О проекте</span></div>
          <div class="about-project mb-4 fade-in">
            <p>
              <strong>KpitReading</strong> — это итоговый проект студента группы <strong>Python411</strong> компьютерной академии «ТОП» города Кирова.
            </p>
            <p>
              Автор проекта: <strong>Кочергин Александр Сергеевич</strong>.
            </p>
            <p>
              Мы стремимся сделать чтение книг удобным, современным и вдохновляющим для каждого пользователя. Проект развивается с любовью к книгам и технологиям.
            </p>
          </div>

          <div class="section-divider my-4 fade-in"><span>Обратная связь</span></div>
          <div class="feedback-block mb-4 fade-in">
            <ul>
              <li>Открыты к вашим идеям, отзывам и предложениям.</li>
              <li>Пишите, если нашли ошибку или хотите предложить новую функцию.</li>
              <li>Ваше мнение помогает нам становиться лучше!</li>
            </ul>
          </div>

          <div class="section-divider my-4 fade-in"><span>Социальные сети</span></div>
          <div class="social-block mb-4 text-center fade-in">
            <p class="mb-2">Пишите нам в удобный мессенджер или соцсеть — мы обязательно ответим!</p>
            <div class="d-flex justify-content-center gap-3">
              <a href="mailto:alexankochergin@yandex.ru" class="social-icon bg-accent text-white" title="Email" data-bs-toggle="tooltip"><i class="bi bi-envelope"></i></a>
              <a href="https://t.me/zhizn_sani" target="_blank" rel="noopener" class="social-icon bg-telegram text-white" title="Telegram" data-bs-toggle="tooltip"><i class="bi bi-telegram"></i></a>
              <a href="https://vk.com/problempro12" target="_blank" rel="noopener" class="social-icon bg-vk text-white" title="VK" data-bs-toggle="tooltip">
                <!-- SVG VK (ваш вариант, фон #4c75a3) -->
                <svg width="1.5em" height="1.5em" viewBox="0 0 101 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <g clip-path="url(#clip0_2_40)">
                    <path d="M0.5 48C0.5 25.3726 0.5 14.0589 7.52944 7.02944C14.5589 0 25.8726 0 48.5 0H52.5C75.1274 0 86.4411 0 93.4706 7.02944C100.5 14.0589 100.5 25.3726 100.5 48V52C100.5 74.6274 100.5 85.9411 93.4706 92.9706C86.4411 100 75.1274 100 52.5 100H48.5C25.8726 100 14.5589 100 7.52944 92.9706C0.5 85.9411 0.5 74.6274 0.5 52V48Z" fill="#4c75a3"/>
                    <path d="M53.7085 72.042C30.9168 72.042 17.9169 56.417 17.3752 30.417H28.7919C29.1669 49.5003 37.5834 57.5836 44.25 59.2503V30.417H55.0004V46.8752C61.5837 46.1669 68.4995 38.667 70.8329 30.417H81.5832C79.7915 40.5837 72.2915 48.0836 66.9582 51.1669C72.2915 53.6669 80.8336 60.2086 84.0836 72.042H72.2499C69.7082 64.1253 63.3754 58.0003 55.0004 57.1669V72.042H53.7085Z" fill="white"/>
                  </g>
                  <defs>
                    <clipPath id="clip0_2_40">
                      <rect width="100" height="100" fill="white" transform="translate(0.5)"/>
                    </clipPath>
                  </defs>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';

onMounted(() => {
  // Инициализация Bootstrap tooltips
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(el => {
    // @ts-ignore
    new window.bootstrap.Tooltip(el);
  });
});
</script>

<style scoped>
.contacts-page {
  min-height: calc(100vh - var(--header-height, 60px) - var(--footer-height, 60px));
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  color: #fff;
  position: relative;
  overflow-x: hidden;
}

.container, .row, .col-lg-8 {
  position: relative;
  z-index: 1;
}

.text-gradient {
  background: linear-gradient(45deg, #a8e6cf, #fff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-accent {
  color: #a8e6cf !important;
}

.bg-accent {
  background: #a8e6cf !important;
}

.bg-telegram {
  background: #229ED9 !important;
}

.bg-vk {
  background: #4C75A3 !important;
}

.btn-accent {
  background: #a8e6cf;
  color: #2c3e50;
  border: none;
  transition: background 0.2s;
}
.btn-accent:hover {
  background: #8cd3b0;
  color: #2c3e50;
}

.text-light-50 {
  color: rgba(255,255,255,0.7);
}

.contact-hero {
  margin-top: 2rem;
}
.contact-avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: #a8e6cf;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  color: #2c3e50;
  box-shadow: 0 4px 24px rgba(168, 230, 207, 0.2);
}

.contact-card {
  background: rgba(255,255,255,0.10);
  border-radius: 18px;
  box-shadow: 0 6px 32px rgba(168, 230, 207, 0.10);
  border: 1px solid rgba(168, 230, 207, 0.15);
  margin-bottom: 2rem;
  border-image: linear-gradient(90deg, #a8e6cf 0%, #8cd3b0 100%) 1;
  border-width: 2px;
  border-style: solid;
}

.contact-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.2rem;
  margin: 0 auto 0.5rem auto;
  box-shadow: 0 2px 12px rgba(168, 230, 207, 0.15);
  background: #a8e6cf;
}

.contact-icon.bg-accent i {
  color: #2c3e50 !important;
}

.section-divider {
  text-align: center;
  position: relative;
  margin: 2.5rem 0 1.5rem 0;
}
.section-divider span {
  background: rgba(44,62,80,0.95);
  padding: 0 1.2rem;
  color: #a8e6cf;
  font-weight: 600;
  position: relative;
  z-index: 1;
  border-radius: 8px;
  font-size: 1.1rem;
}
.section-divider:before {
  content: '';
  position: absolute;
  left: 0; right: 0; top: 50%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #a8e6cf 40%, #a8e6cf 60%, transparent);
  z-index: 0;
}

.feedback-block ul, .about-project ul {
  padding-left: 1.5rem;
}
.feedback-block li, .about-project li {
  margin-bottom: 0.5rem;
  color: rgba(255,255,255,0.85);
}

.social-block .social-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  background: rgba(255,255,255,0.10);
  color: #fff;
  transition: background 0.2s, color 0.2s, transform 0.2s;
  box-shadow: 0 2px 8px rgba(168, 230, 207, 0.10);
  position: relative;
}
.social-block .social-icon:hover:not(.disabled) {
  filter: brightness(1.15) contrast(1.1);
  color: #fff;
  transform: translateY(-3px) scale(1.08);
  opacity: 0.95;
}
.social-block .bg-telegram:hover {
  background: #37b4ec !important;
}
.social-block .bg-vk:hover {
  background: #5b87b7 !important;
}
.social-block .bg-accent:hover {
  background: #8cd3b0 !important;
  color: #2c3e50 !important;
}
.social-block .social-icon.disabled {
  opacity: 0.4;
  pointer-events: none;
}

.social-icon.bg-accent i {
  color: #252d37 !important;
}

.fade-in {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeInUp 0.8s cubic-bezier(.23,1.01,.32,1) forwards;
}
.fade-in:nth-child(1) { animation-delay: 0.1s; }
.fade-in:nth-child(2) { animation-delay: 0.2s; }
.fade-in:nth-child(3) { animation-delay: 0.3s; }
.fade-in:nth-child(4) { animation-delay: 0.4s; }
.fade-in:nth-child(5) { animation-delay: 0.5s; }
.fade-in:nth-child(6) { animation-delay: 0.6s; }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: none;
  }
}

.blockquote {
  border-left: 4px solid #a8e6cf;
  padding-left: 1rem;
  font-size: 1.15rem;
  font-style: italic;
  color: #a8e6cf;
  background: rgba(168, 230, 207, 0.05);
  margin-bottom: 1.5rem;
}

@media (max-width: 768px) {
  .contact-card, .policy-content {
    padding: 1rem;
  }
  .contact-avatar {
    width: 64px;
    height: 64px;
    font-size: 2rem;
  }
}
</style> 