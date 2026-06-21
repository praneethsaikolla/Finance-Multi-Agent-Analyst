/* =============================================
   SCRIPT.JS — Finance Multi-Agent Dashboard
   ============================================= */

/* ---- State ---- */
let currentFilename = null;

/* ---- DOM Refs ---- */
const analyzeForm = document.getElementById('analyze-form');
const tickerInput = document.getElementById('ticker-input');
const analyzeBtn = document.getElementById('analyze-btn');
const reportList = document.getElementById('report-list');
const loadingState = document.getElementById('loading-state');
const loadingTicker = document.getElementById('loading-ticker');
const emptyState = document.getElementById('empty-state');
const reportViewer = document.getElementById('report-viewer');
const currentTickerNav = document.getElementById('current-ticker');

/* ---- Show/Hide States ---- */
function showLoading(ticker) {
    loadingTicker.textContent = ticker;
    loadingState.classList.remove('hidden');
    emptyState.classList.add('hidden');
    reportViewer.classList.add('hidden');
}

function showEmpty() {
    emptyState.classList.remove('hidden');
    loadingState.classList.add('hidden');
    reportViewer.classList.add('hidden');
}

function showReport(html) {
    reportViewer.innerHTML = html;
    reportViewer.classList.remove('hidden');
    loadingState.classList.add('hidden');
    emptyState.classList.add('hidden');
}

/* ---- Format timestamp ---- */
function formatTimestamp(ts) {
    if (!ts || ts.length < 12) return ts;
    // Format: YYYYMMDD_HHMM -> readable date
    try {
        const year = ts.substring(0, 4);
        const month = ts.substring(4, 6);
        const day = ts.substring(6, 8);
        const hour = ts.substring(9, 11);
        const min = ts.substring(11, 13);
        const date = new Date(year, parseInt(month) - 1, day, hour, min);
        return date.toLocaleString('en-IN', {
            month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', hour12: true
        });
    } catch {
        return ts;
    }
}

/* ---- Load Report List ---- */
async function loadReportList() {
    try {
        const res = await fetch('/api/reports');
        const data = await res.json();
        reportList.innerHTML = '';

        if (!data.reports || data.reports.length === 0) {
            reportList.innerHTML = '<li class="report-list-empty">No reports yet</li>';
            return;
        }

        data.reports.forEach(report => {
            const li = document.createElement('li');
            li.className = 'report-item' + (report.filename === currentFilename ? ' active' : '');
            li.innerHTML = `
                <span class="report-item-ticker gradient-text">${report.ticker}</span>
                <span class="report-item-time">${formatTimestamp(report.timestamp)}</span>
            `;
            li.addEventListener('click', () => openReport(report.filename, report.ticker));
            reportList.appendChild(li);
        });
    } catch (err) {
        console.error('Failed to load reports:', err);
        reportList.innerHTML = '<li class="report-list-empty">Error loading history</li>';
    }
}

/* ---- Open Existing Report ---- */
async function openReport(filename, ticker) {
    currentFilename = filename;
    currentTickerNav.textContent = ticker;
    loadingTicker.textContent = ticker;
    showLoading(ticker);

    // Mark active in list
    document.querySelectorAll('.report-item').forEach(el => el.classList.remove('active'));

    try {
        const res = await fetch(`/api/reports/${filename}`);
        const data = await res.json();
        
        // Wrap html in styled sections
        showReport(wrapReportHtml(data.html));
    } catch (err) {
        console.error('Error opening report:', err);
        showEmpty();
    }

    await loadReportList();
}

/* ---- Wrap report html in styled cards ---- */
function wrapReportHtml(rawHtml) {
    // Split at <hr> tags and wrap each section in a card div
    const sections = rawHtml.split('<hr>');
    return sections.map(section => section.trim()).filter(s => s.length > 0).join('');
}

/* ---- Handle Analyze Form ---- */
analyzeForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const ticker = tickerInput.value.trim().toUpperCase();
    if (!ticker) return;

    // UI update
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = `<span class="btn-text">Analyzing...</span><i class="fa-solid fa-spinner fa-spin"></i>`;
    currentTickerNav.textContent = ticker;
    showLoading(ticker);
    tickerInput.value = '';

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker })
        });

        if (!res.ok) {
            const errData = await res.json();
            throw new Error(errData.detail || 'Analysis failed');
        }

        const data = await res.json();
        currentFilename = data.filename;
        showReport(wrapReportHtml(data.html));
        await loadReportList();
    } catch (err) {
        console.error('Analysis failed:', err);
        alert(`Analysis failed for ${ticker}: ${err.message}`);
        showEmpty();
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = `<span class="btn-text">Analyze</span><i class="fa-solid fa-wand-magic-sparkles"></i>`;
    }
});

/* ---- Init ---- */
(async () => {
    await loadReportList();
})();
