import pandas as pd
import streamlit as st
from datetime import datetime
import hashlib

# Function to load existing users
def load_users():
    try:
        users = pd.read_csv('users.csv')
        users['Password'] = users['Password'].apply(str)
    except FileNotFoundError:
        users = pd.DataFrame(columns=["Username", "Password"])
    return users
# Display logo
st.image("sohail.png", width=300)
# Function to load existing tasks
def load_tasks():
    try:
        tasks = pd.read_csv('tasksV2.csv')
        if 'Task History' not in tasks.columns:
            tasks['Task History'] = [[] for _ in range(len(tasks))]
        else:
            tasks['Task History'] = tasks['Task History'].apply(eval)
        if 'Last Modified By' not in tasks.columns:
            tasks['Last Modified By'] = ['Unknown'] * len(tasks)
    except FileNotFoundError:
        tasks = pd.DataFrame(columns=["Task", "Status", "Deadline", "Progress", "Sector", "Importance", "Task History", "Last Modified By"])
    return tasks

# Function to save tasks to a CSV file
def save_tasks(tasks):
    tasks['Task History'] = tasks['Task History'].apply(str)
    tasks.to_csv('tasksV2.csv', index=False)

# Function to hash a password securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to authenticate users
def authenticate_user(username, password, users):
    hashed_password = hash_password(password)
    if username in users['Username'].values:
        stored_password = users[users['Username'] == username]['Password'].values[0]
        if stored_password == hashed_password:
            return True
    return False

# Function to update task history
def add_history(task_row, change_description):
    history_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {change_description}"
    task_row['Task History'].append(history_entry)
    return task_row

# Function to apply background color based on importance
def style_importance(val):
    color_mapping = {
        "High": "#ff4d4d",
        "Medium": "#ffff99",
        "Low": "#b3ffb3",
    }
    return f"background-color: {color_mapping.get(val, '')}"

# Initialize Streamlit app
st.set_page_config(layout="wide")
st.title("Task Tracker")

# Load users and tasks
users = load_users()
tasks = load_tasks()

# Session state setup for logged-in status
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

# Check login status
if not st.session_state['logged_in']:
    
        # Show login screen
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        login_submit = st.form_submit_button("Login")

        if login_submit:
            if authenticate_user(username, password, users):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success("Login successful!")

                st.experimental_rerun()
            else:
                st.error("Invalid username or password")
else:
    # Navigation options
        # Sidebar for adding or updating tasks
        with st.sidebar:
            st.subheader("Add or Update Task")
            with st.form("task_form"):
                task_name = st.text_input("Task Name")
                status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
                deadline = st.date_input("Deadline")
                progress = st.slider("Progress", 0, 100)
                sector = st.selectbox("Sector", ["Technology", "Finance", "Healthcare", "Education", "Other"])
                importance = st.selectbox("Importance", ["Low", "Medium", "High"])

                submit = st.form_submit_button("Add/Update Task")

                if submit:
                    # Check if task exists already
                    existing_task_idx = tasks[tasks['Task'] == task_name].index
                    if len(existing_task_idx) > 0:
                        idx = existing_task_idx[0]
                        task_row = tasks.loc[idx]

                        # Record changes in history
                        changes = []
                        if task_row['Status'] != status:
                            changes.append(f"Status changed from {task_row['Status']} to {status}")
                        if task_row['Deadline'] != str(deadline):
                            changes.append(f"Deadline changed from {task_row['Deadline']} to {deadline}")
                        if task_row['Progress'] != progress:
                            changes.append(f"Progress changed from {task_row['Progress']}% to {progress}%")

                        # Add changes to task history and update row
                        for change in changes:
                            tasks.loc[idx] = add_history(task_row, change)

                        tasks.loc[idx] = {
                            "Task": task_name,
                            "Status": status,
                            "Deadline": str(deadline),
                            "Progress": progress,
                            "Sector": sector,
                            "Importance": importance,
                            "Task History": task_row['Task History'],
                            "Last Modified By": st.session_state['username']
                        }
                    else:
                        # Add new task
                        new_row = {
                            "Task": task_name,
                            "Status": status,
                            "Deadline": str(deadline),
                            "Progress": progress,
                            "Sector": sector,
                            "Importance": importance,
                            "Task History": [f"Created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
                            "Last Modified By": st.session_state['username']
                        }
                        tasks = tasks._append(new_row, ignore_index=True)
                    # Save updated tasks
                    save_tasks(tasks)
#remove
        with st.sidebar:
            st.subheader("Remove Task")
            task_to_remove = st.selectbox("Select Task to Remove", tasks["Task"])
            if st.button("Remove Task"):
                tasks = tasks[tasks["Task"] != task_to_remove]
                save_tasks(tasks)
                st.experimental_rerun()
            # Logout button
            logout = st.sidebar.button("Logout")

            if logout:
                st.session_state['logged_in'] = False

        # Display the main table of tasks with conditional styling
        tasks_display = tasks[["Task", "Status", "Deadline", "Progress", "Sector", "Importance", "Last Modified By"]]
        st.dataframe(tasks_display.style.applymap(style_importance, subset=['Importance']))

        # Option to view task history
        task_to_view = st.selectbox("View Task History for", tasks['Task'])

        if task_to_view:
            task_idx = tasks[tasks['Task'] == task_to_view].index[0]
            task_history = tasks.loc[task_idx]['Task History']
            st.write("Task History:", task_history)
