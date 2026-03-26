// Module 2: GPS Permission & Location Capture Module

export function getCurrentLocation(successCallback, errorCallback) {
  if (!("geolocation" in navigator)) {
    errorCallback("Geolocation not supported");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    position => {
      successCallback(
        position.coords.latitude,
        position.coords.longitude
      );
    },
    () => {
      errorCallback("Location permission denied");
    }
  );
}
