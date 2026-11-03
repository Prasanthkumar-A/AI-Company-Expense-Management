
import os
import streamlit as st
import pandas as pd
import plotly.express as px

import database as db
import expense_analysis as analysis
import rag_engine as rag


# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Company Expense Management",
    page_icon="💼",
    layout="wide"
)

# Create database automatically
db.create_database()

# Create document folder automatically
os.makedirs("documents", exist_ok=True)


# ==========================================
# 2. CUSTOM DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #f4f6fa;
}

[data-testid="stSidebar"] {
    background-color: #101b2d;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {
    color: #172b4d;
    font-size: 32px;
    font-weight: 800;
}

.subtitle {
    color: #64748b;
    font-size: 15px;
}

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 12px;
}

.stButton button {
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("💼 Expense AI")

st.sidebar.caption("Company Finance Intelligence")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Add Expense",
        "Expense Records",
        "Expense Analysis",
        "Document Management",
        "AI Assistant",
        "Policy Checker",
        "Reports"
    ]
)

st.sidebar.divider()

st.sidebar.info(
    "AI-Powered Company Expense "
    "Management and Analysis System"
)


# Get expense data
df = db.get_all_expenses()


# ==========================================
# 4. DASHBOARD
# ==========================================

if page == "Dashboard":

    st.markdown(
        '<div class="main-title">Company Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Financial overview and company spending</div>',
        unsafe_allow_html=True
    )

    st.write("")

    total = analysis.calculate_total_expenses(df)

    count = len(df)

    average = df["amount"].mean() if not df.empty else 0

    departments = (
        df["department"].nunique()
        if not df.empty else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Expenses",
        f"₹{total:,.2f}"
    )

    col2.metric(
        "Expense Records",
        count
    )

    col3.metric(
        "Average Expense",
        f"₹{average:,.2f}"
    )

    col4.metric(
        "Departments",
        departments
    )

    st.divider()

    if df.empty:

        st.info(
            "No expense records available. "
            "Go to Add Expense to enter your first record."
        )

    else:

        left, right = st.columns(2)

        with left:

            st.subheader("Department-wise Expenses")

            dept_data = analysis.department_analysis(df)

            fig = px.bar(
                dept_data,
                x="department",
                y="amount",
                color="department",
                title="Department Spending"
            )

            fig.update_layout(
                showlegend=False,
                xaxis_title="Department",
                yaxis_title="Amount (₹)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with right:

            st.subheader("Category-wise Expenses")

            category_data = analysis.category_analysis(df)

            fig = px.pie(
                category_data,
                names="category",
                values="amount",
                hole=0.45,
                title="Expense Distribution"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader("Monthly Expense Trend")

        monthly_data = analysis.monthly_analysis(df)

        if not monthly_data.empty:

            fig = px.line(
                monthly_data,
                x="month",
                y="amount",
                markers=True,
                title="Monthly Spending Trend"
            )

            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Amount (₹)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.subheader("Recent Expense Records")

        st.dataframe(
            df.head(5),
            use_container_width=True,
            hide_index=True
        )


# ==========================================
# 5. ADD EXPENSE
# ==========================================

elif page == "Add Expense":

    st.title("➕ Add New Expense")

    st.write(
        "Enter employee and expense details below."
    )

    with st.form("expense_form"):

        col1, col2 = st.columns(2)

        with col1:

            employee_name = st.text_input(
                "Employee Name"
            )

            employee_id = st.text_input(
                "Employee ID"
            )

            department = st.selectbox(
                "Department",
                [
                    "IT",
                    "HR",
                    "Finance",
                    "Marketing",
                    "Sales",
                    "Operations"
                ]
            )

        with col2:

            category = st.selectbox(
                "Expense Category",
                [
                    "Travel",
                    "Food",
                    "Accommodation",
                    "Office Supplies",
                    "Transport",
                    "Internet",
                    "Software",
                    "Other"
                ]
            )

            amount = st.number_input(
                "Expense Amount (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0
            )

            expense_date = st.date_input(
                "Expense Date"
            )

        description = st.text_area(
            "Expense Description"
        )

        submitted = st.form_submit_button(
            "Save Expense",
            use_container_width=True
        )

        if submitted:

            if not employee_name.strip():

                st.error("Enter employee name.")

            elif not employee_id.strip():

                st.error("Enter employee ID.")

            elif amount <= 0:

                st.error("Amount must be greater than zero.")

            else:

                db.add_expense(
                    employee_name.strip(),
                    employee_id.strip(),
                    department,
                    category,
                    amount,
                    expense_date.isoformat(),
                    description
                )

                st.success(
                    "Expense added successfully!"
                )

                st.rerun()


# ==========================================
# 6. EXPENSE RECORDS
# ==========================================

elif page == "Expense Records":

    st.title("📋 Expense Records")

    df = db.get_all_expenses()

    if df.empty:

        st.info("No records found.")

    else:

        search = st.text_input(
            "Search by employee name or department"
        )

        filtered = df.copy()

        if search:

            mask = (
                filtered["employee_name"]
                .str.contains(search, case=False, na=False)
                |
                filtered["department"]
                .str.contains(search, case=False, na=False)
            )

            filtered = filtered[mask]

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Edit or Delete Expense")

        expense_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select Expense ID",
            expense_ids
        )

        selected = df[
            df["id"] == selected_id
        ].iloc[0]

        with st.form("edit_expense_form"):

            edit_name = st.text_input(
                "Employee Name",
                value=str(selected["employee_name"])
            )

            edit_employee_id = st.text_input(
                "Employee ID",
                value=str(selected["employee_id"])
            )

            edit_department = st.selectbox(
                "Department",
                [
                    "IT",
                    "HR",
                    "Finance",
                    "Marketing",
                    "Sales",
                    "Operations"
                ],
                index=[
                    "IT", "HR", "Finance",
                    "Marketing", "Sales", "Operations"
                ].index(selected["department"])
            )

            categories = [
                "Travel",
                "Food",
                "Accommodation",
                "Office Supplies",
                "Transport",
                "Internet",
                "Software",
                "Other"
            ]

            edit_category = st.selectbox(
                "Category",
                categories,
                index=categories.index(selected["category"])
            )

            edit_amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(selected["amount"])
            )

            edit_date = st.date_input(
                "Expense Date",
                value=pd.to_datetime(
                    selected["expense_date"]
                ).date()
            )

            edit_description = st.text_area(
                "Description",
                value=str(selected["description"] or "")
            )

            update_button = st.form_submit_button(
                "Update Expense"
            )

            if update_button:

                if not edit_name.strip() or not edit_employee_id.strip():

                    st.error("Employee details cannot be empty.")

                elif edit_amount <= 0:

                    st.error("Amount must be greater than zero.")

                else:

                    db.update_expense(
                        int(selected_id),
                        edit_name.strip(),
                        edit_employee_id.strip(),
                        edit_department,
                        edit_category,
                        edit_amount,
                        edit_date.isoformat(),
                        edit_description
                    )

                    st.success("Expense updated.")

                    st.rerun()

        if st.button(
            "🗑️ Delete Selected Expense",
            type="secondary"
        ):

            st.session_state["confirm_delete"] = int(selected_id)

        if st.session_state.get("confirm_delete") == int(selected_id):

            st.warning(
                "Are you sure you want to delete this expense?"
            )

            yes, no = st.columns(2)

            with yes:

                if st.button("Confirm Delete"):

                    db.delete_expense(int(selected_id))

                    st.session_state.pop("confirm_delete", None)

                    st.success("Expense deleted.")

                    st.rerun()

            with no:

                if st.button("Cancel Delete"):

                    st.session_state.pop("confirm_delete", None)

                    st.rerun()


