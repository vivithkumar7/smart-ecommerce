import os
import requests
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


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
    import json
    
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
