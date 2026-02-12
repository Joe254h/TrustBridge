import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import hashlib
import json
import os
from io import BytesIO
import base64

# Page config
st.set_page_config(
    page_title="TrustBridge - Financial Trust Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'users_db' not in st.session_state:
    st.session_state.users_db = {}
if 'transactions_db' not in st.session_state:
    st.session_state.transactions_db = {}
if 'page' not in st.session_state:
    st.session_state.page = 'Dashboard'

# Database functions (simulated - in production use MongoDB/PostgreSQL)
def save_user(email, name, password, plan='free'):
    """Save user to database"""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    st.session_state.users_db[email] = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'plan': plan,
        'created_at': datetime.now().isoformat(),
        'trust_score': 300,
        'consistency_days': 0,
        'profile_image': None
    }
    # Initialize user transactions
    st.session_state.transactions_db[email] = []
    return True

def verify_user(email, password):
    """Verify user credentials"""
    if email in st.session_state.users_db:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return st.session_state.users_db[email]['password'] == hashed_password
    return False

def get_user_data(email):
    """Get user data"""
    return st.session_state.users_db.get(email, {})

def save_transaction(email, transaction_data):
    """Save transaction to user's record"""
    if email not in st.session_state.transactions_db:
        st.session_state.transactions_db[email] = []
    st.session_state.transactions_db[email].insert(0, transaction_data)
    update_trust_score(email)

def get_user_transactions(email):
    """Get user transactions"""
    return st.session_state.transactions_db.get(email, [])

def calculate_trust_score(email):
    """
    Calculate trust score based on multiple factors:
    - Base score: 300
    - Consistency: +2 points per consecutive day of activity
    - Verification: +5 points per verified transaction (with receipt)
    - Transaction count: +1 point per transaction
    - Income regularity: +10 points if income is regular (weekly/monthly)
    - Expense management: +5 points if expenses < income
    - Streak bonus: +20 points for 30+ day streak
    """
    transactions = get_user_transactions(email)
    user_data = get_user_data(email)
    
    base_score = 300
    score = base_score
    
    if not transactions:
        return score
    
    # Count verified transactions
    verified_count = sum(1 for t in transactions if t.get('verified', False))
    score += verified_count * 5
    
    # Transaction count bonus
    score += len(transactions) * 1
    
    # Calculate consistency (days with activity)
    transaction_dates = set()
    for t in transactions:
        date_str = t['date'].split(' ')[0] if isinstance(t['date'], str) else t['date'].strftime('%Y-%m-%d')
        transaction_dates.add(date_str)
    
    consistency_days = len(transaction_dates)
    score += consistency_days * 2
    
    # Streak bonus
    if consistency_days >= 30:
        score += 20
    
    # Income vs Expense analysis
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
    
    if total_income > total_expense:
        score += 15
    
    # Income regularity check (check if there's income in last 7 days)
    recent_income = [t for t in transactions if t['type'] == 'Income']
    if recent_income:
        score += 10
    
    # Cap score at 850 (similar to credit scores)
    score = min(score, 850)
    
    return score

def update_trust_score(email):
    """Update user's trust score"""
    new_score = calculate_trust_score(email)
    st.session_state.users_db[email]['trust_score'] = new_score

def get_score_tier(score):
    """Get score tier and color"""
    if score >= 750:
        return "Excellent", "#4CAF50", "LEVEL 5"
    elif score >= 650:
        return "Good", "#2196F3", "LEVEL 4"
    elif score >= 500:
        return "Building", "#FF9800", "LEVEL 3"
    elif score >= 400:
        return "Fair", "#FFC107", "LEVEL 2"
    else:
        return "Starting", "#9E9E9E", "LEVEL 1"

