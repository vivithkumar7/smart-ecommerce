import csv
import io
import json
import os
from datetime import timedelta

import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import Order, Product, StoreUser


@staff_member_required
def analytics_dashboard(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=29)
    sales = [
        float(total)
        for total in Order.objects.filter(payment_status="paid").values_list("total", flat=True)
    ]
    revenue_by_day = {}
    for order in Order.objects.filter(payment_status="paid", created_at__date__gte=start_date):
        key = order.created_at.date().isoformat()
        revenue_by_day[key] = round(
            revenue_by_day.get(key, 0) + float(order.total),
            2,
        )

    top_products = []
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT p.name, SUM(oi.quantity) AS units "
            "FROM order_items oi "
            "JOIN orders o ON o.id = oi.order_id "
            "JOIN products p ON p.id = oi.product_id "
            "WHERE o.payment_status = 'paid' GROUP BY p.name "
            "ORDER BY units DESC LIMIT 5"
        )
        top_products = [{"name": row[0], "units": int(row[1])} for row in cursor.fetchall()]

    payment_status_counts = {
        row["payment_status"]: row["count"]
        for row in Order.objects.values("payment_status").annotate(count=Count("id"))
    }

    context = {
        "total_sales": len(sales),
        "total_revenue": round(sum(sales), 2),
        "total_users": StoreUser.objects.count(),
        "failed_payments": payment_status_counts.get("failed", 0),
        "low_stock": list(Product.objects.filter(stock__lte=5, is_active=True).order_by("stock", "name")),
        "revenue_labels": json.dumps(sorted(revenue_by_day)),
        "revenue_values": json.dumps([revenue_by_day[key] for key in sorted(revenue_by_day)]),
        "top_product_labels": json.dumps([item["name"] for item in top_products]),
        "top_product_values": json.dumps([item["units"] for item in top_products]),
        "payment_labels": json.dumps(["Paid", "Failed"]),
        "payment_values": json.dumps([
            payment_status_counts.get("paid", 0),
            payment_status_counts.get("failed", 0),
        ]),
    }
    return render(request, "adminapp/analytics.html", context)


def _report_rows(report_type):
    if report_type == "users":
        return ["ID", "Email"], StoreUser.objects.values_list("id", "email")
    if report_type == "sales":
        return ["Order ID", "User", "Total", "Payment status", "Order status", "Created"], (
            Order.objects.select_related("user").values_list(
                "id", "user__email", "total", "payment_status", "order_status", "created_at"
            )
        )
    return ["Order ID", "User", "Total", "Payment status", "Order status", "Created"], (
        Order.objects.select_related("user").values_list(
            "id", "user__email", "total", "payment_status", "order_status", "created_at"
        )
    )


@staff_member_required
def export_report(request, report_type, file_format):
    headers, rows = _report_rows(report_type)
    filename = f"{report_type}-report"
    if file_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
        return response

    buffer = io.BytesIO()
    document = canvas.Canvas(buffer, pagesize=letter)
    document.setFont("Helvetica-Bold", 14)
    document.drawString(40, 750, f"Smart E-Commerce {report_type.title()} Report")
    document.setFont("Helvetica", 8)
    y = 730
    for row in [headers, *rows]:
        line = " | ".join(str(value)[:35] for value in row)
        document.drawString(40, y, line)
        y -= 14
        if y < 40:
            document.showPage()
            document.setFont("Helvetica", 8)
            y = 750
    document.save()
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}.pdf"'
    return response


@staff_member_required
def returns_dashboard(request):
    """Admin dashboard for managing return requests"""
    admin_key = os.getenv("ORDER_STATUS_ADMIN_KEY", "smart-admin-local-key")
    fastapi_base = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000")
    
    try:
        response = requests.get(
            f"{fastapi_base}/return-requests",
            headers={"X-Admin-Key": admin_key},
            timeout=5
        )
        return_requests = response.json() if response.status_code == 200 else []
    except Exception as e:
        return_requests = []
        error = str(e)
        return render(request, "adminapp/returns.html", {
            "return_requests": return_requests,
            "error": error,
        })
    
    # Group by status
    pending = [r for r in return_requests if r.get("status") == "pending"]
    approved = [r for r in return_requests if r.get("status") == "approved"]
    rejected = [r for r in return_requests if r.get("status") == "rejected"]
    
    context = {
        "return_requests": return_requests,
        "pending_count": len(pending),
        "approved_count": len(approved),
        "rejected_count": len(rejected),
        "pending_requests": pending,
        "approved_requests": approved,
        "rejected_requests": rejected,
    }
    
    return render(request, "adminapp/returns.html", context)


@staff_member_required
@require_http_methods(["POST"])
def update_return_status(request):
    """Update return request status (approve/reject)"""
    import os
    admin_key = os.getenv("ORDER_STATUS_ADMIN_KEY", "smart-admin-local-key")
    fastapi_base = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000")
    
    try:
        body = json.loads(request.body)
        return_id = body.get("return_id")
        new_status = body.get("status")
        
        if not return_id or not new_status:
            return JsonResponse({"error": "Missing return_id or status"}, status=400)
        
        response = requests.patch(
            f"{fastapi_base}/return-requests/{return_id}",
            json={"status": new_status},
            headers={"X-Admin-Key": admin_key},
            timeout=5
        )
        
        if response.status_code in (200, 201):
            return JsonResponse({
                "success": True,
                "message": f"Return request #{return_id} has been {new_status}.",
                "data": response.json()
            })
        else:
            return JsonResponse({
                "success": False,
                "error": response.json().get("detail", "Failed to update return request")
            }, status=response.status_code)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

