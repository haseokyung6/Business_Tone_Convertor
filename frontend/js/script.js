document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const inputText = document.getElementById('inputText');
    const outputText = document.getElementById('outputText');
    const charCount = document.getElementById('charCount');
    const convertBtn = document.getElementById('convertBtn');
    const copyBtn = document.getElementById('copyBtn');
    const feedbackMsg = document.getElementById('feedbackMsg');
    const personaBtns = document.querySelectorAll('.persona-btn');

    // State
    let selectedPersona = 'boss'; // default
    const MAX_CHARS = 500;
    const API_URL = '/api/convert';

    // 1. Persona Selection
    personaBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            personaBtns.forEach(b => b.classList.remove('active'));
            // Add active class to clicked
            btn.classList.add('active');
            // Update state
            selectedPersona = btn.dataset.persona;
        });
    });

    // 2. Character Count & Validation
    inputText.addEventListener('input', () => {
        const currentLength = inputText.value.length;
        charCount.textContent = `${currentLength} / ${MAX_CHARS}`;
        
        if (currentLength > MAX_CHARS) {
            charCount.style.color = 'var(--error-color)';
            convertBtn.disabled = true;
        } else {
            charCount.style.color = '#888';
            convertBtn.disabled = currentLength === 0;
        }
    });

    // 3. Conversion Logic
    convertBtn.addEventListener('click', async () => {
        const text = inputText.value.trim();
        if (!text) return;

        // UI Loading State
        setLoading(true);
        outputText.textContent = '';
        copyBtn.disabled = true;
        feedbackMsg.className = 'feedback-msg';

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    target_persona: selectedPersona
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Server Error');
            }

            // Display Result
            outputText.textContent = data.converted_text;
            copyBtn.disabled = false;

        } catch (error) {
            console.error('Error:', error);
            outputText.textContent = '오류가 발생했습니다. 잠시 후 다시 시도해주세요.\n' + error.message;
            feedbackMsg.textContent = '변환 실패';
            feedbackMsg.classList.add('error');
        } finally {
            setLoading(false);
        }
    });

    // 4. Copy to Clipboard
    copyBtn.addEventListener('click', async () => {
        const textToCopy = outputText.textContent;
        try {
            await navigator.clipboard.writeText(textToCopy);
            showFeedback('복사되었습니다!', 'success');
        } catch (err) {
            console.error('Failed to copy:', err);
            showFeedback('복사 실패', 'error');
        }
    });

    // Helpers
    function setLoading(isLoading) {
        if (isLoading) {
            convertBtn.disabled = true;
            convertBtn.innerHTML = '<span class="spinner"></span> 변환 중...';
        } else {
            convertBtn.disabled = false;
            convertBtn.textContent = '변환하기';
        }
    }

    function showFeedback(msg, type) {
        feedbackMsg.textContent = msg;
        feedbackMsg.className = `feedback-msg ${type}`;
        setTimeout(() => {
            feedbackMsg.classList.remove(type);
        }, 2000);
    }
});
