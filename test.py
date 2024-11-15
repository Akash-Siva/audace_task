import requests
from datetime import datetime, timedelta

def calculate_daily_averages(token_id="ethereum", vs_currency="inr", days="1"):
    try:
        # Fetch historical data from Coingecko
        url = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart"
        params = {
            "vs_currency": vs_currency,
            "days": days,
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

        data = response.json()

        # Initialize accumulators
        total_price = 0
        total_volume = 0
        total_liquidity = 0
        num_points = len(data['prices'])  # Use the same count for prices, volumes, and liquidity

        # Calculate sums
        for i in range(num_points):
            timestamp = data['prices'][i][0] / 1000  # Convert to seconds
            price = data['prices'][i][1]
            volume = data['total_volumes'][i][1]
            market_cap = data['market_caps'][i][1]  # Approximation for liquidity

            total_price += price
            total_volume += volume
            total_liquidity += market_cap

        # Calculate averages
        avg_price = total_price / num_points
        avg_volume = total_volume / num_points
        avg_liquidity = total_liquidity / num_points

        # Format results
        return {
            "token_id": token_id,
            "average_price": avg_price,
            "average_volume": avg_volume,
            "average_liquidity": avg_liquidity,
            "date_range": f"Last {days} days"
        }

    except Exception as e:
        print(f"Error occurred: {e}")
        return None


# Example usage
averages = calculate_daily_averages(token_id="ethereum", vs_currency="inr", days="1")
if averages:
    print(f"Daily Averages for {averages['token_id']}:")
    print(f"  Average Price: rs {averages['average_price']:.2f}")
    print(f"  Average Volume: rs {averages['average_volume']:.2f}")
    print(f"  Average Liquidity: rs {averages['average_liquidity']:.2f}")
    print(f"  Date Range: {averages['date_range']}")
