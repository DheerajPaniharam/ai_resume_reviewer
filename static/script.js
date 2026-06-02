document.addEventListener('DOMContentLoaded', () => {
  initSourceToggler();
  initDragAndDrop();
  initScoreAnimation();
  initTabNavigation();
  initChecklistPersistence();
  initFormSubmissionState();
});

// 1. Source Input Toggler
function initSourceToggler() {
  const toggleButtons = document.querySelectorAll('.toggle-btn');
  const sourceModeInput = document.getElementById('source_mode');
  const sections = document.querySelectorAll('.input-section-content');

  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Toggle active button state
      toggleButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Update mode value
      const targetId = btn.getAttribute('data-target');
      sourceModeInput.value = targetId === 'upload-section' ? 'file' : 'text';

      // Toggle input content panels
      sections.forEach(sec => {
        if (sec.id === targetId) {
          sec.classList.add('active');
        } else {
          sec.classList.remove('active');
        }
      });
    });
  });
}

// 2. Drag & Drop File Upload Handler
function initDragAndDrop() {
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('resume');
  const fileDisplay = document.getElementById('file-name-display');
  const clearBtn = document.getElementById('btn-clear-file');
  const dropzoneText = document.querySelector('.dropzone-text');
  const dropzoneSub = document.querySelector('.dropzone-sub');
  const cloudIcon = document.querySelector('.cloud-icon');

  if (!dropZone || !fileInput) return;

  // Prevent browser default behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  // Toggle drag visual states
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
  });
  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
  });

  // Handle dropped files
  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length) {
      fileInput.files = files;
      updateFileDisplay(files[0].name);
    }
  }, false);

  // File browser click proxy
  dropZone.addEventListener('click', (e) => {
    if (e.target !== fileInput && !e.target.closest('#file-name-display')) {
      fileInput.click();
    }
  });

  // Input change listener (manual select)
  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      updateFileDisplay(fileInput.files[0].name);
    }
  });

  // Clear file choice listener
  clearBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.value = '';
    
    // Reset layout
    fileDisplay.classList.add('hidden');
    cloudIcon.classList.remove('hidden');
    dropzoneText.classList.remove('hidden');
    dropzoneSub.classList.remove('hidden');
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  function updateFileDisplay(name) {
    fileDisplay.querySelector('.file-name').textContent = name;
    fileDisplay.classList.remove('hidden');
    
    // Hide details text
    cloudIcon.classList.add('hidden');
    dropzoneText.classList.add('hidden');
    dropzoneSub.classList.add('hidden');
  }
}

// 3. Score Gauge & Numerical Count Animation
function initScoreAnimation() {
  const progressRing = document.querySelector('.score-ring-progress');
  const scoreCounter = document.getElementById('score-counter');
  
  if (!progressRing || !scoreCounter) return;

  const score = parseFloat(progressRing.getAttribute('data-score')) || 0;
  const radius = parseFloat(progressRing.getAttribute('r')) || 52;
  const circumference = 2 * Math.PI * radius; // ~326.7
  
  // Set stroke attributes
  progressRing.style.strokeDasharray = `${circumference} ${circumference}`;
  progressRing.style.strokeDashoffset = circumference;

  // Trigger stroke transition
  setTimeout(() => {
    const offset = circumference - (circumference * score) / 100;
    progressRing.style.strokeDashoffset = offset;
  }, 100);

  // Count text animation
  let currentVal = 0;
  const duration = 1200; // ms
  const startTime = performance.now();

  function animateCount(timestamp) {
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // Ease-out quad formula
    const easeProgress = progress * (2 - progress);
    currentVal = easeProgress * score;
    
    scoreCounter.textContent = Math.round(currentVal);

    if (progress < 1) {
      requestAnimationFrame(animateCount);
    } else {
      scoreCounter.textContent = Math.round(score);
    }
  }

  if (score > 0) {
    requestAnimationFrame(animateCount);
  } else {
    scoreCounter.textContent = '0';
  }
}

// 4. Tab Switching Sub-navigation
function initTabNavigation() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabId = btn.getAttribute('data-tab');

      // Toggle buttons active classes
      tabButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Toggle visible tab contents
      tabContents.forEach(content => {
        if (content.id === targetTabId) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });
    });
  });
}

