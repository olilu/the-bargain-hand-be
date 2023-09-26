import smtplib, ssl
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import settings
from pydantic_models.wishlist_game import WishlistGameFull

def send_email(receiver_email: str, bargains: List[WishlistGameFull]):
    table_rows = compile_table_rows(bargains)
    html = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Bootstrap demo</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
    </head>
    <body>
        <div class="row mt-4">
        <div class="col">
        </div>
        <div class="col-6">
            <h3>The mighty Bargain Hand has caught some sales!</h2>
            <hr>
            <p>Let's see what we have for you:</p>
            <table class="table table-striped">
            <thead>
                <tr>
                <th scope="col">Game</th>
                <th scope="col">Link</th>
                <th scope="col">NEW Price</th>
                <th scope="col">OLD Price</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
            </table>
        </div>
        <div class="col">
        </div>
        </div>
    </body>
    </html>
"""
    message = MIMEMultipart()
    message["Subject"] = "Bargain Hand Sales Alert"
    message["From"] = settings.SENDER_EMAIL
    message["To"] = receiver_email
    message.attach(MIMEText(html, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, context=context) as server:
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, receiver_email, message.as_string())


def compile_table_rows(bargains: List[WishlistGameFull]):
    for bargain in bargains:
        row = f"""
        <tr>
            <td>{bargain.name}</td>
            <td><a href="{bargain.link}" target="_blank" style="color: #0d6efd;">{bargain.shop} Link</a></td>
            <td class="text-success fw-bold">{bargain.currency} {'{:.2f}'.format(bargain.price_new)}</td>              
            <td class="text-decoration-line-through .fs-6 text fw-lighter text-secondary">{bargain.currency} {'{:.2f}'.format(bargain.price_old)}</td>
        </tr>
        """
        yield row
    

