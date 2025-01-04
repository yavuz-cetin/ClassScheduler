import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import ast
import json
from tkinter.scrolledtext import ScrolledText

class DataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Scheduler Data Editor")
        self.root.geometry("1200x800")
        
        # Initialize data
        self.courses_df = pd.read_csv('courses.csv')
        self.rooms_df = pd.read_csv('rooms.csv')
        self.teachers_df = pd.read_csv('teachers.csv')
        
        # Create main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.courses_tab = ttk.Frame(self.notebook)
        self.rooms_tab = ttk.Frame(self.notebook)
        self.teachers_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.courses_tab, text='Courses')
        self.notebook.add(self.rooms_tab, text='Rooms')
        self.notebook.add(self.teachers_tab, text='Teachers')
        
        # Setup each tab
        self.setup_courses_tab()
        self.setup_rooms_tab()
        self.setup_teachers_tab()
        
        # Add save button
        save_button = ttk.Button(root, text="Save All Changes", command=self.save_all_changes)
        save_button.pack(pady=10)

    def setup_courses_tab(self):
        # Create frames
        list_frame = ttk.Frame(self.courses_tab)
        list_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        edit_frame = ttk.Frame(self.courses_tab)
        edit_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Create course listbox
        self.courses_listbox = tk.Listbox(list_frame, width=30)
        self.courses_listbox.pack(fill='y', expand=True)
        
        # Store the currently selected index
        self.current_course_index = None
        
        # Populate listbox
        for course in self.courses_df['name']:
            self.courses_listbox.insert(tk.END, course)
        
        # Create edit fields
        labels = ['Name:', 'Hours:', 'Students:', 'Possible Teachers:', 'Is Elective:', 'Course Year:']
        self.course_vars = {
            'name': tk.StringVar(),
            'hours': tk.StringVar(),  # Changed from IntVar to StringVar
            'students': tk.StringVar(),  # Changed from IntVar to StringVar
            'possible_teachers': tk.StringVar(),
            'is_elective': tk.StringVar(),  # Changed from IntVar to StringVar
            'course_year': tk.StringVar()  # Changed from IntVar to StringVar
        }
        
        row = 0
        for label in labels:
            ttk.Label(edit_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky='w')
            field_name = label.lower().replace(':', '').replace(' ', '_')
            
            if field_name == 'possible_teachers':
                entry = ttk.Entry(edit_frame, textvariable=self.course_vars[field_name], width=50)
            else:
                entry = ttk.Entry(edit_frame, textvariable=self.course_vars[field_name])
            entry.grid(row=row, column=1, padx=5, pady=5, sticky='w')
            row += 1
        
        # Add buttons
        ttk.Button(edit_frame, text="New Course", command=self.new_course).grid(row=row, column=0, pady=10)
        ttk.Button(edit_frame, text="Update Course", command=self.update_course).grid(row=row, column=1, pady=10)
        ttk.Button(edit_frame, text="Delete Course", command=self.delete_course).grid(row=row, column=2, pady=10)
        
        # Bind the selection event after creating all variables
        self.courses_listbox.bind('<<ListboxSelect>>', self.on_course_select)

    def setup_rooms_tab(self):
        # Create frames
        list_frame = ttk.Frame(self.rooms_tab)
        list_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        edit_frame = ttk.Frame(self.rooms_tab)
        edit_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Create room listbox
        self.rooms_listbox = tk.Listbox(list_frame, width=30)
        self.rooms_listbox.pack(fill='y', expand=True)
        self.rooms_listbox.bind('<<ListboxSelect>>', self.on_room_select)
        
        # Populate listbox
        for room in self.rooms_df['name']:
            self.rooms_listbox.insert(tk.END, room)
        
        # Create edit fields
        self.room_vars = {
            'name': tk.StringVar(),
            'capacity': tk.IntVar(),
            'facilities': tk.StringVar()
        }
        
        row = 0
        for label in ['Name:', 'Capacity:', 'Facilities:']:
            ttk.Label(edit_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky='w')
            field_name = label.lower().replace(':', '')
            entry = ttk.Entry(edit_frame, textvariable=self.room_vars[field_name], width=50)
            entry.grid(row=row, column=1, padx=5, pady=5, sticky='w')
            row += 1
        
        # Add buttons
        ttk.Button(edit_frame, text="New Room", command=self.new_room).grid(row=row, column=0, pady=10)
        ttk.Button(edit_frame, text="Update Room", command=self.update_room).grid(row=row, column=1, pady=10)
        ttk.Button(edit_frame, text="Delete Room", command=self.delete_room).grid(row=row, column=2, pady=10)

    def setup_teachers_tab(self):
        # Create frames
        list_frame = ttk.Frame(self.teachers_tab)
        list_frame.pack(side='left', fill='y', padx=5, pady=5)
        
        edit_frame = ttk.Frame(self.teachers_tab)
        edit_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Create teacher listbox
        self.teachers_listbox = tk.Listbox(list_frame, width=30)
        self.teachers_listbox.pack(fill='y', expand=True)
        self.teachers_listbox.bind('<<ListboxSelect>>', self.on_teacher_select)
        
        # Populate listbox
        for teacher in self.teachers_df['name']:
            self.teachers_listbox.insert(tk.END, teacher)
        
        # Create basic edit fields
        self.teacher_vars = {
            'name': tk.StringVar(),
            'title': tk.StringVar()
        }
        
        row = 0
        for label in ['Name:', 'Title:']:
            ttk.Label(edit_frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky='w')
            field_name = label.lower().replace(':', '')
            entry = ttk.Entry(edit_frame, textvariable=self.teacher_vars[field_name])
            entry.grid(row=row, column=1, padx=5, pady=5, sticky='w')
            row += 1
        
        # Create availability and preferences editors
        ttk.Label(edit_frame, text="Availability:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.availability_text = ScrolledText(edit_frame, width=40, height=5)
        self.availability_text.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        ttk.Label(edit_frame, text="Preferences:").grid(row=row, column=0, padx=5, pady=5, sticky='w')
        self.preferences_text = ScrolledText(edit_frame, width=40, height=5)
        self.preferences_text.grid(row=row, column=1, padx=5, pady=5)
        row += 1
        
        # Add buttons
        ttk.Button(edit_frame, text="New Teacher", command=self.new_teacher).grid(row=row, column=0, pady=10)
        ttk.Button(edit_frame, text="Update Teacher", command=self.update_teacher).grid(row=row, column=1, pady=10)
        ttk.Button(edit_frame, text="Delete Teacher", command=self.delete_teacher).grid(row=row, column=2, pady=10)

    def on_course_select(self, event):
        if self.courses_listbox.curselection():
            idx = self.courses_listbox.curselection()[0]
            self.current_course_index = idx  # Store the current index
            course = self.courses_df.iloc[idx]
            
            # Update all variables with current values
            self.course_vars['name'].set(str(course['name']))
            self.course_vars['hours'].set(str(course['hours']))
            self.course_vars['students'].set(str(course['students']))
            self.course_vars['possible_teachers'].set(str(course['possible_teachers']))
            self.course_vars['is_elective'].set(str(course['is_elective']))
            self.course_vars['course_year'].set(str(course['course_year']))

    def on_room_select(self, event):
        if self.rooms_listbox.curselection():
            idx = self.rooms_listbox.curselection()[0]
            room = self.rooms_df.iloc[idx]
            
            for field, var in self.room_vars.items():
                var.set(room[field])

    def on_teacher_select(self, event):
        if self.teachers_listbox.curselection():
            idx = self.teachers_listbox.curselection()[0]
            teacher = self.teachers_df.iloc[idx]
            
            self.teacher_vars['name'].set(teacher['name'])
            self.teacher_vars['title'].set(teacher['title'])
            
            # Set availability and preferences text
            self.availability_text.delete('1.0', tk.END)
            self.availability_text.insert('1.0', str(teacher['availability']))
            
            self.preferences_text.delete('1.0', tk.END)
            self.preferences_text.insert('1.0', str(teacher['preferences']))

    def new_course(self):
        # Create a new empty row in the DataFrame
        new_row = pd.DataFrame({
            'name': [''],
            'hours': [0],
            'students': [0],
            'possible_teachers': ['[]'],
            'is_elective': [0],
            'course_year': [0]
        })
        self.courses_df = pd.concat([self.courses_df, new_row], ignore_index=True)
        
        # Clear all fields
        for var in self.course_vars.values():
            if isinstance(var, tk.IntVar):
                var.set(0)
            else:
                var.set('')
                
        # Add empty item to listbox and select it
        self.courses_listbox.insert(tk.END, '')
        last_index = self.courses_listbox.size() - 1
        self.courses_listbox.selection_clear(0, tk.END)
        self.courses_listbox.selection_set(last_index)


    def update_course(self):
        try:
            if self.current_course_index is not None:
                # Get values from input fields
                new_values = {
                    'name': self.course_vars['name'].get(),
                    'hours': int(self.course_vars['hours'].get()),
                    'students': int(self.course_vars['students'].get()),
                    'possible_teachers': self.course_vars['possible_teachers'].get(),
                    'is_elective': int(self.course_vars['is_elective'].get()),
                    'course_year': int(self.course_vars['course_year'].get())
                }

                # Update DataFrame row
                self.courses_df.iloc[self.current_course_index] = pd.Series(new_values)
                
                # Update listbox
                self.courses_listbox.delete(self.current_course_index)
                self.courses_listbox.insert(self.current_course_index, new_values['name'])
                self.courses_listbox.selection_set(self.current_course_index)
                
                messagebox.showinfo("Success", "Course updated successfully!")
                
        except ValueError as e:
            messagebox.showerror("Error", "Please ensure all fields are filled correctly.\nNumbers must be integers.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def delete_course(self):
        if self.courses_listbox.curselection():
            idx = self.courses_listbox.curselection()[0]
            self.courses_df.drop(idx, inplace=True)
            self.courses_df.reset_index(drop=True, inplace=True)
            self.courses_listbox.delete(idx)

    def new_room(self):
        # Clear all fields
        for var in self.room_vars.values():
            var.set('')
        self.rooms_listbox.selection_clear(0, tk.END)

    def update_room(self):
        if self.rooms_listbox.curselection():
            idx = self.rooms_listbox.curselection()[0]
            
            # Update DataFrame
            for field, var in self.room_vars.items():
                self.rooms_df.at[idx, field] = var.get()
            
            # Update listbox
            self.rooms_listbox.delete(idx)
            self.rooms_listbox.insert(idx, self.room_vars['name'].get())
            self.rooms_listbox.selection_set(idx)

    def delete_room(self):
        if self.rooms_listbox.curselection():
            idx = self.rooms_listbox.curselection()[0]
            self.rooms_df.drop(idx, inplace=True)
            self.rooms_df.reset_index(drop=True, inplace=True)
            self.rooms_listbox.delete(idx)

    def new_teacher(self):
        # Clear all fields
        for var in self.teacher_vars.values():
            var.set('')
        self.availability_text.delete('1.0', tk.END)
        self.preferences_text.delete('1.0', tk.END)
        self.teachers_listbox.selection_clear(0, tk.END)

    def update_teacher(self):
        if self.teachers_listbox.curselection():
            idx = self.teachers_listbox.curselection()[0]
            
            try:
                # Validate JSON format
                availability = ast.literal_eval(self.availability_text.get('1.0', tk.END).strip())
                preferences = ast.literal_eval(self.preferences_text.get('1.0', tk.END).strip())
                
                # Update DataFrame
                self.teachers_df.at[idx, 'name'] = self.teacher_vars['name'].get()
                self.teachers_df.at[idx, 'title'] = self.teacher_vars['title'].get()
                self.teachers_df.at[idx, 'availability'] = str(availability)
                self.teachers_df.at[idx, 'preferences'] = str(preferences)
                
                # Update listbox
                self.teachers_listbox.delete(idx)
                self.teachers_listbox.insert(idx, self.teacher_vars['name'].get())
                self.teachers_listbox.selection_set(idx)
                
            except (SyntaxError, ValueError) as e:
                messagebox.showerror("Error", "Invalid format in availability or preferences")

    def delete_teacher(self):
        if self.teachers_listbox.curselection():
            idx = self.teachers_listbox.curselection()[0]
            self.teachers_df.drop(idx, inplace=True)
            self.teachers_df.reset_index(drop=True, inplace=True)
            self.teachers_listbox.delete(idx)

    def save_all_changes(self):
        try:
            self.courses_df.to_csv('courses.csv', index=False)
            self.rooms_df.to_csv('rooms.csv', index=False)
            self.teachers_df.to_csv('teachers.csv', index=False)
            messagebox.showinfo("Success", "All changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving changes: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataEditor(root)
    root.mainloop()