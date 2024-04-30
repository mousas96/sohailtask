import pandas as pd
import streamlit as st
from datetime import datetime

# Function to load existing projects
def load_projects():
    try:
        projects = pd.read_csv('completed_projects.csv')
    except FileNotFoundError:
        projects = pd.DataFrame(columns=["Project Name", "Date of Completion", "Link to File", "Category"])
    return projects

# Function to save projects to a CSV file
def save_projects(projects):
    projects.to_csv('completed_projects.csv', index=False)

# Initialize Streamlit app
st.set_page_config(layout="wide")
st.title("Completed Projects")

# Check login status
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to view and manage projects.")
else:
    # Load existing projects
    projects = load_projects()

    # Sidebar for adding projects
    with st.sidebar:
        st.subheader("Add Completed Project")
        with st.form("project_form"):
            project_name = st.text_input("Project Name")
            completion_date = st.date_input("Date of Completion")
            link_to_file = st.text_input("Link to File")
            sector = st.selectbox("Sector", ["Technology", "Finance", "Healthcare", "Education", "Other"])

            submit = st.form_submit_button("Add Project")

            if submit:
                # Add new project
                new_project = {
                    "Project Name": project_name,
                    "Date of Completion": str(completion_date),
                    "Link to File": link_to_file,
                    "Category": category,
                }
                projects = projects.append(new_project, ignore_index=True)

                # Save updated projects
                save_projects(projects)

        # Option to delete a project
        st.sidebar.subheader("Delete a Project")
        project_to_delete = st.sidebar.selectbox("Select Project to Delete", projects["Project Name"])

        delete_button = st.sidebar.button("Delete Project")

        if delete_button and project_to_delete:
            # Delete the selected project
            projects = projects[projects["Project Name"] != project_to_delete]

            # Save updated projects
            save_projects(projects)

        # Logout button
        logout = st.sidebar.button("Logout")

        if logout:
            st.session_state['logged_in'] = False

    # Convert "Link to File" into HTML hyperlinks directly in the DataFrame
    projects_display = projects.copy()
    projects_display['Link to File'] = projects_display['Link to File'].apply(
        lambda link: f'<a href="{link}" target="_blank">Link</a>' if link else "No File"
    )

    # Display as an HTML table
    st.markdown(projects_display.to_html(escape=False), unsafe_allow_html=True)
