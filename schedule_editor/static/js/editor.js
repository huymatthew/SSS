// Global variables
let currentZoom = 1;
let isDragging = false;
let dragStart = { x: 0, y: 0 };
let canvasOffset = { x: 0, y: 0 };
let subjects = [];
let scheduleId = document.getElementById('schedule-id').getAttribute('value');

// Initialize the app
document.addEventListener('DOMContentLoaded', function () {
    loadSubjects();
    initializeCanvas();
    drawGrid();
});

// Subject management functions
async function loadSubjects() {
    try {
        const response = await fetch(`/schedule-editor/api/subjects/?schedule_id=${encodeURIComponent(scheduleId)}`);
        const data = await response.json();
        subjects = data.subjects;
        renderSubjects();
    } catch (error) {
        console.error('Lỗi khi tải danh sách môn học:', error);
    }
}

function renderSubjects() {
    const subjectsList = document.getElementById('subjects-list');
    subjectsList.innerHTML = '';

    subjects.forEach(subject => {
        const subjectElement = document.createElement('div');
        subjectElement.className = 'subject-item';
        subjectElement.innerHTML = `
                    <div class="subject-color" style="background-color: ${subject.color}"></div>
                    <div class="subject-info">
                        <div class="subject-code">${subject.code}</div>
                        <div class="subject-name">${subject.name}</div>
                        <div class="subject-credits">${subject.credits} tín chỉ</div>
                    </div>
                    <div class="subject-actions">
                        <button class="action-btn" onclick="deleteSubject(${subject.id})" title="Xóa">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
        subjectsList.appendChild(subjectElement);
    });
}

async function deleteSubject(subjectId) {
    if (!confirm('Bạn có chắc chắn muốn xóa môn học này khỏi lịch học?')) return;

    try {
        const response = await fetch('/schedule-editor/api/schedule-item/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                schedule_id: scheduleId,
                item_id: subjectId
            })
        });

        const result = await response.json();

        if (result.success) {
            loadSubjects(); // Reload subjects
        } else {
            alert('Lỗi: ' + result.error);
        }
    } catch (error) {
        console.error('Lỗi khi xóa môn học:', error);
        alert('Có lỗi xảy ra khi xóa môn học');
    }
}

// Search Subject Modal functions
let searchTimeout;

function openSearchSubjectModal() {
    document.getElementById('search-subject-modal').style.display = 'block';
    document.getElementById('search-input').value = '';
    document.getElementById('search-results').innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search" style="font-size: 48px; color: #bdc3c7; margin-bottom: 15px;"></i>
                    <p>Nhập từ khóa để tìm kiếm môn học</p>
                </div>
            `;
    setTimeout(() => document.getElementById('search-input').focus(), 100);
}

function closeSearchSubjectModal() {
    document.getElementById('search-subject-modal').style.display = 'none';
}

async function searchSubjects(query) {
    if (!query.trim()) {
        document.getElementById('search-results').innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-search" style="font-size: 48px; color: #bdc3c7; margin-bottom: 15px;"></i>
                        <p>Nhập từ khóa để tìm kiếm môn học</p>
                    </div>
                `;
        return;
    }

    try {
        document.getElementById('search-results').innerHTML = `
                    <div class="loading">
                        <i class="fas fa-spinner fa-spin"></i> Đang tìm kiếm...
                    </div>
                `;

        const response = await fetch(`/schedule-editor/api/search-subjects/?q=${encodeURIComponent(query)}&limit=20`);
        const data = await response.json();

        if (data.subjects.length === 0) {
            document.getElementById('search-results').innerHTML = `
                        <div class="no-results">
                            <i class="fas fa-exclamation-circle" style="font-size: 48px; color: #bdc3c7; margin-bottom: 15px;"></i>
                            <p>Không tìm thấy môn học nào</p>
                        </div>
                    `;
            return;
        }

        const resultsHtml = data.subjects.map(subject => {
            const dayNames = {
                1: 'Thứ 2', 2: 'Thứ 3', 3: 'Thứ 4', 4: 'Thứ 5',
                5: 'Thứ 6', 6: 'Thứ 7', 7: 'Chủ Nhật'
            };

            const timeInfo = subject.day && subject.startperiod && subject.endperiod ?
                `${dayNames[subject.day]}: ${subject.startperiod}-${subject.endperiod}` : '';

            return `
                        <div class="search-result-item" onclick="selectSubject(${subject.id})">
                            <div class="result-header">
                                <div class="result-code">${subject.code}</div>
                                <div class="result-credits">${subject.credits} tín chỉ</div>
                            </div>
                            <div class="result-name">${subject.name}</div>
                            <div class="result-details">
                                ${subject.professor ? `<span class="result-detail">GV: ${subject.professor}</span>` : ''}
                                ${timeInfo ? `<span class="result-detail">${timeInfo}</span>` : ''}
                                ${subject.room ? `<span class="result-detail">Phòng: ${subject.room}</span>` : ''}
                                ${subject.semester ? `<span class="result-detail">HK: ${subject.semester}</span>` : ''}
                            </div>
                        </div>
                    `;
        }).join('');

        document.getElementById('search-results').innerHTML = resultsHtml;

    } catch (error) {
        console.error('Lỗi khi tìm kiếm:', error);
        document.getElementById('search-results').innerHTML = `
                    <div class="no-results">
                        <i class="fas fa-exclamation-triangle" style="font-size: 48px; color: #e74c3c; margin-bottom: 15px;"></i>
                        <p>Có lỗi xảy ra khi tìm kiếm</p>
                    </div>
                `;
    }
}

function selectSubject(subjectId) {
    // Check if subject is already in the list
    const existingSubject = subjects.find(s => s.id === subjectId);
    if (existingSubject) {
        alert('Môn học này đã có trong danh sách!');
        return;
    }

    // Add subject to subjects array and re-render
    // We need to fetch the subject details and add to our local subjects array
    fetchAndAddSubject(subjectId);
    closeSearchSubjectModal();
}

async function fetchAndAddSubject(subjectId) {
    try {
            // Notify server to add subject to schedule
            const addResp = await fetch('/schedule-editor/api/schedule_item_api/', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ schedule_id: scheduleId ,item_id: subjectId }),
            });
            const addResult = await addResp.json();

            if (!addResp.ok || !addResult.success) {
                console.error('Lỗi khi thêm vào thời khóa biểu:', addResult.error || addResp.statusText);
                alert('Có lỗi khi thêm môn học vào thời khóa biểu');
            }
        
    } catch (error) {
        console.error('Lỗi khi thêm môn học:', error);
    }
}

// Search input event listener
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('search-input').addEventListener('input', function (e) {
        const query = e.target.value;

        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        // Set new timeout for debouncing
        searchTimeout = setTimeout(() => {
            searchSubjects(query);
        }, 300);
    });
});

// Canvas functions
function initializeCanvas() {
    const container = document.getElementById('canvas-container');
    // Add a visible red rectangle to the canvas
    const canvas = document.getElementById('canvas');

    const redRect = document.createElement('div');
    redRect.id = 'red-rect';
    Object.assign(redRect.style, {
        position: 'absolute',
        left: '50px',
        top: '50px',
        width: '400px',
        height: '250px',
        backgroundColor: 'red',
        borderRadius: '6px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        zIndex: 10,
        cursor: 'move'
    });

    canvas.appendChild(redRect);

    // Mouse wheel zoom
    container.addEventListener('wheel', function (e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? -0.1 : 0.1;
        zoom(delta, e.clientX, e.clientY);
    });

    // Mouse drag to pan
    container.addEventListener('mousedown', function (e) {
        if (e.target === container || e.target.closest('.canvas')) {
            isDragging = true;
            dragStart.x = e.clientX - canvasOffset.x;
            dragStart.y = e.clientY - canvasOffset.y;
            container.classList.add('dragging');
        }
    });

    document.addEventListener('mousemove', function (e) {
        if (isDragging) {
            canvasOffset.x = e.clientX - dragStart.x;
            canvasOffset.y = e.clientY - dragStart.y;
            updateCanvasTransform();
        }
    });

    document.addEventListener('mouseup', function () {
        if (isDragging) {
            isDragging = false;
            container.classList.remove('dragging');
        }
    });
}

function zoom(delta, centerX, centerY) {
    const minZoom = 0.25;
    const maxZoom = 3;
    const newZoom = Math.max(minZoom, Math.min(maxZoom, currentZoom + delta));

    if (newZoom !== currentZoom) {
        // Calculate zoom center relative to canvas
        const rect = document.getElementById('canvas-container').getBoundingClientRect();
        const zoomCenterX = centerX - rect.left - canvasOffset.x;
        const zoomCenterY = centerY - rect.top - canvasOffset.y;

        // Update offset to zoom around center point
        canvasOffset.x -= zoomCenterX * (newZoom - currentZoom);
        canvasOffset.y -= zoomCenterY * (newZoom - currentZoom);

        currentZoom = newZoom;
        updateCanvasTransform();
        updateZoomDisplay();
    }
}

function zoomIn() {
    zoom(0.25, window.innerWidth / 2, window.innerHeight / 2);
}

function zoomOut() {
    zoom(-0.25, window.innerWidth / 2, window.innerHeight / 2);
}

function resetZoom() {
    currentZoom = 1;
    canvasOffset.x = 0;
    canvasOffset.y = 0;
    updateCanvasTransform();
    updateZoomDisplay();
}

function updateCanvasTransform() {
    const canvas = document.getElementById('canvas');
    canvas.style.transform = `translate(${canvasOffset.x}px, ${canvasOffset.y}px) scale(${currentZoom})`;
}

function updateZoomDisplay() {
    document.getElementById('zoom-level').textContent = Math.round(currentZoom * 100) + '%';
}

function drawGrid() {
    const svg = document.getElementById('canvas-grid');
    const gridSize = 20;
    const containerRect = document.getElementById('canvas-container').getBoundingClientRect();

    svg.innerHTML = '';
    svg.setAttribute('width', containerRect.width);
    svg.setAttribute('height', containerRect.height);

    // Create grid pattern
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const pattern = document.createElementNS('http://www.w3.org/2000/svg', 'pattern');
    pattern.setAttribute('id', 'grid');
    pattern.setAttribute('width', gridSize);
    pattern.setAttribute('height', gridSize);
    pattern.setAttribute('patternUnits', 'userSpaceOnUse');

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', `M ${gridSize} 0 L 0 0 0 ${gridSize}`);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', '#e1e8ed');
    path.setAttribute('stroke-width', '1');

    pattern.appendChild(path);
    defs.appendChild(pattern);
    svg.appendChild(defs);

    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('width', '100%');
    rect.setAttribute('height', '100%');
    rect.setAttribute('fill', 'url(#grid)');
    svg.appendChild(rect);
}

// Close modal when clicking outside
window.addEventListener('click', function (e) {
    const searchModal = document.getElementById('search-subject-modal');

    if (e.target === searchModal) {
        closeSearchSubjectModal();
    }
});

// Redraw grid on window resize
window.addEventListener('resize', drawGrid);