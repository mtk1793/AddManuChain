# pages/02_devices.py
import streamlit as st
import pandas as pd
import plotly.express as px
import time
from datetime import datetime, timedelta
from src.services.device_service import (
    get_all_devices,
    get_device_by_id,
    create_device,
    update_device,
    delete_device,  # Added delete_device for device deletion
)
from src.services.maintenance_service import (
    get_maintenance_records,
    schedule_maintenance,
)
from src.utils.auth import check_authentication
from src.components.navigation import create_sidebar
from src.components.ai_page_context import add_ai_page_context, render_page_ai_assistant, get_device_page_context
from src.components.universal_css import inject_universal_css

# Page configuration
st.set_page_config(
    page_title="Device Management | MITACS Dashboard",
    page_icon="🖨️",
    layout="wide",
)

# Inject universal CSS styling
inject_universal_css()

# Initialize session state for user_id if not already done
if 'user_id' not in st.session_state:
    st.session_state.user_id = None


def display_devices():
    """Display the list of devices with status indicators and filters."""
    st.subheader("Device List")

    # Add a refresh button
    if st.button("🔄 Refresh Devices"):
        st.experimental_rerun()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.multiselect(
            "Status",
            ["Active", "Maintenance", "Offline"],
            default=["Active", "Maintenance"],
        )

    with col2:
        type_filter = st.multiselect(
            "Device Type",
            ["3D Printer", "Scanner", "CNC Machine", "Other"],
            default=["3D Printer"],
        )

    with col3:
        location_filter = st.multiselect(
            "Location",
            ["Lab A", "Lab B", "Production Floor", "R&D Department"],
            default=[],
        )

    # Get devices with filters
    devices = get_all_devices(
        status=status_filter if status_filter else None,
        device_type=type_filter if type_filter else None,
        location=location_filter if location_filter else None,
    )

    if devices:
        # Convert to DataFrame for easy display
        devices_df = pd.DataFrame(
            [
                {
                    "ID": device["id"],  # Change from device.id to device["id"]
                    "Name": device["name"],  # Change from device.name to device["name"]
                    "Type": device["device_type"],  # Change from device.device_type to device["device_type"]
                    "Model": device["model"],  # Change from device.model to device["model"]
                    "Serial": device["serial_number"],  # And so on...
                    "Location": device["location"],
                    "Status": device["status"],
                    "Last Maintenance": (
                        device["last_maintenance_date"].strftime("%Y-%m-%d")
                        if device["last_maintenance_date"]
                        else "Not set"
                    ),
                }
                for device in devices
            ]
        )

        # Apply status styling
        def color_status(val):
            if val == "Active":
                return "background-color: #c6efcd"  # Green
            elif val == "Maintenance":
                return "background-color: #ffeb9c"  # Yellow
            elif val == "Offline":
                return "background-color: #f8c9c4"  # Red
            return ""

        # Style the dataframe
        styled_df = devices_df.style.applymap(color_status, subset=["Status"])

        st.dataframe(styled_df, use_container_width=True)

        # Select a device to show details
        selected_device_id = st.selectbox(
            "Select a device to view details",
            options=[f"{device['id']}: {device['name']}" for device in devices],
            format_func=lambda x: x.split(":")[1].strip(),
        )

        if selected_device_id:
            device_id = int(selected_device_id.split(":")[0])
            display_device_details(device_id)
    else:
        st.info("No devices found with the selected filters.")


