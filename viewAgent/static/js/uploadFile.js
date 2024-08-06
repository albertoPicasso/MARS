function openFileDialog() {
    document.getElementById('fileInput').click();
}


document.getElementById('fileInput').addEventListener('change', function() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = ''; 

    for (const file of this.files) {
        const listItem = document.createElement('li');
        listItem.textContent = file.name;
        fileList.appendChild(listItem);
    }
});
