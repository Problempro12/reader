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
                <a href="#" class="social-link"><i class="bi bi-facebook"></i></a>
                <a href="#" class="social-link"><i class="bi bi-twitter"></i></a>
                <a href="#" class="social-link"><i class="bi bi-instagram"></i></a>
                <a href="#" class="social-link"><i class="bi bi-telegram"></i></a>
              </div>
            </div>
          </div>
          
          <div class="col-lg-2 col-md-4">
            <div class="footer-links">
              <h4>Навигация</h4>
              <ul>
                <li><RouterLink to="/">Главная</RouterLink></li>
                <li><RouterLink to="/app/books">Книги</RouterLink></li>
                <li><RouterLink to="/app/profile">Профиль</RouterLink></li>
                <li><RouterLink to="/app/achievements">Достижения</RouterLink></li>
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
              <RouterLink to="/privacy">Политика конфиденциальности</RouterLink>
              <RouterLink to="/terms">Условия использования</RouterLink>
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