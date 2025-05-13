function toggleAbstract(button) {
    const abstractDiv = button.nextElementSibling;
    if (abstractDiv.style.display === "none") {
        abstractDiv.style.display = "block";
        button.textContent = "Hide Abstract";
    } else {
        abstractDiv.style.display = "none";
        button.textContent = "Show Abstract";
    }
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Toggle paper visibility
function togglePaperVisibility(button, paperId) {
    const paperCard = button.closest('.paper-card');
    if (button.classList.contains('visibility-show')) {
        paperCard.style.display = 'none';
        // We don't remove the element to keep its data
    } else {
        paperCard.style.display = '';
    }
}

// Add new keyword field
function addKeywordField(button) {
    const keywordsDiv = button.parentElement;
    const newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.className = 'keyword-input';
    newInput.placeholder = 'Add keyword';
    keywordsDiv.insertBefore(newInput, button);
}

// Toggle comments edit mode
function toggleCommentsEdit(container) {
    const viewDiv = container.querySelector('.comments-view');
    const editDiv = container.querySelector('.comments-edit');

    if (editDiv.style.display === 'none') {
        viewDiv.style.display = 'none';
        editDiv.style.display = 'block';
    } else {
        // Save the content when toggling back
        const textarea = editDiv.querySelector('.comments-input');
        const contentDiv = viewDiv.querySelector('.comments-content');
        contentDiv.textContent = textarea.value;

        viewDiv.style.display = 'block';
        editDiv.style.display = 'none';
    }
}

// Toggle TL;DR edit mode
function toggleTldrEdit(container) {
    const viewDiv = container.querySelector('.tldr-view');
    const editDiv = container.querySelector('.tldr-edit');

    if (editDiv.style.display === 'none') {
        viewDiv.style.display = 'none';
        editDiv.style.display = 'block';
    } else {
        // Save the content when toggling back
        const textarea = editDiv.querySelector('.tldr-input');
        const contentDiv = viewDiv.querySelector('.tldr-content');
        contentDiv.textContent = textarea.value;

        viewDiv.style.display = 'block';
        editDiv.style.display = 'none';
    }
}

/**
 * Update the card size for a specific section
 * @param {string} value - The card size value (small, medium, large, full)
 * @param {Element} selectElement - The select element that triggered the change
 */
function updateCardSize(value, selectElement) {
    // Find the section container
    const sectionHeader = selectElement.closest('.section-header');
    const papersContainer = sectionHeader.nextElementSibling;

    // Remove existing size classes
    papersContainer.classList.remove('card-size-small', 'card-size-medium', 'card-size-large', 'card-size-full');

    // Add the new size class
    papersContainer.classList.add(`card-size-${value}`);

    // Save the preference in localStorage
    localStorage.setItem('preferredCardSize', value);
}

// Export selected papers to JSON
function exportSelectedPapers() {
    const selectedPapers = [];
    const visiblePaperCards = document.querySelectorAll('.paper-card:not([style*="display: none"])');

    visiblePaperCards.forEach(paperCard => {
        const paperId = paperCard.getAttribute('data-paper-id');
        const title = paperCard.getAttribute('data-paper-title');
        const pdfUrl = paperCard.querySelector('.paper-title a').href;

        // Get authors
        let authors = [];
        const authorsElement = paperCard.querySelector('.authors');
        if (authorsElement) {
            const authorsText = authorsElement.textContent.replace('Authors:', '').trim();
            authors = authorsText.split(',').map(author => author.trim());
        }

        // Get keywords
        const keywords = [];
        const keywordInputs = paperCard.querySelectorAll('.keyword-input');
        keywordInputs.forEach(input => {
            if (input.value.trim()) {
                keywords.push(input.value.trim());
            }
        });

        // Get abstract
        let abstract = '';
        const abstractElement = paperCard.querySelector('.abstract p');
        if (abstractElement) {
            abstract = abstractElement.textContent.trim();
        }

        // Get TLDR
        let tldr = '';
        const tldrElement = paperCard.querySelector('.tldr-content');
        if (tldrElement) {
            tldr = tldrElement.textContent.trim();
        }

        // Get comments (only if checkbox is checked)
        let comments = '';
        const commentsCheckbox = paperCard.querySelector('.comments-checkbox');
        if (commentsCheckbox && commentsCheckbox.checked) {
            const commentsElement = paperCard.querySelector('.comments-content');
            if (commentsElement) {
                comments = commentsElement.textContent.trim();
            }
        }

        selectedPapers.push({
            id: paperId,
            title: title,
            pdf_url: pdfUrl,
            authors: authors,
            keywords: keywords,
            abstract: abstract,
            tldr: tldr,
            comments: comments
        });
    });

    if (selectedPapers.length === 0) {
        alert('No visible papers to export.');
        return;
    }

    // Create JSON file and trigger download
    const jsonData = JSON.stringify(selectedPapers, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'exported_papers.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Select/deselect all papers in a section
function toggleSectionSelection(sectionId, show) {
    const section = document.getElementById(sectionId);
    if (section) {
        const paperCards = section.nextElementSibling.querySelectorAll('.paper-card');
        paperCards.forEach(card => {
            if (show) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
}

// Highlight active section in sidebar
document.addEventListener('DOMContentLoaded', function () {
    window.addEventListener('scroll', function () {
        const sections = document.querySelectorAll('.section-header');
        const sidebarLinks = document.querySelectorAll('.sidebar-link');

        let currentSection = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (window.scrollY >= sectionTop - 100) {
                currentSection = section.id;
            }
        });

        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === currentSection) {
                link.classList.add('active');
            }
        });
    });
});

/**
 * Export selected papers as a markdown file
 */
function exportMarkdown() {
    // Get all visible paper cards
    const visiblePapers = Array.from(document.querySelectorAll('.paper-card'))
        .filter(card => !card.classList.contains('hidden'));

    if (visiblePapers.length === 0) {
        alert('No papers selected for export. Please make sure at least one paper is visible.');
        return;
    }

    // Group papers by section
    const papersBySection = {};

    visiblePapers.forEach(paperCard => {
        // Find the section this paper belongs to
        const sectionElement = paperCard.closest('.papers-container').previousElementSibling;
        const sectionName = sectionElement.textContent.split('(')[0].trim();

        if (!papersBySection[sectionName]) {
            papersBySection[sectionName] = [];
        }

        // Get paper data
        const title = paperCard.querySelector('.paper-title-text').textContent;
        const pdfUrl = paperCard.querySelector('.paper-title a').getAttribute('href');

        // Get keywords (only checked ones)
        const keywordInputs = paperCard.querySelectorAll('.keyword-input');
        const keywords = Array.from(keywordInputs)
            .map(input => input.value.trim())
            .filter(keyword => keyword !== '');

        // Get comments (only if export checkbox is checked)
        const commentsCheckbox = paperCard.querySelector('.comments-checkbox');
        let comments = '';
        if (commentsCheckbox && commentsCheckbox.checked) {
            comments = paperCard.querySelector('.comments-content').textContent;
        }

        // Get TL;DR
        const tldr = paperCard.querySelector('.tldr-content').textContent;

        // Add paper to the section
        papersBySection[sectionName].push({
            title,
            pdfUrl,
            keywords,
            comments,
            tldr
        });
    });

    // Generate markdown content
    let markdownContent = '';

    for (const [section, papers] of Object.entries(papersBySection)) {
        if (section === 'Others') continue;
        if (papers.length === 0) continue;

        markdownContent += `# ${section}\n\n`;

        for (const paper of papers) {
            markdownContent += `${paper.pdfUrl}\n`;
            markdownContent += `标题： ${paper.title}\n`;

            if (paper.keywords.length > 0) {
                markdownContent += `**Keywords:** ${paper.keywords.join(', ')}\n`;
            }

            if (paper.comments) {
                markdownContent += `**Comments:** ${paper.comments}\n`;
            }

            if (paper.tldr) {
                markdownContent += `**TL;DR:** ${paper.tldr}\n`;
            }

            markdownContent += `关键词： \n`;
            markdownContent += `简介： \n`;

            markdownContent += '\n\n';
        }
    }

    // Create and download the markdown file
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'paper_report.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
