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
import zipfile
from io import BytesIO
import time

# Create bills directory if it doesn't exist
BILLS_DIR = "bills_history"
if not os.path.exists(BILLS_DIR):
    os.makedirs(BILLS_DIR)

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

def calculate_total_amount(weight, rate, making_charges_percent):
    """Calculate total amount based on weight, rate, and making charges percentage"""
    try:
        base_amount = float(weight) * float(rate)
        making_charges_amount = base_amount * (float(making_charges_percent) / 100)
        total_amount = base_amount + making_charges_amount
        return base_amount, making_charges_amount, total_amount
    except ValueError:
        return 0, 0, 0

def generate_bill_data(form_data):
    """Generate structured bill data"""
    base_amount, making_charges_amount, total_amount = calculate_total_amount(
        form_data['weight'], 
        form_data['rate'], 
        form_data['making_charges_percent']
    )
    
    # Generate unique bill number with microseconds to prevent duplicates
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    microseconds = int(time.time() * 1000000) % 1000000  # Get microseconds
    unique_bill_number = f"BILL-{timestamp}-{microseconds:06d}"
    
    bill_data = {
        'bill_number': unique_bill_number,
        'billing_date': form_data['billing_date'],
        'shopkeeper_name': form_data['shopkeeper_name'],
        'customer_name': form_data['customer_name'],
        'customer_mobile': form_data['customer_mobile'],
        'customer_address': form_data['customer_address'],
        'gst_number': form_data['gst_number'] if form_data['gst_number'] else "N/A",
        'gst_percent': form_data['gst_percent'],
        'metal_type': form_data['metal_type'],
        'metal_purity': form_data['metal_purity'] if form_data['metal_purity'] else "",
        'weight': form_data['weight'],
        'rate': form_data['rate'],
        'base_amount': base_amount,
        'making_charges_percent': form_data['making_charges_percent'],
        'making_charges_amount': making_charges_amount,
        'total_amount': total_amount,
        'gst_amount': total_amount * (form_data['gst_percent'] / 100) if form_data['gst_number'] else 0,
        'final_amount': total_amount * (1 + (form_data['gst_percent'] / 100)) if form_data['gst_number'] else total_amount
    }
    
    return bill_data

