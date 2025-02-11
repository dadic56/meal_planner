const socket = io();
let selectedPlats = new Set();
let currentPlat = '';

function selectPlat(element) {
    console.log("selectPlat called");
    const plat = element.querySelector('.plat-text').textContent.trim();
    const platContainer = element.parentElement;
    if (selectedPlats.has(plat)) {
        selectedPlats.delete(plat);
        platContainer.classList.remove('selected');
    } else {
        selectedPlats.add(plat);
        platContainer.classList.add('selected');
    }
    socket.emit('select_plat', { plat: plat });
}

function genererListe() {
    console.log("genererListe called");
    socket.emit('generer_liste', Array.from(selectedPlats));
}

function resetSelection() {
    console.log("resetSelection called");
    if (confirm("Voulez-vous vraiment désélectionner tous les plats ?")) {
        selectedPlats.clear();
        document.querySelectorAll('.plat-container').forEach(container => {
            container.classList.remove('selected');
            container.querySelector('.plat').setAttribute('aria-pressed', 'false');
        });
        socket.emit('reset_selection');
    }
}

function openAjouterPlatModal() {
    console.log("openAjouterPlatModal called");
    document.getElementById('ajouterPlatModal').style.display = 'block';
}

function closeAjouterPlatModal() {
    console.log("closeAjouterPlatModal called");
    document.getElementById('ajouterPlatModal').style.display = 'none';
}

function ajouterIngredient() {
    console.log("ajouterIngredient called");
    const container = document.getElementById('ingredientsContainer');
    const ingredientDiv = document.createElement('div');
    ingredientDiv.className = 'ingredient-div';
    
    const ingredientInput = document.createElement('input');
    ingredientInput.type = 'text';
    ingredientInput.className = 'ingredient';
    ingredientInput.placeholder = 'Ingrédient';
    
    const quantiteInput = document.createElement('input');
    quantiteInput.type = 'text';
    quantiteInput.className = 'quantite';
    quantiteInput.placeholder = 'Quantité';
    
    const uniteSelect = document.createElement('select');
    uniteSelect.className = 'unite';
    uniteSelect.innerHTML = `
        <option value="pièce">pièce</option>
        <option value="g">g</option>
        <option value="kg">kg</option>
        <option value="ml">ml</option>
        <option value="cl">cl</option>
        <option value="l">l</option>
        <option value="cuil. à café">cuil. à café</option>
        <option value="cuil. à soupe">cuil. à soupe</option>
        <option value="au goût">au goût</option>
        <option value="besoin">besoin</option>
        <option value="pincée">pincée</option>
        <option value="croûtes">croûtes</option>
        <option value="tranches">tranches</option>
        <option value="portions">portions</option>
        <option value="tête">tête</option>
        <option value="baguette">baguette</option>
        <option value="x 400">x 400</option>
        <!-- Ajouter d'autres unités si nécessaire -->
    `;
    
    ingredientDiv.appendChild(ingredientInput);
    ingredientDiv.appendChild(quantiteInput);
    ingredientDiv.appendChild(uniteSelect);
    container.insertBefore(ingredientDiv, container.lastElementChild);
}

function ajouterPlat() {
    console.log("ajouterPlat called");
    const nomPlat = document.getElementById('nomPlat').value.trim();
    const ingredients = Array.from(document.getElementsByClassName('ingredient-div')).map(div => {
        const ingredient = div.querySelector('.ingredient').value.trim();
        const quantite = div.querySelector('.quantite').value.trim();
        const unite = div.querySelector('.unite').value;
        return { ingredient, quantite, unite };
    }).filter(ing => ing.ingredient && ing.quantite && ing.unite);
    
    if (nomPlat && ingredients.length > 0) {
        socket.emit('ajouter_plat', { plat: nomPlat, ingredients: ingredients });
        closeAjouterPlatModal();
    } else {
        alert("Veuillez entrer un nom de plat et au moins un ingrédient avec une quantité et une unité.");
    }
}

function openOptionsModal(plat) {
    console.log("openOptionsModal called with plat:", plat);
    currentPlat = plat; // Définir currentPlat avec le nom du plat
    document.getElementById('platName').textContent = plat;
    document.getElementById('optionsModal').style.display = 'block';
}

function closeOptionsModal() {
    console.log("closeOptionsModal called");
    document.getElementById('optionsModal').style.display = 'none';
}

