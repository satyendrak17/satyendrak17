import streamlit as st
import pandas as pd
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64
import requests
import json
import os

# Set page config
st.set_page_config(
    page_title="Radhe Jewellers",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .bill-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
    }
    
    .bill-header {
        text-align: center;
        color: #2E86AB;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .success-message {
        color: #28a745;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .error-message {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #2E86AB;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #1d5f85;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bill_data' not in st.session_state:
    st.session_state.bill_data = None
if 'pdf_buffer' not in st.session_state:
    st.session_state.pdf_buffer = None

def calculate_total_amount(weight, rate, billing_price):
    """Calculate total amount based on weight, rate, and billing price"""
    try:
        base_amount = float(weight) * float(rate)
        total_amount = base_amount + float(billing_price)
        return base_amount, total_amount
    except ValueError:
        return 0, 0

def generate_bill_data(form_data):
    """Generate structured bill data"""
    base_amount, total_amount = calculate_total_amount(
        form_data['weight'], 
        form_data['rate'], 
        form_data['billing_price']
    )
    
    bill_data = {
        'bill_number': f"BILL-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'billing_date': form_data['billing_date'],
        'shopkeeper_name': form_data['shopkeeper_name'],
        'customer_name': form_data['customer_name'],
        'customer_mobile': form_data['customer_mobile'],
        'customer_address': form_data['customer_address'],
        'gst_number': form_data['gst_number'] if form_data['gst_number'] else "N/A",
        'metal_type': form_data['metal_type'],
        'weight': form_data['weight'],
        'rate': form_data['rate'],
        'base_amount': base_amount,
        'billing_price': form_data['billing_price'],
        'total_amount': total_amount,
        'gst_amount': total_amount * 0.03 if form_data['gst_number'] else 0,  # 3% GST if GST number provided
        'final_amount': total_amount * 1.03 if form_data['gst_number'] else total_amount
    }
    
    return bill_data

def generate_pdf(bill_data):
    """Generate PDF bill"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#2E86AB')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#2E86AB')
    )
    
    # Build PDF content
    story = []
    
    # Title
    title = Paragraph("Radhe Jewellers,", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Shop and bill details
    shop_info = f"""
    <b>Shopkeeper:</b> {bill_data['shopkeeper_name']}<br/>
    <b>Bill Number:</b> {bill_data['bill_number']}<br/>
    <b>Date:</b> {bill_data['billing_date']}<br/>
    <b>GST Number:</b> {bill_data['gst_number']}
    """
    story.append(Paragraph(shop_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Customer details
    customer_heading = Paragraph("CUSTOMER DETAILS", heading_style)
    story.append(customer_heading)
    
    customer_info = f"""
    <b>Name:</b> {bill_data['customer_name']}<br/>
    <b>Mobile:</b> {bill_data['customer_mobile']}<br/>
    <b>Address:</b> {bill_data['customer_address']}
    """
    story.append(Paragraph(customer_info, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Item details
    item_heading = Paragraph("ITEM DETAILS", heading_style)
    story.append(item_heading)
    
    # Create table for item details
    item_data = [
        ['Description', 'Weight (grams)', 'Rate per gram', 'Amount'],
        [f'{bill_data["metal_type"]} Jewellery', f'{bill_data["weight"]}g', f'₹{bill_data["rate"]}', f'₹{bill_data["base_amount"]:.2f}'],
        ['Additional Charges', '', '', f'₹{bill_data["billing_price"]}'],
        ['Subtotal', '', '', f'₹{bill_data["total_amount"]:.2f}']
    ]
    
    if bill_data['gst_amount'] > 0:
        item_data.append(['GST (3%)', '', '', f'₹{bill_data["gst_amount"]:.2f}'])
    
    item_data.append(['Total Amount', '', '', f'₹{bill_data["final_amount"]:.2f}'])
    
    item_table = Table(item_data, colWidths=[3*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(item_table)
    story.append(Spacer(1, 30))
    
    # Footer
    footer = Paragraph("Thank you for your business!", styles['Normal'])
    story.append(footer)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def send_whatsapp_message(phone_number, pdf_buffer, bill_data):
    """Send WhatsApp message with PDF attachment"""
    try:
        from whatsapp_integration import WhatsAppIntegration, display_whatsapp_setup_guide
        
        # Check if any WhatsApp credentials are configured
        providers = ["twilio", "whatsapp_business", "ultramsg"]
        configured_provider = None
        
        for provider in providers:
            whatsapp = WhatsAppIntegration(provider=provider)
            if provider == "twilio" and all([whatsapp.config.get('account_sid'), whatsapp.config.get('auth_token')]):
                configured_provider = provider
                break
            elif provider == "whatsapp_business" and all([whatsapp.config.get('access_token'), whatsapp.config.get('phone_number_id')]):
                configured_provider = provider
                break
            elif provider == "ultramsg" and all([whatsapp.config.get('token'), whatsapp.config.get('instance_id')]):
                configured_provider = provider
                break
        
        if configured_provider:
            # Use the configured provider
            whatsapp = WhatsAppIntegration(provider=configured_provider)
            pdf_buffer.seek(0)
            success = whatsapp.send_bill(phone_number, pdf_buffer.getvalue(), bill_data)
            return success
        else:
            # Show setup guide if no provider is configured
            st.warning("⚠️ WhatsApp integration not configured")
            
            with st.expander("📱 WhatsApp Setup Guide", expanded=True):
                display_whatsapp_setup_guide()
            
            st.info("Configure any of the above providers to enable WhatsApp functionality.")
            return False
    
    except ImportError:
        st.error("❌ WhatsApp integration module not found")
        return False
    except Exception as e:
        st.error(f"❌ Error sending WhatsApp message: {str(e)}")
        return False

def main():
    st.markdown('<h1 class="main-header">💍 Radhe Jewellers</h1>', unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        default_shopkeeper = st.text_input("Default Shopkeeper Name", value="Jewellery Shop Owner")
        default_gst = st.text_input("Default GST Number", value="")
        
        st.header("📊 Quick Stats")
        st.info("This section can show daily/monthly statistics")
    
    # Main form
    with st.form("billing_form"):
        st.subheader("📝 Billing Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Shop Details**")
            shopkeeper_name = st.text_input("Shopkeeper Name*", value=default_shopkeeper)
            gst_number = st.text_input("GST Number (Optional)", value=default_gst)
            
            st.markdown("**Customer Details**")
            customer_name = st.text_input("Customer Name*")
            customer_mobile = st.text_input("Customer Mobile Number*", placeholder="Enter 10-digit mobile number")
            customer_address = st.text_area("Customer Address*", height=100)
        
        with col2:
            st.markdown("**Item Details**")
            metal_type = st.selectbox("Metal Type", ["Gold", "Silver"])
            weight = st.number_input("Weight (grams)*", min_value=0.0, step=0.1, format="%.2f")
            rate = st.number_input(f"{metal_type} Rate per gram (₹)*", min_value=0.0, step=0.01, format="%.2f")
            billing_price = st.number_input("Additional Charges (₹)*", min_value=0.0, step=0.01, format="%.2f")
            
            st.markdown("**Billing Date**")
            billing_date = st.date_input("Billing Date", value=datetime.now().date())
        
        # Calculate preview
        if weight and rate and billing_price:
            base_amount, total_amount = calculate_total_amount(weight, rate, billing_price)
            gst_amount = total_amount * 0.03 if gst_number else 0
            final_amount = total_amount + gst_amount
            
            st.markdown("---")
            st.subheader("💰 Amount Preview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Base Amount", f"₹{base_amount:.2f}")
            with col2:
                st.metric("Additional Charges", f"₹{billing_price:.2f}")
            with col3:
                st.metric("GST (3%)", f"₹{gst_amount:.2f}" if gst_number else "₹0.00")
            with col4:
                st.metric("Final Amount", f"₹{final_amount:.2f}")
        
        # Form submission
        submitted = st.form_submit_button("🧾 Generate Bill", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not all([shopkeeper_name, customer_name, customer_mobile, customer_address, weight, rate, billing_price]):
                st.error("❌ Please fill in all required fields marked with *")
            elif len(customer_mobile) != 10 or not customer_mobile.isdigit():
                st.error("❌ Please enter a valid 10-digit mobile number")
            else:
                # Generate bill
                form_data = {
                    'shopkeeper_name': shopkeeper_name,
                    'gst_number': gst_number,
                    'customer_name': customer_name,
                    'customer_mobile': customer_mobile,
                    'customer_address': customer_address,
                    'metal_type': metal_type,
                    'weight': weight,
                    'rate': rate,
                    'billing_price': billing_price,
                    'billing_date': billing_date.strftime('%Y-%m-%d')
                }
                
                st.session_state.bill_data = generate_bill_data(form_data)
                st.session_state.pdf_buffer = generate_pdf(st.session_state.bill_data)
                
                st.success("✅ Bill generated successfully!")
                st.rerun()
    
    # Display generated bill
    if st.session_state.bill_data:
        st.markdown("---")
        st.markdown('<div class="bill-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="bill-header">📄 Generated Bill</h2>', unsafe_allow_html=True)
        
        bill_data = st.session_state.bill_data
        
        # Display bill details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Bill Details**")
            st.write(f"**Bill Number:** {bill_data['bill_number']}")
            st.write(f"**Date:** {bill_data['billing_date']}")
            st.write(f"**Shopkeeper:** {bill_data['shopkeeper_name']}")
            st.write(f"**GST Number:** {bill_data['gst_number']}")
            
            st.markdown("**Customer Details**")
            st.write(f"**Name:** {bill_data['customer_name']}")
            st.write(f"**Mobile:** {bill_data['customer_mobile']}")
            st.write(f"**Address:** {bill_data['customer_address']}")
        
        with col2:
            st.markdown("**Item Details**")
            st.write(f"**Metal Type:** {bill_data['metal_type']}")
            st.write(f"**Weight:** {bill_data['weight']}g")
            st.write(f"**Rate:** ₹{bill_data['rate']}/g")
            st.write(f"**Base Amount:** ₹{bill_data['base_amount']:.2f}")
            st.write(f"**Additional Charges:** ₹{bill_data['billing_price']:.2f}")
            if bill_data['gst_amount'] > 0:
                st.write(f"**GST (3%):** ₹{bill_data['gst_amount']:.2f}")
            st.write(f"**Final Amount:** ₹{bill_data['final_amount']:.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Download PDF", use_container_width=True):
                st.session_state.pdf_buffer.seek(0)
                st.download_button(
                    label="💾 Save Bill PDF",
                    data=st.session_state.pdf_buffer.getvalue(),
                    file_name=f"bill_{bill_data['bill_number']}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            if st.button("👁️ Preview PDF", use_container_width=True):
                st.session_state.pdf_buffer.seek(0)
                base64_pdf = base64.b64encode(st.session_state.pdf_buffer.getvalue()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
        
    
    # Clear bill button
    if st.session_state.bill_data:
        if st.button("🗑️ Clear Bill", use_container_width=True):
            st.session_state.bill_data = None
            st.session_state.pdf_buffer = None
            st.rerun()

if __name__ == "__main__":
    main() 