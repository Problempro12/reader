from rest_framework import generics, permissions
from prisma import Prisma
from asgiref.sync import async_to_sync
from rest_framework import serializers

class AchievementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    type = serializers.CharField()
    criteria = serializers.JSONField()
    reward = serializers.IntegerField()

class UserAchievementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    achievedAt = serializers.DateTimeField(source='achievedAt')
    achievement = AchievementSerializer(source='achievement')

class AchievementListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AchievementSerializer

    def get_queryset(self):
        async def get_achievements():
            prisma = Prisma()
            await prisma.connect()
            achievements = await prisma.achievement.find_many()
            await prisma.disconnect()
            return achievements
        return async_to_sync(get_achievements())

class UserAchievementListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserAchievementSerializer

    def get_queryset(self):
        user = self.request.user
        async def get_user_achievements():
            prisma = Prisma()
            await prisma.connect()
            user_achievements = await prisma.userachievement.find_many(
                where={'userId': user.id},
                include={'achievement': True}
            )
            await prisma.disconnect()
            return user_achievements
        return async_to_sync(get_user_achievements()) 