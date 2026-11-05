// ==========================================
// 1. REUSABLE ENGINES (CORE FUNCTIONS)
// ==========================================
/**
 * Inserts a markdown code block at the current cursor position.
 * Can be reused anywhere (main forms or inside modals).
 * @param {HTMLTextAreaElement} textarea - The target textarea element.
 * @param {string} language - The name of the programming language.
 */
function injectMarkdownSnippet(textarea, language) {
    if (!textarea || !language) return;

    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    
    // Clean, standard markdown format string
    const codeBlock = `\n\`\`\`\n add ${language} code here\n\´\´\´\n`;

    // Inject text at cursor position
    textarea.value = textarea.value.substring(0, startPos) + codeBlock + textarea.value.substring(endPos);
    
    // Refocus and place cursor exactly inside the backticks block
    textarea.focus();
    const newCursorPos = startPos + codeBlock.length;
    textarea.selectionStart = textarea.selectionEnd = newCursorPos;
}

/**
 * Updates a specific character count text element and progress bar.
 * @param {HTMLTextAreaElement} textarea - The source textarea element.
 * @param {string} counterId - The ID of the text counter element.
 * @param {string} barId - The ID of the progress bar element.
 */
function handleCharacterCount(textarea, counterId, barId) {
    const counterEl = document.getElementById(counterId);
    const barEl = document.getElementById(barId);
    
    if (!textarea) return;

    const currentLength = textarea.value.length;
    const maxLength = textarea.getAttribute('maxlength') || 1500;

    // Update the visual text indicator state
    if (counterEl) {
        counterEl.textContent = `${currentLength} / ${maxLength}`;
    }

    // Update the progress element layout bar fill state
    if (barEl) {
        barEl.value = currentLength;
        barEl.setAttribute('max', maxLength);
    }
}


/**
 * count number of chars for textareas and adding progress-bar style
 */
function updateCount(textarea, counterId, progressId) {
    if (!textarea) return;

    const currentLength = textarea.value.length;
    const maxLength = parseInt(textarea.getAttribute('maxlength'), 10) || 100;
    const remaining = maxLength - currentLength;

    // Target the specific counter and progress bar
    const counter = document.getElementById(counterId);
    const progressBar = document.getElementById(progressId);

    // Update the values
    if (counter) {
        counter.textContent = `${currentLength} / ${maxLength}`;
    }
    
    if (progressBar) {
        progressBar.setAttribute('max', maxLength);
        progressBar.value = currentLength;

        // Calculate percentage of remaining characters (100% is empty, 0% is full/no remaining)
        // Calculate the percentage of characters remaining
        const pctRemaining = (remaining / maxLength) * 100;
        
        // Determine color based on how close you are to 0 remaining characters
        let color = '#00E676'; // Green
        
        if (pctRemaining <= 10) {
            color = '#D32F2F'; // Red (Critical: Less than 10% space left)
        } else if (pctRemaining <= 25) {
            color = '#FF8F00'; // Orange (Warning: Less than 25% space left)
        } else if (pctRemaining <= 50) {
            color = '#FFFF00'; // Yellow (Caution: Less than 50% space left)
        }
        
        // Apply the color dynamically to the native progress bar
        progressBar.style.setProperty('--progress-color', color);
    }
};


/**
 * Renders visual tag badges based on the text value of a target field.
 * @param {HTMLElement} parentContainer - The form or modal parent wrapper.
 */
function renderDynamicBadges(parentContainer) {
    const tagsInput = parentContainer.querySelector('.input-tag-list');
    const badgeContainer = parentContainer.querySelector('.dynamic-badge-container');
    if (!tagsInput || !badgeContainer) return;

    badgeContainer.innerHTML = '';

    const cleanValue = tagsInput.value.replace(/\s+/g, ' ').trim();
    if (!cleanValue) return;
    
    const currentTags = cleanValue.split(' ');

    currentTags.forEach((tag, index) => {
        const badge = document.createElement('span');
        badge.className = 'badge bg-secondary text-light d-flex align-items-center gap-1 py-1.5 px-2 animate__animated animate__fadeIn';
        badge.style.fontSize = '0.85rem';
        badge.innerHTML = `
            ${tag}
            <i class="bi bi-x-circle-fill text-warning remove-tag-btn" data-tag="${tag}" data-index="${index}" style="cursor:pointer; font-size:0.95rem;"></i>
        `;
        badgeContainer.appendChild(badge);
    });
}


// ==========================================
// 2. AUTOMATED GLOBAL CONTROLLERS (DOM LOADER)
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    
    // Initialize initial tags right away on page load (Crucial for Edit Post mode!)
    const activeForm = document.querySelector('.question-form') || document.querySelector('form');
    if (activeForm) {
        renderDynamicBadges(activeForm);
        
        // Sync badges instantly if the user manually types or edits the tag string field
        const tagsInput = activeForm.querySelector('.input-tag-list');
        if (tagsInput) {
            tagsInput.addEventListener('input', function() {
                renderDynamicBadges(activeForm);
            });
        }
    }

    // === DROPDOWN LANGUAGE MANAGER ===
    document.addEventListener('click', function (event) {
        const langBtn = event.target.closest('.snippet-lang-btn');
        if (!langBtn) return;

        event.preventDefault(); 

        const chosenLanguage = langBtn.value;
        const parentContainer = langBtn.closest('form') || langBtn.closest('.col-10.col-lg-8') || langBtn.closest('.modal-content');
        if (!parentContainer) return;

        const textarea = parentContainer.querySelector('textarea');
        const tagsInput = parentContainer.querySelector('.input-tag-list');

        // A. Call the modular text snippet injector engine
        if (textarea) {
            injectMarkdownSnippet(textarea, chosenLanguage);
            
            // Auto-refresh the counting meters inside the active view
            const isEdit = parentContainer.getAttribute('data-mode') === 'edit';
            handleCharacterCount(textarea, isEdit ? 'edit-counter' : 'new-counter', isEdit ? 'edit-bars' : 'new-bars');
        }

        // B. Update text metadata string input array fields
        if (tagsInput) {
            let currentTags = tagsInput.value.trim() ? tagsInput.value.trim().replace(/\s+/g, ' ').split(' ') : [];
            currentTags.push(chosenLanguage);
            tagsInput.value = currentTags.join(' ');
        }

        // C. Refresh component badge rendering loops
        renderDynamicBadges(parentContainer);
    });

    // === DYNAMIC BADGE REMOVAL CONTROLLER ===
    document.addEventListener('click', function (event) {
        const removeBtn = event.target.closest('.remove-tag-btn');
        if (!removeBtn) return;

        const indexToRemove = parseInt(removeBtn.getAttribute('data-index'), 10);
        const parentContainer = removeBtn.closest('form') || removeBtn.closest('.col-10.col-lg-8') || removeBtn.closest('.modal-content');
        if (!parentContainer) return;

        const tagsInput = parentContainer.querySelector('.input-tag-list');
        if (tagsInput) {
            let currentTags = tagsInput.value.trim() ? tagsInput.value.trim().replace(/\s+/g, ' ').split(' ') : [];
            currentTags.splice(indexToRemove, 1);
            tagsInput.value = currentTags.join(' ');
        }

        renderDynamicBadges(parentContainer);
    });
});
