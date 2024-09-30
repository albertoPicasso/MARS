function openUploadWindow(dbName) {
    const isDarkMode = document.body.classList.contains('dark-mode');
    const url = `/uploadFile?db=${dbName}&darkMode=${isDarkMode}`;
    window.open(url, '_blank');
}