function openModifierPlatModal() {
    console.log("openModifierPlatModal called");
    document.getElementById('modifierPlatName').textContent = currentPlat;
    document.getElementById('nouveauNomPlat').value = currentPlat;
    const modifierIngredientsContainer = document.getElementById('modifierIngredientsContainer');
    modifierIngredientsContainer.innerHTML = ''; // Clear previous ingredients

    // Fetch existing ingredients for the current plat
    fetch(`/get_ingredients?plat=${currentPlat}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(ingredient => {
                const ingredientDiv = createIngredientDiv(ingredient);
                modifierIngredientsContainer.appendChild(ingredientDiv);
            });
        });

    document.getElementById('modifierPlatModal').style.display = 'block';
}

function closeModifierPlatModal() {
    console.log("closeModifierPlatModal called");
    document.getElementById('modifierPlatModal').style.display = 'none';
}

function createIngredientDiv(ingredient = null) {
    const ingredientDiv = document.createElement('div');
    ingredientDiv.className = 'ingredient-div';

    const ingredientInput = document.createElement('input');
    ingredientInput.type = 'text';
    ingredientInput.className = 'ingredient';
    ingredientInput.placeholder = 'Ingrédient';
    if (ingredient) ingredientInput.value = ingredient['Ingrédient'];

    const quantiteInput = document.createElement('input');
    quantiteInput.type = 'text';
    quantiteInput.className = 'quantite';
    quantiteInput.placeholder = 'Quantité';
    if (ingredient) quantiteInput.value = ingredient['Quantité'];

    const uniteSelect = document.createElement('select');
    uniteSelect.className = 'unite';
    uniteSelect.innerHTML = `
        <option value="pièce" ${ingredient && ingredient['Unité'] === 'pièce' ? 'selected' : ''}>pièce</option>
        <option value="g" ${ingredient && ingredient['Unité'] === 'g' ? 'selected' : ''}>g</option>
        <option value="kg" ${ingredient && ingredient['Unité'] === 'kg' ? 'selected' : ''}>kg</option>
        <option value="ml" ${ingredient && ingredient['Unité'] === 'ml' ? 'selected' : ''}>ml</option>
        <option value="cl" ${ingredient && ingredient['Unité'] === 'cl' ? 'selected' : ''}>cl</option>
        <option value="l" ${ingredient && ingredient['Unité'] === 'l' ? 'selected' : ''}>l</option>
        <option value="cuil. à café" ${ingredient && ingredient['Unité'] === 'cuil. à café' ? 'selected' : ''}>cuil. à café</option>
        <option value="cuil. à soupe" ${ingredient && ingredient['Unité'] === 'cuil. à soupe' ? 'selected' : ''}>cuil. à soupe</option>
        <option value="au goût" ${ingredient && ingredient['Unité'] === 'au goût' ? 'selected' : ''}>au goût</option>
        <option value="besoin" ${ingredient && ingredient['Unité'] === 'besoin' ? 'selected' : ''}>besoin</option>
        <option value="pincée" ${ingredient && ingredient['Unité'] === 'pincée' ? 'selected' : ''}>pincée</option>
        <option value="croûtes" ${ingredient && ingredient['Unité'] === 'croûtes' ? 'selected' : ''}>croûtes</option>
        <option value="tranches" ${ingredient && ingredient['Unité'] === 'tranches' ? 'selected' : ''}>tranches</option>
        <option value="portions" ${ingredient && ingredient['Unité'] === 'portions' ? 'selected' : ''}>portions</option>
        <option value="tête" ${ingredient && ingredient['Unité'] === 'tête' ? 'selected' : ''}>tête</option>
        <option value="baguette" ${ingredient && ingredient['Unité'] === 'baguette' ? 'selected' : ''}>baguette</option>
        <option value="x 400" ${ingredient && ingredient['Unité'] === 'x 400' ? 'selected' : ''}>x 400</option>
        <!-- Ajouter d'autres unités si nécessaire -->
    `;

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Supprimer';
    deleteButton.onclick = () => ingredientDiv.remove();

    ingredientDiv.appendChild(ingredientInput);
    ingredientDiv.appendChild(quantiteInput);
    ingredientDiv.appendChild(uniteSelect);
    ingredientDiv.appendChild(deleteButton);
    return ingredientDiv;
}

function ajouterIngredientModifier() {
    console.log("ajouterIngredientModifier called");
    const container = document.getElementById('modifierIngredientsContainer');
    const ingredientDiv = createIngredientDiv();
    container.insertBefore(ingredientDiv, container.lastElementChild);
}

function modifierPlat() {
    console.log("modifierPlat called");
    const nouveauNom = document.getElementById('nouveauNomPlat').value.trim();
    const ingredients = Array.from(document.getElementById('modifierIngredientsContainer').getElementsByClassName('ingredient-div')).map(div => {
        const ingredient = div.querySelector('.ingredient').value.trim();
        const quantite = div.querySelector('.quantite').value.trim();
        const unite = div.querySelector('.unite').value;
        return { ingredient, quantite, unite };
    }).filter(ing => ing.ingredient && ing.quantite && ing.unite);
    
    if (nouveauNom && ingredients.length > 0) {
        console.log("Emitting modifier_plat event with plat:", currentPlat, "nouveauNom:", nouveauNom, "and ingredients:", ingredients);
        socket.emit('modifier_plat', { plat: currentPlat, nouveauNom: nouveauNom, ingredients: ingredients });
        closeModifierPlatModal();
        closeOptionsModal();  // Fermer également la fenêtre modale des options
    } else {
        alert("Veuillez entrer un nouveau nom de plat et au moins un ingrédient avec une quantité et une unité.");
    }
}

function supprimerPlat() {
    console.log("supprimerPlat called");
    if (confirm(`Voulez-vous vraiment supprimer le plat "${currentPlat}" ?`)) {
        socket.emit('supprimer_plat', { plat: currentPlat });
        closeOptionsModal();
    }
}

window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        closeOptionsModal();
        closeAjouterPlatModal();
        closeModifierPlatModal();
    }
});

socket.on('update_selection', function(selectedPlatsArray) {
    console.log("update_selection received");
    selectedPlats = new Set(selectedPlatsArray);
    document.querySelectorAll('.plat-container').forEach(container => {
        const plat = container.querySelector('.plat-text').textContent.trim();
        if (selectedPlats.has(plat)) {
            container.classList.add('selected');
        } else {
            container.classList.remove('selected');
        }
    });
    genererListe();
});

socket.on('liste_courses', function(data) {
    console.log("liste_courses received");
    const listeItems = document.getElementById('listeItems');
    listeItems.innerHTML = '';
    data.sort((a, b) => a.ingredient.localeCompare(b.ingredient));
    data.forEach(item => {
        const p = document.createElement('p');
        p.textContent = `${item.ingredient}: ${item.quantite} ${item.unite}`;
        listeItems.appendChild(p);
    });
});

socket.on('plat_ajoute', function(plat) {
    console.log("plat_ajoute received with plat:", plat);
    const platsContainer = document.getElementById('plats');
    const platContainer = document.createElement('div');
    platContainer.className = 'plat-container';
    platContainer.innerHTML = `
        <div class="plat" onclick="selectPlat(this)">
            <span class="plat-text">${plat}</span>
        </div>
        <div class="options-container">
            <button class="options-button" onclick="openOptionsModal('${plat}')">⋮</button>
        </div>
    `;
    platsContainer.appendChild(platContainer);
});

socket.on('plat_supprime', function(plat) {
    console.log("plat_supprime received with plat:", plat);
    const platElement = document.querySelector(`.plat-container .plat-text:contains('${plat}')`).parentElement;
    if (platElement) {
        platElement.parentElement.remove();
    }
});

socket.on('plat_modifie', function(data) {
    console.log("plat_modifie received with data:", data);
    const { ancienNom, nouveauNom } = data;
    const platElement = document.querySelector(`.plat-container .plat-text:contains('${ancienNom}')`);
    if (platElement) {
        platElement.textContent = nouveauNom;
        platElement.closest('.plat-container').querySelector('.plat').setAttribute('onclick', `selectPlat(this)`);
        platElement.closest('.plat-container').querySelector('.options-button').setAttribute('onclick', `openOptionsModal('${nouveauNom}')`);
    }
    currentPlat = nouveauNom;
    if (selectedPlats.has(ancienNom)) {
        selectedPlats.delete(ancienNom);
        selectedPlats.add(nouveauNom);
    }
    genererListe();  // Mettre à jour la liste de courses
});

socket.on('generer_liste', function(selectedPlatsArray) {
    console.log("generer_liste received");
    selectedPlats = new Set(selectedPlatsArray);
    genererListe();
});

window.addEventListener('load', () => {
    console.log("window load event");
    fetch('/get_selected_plats')
    .then(response => response.json())
    .then(data => {
        selectedPlats = new Set(data);
        document.querySelectorAll('.plat-container').forEach(container => {
            const plat = container.querySelector('.plat-text').textContent.trim();
            if (selectedPlats.has(plat)) {
                container.classList.add('selected');
            }
        });
        genererListe();
    });
});
