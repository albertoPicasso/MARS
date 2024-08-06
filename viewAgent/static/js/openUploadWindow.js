function openUploadWindow(dbName) {
    const url = `/uploadFile?db=${dbName}`;
    window.open(url, '_blank');
}