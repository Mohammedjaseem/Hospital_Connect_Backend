import os
import requests
from django.views.decorators.csrf import csrf_exempt
from connect_bills.models import WhatsAppBill


@csrf_exempt
def send_whatsapp_message(request, passing_data, type, sent_to, org):
    
        #token fetch
        app_id = os.getenv("WA_APP_ID")
        access_token = os.getenv("WA_ACCESS")
        
        #api url
        graph_api_url = f'https://graph.facebook.com/v18.0/{app_id}/messages'

        # Your whsatapp page access token
        access_token = f'{access_token}'
        
        # Headers for the request
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }
        
        #data from function
        data = passing_data
        
        # Make the POST request with JSON data
        response = requests.post(graph_api_url, headers=headers, json=data)
        

        if response.status_code == 200:
            try:
                #updateing the biller function
                bill = WhatsAppBill()
                bill.type=type
                bill.sent_to=sent_to
                bill.save()
            except Exception as e:
                print(f"Error updating bill: {e}")
            return True
        else:
            return response.text