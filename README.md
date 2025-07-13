# 💍 Radhe Jewellers

A comprehensive billing solution for jewellery shops dealing in gold and silver, built with Streamlit. This application provides a user-friendly interface for generating professional bills, PDF export, and WhatsApp integration for seamless customer communication.

## ✨ Features

- **📝 Comprehensive Billing Form**
  - GST number (optional)
  - Shopkeeper name
  - Customer details (name, mobile, address)
  - Weight and metal type (Gold/Silver)
  - Rate per gram
  - Additional charges
  - Auto-generated billing date

- **💰 Automatic Calculations**
  - Base amount calculation (weight × rate)
  - GST calculation (3% if GST number provided)
  - Total amount with all charges
  - Real-time preview of amounts

- **📄 Professional PDF Generation**
  - Formatted bill with company branding
  - Detailed itemization
  - Professional layout using ReportLab
  - Downloadable PDF files

- **📱 WhatsApp Integration**
  - Send bills directly to customers via WhatsApp
  - Support for multiple providers (Twilio, WhatsApp Business API, UltraMsg)
  - Automatic message formatting
  - PDF attachment support (provider dependent)

- **🎨 Modern UI/UX**
  - Clean, responsive design
  - Intuitive form layout
  - Real-time validation
  - Professional styling

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project**
   ```bash
   # If you have git
   git clone <repository-url>
   cd "Billing Software"
   
   # Or download and extract the files
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:8501`
   - The application will be ready to use!

## 📋 Usage Guide

### Basic Billing Process

1. **Fill Shop Details**
   - Enter shopkeeper name
   - Add GST number (optional but recommended for GST calculation)

2. **Enter Customer Information**
   - Customer name
   - 10-digit mobile number
   - Complete address

3. **Specify Item Details**
   - Select metal type (Gold/Silver)
   - Enter weight in grams
   - Set rate per gram
   - Add any additional charges

4. **Generate Bill**
   - Review the amount preview
   - Click "Generate Bill"
   - Bill will be created with auto-generated bill number

5. **Actions Available**
   - **Download PDF**: Save bill as PDF file
   - **Preview PDF**: View bill in browser
   - **Send via WhatsApp**: Send bill to customer (requires configuration)

### WhatsApp Integration Setup

The application supports three WhatsApp providers:

#### Option 1: Twilio WhatsApp API
1. Create account at [Twilio Console](https://console.twilio.com)
2. Set up WhatsApp Sandbox
3. Get credentials and add to `.streamlit/secrets.toml`:
   ```toml
   TWILIO_ACCOUNT_SID = "your_account_sid"
   TWILIO_AUTH_TOKEN = "your_auth_token"
   TWILIO_WHATSAPP_NUMBER = "+14155238886"
   ```

#### Option 2: WhatsApp Business API
1. Create Facebook Developer account
2. Set up WhatsApp Business API
3. Get credentials and add to `.streamlit/secrets.toml`:
   ```toml
   WHATSAPP_ACCESS_TOKEN = "your_access_token"
   WHATSAPP_PHONE_NUMBER_ID = "your_phone_number_id"
   ```

#### Option 3: UltraMsg API (Recommended for small businesses)
1. Create account at [UltraMsg](https://ultramsg.com)
2. Get credentials and add to `.streamlit/secrets.toml`:
   ```toml
   ULTRAMSG_TOKEN = "your_token"
   ULTRAMSG_INSTANCE_ID = "your_instance_id"
   ```

### Configuration

Create a `.streamlit/secrets.toml` file in your project directory:

```toml
# WhatsApp Integration (choose one)
# Twilio
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_WHATSAPP_NUMBER = "+14155238886"

# OR WhatsApp Business API
WHATSAPP_ACCESS_TOKEN = "your_access_token"
WHATSAPP_PHONE_NUMBER_ID = "your_phone_number_id"

# OR UltraMsg
ULTRAMSG_TOKEN = "your_token"
ULTRAMSG_INSTANCE_ID = "your_instance_id"
```

## 🏗️ Project Structure

```
Billing Software/
├── app.py                      # Main Streamlit application
├── whatsapp_integration.py     # WhatsApp integration module
├── requirements.txt            # Python dependencies
├── README.md                  # This file
└── .streamlit/
    └── secrets.toml           # Configuration file (create this)
```

## 🔧 Customization

### Adding New Features

1. **New Metal Types**: Edit the `metal_type` selectbox in `app.py`
2. **Custom Styling**: Modify the CSS in the `st.markdown` section
3. **Additional Fields**: Add new input fields in the form section
4. **Custom Calculations**: Modify the `calculate_total_amount` function

### Branding

1. **Company Name**: Update the title in `generate_pdf` function
2. **Logo**: Add logo image in PDF generation
3. **Colors**: Modify the color scheme in CSS and PDF styles
4. **Contact Info**: Add company contact details in PDF footer

## 📝 Bill Information

Each generated bill includes:
- **Unique Bill Number**: Auto-generated with timestamp
- **Billing Date**: Current date (editable)
- **Shop Details**: Shopkeeper name and GST number
- **Customer Details**: Name, mobile, and address
- **Item Details**: Metal type, weight, rate, and calculations
- **Amount Breakdown**: Base amount, additional charges, GST, and total

## 🛠️ Technical Details

### Dependencies

- **Streamlit**: Web application framework
- **ReportLab**: PDF generation
- **Pandas**: Data manipulation
- **Requests**: HTTP requests for APIs
- **Twilio**: WhatsApp integration (optional)
- **Pillow**: Image processing

### Data Flow

1. User inputs → Form validation → Bill data structure
2. Bill data → PDF generation → PDF buffer
3. PDF buffer → WhatsApp integration → Message sent
4. All operations use session state for persistence

## 🐛 Troubleshooting

### Common Issues

1. **WhatsApp not working**
   - Check if credentials are properly configured
   - Verify the phone number format
   - Ensure the chosen provider is set up correctly

2. **PDF generation fails**
   - Check if ReportLab is installed correctly
   - Verify all bill data fields are present

3. **Application won't start**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify file permissions

### Support

For issues or questions:
1. Check the error messages in the application
2. Verify your configuration files
3. Ensure all dependencies are installed
4. Check the console for detailed error logs

## 🚀 Deployment

### Local Development
- Use `streamlit run app.py` for development
- Access at `http://localhost:8501`

### Production Deployment
- Deploy to Streamlit Cloud, Heroku, or similar platforms
- Set environment variables for WhatsApp credentials
- Use HTTPS for production deployment

## 📈 Future Enhancements

Potential features to add:
- **Database Integration**: Store bills and customer data
- **Invoice Templates**: Multiple PDF templates
- **Inventory Management**: Track gold/silver stock
- **Analytics Dashboard**: Sales reports and analytics
- **Multi-language Support**: Regional language options
- **Email Integration**: Send bills via email
- **Barcode Integration**: Generate barcodes for bills
- **Customer Management**: Customer database and history

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Made with ❤️ for jewellery shop owners** 