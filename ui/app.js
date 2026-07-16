const ui = {
    pokemon: null,
    pokemonForm: null,
    move: null,

    enemy: null,
    enemyPokemon: null,
    enemyForm: null
};

const controls = {
    shadow: null,
    minAtk: null,
    maxAtk: null,
    minLevel: null,
    maxLevel: null,
    trainerLevel: null,
    calculateButton: null,
    message: null,
    resultsSection: null,
    enemyCard: null,
    breakpointsTable: null,
};

function fillSelect(select, values) {

    select.innerHTML = "";

    for (const value of values) {

        const option = document.createElement("option");
        option.value = value;
        option.text = value;

        select.appendChild(option);
    }

}

async function loadOptions(select, apiMethod, ...args) {

    const result = await apiMethod(...args);

    const values = Object.values(result)[0];

    select.clear();
    select.clearOptions();

    values.forEach(value => {
        select.addOption({
            value: value,
            text: value
        });
    });

    select.refreshOptions(false);

    return values;

}

function clearSelect(select) {

    select.clear();
    select.clearOptions();
    select.disable();

}

function enableSelect(select) {

    select.enable();

}

function showError(message) {

    controls.message.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            ${message}
            <button type="button"
                    class="btn-close"
                    data-bs-dismiss="alert">
            </button>
        </div>
    `;

}

function clearMessage() {

    controls.message.innerHTML = "";

}

function buildRequest() {

    return {

        pokemon: {
            name: ui.pokemon.getValue(),
            form: ui.pokemonForm.getValue(),
            shadow: controls.shadow.checked
        },

        move: ui.move.getValue(),

        min_atk: parseInt(controls.minAtk.value),
        max_atk: parseInt(controls.maxAtk.value),

        min_level: parseFloat(controls.minLevel.value),
        max_level: parseFloat(controls.maxLevel.value),

        enemy: ui.enemy.getValue(),

        enemy_pokemon: {
            name: ui.enemyPokemon.getValue(),
            form: ui.enemyForm.getValue()
        },

        trainer_level: parseInt(controls.trainerLevel.value)

    };

}

function validateRequest(request) {

    if (!request.pokemon.name)
        return "Please select your Pokémon.";

    if (!request.pokemon.form)
        return "Please select your Pokémon form.";

    if (!request.move)
        return "Please select a move.";

    if (!request.enemy)
        return "Please select an enemy.";

    if (!request.enemy_pokemon.name)
        return "Please select the enemy Pokémon.";

    if (!request.enemy_pokemon.form)
        return "Please select the enemy Pokémon form.";

    if (request.min_atk > request.max_atk)
        return "Minimum attack cannot be greater than maximum attack.";

    if (request.min_level > request.max_level)
        return "Minimum level cannot be greater than maximum level.";

    return null;

}

function damageColor(damage, min, max) {

    if (min === max)
        return "hsl(210, 80%, 85%)";

    const t = (damage - min) / (max - min);

    const lightness = 92 - t * 32;

    return `hsl(210, 80%, ${lightness}%)`;

}

function displayResults(result) {

    let minDamage = Infinity;
    let maxDamage = -Infinity;

    for (const bp of result.breakpoints) {
        for (const d of bp.damages) {
            minDamage = Math.min(minDamage, d.damage);
            maxDamage = Math.max(maxDamage, d.damage);
        }
    }

    const enemy = result.enemy;

    controls.enemyCard.innerHTML = `
        <div class="card">
            <div class="card-header">
                Enemy Stats
            </div>

            <div class="card-body">

                <div class="row text-center">

                    <div class="col">
                        <h5>Attack</h5>
                        <p>${enemy.atk.toFixed(2)}</p>
                    </div>

                    <div class="col">
                        <h5>Defense</h5>
                        <p>${enemy.def.toFixed(2)}</p>
                    </div>

                    <div class="col">
                        <h5>HP</h5>
                        <p>${enemy.hp}</p>
                    </div>

                    <div class="col">
                        <h5>CP</h5>
                        <p>${enemy.cp}</p>
                    </div>

                </div>

            </div>
        </div>
    `;

    let header = `<tr><th class="text-center">Level</th>`;

    for (const bp of result.breakpoints) {
        header += `<th class="text-center">${bp.atk}</th>`;
    }

    header += "</tr>";

    let rows = "";

    for (let i = 0; i < result.breakpoints[0].damages.length; i++) {

        rows += `<tr>`;

        rows += `<th class="text-center">${Number(result.breakpoints[0].damages[i].level).toFixed(1)}</th>`;

        for (const bp of result.breakpoints) {
            rows += `
                <td
                    class="text-center"
                    style="background-color: ${damageColor(bp.damages[i].damage, minDamage, maxDamage)};">
                    ${bp.damages[i].damage}
                </td>
            `;
        }

        rows += `</tr>`;
    }

    controls.breakpointsTable.innerHTML = `
        <div class="card mt-4">
            <div class="card-header">
                Damage Breakpoints
            </div>

            <div class="card-body p-0">
                <div class="table-responsive breakpoint-table">
                    <table class="table table-bordered table-hover align-middle mb-0">

                        <thead class="table-dark sticky-top">
                            ${header}
                        </thead>

                        <tbody>
                            ${rows}
                        </tbody>

                    </table>
                </div>
            </div>
        </div>
    `;

}

window.addEventListener("pywebviewready", async () => {

    ui.pokemon = new TomSelect("#pokemon");
    ui.pokemonForm = new TomSelect("#pokemonForm");
    ui.move = new TomSelect("#move");

    ui.enemy = new TomSelect("#enemy");
    ui.enemyPokemon = new TomSelect("#enemyPokemon");
    ui.enemyForm = new TomSelect("#enemyForm");

    controls.shadow = document.getElementById("shadow");
    controls.minAtk = document.getElementById("minAtk");
    controls.maxAtk = document.getElementById("maxAtk");
    controls.minLevel = document.getElementById("minLevel");
    controls.maxLevel = document.getElementById("maxLevel");
    controls.trainerLevel = document.getElementById("trainerLevel");
    controls.calculateButton = document.getElementById("calculateButton");
    controls.message = document.getElementById("message");
    controls.resultsSection = document.getElementById("resultsSection");
    controls.enemyCard = document.getElementById("enemyCard");
    controls.breakpointsTable = document.getElementById("breakpointsTable");

    controls.resultsSection.classList.add("d-none");

    fillSelect(
        controls.minAtk,
        [...Array(16).keys()]
    );

    fillSelect(
        controls.maxAtk,
        [...Array(16).keys()]
    );

    const levels = [];

    for (let level = 1; level <= 55; level += 0.5)
        levels.push(level.toFixed(1));

    fillSelect(controls.minLevel, levels);
    fillSelect(controls.maxLevel, levels);

    fillSelect(
        controls.trainerLevel,
        Array.from({ length: 73 }, (_, i) => i + 8)
    );

    controls.minAtk.value = "10";
    controls.maxAtk.value = "15";

    controls.minLevel.value = "40.0";
    controls.maxLevel.value = "50.0";

    controls.trainerLevel.value = "70";

    await loadOptions(
        ui.pokemon,
        window.pywebview.api.get_pokemon_names
    );

    await loadOptions(
        ui.enemy,
        window.pywebview.api.get_enemy_names
    );

    await loadOptions(
        ui.enemyPokemon,
        window.pywebview.api.get_pokemon_names
    );

    ui.pokemon.on("change", async function(value) {

        clearSelect(ui.pokemonForm);
        clearSelect(ui.move);

        if (!value)
            return;

        enableSelect(ui.pokemonForm);

        const forms = await loadOptions(
            ui.pokemonForm,
            window.pywebview.api.get_pokemon_forms,
            value
        );

        if (forms.length > 0) {
            ui.pokemonForm.setValue(forms[0]);
        }

    });

    ui.pokemonForm.on("change", async function(value) {

        clearSelect(ui.move);

        if (!value)
            return;

        enableSelect(ui.move);

        await loadOptions(
            ui.move,
            window.pywebview.api.get_move_names,
            ui.pokemon.getValue(),
            value
        );

    });

    ui.enemyPokemon.on("change", async function(value) {

        clearSelect(ui.enemyForm);

        if (!value)
            return;

        enableSelect(ui.enemyForm);

        const forms = await loadOptions(
            ui.enemyForm,
            window.pywebview.api.get_pokemon_forms,
            value
        );

        if (forms.length > 0) {
            ui.enemyForm.setValue(forms[0]);
        }

    });

    controls.calculateButton.onclick = async function () {

        clearMessage();
        clearMessage();

        controls.enemyCard.innerHTML = "";
        controls.breakpointsTable.innerHTML = "";

        controls.resultsSection.classList.add("d-none");

        const request = buildRequest();

        const error = validateRequest(request);

        if (error) {
            showError(error);
            return;
        }

        try {

            const result =
                await window.pywebview.api.calculate_damage(request);

            displayResults(result);

            controls.resultsSection.classList.remove("d-none");

        }
        catch (error) {

            console.error(error);

            showError("An error occurred while calculating damage.");

        }

    };

});
