import streamlit as st
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional
import hashlib
import secrets


class UserManager:
    """Manage user access, authentication, and permissions"""
    
    def __init__(self):
        self.users_file = "users_database.json"
        self.pending_file = "pending_users.json"
        self.admin_emails = st.secrets.get("ADMIN_EMAILS", [])
        self.initialize_files()
    
    def initialize_files(self):
        """Create user database files if they don't exist"""
        for file in [self.users_file, self.pending_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump({}, f)
    
    def load_users(self) -> Dict:
        """Load approved users"""
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except:
            return {}
    
    def load_pending_users(self) -> Dict:
        """Load pending approval requests"""
        try:
            with open(self.pending_file, "r") as f:
                return json.load(f)
        except:
            return {}
    
    def save_users(self, users: Dict):
        """Save approved users"""
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)
    
    def save_pending_users(self, pending: Dict):
        """Save pending users"""
        with open(self.pending_file, "w") as f:
            json.dump(pending, f, indent=2)
    
    def is_admin(self, email: str) -> bool:
        """Check if user is admin"""
        return email in self.admin_emails
    
    def is_approved_user(self, email: str) -> bool:
        """Check if user is approved"""
        users = self.load_users()
        return email in users and users[email]["status"] == "active"
    
    def request_access(self, email: str, name: str, organization: str, reason: str) -> bool:
        """Submit access request"""
        pending = self.load_pending_users()
        
        if email in pending:
            return False  # Already has pending request
        
        users = self.load_users()
        if email in users:
            return False  # Already approved
        
        pending[email] = {
            "name": name,
            "organization": organization,
            "reason": reason,
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self.save_pending_users(pending)
        return True
    
    def approve_user(self, email: str, admin_email: str) -> bool:
        """Approve user access"""
        if not self.is_admin(admin_email):
            return False
        
        pending = self.load_pending_users()
        if email not in pending:
            return False
        
        users = self.load_users()
        user_data = pending[email]
        user_data["status"] = "active"
        user_data["approved_by"] = admin_email
        user_data["approved_at"] = datetime.now().isoformat()
        user_data["total_transcriptions"] = 0
        user_data["total_duration_min"] = 0
        
        users[email] = user_data
        self.save_users(users)
        
        # Remove from pending
        del pending[email]
        self.save_pending_users(pending)
        
        return True
    
    def reject_user(self, email: str, admin_email: str, reason: str = "") -> bool:
        """Reject user access request"""
        if not self.is_admin(admin_email):
            return False
        
        pending = self.load_pending_users()
        if email not in pending:
            return False
        
        pending[email]["status"] = "rejected"
        pending[email]["rejected_by"] = admin_email
        pending[email]["rejected_at"] = datetime.now().isoformat()
        pending[email]["rejection_reason"] = reason
        
        self.save_pending_users(pending)
        return True
    
    def revoke_access(self, email: str, admin_email: str, reason: str = "") -> bool:
        """Revoke user access"""
        if not self.is_admin(admin_email):
            return False
        
        users = self.load_users()
        if email not in users:
            return False
        
        users[email]["status"] = "revoked"
        users[email]["revoked_by"] = admin_email
        users[email]["revoked_at"] = datetime.now().isoformat()
        users[email]["revocation_reason"] = reason
        
        self.save_users(users)
        return True
    
    def update_user_stats(self, email: str, duration_min: float):
        """Update user usage statistics"""
        users = self.load_users()
        if email in users:
            users[email]["total_transcriptions"] += 1
            users[email]["total_duration_min"] += duration_min
            users[email]["last_used"] = datetime.now().isoformat()
            self.save_users(users)


class AdminDashboard:
    """Admin dashboard for user and usage management"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.usage_file = "usage_logs.json"
    
    def render(self, admin_email: str):
        """Render admin dashboard"""
        if not self.user_manager.is_admin(admin_email):
            st.error("⛔ Unauthorized: Admin access required")
            return
        
        st.title("🔐 Admin Dashboard")
        st.markdown(f"**Admin:** {admin_email}")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "👥 User Management",
            "⏳ Pending Requests",
            "📊 Usage Analytics",
            "⚙️ System Settings"
        ])
        
        with tab1:
            self.render_user_management()
        
        with tab2:
            self.render_pending_requests(admin_email)
        
        with tab3:
            self.render_usage_analytics()
        
        with tab4:
            self.render_system_settings()
    
    def render_user_management(self):
        """Render active users management"""
        st.subheader("Active Users")
        
        users = self.user_manager.load_users()
        active_users = {k: v for k, v in users.items() if v.get("status") == "active"}
        
        if not active_users:
            st.info("No active users yet")
            return
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Active Users", len(active_users))
        with col2:
            total_transcriptions = sum(u.get("total_transcriptions", 0) for u in active_users.values())
            st.metric("Total Transcriptions", total_transcriptions)
        with col3:
            total_duration = sum(u.get("total_duration_min", 0) for u in active_users.values())
            st.metric("Total Duration (min)", f"{total_duration:.1f}")
        
        st.markdown("---")
        
        # User list
        for email, data in active_users.items():
            with st.expander(f"📧 {email} - {data.get('name', 'N/A')}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Organization:** {data.get('organization', 'N/A')}")
                    st.write(f"**Approved:** {data.get('approved_at', 'N/A')[:10]}")
                    st.write(f"**Transcriptions:** {data.get('total_transcriptions', 0)}")
                    st.write(f"**Duration:** {data.get('total_duration_min', 0):.1f} min")
                    st.write(f"**Last Used:** {data.get('last_used', 'Never')[:10]}")
                
                with col2:
                    if st.button("🚫 Revoke Access", key=f"revoke_{email}"):
                        reason = st.text_input("Reason for revocation:", key=f"reason_{email}")
                        if st.button("Confirm Revoke", key=f"confirm_{email}"):
                            if self.user_manager.revoke_access(email, st.session_state.user_email, reason):
                                st.success(f"✅ Access revoked for {email}")
                                st.rerun()
    
    def render_pending_requests(self, admin_email: str):
        """Render pending access requests"""
        st.subheader("Pending Access Requests")
        
        pending = self.user_manager.load_pending_users()
        pending_requests = {k: v for k, v in pending.items() if v.get("status") == "pending"}
        
        if not pending_requests:
            st.info("✅ No pending requests")
            return
        
        st.warning(f"⚠️ {len(pending_requests)} pending request(s)")
        
        for email, data in pending_requests.items():
            with st.expander(f"📩 {email} - {data.get('name', 'N/A')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Name:** {data.get('name', 'N/A')}")
                    st.write(f"**Organization:** {data.get('organization', 'N/A')}")
                    st.write(f"**Reason:** {data.get('reason', 'N/A')}")
                    st.write(f"**Requested:** {data.get('requested_at', 'N/A')[:10]}")
                
                with col2:
                    col_approve, col_reject = st.columns(2)
                    
                    with col_approve:
                        if st.button("✅ Approve", key=f"approve_{email}"):
                            if self.user_manager.approve_user(email, admin_email):
                                st.success(f"✅ {email} approved!")
                                st.rerun()
                    
                    with col_reject:
                        if st.button("❌ Reject", key=f"reject_{email}"):
                            reason = st.text_input("Rejection reason:", key=f"reject_reason_{email}")
                            if st.button("Confirm Reject", key=f"confirm_reject_{email}"):
                                if self.user_manager.reject_user(email, admin_email, reason):
                                    st.success(f"❌ {email} rejected")
                                    st.rerun()
    
    def render_usage_analytics(self):
        """Render usage analytics"""
        st.subheader("Usage Analytics")
        
        logs = self.load_usage_logs()
        
        if not logs:
            st.info("No usage data yet")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", len(logs))
        
        with col2:
            total_duration = sum(log.get("duration_min", 0) for log in logs)
            st.metric("Total Duration (min)", f"{total_duration:.1f}")
        
        with col3:
            unique_users = len(set(log.get("user") for log in logs))
            st.metric("Unique Users", unique_users)
        
        with col4:
            avg_duration = total_duration / len(logs) if logs else 0
            st.metric("Avg Duration (min)", f"{avg_duration:.1f}")
        
        st.markdown("---")
        
        # Recent activity
        st.subheader("Recent Activity (Last 20)")
        recent_logs = sorted(logs, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]
        
        for log in recent_logs:
            st.text(
                f"{log.get('timestamp', 'N/A')[:19]} | "
                f"{log.get('user', 'N/A')[:30]} | "
                f"{log.get('filename', 'N/A')[:40]} | "
                f"{log.get('duration_min', 0):.1f} min"
            )
    
    def render_system_settings(self):
        """Render system settings"""
        st.subheader("System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Upload Limits")
            max_size = st.number_input("Max File Size (MB)", value=50, min_value=10, max_value=500)
            max_duration = st.number_input("Max Duration (min)", value=30, min_value=5, max_value=120)
            daily_limit = st.number_input("Daily Upload Limit", value=10, min_value=1, max_value=100)
            
            if st.button("💾 Save Settings"):
                st.success("✅ Settings saved successfully")
        
        with col2:
            st.markdown("### Database Management")
            
            if st.button("📥 Export User Database"):
                users = self.user_manager.load_users()
                st.download_button(
                    "Download users.json",
                    json.dumps(users, indent=2),
                    file_name=f"users_export_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            if st.button("📥 Export Usage Logs"):
                logs = self.load_usage_logs()
                st.download_button(
                    "Download logs.json",
                    json.dumps(logs, indent=2),
                    file_name=f"usage_logs_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            st.markdown("---")
            st.warning("⚠️ Danger Zone")
            
            if st.button("🗑️ Clear All Logs", type="secondary"):
                if st.checkbox("I understand this action is irreversible"):
                    if st.button("Confirm Delete Logs"):
                        with open(self.usage_file, "w") as f:
                            json.dump([], f)
                        st.success("✅ Logs cleared")
                        st.rerun()
    
    def load_usage_logs(self) -> List[Dict]:
        """Load usage logs"""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, "r") as f:
                return json.load(f)
        return []
    
    def log_usage(self, user_email: str, filename: str, file_size_mb: float, duration_sec: float):
        """Log transcription usage"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_email,
            "filename": filename,
            "size_mb": round(file_size_mb, 2),
            "duration_sec": round(duration_sec, 2),
            "duration_min": round(duration_sec / 60, 2)
        }
        
        logs = self.load_usage_logs()
        logs.append(log_entry)
        
        with open(self.usage_file, "w") as f:
            json.dump(logs, f, indent=2)
        
        # Update user stats
        self.user_manager.update_user_stats(user_email, log_entry["duration_min"])
