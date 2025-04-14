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

    // Handle upload button click
    uploadBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            handleFileUpload();
        }
    });

    // Handle drag and drop
    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.add('dragover');
    });

    uploadBox.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.remove('dragover');
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        uploadBox.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
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

    // Handle download button
    downloadBtn.addEventListener('click', () => {
        if (currentData && currentData.report_url) {
            window.open(currentData.report_url, '_blank');
        } else {
            showError('No PDF report available');
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

        // Validate file size (max 16MB)
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            showError('File size exceeds 16MB limit');
            return;
        }

        // Show loading overlay with animation
        loadingOverlay.style.display = 'flex';
        loadingOverlay.querySelector('p').textContent = 'Processing your document...';

        try {
            const formData = new FormData();
            formData.append('document', file);

            const response = await fetch('/summarize', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to process document');
            }

            if (!data.success) {
                throw new Error(data.error || 'Failed to process document');
            }

            // Store the data and display results
            currentData = data.data;
            displayResults(currentData);
            showSuccess('Document processed successfully!');
        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while processing your document');
        } finally {
            loadingOverlay.style.display = 'none';
        }
    }

    function displayResults(data) {
        if (!data) {
            console.error('No data received from server');
            return;
        }

        // Update summary
        const summaryContent = document.getElementById('summaryContent');
        summaryContent.textContent = data.summary || 'No summary available';

        // Update dates
        const datesList = document.getElementById('datesList');
        datesList.innerHTML = '';
        if (data.dates && data.dates.length > 0) {
            data.dates.forEach(date => {
                const li = document.createElement('li');
                li.className = 'date-item';
                li.innerHTML = `
                    <i class="fas fa-calendar-alt"></i>
                    <div class="date-content">
                        <span class="date-value">${date.date}</span>
                        <span class="date-context">${date.context}</span>
                    </div>
                `;
                datesList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.className = 'date-item';
            li.innerHTML = '<i class="fas fa-info-circle"></i> No important dates found';
            datesList.appendChild(li);
        }

        // Update importance
        const importanceContent = document.getElementById('importanceContent');
        importanceContent.innerHTML = '';
        if (data.importance) {
            const importanceLevels = ['high', 'medium', 'low'];
            importanceLevels.forEach(level => {
                if (data.importance[level] && data.importance[level].length > 0) {
                    const ul = document.createElement('ul');
                    data.importance[level].forEach(item => {
                        const li = document.createElement('li');
                        li.innerHTML = `<i class="fas fa-${level === 'high' ? 'exclamation-circle' : level === 'medium' ? 'info-circle' : 'comment'}"></i> ${item}`;
                        ul.appendChild(li);
                    });
                    importanceContent.appendChild(ul);
                }
            });
        }

        // Update law articles
        const lawArticlesList = document.getElementById('lawArticlesList');
        lawArticlesList.innerHTML = '';
        if (data.suggested_articles && data.suggested_articles.length > 0) {
            data.suggested_articles.forEach(article => {
                const articleDiv = document.createElement('div');
                articleDiv.className = 'law-article-item';
                articleDiv.innerHTML = `
                    <div class="law-article-header">
                        <i class="fas fa-gavel"></i>
                        <span class="law-article-title">${article.article} - ${article.title}</span>
                    </div>
                    <div class="law-article-description">${article.description}</div>
                `;
                lawArticlesList.appendChild(articleDiv);
            });
        } else {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'law-article-item';
            articleDiv.innerHTML = '<i class="fas fa-info-circle"></i> No relevant law articles found';
            lawArticlesList.appendChild(articleDiv);
        }

        // Update download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (data.report_url) {
            downloadBtn.style.display = 'inline-flex';
            downloadBtn.style.visibility = 'visible';
        } else {
            downloadBtn.style.display = 'none';
            downloadBtn.style.visibility = 'hidden';
        }

        // Show results section with animation
        resultsSection.style.display = 'block';
        setTimeout(() => {
            resultsSection.style.opacity = '1';
            resultsSection.style.transform = 'translateY(0)';
        }, 100);

        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
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
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    function showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'notification success';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}); 