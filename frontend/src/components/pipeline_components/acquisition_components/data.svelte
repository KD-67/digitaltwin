<script>
    import ViewIcon from "../../../assets/view_icon.svg?raw";
    import AddIcon from "../../../assets/add_icon.svg?raw";
    import EditIcon from "../../../assets/edit_icon.svg?raw";
    import DeleteIcon from "../../../assets/delete_icon.svg?raw";
    import LevelsIcon from "../../../assets/levels_icon.svg?raw";
    import CancelIcon from "../../../assets/cancel_icon.svg?raw";

    let statusMessage = $state("");
    let mode = $state("view");
    let expandedMarker = $state("");
    let editingMarker = $state("");

    // Add new marker form
    let marker_name = $state("");
    let description = $state("");
    let unit = $state("");
    let volatility_class = $state("");

    // Edit existing marker form
    let edit_marker_name = $state(null);
    let edit_description = $state(null);
    let edit_unit = $state(null);
    let edit_volatility_class = $state(null);

    import { onMount } from "svelte";
    import { formatDate, createMarker, updateMarker, deleteMarker } from "../../../lib/services.js";
    import { appState, ensureMarkersLoaded } from "../../../lib/stores.svelte.js";

    // INTERFACE FUNCTIONALITY:
    function collapseCard() {
        expandedMarker = null;
        editingMarker = null;
    }

    // BACKEND FUNCTIONALITY:
    function handleAddNewMarker() {
        if (!window.confirm(`Are you sure you want to create this new marker? Go ahead and double check all fields one more time just to be sure :)`)) return;
        createMarker({ marker_name, description, unit, volatility_class });
        statusMessage = "marker created";
    }

    function handleDeleteMarker(marker_id) {
        if (!window.confirm(`Are you sure you want to delete marker ${marker_id}? This cannot be undone.`)) return;
        deleteMarker(marker_id);
        statusMessage = "marker deleted";
    }

    async function handleEditMarker() {
        if (!window.confirm(`Are you sure you want to make these edits? They cannot be undone.`)) return;
        const raw = { marker_name: edit_marker_name, description: edit_description, unit: edit_unit, volatility_class: edit_volatility_class };
        const updates = Object.fromEntries(Object.entries(raw).filter(([, v]) => v !== null && v !== ""));
        try {
            await updateMarker(editingMarker, updates);
            statusMessage = "Marker updated";
        } catch (e) {
            statusMessage = `Update failed: ${e.message}`;
        } finally {
            collapseCard();
        }
    }

    onMount(() => {
        ensureMarkersLoaded();
    })
</script>

