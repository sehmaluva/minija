from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.forecast.models.models import HistoricalEntry
from datetime import timedelta


def simple_linear_predict(xs, ys):
    # simple least-squares line fit y = a*x + b; xs expected as 0..n-1
    n = len(xs)
    if n == 0:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den = sum((x - mean_x) ** 2 for x in xs)
    if den == 0:
        return ys[-1]
    a = num / den
    b = mean_y - a * mean_x
    return a * (n) + b

class FeedPredictionView(APIView):
    """Predict next day's feed requirement (kg) using a simple linear trend on recent entries."""

    def get(self, request):
        days = int(request.query_params.get("days", 7))
        entries = HistoricalEntry.objects.all().order_by("-date")[:days]
        entries = list(reversed(entries))
        if not entries:
            return Response({"error": "no data"}, status=status.HTTP_400_BAD_REQUEST)
        xs = list(range(len(entries)))
        ys = [float(e.feed_kg) for e in entries]
        pred = simple_linear_predict(xs, ys)
        return Response({"predicted_feed_kg": round(pred, 2)})
