from datetime import datetime, timedelta
import heapq


class ClassScheduler:
    def __init__(self, schedule, classes):
        self.schedule = schedule
        self.classes = classes
        self.start_time = datetime.strptime("00:00", "%H:%M")
        self.visited_slots = set()  # Conjunto para mantener los nodos visitados

    def calculate_remaining_time(self, current_time, event_time):
        if current_time < event_time:
            return event_time - current_time
        else:
            return timedelta(days=1) - (current_time - event_time)

    def heuristic(self, current_time, remaining_classes):
        # Simple heuristic: estimated time to schedule remaining classes
        return sum([class_duration.total_seconds() for class_duration in remaining_classes])

    def find_earliest_available_slot(self, current_time):
        earliest_slot = None
        min_remaining_time = timedelta(days=1)

        for day, slots in self.schedule.items():
            for start_time, end_time in slots:
                slot = (day, start_time)
                if slot not in self.visited_slots:
                    start = datetime.strptime(start_time, "%H:%M")
                    if start >= current_time:
                        remaining_time = self.calculate_remaining_time(current_time, start)
                        if remaining_time < min_remaining_time:
                            earliest_slot = (day, start_time)
                            min_remaining_time = remaining_time

        return earliest_slot

    def assign_class_schedule(self):
        current_time = self.start_time
        remaining_classes = [(duration, class_name) for class_name, duration in self.classes.items()]
        heapq.heapify(remaining_classes)
        class_schedule = {}

        for day in self.schedule:  # Iterar sobre todos los días disponibles
            current_time = self.start_time  # Reiniciar el tiempo al principio del día
            while remaining_classes:
                current_slot = self.find_earliest_available_slot(current_time)

                if current_slot:
                    current_day, start_time = current_slot
                    duration, class_name = heapq.heappop(remaining_classes)
                    end_time = datetime.strptime(start_time, "%H:%M") + duration

                    class_schedule[class_name] = (current_day, start_time, end_time.strftime("%H:%M"))
                    current_time = end_time
                    # Marcar el slot como visitado
                    self.visited_slots.add(current_slot)
                else:
                    break

        return class_schedule


# Ejemplo de horarios
schedule = {
    "Monday": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
    "Tuesday": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
    "Wednesday": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
    "Thursday": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
    "Friday": [("08:00", "10:00"), ("10:00", "12:00"), ("14:00", "16:00")],
}

# Diccionario de clases con duraciones
classes = {
    "Matemáticas": timedelta(hours=2),
    "Historia": timedelta(hours=2),
    "Ciencias": timedelta(hours=2),
    "Literatura": timedelta(hours=2),
    "Física": timedelta(hours=2),
    "Química": timedelta(hours=2),
}

scheduler = ClassScheduler(schedule, classes)
class_schedule = scheduler.assign_class_schedule()
print("Mejor horario encontrado:")
for class_name, (day, start_time, end_time) in class_schedule.items():
    print(f"{class_name}: {day} {start_time}-{end_time}")
