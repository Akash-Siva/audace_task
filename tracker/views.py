# Create your views here.
import json
import requests
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
import numpy as np


def render_index(request):
    """
    Method to render the line chart
    """
    return render(request, 'index.html')

def render_chart(request):
    """
    Method to fetch data from CoinGecko for the line chart.
    """
    
    url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
    params = {
        "vs_currency": "inr",
        "days": "1",  # Change to "30" for 30 days; "1" for 24 hours; "max" for max available data
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        total_price = 0
        total_volume = 0
        total_liquidity = 0
        num_points = len(data['prices'])

        formatted_data = []
        for i in range(len(data['prices'])):
            timestamp = data['prices'][i][0] / 1000  # Convert to seconds
            date = datetime.fromtimestamp(timestamp).isoformat()
            price = data['prices'][i][1]
            volume = data['total_volumes'][i][1]
            market_cap = data['market_caps'][i][1]

            total_price += price
            total_volume += volume
            total_liquidity += market_cap

            formatted_data.append({
                "date": date,
                "price": price,
                "volume": volume,
                "market_cap": market_cap
            })
        
         # Calculate averages
        avg_volume = total_volume / num_points
        avg_liquidity = total_liquidity / num_points
        avg_price = total_price / num_points

        averages = {
            'avg_volume': round(avg_volume, 2),
            'avg_liquidity': round(avg_liquidity, 2),
            'total_price':  round(avg_price, 2)
        }

        # Pass formatted data to template as JSON
        context = {
            "chart_data": json.dumps(formatted_data),
            "averages": averages
        }
        return JsonResponse(context)

    return JsonResponse({"error": "Failed to fetch data from CoinGecko"}, status=500)


def render_metrics(request):
    """
    Method to render metrics chart
    """
    return render(request, 'token_metrics.html')

def summarize_token_metrics(request):
    """
    Method to fetch data for metrics chart
    """
    token_id="ethereum"
    days="1"
    try:
        # Fetch historical data from Coingecko
        url = "https://api.coingecko.com/api/v3/coins/ethereum/market_chart"
        params = {
            "vs_currency": 'inr',
            "days": days,
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

        data = response.json()

        # Extract price data
        prices = [
            {"timestamp": p[0], "price": p[1]} for p in data["prices"]
        ]

        # Calculate metrics
        price_values = [p["price"] for p in prices]
        avg_price = np.mean(price_values)
        std_dev_price = np.std(price_values)
        max_price = max(price_values)
        min_price = min(price_values)

        # Detect spikes and dips
        threshold = 2 * std_dev_price  # Define spike/dip threshold
        spikes = [
            {"date": datetime.fromtimestamp(p["timestamp"] / 1000).isoformat(), "price": p["price"]}
            for p in prices if p["price"] > avg_price + threshold
        ]

        dips = [
            {"date": datetime.fromtimestamp(p["timestamp"] / 1000).isoformat(), "price": p["price"]}
            for p in prices if p["price"] < avg_price - threshold
        ]
            
        # Format results
        summary = {
            "token_id": token_id,
            "date_range": f"Last {days} days",
            "average_price": round(avg_price, 2),
            "highest_price": round(max_price, 2),
            "lowest_price": round(min_price, 2),
            "price_spikes": spikes,
            "price_dips": dips,
        }
        
        if len(spikes) == 0:
            summary['spikes'] = "No price spikes detected"
        if len(dips) == 0:
            summary['dips'] = "No price dips detected"

        context = {
            "chart_data": json.dumps(summary)
        }
        return JsonResponse(context)

    except Exception as e:
        print(f"Error occurred: {e}")
        return None
