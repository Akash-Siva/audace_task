import requests
import logging
from celery import shared_task
from .models import TokenData
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@shared_task
def fetch_token_data():
    """
    Method to fetch data for the past 24 hours to create line chart. The data is also being saved
    in sqlite3 database for comparison. This method is called every 5 minutes.
    """
    try:
        COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "inr",
            "ids": "ethereum",
            "order": "market_cap_desc",
            "per_page": 1,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }

        logger.info(f"Sending request to {COINGECKO_API_URL} with params: {params}")

        response = requests.get(COINGECKO_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()[0]
            logger.info(f"Fetched data: {data}")

            # Example saving data to the database
            token_data = TokenData(
                name=data['name'],
                symbol=data['symbol'].upper(),
                price_inr=data['current_price'],  
                market_cap_inr=data['market_cap'],
                volume_inr=data['total_volume'],
                price_change_24h=data['price_change_percentage_24h']
            )
            token_data.save()
            logger.info("Data saved successfully.")

        else:
            logger.error(f"Failed to fetch data. Status code: {response.status_code}, Response: {response.text}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

ALERT_THRESHOLD = 5

@shared_task
def calculate_percentage_change():
    """
    Method to send mail to the user, in this case myself when the threshold exceeds 5%.
    Implementing registration would make it easier to send mails to users automatically.
    """
    last_two_records = TokenData.objects.order_by('-id')[:2]

    if len(last_two_records) < 2:
        print("Not enough data to calculate percentage change.")
        return

    latest_record = last_two_records[0]
    previous_record = last_two_records[1]

    latest_price = latest_record.price_inr
    previous_price = previous_record.price_inr

    percentage_change = ((latest_price - previous_price) / previous_price) * 100

    print(f"====================================> Percentage Change: {percentage_change:.2f}%")

    if abs(percentage_change) >= ALERT_THRESHOLD:
        subject = "Token Price Alert: Significant Change Detected"
        message = (
            f"The price of {latest_record.name} has changed by {percentage_change:.2f}% "
            f"in the last 5 minutes.\n"
            f"Previous Price: rs{previous_price:.2f}\n"
            f"Latest Price: rs{latest_price:.2f}\n"
            f"Please take appropriate action."
        )
        recipient_list = ['akashsiva569@gmail.com', 'balagurunadhaswamy.ts@gmail.com']  # Replace with actual client emails

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        print("Alert email sent to clients.")
    else:
        print("No significant price change detected; no email sent.")