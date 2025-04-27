 // Hover effect for pricing cards
function hoverEffect(card) {
    card.classList.toggle('hover-effect');
}

// Page transition effects
document.addEventListener('DOMContentLoaded', () => {
    document.body.style.opacity = '1';
});

// Dark/light mode toggle
const modeToggle = document.createElement('div');
modeToggle.innerHTML = '🌓';
modeToggle.style.position = 'fixed';
modeToggle.style.bottom = '20px';
modeToggle.style.right = '20px';
modeToggle.style.cursor = 'pointer';
modeToggle.style.fontSize = '24px';
modeToggle.style.zIndex = '1000';

modeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});

document.body.appendChild(modeToggle);

// Check for saved mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}
