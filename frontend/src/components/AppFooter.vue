<template>
  <footer class="footer">
    <div class="footer-top">
      <div class="container">
        <div class="row g-4">
          <div class="col-lg-4">
            <div class="footer-info">
              <RouterLink to="/" class="footer-logo">
                <i class="bi bi-book-half"></i>
                KpitReading
              </RouterLink>
              <p class="mt-3">Ваш персональный помощник в мире литературы. Откройте для себя новые книги, присоединяйтесь к сообществу читателей и развивайтесь вместе с нами.</p>
              <div class="social-links mt-4">
                <a href="mailto:alexankochergin@yandex.ru" class="social-link" title="Email">
                  <svg viewBox="0 0 512 512" width="1.2em" height="1.2em" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
                    <g fill="none" fill-rule="evenodd">
                      <path fill="#ffda3e" d="M56 402.667h400V109.333H56z"/>
                      <path fill="#fc0" d="M256 182.667l-200 220h400z"/>
                      <path d="M456 109.333L276.848 284.116c-11.675 11.4-30.02 11.4-41.696 0L56 109.333h400z" fill="#f33"/>
                    </g>
                  </svg>
                </a>
                <a href="https://t.me/zhizn_sani" class="social-link" target="_blank" rel="noopener" title="Telegram">
                  <svg width="1.2em" height="1.2em" viewBox="0 0 1000 1000" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
                    <defs>
                      <linearGradient x1="50%" y1="0%" x2="50%" y2="99.2583404%" id="tg-gradient">
                        <stop stop-color="#2AABEE" offset="0%"></stop>
                        <stop stop-color="#229ED9" offset="100%"></stop>
                      </linearGradient>
                    </defs>
                    <circle fill="url(#tg-gradient)" cx="500" cy="500" r="500"></circle>
                    <path d="M226.328419,494.722069 C372.088573,431.216685 469.284839,389.350049 517.917216,369.122161 C656.772535,311.36743 685.625481,301.334815 704.431427,301.003532 C708.567621,300.93067 717.815839,301.955743 723.806446,306.816707 C728.864797,310.92121 730.256552,316.46581 730.922551,320.357329 C731.588551,324.248848 732.417879,333.113828 731.758626,340.040666 C724.234007,419.102486 691.675104,610.964674 675.110982,699.515267 C668.10208,736.984342 654.301336,749.547532 640.940618,750.777006 C611.904684,753.448938 589.856115,731.588035 561.733393,713.153237 C517.726886,684.306416 492.866009,666.349181 450.150074,638.200013 C400.78442,605.66878 432.786119,587.789048 460.919462,558.568563 C468.282091,550.921423 596.21508,434.556479 598.691227,424.000355 C599.00091,422.680135 599.288312,417.758981 596.36474,415.160431 C593.441168,412.561881 589.126229,413.450484 586.012448,414.157198 C581.598758,415.158943 511.297793,461.625274 375.109553,553.556189 C355.154858,567.258623 337.080515,573.934908 320.886524,573.585046 C303.033948,573.199351 268.692754,563.490928 243.163606,555.192408 C211.851067,545.013936 186.964484,539.632504 189.131547,522.346309 C190.260287,513.342589 202.659244,504.134509 226.328419,494.722069 Z" fill="#FFFFFF"></path>
                  </svg>
                </a>
                <a href="https://vk.com/problempro12" class="social-link" target="_blank" rel="noopener" title="VK">
                  <svg width="1.2em" height="1.2em" viewBox="0 0 101 100" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle;">
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
          
          <div class="col-lg-2 col-md-4">
            <div class="footer-links">
              <h4>Навигация</h4>
              <ul>
                <li><RouterLink to="/">Главная</RouterLink></li>
                <li><RouterLink to="/books">Каталог</RouterLink></li>
                <li><RouterLink to="/profile">Профиль</RouterLink></li>
                <li><RouterLink to="/achievements">Достижения</RouterLink></li>
              </ul>
            </div>
          </div>
          
          <div class="col-lg-2 col-md-4">
            <div class="footer-links">
              <h4>Категории</h4>
              <ul>
                <li><RouterLink to="/app/books?category=classic">Классика</RouterLink></li>
                <li><RouterLink to="/app/books?category=fantasy">Фэнтези</RouterLink></li>
                <li><RouterLink to="/app/books?category=sci-fi">Научная фантастика</RouterLink></li>
                <li><RouterLink to="/app/books?category=detective">Детективы</RouterLink></li>
              </ul>
            </div>
          </div>
          
          <div class="col-lg-4 col-md-4">
            <div class="footer-newsletter">
              <h4>Подпишитесь на новости</h4>
              <p>Будьте в курсе новых книг и событий</p>
              <form class="newsletter-form">
                <input type="email" placeholder="Ваш email" class="form-control">
                <button type="submit" class="btn btn-primary">
                  <i class="bi bi-send"></i>
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="footer-bottom">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-md-6">
            <p class="mb-0">&copy; 2025 KpitReading. Все права защищены.</p>
          </div>
          <div class="col-md-6">
            <div class="footer-bottom-links">
              <RouterLink to="/privacy-policy">Политика конфиденциальности</RouterLink>
              <RouterLink to="/terms">Условия пользования</RouterLink>
              <RouterLink to="/contact">Контакты</RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.footer {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c3e50 100%);
  color: #fff;
  position: relative;
}