# ==========================================
# 7. EXPENSE ANALYSIS
# ==========================================

elif page == "Expense Analysis":

    st.title("📊 Expense Analysis")

    df = db.get_all_expenses()

    if df.empty:

        st.info("Add expenses to view analysis.")

    else:

        st.subheader("Financial Summary")

        st.text(
            analysis.generate_insights(df)
        )

        st.divider()

        st.subheader("Department Comparison")

        dept = analysis.department_analysis(df)

        fig = px.bar(
            dept,
            x="department",
            y="amount",
            color="department",
            title="Department Expense Comparison"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Monthly Comparison")

        monthly = analysis.monthly_analysis(df)

        fig = px.bar(
            monthly,
            x="month",
            y="amount",
            title="Monthly Expense Comparison"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader("Potentially Unusual Expenses")

        unusual = analysis.find_unusual_expenses(df)

        if unusual.empty:

            st.success("No expenses crossed the demonstration threshold.")

        else:

            st.warning(
                "These expenses are more than twice the overall average. "
                "They require human review, not an automatic fraud finding."
            )

            st.dataframe(
                unusual,
                use_container_width=True,
                hide_index=True
            )


# ==========================================
# 8. DOCUMENT MANAGEMENT
# ==========================================

elif page == "Document Management":

    st.title("📁 Company Document Management")

    st.write(
        "Upload company expense policies and financial documents."
    )

    uploaded_file = st.file_uploader(
        "Upload PDF or TXT Document",
        type=["pdf", "txt"]
    )

    if uploaded_file is not None:

        if st.button("Process and Index Document"):

            file_path = os.path.join(
                "documents",
                os.path.basename(uploaded_file.name)
            )

            with open(file_path, "wb") as file:

                file.write(uploaded_file.getvalue())

            try:

                with st.spinner(
                    "Extracting text and generating embeddings..."
                ):

                    chunks = rag.process_document(file_path)

                st.success(
                    f"Document processed successfully! "
                    f"{chunks} chunks indexed."
                )

            except Exception as error:

                st.error(
                    f"Document processing failed: {error}"
                )

    st.divider()

    st.subheader("Indexed Document Information")

    st.metric(
        "Total Indexed Text Chunks",
        rag.get_document_count()
    )

    if os.path.exists("documents"):

        files = os.listdir("documents")

        st.write("Uploaded files:")

        if files:

            for filename in files:

                st.write(f"📄 {filename}")

        else:

            st.info("No documents uploaded yet.")


# ==========================================
# 9. AI ASSISTANT
# ==========================================

elif page == "AI Assistant":

    st.title("🤖 AI Expense Assistant")

    st.write(
        "Ask questions about your uploaded company documents."
    )

    st.caption(
        "This assistant uses RAG to retrieve document information "
        "before generating answers."
    )

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []

    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    question = st.chat_input(
        "Ask about company expense policies..."
    )

    if question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):

            st.markdown(question)

        with st.chat_message("assistant"):

            try:

                with st.spinner(
                    "Searching company documents and generating answer..."
                ):

                    answer, sources = rag.ask_ai(
                        question,
                        db.get_all_expenses()
                    )

                st.markdown(answer)

                if sources:

                    with st.expander("View retrieved sources"):

                        for source in sources:

                            st.write(
                                f"**{source['source']}** "
                                f"— Chunk {source['chunk']}"
                            )

                            st.write(source["text"])

                            st.divider()

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:

                st.error(
                    f"AI assistant error: {error}"
                )

                st.info(
                    "Check whether Ollama is running and "
                    "whether llama3.2 is installed."
                )

    if st.button("Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()


# ==========================================
# 10. POLICY CHECKER
# ==========================================

elif page == "Policy Checker":

    st.title("🛡️ Expense Policy Checker")

    st.write(
        "Check a submitted expense against the uploaded company policies."
    )

    with st.form("policy_form"):

        employee = st.text_input(
            "Employee Name"
        )

        expense_type = st.selectbox(
            "Expense Type",
            [
                "Hotel Accommodation",
                "Food",
                "Travel",
                "Transport",
                "Office Supplies",
                "Other"
            ]
        )

        expense_amount = st.number_input(
            "Claimed Amount (₹)",
            min_value=0.0,
            value=0.0
        )

        policy_description = st.text_area(
            "Additional Details",
            placeholder="Example: One night hotel stay for business travel."
        )

        check_button = st.form_submit_button(
            "Check Expense Policy"
        )

        if check_button:

            if not employee.strip() or expense_amount <= 0:

                st.error(
                    "Enter employee name and a valid expense amount."
                )

            else:

                question = f"""
                Check this expense against the company policies.

                Employee: {employee}

                Expense Type: {expense_type}

                Claimed Amount: Rs. {expense_amount}

                Details: {policy_description}

                Explain:
                1. Relevant company policy.
                2. Whether the expense appears compliant.
                3. Any amount exceeding the stated policy limit.
                4. Whether more information is required.

                Do not invent a policy limit.
                If no relevant policy exists, say so.
                """

                try:

                    with st.spinner(
                        "Checking company policy documents..."
                    ):

                        answer, sources = rag.ask_ai(question)

                    st.subheader("Policy Check Result")

                    st.write(answer)

                    if sources:

                        with st.expander("View policy sources"):

                            for source in sources:

                                st.write(
                                    f"{source['source']} "
                                    f"- Chunk {source['chunk']}"
                                )

                except Exception as error:

                    st.error(
                        f"Policy check failed: {error}"
                    )


# ==========================================
# 11. REPORTS
# ==========================================

elif page == "Reports":

    st.title("📄 Expense Reports")

    df = db.get_all_expenses()

    if df.empty:

        st.info("No expense data available.")

    else:

        st.subheader("Company Expense Report")

        total = df["amount"].sum()

        st.metric(
            "Total Company Expenses",
            f"₹{total:,.2f}"
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇️ Download Expense Report (CSV)",
            data=csv_data,
            file_name="company_expense_report.csv",
            mime="text/csv",
            use_container_width=True
        )


# ==========================================
# 12. FOOTER
# ==========================================

st.sidebar.divider()

st.sidebar.caption(
    "AI Company Expense Management System | 2026"
)
