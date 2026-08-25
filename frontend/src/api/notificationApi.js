import api from "./axios";

export async function getNotifications() {
  const response = await api.get("/notifications");
  return response.data;
}

export async function markNotificationsRead(notificationIds = null) {
  const response = await api.post("/notifications/read", {
    notification_ids: notificationIds,
  });
  return response.data;
}
