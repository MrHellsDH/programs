import json
import datetime
import os
import csv
import time


class TaskManager:
    def __init__(self, filename="tasks.json"):
        self.filename = filename
        self.tasks = self.load_tasks()
        self.history = []  # Stack to store actions for undo

    def load_tasks(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.tasks, file, ensure_ascii=False, indent=4)

    def add_task(self, title, category, priority, due_date, description=""):
        task = {
            "title": title,
            "category": category,
            "priority": priority,
            "due_date": due_date,
            "description": description,
            "created_at": str(datetime.datetime.now()),
            "completed": False,
            "reminder": None
        }
        self.tasks.append(task)
        self.save_tasks()
        self.history.append(('add', task))  # Save history for undo
        print("Задача добавлена!")

    def remove_task(self, title):
        task_to_remove = None
        for task in self.tasks:
            if task["title"] == title:
                task_to_remove = task
                break

        if task_to_remove:
            self.tasks = [task for task in self.tasks if task["title"] != title]
            self.save_tasks()
            self.history.append(('remove', task_to_remove))  # Save history for undo
            print("Задача удалена!")
        else:
            print("Задача не найдена!")

    def edit_task(self, title, new_title=None, new_category=None, new_priority=None, new_due_date=None,
                  new_description=None):
        for task in self.tasks:
            if task["title"] == title:
                old_task = task.copy()
                if new_title:
                    task["title"] = new_title
                if new_category:
                    task["category"] = new_category
                if new_priority:
                    task["priority"] = new_priority
                if new_due_date:
                    task["due_date"] = new_due_date
                if new_description:
                    task["description"] = new_description
                self.save_tasks()
                self.history.append(('edit', old_task, task))  # Save history for undo
                print("Задача обновлена!")
                return
        print("Задача не найдена!")

    def list_tasks(self):
        if not self.tasks:
            print("Нет задач.")
            return
        for task in self.tasks:
            print(
                f"Название: {task['title']}, Категория: {task['category']}, Приоритет: {task['priority']}, Срок: {task['due_date']}, Завершена: {task['completed']}, Описание: {task['description']}")

    def mark_completed(self, title):
        for task in self.tasks:
            if task["title"] == title:
                task["completed"] = True
                self.save_tasks()
                self.history.append(('mark_completed', task))  # Save history for undo
                print("Задача выполнена!")
                return
        print("Задача не найдена!")

    def export_to_csv(self, filename="tasks.csv"):
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Название", "Категория", "Приоритет", "Срок", "Завершена", "Описание"])
            for task in self.tasks:
                writer.writerow([task["title"], task["category"], task["priority"], task["due_date"], task["completed"],
                                 task["description"]])
        print("Задачи экспортированы в CSV!")

    def clear_completed_tasks(self):
        self.tasks = [task for task in self.tasks if not task["completed"]]
        self.save_tasks()
        print("Все выполненные задачи удалены!")

    def show_statistics(self):
        total = len(self.tasks)
        completed = len([task for task in self.tasks if task["completed"]])
        pending = total - completed
        print(f"Всего задач: {total}\nВыполнено: {completed}\nОсталось: {pending}")

    def search_tasks(self, keyword):
        result = [task for task in self.tasks if keyword.lower() in task["title"].lower() or keyword.lower() in task["category"].lower()]
        if result:
            for task in result:
                print(
                    f"Название: {task['title']}, Категория: {task['category']}, Приоритет: {task['priority']}, Срок: {task['due_date']}, Завершена: {task['completed']}, Описание: {task['description']}")
        else:
            print("Задачи не найдены.")

    def set_reminder(self, title, reminder_time):
        for task in self.tasks:
            if task["title"] == title:
                task["reminder"] = reminder_time
                self.save_tasks()
                print(f"Напоминание установлено на {reminder_time} для задачи {title}")
                return
        print("Задача не найдена!")

    def check_reminders(self):
        current_time = datetime.datetime.now()
        for task in self.tasks:
            if task["reminder"] and datetime.datetime.strptime(task["reminder"], "%Y-%m-%d %H:%M:%S") <= current_time:
                print(f"Напоминание для задачи '{task['title']}': {task['reminder']}")

    def sort_tasks(self, by="priority"):
        if by == "priority":
            self.tasks.sort(key=lambda task: task["priority"])
        elif by == "due_date":
            self.tasks.sort(key=lambda task: task["due_date"])
        self.save_tasks()
        print(f"Задачи отсортированы по {by}.")

    def filter_tasks(self, completed=None):
        if completed is None:
            return self.tasks
        return [task for task in self.tasks if task["completed"] == completed]

    def undo_last_action(self):
        if not self.history:
            print("Нет действия для отмены.")
            return

        last_action = self.history.pop()
        if last_action[0] == "add":
            self.tasks.remove(last_action[1])
        elif last_action[0] == "remove":
            self.tasks.append(last_action[1])
        elif last_action[0] == "edit":
            old_task = last_action[1]
            new_task = last_action[2]
            self.tasks = [old_task if task == new_task else task for task in self.tasks]
        elif last_action[0] == "mark_completed":
            task = last_action[1]
            task["completed"] = False
        self.save_tasks()
        print("Последнее действие отменено.")

    def task_deadline_alert(self):
        current_time = datetime.datetime.now()
        for task in self.tasks:
            due_date = datetime.datetime.strptime(task["due_date"], "%Y-%m-%d")
            if due_date - current_time <= datetime.timedelta(days=1):
                print(f"Задача '{task['title']}' скоро истечет! Срок: {task['due_date']}.")