def display_device_details(device_id):
    """Display detailed information about a specific device."""
    device = get_device_by_id(device_id)

    if device:
        st.divider()
        st.subheader(f"Device Details: {device['name']}")

        # Initialize session state variables for this device if they don't exist
        if f"show_modify_form_{device_id}" not in st.session_state:
            st.session_state[f"show_modify_form_{device_id}"] = False
        if f"show_delete_confirm_{device_id}" not in st.session_state:
            st.session_state[f"show_delete_confirm_{device_id}"] = False

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Type:** {device['device_type']}")
            st.write(f"**Model:** {device['model']}")
            st.write(f"**Serial Number:** {device['serial_number']}")
            st.write(f"**Location:** {device['location']}")
            st.write(f"**Status:** {device['status']}")

        with col2:
            st.write(
                f"**Acquisition Date:** {device['acquisition_date'].strftime('%Y-%m-%d') if device['acquisition_date'] else 'Unknown'}"
            )
            st.write(
                f"**Last Maintenance:** {device['last_maintenance_date'].strftime('%Y-%m-%d') if device['last_maintenance_date'] else 'Never'}"
            )
            st.write(
                f"**Next Maintenance:** {device['next_maintenance_date'].strftime('%Y-%m-%d') if device['next_maintenance_date'] else 'Not Scheduled'}"
            )
            st.write(f"**Manager:** {device['manager_id'] if device['manager_id'] else 'Unassigned'}")

        st.write(f"**Notes:** {device['notes']}")

        # Maintenance History
        maintenance_records = get_maintenance_records(device_id=device_id)
        if maintenance_records:
            st.subheader("Maintenance History")
            maintenance_data = [
                {
                    "Date": record["maintenance_date"].strftime("%Y-%m-%d"),
                    "Type": record["maintenance_type"],
                    "Description": record["description"],
                    "Status": record["status"],
                    "Cost": f"${record['cost']:.2f}" if record['cost'] else "N/A",
                }
                for record in maintenance_records
            ]
            st.dataframe(maintenance_data, use_container_width=True)
        else:
            st.info("No maintenance records found for this device.")

        # Actions section
        st.divider()
        st.subheader("Actions")
        
        # Button row
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✏️ Modify Device", key=f"modify_btn_{device_id}"):
                st.session_state[f"show_modify_form_{device_id}"] = True
                st.session_state[f"show_delete_confirm_{device_id}"] = False
        
        with col2:
            if st.button("🗑️ Delete Device", key=f"delete_btn_{device_id}"):
                st.session_state[f"show_delete_confirm_{device_id}"] = True
                st.session_state[f"show_modify_form_{device_id}"] = False

        # Schedule maintenance button
        with col3:
            if st.button("🔧 Schedule Maintenance", key=f"schedule_maintenance_{device_id}"):
                st.session_state.show_maintenance_form = True
                st.session_state.selected_device_id = device_id
                st.session_state[f"show_modify_form_{device_id}"] = False
                st.session_state[f"show_delete_confirm_{device_id}"] = False

        # Modify Form
        if st.session_state[f"show_modify_form_{device_id}"]:
            st.subheader("Modify Device")
            with st.form(f"modify_device_form_{device_id}"):
                mod_name = st.text_input("Device Name", value=device['name'])
                mod_type = st.selectbox(
                    "Device Type", 
                    ["3D Printer", "Scanner", "CNC Machine", "Other"], 
                    index=["3D Printer", "Scanner", "CNC Machine", "Other"].index(device['device_type'])
                )
                mod_model = st.text_input("Model", value=device['model'])
                mod_serial = st.text_input("Serial Number", value=device['serial_number'])
                mod_location = st.selectbox(
                    "Location",
                    ["Lab A", "Lab B", "Production Floor", "R&D Department", "Other"],
                    index=["Lab A", "Lab B", "Production Floor", "R&D Department", "Other"].index(device['location']) if device['location'] in ["Lab A", "Lab B", "Production Floor", "R&D Department", "Other"] else 4
                )
                mod_status = st.selectbox(
                    "Status", 
                    ["Active", "Maintenance", "Offline"],
                    index=["Active", "Maintenance", "Offline"].index(device['status'])
                )
                mod_notes = st.text_area("Notes", value=device['notes'])
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_modify = st.form_submit_button("Save Changes")
                with col2:
                    cancel_modify = st.form_submit_button("Cancel")
                
                if submit_modify:
                    success = update_device(
                        device_id=device_id,
                        device_data={
                            "name": mod_name,
                            "device_type": mod_type,
                            "model": mod_model,
                            "serial_number": mod_serial,
                            "location": mod_location,
                            "status": mod_status,
                            "notes": mod_notes
                        }
                    )

                    if success:
                        st.session_state[f"show_modify_form_{device_id}"] = False
                        st.success("Device updated successfully.")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("Failed to update device.")
                
                if cancel_modify:
                    st.session_state[f"show_modify_form_{device_id}"] = False
                    st.experimental_rerun()

        # Delete Confirmation
        if st.session_state[f"show_delete_confirm_{device_id}"]:
            st.warning("⚠️ Are you sure you want to delete this device? This action cannot be undone.")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes, Delete Device", key=f"confirm_delete_{device_id}"):
                    success = delete_device(device_id=device_id)
                    if success:
                        st.session_state[f"show_delete_confirm_{device_id}"] = False
                        st.success("Device deleted successfully.")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("Failed to delete device.")
            
            with col2:
                if st.button("Cancel", key=f"cancel_delete_{device_id}"):
                    st.session_state[f"show_delete_confirm_{device_id}"] = False
                    st.experimental_rerun()

        # Display maintenance form if button is clicked
        if (
            st.session_state.get("show_maintenance_form", False)
            and st.session_state.get("selected_device_id") == device_id
        ):
            st.subheader("Schedule Maintenance")
            with st.form("maintenance_form"):
                maintenance_type = st.selectbox(
                    "Maintenance Type", ["Regular", "Emergency", "Calibration"]
                )
                maintenance_date = st.date_input(
                    "Maintenance Date", min_value=datetime.now().date()
                )
                description = st.text_area("Description")

                col1, col2 = st.columns(2)
                with col1:
                    submit = st.form_submit_button("Save")
                with col2:
                    cancel = st.form_submit_button("Cancel")

                if submit:
                    success = schedule_maintenance(
                        device_id=device_id,
                        technician_id=st.session_state.user_id,
                        maintenance_date=maintenance_date,
                        maintenance_type=maintenance_type,
                        description=description,
                    )

                    if success:
                        st.session_state.show_maintenance_form = False
                        st.success(f"Maintenance scheduled for {maintenance_date}")
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("Failed to schedule maintenance.")
                
                if cancel:
                    st.session_state.show_maintenance_form = False
                    st.experimental_rerun()