def generate_pdf(bill_data):
    """Generate a luxury-style professional PDF bill for jewelry store"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=25,
        bottomMargin=25
    )
    styles = getSampleStyleSheet()
    
    # Luxury color scheme
    GOLD = colors.HexColor('#D4AF37')
    DARK_GOLD = colors.HexColor('#B8860B')
    NAVY = colors.HexColor('#1A237E')
    CHARCOAL = colors.HexColor('#2C3E50')
    SILVER = colors.HexColor('#C0C0C0')
    LIGHT_GRAY = colors.HexColor('#F5F5F5')
    SUCCESS_GREEN = colors.HexColor('#27AE60')
    ACCENT_RED = colors.HexColor('#E74C3C')
    
    # Optimized typography styles for better space usage
    company_style = ParagraphStyle(
        'CompanyName',
        parent=styles['Heading1'],
        fontSize=22,
        spaceAfter=5,
        alignment=1,
        textColor=NAVY,
        fontName='Helvetica-Bold',
        letterSpacing=1
    )
    
    tagline_style = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=12,
        alignment=1,
        textColor=DARK_GOLD,
        fontName='Helvetica-Oblique',
        letterSpacing=0.5
    )
    
    invoice_title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=10,
        alignment=1,
        textColor=ACCENT_RED,
        fontName='Helvetica-Bold',
        letterSpacing=2
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading3'],
        fontSize=10,
        spaceAfter=4,
        spaceBefore=6,
        textColor=NAVY,
        fontName='Helvetica-Bold',
        backColor=LIGHT_GRAY,
        borderWidth=1,
        borderColor=SILVER,
        borderPadding=4,
        leftIndent=0,
        rightIndent=0
    )
    
    content_style = ParagraphStyle(
        'Content',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=2,
        textColor=CHARCOAL,
        fontName='Helvetica',
        leading=11
    )
    
    # Build PDF content
    story = []
    
    # Elegant company header (removed unnecessary border table)
    story.append(Spacer(1, 8))
    
    header_data = [
        [
            "",
            Paragraph("💎", ParagraphStyle('DiamondEmoji', fontSize=30, alignment=1, textColor=GOLD)),
            Paragraph("Radhe Jewellers", company_style),
            Paragraph("💎", ParagraphStyle('DiamondEmoji', fontSize=30, alignment=1, textColor=GOLD)),
            ""
        ]
    ]
    
    header_table = Table(header_data, colWidths=[0.5*inch, 0.7*inch, 5*inch, 0.7*inch, 0.5*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)
    
    # Company tagline
    tagline = Paragraph("✨ Exquisite Jewelry • Timeless Elegance • Trusted Heritage ✨", tagline_style)
    story.append(tagline)
    
    # Compact address
    address_style = ParagraphStyle(
        'Address',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=CHARCOAL,
        fontName='Helvetica',
        borderWidth=1,
        borderColor=SILVER,
        borderPadding=4,
        backColor=LIGHT_GRAY,
        spaceAfter=8
    )
    
    address = Paragraph(
        "📍 Purnadih Phulwaria Chowk, 200 Meters away from the chowk towards high school phulwaria",
        address_style
    )
    story.append(address)
    story.append(Spacer(1, 12))
    
    # Compact invoice title
    invoice_header_data = [
        [
            "═══",
            Paragraph("INVOICE", invoice_title_style),
            "═══"
        ]
    ]
    
    invoice_header_table = Table(invoice_header_data, colWidths=[1*inch, 5*inch, 1*inch])
    invoice_header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 12),
        ('FONTSIZE', (2, 0), (2, 0), 12),
        ('TEXTCOLOR', (0, 0), (0, 0), GOLD),
        ('TEXTCOLOR', (2, 0), (2, 0), GOLD),
    ]))
    story.append(invoice_header_table)
    story.append(Spacer(1, 10))
    
    # Compact bill and customer information layout
    info_header_data = [
        [
            Paragraph("📋 BILL INFORMATION", section_header_style),
            "",
            Paragraph("👤 CUSTOMER INFORMATION", section_header_style)
        ]
    ]
    
    info_content_data = [
        [
            Paragraph(f"<b>Invoice Number:</b><br/>{bill_data['bill_number']}", content_style),
            "",
            Paragraph(f"<b>Customer Name:</b><br/>{bill_data['customer_name']}", content_style)
        ],
        [
            Paragraph(f"<b>Invoice Date:</b><br/>{bill_data['billing_date']}", content_style),
            "",
            Paragraph(f"<b>Mobile Number:</b><br/>{bill_data['customer_mobile']}", content_style)
        ],
        [
            Paragraph(f"<b>Billed By:</b><br/>{bill_data['shopkeeper_name']}", content_style),
            "",
            Paragraph(f"<b>Address:</b><br/>{bill_data['customer_address']}", content_style)
        ],
        [
            Paragraph(f"<b>GST Number:</b><br/>{bill_data['gst_number']}", content_style),
            "",
            ""
        ]
    ]
    
    # Combine header and content
    all_info_data = info_header_data + info_content_data
    
    info_table = Table(all_info_data, colWidths=[3.2*inch, 0.6*inch, 3.2*inch])
    info_table.setStyle(TableStyle([
        # Header styling
        ('SPAN', (0, 0), (0, 0)),
        ('SPAN', (2, 0), (2, 0)),
        ('BACKGROUND', (0, 0), (0, 0), NAVY),
        ('BACKGROUND', (2, 0), (2, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
        ('TEXTCOLOR', (2, 0), (2, 0), colors.white),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Content styling
        ('BACKGROUND', (0, 1), (0, -1), colors.white),
        ('BACKGROUND', (2, 1), (2, -1), colors.white),
        ('GRID', (0, 0), (0, -1), 1, SILVER),
        ('GRID', (2, 0), (2, -1), 1, SILVER),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))
    
    # Item details section (removed unnecessary header table)
    story.append(Spacer(1, 8))
    
    # Compact item table
    item_data = [
        [
            Paragraph('<b>DESCRIPTION</b>', ParagraphStyle('TableHeader', fontSize=9, textColor=colors.white, fontName='Helvetica-Bold')),
            Paragraph('<b>WEIGHT</b>', ParagraphStyle('TableHeader', fontSize=9, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('<b>RATE/GRAM</b>', ParagraphStyle('TableHeader', fontSize=9, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)),
            Paragraph('<b>AMOUNT</b>', ParagraphStyle('TableHeader', fontSize=9, textColor=colors.white, fontName='Helvetica-Bold', alignment=2))
        ],
        [
            Paragraph(f'Premium {bill_data["metal_type"]}{" (" + bill_data["metal_purity"] + ")" if bill_data["metal_purity"] else ""} Jewellery', ParagraphStyle('ItemDesc', fontSize=9, fontName='Helvetica-Bold', textColor=CHARCOAL)),
            Paragraph(f'{bill_data["weight"]:,.2f}g', ParagraphStyle('TableContent', fontSize=8, alignment=1, textColor=CHARCOAL)),
            Paragraph(f'₹{bill_data["rate"]:,.2f}', ParagraphStyle('TableContent', fontSize=8, alignment=1, textColor=CHARCOAL)),
            Paragraph(f'₹{bill_data["base_amount"]:,.2f}', ParagraphStyle('Amount', fontSize=9, alignment=2, textColor=SUCCESS_GREEN, fontName='Helvetica-Bold'))
        ],
        [
            Paragraph(f'Craftsmanship & Making Charges ({bill_data["making_charges_percent"]:.1f}%)', ParagraphStyle('ItemDesc', fontSize=8, textColor=CHARCOAL)),
            Paragraph('—', ParagraphStyle('TableContent', fontSize=8, alignment=1, textColor=CHARCOAL)),
            Paragraph('—', ParagraphStyle('TableContent', fontSize=8, alignment=1, textColor=CHARCOAL)),
            Paragraph(f'₹{bill_data["making_charges_amount"]:,.2f}', ParagraphStyle('Amount', fontSize=9, alignment=2, textColor=DARK_GOLD, fontName='Helvetica-Bold'))
        ],
        [
            Paragraph('<b>SUBTOTAL</b>', ParagraphStyle('SubtotalLabel', fontSize=10, fontName='Helvetica-Bold', textColor=NAVY)),
            Paragraph('', content_style),
            Paragraph('', content_style),
            Paragraph(f'<b>₹{bill_data["total_amount"]:,.2f}</b>', ParagraphStyle('SubtotalAmount', fontSize=10, alignment=2, fontName='Helvetica-Bold', textColor=NAVY))
        ]
    ]
    
    # Add GST row if applicable
    if bill_data['gst_amount'] > 0:
        item_data.append([
            Paragraph(f'Goods & Services Tax (GST @ {bill_data["gst_percent"]:.1f}%)', ParagraphStyle('ItemDesc', fontSize=8, textColor=CHARCOAL)),
            Paragraph('—', ParagraphStyle('TableContent', fontSize=8, alignment=1, textColor=CHARCOAL)),
            Paragraph('—', ParagraphStyle('TableContent', fontSize=8, alignment=1, textColor=CHARCOAL)),
            Paragraph(f'₹{bill_data["gst_amount"]:,.2f}', ParagraphStyle('Amount', fontSize=9, alignment=2, textColor=ACCENT_RED, fontName='Helvetica-Bold'))
        ])
    
    # Grand total with compact styling
    item_data.append([
        Paragraph('<b>TOTAL AMOUNT PAYABLE</b>', ParagraphStyle('TotalLabel', fontSize=11, fontName='Helvetica-Bold', textColor=colors.white)),
        Paragraph('', content_style),
        Paragraph('', content_style),
        Paragraph(f'<b>₹{bill_data["final_amount"]:,.2f}</b>', ParagraphStyle('TotalAmount', fontSize=12, alignment=2, fontName='Helvetica-Bold', textColor=colors.white))
    ])
    
    item_table = Table(item_data, colWidths=[3.8*inch, 1*inch, 1.2*inch, 1.5*inch])
    
    # Build style list dynamically to avoid None values
    table_styles = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        
        # Item rows styling
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), LIGHT_GRAY),
        ('FONTNAME', (0, 1), (-1, 2), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 2), 8),
        
        # Subtotal styling
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#E3F2FD')),
        ('LINEABOVE', (0, 3), (-1, 3), 2, NAVY),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
    ]
    
    # Add GST styling only if GST is applicable
    if bill_data['gst_amount'] > 0:
        table_styles.append(('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#FFEBEE')))
    
    # Add final styling
    table_styles.extend([
        # Total styling
        ('BACKGROUND', (0, -1), (-1, -1), ACCENT_RED),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('LINEABOVE', (0, -1), (-1, -1), 2, ACCENT_RED),
        ('LINEBELOW', (0, -1), (-1, -1), 2, ACCENT_RED),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        
        # General styling
        ('GRID', (0, 0), (-1, -2), 1, SILVER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -2), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -2), 3),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
    ])
    
    item_table.setStyle(TableStyle(table_styles))
    
    story.append(item_table)
    story.append(Spacer(1, 15))
    
    # Compact thank you section
    thanks_style = ParagraphStyle(
        'Thanks',
        parent=styles['Normal'],
        fontSize=11,
        alignment=1,
        textColor=NAVY,
        fontName='Helvetica-Bold',
        spaceAfter=5
    )
    
    gratitude_style = ParagraphStyle(
        'Gratitude',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=DARK_GOLD,
        fontName='Helvetica-Oblique',
        spaceAfter=8
    )
    
    terms_style = ParagraphStyle(
        'Terms',
        parent=styles['Normal'],
        fontSize=7,
        alignment=1,
        textColor=CHARCOAL,
        fontName='Helvetica',
        leading=9,
        spaceAfter=5
    )
    
    # Compact footer messages
    thanks_msg = Paragraph("🙏 Thank you for choosing Radhe Jewellers! 🙏", thanks_style)
    story.append(thanks_msg)
    
    gratitude_msg = Paragraph("Your trust in our craftsmanship is our greatest reward", gratitude_style)
    story.append(gratitude_msg)
    
    # Compact terms and conditions
    terms_msg = Paragraph(
        "• All items sold are subject to our terms and conditions • "
        "Please retain this invoice for warranty claims • "
        "Prices include all applicable taxes • "
        "Thank you for your business •",
        terms_style
    )
    story.append(terms_msg)
    
    # Build the PDF
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

def save_bill_to_json(bill_data):
    """Save bill data to a JSON file with duplicate prevention."""
    try:
        filename = f"{bill_data['bill_number']}.json"
        filepath = os.path.join(BILLS_DIR, filename)
        
        # Check if bill already exists
        if os.path.exists(filepath):
            # Load existing bill to compare
            with open(filepath, 'r') as f:
                existing_bill = json.load(f)
            
            # Check if the content is actually different
            if existing_bill == bill_data:
                st.info(f"ℹ️ Bill {bill_data['bill_number']} already exists with identical data. No changes made.")
                return "no_change"
            else:
                # Content is different, update it
                with open(filepath, 'w') as f:
                    json.dump(bill_data, f, indent=4)
                st.warning(f"⚠️ Bill {bill_data['bill_number']} updated with new data!")
                return "updated"
        else:
            # New bill, create it
            with open(filepath, 'w') as f:
                json.dump(bill_data, f, indent=4)
            st.success(f"✅ New bill {bill_data['bill_number']} saved successfully!")
            return "created"
    except Exception as e:
        st.error(f"❌ Error saving bill to JSON: {str(e)}")
        return "error"

def load_historical_bills():
    """Load all saved bill data from JSON files."""
    historical_bills = []
    for filename in os.listdir(BILLS_DIR):
        if filename.endswith('.json'):
            try:
                filepath = os.path.join(BILLS_DIR, filename)
                with open(filepath, 'r') as f:
                    bill_data = json.load(f)
                    historical_bills.append(bill_data)
            except json.JSONDecodeError:
                st.warning(f"⚠️ Could not decode JSON from {filename}. Skipping.")
            except Exception as e:
                st.error(f"❌ Error loading bill from {filename}: {str(e)}")
    return historical_bills

def export_bills_to_csv(historical_bills):
    """Export historical bills to CSV format."""
    if not historical_bills:
        return None
    
    # Prepare data for CSV
    csv_data = []
    for bill in historical_bills:
        csv_data.append({
            'Bill Number': bill['bill_number'],
            'Date': bill['billing_date'],
            'Customer Name': bill['customer_name'],
            'Customer Mobile': bill['customer_mobile'],
            'Metal Type': bill['metal_type'],
            'Metal Purity': bill.get('metal_purity', ''),
            'Weight (grams)': bill['weight'],
            'Rate per gram': bill['rate'],
            'Base Amount': bill['base_amount'],
            'Making Charges %': bill['making_charges_percent'],
            'Making Charges Amount': bill['making_charges_amount'],
            'Subtotal': bill['total_amount'],
            'GST %': bill.get('gst_percent', 3.0),
            'GST Amount': bill['gst_amount'],
            'Final Amount': bill['final_amount'],
            'Billed By': bill['shopkeeper_name'],
            'GST Number': bill['gst_number']
        })
    
    df = pd.DataFrame(csv_data)
    return df.to_csv(index=False).encode('utf-8')

def get_bills_summary(historical_bills):
    """Get summary statistics of historical bills."""
    if not historical_bills:
        return None
    
    df = pd.DataFrame(historical_bills)
    
    summary = {
        'total_bills': len(historical_bills),
        'total_revenue': df['final_amount'].sum(),
        'avg_bill_amount': df['final_amount'].mean(),
        'total_weight': df['weight'].sum(),
        'date_range': f"{df['billing_date'].min()} to {df['billing_date'].max()}"
    }
    
    return summary

def delete_bill(bill_number):
    """Delete a bill from the JSON storage."""
    try:
        filename = f"{bill_number}.json"
        filepath = os.path.join(BILLS_DIR, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            st.success(f"✅ Bill {bill_number} deleted successfully!")
            return True
        else:
            st.error(f"❌ Bill {bill_number} not found!")
            return False
    except Exception as e:
        st.error(f"❌ Error deleting bill: {str(e)}")
        return False

def create_bills_backup():
    """Create a ZIP backup of all bills."""
    try:
        # Create a BytesIO buffer for the ZIP file
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add all JSON files from bills directory
            for filename in os.listdir(BILLS_DIR):
                if filename.endswith('.json'):
                    file_path = os.path.join(BILLS_DIR, filename)
                    zip_file.write(file_path, filename)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    except Exception as e:
        st.error(f"❌ Error creating backup: {str(e)}")
        return None

def main():
    st.markdown('<h1 class="main-header">💍 Radhe Jewellers</h1>', unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        default_shopkeeper = st.text_input("Default Billed By Name", value="Upendra Kumar")
        default_gst = st.text_input("Default GST Number", value="")
        
        st.header("📊 Quick Stats")
        
        # Load historical bills for stats
        historical_bills_for_stats = load_historical_bills()
        
        if historical_bills_for_stats:
            summary = get_bills_summary(historical_bills_for_stats)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Bills", summary['total_bills'])
                st.metric("Avg Bill Amount", f"₹{summary['avg_bill_amount']:.2f}")
            with col2:
                st.metric("Total Revenue", f"₹{summary['total_revenue']:.2f}")
                st.metric("Total Weight", f"{summary['total_weight']:.2f}g")
            
            st.caption(f"Period: {summary['date_range']}")
            
            # Export functionality
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = export_bills_to_csv(historical_bills_for_stats)
                if csv_data:
                    st.download_button(
                        label="📊 CSV Export",
                        data=csv_data,
                        file_name=f"radhe_jewellers_bills_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                backup_data = create_bills_backup()
                if backup_data:
                    st.download_button(
                        label="💾 Full Backup",
                        data=backup_data,
                        file_name=f"radhe_jewellers_backup_{datetime.now().strftime('%Y%m%d')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
        else:
            st.info("No bills generated yet. Create your first bill to see statistics!")
        
        st.header("📋 Historical Bills")
        
        # Load and display historical bills
        historical_bills = load_historical_bills()
        
        if historical_bills:
            # Sort bills by date (newest first)
            historical_bills.sort(key=lambda x: x['billing_date'], reverse=True)
            
            # Search and filter functionality
            search_term = st.text_input("🔍 Search Bills", placeholder="Search by bill number, customer name...")
            
            # Date filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From Date", value=None)
            with col2:
                end_date = st.date_input("To Date", value=None)
            
            # Filter bills based on search and date
            filtered_bills = historical_bills
            
            if search_term:
                filtered_bills = [
                    bill for bill in filtered_bills 
                    if search_term.lower() in bill['bill_number'].lower() or 
                       search_term.lower() in bill['customer_name'].lower()
                ]
            
            if start_date:
                filtered_bills = [
                    bill for bill in filtered_bills 
                    if bill['billing_date'] >= start_date.strftime('%Y-%m-%d')
                ]
            
            if end_date:
                filtered_bills = [
                    bill for bill in filtered_bills 
                    if bill['billing_date'] <= end_date.strftime('%Y-%m-%d')
                ]
            
            # Display bills
            st.write(f"Found {len(filtered_bills)} bills")
            
            for bill in filtered_bills[:10]:  # Show latest 10 bills
                with st.expander(f"📄 {bill['bill_number']} - {bill['customer_name']} (₹{bill['final_amount']:.2f})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Date:** {bill['billing_date']}")
                        st.write(f"**Customer:** {bill['customer_name']}")
                        st.write(f"**Metal:** {bill['metal_type']}")
                        if bill['metal_purity']:
                            st.write(f"**Purity:** {bill['metal_purity']}")
                        st.write(f"**Weight:** {bill['weight']}g")
                        st.write(f"**Amount:** ₹{bill['final_amount']:.2f}")
                    
                    with col2:
                        if st.button("📄 PDF", key=f"download_{bill['bill_number']}", use_container_width=True):
                            # Generate PDF for historical bill
                            pdf_buffer = generate_pdf(bill)
                            pdf_buffer.seek(0)
                            st.download_button(
                                label="💾 Save PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"bill_{bill['bill_number']}.pdf",
                                mime="application/pdf",
                                key=f"save_{bill['bill_number']}",
                                use_container_width=True
                            )
                        
                        if st.button("👁️ View", key=f"view_{bill['bill_number']}", use_container_width=True):
                            st.session_state.bill_data = bill
                            st.session_state.pdf_buffer = generate_pdf(bill)
                            st.rerun()
                        
                        # Delete functionality with confirmation
                        if st.button("🗑️ Delete", key=f"delete_{bill['bill_number']}", use_container_width=True, type="secondary"):
                            if f"confirm_delete_{bill['bill_number']}" not in st.session_state:
                                st.session_state[f"confirm_delete_{bill['bill_number']}"] = True
                                st.rerun()
                        
                        # Show confirmation dialog
                        if st.session_state.get(f"confirm_delete_{bill['bill_number']}", False):
                            st.warning(f"⚠️ Delete {bill['bill_number']}?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Yes", key=f"confirm_yes_{bill['bill_number']}"):
                                    if delete_bill(bill['bill_number']):
                                        if f"confirm_delete_{bill['bill_number']}" in st.session_state:
                                            del st.session_state[f"confirm_delete_{bill['bill_number']}"]
                                        st.rerun()
                            with col_no:
                                if st.button("❌ No", key=f"confirm_no_{bill['bill_number']}"):
                                    if f"confirm_delete_{bill['bill_number']}" in st.session_state:
                                        del st.session_state[f"confirm_delete_{bill['bill_number']}"]
                                    st.rerun()
            
            if len(filtered_bills) > 10:
                st.info(f"Showing 10 of {len(filtered_bills)} bills. Use search to find specific bills.")
        else:
            st.info("No historical bills found. Generate your first bill to see it here!")
    
    # Main form
    with st.form("billing_form"):
        st.subheader("📝 Billing Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Shop Details**")
            shopkeeper_name = st.text_input("Billed By*", value=default_shopkeeper)
            gst_number = st.text_input("GST Number (Optional)", value=default_gst)
            gst_percent = st.number_input("GST Percentage (%)", min_value=0.0, max_value=50.0, value=3.0, step=0.1, format="%.1f", help="Enter GST percentage (e.g., 3.0, 5.0, 12.0, 18.0)")
            
            st.markdown("**Customer Details**")
            customer_name = st.text_input("Customer Name*")
            customer_mobile = st.text_input("Customer Mobile Number*", placeholder="Enter 10-digit mobile number")
            customer_address = st.text_area("Customer Address*", height=100)
        
        with col2:
            st.markdown("**Item Details**")
            metal_type = st.selectbox("Metal Type", ["Gold", "Silver"])
            metal_purity = st.text_input("Metal Purity (Optional)", placeholder="e.g., 22K, 18K, 925 Silver")
            weight = st.number_input("Weight (grams)*", min_value=0.0, step=0.1, format="%.2f")
            rate = st.number_input(f"{metal_type} Rate per gram (₹)*", min_value=0.0, step=0.01, format="%.2f")
            making_charges_percent = st.number_input("Making Charges (%)*", min_value=0.0, step=0.1, format="%.2f")
            
            st.markdown("**Billing Date**")
            billing_date = st.date_input("Billing Date", value=datetime.now().date())
        
        # Calculate preview
        if weight and rate and making_charges_percent >= 0:
            base_amount, making_charges_amount, total_amount = calculate_total_amount(weight, rate, making_charges_percent)
            gst_amount = total_amount * (gst_percent / 100) if gst_number else 0
            final_amount = total_amount + gst_amount
            
            st.markdown("---")
            st.subheader("💰 Amount Preview")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Base Amount", f"₹{base_amount:.2f}")
            with col2:
                st.metric("Making Charges", f"₹{making_charges_amount:.2f} ({making_charges_percent:.2f}%)")
            with col3:
                st.metric(f"GST ({gst_percent:.1f}%)", f"₹{gst_amount:.2f}" if gst_number else "₹0.00")
            with col4:
                st.metric("Final Amount", f"₹{final_amount:.2f}")
        
        # Form submission
        submitted = st.form_submit_button("🧾 Generate Bill", use_container_width=True)
        
        if submitted:
            # Check for rapid successive clicks (prevent double submission)
            current_time = time.time()
            last_submission_time = st.session_state.get('last_bill_submission', 0)
            
            if current_time - last_submission_time < 2:  # 2 second cooldown
                st.warning("⏳ Please wait a moment before generating another bill.")
                st.stop()
            
            # Update last submission time
            st.session_state.last_bill_submission = current_time
            
            # Validate required fields
            if not all([shopkeeper_name, customer_name, customer_mobile, customer_address]) or weight <= 0 or rate <= 0 or making_charges_percent < 0:
                st.error("❌ Please fill in all required fields marked with *")
            elif len(customer_mobile) != 10 or not customer_mobile.isdigit():
                st.error("❌ Please enter a valid 10-digit mobile number")
            else:
                # Show processing message
                with st.spinner("🔄 Generating bill..."):
                    # Generate bill
                    form_data = {
                        'shopkeeper_name': shopkeeper_name,
                        'gst_number': gst_number,
                        'gst_percent': gst_percent,
                        'customer_name': customer_name,
                        'customer_mobile': customer_mobile,
                        'customer_address': customer_address,
                        'metal_type': metal_type,
                        'metal_purity': metal_purity,
                        'weight': weight,
                        'rate': rate,
                        'making_charges_percent': making_charges_percent,
                        'billing_date': billing_date.strftime('%Y-%m-%d')
                    }
                    
                    st.session_state.bill_data = generate_bill_data(form_data)
                    st.session_state.pdf_buffer = generate_pdf(st.session_state.bill_data)
                    
                    # Save bill data to JSON file with duplicate check
                    save_result = save_bill_to_json(st.session_state.bill_data)
                    
                    if save_result == "created":
                        st.success("✅ Bill generated and saved successfully!")
                    elif save_result == "updated":
                        st.info("ℹ️ Bill generated successfully (existing bill updated)!")
                    elif save_result == "no_change":
                        st.info("ℹ️ Bill generated successfully (no changes to existing data)!")
                    
                    time.sleep(0.5)  # Brief pause for better UX
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
            st.write(f"**Billed By:** {bill_data['shopkeeper_name']}")
            st.write(f"**GST Number:** {bill_data['gst_number']}")
            
            st.markdown("**Customer Details**")
            st.write(f"**Name:** {bill_data['customer_name']}")
            st.write(f"**Mobile:** {bill_data['customer_mobile']}")
            st.write(f"**Address:** {bill_data['customer_address']}")
        
        with col2:
            st.markdown("**Item Details**")
            st.write(f"**Metal Type:** {bill_data['metal_type']}")
            if bill_data['metal_purity']:
                st.write(f"**Metal Purity:** {bill_data['metal_purity']}")
            st.write(f"**Weight:** {bill_data['weight']}g")
            st.write(f"**Rate:** ₹{bill_data['rate']}/g")
            st.write(f"**Base Amount:** ₹{bill_data['base_amount']:.2f}")
            st.write(f"**Making Charges:** {bill_data['making_charges_percent']:.2f}%")
            st.write(f"**Making Charges Amount:** ₹{bill_data['making_charges_amount']:.2f}")
            if bill_data['gst_amount'] > 0:
                st.write(f"**GST ({bill_data['gst_percent']:.1f}%):** ₹{bill_data['gst_amount']:.2f}")
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
        
        # with col3:
        #     if st.button("📱 Send via WhatsApp", use_container_width=True):
        #         send_whatsapp_message(
        #             bill_data['customer_mobile'], 
        #             st.session_state.pdf_buffer,
        #             bill_data
        #         )
    
            # Clear bill button
    if st.session_state.bill_data:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🗑️ Clear Current Bill", use_container_width=True):
                st.session_state.bill_data = None
                st.session_state.pdf_buffer = None
                # Also reset the submission timer to allow immediate new bill generation
                if 'last_bill_submission' in st.session_state:
                    del st.session_state.last_bill_submission
                st.rerun()
        with col2:
            st.metric("Bill Status", "Generated" if st.session_state.bill_data else "None")

if __name__ == "__main__":
    main() 