.footer::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(168, 230, 207, 0.3), transparent);
}

.footer-top {
  padding: 5rem 0 3rem;
}

.footer-logo {
  font-size: 1.8rem;
  font-weight: 700;
  color: #fff;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.footer-logo i {
  color: #a8e6cf;
}

.footer-info p {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  text-decoration: none;
  transition: all 0.3s ease;
}

.social-link:hover {
  background: #a8e6cf;
  color: #2c3e50;
  transform: translateY(-3px);
}

.footer-links h4 {
  color: #fff;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  position: relative;
}

.footer-links h4::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -0.5rem;
  width: 30px;
  height: 2px;
  background: #a8e6cf;
}

.footer-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links ul li {
  margin-bottom: 0.8rem;
}

.footer-links ul li a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-block;
}

.footer-links ul li a:hover {
  color: #a8e6cf;
  transform: translateX(5px);
}

.footer-newsletter h4 {
  color: #fff;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.footer-newsletter p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 1.5rem;
}

.newsletter-form {
  display: flex;
  gap: 0.5rem;
}

.newsletter-form input {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 20px;
  padding: 0.8rem 1.5rem;
  color: #fff;
  flex: 1;
}

.newsletter-form input:focus {
  background: rgba(255, 255, 255, 0.15);
  outline: none;
  box-shadow: none;
}

.newsletter-form input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.newsletter-form button {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #a8e6cf;
  border: none;
  color: #2c3e50;
  transition: all 0.3s ease;
}

.newsletter-form button:hover {
  background: #8cd3b0;
  transform: translateY(-2px);
}

.footer-bottom {
  padding: 1.5rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  color: rgba(255, 255, 255, 0.7);
}

.footer-bottom-links {
  display: flex;
  justify-content: flex-end;
  gap: 1.5rem;
}

.footer-bottom-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s ease;
}

.footer-bottom-links a:hover {
  color: #a8e6cf;
}

@media (max-width: 991px) {
  .footer-top {
    padding: 3rem 0 2rem;
  }
  
  .footer-info {
    margin-bottom: 2rem;
  }
  
  .footer-links {
    margin-bottom: 2rem;
  }
  
  .footer-bottom-links {
    justify-content: center;
    margin-top: 1rem;
  }
}

@media (max-width: 767px) {
  .footer-bottom {
    text-align: center;
  }
  
  .footer-bottom p {
    margin-bottom: 1rem;
  }
  
  .footer-bottom-links {
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
  }
}
</style> 