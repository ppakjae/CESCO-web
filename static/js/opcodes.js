console.log('opcodes.js loaded');

function toggleRow(row, filename) {
    console.log('loadMarkdownFile called with filename:', filename);
    fetch(filename)
        .then(response => response.text())
        .then(md => {
            const mdParser = new markdownit({html: true});
            const html = mdParser.render(md);

            const formattedHtml = `<div class="markdown-body">${html}</div>`;

            if (row.getAttribute('data-expanded') === 'true') {
                row.nextSibling.remove();
                row.setAttribute('data-expanded', 'false');
            } else {
                const newRow = document.createElement('tr');
                newRow.classList.add('description');
                const newCell = document.createElement('td');
                newCell.innerHTML = formattedHtml;
                newCell.setAttribute('colspan', row.childElementCount);

                const cells = newCell.querySelectorAll('td, th');
                cells.forEach(cell => {
                    if (cell.textContent.trim() === '*') {
                        cell.style.visibility = 'hidden';
                        cell.classList.add('no-border');
                    }
                });

                newRow.appendChild(newCell);
                row.parentNode.insertBefore(newRow, row.nextSibling);
                row.setAttribute('data-expanded', 'true');
            }
        });
}