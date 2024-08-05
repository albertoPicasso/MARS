// panelControl.js
document.addEventListener('DOMContentLoaded', () => {
    const panelToggle = document.getElementById('panel-toggle');
    const controlPanel = document.getElementById('control-panel');
    let isPanelOpen = false;

    panelToggle.addEventListener('click', () => {
        isPanelOpen = !isPanelOpen;
        if (isPanelOpen) {
            controlPanel.style.left = '0';
        } else {
            controlPanel.style.left = '-250px'; // Assuming the panel is 250px wide
        }
    });
});
