import smtplib
from src.config.config import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from jinja2 import Template
import pathlib

current_dir = pathlib.Path().cwd() / "src/services/gmailer/"

class SMTPGmailer:
    """A class to handle sending emails using Gmail's SMTP server.

    This class provides functionality to send emails with an HTML template 
    and dynamic content using the Jinja2 templating engine.

    Attributes:
        sender_email (str): The email address of the sender (Gmail account).
        sender_password (str): The password or app password for the sender's Gmail account.
        template (Template): The Jinja2 template object to render HTML emails.

    Methods:
        send_mail(recipient_email: str, subject: str, context: dict):
            Sends an HTML email to the specified recipient using the provided context.
    """

    def __init__(self):
        """Initializes the SMTPGmailer instance with sender email, password, 
        and loads the HTML email template.

        Reads the email template located at 'src/services/gmailer/templates/client-check.html'
        and prepares it for dynamic rendering.
        """
        self.sender_email = settings.gmail_sender
        self.sender_password = settings.gmail_password

        # HTML Template
        with open(current_dir / 'templates/client-check.html', 'r') as file:
            self.template = Template(file.read())

    
    async def send_mail(self, recipient_email: str, subject: str, context: dict):
        """Sends an email with the specified subject and context to the given recipient.

        Args:
            recipient_email (str): The recipient's email address.
            subject (str): The subject of the email.
            context (dict): A dictionary of key-value pairs to populate the template with.

        Raises:
            Exception: If there is any error during the email sending process, an exception is raised.

        Example:
            await send_mail(
                recipient_email="recipient@example.com",
                subject="Subject Here",
                context={"name": "John", "date": "2025-03-25"}
            )
        """
    
        html_msg = self.template.render(context)
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg.attach(MIMEText(html_msg, 'html'))
        
        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, msg.as_string())
            print("Message was successfully sended!")
        except Exception as e:
            print(f"Error: {e}")


    
MAILER = SMTPGmailer()