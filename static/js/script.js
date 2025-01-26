const selecionadosDiv = document.getElementById('selecionados');
const form = document.getElementById('emprestimoForm');

document.querySelectorAll('.adicionar').forEach(button => {
    button.addEventListener('click', () => {
        const livroId = button.dataset.id;
        const titulo = button.dataset.titulo;
        const preco = button.dataset.preco;

        if (document.querySelector(`#livro-${livroId}`)) {
            alert('Este livro já foi adicionado!');
            return;
        }

        const div = document.createElement('div');
        div.id = `livro-${livroId}`;
        div.innerHTML = `
            <p>${titulo} (R$ ${preco})</p>
            <input type="hidden" name="livros[]" value="${livroId}">
            <label>Quantidade: </label>
            <input type="number" name="quantidades[]" min="1" value="1">
            <button type="button" onclick="remover(${livroId})">Remover</button>
        `;
        selecionadosDiv.appendChild(div);
    });
});

function remover(id) {
    const div = document.getElementById(`livro-${id}`);
    if (div) {
        div.querySelector('input[name="livros[]"]').remove();
        div.querySelector('input[name="quantidades[]"]').remove();
        div.remove();
    }
}
