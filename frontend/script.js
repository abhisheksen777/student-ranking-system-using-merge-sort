/* ==================== Student Marks Sorting & Ranking System ====================
   JavaScript - Frontend Logic
   ============================================================================== */

const API_BASE_URL = "http://127.0.0.1:5000";

let students = [];
let rankedStudents = [];
let vizSteps = [];
let vizCurrentStep = 0;
let vizPlayInterval = null;

// ==================== NAVIGATION ====================

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(sectionId).classList.add('active');

    if (sectionId === 'dashboard') updateDashboard();
    if (sectionId === 'students') renderStudentTable();
}

// ==================== UTILITY FUNCTIONS ====================

async function apiCall(endpoint, method = 'GET', body = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
    };
    if (body) options.body = JSON.stringify(body);

    try {
        const response = await fetch(url, options);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: response.statusText }));
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        return await response.json();
    } catch (err) {
        throw new Error(`Failed to fetch from ${endpoint}: ${err.message}`);
    }
}

// ==================== TOAST ====================

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => { toast.classList.remove('show'); }, 3000);
}

// ==================== DASHBOARD ====================

async function updateDashboard() {
    try {
        const data = await apiCall('/api/statistics');
        document.getElementById('dash-total').textContent = data.total_students;
        document.getElementById('dash-highest').textContent = data.highest_marks;
        document.getElementById('dash-average').textContent = data.average_marks;
        document.getElementById('dash-lowest').textContent = data.lowest_marks;
    } catch (err) {
        showToast('Failed to load dashboard: ' + err.message, 'error');
    }
}

// ==================== STUDENT MANAGEMENT ====================

