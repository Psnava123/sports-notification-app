self.addEventListener("push", function(event) {
    var options = {
        body: event.data.text(),
        icon: "https://example.com/match-icon.png", // Replace with a valid icon URL
        badge: "https://example.com/match-badge.png", // Optional: Add a badge for the notification
    };

    event.waitUntil(
        self.registration.showNotification("Upcoming Match", options)
    );
});
