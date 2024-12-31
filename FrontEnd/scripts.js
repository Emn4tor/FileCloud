const API_BASE = "http://127.0.0.1:8000"; // backend

// Map file extensions to specific icons
const ICONS = {
    folder: 'folder-icon.png',
    file: 'file-icon.png',
    video: 'video-file.png',
    text: 'txt-file.png',
    photo: 'image-icon.png',
    audio: 'audio-icon.png'
};

function getFileIcon(file) {
    if (file.is_dir) return ICONS.folder;

    const ext = file.name.split('.').pop().toLowerCase();

    if (['mp4', 'mkv', 'avi', 'mov'].includes(ext)) return ICONS.video;
    if (['txt', 'doc', 'docx', 'pdf'].includes(ext)) return ICONS.text;
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'].includes(ext)) return ICONS.photo;
    if (['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(ext)) return ICONS.audio;

    return ICONS.file;
}

// Fetch + display files
async function loadFiles(path = "") {
    const response = await fetch(`${API_BASE}/files?path=${path}`);
    const files = await response.json();

    const fileGrid = document.getElementById('file-grid');
    fileGrid.innerHTML = '';

    files.forEach(file => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const icon = document.createElement('img');
        icon.src = getFileIcon(file);
        fileItem.appendChild(icon);

        const name = document.createElement('div');
        name.textContent = file.name;
        fileItem.appendChild(name);

        fileItem.addEventListener('click', () => {
            if (file.is_dir) {
                document.getElementById('path-input').value = file.path;
                loadFiles(file.path);
            } else {
                window.open(`${API_BASE}/file/${file.path}`);
            }
        });

        fileGrid.appendChild(fileItem);
    });
}

// Upload
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('file-input');
    const uploadPath = document.getElementById('upload-path').value;
    const formData = new FormData();

    formData.append('file', fileInput.files[0]);
    formData.append('target_dir', uploadPath);

    await fetch(`${API_BASE}/file/upload`, {
        method: 'POST',
        body: formData
    });

    alert('File uploaded successfully!');
    loadFiles(uploadPath);
});



// Initialize
loadFiles();
