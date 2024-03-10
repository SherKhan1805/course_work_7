from datetime import datetime

import requests
from rest_framework import generics

from config.settings import TELEGRAM_BOT_API_TOKEN
from habits.models import Habit
from habits.paginators import HabitsPagination
from rest_framework.permissions import IsAuthenticated, AllowAny

from habits.permissions import IsAuthorHabit, IsModer
from habits.serializers import HabitSerializer, HabitPublicUsefulListSerializer, HabitPublicPleasantListSerializer
from habits.services import calculate_next_notification_time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class HabitCreateAPIView(generics.CreateAPIView):
    """
    Создание привычки
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer]
    # permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Установка пользователя перед сохранением
        serializer.save(user=self.request.user)

        # Получение ID созданной привычки
        habit_id = serializer.instance.id
        print(habit_id)
        habit = Habit.objects.get(id=habit_id)
        # Установка даты и времени создания привычки
        time = habit.time
        periodicity = habit.periodicity
        notification_time = datetime.utcnow()

        next_notification_time = calculate_next_notification_time(time, periodicity, notification_time)
        print(next_notification_time)

        habit.notification_time = next_notification_time
        habit.save()
        print(type(habit.notification_time))
        # Или можно получить ID привычки из сохраненного объекта
        # habit_id = serializer.data.get('id')


class HabitListAPIView(generics.ListAPIView):
    """
    Просмотр списка привычек
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)


class HabitUsefulListAPIView(generics.ListAPIView):
    """
    Просмотр списка полезных публичных привычек
    """
    serializer_class = HabitPublicUsefulListSerializer
    queryset = Habit.objects.filter(pleasant_habit=False)
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]


class HabitPleasantListAPIView(generics.ListAPIView):
    """
    Просмотр списка приятных публичных привычек
    """
    serializer_class = HabitPublicPleasantListSerializer
    queryset = Habit.objects.filter(pleasant_habit=True)
    pagination_class = HabitsPagination
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    """
    Просмотр привычки
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorHabit | IsModer]
    # permission_classes = [AllowAny]


class HabitDeleteAPIView(generics.DestroyAPIView):
    """
    Удаление привычки
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorHabit]
    # permission_classes = [AllowAny]


class HabitUpdateAPIView(generics.UpdateAPIView):
    """
    Изменение привычки
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorHabit | IsModer]
    # permission_classes = [AllowAny]


class GetChatId(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def get(self, request):
        global telegram_user_id
        bot_token = TELEGRAM_BOT_API_TOKEN
        url = f'https://api.telegram.org/bot{bot_token}/getUpdates'

        user_id = request.user.id

        try:
            response = requests.get(url)
            response_data = response.json()
            results_data = response_data['result']
            for result in results_data:
                telegram_user_first_name = result['message']['chat']['first_name']
                telegram_user_id = result['message']['chat']['id']
                error_last_name = result['message']['chat']
                if error_last_name.get('last_name'):
                    telegram_user_last_name = result['message']['chat']['last_name']
                    print(f'{telegram_user_first_name} {telegram_user_last_name} - id: {telegram_user_id}')
                    habits = Habit.objects.filter(user=user_id).all()
                    for habit in habits:
                        habit.telegram_chat_id = telegram_user_id
                        print(habit.telegram_chat_id)
                        habit.save()
                else:
                    print(f'{telegram_user_first_name} last_name "not found" - id: {telegram_user_id}')



            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
