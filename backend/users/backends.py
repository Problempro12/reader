from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.utils import ProgrammingError
from django.db import connections

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"[EmailBackend] Попытка аутентификации для email: {email}")
        for conn in connections.all():
            conn.close_if_unusable_or_obsolete()
        print("[EmailBackend] Кеш подключений очищен.")

        try:
            print(f"[EmailBackend] Ищем пользователя с email: {email}")
            user = User.objects.get(email=email)
            print(f"[EmailBackend] Пользователь найден: {user.email}")
            print("[EmailBackend] Проверяем пароль...")
            if user.check_password(password):
                print("[EmailBackend] Проверка пароля успешна.")
                return user
            else:
                print("[EmailBackend] Проверка пароля не удалась.")
        except User.DoesNotExist:
            print(f"[EmailBackend] Пользователь с email '{email}' не найден.")
            return None
        except ProgrammingError as e:
            print(f"[EmailBackend] Ошибка базы данных (ProgrammingError) при поиске пользователя: {str(e)}")
            print(f"[EmailBackend] Тип ошибки: {type(e)}")
            return None # Или пробросить исключение, если нужно
        except Exception as e:
            print(f"[EmailBackend] Неожиданная ошибка при аутентификации: {str(e)}")
            print(f"[EmailBackend] Тип ошибки: {type(e)}")
            # Возможно, стоит пробросить исключение или вернуть None, в зависимости от желаемого поведения
            return None
        print("[EmailBackend] Аутентификация не удалась (общий возврат None).")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 