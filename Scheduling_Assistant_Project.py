from datetime import datetime, timedelta
from heapq import heappop, heappush
import matplotlib.pyplot as plt

# Task class to represent a single task
class Task:
    def __init__(self, name, task_type, deadline, priority, duration):
        self.name = name
        self.task_type = task_type  # "personal" or "academic"
        self.deadline = deadline  # datetime object
        self.priority = priority  # Integer priority level
        self.duration = duration  # Duration in minutes

    def __repr__(self):
        return f"{self.name} ({self.task_type}) - Priority: {self.priority}, Due: {self.deadline.strftime('%Y-%m-%d %H:%M')}, Duration: {self.duration} min"

# TaskManager class to manage tasks
class TaskManager:
    def __init__(self):
        self.tasks = []  # Min-heap for priority-based task sorting
        self.schedule = []  # List of scheduled tasks
        self.completed_tasks = []  # List to store completed tasks

    # Add a task into the priority queue
    def add_task(self, task):
        heappush(self.tasks, (task.priority, task.deadline, task))
    
    # Merge Sort for sorting tasks by deadline
    def merge_sort(self, tasks, key):
        if len(tasks) <= 1:
            return tasks
        mid = len(tasks) // 2
        left = self.merge_sort(tasks[:mid], key)
        right = self.merge_sort(tasks[mid:], key)
        return self.merge(left, right, key)
    
    # Merge function to merge two sorted halves
    def merge(self, left, right, key):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if key(left[i]) <= key(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    # Retrieve upcoming tasks sorted by deadline using Merge Sort
    def get_upcoming_tasks(self):
        sorted_tasks = self.merge_sort(self.tasks, key=lambda x: x[1])
        return [task for _, _, task in sorted_tasks]

    # Schedule tasks based on priority and deadline
    def schedule_tasks(self):
        current_time = datetime.now()
        scheduled_tasks = []
        for priority, deadline, task in sorted(self.tasks):
            if current_time + timedelta(minutes=task.duration) <= deadline:
                scheduled_tasks.append(task)
                current_time += timedelta(minutes=task.duration)
        self.schedule = scheduled_tasks
        return self.schedule

    # Analyze task density by plotting deadlines
    def analyze_task_density(self):
        deadlines = [task.deadline for _, _, task in self.tasks]
        if not deadlines:
            print("No tasks to analyze.")
            return
        deadlines.sort()
        density_times = [deadlines[0] + timedelta(hours=i) for i in range(int((deadlines[-1] - deadlines[0]).total_seconds() // 3600) + 1)]
        density_values = [sum(1 for deadline in deadlines if deadline <= time) for time in density_times]
        
        plt.figure()
        plt.plot(density_times, density_values, marker='o', color="purple")
        plt.xlabel("Time")
        plt.ylabel("Number of Tasks Due")
        plt.title("Task Density Over Time")
        plt.grid(True)
        plt.show()

    # Task reminders for overdue and pending tasks
    def remind_tasks(self):
        current_time = datetime.now()
        overdue_tasks = []
        pending_tasks = []
        for priority, deadline, task in self.tasks:#linear search
            if deadline < current_time:
                overdue_tasks.append(task)
            else:
                pending_tasks.append(task)

        overdue_tasks.sort(key=lambda x: x.priority)
        pending_tasks.sort(key=lambda x: x.priority)

        print("\n--- Task Reminders ---")
        if overdue_tasks:
            print("Overdue Tasks:")
            for task in overdue_tasks:
                print(task)
        else:
            print("No overdue tasks!")
        if pending_tasks:
            print("\nPending Tasks:")
            for task in pending_tasks:
                print(task)
        else:
            print("No pending tasks!")

    # Mark a task as completed
    def mark_task_as_completed(self, task_name):
        for index, (priority, deadline, task) in enumerate(self.tasks):
            if task.name == task_name:
                self.completed_tasks.append(task)
                del self.tasks[index]
                print(f"Task '{task_name}' marked as completed.")
                return
        print(f"Task '{task_name}' not found.")

    # View completed tasks
    def view_completed_tasks(self):
        print("\n--- Completed Tasks ---")
        if self.completed_tasks:
            for task in self.completed_tasks:
                print(task)
        else:
            print("No tasks have been completed yet.")

# Plot Gantt chart for scheduled tasks
def plot_gantt_chart(tasks):
    if not tasks:
        print("No tasks available to plot.")
        return
    
    fig, gnt = plt.subplots(figsize=(10, 5))
    gnt.set_ylim(0, 50)
    gnt.set_xlim(min(task.deadline for task in tasks), max(task.deadline for task in tasks) + timedelta(minutes=60))
    gnt.set_yticks([15, 25])
    gnt.set_yticklabels(['Academic', 'Personal'])
    gnt.set_xlabel('Time')
    gnt.set_title('Task Schedule Gantt Chart')
    
    for task in tasks:
        start = task.deadline - timedelta(minutes=task.duration)
        color = 'skyblue' if task.task_type == "academic" else 'salmon'
        gnt.broken_barh([(start, timedelta(minutes=task.duration))], 
                        (15 if task.task_type == "academic" else 25, 9),
                        facecolors=color, edgecolor='black', label=task.name)
    
    handles, labels = plt.gca().get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    gnt.legend(unique_labels.values(), unique_labels.keys())
    
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.show()

# Function to get user input for tasks
def get_user_input(manager):
    print("Enter your tasks. Type 'done' when finished.")
    while True:
        name = input("Task name (or type 'done' to finish): ")
        if name.lower() == 'done':
            break

        task_type = input("Task type (academic/personal): ").strip().lower()
        while task_type not in ['academic', 'personal']:
            task_type = input("Please enter a valid task type (academic/personal): ").strip().lower()

        while True:
            deadline_str = input("Deadline (YYYY-MM-DD HH:MM): ")
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M')
                break
            except ValueError:
                print("Invalid format. Please enter the deadline in the format YYYY-MM-DD HH:MM")

        priority = int(input("Priority (1 for highest priority): "))
        duration = int(input("Duration in minutes: "))

        task = Task(name, task_type, deadline, priority, duration)
        manager.add_task(task)
        print(f"Task '{name}' added.\n")

# Menu function
def display_menu(manager):
    manager.add_task(Task("Calculus Assignment", "academic", datetime.now() + timedelta(hours=5), 1, 120))
    manager.add_task(Task("Project Report", "academic", datetime.now() + timedelta(hours=12), 2, 180))
    manager.add_task(Task("Self-Care", "personal", datetime.now() + timedelta(hours=8), 3, 60))
    
    while True:
        print("\n--- Personal Scheduling Assistant ---")
        print("1. Add Task")
        print("2. View Upcoming Tasks")
        print("3. Schedule Tasks")
        print("4. Analyze Task Density")
        print("5. Task Reminders")
        print("6. Mark Task as Completed")
        print("7. View Completed Tasks")
        print("8. Exit")
        
        choice = input("Enter your choice (1-8): ")

        if choice == '1':
            get_user_input(manager)
        elif choice == '2':
            upcoming_tasks = manager.get_upcoming_tasks()
            if upcoming_tasks:
                print("\nUpcoming Tasks:")
                for task in upcoming_tasks:
                    print(task)
            else:
                print("No upcoming tasks.")
        elif choice == '3':
            scheduled_tasks = manager.schedule_tasks()
            if scheduled_tasks:
                print("\nScheduled Tasks:")
                for task in scheduled_tasks:
                    print(task)
                plot_gantt_chart(scheduled_tasks)
            else:
                print("No tasks available to schedule.")
        elif choice == '4':
            manager.analyze_task_density()
        elif choice == '5':
            manager.remind_tasks()
        elif choice == '6':
            task_name = input("Enter the name of the task to mark as completed: ")
            manager.mark_task_as_completed(task_name)
        elif choice == '7':
            manager.view_completed_tasks()
        elif choice == '8':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

# Main function
def main():
    manager = TaskManager()
    display_menu(manager)

# Run the main function
if __name__ == "__main__":
    main()
