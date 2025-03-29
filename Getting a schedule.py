import requests
from datetime import datetime, timedelta


def get_booking_times(api_key, company_id, staff_id, date, user_id):
    url = f"https://api.yclients.com/api/v1/timetable/seances/{company_id}/{staff_id}/{date}"
    headers = {
        'Authorization': f'Bearer {api_key}, User {user_id}',  # Указываем API-ключ
        'Accept': 'application/vnd.api.v2+json',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()  # Возвращаем данные в формате JSON
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка при получении сеансов для staff_id {staff_id} на дату {date}: {http_err}")
        return None
    except Exception as err:
        print(f"Произошла ошибка: {err}")
        return None


def save_successful_responses(responses, file_name='successful_responses.txt'):
    with open(file_name, 'a') as file:
        for response in responses:
            file.write(f"{response['Name']}\n")
            file.write(f"{response['date']}\n")
            for i in response['times']:
                file.write(f"{i}\n")
            # Записываем ответы в файл


def check_availability(current_time, sheld):
    return sheld.get(current_time, False)


# Преобразование времени
def true_Time(appointments, duration, times):
    sheld = {}
    for y in times:
        sheld[y['time']] = f"{y['is_free']}" == 'True'
    results = []
    for appointment in appointments:
        start_time = datetime.strptime(appointment, "%H:%M")
        end_time = start_time + duration

        available = True
        while start_time < end_time:
            if not check_availability(start_time.strftime("%H:%M"), sheld):
                available = False
                break
            start_time += timedelta(minutes=5)

        results.append(f"{appointment};{available}")
    return results


def main():
    api_key = "cktwj7a8u5skf3bab393"  # Замените на ваш API-ключ
    company_id = "113848"
    user_id = "3b1268ae6fffb76cf2321db538ce02e8"  # Замените на идентификатор вашей организации
    staff_ids = [
        266185, 738955, 1959651, 1959169, 2072386,
        2853962, 1959172, 2072386, 1959176

    ]
    masters = {
        266185: 'Анастасия Горнева', 738955: 'Юлия Михайлюк',
        1959651: 'Татьяна Любцева', 1959169: 'Ксения Иванова',
        2072386: 'Дарья Мерзлякова', 2853962: 'Дарья Богданова',
        1959172: 'Светлана Гирина', 2072386: 'Дарья Мерзлякова',
        1959176: 'Мария Малышкина'
    }

    appointments = ['09:00', '11:00', '13:00', '15:00', '17:30', '19:30']
    duration = timedelta(hours=1, minutes=59)

    # Определяем диапазон дат
    today = datetime.now()
    start_date = today
    if today.day > 15:
        start_date = today.replace(day=16)
        end_date = (start_date + timedelta(days=30)).replace(day=15)
    else:
        end_date = today.replace(day=15)

    current_date = today

    successful_responses = []

    # Итерация по всем датам до 15 числа следующего месяца
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')  # Форматируем дату
        print(f"Проверка сеансов доступных для бронирования на {date_str}")

        for staff_id in staff_ids:
            booking_times = get_booking_times(api_key, company_id, staff_id, date_str, user_id)

            if booking_times is not None and len(booking_times['data']) != 0:
                print(f"Успешные сеансы для {masters[staff_id]} на {date_str}: {booking_times}")
                successful_responses.append({
                    'Name': masters[staff_id],
                    'date': date_str,
                    'times': true_Time(appointments, duration, booking_times['data'])
                })  # Добавляем успешный ответ
            else:
                print(f"Не удалось получить сеансы для staff_id {staff_id} на {date_str}")

        current_date += timedelta(days=1)  # Переход к следующей дате

    # Сохраняем успешные ответы в файл
    save_successful_responses(successful_responses)


if __name__ == "__main__":
    main()