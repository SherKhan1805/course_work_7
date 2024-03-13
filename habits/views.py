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


class AddHabitToUserAPIView(generics.CreateAPIView):
    """
    Контроллер добавления публичной привычки
    к пользователю
    """
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            # Получаем данные из запроса
            habit_id = request.data.get('habit_id')
            # Получаем пользователя из запроса
            user = request.user
            # Получаем публичную привычку по идентификатору
            public_habit = Habit.objects.get(id=habit_id)

            habit_values = public_habit.__dict__.copy()
            # Удаляем _state атрибут
            del habit_values['_state']
            # Удаляем 'id' из значений атрибутов,
            # чтобы не возникала конфликт с уже существующими объектами
            del habit_values['id']

            # Создаем новый объект Habit,
            # передавая значения атрибутов public_habit
            habit = Habit.objects.create(user=user, **habit_values)

            # Установка даты и времени привычки
            time = habit.time
            periodicity = habit.periodicity
            notification_time = datetime.utcnow()

            next_no_time = calculate_next_notification_time(
                time, periodicity, notification_time)

            habit.notification_time = next_no_time

            # Сохраняем привычку пользователю
            habit.save()

            # Сериализуем созданную привычку и возвращаем в ответе
            serializer = self.get_serializer(habit)

            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        except Habit.DoesNotExist:
            return Response({"error": "Публичная привычка не найдена."},
                            status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