<main>
<div class="main-container">
    <div id="mode-toggle-container">
        <button type="button" class="view-btn" onclick={() => {mode = "view"; statusMessage = "changed to view mode";}}>{@html ViewIcon}</button>
        <button type="button" class="add-btn" onclick={() => {mode = "add"; statusMessage = "changed to add mode";}}>{@html AddIcon}</button>

        {#if statusMessage}
            <p id="status_msg">{statusMessage}</p>
        {/if}
    </div>

    <div id="viewbox">
    <h3 id="viewbox-header">Marker Management</h3>

    {#if mode === "view"}
        <h4>View existing markers</h4>
        {#if appState.markers.length === 0}
            <p>No markers found</p>
        {/if}
        {#each appState.markers as m}
            <div class="card" role="button" tabindex='0' onkeydown={(e) => e.stopPropagation()}
                onclick={() => {
                    if (expandedMarker === m.marker_id) {
                        collapseCard();
                        statusMessage = "card collapsed";
                    } else {
                        collapseCard();
                        expandedMarker = m.marker_id;
                        statusMessage = "card expanded";
                    }
                }}>
                <div class="card-header-container">
                    <div class="card-icon-container">
                        <div class="card-icon">{@html LevelsIcon}</div>
                    </div>
                    <div class="card-title-container">{m.marker_name}</div>
                </div>
                <div class="card-actions-container">
                    <button class="edit-btn" onclick={(e) => {
                        e.stopPropagation();
                        if (editingMarker === m.marker_id) {
                            collapseCard();
                            statusMessage = "card collapsed";
                        } else {
                            expandedMarker = m.marker_id;
                            editingMarker = m.marker_id;
                            statusMessage = "marker edited";
                        }
                    }}>{@html EditIcon}</button>

                    <button class="delete-btn" onclick={(e) => { e.stopPropagation(); handleDeleteMarker(m.marker_id); }}>{@html DeleteIcon}</button>
                </div>
                <div class="card-description-container">Unit: {m.unit || '—'}, Volatility: {m.volatility_class || '—'}</div>
                {#if expandedMarker === m.marker_id}
                <div class="card-expanded-container">
                    <div class="marker-profile-container">
                            <p class="marker-profile-row" id="marker-profile-row-header"><strong>Profile</strong></p>
                            <p class="marker-profile-row"><strong>ID:</strong> {m.marker_id}</p>
                            <p class="marker-profile-row"><strong>Description:</strong> {m.description || '—'}</p>
                            <p class="marker-profile-row"><strong>Unit:</strong> {m.unit || '—'}</p>
                            <p class="marker-profile-row"><strong>Volatility class:</strong> {m.volatility_class || '—'}</p>
                            <p class="marker-profile-row"><strong>Created:</strong> {formatDate(m.created_at)}</p>
                    </div>
                </div>
                {/if}
                {#if editingMarker === m.marker_id}
                <div class="card-edit-container" role="button" tabindex='0' onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                    <p><strong>Edit Marker</strong></p>

                    <form class="inline-form" id="marker-edit-form">
                        <div class="form-element" id="edit-marker-name-container">
                            <label for="edit-marker-name">Marker name:</label>
                            <input id="edit-marker-name" type="text" bind:value={edit_marker_name}>
                        </div>

                        <div class="form-element" id="edit-description-container">
                            <label for="edit-description">Description:</label>
                            <input id="edit-description" type="text" bind:value={edit_description}>
                        </div>

                        <div class="form-element" id="edit-unit-container">
                            <label for="edit-unit">Unit:</label>
                            <input id="edit-unit" type="text" bind:value={edit_unit}>
                        </div>

                        <div class="form-element" id="edit-volatility-class-container">
                            <label for="edit-volatility-class">Volatility class:</label>
                            <select id="edit-volatility-class" bind:value={edit_volatility_class}>
                                <option value={null}>--</option>
                                <option value="low">Low</option>
                                <option value="medium">Medium</option>
                                <option value="high">High</option>
                            </select>
                        </div>

                        <div class="form-element" id="edit-btn-container">
                            <button class="edit-btn" onclick={handleEditMarker}>{@html EditIcon}</button>
                        </div>
                    </form>
                </div>
                {/if}
            </div>
        {/each}
    {/if}

    {#if mode === "add"}
        <h4>Add new marker</h4>
        <form class="new-marker-form">

            <div class="form-element" id="add-marker-name-container">
                <label for="add-marker-name">Marker name:</label>
                <input type="text" id="add-marker-name" bind:value={marker_name}>
            </div>

            <div class="form-element" id="add-description-container">
                <label for="add-description">Description:</label>
                <input type="text" id="add-description" bind:value={description}>
            </div>

            <div class="form-element" id="add-unit-container">
                <label for="add-unit">Unit:</label>
                <input type="text" id="add-unit" bind:value={unit}>
            </div>

            <div class="form-element" id="add-volatility-class-container">
                <label for="add-volatility-class">Volatility class:</label>
                <select id="add-volatility-class" bind:value={volatility_class}>
                    <option value="">-- select --</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                </select>
            </div>

            <div class="form-element" id="add-new-marker-btn-container">
                <button type="button" class="add-btn" onclick={handleAddNewMarker}>{@html AddIcon}</button>
            </div>
        </form>
    {/if}
    </div>
</div>

</main>

<style>
    .card-expanded-container {
        display: flex;
    }

    .marker-profile-container {
        background: rgb(206, 233, 241);
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    .marker-profile-row {
        margin: 0;
        display: flex;
    }

    #marker-profile-row-header {
        justify-content: center;
    }

    #marker-edit-form {
        display: grid;
        grid-template-columns: auto auto auto;
        grid-template-rows: auto auto auto auto;
    }

    #edit-btn-container {
        justify-content: center;
        align-items: center;
    }

    #add-new-marker-btn-container {
        justify-content: flex-end;
    }
</style>
