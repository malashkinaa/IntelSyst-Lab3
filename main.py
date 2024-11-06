import pandas as pd
import random

# Завантаження даних з CSV
auditoriums = pd.read_csv('auditoriums.csv')
groups = pd.read_csv('groups.csv')
lecturers = pd.read_csv('lectures.csv')
subjects = pd.read_csv('subjects.csv')

# Параметри генетичного алгоритму
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1
HOURS_PER_LESSON = 1.5
WEEKS_PER_SEMЕSTER = 14

# Створення початкової популяції
def initialize_population():
    population = []
    for _ in range(POPULATION_SIZE):
        individual = create_schedule()
        population.append(individual)
    return population

# Функція для створення випадкового розкладу
def create_schedule():
    schedule = []
    for _, subject in subjects.iterrows():
        group_id = subject['group_id']
        lecture_hours = subject['num_lectures']
        exercise_hours = subject['num_exercises']
        total_weeks = lecture_hours + exercise_hours

        for week in range(total_weeks):
            day = random.randint(1, 5)
            time_slot = random.randint(1, 4)
            auditorium_id = find_auditorium(groups[groups['group_id'] == group_id]['am_students'].values[0])
            lecturer_id = find_lecturer(subject['subject_id'], 'Лекція' if week < lecture_hours else 'Практика')

            if lecturer_id and auditorium_id:
                schedule.append({
                    'group_id': group_id,
                    'subject': subject['subject_name'],
                    'auditorium_id': auditorium_id,
                    'lecturer_id': lecturer_id,
                    'day': day,
                    'time_slot': time_slot,
                    'class_format': 'Лекція' if week < lecture_hours else 'Практика'
                })
    return schedule

# Функція оцінки пристосованості індивідуума
def fitness(schedule):
    score = 0
    conflicts = 0
    occupied_slots = {}

    for lesson in schedule:
        group_slot = (lesson['group_id'], lesson['day'], lesson['time_slot'])
        lecturer_slot = (lesson['lecturer_id'], lesson['day'], lesson['time_slot'])
        room_slot = (lesson['auditorium_id'], lesson['day'], lesson['time_slot'])

        if group_slot in occupied_slots or lecturer_slot in occupied_slots or room_slot in occupied_slots:
            conflicts += 1
        else:
            occupied_slots[group_slot] = True
            occupied_slots[lecturer_slot] = True
            occupied_slots[room_slot] = True

        score -= conflicts  # Зменшення оцінки за конфлікти
        score -= abs(schedule.count(lesson) - 1)  # Мінімізація "вікон"
    
    return score

# Вибір батьків для схрещування
def select_parents(population):
    population.sort(key=lambda x: fitness(x), reverse=True)
    return population[:2]

# Функція схрещування
def crossover(parent1, parent2):
    cutoff = len(parent1) // 2
    child = parent1[:cutoff] + parent2[cutoff:]
    return child

# Функція мутації
def mutate(schedule):
    if random.random() < MUTATION_RATE:
        lesson = random.choice(schedule)
        lesson['day'] = random.randint(1, 5)
        lesson['time_slot'] = random.randint(1, 4)
    return schedule

# Пошук доступної аудиторії для заданої кількості студентів
def find_auditorium(student_count):
    suitable_auditoriums = auditoriums[auditoriums['capacity'] >= student_count]
    if not suitable_auditoriums.empty:
        return random.choice(suitable_auditoriums['auditorium_id'].values)
    return None

# Пошук викладача для предмету
def find_lecturer(subject_id, class_format):
    eligible_lecturers = lecturers[lecturers['subject'].str.contains(subject_id) & 
                                   lecturers['class_format'].str.contains(class_format)]
    if not eligible_lecturers.empty:
        return random.choice(eligible_lecturers['lecturer_id'].values)
    return None

# Основний цикл генетичного алгоритму
def genetic_algorithm():
    population = initialize_population()
    for generation in range(GENERATIONS):
        new_population = []
        
        # Селекція та кросовер
        for _ in range(POPULATION_SIZE // 2):
            parent1, parent2 = select_parents(population)
            child1 = mutate(crossover(parent1, parent2))
            child2 = mutate(crossover(parent2, parent1))
            new_population.extend([child1, child2])

        # Оновлення популяції
        population = new_population

    # Повернення найкращого індивідуума
    best_schedule = max(population, key=lambda x: fitness(x))
    return best_schedule

# Виклик генетичного алгоритму та вивід результату
best_schedule = genetic_algorithm()
schedule_df = pd.DataFrame(best_schedule)

# Вивід таблиці розкладу
print("Фінальний розклад:")
print(schedule_df.to_string(index=False))
