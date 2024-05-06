import random

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


# Ejecutar el algoritmo y mostrar el resultado
mejor_horario = hill_climbing()
print("Mejor horario encontrado:")
for clase, horario in mejor_horario.items():
    print(f"{clase}: {horario}")
