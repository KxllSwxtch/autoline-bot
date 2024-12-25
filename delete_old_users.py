import psycopg2
from datetime import timedelta, date
from main import DATABASE_URL  # Импортируйте URL для подключения к базе данных


def delete_old_users():
    # Получаем текущую дату
    today = date.today()

    # Определяем последний пятничный день
    days_since_friday = today.weekday() - 4  # 4 — это пятница
    last_friday = today - timedelta(days=days_since_friday)

    # Определяем, до какой даты нужно удалять записи (7 дней назад)
    delete_before_date = last_friday - timedelta(days=7)

    # Подключаемся к базе данных
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cursor = conn.cursor()

    # Удаляем пользователей, зарегистрировавшихся до delete_before_date
    cursor.execute(
        """
        DELETE FROM user_stats
        WHERE join_date < %s
        """,
        (delete_before_date,),
    )
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    delete_old_users()