async function saveStudent(e) {
    e.preventDefault();

    const roll = parseInt(document.getElementById('student-roll').value);
    const name = document.getElementById('student-name').value.trim();
    const marks = parseInt(document.getElementById('student-marks').value);

    if (!roll || !name) {
        showToast('Roll number and name cannot be empty!', 'error');
        return;
    }
    if (marks < 0 || marks > 100) {
        showToast('Marks must be between 0 and 100!', 'error');
        return;
    }

    try {
        // Check if editing or adding
        const editIndex = document.getElementById('edit-index').value;
        if (editIndex !== '-1') {
            const studentId = parseInt(editIndex);
            await apiCall(`/api/students/${studentId}`, 'PUT', { roll, name, marks });
            showToast('Student updated successfully!', 'success');
            document.getElementById('edit-index').value = '-1';
            document.getElementById('submit-btn').textContent = 'Add Student';
        } else {
            await apiCall('/api/students', 'POST', { roll, name, marks });
            showToast('Student added successfully!', 'success');
        }
        clearForm();
        await loadAndRenderStudents();
        updateDashboard();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loadAndRenderStudents() {
    try {
        const data = await apiCall('/api/students');
        students = data.students;
        renderStudentTable();
    } catch (err) {
        showToast('Failed to load students: ' + err.message, 'error');
        students = [];
        renderStudentTable();
    }
}

async function renderStudentTable() {
    const tbody = document.getElementById('student-tbody');
    if (students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-message">No students found. Load sample data or add students.</td></tr>';
        return;
    }

    tbody.innerHTML = students.map((s, i) => `
        <tr>
            <td>${s.roll}</td>
            <td>${s.name}</td>
            <td>${s.marks}</td>
            <td>
                <button class="btn btn-sm btn-info" onclick="editStudent(${s.id})">Edit</button>
                <button class="btn btn-sm btn-danger" onclick="deleteStudent(${s.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

async function editStudent(id) {
    const student = students.find(s => s.id === id);
    if (!student) return;
    document.getElementById('student-roll').value = student.roll;
    document.getElementById('student-name').value = student.name;
    document.getElementById('student-marks').value = student.marks;
    document.getElementById('edit-index').value = id;
    document.getElementById('submit-btn').textContent = 'Update Student';
    showToast('Editing student...', 'info');
}

async function deleteStudent(id) {
    if (!confirm('Are you sure you want to delete this student?')) return;
    try {
        await apiCall(`/api/students/${id}`, 'DELETE');
        showToast('Student deleted!', 'success');
        await loadAndRenderStudents();
        updateDashboard();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function clearAllStudents() {
    if (students.length === 0) return;
    if (!confirm('Are you sure you want to clear all students?')) return;
    try {
        await apiCall('/api/students', 'DELETE');
        showToast('All students cleared!', 'success');
        students = [];
        await loadAndRenderStudents();
        updateDashboard();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function loadSample() {
    try {
        const data = await apiCall('/api/sample');
        showToast(`Sample data loaded! Added: ${data.added.length}, Skipped: ${data.skipped.length}`, 'success');
        await loadAndRenderStudents();
        updateDashboard();
    } catch (err) {
        showToast('Failed to load sample data: ' + err.message, 'error');
    }
}

function clearForm() {
    document.getElementById('student-form').reset();
    document.getElementById('edit-index').value = '-1';
    document.getElementById('submit-btn').textContent = 'Add Student';
}

// ==================== RANKING ====================

async function generateRanking() {
    try {
        const data = await apiCall('/api/ranking');
        rankedStudents = data.students;
        renderRankingTable(rankedStudents);
        showRankingStats(data.statistics);
        showToast('Ranking generated!', 'success');
    } catch (err) {
        showToast('Error generating ranking: ' + err.message, 'error');
    }
}

function renderRankingTable(data) {
    const tbody = document.getElementById('ranking-tbody');
    if (data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-message">No students to display. Generate ranking first.</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(s => `
        <tr class="${s.rank === 1 ? 'rank-1' : ''}">
            <td>${s.rank}</td>
            <td>${s.roll}</td>
            <td>${s.name}</td>
            <td>${s.marks}</td>
        </tr>
    `).join('');
}

function showRankingStats(stats) {
    const el = document.getElementById('ranking-stats');
    el.innerHTML = `
        <div class="rank-stat">Total Students: <strong>${stats.total}</strong></div>
        <div class="rank-stat">Highest: <strong>${stats.highest}</strong></div>
        <div class="rank-stat">Average: <strong>${stats.average}</strong></div>
        <div class="rank-stat">Lowest: <strong>${stats.lowest}</strong></div>
    `;
}

function filterRanking() {
    const search = document.getElementById('search-student').value.toLowerCase();
    const filterMarks = parseInt(document.getElementById('filter-marks').value);

    let filtered = [...rankedStudents];

    if (search) {
        filtered = filtered.filter(s => s.name.toLowerCase().includes(search));
    }
    if (!isNaN(filterMarks) && filterMarks >= 0 && filterMarks <= 100) {
        filtered = filtered.filter(s => s.marks === filterMarks);
    }

    renderRankingTable(filtered);
}

// ==================== MERGE SORT VISUALIZATION ====================

function startViz() {
    const input = document.getElementById('viz-input').value.trim();
    if (!input) {
        showToast('Enter marks separated by commas!', 'error');
        return;
    }

    const marks = input.split(',').map(m => parseInt(m.trim())).filter(m => !isNaN(m) && m >= 0 && m <= 100);
    if (marks.length === 0) {
        showToast('Enter valid marks!', 'error');
        return;
    }

    const data = marks.map((m, i) => ({ marks: m, name: `S${i + 1}` }));
    vizSteps = generateVizSteps(data);
    vizCurrentStep = 0;

    renderVizSteps();
    renderVizStep();
    showToast('Visualization started!', 'success');
}

function generateVizSteps(data) {
    const steps = [];

    function divide(arr) {
        if (arr.length <= 1) {
            steps.push({ type: 'conquer', message: `Base case reached: [${arr.map(a => a.marks).join(', ')}]` });
            return arr;
        }

        const mid = Math.floor(arr.length / 2);
        const left = arr.slice(0, mid);
        const right = arr.slice(mid);

        steps.push({ type: 'divide', message: `DIVIDING: [${arr.map(a => a.marks).join(', ')}] → [${left.map(a => a.marks).join(', ')}] and [${right.map(a => a.marks).join(', ')}]` });

        const sortedLeft = divide(left);
        const sortedRight = divide(right);

        const merged = mergeViz(sortedLeft, sortedRight);
        return merged;
    }

    function mergeViz(left, right) {
        const result = [];
        let i = 0, j = 0;

        steps.push({ type: 'combine', message: `COMBINING: Comparing [${left.map(a => a.marks).join(', ')}] and [${right.map(a => a.marks).join(', ')}]` });

        while (i < left.length && j < right.length) {
            steps.push({ type: 'combine', message: `Comparing ${left[i].marks} vs ${right[j].marks}` });
            if (left[i].marks >= right[j].marks) {
                result.push(left[i]);
                steps.push({ type: 'combine', message: `${left[i].marks} ≥ ${right[j].marks} → Take ${left[i].marks}` });
                i++;
            } else {
                result.push(right[j]);
                steps.push({ type: 'combine', message: `${left[i].marks} < ${right[j].marks} → Take ${right[j].marks}` });
                j++;
            }
        }

        while (i < left.length) { result.push(left[i]); i++; }
        while (j < right.length) { result.push(right[j]); j++; }

        steps.push({ type: 'combine', message: `Merged result: [${result.map(a => a.marks).join(', ')}]` });

        return result;
    }

    steps.push({ type: 'divide', message: `START: Initial array: [${data.map(a => a.marks).join(', ')}]` });
    divide(data);
    const sorted = [...data].sort((a, b) => b.marks - a.marks);
    steps.push({ type: 'combine', message: `FINAL SORTED: [${sorted.map(a => a.marks).join(', ')}]` });

    return steps;
}

function renderVizSteps() {
    const container = document.getElementById('viz-steps');
    container.innerHTML = vizSteps.map((step, i) => `
        <div class="step-item ${step.type}" style="${i === vizCurrentStep ? 'border-left-width: 6px; background: #e3f2fd;' : ''}">
            <strong>Step ${i + 1}:</strong> ${step.message}
        </div>
    `).join('');
}

function renderVizStep() {
    const messageEl = document.getElementById('viz-message');
    const arrayEl = document.getElementById('viz-array');

    if (vizSteps.length === 0) {
        messageEl.textContent = 'Enter marks and click "Start Visualization"';
        arrayEl.innerHTML = '';
        return;
    }

    const step = vizSteps[vizCurrentStep];
    messageEl.textContent = step.message;

    const match = step.message.match(/\[([^\]]+)\]/);
    if (match) {
        const nums = match[1].split(',').map(Number);
        arrayEl.innerHTML = nums.map((n, i) =>
            `<div class="viz-bar">${n}</div>`
        ).join('');
    }

    const stepItems = document.querySelectorAll('.step-item');
    stepItems.forEach((el, i) => {
        el.style.borderLeftWidth = i === vizCurrentStep ? '6px' : '4px';
        el.style.background = i === vizCurrentStep ? '#e3f2fd' : '#f8f9fa';
    });
}

function vizPrev() { if (vizCurrentStep > 0) { vizCurrentStep--; renderVizStep(); renderVizSteps(); } }
function vizNext() { if (vizCurrentStep < vizSteps.length - 1) { vizCurrentStep++; renderVizStep(); renderVizSteps(); } }

function vizPlay() {
    if (vizPlayInterval) clearInterval(vizPlayInterval);
    vizPlayInterval = setInterval(() => {
        if (vizCurrentStep >= vizSteps.length - 1) { clearInterval(vizPlayInterval); vizPlayInterval = null; return; }
        vizCurrentStep++;
        renderVizStep();
        renderVizSteps();
    }, 1000);
}

function vizPause() { if (vizPlayInterval) { clearInterval(vizPlayInterval); vizPlayInterval = null; } }

function vizReset() {
    vizPause();
    vizCurrentStep = 0;
    renderVizStep();
    renderVizSteps();
    document.getElementById('viz-message').textContent = 'Enter marks and click "Start Visualization"';
    document.getElementById('viz-array').innerHTML = '';
}

// ==================== PERFORMANCE TESTING ====================

async function runPerformance(sizes) {
    const resultsContainer = document.getElementById('perf-results');
    const chartContainer = document.getElementById('perf-chart');

    resultsContainer.innerHTML = '<p>Running performance tests...</p>';
    chartContainer.innerHTML = '<p>Running performance tests...</p>';

    try {
        const results = [];
        for (const size of sizes) {
            const data = await apiCall('/api/performance', 'POST', { size });
            results.push(data);
            await new Promise(r => setTimeout(r, 200)); // Small delay between requests
        }

        resultsContainer.innerHTML = `
            <table>
                <thead><tr><th>Dataset Size</th><th>Execution Time (ms)</th></tr></thead>
                <tbody>
                    ${results.map(r => `<tr><td>${r.size}</td><td>${r.execution_time_ms}</td></tr>`).join('')}
                </tbody>
            </table>
        `;

        const maxTime = Math.max(...results.map(r => r.execution_time_ms), 1);
        chartContainer.innerHTML = `
            <div class="bar-chart">
                ${results.map(r => {
                    const height = Math.max((r.execution_time_ms / maxTime) * 150, 5);
                    return `<div class="bar-item">
                        <div class="bar-value">${r.execution_time_ms}ms</div>
                        <div class="bar" style="height: ${height}px"></div>
                        <div class="bar-label">${r.size}</div>
                    </div>`;
                }).join('')}
            </div>
        `;
    } catch (err) {
        resultsContainer.innerHTML = `<p style="color:red">Error: ${err.message}</p>`;
        chartContainer.innerHTML = '<p style="color:red">Error running tests</p>';
    }
}

// ==================== INITIALIZE ====================

loadAndRenderStudents();
updateDashboard();
