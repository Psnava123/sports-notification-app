function checkCricketMatches() {
    fetch('/matches/cricket')
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error:', error));
}

function checkFootballMatches() {
    fetch('/matches/football')
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error:', error));
}