def add_device_form():
    """Display form to add a new device."""
    st.subheader("Add New Device")

    with st.form("add_device_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Device Name*")
            device_type = st.selectbox(
                "Device Type*", ["3D Printer", "Scanner", "CNC Machine", "Other"]
            )
            model = st.text_input("Model*")
            serial_number = st.text_input("Serial Number*")
            location = st.selectbox(
                "Location",
                ["Lab A", "Lab B", "Production Floor", "R&D Department", "Other"],
            )

        with col2:
            status = st.selectbox(
                "Status", ["Active", "Maintenance", "Offline"], index=0
            )
            acquisition_date = st.date_input("Acquisition Date")
            last_maintenance_date = st.date_input("Last Maintenance Date", value=None)
            next_maintenance_date = st.date_input("Next Maintenance Date", value=None)
            # Manager would be selected from existing users, but for simplicity we'll use the current user
            manager_id = st.session_state.user_id

        notes = st.text_area("Notes")

        submit = st.form_submit_button("Add Device")

        if submit:
            if not name or not device_type or not model or not serial_number:
                st.error("Please fill in all required fields.")
                return

            success = create_device(
                name=name,
                device_type=device_type,
                model=model,
                serial_number=serial_number,
                location=location,
                status=status,
                acquisition_date=acquisition_date,
                last_maintenance_date=last_maintenance_date,
                next_maintenance_date=next_maintenance_date,
                manager_id=manager_id,
                notes=notes,
            )

            if success:
                st.success(f"Device {name} has been added successfully.")
                st.rerun()
            else:
                st.error("Failed to add device. Serial number may already be in use.")


def generate_device_visualizations():
    """Generate visualizations for device statistics."""
    st.subheader("Device Statistics")

    # Get all devices for statistics
    devices = get_all_devices()

    if not devices:
        st.info("No devices available for statistics.")
        return

    # Create DataFrames for visualizations
    devices_df = pd.DataFrame(
        [
            {
                "ID": device["id"],
                "Name": device["name"],
                "Type": device["device_type"],
                "Status": device["status"],
                "Location": device["location"],
                "Acquisition Date": device["acquisition_date"].strftime("%Y-%m-%d") if device["acquisition_date"] else "Unknown",
                "Last Maintenance": device["last_maintenance_date"].strftime("%Y-%m-%d") if device["last_maintenance_date"] else "Not set",
            }
            for device in devices
        ]
    )

    col1, col2 = st.columns(2)

    # Device Status Distribution
    with col1:
        status_counts = devices_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig1 = px.pie(
            status_counts,
            values="Count",
            names="Status",
            title="Device Status Distribution",
            color="Status",
            color_discrete_map={
                "Active": "#28a745",
                "Maintenance": "#ffc107",
                "Offline": "#dc3545",
            },
        )

        st.plotly_chart(fig1, use_container_width=True)

    # Device Type Distribution
    with col2:
        type_counts = devices_df["Type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]

        fig2 = px.bar(
            type_counts, x="Type", y="Count", title="Device Types", color="Type"
        )

        st.plotly_chart(fig2, use_container_width=True)

    # Device Locations
    location_counts = devices_df["Location"].value_counts().reset_index()
    location_counts.columns = ["Location", "Count"]

    fig3 = px.bar(
        location_counts,
        x="Location",
        y="Count",
        title="Devices by Location",
        color="Location",
    )

    st.plotly_chart(fig3, use_container_width=True)


def main():
    """Main function to display the Device Management page."""
    # Add AI assistant context for this page
    add_ai_page_context(
        page_title="Device Management",
        page_type="management", 
        **get_device_page_context()
    )
    
    # Check if user is authenticated
    check_authentication()

    # Create sidebar navigation
    create_sidebar()

    # Page header
    st.title("🖨️ Device Management")

    # Initialize session state for device management
    if "show_maintenance_form" not in st.session_state:
        st.session_state.show_maintenance_form = False
    if "selected_device_id" not in st.session_state:
        st.session_state.selected_device_id = None

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Device List", "Add New Device", "Statistics"])

    with tab1:
        display_devices()

    with tab2:
        add_device_form()

    with tab3:
        generate_device_visualizations()

    # Render AI assistant for this page
    render_page_ai_assistant()


if __name__ == "__main__":
    main()
