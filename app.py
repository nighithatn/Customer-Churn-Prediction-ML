import streamlit as st
import pandas as pd
from joblib import load
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

# ===============================
# Page Configuration
# ===============================
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide"
)

# ===============================
# Styling
# ===============================
st.markdown("""
<style>
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ===============================
# Load Model & Feature List
# ===============================
model = load("final_churn_model.joblib")
feature_list = load("final_feature_list.joblib")

# ===============================
# PDF Generator Function
# ===============================
def generate_pdf(input_data, prediction, probability, risk):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Customer Churn Prediction Report")

    y -= 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Customer Input Summary")

    y -= 20
    c.setFont("Helvetica", 11)
    for k, v in input_data.items():
        c.drawString(60, y, f"{k}: {v}")
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Prediction Result")

    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(60, y, f"Prediction: {prediction}")
    y -= 18
    c.drawString(60, y, f"Churn Probability: {probability:.2%}")
    y -= 18
    c.drawString(60, y, f"Risk Level: {risk}")

    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Recommended Business Action")

    y -= 20
    c.setFont("Helvetica", 11)
    if probability >= 0.6:
        c.drawString(60, y, "• Offer discounts or retention plans.")
    else:
        c.drawString(60, y, "• Maintain service quality and engagement.")

    y -= 40
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(
        50,
        y,
        "Generated using a Machine Learning based Customer Churn Prediction System"
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# ===============================
# Title Section
# ===============================
st.markdown(
    "<h1 style='text-align:center;'>📊 Customer Churn Prediction Dashboard</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;'>Predict whether a customer is likely to churn based on service and billing details</p>",
    unsafe_allow_html=True
)
st.divider()

# ===============================
# Sidebar Inputs
# ===============================
st.sidebar.header("🔧 Customer Information")

tenure = st.sidebar.slider("Tenure (months)", 0, 72, 12)

contract = st.sidebar.selectbox(
    "Contract Type",
    ["Month-to-month", "One year", "Two year"]
)

internet_service = st.sidebar.selectbox(
    "Internet Service",
    ["DSL", "Fiber optic", "No"]
)

payment_method = st.sidebar.selectbox(
    "Payment Method",
    ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
)

monthly_charges = st.sidebar.slider("Monthly Charges ($)", 0, 150, 70)
total_charges = st.sidebar.slider("Total Charges ($)", 0, 10000, 2000)

# ===============================
# Build Input DataFrame (RAW)
# ===============================
input_df = pd.DataFrame([{
    "tenure": tenure,
    "Contract": contract,
    "InternetService": internet_service,
    "PaymentMethod": payment_method,
    "MonthlyCharges": monthly_charges,
    "TotalCharges": total_charges
}])

# ===============================
# One-Hot Encoding & Alignment
# ===============================
input_df = pd.get_dummies(input_df)
input_df = input_df.reindex(columns=feature_list, fill_value=0)

# ===============================
# Prediction Section
# ===============================
st.subheader("🔮 Prediction Result")

if st.button("Predict Churn"):
    prediction = model.predict(input_df)
    probability = model.predict_proba(input_df)[0][1]

    # Risk Level
    if probability < 0.4:
        risk = "🟢 Low Risk"
    elif probability < 0.7:
        risk = "🟠 Medium Risk"
    else:
        risk = "🔴 High Risk"

    col1, col2 = st.columns(2)

    with col1:
        if prediction[0] == 1:
            st.error("⚠️ Customer is likely to churn")
        else:
            st.success("✅ Customer is likely to stay")
        st.markdown(f"### Risk Level: **{risk}**")

    with col2:
        st.metric("Churn Probability", f"{probability:.2%}")
        st.progress(int(probability * 100))

    # ===============================
    # Key Risk Indicators
    # ===============================
    st.subheader("🧠 Key Risk Indicators")

    if tenure < 12:
        st.write("• Short tenure increases churn risk")
    if contract == "Month-to-month":
        st.write("• Month-to-month contracts have higher churn")
    if monthly_charges > 70:
        st.write("• Higher monthly charges increase churn risk")
    if payment_method == "Electronic check":
        st.write("• Electronic check payment method is linked to higher churn")

    # ===============================
    # Business Recommendation
    # ===============================
    st.subheader("📌 Recommended Business Action")

    if probability >= 0.6:
        st.warning("Offer personalized discounts, retention plans, or proactive support.")
    else:
        st.success("Customer appears stable. Maintain service quality.")

    # ===============================
    # PDF Download
    # ===============================
    pdf_inputs = {
        "Tenure (months)": tenure,
        "Contract Type": contract,
        "Internet Service": internet_service,
        "Payment Method": payment_method,
        "Monthly Charges ($)": monthly_charges,
        "Total Charges ($)": total_charges
    }

    pdf_buffer = generate_pdf(
        pdf_inputs,
        "Likely to Churn" if prediction[0] == 1 else "Likely to Stay",
        probability,
        risk
    )

    st.download_button(
        label="📄 Download Prediction Report (PDF)",
        data=pdf_buffer,
        file_name="customer_churn_prediction_report.pdf",
        mime="application/pdf"
    )

# ===============================
# Explanation Section
# ===============================
st.divider()
st.subheader("ℹ️ Model Explanation")

st.write("""
- This prediction is generated using the **final machine learning model** selected after evaluating multiple classifiers.
- The model applies **one-hot encoding**, identical to the training pipeline.
- Important churn drivers include **tenure, contract type, monthly charges, and payment method**.
""")

st.info("This Streamlit application demonstrates real-time customer churn prediction using a trained ML model.")

