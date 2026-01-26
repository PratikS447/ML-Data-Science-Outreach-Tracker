# 📧 ML-Data-Science-Outreach-Tracker

This application is a professional automation tool designed to streamline personalized email outreach for Data Science and Machine Learning roles. It integrates a Streamlit UI with Python's SMTP capabilities to manage bulk applications with high precision.

---

## 🚀 How to Use

1. **Enter Credentials**: In the sidebar, enter your Gmail and your unique 16-character App Password.
2. **Upload Files**:
   * **Excel**: Upload your contact list containing `Name`, `Email`, and `Company`.
   * **Resume**: Upload your PDF resume to be included as an attachment.
3. **Set Delay**: Use the slider to set a 4–10 second delay between emails to avoid spam filters.
4. **Send**: Click **"Start/Resume Batch Sending"** to begin the process.

---

## 📊 Data Format Requirement

Your Excel file (`.xlsx`) must contain these exact headers for the script to function correctly:

| Name | Email | Company |
| :--- | :--- | :--- |
| John Doe | j.doe@example.com | TechCorp |
| Jane Smith | jane.s@datainc.io | DataFlow |

---

## ⚙️ Technical Architecture

The app follows a modular design to ensure reliability:
* **Frontend**: **Streamlit** provides a web interface for file handling and real-time metric visualization.
* **Data Processing**: **Pandas** manages the contact list, performing regex-based cleaning to remove numbering from names (e.g., converting "1 Pratik" to "Pratik").
* **Persistence**: A local `sent_emails_log.csv` acts as a database to prevent duplicate emails.
* **Networking**: Python's `smtplib` handles the secure SSL connection to Gmail's servers.

---

## 🛡️ Key Features & Safety

* **Duplicate Protection**: Before sending, the app cross-references the `Email` column with the log file.
* **Live Dashboard**: Monitor batch progress with a dynamic progress bar and estimated time remaining (ETR) calculations.
* **Batch Pagination**: Processes up to 50 rows at a time to prevent memory issues and allow for easy review.
* **Personalization**: The email template automatically extracts the `First_Name` from the `Name` column for a more natural greeting.

---

## 🛠️ Requirements & Installation

To run this project locally, install the dependencies using pip:

```bash
pip install streamlit pandas openpyxl