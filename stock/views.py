from django.db.models import Sum, F, Max, Min
from datetime import timedelta, date
import math
import numpy as np
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Stock


def get_request_params(request):
    """Process request parameters: brand and period"""
    # Handle brand parameter (default: Apple)
    brand = request.GET.get('brand', 'Apple').strip() if request.method == 'GET' else request.data.get('brand', 'Apple').strip()
    if not brand:
        brand = 'Apple'

    # Handle period parameters (default: week=1)
    try:
        if request.method == 'GET':
            week = int(request.GET.get('week', 1))
            month = int(request.GET.get('month', 0))
            year = int(request.GET.get('year', 0))
        else:
            week = int(request.data.get('week', 1))
            month = int(request.data.get('month', 0))
            year = int(request.data.get('year', 0))
    except (ValueError, TypeError):
        week, month, year = 1, 0, 0

    # Determine period (priority: year > month > week)
    period = 'week'
    if month == 1:
        period = 'month'
    if year == 1:
        period = 'year'

    # Calculate date range
    today = date.today()
    period_map = {
        'week': timedelta(days=7),
        'month': timedelta(days=30),
        'year': timedelta(days=365)
    }

    return {
        'brand': brand,
        'period': period,
        'start_date': today - period_map[period],
        'end_date': today
    }


def get_aggregated_data(brand, period, start_date, end_date):
    """Aggregate stock data by brand and period"""
    base_qs = Stock.objects.filter(
        brand=brand,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    if not base_qs.exists():
        return []

    if period == 'week':
        return [
            {
                'date': item.date.strftime('%Y-%m-%d'),
                'open': float(item.open),
                'close': float(item.close),
                'high': float(item.high),
                'low': float(item.low),
                'volume': item.volume
            }
            for item in base_qs
        ]
    elif period == 'month':
        return [
            {
                'date': item.date.strftime('%Y-%m-%d'),
                'open': float(item.open),
                'close': float(item.close),
                'high': float(item.high),
                'low': float(item.low),
                'volume': item.volume
            }
            for item in base_qs
        ]
    elif period == 'year':
        month_data = base_qs.values(
            year=F('date__year'),
            month=F('date__month')
        ).annotate(
            first_date=Min('date'),
            open=Min('open'),
            close=Max('close'),
            high=Max('high'),
            low=Min('low'),
            volume=Sum('volume')
        ).order_by('year', 'month')

        return [
            {
                'date': item['first_date'].strftime('%Y-%m'),
                'open': float(item['open']),
                'close': float(item['close']),
                'high': float(item['high']),
                'low': float(item['low']),
                'volume': item['volume']
            }
            for item in month_data
        ]
    return []


def calculate_key_indicators(brand, start_date, end_date):
    """Calculate key time series indicators"""
    indicators = {}
    stock_qs = Stock.objects.filter(brand=brand, date__range=(start_date, end_date))

    # 1. Volatility (historical volatility, annualized)
    if stock_qs.count() >= 2:
        daily_returns = []
        prev_close = None
        for stock in stock_qs.order_by('date'):
            if prev_close is not None:
                ret = (float(stock.close) - float(prev_close)) / float(prev_close)
                daily_returns.append(ret)
            prev_close = stock.close

        if daily_returns:
            std_dev = np.std(daily_returns)
            annual_volatility = float(std_dev) * math.sqrt(252)
            indicators['Volatility'] = f"{annual_volatility * 100:.2f}%"
    else:
        indicators['Volatility'] = "N/A"

    # 2. Market Value
    total_shares = 100000000  # Assumed total shares
    if stock_qs.exists():
        market_value = float(stock_qs.last().close) * total_shares
        indicators['Market Value'] = f"{market_value / 100000000:.2f} trillion"
    else:
        indicators['Market Value'] = "N/A"

    # 3. Trading Volume statistics
    volume_sum = stock_qs.aggregate(total_volume=Sum('volume'))['total_volume']
    if volume_sum:
        indicators['Trading Volume'] = f"{volume_sum / 100000000:.2f} hundred million"
        yesterday = end_date - timedelta(days=1)
        yesterday_volume = Stock.objects.filter(brand=brand, date=yesterday).aggregate(yesterday_vol=Sum('volume'))['yesterday_vol']
        if yesterday_volume:
            change_amt = volume_sum - yesterday_volume
            change_pct = (change_amt / yesterday_volume) * 100 if yesterday_volume != 0 else 0
            indicators['Volume Change'] = {
                "Change from previous day": change_amt,
                "Percentage change from previous day": f"{change_pct:.2f}%"
            }
    else:
        indicators['Trading Volume'] = "N/A"

    # 4. Historical Return (annualized)
    if stock_qs.count() >= 2:
        start_price = float(stock_qs.first().close)
        end_price = float(stock_qs.last().close)
        period_days = (end_date - start_date).days
        if period_days != 0:
            simple_return = (end_price / start_price - 1)
            annual_return = simple_return * (365 / period_days)
            indicators['Historical Return (Annualized)'] = f"{annual_return * 100:.2f}%"
        else:
            indicators['Historical Return (Annualized)'] = "N/A"
    else:
        indicators['Historical Return (Annualized)'] = "N/A"

    return indicators


class MarketShowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        params = get_request_params(request)
        data = get_aggregated_data(
            brand=params['brand'],
            period=params['period'],
            start_date=params['start_date'],
            end_date=params['end_date']
        )
        key_indicators = calculate_key_indicators(
            brand=params['brand'],
            start_date=params['start_date'],
            end_date=params['end_date']
        )

        if not data:
            return Response({
                'status': 'warning',
                'message': f'No data found for brand "{params["brand"]}" in the specified period',
                'used_params': params,
                'key_indicators': key_indicators
            }, status=200)

        return Response({
            'status': 'success',
            'used_params': {
                'brand': params['brand'],
                'period': params['period'],
                'date_range': {
                    'start': params['start_date'].strftime('%Y-%m-%d'),
                    'end': params['end_date'].strftime('%Y-%m-%d')
                }
            },
            'key_indicators': key_indicators,
            'data': data,
            'count': len(data)
        })

    def post(self, request):
        brand = request.data.get('brand', 'Apple').strip()
        if not brand:
            brand = 'Apple'

        try:
            week = int(request.data.get('week', 1))
            month = int(request.data.get('month', 0))
            year = int(request.data.get('year', 0))
        except (ValueError, TypeError):
            brand = 'Apple'
            week, month, year = 1, 0, 0

        period = 'week'
        if month == 1:
            period = 'month'
        if year == 1:
            period = 'year'

        today = date.today()
        period_map = {
            'week': timedelta(days=7),
            'month': timedelta(days=30),
            'year': timedelta(days=365)
        }
        start_date = today - period_map[period]
        end_date = today

        data = get_aggregated_data(
            brand=brand,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        key_indicators = calculate_key_indicators(
            brand=brand,
            start_date=start_date,
            end_date=end_date
        )

        if not data:
            return Response({
                'status': 'warning',
                'message': f'No data found for brand "{brand}" in the specified period',
                'used_params': {
                    'brand': brand,
                    'period': period,
                    'start_date': start_date,
                    'end_date': end_date
                },
                'key_indicators': key_indicators
            }, status=200)

        return Response({
            'status': 'success',
            'used_params': {
                'brand': brand,
                'period': period,
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            },
            'key_indicators': key_indicators,
            'data': data,
            'count': len(data)
        })
