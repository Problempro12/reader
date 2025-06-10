import os
from crontab import CronTab

def setup_cron():
    # Получаем текущего пользователя
    user = os.getenv('USER')
    cron = CronTab(user=user)

    # Путь к Python в виртуальном окружении
    python_path = os.path.join(os.getcwd(), 'venv', 'bin', 'python')
    
    # Путь к скрипту импорта книг
    import_script = os.path.join(os.getcwd(), 'scripts', 'import_books.py')
    
    # Создаем задачу для импорта книг (каждый день в 3:00)
    import_job = cron.new(command=f'{python_path} {import_script}')
    import_job.hour.on(3)
    import_job.minute.on(0)

    # Путь к скрипту определения победителя
    winner_script = os.path.join(os.getcwd(), 'manage.py')
    
    # Создаем задачу для определения победителя (каждый понедельник в 00:00)
    winner_job = cron.new(command=f'cd {os.getcwd()} && {python_path} {winner_script} determine_weekly_winner')
    winner_job.setall('0 0 * * 1')  # Каждый понедельник в 00:00

    # Сохраняем изменения
    cron.write()

if __name__ == '__main__':
    setup_cron() 