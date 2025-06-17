import os
import django
import sys
from pathlib import Path
from asgiref.sync import sync_to_async

# Добавляем путь к корню проекта
sys.path.append(str(Path(__file__).parent.parent))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User  # Используем кастомную модель пользователя
from prisma import Prisma
import asyncio
from datetime import datetime

async def migrate_users(prisma: Prisma):
    """Миграция пользователей из Django в Prisma"""
    django_users = await sync_to_async(list)(User.objects.all())
    
    for user in django_users:
        await prisma.user.create(
            data={
                'email': user.email,
                'username': user.username,
                'passwordHash': user.password,  # Django уже хранит хеш
                'isPremium': False,  # По умолчанию
                'hideAds': False,    # По умолчанию
                'createdAt': user.date_joined,
                'updatedAt': user.date_joined,
                'registrationDate': user.date_joined,
                'isActive': user.is_active,
                'isStaff': user.is_staff,
                'isSuperuser': user.is_superuser,
                'lastLogin': user.last_login,
            }
        )
    print(f"Migrated {len(django_users)} users")

async def migrate_groups(prisma: Prisma):
    """Миграция групп из Django в Prisma"""
    django_groups = await sync_to_async(list)(Group.objects.all())
    
    for group in django_groups:
        await prisma.group.create(
            data={
                'name': group.name,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
        )
    print(f"Migrated {len(django_groups)} groups")

async def migrate_permissions(prisma: Prisma):
    """Миграция разрешений из Django в Prisma"""
    django_permissions = await sync_to_async(list)(Permission.objects.all())
    
    for perm in django_permissions:
        await prisma.permission.create(
            data={
                'name': perm.name,
                'codename': perm.codename,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now(),
            }
        )
    print(f"Migrated {len(django_permissions)} permissions")

async def migrate_user_groups(prisma: Prisma):
    """Миграция связей пользователей с группами"""
    django_users = await sync_to_async(list)(User.objects.all())
    
    for user in django_users:
        groups = await sync_to_async(list)(user.groups.all())
        for group in groups:
            await prisma.usergroup.create(
                data={
                    'userId': user.id,
                    'groupId': group.id,
                    'createdAt': datetime.now(),
                }
            )
    print("Migrated user groups")

async def migrate_user_permissions(prisma: Prisma):
    """Миграция разрешений пользователей"""
    django_users = await sync_to_async(list)(User.objects.all())
    
    for user in django_users:
        perms = await sync_to_async(list)(user.user_permissions.all())
        for perm in perms:
            await prisma.userpermission.create(
                data={
                    'userId': user.id,
                    'permissionId': perm.id,
                    'createdAt': datetime.now(),
                }
            )
    print("Migrated user permissions")

async def migrate_group_permissions(prisma: Prisma):
    """Миграция разрешений групп"""
    django_groups = await sync_to_async(list)(Group.objects.all())
    
    for group in django_groups:
        perms = await sync_to_async(list)(group.permissions.all())
        for perm in perms:
            await prisma.grouppermission.create(
                data={
                    'groupId': group.id,
                    'permissionId': perm.id,
                    'createdAt': datetime.now(),
                }
            )
    print("Migrated group permissions")

async def main():
    prisma = Prisma()
    await prisma.connect()
    
    try:
        print("Starting migration...")
        
        # Миграция в правильном порядке
        await migrate_permissions(prisma)
        await migrate_groups(prisma)
        await migrate_users(prisma)
        await migrate_user_groups(prisma)
        await migrate_user_permissions(prisma)
        await migrate_group_permissions(prisma)
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 