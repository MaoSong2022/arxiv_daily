/**
 * Toggle abstract visibility
 * @param {HTMLElement} button - The button that was clicked
 */
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

/**
 * Scroll to a specific section
 * @param {string} sectionId - The ID of the section to scroll to
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

/**
 * Toggle paper visibility
 * @param {HTMLElement} button - The button that was clicked
 * @param {string} paperId - The ID of the paper
 */
function togglePaperVisibility(button, paperId) {
    const paperCard = button.closest('.paper-card');
    if (paperCard.classList.contains('hidden')) {
        paperCard.classList.remove('hidden');
        button.textContent = "Hide";
    } else {
        paperCard.classList.add('hidden');
        button.textContent = "Show";
    }
}

/**
 * Add a new keyword field
 * @param {HTMLElement} button - The button that was clicked
 */
function addKeywordField(button) {
    const keywordsDiv = button.parentElement;
    const newInput = document.createElement('input');
    newInput.type = 'text';
    newInput.className = 'keyword-input';
    newInput.placeholder = 'Add keyword';
    keywordsDiv.insertBefore(newInput, button);
}

/**
 * Toggle comments edit mode
 * @param {HTMLElement} container - The container element
 */
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

/**
 * Toggle TL;DR edit mode
 * @param {HTMLElement} container - The container element
 */
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
 * Update card size
 * @param {string} size - The card size (small, medium, large, full)
 */
function updateCardSize(size) {
    const mainContent = document.querySelector('.main-content');
    // Remove existing size classes
    mainContent.classList.remove('card-size-small', 'card-size-medium', 'card-size-large', 'card-size-full');
    // Add new size class
    mainContent.classList.add(`card-size-${size}`);
    // Save preference to localStorage
    localStorage.setItem('preferredCardSize', size);
}

/**
 * Export selected papers to JSON
 */
function exportSelectedPapers() {
    const selectedPapers = collectSelectedPapers();

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

/**
 * Export selected papers to Markdown
 */
function exportSelectedPapersToMarkdown() {
    const selectedPapers = collectSelectedPapers();

    if (selectedPapers.length === 0) {
        alert('No visible papers to export.');
        return;
    }

    // Generate markdown content
    let markdownContent = '# Selected Papers\n\n';

    selectedPapers.forEach(paper => {
        markdownContent += `## ${paper.title}\n\n`;

        if (paper.authors && paper.authors.length > 0) {
            markdownContent += `**Authors:** ${paper.authors.join(', ')}\n\n`;
        }

        if (paper.pdf_url) {
            markdownContent += `**PDF:** [${paper.pdf_url}](${paper.pdf_url})\n\n`;
        }

        if (paper.keywords && paper.keywords.length > 0) {
            markdownContent += `**Keywords:** ${paper.keywords.join(', ')}\n\n`;
        }

        if (paper.tldr) {
            markdownContent += `**TL;DR:** ${paper.tldr}\n\n`;
        }

        if (paper.abstract) {
            markdownContent += `### Abstract\n\n${paper.abstract}\n\n`;
        }

        if (paper.comments) {
            markdownContent += `### Comments\n\n${paper.comments}\n\n`;
        }

        markdownContent += '---\n\n';
    });

    // Create markdown file and trigger download
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'exported_papers.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Collect data from selected papers
 * @returns {Array} Array of paper objects
 */
function collectSelectedPapers() {
    const selectedPapers = [];
    const visiblePaperCards = document.querySelectorAll('.paper-card:not(.hidden)');

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

        // Get comments
        let comments = '';
        const commentsElement = paperCard.querySelector('.comments-content');
        if (commentsElement) {
            comments = commentsElement.textContent.trim();
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

    return selectedPapers;
}

/**
 * Toggle visibility of all papers in a section
 * @param {string} sectionId - The ID of the section
 * @param {boolean} show - Whether to show or hide the papers
 */
function toggleSectionSelection(sectionId, show) {
    const section = document.getElementById(sectionId);
    if (section) {
        const paperCards = section.nextElementSibling.querySelectorAll('.paper-card');
        paperCards.forEach(card => {
            if (show) {
                card.classList.remove('hidden');
                const hideButton = card.querySelector('.visibility-toggle');
                if (hideButton) hideButton.textContent = "Hide";
            } else {
                card.classList.add('hidden');
                const hideButton = card.querySelector('.visibility-toggle');
                if (hideButton) hideButton.textContent = "Show";
            }
        });
    }
}

/**
 * Delete a category and its papers
 * @param {string} categoryId - The ID of the category to delete
 * @param {Event} event - The click event
 */
function deleteCategory(categoryId, event) {
    // Prevent the click from triggering the parent link
    event.stopPropagation();
    
    // Ask for confirmation
    if (!confirm(`Are you sure you want to delete this category and all its papers?`)) {
        return;
    }
    
    // Find the category section
    const sectionHeader = document.getElementById(categoryId);
    if (!sectionHeader) return;
    
    // Find the papers container
    const papersContainer = sectionHeader.nextElementSibling;
    if (!papersContainer) return;
    
    // Remove the section header and papers container
    sectionHeader.remove();
    papersContainer.remove();
    
    // Remove the sidebar item
    const sidebarItem = document.querySelector(`.sidebar-link[data-section="${categoryId}"]`).closest('.sidebar-item');
    if (sidebarItem) {
        sidebarItem.remove();
    }
    
    // If there are no more categories, show a message
    const remainingCategories = document.querySelectorAll('.section-header');
    if (remainingCategories.length === 0) {
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            const noContentMsg = document.createElement('div');
            noContentMsg.className = 'no-content-message';
            noContentMsg.textContent = 'No paper categories available.';
            mainContent.appendChild(noContentMsg);
        }
    }
}

/**
 * Initialize the page
 */
document.addEventListener('DOMContentLoaded', function () {
    // Highlight active section in sidebar
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

    // Restore preferred card size from localStorage
    const preferredCardSize = localStorage.getItem('preferredCardSize');
    if (preferredCardSize) {
        updateCardSize(preferredCardSize);
        const sizeSelector = document.getElementById('card-size-selector');
        if (sizeSelector) {
            sizeSelector.value = preferredCardSize;
        }
    }
}); 