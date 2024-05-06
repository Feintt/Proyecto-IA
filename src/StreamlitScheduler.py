import streamlit as st
import random
from datetime import datetime, timedelta
import heapq

# Definición de las clases y sus horarios disponibles
clases = {
    'Matemáticas': ['Lunes 8:00-10:00', 'Miércoles 10:00-12:00'],
    'Historia': ['Lunes 10:00-12:00', 'Jueves 8:00-10:00'],
    'Ciencias': ['Martes 8:00-10:00', 'Viernes 10:00-12:00'],
    'Literatura': ['Martes 10:00-12:00', 'Miércoles 8:00-10:00'],
    'Física': ['Miércoles 14:00-16:00', 'Viernes 8:00-10:00'],
    'Química': ['Jueves 10:00-12:00', 'Viernes 14:00-16:00']
}

# Definición de las restricciones de disponibilidad de los profesores
disponibilidad_profesores = {
    'Profesor1': ['Lunes 8:00-12:00', 'Martes 8:00-12:00', 'Miércoles 8:00-12:00'],
    'Profesor2': ['Lunes 10:00-14:00', 'Martes 10:00-14:00', 'Miércoles 10:00-14:00'],
    'Profesor3': ['Martes 14:00-18:00', 'Jueves 14:00-18:00', 'Viernes 14:00-18:00'],
    'Profesor4': ['Lunes 14:00-18:00', 'Miércoles 14:00-18:00', 'Viernes 10:00-14:00'],
    'Profesor5': ['Lunes 8:00-12:00', 'Miércoles 8:00-12:00', 'Viernes 8:00-12:00'],
}

# Función para generar un horario inicial aleatorio
def generar_horario_inicial():
    horario = {}
    for clase in clases.keys():
        horario[clase] = random.choice(clases[clase])
    return horario

# Función para evaluar la calidad de un horario
def evaluar_horario(horario):
    # Por simplicidad, evaluamos simplemente la disponibilidad de los profesores
    for clase, horario_clase in horario.items():
        for profesor, horarios_disponibles in disponibilidad_profesores.items():
            if horario_clase not in horarios_disponibles:
                return False
    return True

# Función de hill climbing para mejorar el horario
def hill_climbing():
    horario_actual = generar_horario_inicial()
    mejor_horario = horario_actual.copy()

    while True:
        vecino = horario_actual.copy()
        clase_a_cambiar = random.choice(list(clases.keys()))
        nuevo_horario = random.choice(clases[clase_a_cambiar])
        vecino[clase_a_cambiar] = nuevo_horario

        if evaluar_horario(vecino):
            mejor_horario = vecino.copy()

        if random.random() < 0.1:
            break

        horario_actual = vecino.copy()

    return mejor_horario

# Clase para asignar horarios de clases
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

# Definir la interfaz de usuario con Streamlit
def main():
    st.title("Generador de Horarios Escolares")

    st.header("Generador de Horario Aleatorio")
    st.write("Haz clic en el botón para generar un horario escolar aleatorio.")
    if st.button("Generar Horario Aleatorio"):
        mejor_horario = hill_climbing()
        st.write("Mejor horario encontrado:")
        for clase, horario in mejor_horario.items():
            st.write(f"{clase}: {horario}")

    st.header("Asignador de Horario de Clases")
    st.write("Haz clic en el botón para asignar horarios de clases.")
    if st.button("Asignar Horario de Clases"):
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
        st.write("Mejor horario encontrado:")
        for class_name, (day, start_time, end_time) in class_schedule.items():
            st.write(f"{class_name}: {day} {start_time}-{end_time}")

if __name__ == "__main__":
    main()