if __name__ == "__main__":
    manager = TaskManager()
    while True:
        print(
            "\n1. Добавить задачу\n2. Удалить задачу\n3. Редактировать задачу\n4. Список задач\n5. Отметить выполненной\n6. Очистить выполненные\n7. Экспорт в CSV\n8. Показать статистику\n9. Поиск задач\n10. Установить напоминание\n11. Проверить напоминания\n12. Сортировать задачи\n13. Фильтрация задач\n14. Отмена последнего действия\n15. Проверка сроков задач\n16. Выйти")
        choice = input("Выберите действие: ")
        if choice == "1":
            title = input("Название: ")
            category = input("Категория: ")
            priority = input("Приоритет (низкий, средний, высокий): ")
            due_date = input("Срок выполнения (YYYY-MM-DD): ")
            description = input("Описание (необязательно): ")
            manager.add_task(title, category, priority, due_date, description)
        elif choice == "2":
            title = input("Название задачи для удаления: ")
            manager.remove_task(title)
        elif choice == "3":
            title = input("Название задачи для редактирования: ")
            new_title = input("Новое название: ") or None
            new_category = input("Новая категория: ") or None
            new_priority = input("Новый приоритет: ") or None
            new_due_date = input("Новый срок выполнения: ") or None
            new_description = input("Новое описание: ") or None
            manager.edit_task(title, new_title, new_category, new_priority, new_due_date, new_description)
        elif choice == "4":
            manager.list_tasks()
        elif choice == "5":
            title = input("Название задачи для отметки выполненной: ")
            manager.mark_completed(title)
        elif choice == "6":
            manager.clear_completed_tasks()
        elif choice == "7":
            manager.export_to_csv()
        elif choice == "8":
            manager.show_statistics()
        elif choice == "9":
            keyword = input("Введите ключевое слово для поиска: ")
            manager.search_tasks(keyword)
        elif choice == "10":
            title = input("Название задачи для установки напоминания: ")
            reminder_time = input("Время напоминания (YYYY-MM-DD HH:MM:SS): ")
            manager.set_reminder(title, reminder_time)
        elif choice == "11":
            manager.check_reminders()
        elif choice == "12":
            by = input("Сортировать по (приоритет, срок): ")
            manager.sort_tasks(by)
        elif choice == "13":
            completed = input("Фильтровать по завершенности (выполнена/не выполнена): ").lower()
            completed = True if completed == "выполнена" else False if completed == "не выполнена" else None
            filtered_tasks = manager.filter_tasks(completed)
            for task in filtered_tasks:
                print(f"Название: {task['title']}, Категория: {task['category']}")
        elif choice == "14":
            manager.undo_last_action()
        elif choice == "15":
            manager.task_deadline_alert()
        elif choice == "16":
            break
        else:
            print("Неверный выбор!")
