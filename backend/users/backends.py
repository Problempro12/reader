from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.utils import ProgrammingError
from django.db import connections
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"[EmailBackend] Попытка аутентификации для email: {email}")
        
        # Очищаем кеш подключений
        for conn in connections.all():
            conn.close_if_unusable_or_obsolete()
        print("[EmailBackend] Кеш подключений очищен.")

        if email is None or password is None:
            print("[EmailBackend] Email или пароль не указаны")
            return None

        try:
            print(f"[EmailBackend] Ищем пользователя с email: {email}")
            user = User.objects.get(email=email)
            print(f"[EmailBackend] Пользователь найден: {user.email}")
            
            if user.check_password(password):
                print("[EmailBackend] Проверка пароля успешна")
                return user
            else:
                print("[EmailBackend] Неверный пароль")
                return None
                
        except User.DoesNotExist:
            print(f"[EmailBackend] Пользователь с email '{email}' не найден")
            return None
            
        except ProgrammingError as e:
            print(f"[EmailBackend] Ошибка базы данных: {str(e)}")
            # Пробрасываем ошибку дальше, чтобы Django мог её обработать
            raise ImproperlyConfigured(f"Ошибка базы данных: {str(e)}")
            
        except Exception as e:
            print(f"[EmailBackend] Неожиданная ошибка: {str(e)}")
            raise

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 