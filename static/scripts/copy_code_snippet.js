function copyCode(button) {
    // Encontra a tag <code> mais próxima dentro do mesmo bloco <pre>
    const preElement = button.closest('.code-block-container');
    const codeElement = preElement.querySelector('code');
    
    if (!codeElement) return;

    // Copia o texto para a área de transferência
    navigator.clipboard.writeText(codeElement.innerText).then(() => {
        // Feedback visual de sucesso
        const originalText = button.innerText;
        button.innerText = 'Copiado!';
        button.classList.replace('btn-outline-secondary', 'btn-success');
        button.disabled = true;

        // Restaura o botão após 2 segundos
        setTimeout(() => {
            button.innerText = originalText;
            button.classList.replace('btn-success', 'btn-outline-secondary');
            button.disabled = false;
        }, 2000);
    }).catch(err => {
        console.error('Erro ao copiar código: ', err);
    });
}