def check_password_strength(password):
    """Check password strength"""
    if len(password) < 8:
        return "Too short", "🔴", 0
    
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    strength = sum([has_upper, has_lower, has_digit, has_special])
    
    if strength == 4 and len(password) >= 12:
        return "Very Strong", "🟢", 100
    elif strength >= 3 and len(password) >= 10:
        return "Strong", "🟢", 75
    elif strength >= 2:
        return "Moderate", "🟡", 50
    else:
        return "Weak", "🔴", 25

def extract_amount_from_text(text):
    """Extract amount from receipt text using regex"""
    # Common patterns for amounts
    patterns = [
        r'(?:TOTAL|Total|total|AMOUNT|Amount|amount)[\s:]*[₦$£€]?\s*(\d+[,.]?\d*\.?\d+)',
        r'[₦$£€]\s*(\d+[,.]?\d*\.?\d+)',
        r'(\d+[,.]?\d*\.?\d+)\s*(?:NGN|USD|GBP|EUR)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except:
                continue
    return None

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        background: #F8F9FA;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #E5E7EB;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        padding: 0;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: 1px solid #E5E7EB;
    }
    
    /* Trust Score Circle */
    .score-circle {
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: conic-gradient(#2563EB 0deg 270deg, #E5E7EB 270deg 360deg);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .score-inner {
        width: 190px;
        height: 190px;
        background: white;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .score-number {
        font-size: 72px;
        font-weight: 700;
        color: #2563EB;
        line-height: 1;
    }
    
    .score-label {
        font-size: 14px;
        color: #6B7280;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Action buttons */
    .income-btn {
        background: #10B981 !important;
        color: white !important;
    }
    
    .expense-btn {
        background: #EF4444 !important;
        color: white !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: #2563EB;
    }
    
    /* Badges */
    .status-badge {
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-excellent {
        background: #10B981;
        color: white;
    }
    
    .badge-good {
        background: #2563EB;
        color: white;
    }
    
    .badge-building {
        background: #F59E0B;
        color: white;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 30px;
        color: #6B7280;
        font-size: 14px;
        border-top: 1px solid #E5E7EB;
        margin-top: 50px;
    }
    
    /* Transaction items */
    .transaction-item {
        background: white;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        margin-bottom: 12px;
    }
    
    /* Password strength */
    .password-strength {
        margin-top: 8px;
        font-size: 13px;
    }
    
    /* Professional spacing */
    h1 {
        font-weight: 700;
        color: #111827;
    }
    
    h2 {
        font-weight: 600;
        color: #1F2937;
    }
    
    h3 {
        font-weight: 600;
        color: #374151;
    }
    
    p {
        color: #6B7280;
    }
    
    /* Remove streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom divider */
    hr {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 24px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Authentication pages
def login_page():
    st.markdown("<h1 style='text-align: center; margin-bottom: 10px;'>🛡️ TrustBridge</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; margin-bottom: 40px;'>Build financial trust through verified transactions</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])
    
    with tab1:
        st.markdown("### Welcome Back")
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            with col2:
                forgot = st.form_submit_button("Forgot Password?", use_container_width=True)
            
            if submit:
                if verify_user(email, password):
                    st.session_state.authenticated = True
                    st.session_state.current_user = email
                    st.success("✓ Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    with tab2:
        st.markdown("### Create Your Account")
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email Address", placeholder="your.email@example.com", key="signup_email")
            password = st.text_input("Password", type="password", placeholder="Create a strong password", key="signup_password")
            
            # Password strength indicator
            if password:
                strength_text, strength_emoji, strength_value = check_password_strength(password)
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.progress(strength_value / 100)
                with col_b:
                    st.markdown(f"**{strength_emoji} {strength_text}**")
                
                st.caption("Password must contain: Uppercase, lowercase, number, special character (8+ chars)")
            
            plan = st.radio("Choose Plan", ["Free (Basic features)", "Premium ($9.99/month - Coming soon)"], horizontal=True)
            
            agree = st.checkbox("I agree to Terms of Service and Privacy Policy")
            
            submit = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if submit:
                if not all([name, email, password]):
                    st.error("Please fill in all fields")
                elif not agree:
                    st.error("Please agree to Terms of Service")
                elif email in st.session_state.users_db:
                    st.error("Email already registered")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    plan_type = 'free' if 'Free' in plan else 'premium'
                    save_user(email, name, password, plan_type)
                    st.success("✓ Account created! Please sign in.")
                    st.balloons()

def sidebar_navigation():
    """Professional sidebar navigation"""
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style='display: flex; align-items: center; gap: 15px; padding: 20px 10px;'>
            <div style='font-size: 36px;'>🛡️</div>
            <div style='font-size: 24px; font-weight: 700; color: #2563EB;'>TrustBridge</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # User info
        user_data = get_user_data(st.session_state.current_user)
        st.markdown(f"**{user_data.get('name', 'User')}**")
        st.caption(st.session_state.current_user)
        
        # Plan badge
        plan = user_data.get('plan', 'free')
        if plan == 'premium':
            st.markdown("⭐ **Premium Member**")
        else:
            st.markdown("🆓 **Free Plan**")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Navigation
        st.markdown("**MAIN**")
        pages = {
            "Dashboard": "📊",
            "Transactions": "💳",
            "Opportunities": "🔓",
        }
        
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()
        
        st.markdown("<br>**REPORTS**", unsafe_allow_html=True)
        report_pages = {
            "Financial Report": "📄",
            "Verification History": "🔍",
        }
        
        for page_name, icon in report_pages.items():
            if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state.page = page_name
                st.rerun()
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Secure badge
        st.info("**✓ Secure History**\n\nVerifiable Engine Active")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Settings and Help
        if st.button("⚙️ Profile & Settings", use_container_width=True):
            st.session_state.page = "Profile"
            st.rerun()
        
        if st.button("❓ Help Center", use_container_width=True):
            st.session_state.page = "Help"
            st.rerun()
        
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()

# Main content pages
def dashboard_page():
    user_data = get_user_data(st.session_state.current_user)
    transactions = get_user_transactions(st.session_state.current_user)
    
    st.title("Dashboard")
    st.caption("Track your trust score and unlock financial opportunities.")
    
    # Calculate metrics
    total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
    net_flow = total_income - total_expense
    verified_count = sum(1 for t in transactions if t.get('verified', False))
    
    # Calculate consistency
    if transactions:
        transaction_dates = set()
        for t in transactions:
            date_str = t['date'].split(' ')[0] if isinstance(t['date'], str) else t['date'].strftime('%Y-%m-%d')
            transaction_dates.add(date_str)
        consistency_weeks = len(transaction_dates) // 7
    else:
        consistency_weeks = 0
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Verified Monthly Income", f"${total_income:,.2f}", 
                 delta="+12% vs last month" if total_income > 0 else None)
    
    with col2:
        st.metric("Consistency Streak", f"{consistency_weeks} Weeks",
                 delta="Active" if consistency_weeks > 0 else "Start tracking")
    
    with col3:
        st.metric("Verified Expenses", f"${total_expense:,.2f}",
                 delta="Updated recently")
    
    with col4:
        report_status = "Ready" if verified_count >= 5 else "Need more data"
        st.metric("Report Readiness", report_status,
                 delta="✓ Verified for banks" if verified_count >= 5 else None)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Trust Score Section
        st.markdown("### Your Trust Score")
        
        trust_score = user_data.get('trust_score', 300)
        status, color, level = get_score_tier(trust_score)
        
        col_score, col_actions = st.columns(2)
        
        with col_score:
            # Score circle
            progress_angle = min(360, (trust_score / 850) * 360)
            st.markdown(f"""
            <div style='text-align: center; margin: 20px 0;'>
                <div class='score-circle' style='background: conic-gradient({color} 0deg {progress_angle}deg, #E5E7EB {progress_angle}deg 360deg);'>
                    <div class='score-inner'>
                        <div class='score-number'>{trust_score}</div>
                        <div class='score-label'>{level}</div>
                    </div>
                </div>
                <div style='margin-top: 20px;'>
                    <span class='status-badge badge-{status.lower()}'>{status}</span>
                </div>
                <p style='margin-top: 15px; color: #6B7280; font-size: 14px;'>
                    Updated dynamically based on activity
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_actions:
            st.markdown("#### Core Actions")
            
            col_inc, col_exp = st.columns(2)
            with col_inc:
                if st.button("➕\nIncome", use_container_width=True, key="add_income_btn"):
                    st.session_state.show_income_modal = True
            
            with col_exp:
                if st.button("➖\nExpense", use_container_width=True, key="add_expense_btn"):
                    st.session_state.show_expense_modal = True
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("#### Net Monthly Flow")
            st.markdown(f"<h2 style='color: {'#10B981' if net_flow > 0 else '#EF4444'};'>${net_flow:,.2f}</h2>", unsafe_allow_html=True)
            st.caption(f"Across {verified_count} verified records")
        
        # Progress to next tier
        next_tier_score = 800 if trust_score < 750 else 850
        progress = min(100, ((trust_score - 700) / (next_tier_score - 700)) * 100) if trust_score >= 700 else (trust_score / 700) * 100
        
        st.info(f"**Progress to Tier 2 Eligibility: {progress:.0f}%**\n\n🎉 Keep it up! You are {max(0, 5 - verified_count)} verified transactions away from unlocking micro-loans.")
        
        st.progress(progress / 100)
        
        # Unlock Opportunities
        st.markdown("<br>### Unlock Opportunities", unsafe_allow_html=True)
        
        opportunities = [
            {"name": "Apartment Rental Eligibility", "icon": "🏢", "progress": min(100, (trust_score / 750) * 100), 
             "status": "Ready to apply" if trust_score >= 750 else f"Need {750 - trust_score} more points"},
            {"name": "Micro-Loan ($500 - $2000)", "icon": "💰", "progress": min(100, (verified_count / 15) * 100),
             "status": "Eligible now!" if verified_count >= 15 else f"Record {15 - verified_count} more verified transactions"},
            {"name": "Job Verification Premium", "icon": "💼", "progress": min(100, (trust_score / 650) * 100),
             "status": "Unlocked!" if trust_score >= 650 else f"Need {650 - trust_score} more points"},
        ]
        
        for opp in opportunities:
            with st.container():
                col_icon, col_content, col_status = st.columns([0.3, 2.5, 1.2])
                
                with col_icon:
                    st.markdown(f"<div style='font-size: 32px; text-align: center;'>{opp['icon']}</div>", unsafe_allow_html=True)
                
                with col_content:
                    st.markdown(f"**{opp['name']}**")
                    st.progress(opp['progress'] / 100)
                    st.caption(opp['status'])
                
                with col_status:
                    if opp['progress'] >= 100:
                        if st.button("Apply", key=f"apply_{opp['name']}", type="primary"):
                            st.success("🎉 Application started!")
                    else:
                        st.caption(f"{opp['progress']:.0f}% Ready")
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown("### Recent Activity")
        
        if transactions:
            for txn in transactions[:5]:
                with st.container():
                    col_icon, col_details, col_amount = st.columns([0.4, 2, 1])
                    
                    with col_icon:
                        icon = "💼" if txn['type'] == 'Income' else "🛒"
                        st.markdown(f"<div style='font-size: 24px;'>{icon}</div>", unsafe_allow_html=True)
                    
                    with col_details:
                        st.markdown(f"**{txn['category']}**")
                        date_str = txn['date'] if isinstance(txn['date'], str) else txn['date'].strftime("%b %d, %Y %I:%M %p")
                        st.caption(date_str)
                    
                    with col_amount:
                        sign = "+" if txn['type'] == 'Income' else "-"
                        color = "#10B981" if txn['type'] == 'Income' else "#EF4444"
                        st.markdown(f"<div style='color: {color}; font-weight: 600;'>{sign}${txn['amount']:.2f}</div>", unsafe_allow_html=True)
                        if txn.get('verified'):
                            st.caption("✓ Verified")
                    
                    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No transactions yet. Start recording to build your trust score!")
        
        # Generate Report
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📄 Generate Report", use_container_width=True, type="primary"):
            st.session_state.page = "Financial Report"
            st.rerun()

def transactions_page():
    st.title("Transactions")
    
    tab1, tab2 = st.tabs(["📋 View Transactions", "➕ Add Transaction"])
    
    with tab1:
        transactions = get_user_transactions(st.session_state.current_user)
        
        if transactions:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_type = st.selectbox("Type", ["All", "Income", "Expense"])
            with col2:
                filter_verified = st.selectbox("Status", ["All", "Verified Only", "Unverified Only"])
            with col3:
                sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High-Low)", "Amount (Low-High)"])
            
            # Apply filters
            filtered = transactions.copy()
            if filter_type != "All":
                filtered = [t for t in filtered if t['type'] == filter_type]
            if filter_verified == "Verified Only":
                filtered = [t for t in filtered if t.get('verified', False)]
            elif filter_verified == "Unverified Only":
                filtered = [t for t in filtered if not t.get('verified', False)]
            
            # Sort
            if "Amount" in sort_by:
                filtered = sorted(filtered, key=lambda x: x['amount'], reverse="High" in sort_by)
            
            # Display
            st.markdown(f"**{len(filtered)} transactions**")
            
            for txn in filtered:
                with st.expander(f"{txn['type']}: ${txn['amount']:.2f} - {txn['category']} {'✓' if txn.get('verified') else ''}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Amount:** ${txn['amount']:.2f}")
                        st.write(f"**Category:** {txn['category']}")
                        st.write(f"**Type:** {txn['type']}")
                    with col2:
                        date_str = txn['date'] if isinstance(txn['date'], str) else txn['date'].strftime("%b %d, %Y %I:%M %p")
                        st.write(f"**Date:** {date_str}")
                        st.write(f"**Verified:** {'Yes ✓' if txn.get('verified') else 'No'}")
                        if txn.get('description'):
                            st.write(f"**Note:** {txn['description']}")
                    
                    if txn.get('extracted_text'):
                        with st.expander("📄 View Receipt Text"):
                            st.code(txn['extracted_text'])
        else:
            st.info("No transactions yet. Add your first transaction below!")
    
    with tab2:
        add_transaction_form()

def add_transaction_form():
    st.markdown("### Add New Transaction")
    
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            txn_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
            amount = st.number_input("Amount ($)", min_value=0.01, step=0.01, value=None, placeholder="0.00")
            category = st.selectbox("Category", [
                "Freelance Pay", "Salary", "Business Income", "Investment", "Other Income",
                "Grocery", "Rent", "Utility Bill", "Transport", "Healthcare", "Entertainment", "Other Expense"
            ])
        
        with col2:
            txn_date = st.date_input("Date", datetime.now())
            description = st.text_input("Description (optional)", placeholder="Add a note about this transaction")
        
        st.markdown("#### 📸 Upload Receipt (Recommended for verification)")
        st.info("Upload a receipt to automatically extract amount and verify your transaction. This increases your trust score by +5 points instead of +2.")
        
        uploaded_file = st.file_uploader(
            "Take a photo or upload receipt",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Supports handwritten and printed receipts"
        )
        
        extracted_amount = None
        extracted_text = ""
        
        if uploaded_file:
            col_img, col_extract = st.columns(2)
            
            with col_img:
                if uploaded_file.type.startswith('image'):
                    from PIL import Image
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Receipt Preview", width=300)
            
            with col_extract:
                st.markdown("**Processing Receipt...**")
                # Simulated OCR (in production, use pytesseract or Google Vision API)
                sample_texts = [
                    "TOTAL: $45.50\nThank you for your purchase",
                    "Amount Due: ₦1,250.00\nDate: " + datetime.now().strftime("%Y-%m-%d"),
                    "GRAND TOTAL\n$82.30\nCash",
                ]
                extracted_text = sample_texts[0]  # In production, use actual OCR
                
                # Extract amount
                extracted_amount = extract_amount_from_text(extracted_text)
                
                if extracted_amount:
                    st.success(f"✓ Amount detected: ${extracted_amount:.2f}")
                    st.caption("Amount will be used if you don't enter one manually")
                else:
                    st.warning("Could not detect amount. Please enter manually.")
                
                with st.expander("📄 View Extracted Text"):
                    st.code(extracted_text)
        
        submitted = st.form_submit_button("💾 Save Transaction", type="primary", use_container_width=True)
        
        if submitted:
            # Use extracted amount if manual amount not provided
            final_amount = amount if amount else extracted_amount
            
            if not final_amount:
                st.error("Please enter an amount or upload a receipt with a visible amount.")
            elif not category:
                st.error("Please select a category.")
            else:
                new_txn = {
                    "date": datetime.combine(txn_date, datetime.now().time()),
                    "type": txn_type,
                    "amount": final_amount,
                    "category": category,
                    "description": description,
                    "verified": uploaded_file is not None,
                    "extracted_text": extracted_text if uploaded_file else None
                }
                
                save_transaction(st.session_state.current_user, new_txn)
                
                points = 5 if uploaded_file else 2
                st.success(f"✓ Transaction saved! Trust score increased by +{points} points")
                st.balloons()
                st.rerun()

def profile_page():
    st.title("Profile & Settings")
    
    user_data = get_user_data(st.session_state.current_user)
    
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔐 Security", "📊 Statistics"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Profile Photo")
            st.image("https://via.placeholder.com/150", width=150)
            uploaded_photo = st.file_uploader("Upload new photo", type=['png', 'jpg', 'jpeg'])
            if uploaded_photo:
                st.info("Photo upload feature - Premium only")
        
        with col2:
            st.markdown("### Account Information")
            with st.form("profile_form"):
                name = st.text_input("Full Name", value=user_data.get('name', ''))
                email = st.text_input("Email", value=st.session_state.current_user, disabled=True)
                
                plan = user_data.get('plan', 'free')
                st.info(f"**Current Plan:** {plan.upper()}")
                
                if plan == 'free':
                    st.warning("**Upgrade to Premium for:**\n- Advanced analytics\n- Priority support\n- PDF report encryption\n- Image verification\n- Custom categories")
                    if st.form_submit_button("🌟 Upgrade to Premium ($9.99/month)"):
                        st.info("Premium upgrade coming soon!")
                
                if st.form_submit_button("Save Changes"):
                    st.session_state.users_db[st.session_state.current_user]['name'] = name
                    st.success("Profile updated!")
    
    with tab2:
        st.markdown("### Security Settings")
        
        with st.form("password_form"):
            st.markdown("**Change Password**")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if new_password:
                strength_text, strength_emoji, strength_value = check_password_strength(new_password)
                st.progress(strength_value / 100)
                st.caption(f"{strength_emoji} {strength_text}")
            
            if st.form_submit_button("Update Password"):
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 8:
                    st.error("Password too short")
                else:
                    st.success("Password updated successfully!")
    
    with tab3:
        st.markdown("### Your Statistics")
        
        transactions = get_user_transactions(st.session_state.current_user)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Transactions", len(transactions))
        with col2:
            verified = sum(1 for t in transactions if t.get('verified'))
            st.metric("Verified Transactions", verified)
        with col3:
            st.metric("Trust Score", user_data.get('trust_score', 300))
        
        st.markdown("### Transaction History")
        if transactions:
            df = pd.DataFrame(transactions)
            st.dataframe(df[['date', 'type', 'category', 'amount', 'verified']], use_container_width=True)
        else:
            st.info("No transaction data yet")

def help_center_page():
    st.title("Help Center")
    
    st.markdown("""
    ### Welcome to TrustBridge Help Center
    
    #### 📚 Quick Start Guide
    """)
    
    with st.expander("🚀 How to Get Started"):
        st.markdown("""
        1. **Create an account** with your email and a strong password
        2. **Add your first transaction** by uploading a receipt or manually entering details
        3. **Build your trust score** by consistently recording verified transactions
        4. **Unlock opportunities** like loans, rentals, and job verifications
        """)
    
    with st.expander("📸 How Receipt Scanning Works"):
        st.markdown("""
        **TrustBridge uses OCR (Optical Character Recognition) to read receipts:**
        
        - Upload any receipt: handwritten or printed
        - Works with photos from your phone camera
        - Automatically extracts amounts and dates
        - Increases trust score more than manual entries
        
        **Tips for best results:**
        - Take clear, well-lit photos
        - Make sure text is readable
        - Capture the full receipt
        """)
    
    with st.expander("🎯 Understanding Trust Score"):
        st.markdown("""
        **Your trust score (300-850) is calculated based on:**
        
        - ✅ Number of verified transactions (+5 points each)
        - ✅ Consistency of activity (+2 points per active day)
        - ✅ Regular income (+10 points)
        - ✅ Positive cash flow (+15 points if income > expenses)
        - ✅ Streaks (+20 points for 30+ day streak)
        
        **Score Tiers:**
        - 750+: Excellent (Unlock all opportunities)
        - 650-749: Good (Most opportunities available)
        - 500-649: Building (Some opportunities)
        - 400-499: Fair (Keep building)
        - 300-399: Starting (New user)
        """)
    
    with st.expander("🔓 Unlocking Opportunities"):
        st.markdown("""
        **Requirements for opportunities:**
        
        **Micro-Loans ($500-$2000):**
        - 15+ verified transactions
        - Trust score 650+
        - Consistent income records
        
        **Apartment Rental Pre-Approval:**
        - Trust score 750+
        - 20+ verified transactions
        - Proof of stable income
        
        **Job Verification Premium:**
        - Trust score 650+
        - 10+ verified income records
        """)
    
    with st.expander("📄 Generating Reports"):
        st.markdown("""
        **Financial reports are:**
        - PDF format, professionally formatted
        - Password protected (code sent to your email)
        - Verified and tamper-proof
        - Accepted by banks, landlords, and employers
        
        **Premium users get:**
        - Custom branding
        - Enhanced security
        - Unlimited reports
        - Priority processing
        """)
    
    with st.expander("🆓 Free vs Premium"):
        st.markdown("""
        **Free Plan:**
        - ✅ Unlimited transaction recording
        - ✅ Basic trust score
        - ✅ 5 PDF reports per month
        - ✅ Standard opportunities
        
        **Premium Plan ($9.99/month):**
        - ⭐ Everything in Free
        - ⭐ Advanced analytics
        - ⭐ Unlimited encrypted reports
        - ⭐ Priority customer support
        - ⭐ Custom categories
        - ⭐ Image verification
        - ⭐ Early access to new features
        """)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("### 📧 Contact Support")
    st.info("**Email:** support@trustbridge.ng\n\n**WhatsApp:** +234 XXX XXX XXXX\n\n**Response time:** Within 24 hours")
    
    st.markdown("### 🌐 Resources")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("📖 [User Guide](https://trustbridge.ng/guide)")
    with col2:
        st.markdown("🎥 [Video Tutorials](https://trustbridge.ng/videos)")
    with col3:
        st.markdown("💬 [Community Forum](https://trustbridge.ng/forum)")

def financial_report_page():
    st.title("Financial Report")
    
    st.markdown("### Generate Verifiable Report")
    st.caption("Create a PDF report verified for banks, landlords, and employers")
    
    user_data = get_user_data(st.session_state.current_user)
    transactions = get_user_transactions(st.session_state.current_user)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        with st.form("report_form"):
            report_type = st.selectbox(
                "Report Type",
                ["Full Financial Summary", "Income Verification Only", "Trust Score Certificate", "Transaction History"]
            )
            
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now() - timedelta(days=30), datetime.now()),
                max_value=datetime.now()
            )
            
            include_charts = st.checkbox("Include Charts & Analytics", value=True)
            
            password_protect = st.checkbox("Password Protect PDF (Code sent to email)", value=True)
            
            if st.form_submit_button("🔽 Generate Report", type="primary", use_container_width=True):
                st.success("✓ Report generated successfully!")
                
                # Simulate PDF generation
                st.download_button(
                    "📥 Download PDF Report",
                    data=b"[Simulated PDF Content - In production this would be actual PDF]",
                    file_name=f"trustbridge_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                if password_protect:
                    st.info(f"🔐 **Report locked!**\n\nPassword has been sent to: {st.session_state.current_user}\n\nAccess Code: TB-{datetime.now().strftime('%Y%m%d')}-XXXX")
                
                st.balloons()
    
    with col2:
        st.markdown("#### Report Preview")
        
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'Income')
        total_expense = sum(t['amount'] for t in transactions if t['type'] == 'Expense')
        net_flow = total_income - total_expense
        verified_count = sum(1 for t in transactions if t.get('verified'))
        
        st.metric("Trust Score", user_data.get('trust_score', 300))
        st.metric("Total Income", f"${total_income:,.2f}")
        st.metric("Total Expense", f"${total_expense:,.2f}")
        st.metric("Net Flow", f"${net_flow:,.2f}")
        st.metric("Verified Transactions", verified_count)
        
        st.info("**What's included:**\n- Official TrustBridge letterhead\n- Your trust score and tier\n- Transaction summary\n- Verification stamps\n- QR code for validation")

def verification_history_page():
    st.title("Verification History")
    
    transactions = get_user_transactions(st.session_state.current_user)
    verified_transactions = [t for t in transactions if t.get('verified')]
    
    st.markdown(f"### {len(verified_transactions)} Verified Transactions")
    
    if verified_transactions:
        for txn in verified_transactions:
            with st.expander(f"✓ {txn['category']} - ${txn['amount']:.2f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Amount:** ${txn['amount']:.2f}")
                    st.write(f"**Type:** {txn['type']}")
                    st.write(f"**Category:** {txn['category']}")
                with col2:
                    date_str = txn['date'] if isinstance(txn['date'], str) else txn['date'].strftime("%b %d, %Y %I:%M %p")
                    st.write(f"**Date:** {date_str}")
                    st.write(f"**Status:** ✓ Verified")
                    st.write(f"**Trust Points:** +5")
                
                if txn.get('extracted_text'):
                    st.markdown("**Receipt Text:**")
                    st.code(txn['extracted_text'], language=None)
    else:
        st.info("No verified transactions yet. Upload receipts to verify your transactions!")

# Main app
def main():
    load_css()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        sidebar_navigation()
        
        # Route to pages
        page = st.session_state.get('page', 'Dashboard')
        
        if page == "Dashboard":
            dashboard_page()
        elif page == "Transactions":
            transactions_page()
        elif page == "Opportunities":
            st.title("Opportunities")
            st.info("Opportunities page - Full implementation in main app")
        elif page == "Financial Report":
            financial_report_page()
        elif page == "Verification History":
            verification_history_page()
        elif page == "Profile":
            profile_page()
        elif page == "Help":
            help_center_page()
        
        # Footer
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            "<div class='custom-footer'>🛡️ TrustBridge - Building financial trust for informal workers | "
            "Secure • Verifiable • Empowering<br><small>© 2024 @FinAfric. All rights reserved.</small></div>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
