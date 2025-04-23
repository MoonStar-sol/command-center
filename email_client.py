import os
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv
import openai
import argparse

# Load environment variables
load_dotenv()

class EmailClient:
    def __init__(self):
        # IMAP Configuration
        self.imap_host = os.getenv('IMAP_HOST')
        self.imap_port = int(os.getenv('IMAP_PORT'))
        self.imap_user = os.getenv('IMAP_USER')
        self.imap_password = os.getenv('IMAP_PASSWORD')
        self.imap_use_ssl = os.getenv('IMAP_USE_SSL', 'True').lower() == 'true'

        # SMTP Configuration
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

        # OpenAI Configuration
        openai.api_key = os.getenv('OPENAI_API_KEY')

        # Initialize connections
        self.imap = None
        self.smtp = None

    def connect_imap(self):
        """Connect to IMAP server"""
        try:
            if self.imap_use_ssl:
                self.imap = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            else:
                self.imap = imaplib.IMAP4(self.imap_host, self.imap_port)
            
            self.imap.login(self.imap_user, self.imap_password)
            self.imap.select('INBOX')
            return True
        except Exception as e:
            print(f"IMAP Connection Error: {str(e)}")
            return False

    def connect_smtp(self):
        """Connect to SMTP server"""
        try:
            self.smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
            self.smtp.starttls()
            self.smtp.login(self.smtp_user, self.smtp_password)
            return True
        except Exception as e:
            print(f"SMTP Connection Error: {str(e)}")
            return False

    def decode_subject(self, subject):
        """Decode email subject"""
        decoded = []
        for part, encoding in decode_header(subject):
            if isinstance(part, bytes):
                decoded.append(part.decode(encoding or 'utf-8'))
            else:
                decoded.append(part)
        return ''.join(decoded)

    def get_unread_emails(self):
        """Get all unread emails"""
        if not self.imap:
            if not self.connect_imap():
                return []

        try:
            _, messages = self.imap.search(None, 'UNSEEN')
            email_list = []
            
            for num in messages[0].split():
                # Use BODY.PEEK instead of RFC822 to prevent marking as read
                _, msg_data = self.imap.fetch(num, '(BODY.PEEK[])')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = self.decode_subject(email_message['subject'])
                from_addr = email_message['from']
                date = email_message['date']
                
                content = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            content = part.get_payload(decode=True).decode()
                            break
                else:
                    content = email_message.get_payload(decode=True).decode()
                
                email_list.append({
                    'uid': num.decode(),
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'content': content
                })
            
            return email_list
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")
            return []

    def summarize_emails(self, emails):
        """Summarize all unread emails using OpenAI"""
        if not emails:
            return "No unread emails to summarize."

        combined_content = "\n\n".join([
            f"From: {email['from']}\nSubject: {email['subject']}\nDate: {email['date']}\nContent: {email['content']}"
            for email in emails
        ])

        try:
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes emails concisely."},
                    {"role": "user", "content": f"Please summarize these emails:\n\n{combined_content}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error summarizing emails: {str(e)}")
            return "Failed to generate summary."

    def respond_to_oldest_email(self, email, response_content):
        """Send a reply to the oldest unread email"""
        if not self.smtp:
            if not self.connect_smtp():
                return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = email['from']
            
            subject = email['subject']
            if not subject.startswith('Re:'):
                subject = f"Re: {subject}"
            msg['Subject'] = subject
            
            msg.attach(MIMEText(response_content, 'plain'))
            
            self.smtp.send_message(msg)
            
            # Mark email as read
            self.imap.store(email['uid'], '+FLAGS', '\\Seen')
            
            return True
        except Exception as e:
            print(f"Error sending reply: {str(e)}")
            return False

    def send_email(self, recipient, subject, body):
        """Send a new email"""
        if not self.smtp:
            if not self.connect_smtp():
                print("SMTP Connection Error: Failed to connect.")
                return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            self.smtp.send_message(msg)
            print(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def close_connections(self):
        """Close all connections"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
        if self.smtp:
            try:
                self.smtp.quit()
            except:
                pass

    def display_unread_emails(self, emails):
        """Display crucial information about unread emails"""
        if not emails:
            print("No unread emails found.")
            return

        print(f"\nFound {len(emails)} unread email(s):")
        print("-" * 50)
        
        for idx, email in enumerate(emails, 1):
            print(f"\nEmail {idx}:")
            print(f"From: {email['from']}")
            print(f"Subject: {email['subject']}")
            print(f"Date: {email['date']}")
            print(f"Preview: {email['content'][:150]}..." if len(email['content']) > 150 else f"Preview: {email['content']}")
            print("-" * 50)

    def get_email_thread(self, message_id):
        """Get all emails in a thread using the References header"""
        if not self.imap:
            if not self.connect_imap():
                return []

        try:
            # Search for emails with matching References or In-Reply-To
            search_criteria = f'(OR HEADER References "{message_id}" HEADER In-Reply-To "{message_id}")'
            _, messages = self.imap.search(None, search_criteria)
            
            thread_emails = []
            for num in messages[0].split():
                _, msg_data = self.imap.fetch(num, '(BODY.PEEK[])')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = self.decode_subject(email_message['subject'])
                from_addr = email_message['from']
                date = email_message['date']
                
                content = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            content = part.get_payload(decode=True).decode()
                            break
                else:
                    content = email_message.get_payload(decode=True).decode()
                
                thread_emails.append({
                    'uid': num.decode(),
                    'from': from_addr,
                    'subject': subject,
                    'date': date,
                    'content': content,
                    'message_id': email_message['Message-ID']
                })
            
            # Sort emails by date
            thread_emails.sort(key=lambda x: x['date'])
            return thread_emails
        except Exception as e:
            print(f"Error fetching email thread: {str(e)}")
            return []

    def get_recent_email(self):
        """Get the most recent email and its thread"""
        if not self.imap:
            if not self.connect_imap():
                return None

        try:
            # Search for all emails, sorted by date in descending order
            _, messages = self.imap.search(None, 'ALL')
            if not messages[0]:
                return None

            # Get the most recent email
            num = messages[0].split()[-1]
            _, msg_data = self.imap.fetch(num, '(BODY.PEEK[])')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Get the Message-ID of the most recent email
            message_id = email_message['Message-ID']
            if not message_id:
                return None

            # Get the entire thread
            thread_emails = self.get_email_thread(message_id)
            
            if not thread_emails:
                return None

            return {
                'thread': thread_emails,
                'most_recent': thread_emails[-1]  # Last email in the sorted thread
            }
        except Exception as e:
            print(f"Error fetching recent email: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Email Client for Summarization and Response')
    parser.add_argument('--summarize', action='store_true', help='Summarize all unread emails')
    parser.add_argument('--respond', action='store_true', help='Respond to oldest unread email')
    parser.add_argument('--check', action='store_true', help='Display information about unread emails')
    parser.add_argument('--recent', action='store_true', help='Read the most recent email and its thread')
    parser.add_argument('--send', action='store_true', help='Send a new email')
    parser.add_argument('--recipient', type=str, help='Recipient email address (required for --send)')
    parser.add_argument('--subject', type=str, help='Email subject (required for --send)')
    parser.add_argument('--body', type=str, help='Email body (required for --send or --respond)')
    args = parser.parse_args()

    client = EmailClient()
    
    try:
        if args.send:
            if not args.recipient or not args.subject or not args.body:
                print("Error: --recipient, --subject, and --body are required when using --send.")
                return
            if client.connect_smtp():
                client.send_email(args.recipient, args.subject, args.body)
            else:
                print("Failed to connect to SMTP server to send email.")
            return

        if args.recent:
            recent_email = client.get_recent_email()
            if recent_email:
                print("\nEmail Thread:")
                print("-" * 50)
                for idx, email in enumerate(recent_email['thread'], 1):
                    print(f"\nMessage {idx}:")
                    print(f"From: {email['from']}")
                    print(f"Subject: {email['subject']}")
                    print(f"Date: {email['date']}")
                    print("\nContent:")
                    print("-" * 50)
                    print(email['content'])
                    print("-" * 50)
            else:
                print("No emails found in the inbox.")
            return

        unread_emails = client.get_unread_emails()
        
        if args.check:
            client.display_unread_emails(unread_emails)
            return

        if not unread_emails:
            print("No unread emails found.")
            return

        if args.summarize:
            summary = client.summarize_emails(unread_emails)
            print("\nEmail Summary:")
            print(summary)

        if args.respond and unread_emails:
            if not args.body:
                print("Error: --body is required when using --respond.")
                return
                
            oldest_email = unread_emails[0]  # First email is the oldest
            print(f"\nResponding to oldest unread email:")
            print(f"From: {oldest_email['from']}")
            print(f"Subject: {oldest_email['subject']}")
            
            response_content = args.body # Use the body argument
            if client.respond_to_oldest_email(oldest_email, response_content):
                print("Response sent successfully!")
            else:
                print("Failed to send response.")

    finally:
        client.close_connections()

if __name__ == "__main__":
    main() 