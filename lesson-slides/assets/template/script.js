// Inizializzazione variabili
let currentSlideIndex = 0;
const slides = document.querySelectorAll('.slide');
const counterDisplay = document.getElementById('slide-counter');

// ===== NAVIGAZIONE =====
function showSlide(index) {
    if (index >= slides.length) {
        currentSlideIndex = 0;
    } else if (index < 0) {
        currentSlideIndex = slides.length - 1;
    } else {
        currentSlideIndex = index;
    }

    slides.forEach(slide => slide.classList.remove('active'));
    slides[currentSlideIndex].classList.add('active');
    counterDisplay.innerText = `${currentSlideIndex + 1} / ${slides.length}`;

}

function nextSlide() { showSlide(currentSlideIndex + 1); }
function prevSlide() { showSlide(currentSlideIndex - 1); }

document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight' || event.key === ' ') {
        event.preventDefault();
        nextSlide();
    } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        prevSlide();
    }
});

// Avvio
showSlide(currentSlideIndex);
