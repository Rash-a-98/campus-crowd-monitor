// Module 1: User Identification Module

export function getClientId() {
  let clientId = localStorage.getItem("client_id");

  if (!clientId) {
    clientId = "user_" + Math.random().toString(36).substring(2, 10);
    localStorage.setItem("client_id", clientId);
  }

  return clientId;
}
