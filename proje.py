from ortools.linear_solver import pywraplp
import pandas as pd
import numpy as np
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
class CourseScheduler:
    def __init__(self):
        # Time slots (assuming 9:00 to 17:00)
        self.time_slots = list(range(9, 12)) + list(range(13, 17))  # Excluding 12:00-13:00
        self.days = range(5)  # Monday to Friday
        
        # Read data from CSV files
        self.courses_df = pd.read_csv('courses.csv')
        self.rooms_df = pd.read_csv('rooms.csv')
        self.teachers_df = pd.read_csv('teachers.csv')
    
    def create_model(self):
        # Create the solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        
        # Create variables
        # x[course, teacher, room, day, start_time] = 1 if the course is scheduled
        self.x = {}
        
        for course_idx, course in self.courses_df.iterrows():
            course_hours = course['hours']
            possible_teachers = str(course['possible_teachers']).split(';')
            
            for teacher_idx, teacher in self.teachers_df.iterrows():
                if teacher['name'] in possible_teachers:
                    for room_idx, room in self.rooms_df.iterrows():
                        if room['capacity'] >= course['students']:
                            for day in self.days:
                                # Morning slots
                                for start_time in range(9, 13 - course_hours):
                                    self.x[course_idx, teacher_idx, room_idx, day, start_time] = \
                                        solver.IntVar(0, 1, f'x_{course_idx}_{teacher_idx}_{room_idx}_{day}_{start_time}')
                                # Afternoon slots
                                for start_time in range(13, 17 - course_hours + 1):
                                    self.x[course_idx, teacher_idx, room_idx, day, start_time] = \
                                        solver.IntVar(0, 1, f'x_{course_idx}_{teacher_idx}_{room_idx}_{day}_{start_time}')
        
        # Add constraints
        self.add_course_assignment_constraints(solver)
        self.add_teacher_constraints(solver)
        self.add_room_constraints(solver)
        self.add_preference_constraints(solver)
        self.add_elective_constraints(solver)
        self.add_mandatory_course_constraints(solver)
        self.add_noon_break_constraint(solver)
        
        # Set objective function
        self.set_objective_function(solver)
        
        return solver
    
    def add_course_assignment_constraints(self, solver):
        # Each course must be assigned exactly once
        for course_idx, course in self.courses_df.iterrows():
            course_vars = []
            for key, var in self.x.items():
                if key[0] == course_idx:
                    course_vars.append(var)
            solver.Add(sum(course_vars) == 1)
    
    def add_teacher_constraints(self, solver):
        # Teachers can't teach multiple courses at the same time
        for teacher_idx, teacher in self.teachers_df.iterrows():
            for day in self.days:
                for time in self.time_slots:
                    time_vars = []
                    for key, var in self.x.items():
                        course_idx, t_idx, room_idx, d, start_time = key
                        course_hours = self.courses_df.iloc[course_idx]['hours']
                        if (t_idx == teacher_idx and d == day and 
                            start_time <= time < start_time + course_hours):
                            time_vars.append(var)
                    solver.Add(sum(time_vars) <= 1)
                    
                    # Add teacher availability constraints
                    availability = eval(teacher['availability'])
                    if not availability[day][time-9]:  # Convert time to 0-based index
                        solver.Add(sum(time_vars) == 0)
    
    def add_room_constraints(self, solver):
        # Rooms can't host multiple courses at the same time
        for room_idx, room in self.rooms_df.iterrows():
            for day in self.days:
                for time in self.time_slots:
                    time_vars = []
                    for key, var in self.x.items():
                        course_idx, teacher_idx, r_idx, d, start_time = key
                        course_hours = self.courses_df.iloc[course_idx]['hours']
                        if (r_idx == room_idx and d == day and 
                            start_time <= time < start_time + course_hours):
                            time_vars.append(var)
                    solver.Add(sum(time_vars) <= 1)
    
    def add_preference_constraints(self, solver):
        # Add constraints to respect teacher preferences
        for teacher_idx, teacher in self.teachers_df.iterrows():
            preferences = eval(teacher['preferences'])
            for day in self.days:
                for start_time in self.time_slots:
                    preference_value = preferences[day][start_time - 9]
                    if preference_value == 0:
                        time_vars = []
                        for key, var in self.x.items():
                            course_idx, t_idx, room_idx, d, s_time = key
                            if (t_idx == teacher_idx and d == day and s_time == start_time):
                                time_vars.append(var)
                        solver.Add(sum(time_vars) == 0)
    
    def add_elective_constraints(self, solver):
        # Elective courses can be scheduled at any time
        pass
    
    def add_mandatory_course_constraints(self, solver):
        # Mandatory courses of the same year should not overlap
        for course_idx_1, course_1 in self.courses_df.iterrows():
            if course_1['is_elective'] == 0:
                for course_idx_2, course_2 in self.courses_df.iterrows():
                    if (course_idx_1 != course_idx_2 and 
                        course_2['is_elective'] == 0 and
                        course_1['course_year'] == course_2['course_year']):
                        
                        for teacher_idx_1, _ in self.teachers_df.iterrows():
                            for teacher_idx_2, _ in self.teachers_df.iterrows():
                                for room_idx_1, _ in self.rooms_df.iterrows():
                                    for room_idx_2, _ in self.rooms_df.iterrows():
                                        for day in self.days:
                                            for start_time_1 in self.time_slots:
                                                for start_time_2 in self.time_slots:
                                                    if (start_time_1 <= start_time_2 + course_2['hours'] - 1 and
                                                        start_time_2 <= start_time_1 + course_1['hours'] - 1):
                                                        key1 = (course_idx_1, teacher_idx_1, room_idx_1, day, start_time_1)
                                                        key2 = (course_idx_2, teacher_idx_2, room_idx_2, day, start_time_2)
                                                        if key1 in self.x and key2 in self.x:
                                                            solver.Add(self.x[key1] + self.x[key2] <= 1)

    def add_noon_break_constraint(self, solver):
            # Ensure no courses overlap with noon break (12:00-13:00)
            for day in self.days:
                for room_idx, _ in self.rooms_df.iterrows():
                    noon_break_vars = []
                    for key, var in self.x.items():
                        course_idx, teacher_idx, r_idx, d, start_time = key
                        course_hours = self.courses_df.iloc[course_idx]['hours']
                        # Check if the course would overlap with noon break
                        if (d == day and r_idx == room_idx and 
                            ((start_time < 12 and start_time + course_hours > 12) or
                            (start_time == 12))):
                            noon_break_vars.append(var)
                    solver.Add(sum(noon_break_vars) == 0)
    
    def set_objective_function(self, solver):
        objective = solver.Objective()
        
        # For each assignment, add its preference value to the objective
        for key, var in self.x.items():
            course_idx, teacher_idx, room_idx, day, start_time = key
            course_hours = self.courses_df.iloc[course_idx]['hours']
            teacher_preferences = eval(self.teachers_df.iloc[teacher_idx]['preferences'])
            
            # Calculate preference value for this assignment
            preference_value = 0
            for hour in range(course_hours):
                current_time = start_time + hour
                if current_time != 12:  # Skip noon break hour
                    adjusted_time = current_time if current_time < 12 else current_time - 1
                    if adjusted_time - 9 < len(teacher_preferences[day]):
                        preference_value += teacher_preferences[day][adjusted_time - 9]
            
            # Add to objective with appropriate coefficient
            objective.SetCoefficient(var, preference_value)
        
        objective.SetMaximization()
    
    def solve(self):
        solver = self.create_model()
        status = solver.Solve()
        
        if status == pywraplp.Solver.OPTIMAL:
            self.print_solution()
            print(f"\nObjective value (Total preference score): {solver.Objective().Value()}")
            return True
        else:
            print("No solution found.")
            return False
    
    def print_solution(self):
        for key, var in self.x.items():
            if var.solution_value() > 0.5:
                course_idx, teacher_idx, room_idx, day, start_time = key
                course = self.courses_df.iloc[course_idx]
                teacher = self.teachers_df.iloc[teacher_idx]
                room = self.rooms_df.iloc[room_idx]
                
                # Get preference value for this assignment
                preferences = eval(teacher['preferences'])
                course_hours = course['hours']
                pref_value = 0
                for h in range(course_hours):
                    current_time = start_time + h
                    if current_time != 12:  # Skip noon break hour
                        adjusted_time = current_time if current_time < 12 else current_time - 1
                        if adjusted_time - 9 < len(preferences[day]):
                            pref_value += preferences[day][adjusted_time - 9]
                
                print(f"Course: {course['name']}")
                print(f"Teacher: {teacher['name']}")
                print(f"Room: {room['name']}")
                print(f"Day: {day + 1}")
                print(f"Time: {start_time}:00 - {start_time + course['hours']}:00")
                print(f"Preference Score: {pref_value}")
                print("-------------------")

# Usage
if __name__ == "__main__":
    scheduler = CourseScheduler()
    scheduler.solve()
