import asyncio
from django.core.management.base import BaseCommand
from prisma import Prisma
import json

class Command(BaseCommand):
    help = 'Seeds the database with initial achievements'

    def handle(self, *args, **options):
        async def seed_data():
            prisma = Prisma()
            await prisma.connect()

            achievements_to_create = [
                {
                    "name": "Первый голос",
                    "description": "Проголосуйте за книгу недели в первый раз.",
                    "type": "voting",
                    "criteria": {"min_votes": 1},
                    "reward": 10
                },
                {
                    "name": "Активный избиратель",
                    "description": "Проголосуйте за книгу недели 5 раз.",
                    "type": "voting",
                    "criteria": {"min_votes": 5},
                    "reward": 50
                },
                {
                    "name": "Ветеран голосования",
                    "description": "Проголосуйте за книгу недели 10 раз.",
                    "type": "voting",
                    "criteria": {"min_votes": 10},
                    "reward": 100
                },
            ]

            for achievement_data in achievements_to_create:
                existing_achievement = await prisma.achievement.find_first(
                    where={'name': achievement_data['name']}
                )
                if not existing_achievement:
                    await prisma.achievement.create(
                        data={
                            "name": achievement_data['name'],
                            "description": achievement_data['description'],
                            "type": achievement_data['type'],
                            "criteria": json.dumps(achievement_data['criteria']),
                            "reward": achievement_data['reward']
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"Successfully added achievement: {achievement_data['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Achievement already exists: {achievement_data['name']}"))

            await prisma.disconnect()

        asyncio.run(seed_data())