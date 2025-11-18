import streamlit as st
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
from src.config.settings import config

class UserManager:
    """Manages user access, authentication, and permissions.

    Attributes:
        users_file: The path to the file containing the user database.
        pending_file: The path to the file containing pending user requests.
        admin_emails: A list of administrator email addresses.
    """

    def __init__(self):
        """Initializes the UserManager."""
        self.users_file = "users_database.json"
        self.pending_file = "pending_users.json"
        self.admin_emails = config.admin_emails
        self.initialize_files()

    def initialize_files(self):
        """Creates the user database files if they do not already exist."""
        for file in [self.users_file, self.pending_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump({}, f)

    def load_users(self) -> Dict:
        """Loads the approved users from the database file.

        Returns:
            A dictionary of approved users.
        """
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_pending_users(self) -> Dict:
        """Loads the pending user requests from the database file.

        Returns:
            A dictionary of pending user requests.
        """
        try:
            with open(self.pending_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_users(self, users: Dict):
        """Saves the approved users to the database file.

        Args:
            users: A dictionary of approved users.
        """
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)

    def save_pending_users(self, pending: Dict):
        """Saves the pending user requests to the database file.

        Args:
            pending: A dictionary of pending user requests.
        """
        with open(self.pending_file, "w") as f:
            json.dump(pending, f, indent=2)

    def is_admin(self, email: str) -> bool:
        """Checks if a user is an administrator.

        Args:
            email: The email address of the user.

        Returns:
            True if the user is an administrator, False otherwise.
        """
        return email in self.admin_emails

    def is_approved_user(self, email: str) -> bool:
        """Checks if a user is an approved user.

        Args:
            email: The email address of the user.

        Returns:
            True if the user is an approved user, False otherwise.
        """
        users = self.load_users()
        return email in users and users[email]["status"] == "active"

    def request_access(
        self, email: str, name: str, organization: str, reason: str
    ) -> bool:
        """Submits a request for access to the application.

        Args:
            email: The email address of the user.
            name: The name of the user.
            organization: The organization of the user.
            reason: The reason for the access request.

        Returns:
            True if the request was successfully submitted, False otherwise.
        """
        pending = self.load_pending_users()
        users = self.load_users()

        # Check if already has access or pending
        if email in users or email in pending:
            return False

        # Create request
        pending[email] = {
            "name": name,
            "organization": organization,
            "reason": reason,
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }

        self.save_pending_users(pending)
        return True

    def approve_user(self, email: str, approved_by: str):
        """Approves a user's access request.

        Args:
            email: The email address of the user to approve.
            approved_by: The email address of the administrator who approved the
                request.
        """
        pending = self.load_pending_users()
        users = self.load_users()

        if email in pending:
            # Move from pending to users
            user_data = pending[email]
            users[email] = {
                **user_data,
                "status": "active",
                "approved_by": approved_by,
                "approved_at": datetime.now().isoformat(),
                "upload_count": 0,
                "last_upload": None,
            }

            del pending[email]

            self.save_users(users)
            self.save_pending_users(pending)

    def reject_user(self, email: str):
        """Rejects a user's access request.

        Args:
            email: The email address of the user to reject.
        """
        pending = self.load_pending_users()

        if email in pending:
            del pending[email]
            self.save_pending_users(pending)

    def revoke_access(self, email: str):
        """Revokes a user's access to the application.

        Args:
            email: The email address of the user to revoke access from.
        """
        users = self.load_users()

        if email in users:
            users[email]["status"] = "revoked"
            users[email]["revoked_at"] = datetime.now().isoformat()
            self.save_users(users)


class AdminDashboard:
    """A class for rendering the administrator dashboard.

    Attributes:
        user_manager: An instance of the UserManager class.
        logs_file: The path to the file containing the usage logs.
    """

    def __init__(self):
        """Initializes the AdminDashboard."""
        self.user_manager = UserManager()
        self.logs_file = "usage_logs.json"
        self.initialize_logs()

    def initialize_logs(self):
        """Creates the logs file if it does not already exist."""
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, "w") as f:
                json.dump([], f)

    def load_logs(self) -> List:
        """Loads the usage logs from the database file.

        Returns:
            A list of usage log entries.
        """
        try:
            with open(self.logs_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_logs(self, logs: List):
        """Saves the usage logs to the database file.

        Args:
            logs: A list of usage log entries.
        """
        with open(self.logs_file, "w") as f:
            json.dump(logs, f, indent=2)

    def log_usage(
        self, email: str, filename: str, file_size_mb: float, duration_sec: float
    ):
        """Logs the usage of the transcription service.

        Args:
            email: The email address of the user.
            filename: The name of the file that was transcribed.
            file_size_mb: The size of the file in megabytes.
            duration_sec: The duration of the audio in seconds.
        """
        logs = self.load_logs()

        logs.append({
            "email": email,
            "filename": filename,
            "file_size_mb": round(file_size_mb, 2),
            "duration_sec": round(duration_sec, 2),
            "timestamp": datetime.now().isoformat()
        })

        self.save_logs(logs)

        # Update user upload count
        users = self.user_manager.load_users()
        if email in users:
            users[email]["upload_count"] = users[email].get("upload_count", 0) + 1
            users[email]["last_upload"] = datetime.now().isoformat()
            self.user_manager.save_users(users)

    def render(self, admin_email: str):
        """Renders the administrator dashboard.

        Args:
            admin_email: The email address of the administrator.
        """
        st.title("🛡️ Admin Dashboard")
        st.markdown(f"**Logged in as:** {admin_email}")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["👥 User Management", "⏳ Pending Requests", "📊 Usage Analytics", "⚙️ System Settings"]
        )

        with tab1:
            self._render_user_management()

        with tab2:
            self._render_pending_requests(admin_email)

        with tab3:
            self._render_usage_analytics()

        with tab4:
            self._render_system_settings()

    def _render_user_management(self):
        """Renders the user management tab."""
        st.subheader("Active Users")

        users = self.user_manager.load_users()

        if not users:
            st.info("No active users yet.")
            return

        for email, data in users.items():
            if data["status"] == "active":
                with st.expander(f"📧 {email}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Name:** {data.get('name', 'N/A')}")
                        st.write(
                            f"**Organization:** {data.get('organization', 'N/A')}"
                        )
                        st.write(f"**Uploads:** {data.get('upload_count', 0)}")

                    with col2:
                        st.write(
                            f"**Approved:** {data.get('approved_at', 'N/A')[:10]}"
                        )
                        st.write(f"**Approved by:** {data.get('approved_by', 'N/A')}")
                        st.write(
                            f"**Last upload:** {data.get('last_upload', 'Never')[:10]}"
                        )

                    if st.button(f"🚫 Revoke Access", key=f"revoke_{email}"):
                        self.user_manager.revoke_access(email)
                        st.success(f"Access revoked for {email}")
                        st.rerun()

    def _render_pending_requests(self, admin_email: str):
        """Renders the pending user requests tab.

        Args:
            admin_email: The email address of the administrator.
        """
        st.subheader("Pending Access Requests")

        pending = self.user_manager.load_pending_users()

        if not pending:
            st.info("No pending requests.")
            return

        for email, data in pending.items():
            with st.expander(f"📬 {email}"):
                st.write(f"**Name:** {data['name']}")
                st.write(f"**Organization:** {data['organization']}")
                st.write(f"**Reason:** {data['reason']}")
                st.write(f"**Requested:** {data['requested_at'][:10]}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(f"✅ Approve", key=f"approve_{email}"):
                        self.user_manager.approve_user(email, admin_email)
                        st.success(f"Approved {email}")
                        st.rerun()

                with col2:
                    if st.button(f"❌ Reject", key=f"reject_{email}"):
                        self.user_manager.reject_user(email)
                        st.warning(f"Rejected {email}")
                        st.rerun()

    def _render_usage_analytics(self):
        """Renders the usage analytics tab."""
        st.subheader("System Usage Analytics")

        logs = self.load_logs()
        users = self.user_manager.load_users()

        if not logs:
            st.info("No usage data yet.")
            return

        # Summary metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Transcriptions", len(logs))

        with col2:
            total_size = sum(log["file_size_mb"] for log in logs)
            st.metric("Total Data Processed", f"{total_size:.2f} MB")

        with col3:
            st.metric(
                "Active Users",
                len([u for u in users.values() if u["status"] == "active"]),
            )

        # Recent activity
        st.markdown("### Recent Activity")
        recent_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:10]

        for log in recent_logs:
            st.write(
                f"**{log['email']}** - {log['filename']} ({log['file_size_mb']} MB) - {log['timestamp'][:10]}"
            )

    def _render_system_settings(self):
        """Renders the system settings tab."""
        st.subheader("System Configuration")

        st.info("""
        **Current Configuration:**
        - Max File Size: 50 MB
        - Max Duration: 30 minutes
        - Daily Upload Limit: 10 files per user
        - GPU Support: Disabled
        """)

        st.markdown("### Database Management")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📥 Export User Database"):
                users = self.user_manager.load_users()
                st.download_button(
                    "Download users.json",
                    json.dumps(users, indent=2),
                    file_name="users_export.json",
                    mime="application/json"
                )

        with col2:
            if st.button("📥 Export Usage Logs"):
                logs = self.load_logs()
                st.download_button(
                    "Download logs.json",
                    json.dumps(logs, indent=2),
                    file_name="usage_logs_export.json",
                    mime="application/json"
                )
