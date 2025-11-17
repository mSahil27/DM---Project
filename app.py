import streamlit as st
import pandas as pd

# --- PART 1: LOGIC ENGINE ---
def evaluate_loan(p_credit, q_income, r_criminal, s_high_amt):
    """
    P = Good Credit | Q = Stable Income | R = Criminal Record | S = High Loan
    """
    approve = False
    reject = False
    review = False
    
    # Rule 1: R -> Reject (Criminal record overrides everything)
    if r_criminal:
        reject = True
    # Rule 2: (S AND NOT Q) -> Reject (High loan with no income)
    elif s_high_amt and not q_income:
        reject = True
    # Rule 3: (P AND Q) -> Approve (Good credit and income)
    elif p_credit and q_income:
        approve = True
        # Rule 4: (S AND P) -> Review (High loan needs review even if approved)
        if s_high_amt:
            review = True
            approve = False # Review overrides auto-approval
    else:
        reject = True
    return approve, review, reject

# --- PART 2: TRUTH TABLE GENERATOR ---
@st.cache_data
def get_truth_table_data():
    """ Generates the truth table data as a Pandas DataFrame """
    table_data = []
    inputs = [False, True]
    for P in inputs:
        for Q in inputs:
            for R in inputs:
                for S in inputs:
                    app, rev, rej = evaluate_loan(P, Q, R, S)
                    table_data.append({
                        "Credit(P)": "1" if P else "0",
                        "Income(Q)": "1" if Q else "0",
                        "Crim(R)": "1" if R else "0",
                        "High(S)": "1" if S else "0",
                        "Approve": "YES" if app else "",
                        "Review": "YES" if rev else "",
                        "Reject": "YES" if rej else ""
                    })
    return pd.DataFrame(table_data)

# --- PART 3: STREAMLIT UI ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN PAGE ---
if not st.session_state.logged_in:
    st.set_page_config(page_title="Bank System Login")
    st.title("--- SECURE BANK SYSTEM LOGIN ---")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("❌ Access Denied. Invalid username or password.")

# --- MAIN APPLICATION PAGE ---
else:
    st.set_page_config(page_title="Bank Loan AI", layout="wide")
    
    st.sidebar.title(f"Welcome, admin!")
    page = st.sidebar.radio(
        "Navigation",
        ["Check Loan Eligibility", "View System Logic Proof"]
    )
    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- Page 1: Loan Checker ---
    if page == "Check Loan Eligibility":
        st.title("🏦 AI Loan Eligibility Checker")
        st.write("Enter the applicant's details below to get an instant decision.")
        col1, col2 = st.columns(2)
        with col1:
            p = st.radio("Good Credit Score (>700)?", ("Yes", "No"), index=1) == "Yes"
            q = st.radio("Stable Income Source?", ("Yes", "No"), index=1) == "Yes"
        with col2:
            r = st.radio("Criminal Record?", ("Yes", "No"), index=1) == "Yes"
            s = st.radio("High Loan Amount (>$50k)?", ("Yes", "No"), index=1) == "Yes"
        
        st.markdown("---")
        if st.button("Evaluate Loan Application", type="primary"):
            app, rev, rej = evaluate_loan(p, q, r, s)
            st.subheader("--- AI Decision Result ---")
            if rej: st.error("🔴 LOAN REJECTED")
            elif rev: st.warning("🟡 SENT FOR MANAGER REVIEW")
            elif app: st.success("🟢 LOAN APPROVED")

    # --- Page 2: Truth Table ---
    elif page == "View System Logic Proof":
        st.title("🔬 System Logic Proof (Full Truth Table)")
        st.write("This table shows the decision for all 16 possible applicant scenarios.")
        df = get_truth_table_data()
        st.dataframe(df, height=610, use_container_width=True)
