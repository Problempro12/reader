from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from prisma import Prisma
import logging
import asyncio
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)
User = get_user_model()

async def sync_user_async(user, is_created=False):
    """Асинхронная синхронизация пользователя"""
    prisma = Prisma()
    await prisma.connect()
    
    try:
        if is_created:
            await prisma.user.create(
                data={
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'passwordHash': user.password,
                    'isPremium': False,
                    'hideAds': False
                }
            )
        else:
            await prisma.user.update(
                where={'id': user.id},
                data={
                    'email': user.email,
                    'username': user.username,
                    'passwordHash': user.password
                }
            )
    finally:
        await prisma.disconnect()

@receiver(post_save, sender=User)
def sync_user_to_prisma(sender, instance, created, **kwargs):
    """Синхронизирует пользователя Django с Prisma"""
    logger.info(f"Начинаем синхронизацию пользователя {instance.username}")
    asyncio.run(sync_user_async(instance, created))

async def sync_all_users_async():
    """Асинхронная синхронизация всех пользователей"""
    logger.info("Начинаем синхронизацию всех пользователей")
    prisma = Prisma()
    await prisma.connect()
    
    try:
        django_users = await sync_to_async(list)(User.objects.all())
        logger.info(f"Найдено пользователей в Django: {len(django_users)}")
        
        for user in django_users:
            try:
                logger.info(f"Синхронизируем пользователя: {user.username}")
                await prisma.user.create(
                    data={
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'passwordHash': user.password,
                        'isPremium': False,
                        'hideAds': False
                    }
                )
                logger.info(f"Пользователь {user.username} успешно синхронизирован")
            except Exception as e:
                logger.error(f"Ошибка при синхронизации пользователя {user.username}: {str(e)}")
                raise
    finally:
        await prisma.disconnect()

def sync_all_users():
    """Синхронизирует всех пользователей Django с Prisma"""
    asyncio.run(sync_all_users_async()) 