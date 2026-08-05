import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import requests
from livekit.agents import function_tool, RunContext


@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """Get the current weather for a given city."""
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3", timeout=10)
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Sorry, couldn't retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"Sorry, couldn't retrieve weather for {city}."


@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """Search the web using DuckDuckGo's public API."""
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        elif data.get("RelatedTopics"):
            related = [
                t.get("Text", "")
                for t in data["RelatedTopics"]
                if isinstance(t, dict) and "Text" in t
            ]
            if related:
                return "\n".join(related[:5])

        return f"No clear results found for '{query}'."
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"Error while searching the web: {str(e)}"


@function_tool()
async def send_email(
    context: RunContext,
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None,
) -> str:
    """Send an email through Gmail.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")

        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Gmail credentials not found."

        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject

        recipients = [to_email]
        if cc_email:
            msg["Cc"] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())
        server.quit()

        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"

    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"Sorry, couldn't send email: {str(e)}"
