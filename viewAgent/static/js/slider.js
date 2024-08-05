const dbSlider = document.getElementById('dbSlider');
const selectedValue = document.getElementById('selectedValue');

dbSlider.addEventListener('input', (event) => {
    const value = event.target.value;
    currentDB = `db${value}`;
    selectedValue.textContent = `db${value}`;
    updateChat();
});