// 5. Checklist Strike-through Caching
function initChecklistPersistence() {
  const checkboxes = document.querySelectorAll('.checklist-checkbox');

  checkboxes.forEach(box => {
    const key = `resume_fix_${box.id}`;
    
    // Load local state
    if (localStorage.getItem(key) === 'checked') {
      box.checked = true;
    }

    // Capture state updates
    box.addEventListener('change', () => {
      if (box.checked) {
        localStorage.setItem(key, 'checked');
      } else {
        localStorage.removeItem(key);
      }
    });
  });
}

// 6. Loading submission spinner
function initFormSubmissionState() {
  const form = document.getElementById('analysis-form');
  const btn = document.querySelector('.btn-submit');
  const spinner = document.getElementById('btn-spinner');
  const btnText = btn ? btn.querySelector('.btn-text') : null;

  if (!form || !btn) return;

  form.addEventListener('submit', () => {
    btn.disabled = true;
    if (spinner) spinner.classList.remove('hidden');
    if (btnText) btnText.textContent = 'Analyzing details...';
  });
}

// 7. Copy markdown analysis report
function copyReportToClipboard() {
  const jsonDataElement = document.getElementById('result-json-data');
  if (!jsonDataElement) {
    alert('No active analysis data to extract.');
    return;
  }

  try {
    const data = JSON.parse(jsonDataElement.textContent);
    
    // Generate beautiful markdown formatting
    let report = `# SmartScreen: Resume Assessment Report\n\n`;
    report += `**Overall Score:** ${data.score}% \n`;
    report += `**Target Career:** ${data.job_target || 'General Resume'}\n\n`;
    
    report += `## Document Metadata Metrics\n`;
    report += `- **Word Count:** ${data.word_count} words\n`;
    report += `- **Experience Duration:** ${data.experience_years} years estimated\n`;
    report += `- **Bullet point items:** ${data.bullet_count} lines parsed\n`;
    report += `- **Quantifiable metrics:** ${data.metrics_count} achievements detected\n\n`;

    report += `## Key Strengths\n`;
    data.strengths.forEach(str => {
      report += `- ✓ ${str}\n`;
    });
    report += `\n`;

    report += `## Actionable Fix Checklist\n`;
    data.feedback.forEach(item => {
      // Strip priority tags and format
      const cleaned = item.replace(/\[High\]|\[Medium\]|\[Low\]/g, '').trim();
      let priority = 'Low';
      if (item.includes('[High]')) priority = 'High';
      else if (item.includes('[Medium]')) priority = 'Medium';
      
      report += `- [ ] [Priority: ${priority}] ${cleaned}\n`;
    });
    report += `\n`;

    report += `*Review Report generated locally via SmartScreen.*`;

    // Copy to clipboard
    navigator.clipboard.writeText(report).then(() => {
      alert('Markdown report successfully copied to clipboard!');
    }, () => {
      alert('Clipboard error. Please copy analysis manually.');
    });

  } catch (err) {
    console.error("JSON parsing error for report copy:", err);
    alert('Error generating report representation.');
  }
}

// 8. Download JSON analysis blob
function downloadJSONReport() {
  const jsonDataElement = document.getElementById('result-json-data');
  if (!jsonDataElement) return;

  try {
    const data = JSON.parse(jsonDataElement.textContent);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `smartscreen_analysis_${data.job_target.replace(/\s+/g, '_').toLowerCase() || 'general'}.json`;
    a.click();
    
    // Clean memory
    setTimeout(() => URL.revokeObjectURL(url), 100);
  } catch (err) {
    console.error("Download failed:", err);
  }
}

// Helper: Copies single suggested optimized statement
function copySnippet(elementId, btn) {
  const el = document.getElementById(elementId);
  if (!el) return;

  // Clean double quotes from suggestion text
  const text = el.textContent.replace(/^“|”$/g, '').trim();
  
  navigator.clipboard.writeText(text).then(() => {
    const originalText = btn.textContent;
    btn.textContent = 'Copied!';
    btn.style.backgroundColor = '#10b981';
    btn.style.borderColor = '#10b981';
    
    setTimeout(() => {
      btn.textContent = originalText;
      btn.style.backgroundColor = '';
      btn.style.borderColor = '';
    }, 2000);
  });
}
