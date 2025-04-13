document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.querySelector('.upload-box');
    const fileInput = document.querySelector('#fileInput');
    const uploadBtn = document.querySelector('#uploadBtn');
    const loadingOverlay = document.querySelector('#loadingOverlay');
    const resultsSection = document.querySelector('#resultsSection');
    const summaryContent = document.querySelector('#summaryContent');
    const datesList = document.querySelector('#datesList');
    const importanceContent = document.querySelector('#importanceContent');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const copySummaryBtn = document.querySelector('#copySummaryBtn');
    const downloadBtn = document.querySelector('#downloadBtn');

    let currentData = null;

    // Handle drag and drop
    uploadBox.addEventListener('click', (e) => {
        if (e.target === uploadBox || e.target.closest('.upload-box')) {
            e.preventDefault();
            e.stopPropagation();
            fileInput.click();
        }
    });

    // Handle file input change
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload();
        }
    });

    // Handle upload button click
    if (uploadBtn) {
        uploadBtn.onclick = (e) => {
            e.preventDefault();
            fileInput.click();
        };
    }

    // Handle drag and drop events
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.add('dragover');
        uploadBox.style.borderColor = '#3498db';
        uploadBox.style.backgroundColor = 'rgba(52, 152, 219, 0.05)';
    });

    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.remove('dragover');
        uploadBox.style.borderColor = '';
        uploadBox.style.backgroundColor = '';
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.remove('dragover');
        uploadBox.style.borderColor = '';
        uploadBox.style.backgroundColor = '';
        const files = e.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            handleFileUpload();
        }
    });

    // Handle copy summary button
    copySummaryBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(summaryContent.textContent);
            showSuccess('Summary copied to clipboard!');
        } catch (err) {
            showError('Failed to copy summary');
        }
    });

    // Handle tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const importance = button.dataset.tab;
            updateImportanceContent(importance);
        });
    });

    async function handleFileUpload() {
        const file = fileInput.files[0];
        if (!file) return;

        // Validate file type
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        if (!validTypes.includes(file.type)) {
            showError('Please upload a valid file type (PDF, DOCX, or TXT)');
            return;
        }

        // Validate file size (max 10MB)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            showError('File size exceeds 10MB limit');
            return;
        }

        // Show loading overlay with animation
        loadingOverlay.style.display = 'flex';
        setTimeout(() => loadingOverlay.style.opacity = '1', 10);
        resultsSection.style.display = 'none';

        const formData = new FormData();
        formData.append('document', file);

        try {
            const response = await fetch('http://127.0.0.1:5001/summarize', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to process document');
            }

            currentData = result.data;
            displayResults(result.data);
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while processing the document. Please try again.');
        } finally {
            // Hide loading overlay with animation
            loadingOverlay.style.opacity = '0';
            setTimeout(() => loadingOverlay.style.display = 'none', 300);
        }
    }

    function displayResults(data) {
        if (!data) {
            showError('No data received from server');
            return;
        }

        // Update summary
        summaryContent.textContent = data.summary || 'No summary available';

        // Update dates
        datesList.innerHTML = '';
        if (data.dates && data.dates.length > 0) {
            data.dates.forEach(date => {
                const li = document.createElement('li');
                li.innerHTML = `<i class="fas fa-calendar"></i> ${date}`;
                datesList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.innerHTML = '<i class="fas fa-info-circle"></i> No dates found';
            datesList.appendChild(li);
        }

        // Update importance content
        updateImportanceContent('very-important');

        // Update download button
        if (data.report_url) {
            downloadBtn.href = data.report_url;
            downloadBtn.style.display = 'inline-flex';
        } else {
            downloadBtn.style.display = 'none';
        }

        // Show results section with animation
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.classList.add('visible');
            // Scroll to results with smooth animation
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 10);
    }

    function updateImportanceContent(importance) {
        if (!currentData || !currentData.importance) {
            importanceContent.innerHTML = '<p>No importance data available</p>';
            return;
        }

        const content = {
            'very-important': currentData.importance.high || [],
            'important': currentData.importance.medium || [],
            'not-so-important': currentData.importance.low || []
        };
        
        importanceContent.innerHTML = '';
        const ul = document.createElement('ul');
        
        if (content[importance].length === 0) {
            const li = document.createElement('li');
            li.innerHTML = '<i class="fas fa-info-circle"></i> No items in this category';
            ul.appendChild(li);
        } else {
            content[importance].forEach(item => {
                const li = document.createElement('li');
                const icon = importance === 'very-important' ? 'exclamation-circle' :
                           importance === 'important' ? 'info-circle' : 'comment';
                li.innerHTML = `<i class="fas fa-${icon}"></i> ${item}`;
                ul.appendChild(li);
            });
        }
        
        importanceContent.appendChild(ul);
    }

    function showError(message) {
        showNotification(message, 'error');
    }

    function showSuccess(message) {
        showNotification(message, 'success');
    }

    function showNotification(message, type) {
        // Create notification element if it doesn't exist
        let notificationElement = document.querySelector('.notification');
        if (!notificationElement) {
            notificationElement = document.createElement('div');
            notificationElement.className = 'notification';
            document.querySelector('.upload-section').appendChild(notificationElement);
        }

        // Set notification style based on type
        notificationElement.className = `notification ${type}`;
        const icon = type === 'error' ? 'exclamation-circle' : 'check-circle';
        notificationElement.innerHTML = `<i class="fas fa-${icon}"></i> ${message}`;

        // Show notification with animation
        notificationElement.style.display = 'flex';
        notificationElement.style.opacity = '0';
        setTimeout(() => {
            notificationElement.style.opacity = '1';
        }, 10);

        // Hide notification after delay
        setTimeout(() => {
            notificationElement.style.opacity = '0';
            setTimeout(() => {
                notificationElement.style.display = 'none';
            }, 300);
        }, 5000);
    }
}); 