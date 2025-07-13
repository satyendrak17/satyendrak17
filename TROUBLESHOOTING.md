# 🔧 Troubleshooting Guide

## WhatsApp Integration Issues

### ❌ **Error: "Twilio could not find a Channel with the specified From address"**

**Problem**: The WhatsApp number in your configuration is incorrect or not properly set up.

**Solution**:
1. **Check your Twilio WhatsApp Sandbox**:
   - Go to [Twilio Console](https://console.twilio.com)
   - Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
   - Note the exact sandbox number (usually `+1 415 523 8886`)

2. **Join the Sandbox**:
   - Send a WhatsApp message to the sandbox number
   - Message format: `join <your-sandbox-code>`
   - Wait for confirmation message

3. **Update your configuration**:
   ```toml
   # .streamlit/secrets.toml
   TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   TWILIO_AUTH_TOKEN = "your_auth_token_here"
   TWILIO_WHATSAPP_NUMBER = "+14155238886"  # Use exact sandbox number
   ```

4. **Common mistakes**:
   - ❌ Using your regular Twilio phone number instead of WhatsApp sandbox number
   - ❌ Adding "whatsapp:" prefix to the number in secrets.toml
   - ❌ Using a different sandbox number than what Twilio provides
   - ❌ Not joining the sandbox before testing

### ❌ **Error: "The destination number is not a valid WhatsApp number"**

**Problem**: The customer's phone number format is incorrect.

**Solution**:
- Use 10-digit mobile numbers (e.g., 9876543210)
- Don't include country code or + sign
- The app automatically adds +91 for Indian numbers

### ❌ **Error: "Permission denied to send to this number"**

**Problem**: In Twilio sandbox, you can only send to numbers that have joined the sandbox.

**Solution**:
1. Ask the customer to send `join <your-sandbox-code>` to the Twilio sandbox number
2. Or use a different WhatsApp provider (UltraMsg or WhatsApp Business API)

### ❌ **Error: "Invalid credentials"**

**Problem**: Twilio Account SID or Auth Token is incorrect.

**Solution**:
1. Go to [Twilio Console](https://console.twilio.com) dashboard
2. Copy the exact **Account SID** and **Auth Token**
3. For Auth Token, click "View" to reveal the token
4. Update your `.streamlit/secrets.toml` file

### ❌ **PDF attachment not working**

**Problem**: Twilio WhatsApp API doesn't support direct file uploads.

**Solution**:
- Use **UltraMsg API** instead (supports PDF attachments)
- Or host the PDF file online and send the link via Twilio

## Alternative WhatsApp Providers

### 🚀 **UltraMsg (Recommended for small businesses)**
- ✅ Supports PDF attachments
- ✅ Easy setup
- ✅ Works with any phone number
- ✅ No sandbox limitations

**Setup**:
1. Go to [UltraMsg](https://ultramsg.com)
2. Create account and get Instance ID and Token
3. Update your `.streamlit/secrets.toml`:
   ```toml
   ULTRAMSG_TOKEN = "your_token_here"
   ULTRAMSG_INSTANCE_ID = "your_instance_id_here"
   ```

### 🏢 **WhatsApp Business API**
- ✅ Official WhatsApp API
- ✅ No sandbox limitations
- ❌ Requires business verification
- ❌ More complex setup

## General Issues

### 🔧 **Application won't start**
```bash
# Update pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### 🔧 **PDF generation fails**
- Ensure all bill fields are filled
- Check that ReportLab is installed correctly
- Verify file permissions

### 🔧 **Configuration not loading**
- Check that `.streamlit/secrets.toml` exists
- Verify file format and syntax
- Ensure no extra spaces in credentials

## Getting Help

If you're still having issues:
1. Check the error message in the application
2. Verify your configuration files
3. Test with a simple message first
4. Check the console for detailed error logs

For Twilio-specific issues, visit: https://www.twilio.com/docs/whatsapp 