import streamlit as st
import pandas as pd
import smtplib
import ssl
import time
import os
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# --- 1. SETTINGS & CONSTANTS ---
st.set_page_config(page_title="Data Science Outreach Pro", layout="wide")
LOG_FILE = "sent_emails_log.csv"
ROWS_PER_PAGE = 50


# --- 2. CACHED DATA LOADING ---
@st.cache_data
def load_and_clean_data(file):
    """Cleans Excel data for professional outreach."""
    df = pd.read_excel(file)
    # Remove leading numbers from PDF-to-Excel conversion (e.g., '1 Akanksha' -> 'Akanksha')
    df['Name'] = df['Name'].astype(str).str.replace(r'^\d+\s*', '', regex=True)
    df['First_Name'] = df['Name'].str.split().str[0]
    df['Company'] = df['Company'].astype(str).str.strip()
    df['Email'] = df['Email'].astype(str).str.strip().str.lower()
    return df


@st.cache_resource
def get_ssl_context():
    return ssl.create_default_context()


def load_sent_log():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=['email', 'timestamp', 'status'])


def save_to_log(email, status="Sent"):
    new_entry = pd.DataFrame([[email, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status]],
                             columns=['email', 'timestamp', 'status'])
    new_entry.to_csv(LOG_FILE, mode='a', header=not os.path.exists(LOG_FILE), index=False)


# --- 3. SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("🔑 Credentials")
    sender_email = st.text_input("Your Gmail", value="shindepratik447@gmail.com")
    app_password = st.text_input("App Password", type="password", help="Use a 16-character Google App Password.")

    st.header("📄 Attachments")
    resume_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

    st.header("⚙️ Advanced Controls")
    start_from_row = st.number_input("Start from Row # (on current page)", min_value=1, value=1)
    delay_seconds = st.slider("Delay between emails (sec)", 2, 10, 4)

    if st.button("🗑️ Reset All Progress"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
            st.cache_data.clear()
            st.rerun()

# --- 4. DATA PROCESSING & PAGINATION ---
st.title("📧 ML & Data Science Outreach Tracker")
uploaded_file = st.file_uploader("Upload Excel Contact List", type=["xlsx"])

if uploaded_file:
    full_df = load_and_clean_data(uploaded_file)
    log_df = load_sent_log()
    sent_emails = log_df['email'].tolist()

    # Apply tracking status to the main dataframe
    full_df['Status'] = full_df['Email'].apply(lambda x: "✅ Sent" if x in sent_emails else "⏳ Pending")

    # Global Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Contacts", len(full_df))
    c2.metric("Sent (Lifetime)", len(sent_emails))
    c3.metric("Remaining", len(full_df) - len(sent_emails))

    # Pagination Logic
    total_pages = math.ceil(len(full_df) / ROWS_PER_PAGE)
    current_page = st.select_slider("Select Page Range", options=list(range(1, total_pages + 1)), value=1)

    start_idx = (current_page - 1) * ROWS_PER_PAGE
    page_df = full_df.iloc[start_idx: start_idx + ROWS_PER_PAGE]

    st.subheader(f"Current View: Page {current_page}")
    st.dataframe(page_df[['Name', 'Email', 'Company', 'Status']], width="stretch")

    # --- 5. PROGRESS DASHBOARD ---
    st.divider()
    st.subheader("🚀 Live Sending Progress")
    col_m1, col_m2, col_m3 = st.columns(3)
    metric_sent = col_m1.empty()
    metric_todo = col_m2.empty()
    metric_time = col_m3.empty()

    p_bar = st.progress(0)
    status_msg = st.empty()

    # --- 6. EXECUTION LOGIC ---
    if st.button("Start/Resume Batch Sending"):
        # Filter for pending rows and apply row offset
        to_send = page_df[page_df['Status'] == "⏳ Pending"].iloc[start_from_row - 1:]

        if to_send.empty:
            st.warning("No pending emails found for this selection.")
        elif not app_password:
            st.error("Please provide your App Password in the sidebar.")
        else:
            context = get_ssl_context()
            total_batch = len(to_send)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, app_password)

                    for i, (idx, row) in enumerate(to_send.iterrows()):
                        # Calculate Metrics
                        current_num = i + 1
                        remaining = total_batch - current_num
                        etr = remaining * delay_seconds

                        metric_sent.metric("Sent in Batch", current_num)
                        metric_todo.metric("Remaining", remaining)
                        metric_time.metric("Est. Time Left", f"{etr}s")

                        # Prepare Personalized Email
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = row['Email']
                        msg['Subject'] = f"Data Science / ML Engineer Application - {row['Company']}"

                        body = f"""Dear {row['First_Name']},

I am writing to express my strong interest in joining the data team at {row['Company']} as a Data Scientist or Machine Learning Engineer.

I have a solid foundation in Python, SQL, and Statistics, along with hands-on experience in building ML models. I'm eager to apply my analytical skills to contribute to {row['Company']}.

Please find my resume attached. I'd welcome the opportunity to discuss my background with you.

Best regards,
Pratik Shinde
https://github.com/PratikS447
"""
                        msg.attach(MIMEText(body, 'plain'))

                        if resume_file:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(resume_file.getvalue())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition", f"attachment; filename=Pratik_Shinde_Resume.pdf")
                            msg.attach(part)

                        # Send and Log
                        server.send_message(msg)
                        save_to_log(row['Email'], "Sent")

                        # Update Visuals
                        p_bar.progress(current_num / total_batch)
                        status_msg.info(f"✅ Sent to {row['First_Name']} at {row['Company']}")

                        if remaining > 0:
                            time.sleep(delay_seconds)

                st.success("Batch Completed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# --- 7. EXPORT LOGS ---
st.divider()
final_log = load_sent_log()
if not final_log.empty:
    st.subheader("📥 Download Activity Report")
    csv_data = final_log.to_csv(index=False).encode('utf-8')
    st.download_button("Download Success/Failure Log", csv_data, "outreach_report.csv", "text/csv")