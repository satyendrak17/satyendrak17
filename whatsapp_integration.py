"""
WhatsApp Integration Module for Radhe Jewellers

This module provides integration with WhatsApp APIs to send bills to customers.
It includes examples for different WhatsApp API providers.
"""

import requests
import json
import base64
import os
from typing import Optional, Dict, Any
import streamlit as st

class WhatsAppIntegration:
    """
    WhatsApp Integration class supporting multiple providers
    """
    
    def __init__(self, provider: str = "twilio"):
        """
        Initialize WhatsApp integration
        
        Args:
            provider: WhatsApp API provider ('twilio', 'whatsapp_business', 'ultramsg')
        """
        self.provider = provider
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, str]:
        """Load configuration from environment variables or Streamlit secrets"""
        config = {}
        
        if self.provider == "twilio":
            config = {
                'account_sid': os.getenv('TWILIO_ACCOUNT_SID') or st.secrets.get('TWILIO_ACCOUNT_SID', ''),
                'auth_token': os.getenv('TWILIO_AUTH_TOKEN') or st.secrets.get('TWILIO_AUTH_TOKEN', ''),
                'whatsapp_number': os.getenv('TWILIO_WHATSAPP_NUMBER') or st.secrets.get('TWILIO_WHATSAPP_NUMBER', '')
            }
        elif self.provider == "whatsapp_business":
            config = {
                'access_token': os.getenv('WHATSAPP_ACCESS_TOKEN') or st.secrets.get('WHATSAPP_ACCESS_TOKEN', ''),
                'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID') or st.secrets.get('WHATSAPP_PHONE_NUMBER_ID', '')
            }
        elif self.provider == "ultramsg":
            config = {
                'token': os.getenv('ULTRAMSG_TOKEN') or st.secrets.get('ULTRAMSG_TOKEN', ''),
                'instance_id': os.getenv('ULTRAMSG_INSTANCE_ID') or st.secrets.get('ULTRAMSG_INSTANCE_ID', '')
            }
        
        return config
    
    def send_bill_via_twilio(self, customer_phone: str, pdf_buffer: bytes, bill_data: Dict[str, Any]) -> bool:
        """
        Send bill via Twilio WhatsApp API
        
        Args:
            customer_phone: Customer's phone number
            pdf_buffer: PDF file as bytes
            bill_data: Bill information
            
        Returns:
            bool: Success status
        """
        if not all([self.config.get('account_sid'), self.config.get('auth_token'), self.config.get('whatsapp_number')]):
            st.error("❌ Twilio credentials not configured")
            return False
        
        try:
            from twilio.rest import Client
            from twilio.base.exceptions import TwilioRestException
            
            client = Client(self.config['account_sid'], self.config['auth_token'])
            
            # Format phone number for WhatsApp
            if customer_phone.startswith('+'):
                formatted_phone = f"whatsapp:{customer_phone}"
            else:
                # Remove any spaces, dashes, or other formatting
                clean_phone = customer_phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                formatted_phone = f"whatsapp:+91{clean_phone}"
            
            # Format the FROM number
            from_number = self.config['whatsapp_number']
            if not from_number.startswith('whatsapp:'):
                from_number = f"whatsapp:{from_number}"
            
            # Create message text
            message_text = f"""🧾 *Bill from {bill_data['shopkeeper_name']}*

📋 Bill Number: {bill_data['bill_number']}
📅 Date: {bill_data['billing_date']}
👤 Customer: {bill_data['customer_name']}

💰 Amount Details:
• {bill_data['metal_type']} ({bill_data['weight']}g): ₹{bill_data['base_amount']:.2f}
• Additional Charges: ₹{bill_data['billing_price']:.2f}
• GST (3%): ₹{bill_data['gst_amount']:.2f}
• *Final Amount: ₹{bill_data['final_amount']:.2f}*

Thank you for your business! 💍"""
            
            # Send message
            message = client.messages.create(
                body=message_text,
                from_=from_number,
                to=formatted_phone
            )
            
            st.success(f"✅ Bill sent via Twilio WhatsApp to {customer_phone}")
            st.info("📎 PDF attachment requires hosting the file and sending the link")
            
            return True
            
        except TwilioRestException as e:
            if e.code == 63007:
                st.error("❌ Twilio WhatsApp Error: Invalid WhatsApp number configured")
                st.error("🔧 Please check your Twilio WhatsApp Sandbox settings:")
                st.error("1. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message")
                st.error("2. Copy the exact sandbox number (e.g., +1 415 523 8886)")
                st.error("3. Update your .streamlit/secrets.toml file")
                st.error("4. Make sure you've joined the sandbox by sending 'join <sandbox-code>' to the number")
            else:
                st.error(f"❌ Twilio Error [{e.code}]: {e.msg}")
            return False
        except Exception as e:
            st.error(f"❌ Error sending via Twilio: {str(e)}")
            return False
    
    def send_bill_via_whatsapp_business(self, customer_phone: str, pdf_buffer: bytes, bill_data: Dict[str, Any]) -> bool:
        """
        Send bill via WhatsApp Business API
        
        Args:
            customer_phone: Customer's phone number
            pdf_buffer: PDF file as bytes
            bill_data: Bill information
            
        Returns:
            bool: Success status
        """
        if not all([self.config.get('access_token'), self.config.get('phone_number_id')]):
            st.error("❌ WhatsApp Business API credentials not configured")
            return False
        
        try:
            # WhatsApp Business API endpoint
            url = f"https://graph.facebook.com/v18.0/{self.config['phone_number_id']}/messages"
            
            headers = {
                'Authorization': f"Bearer {self.config['access_token']}",
                'Content-Type': 'application/json'
            }
            
            # Format phone number (remove + and country code formatting)
            formatted_phone = customer_phone.replace('+', '').replace('-', '').replace(' ', '')
            if not formatted_phone.startswith('91'):
                formatted_phone = f"91{formatted_phone}"
            
            # Create message payload
            message_text = f"""
🧾 *Bill from {bill_data['shopkeeper_name']}*

📋 Bill Number: {bill_data['bill_number']}
📅 Date: {bill_data['billing_date']}
👤 Customer: {bill_data['customer_name']}

💰 Amount Details:
• {bill_data['metal_type']} ({bill_data['weight']}g): ₹{bill_data['base_amount']:.2f}
• Additional Charges: ₹{bill_data['billing_price']:.2f}
• GST (3%): ₹{bill_data['gst_amount']:.2f}
• *Final Amount: ₹{bill_data['final_amount']:.2f}*

Thank you for your business! 💍
            """
            
            payload = {
                "messaging_product": "whatsapp",
                "to": formatted_phone,
                "type": "text",
                "text": {"body": message_text}
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                st.success(f"✅ Bill sent via WhatsApp Business API to {customer_phone}")
                return True
            else:
                st.error(f"❌ Error sending message: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error sending via WhatsApp Business API: {str(e)}")
            return False
    
    def send_bill_via_ultramsg(self, customer_phone: str, pdf_buffer: bytes, bill_data: Dict[str, Any]) -> bool:
        """
        Send bill via UltraMsg API (supports file uploads)
        
        Args:
            customer_phone: Customer's phone number
            pdf_buffer: PDF file as bytes
            bill_data: Bill information
            
        Returns:
            bool: Success status
        """
        if not all([self.config.get('token'), self.config.get('instance_id')]):
            st.error("❌ UltraMsg credentials not configured")
            return False
        
        try:
            # UltraMsg API endpoint
            url = f"https://api.ultramsg.com/{self.config['instance_id']}/messages/document"
            
            # Format phone number
            formatted_phone = customer_phone.replace('+', '').replace('-', '').replace(' ', '')
            if not formatted_phone.startswith('91'):
                formatted_phone = f"91{formatted_phone}"
            
            # Create message text
            message_text = f"""
🧾 *Bill from {bill_data['shopkeeper_name']}*

📋 Bill Number: {bill_data['bill_number']}
📅 Date: {bill_data['billing_date']}
👤 Customer: {bill_data['customer_name']}

💰 Final Amount: ₹{bill_data['final_amount']:.2f}

Thank you for your business! 💍
            """
            
            # Prepare file data
            files = {
                'document': (f"bill_{bill_data['bill_number']}.pdf", pdf_buffer, 'application/pdf')
            }
            
            data = {
                'token': self.config['token'],
                'to': formatted_phone,
                'caption': message_text,
                'filename': f"bill_{bill_data['bill_number']}.pdf"
            }
            
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('sent'):
                    st.success(f"✅ Bill sent via UltraMsg to {customer_phone}")
                    return True
                else:
                    st.error(f"❌ Error sending message: {result.get('message', 'Unknown error')}")
                    return False
            else:
                st.error(f"❌ Error sending message: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error sending via UltraMsg: {str(e)}")
            return False
    
    def send_bill(self, customer_phone: str, pdf_buffer: bytes, bill_data: Dict[str, Any]) -> bool:
        """
        Send bill using the configured provider
        
        Args:
            customer_phone: Customer's phone number
            pdf_buffer: PDF file as bytes
            bill_data: Bill information
            
        Returns:
            bool: Success status
        """
        if self.provider == "twilio":
            return self.send_bill_via_twilio(customer_phone, pdf_buffer, bill_data)
        elif self.provider == "whatsapp_business":
            return self.send_bill_via_whatsapp_business(customer_phone, pdf_buffer, bill_data)
        elif self.provider == "ultramsg":
            return self.send_bill_via_ultramsg(customer_phone, pdf_buffer, bill_data)
        else:
            st.error(f"❌ Unsupported provider: {self.provider}")
            return False

def display_whatsapp_setup_guide():
    """Display setup guide for WhatsApp integration"""
    st.markdown("## 📱 WhatsApp Integration Setup Guide")
    
    tab1, tab2, tab3 = st.tabs(["Twilio", "WhatsApp Business API", "UltraMsg"])
    
    with tab1:
        st.markdown("### Twilio WhatsApp API Setup")
        st.markdown("""
        1. **Create a Twilio Account**
           - Go to [Twilio Console](https://console.twilio.com)
           - Sign up for a free account
        
        2. **Set up WhatsApp Sandbox**
           - Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
           - Note the sandbox WhatsApp number (e.g., +1 415 523 8886)
           - Note the sandbox code (e.g., join <code>)
        
        3. **Join the Sandbox**
           - Send a WhatsApp message to the sandbox number
           - Message format: `join <your-sandbox-code>`
           - Wait for confirmation message
        
        4. **Get Credentials**
           - **Account SID**: From Twilio Console dashboard
           - **Auth Token**: From Twilio Console dashboard (click "View" to reveal)
           - **WhatsApp Number**: The sandbox number (e.g., +14155238886)
        
        5. **Configuration**
           - Add credentials to `.streamlit/secrets.toml`:
           ```toml
           # .streamlit/secrets.toml
           TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
           TWILIO_AUTH_TOKEN = "your_auth_token_here"
           TWILIO_WHATSAPP_NUMBER = "+14155238886"
           ```
        
        6. **Important Notes**
           - ⚠️ Use the exact sandbox number provided by Twilio
           - ⚠️ Don't add "whatsapp:" prefix to the number in secrets.toml
           - ⚠️ Make sure you've joined the sandbox before testing
           - ⚠️ Free sandbox only works with pre-verified numbers
        """)
    
    with tab2:
        st.markdown("### WhatsApp Business API Setup")
        st.markdown("""
        1. **Create Facebook Developer Account**
           - Go to [Facebook Developers](https://developers.facebook.com)
           - Create a new app for WhatsApp Business
        
        2. **Set up WhatsApp Business API**
           - Add WhatsApp product to your app
           - Complete business verification
           - Get phone number ID and access token
        
        3. **Configuration**
           ```toml
           # .streamlit/secrets.toml
           WHATSAPP_ACCESS_TOKEN = "your_access_token"
           WHATSAPP_PHONE_NUMBER_ID = "your_phone_number_id"
           ```
        """)
    
    with tab3:
        st.markdown("### UltraMsg API Setup")
        st.markdown("""
        1. **Create UltraMsg Account**
           - Go to [UltraMsg](https://ultramsg.com)
           - Create an account and instance
        
        2. **Get Credentials**
           - Instance ID: From your UltraMsg dashboard
           - Token: From your UltraMsg dashboard
        
        3. **Configuration**
           ```toml
           # .streamlit/secrets.toml
           ULTRAMSG_TOKEN = "your_token"
           ULTRAMSG_INSTANCE_ID = "your_instance_id"
           ```
        
        4. **Advantages**
           - Supports file uploads (PDFs)
           - Easy to set up
           - Good for small to medium businesses
        """)

# Example usage function
def example_usage():
    """Example of how to use the WhatsApp integration"""
    
    # Initialize WhatsApp integration
    whatsapp = WhatsAppIntegration(provider="ultramsg")  # or "twilio" or "whatsapp_business"
    
    # Example bill data
    bill_data = {
        'bill_number': 'BILL-20231201120000',
        'billing_date': '2023-12-01',
        'shopkeeper_name': 'Gold Palace Jewellers',
        'customer_name': 'John Doe',
        'metal_type': 'Gold',
        'weight': 10.5,
        'base_amount': 55000.00,
        'billing_price': 2000.00,
        'gst_amount': 1710.00,
        'final_amount': 58710.00
    }
    
    # Example PDF buffer (in real usage, this would come from generate_pdf function)
    pdf_buffer = b"dummy_pdf_content"  # This would be actual PDF bytes
    
    # Send bill
    success = whatsapp.send_bill(
        customer_phone="9876543210",
        pdf_buffer=pdf_buffer,
        bill_data=bill_data
    )
    
    return success 