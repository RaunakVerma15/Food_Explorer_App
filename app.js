document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const searchButton = document.getElementById('searchButton');
    const dishesContainer = document.getElementById('dishesContainer');

    // Static credentials
    const validUsername = 'Food_Explorer';
    const validPassword = '1234';

    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            if (username === validUsername && password === validPassword) {
                window.location.href = 'home.html';
            } else {
                document.getElementById('loginError').textContent = 'Invalid credentials. Please try again.';
            }
        });
    }

    if (searchButton) {
        searchButton.addEventListener('click', function () {
            const dish = document.getElementById('searchInput').value;
            handleSearch(dish);
        });

        // Fetch dishes from the backend API
        fetch('http://localhost:5000/dishes')
            .then(response => response.json())
            .then(dishes => {
                dishesContainer.innerHTML = '';
                dishes.forEach(dish => {
                    const dishCard = `
                    <div class="col-md-3 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${dish.name}</h5>
                                <button class="btn btn-primary" onclick="handleSearch('${dish.name}')">View Restaurants</button>
                            </div>
                        </div>
                    </div>`;
                    dishesContainer.innerHTML += dishCard;
                });
            });
    }
});

function handleSearch(dish) {
    window.location.href = `restaurants.html?dish=${encodeURIComponent(dish)}`;
}
