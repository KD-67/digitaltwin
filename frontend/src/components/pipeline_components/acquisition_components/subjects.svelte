<script>
    import ViewIcon from "../../../assets/view_icon.svg?raw";
    import AddIcon from "../../../assets/add_icon.svg?raw";
    import EditIcon from "../../../assets/edit_icon.svg?raw";
    import DeleteIcon from "../../../assets/delete_icon.svg?raw";
    import GenericUserIcon from "../../../assets/generic_user_icon.svg?raw";
    import CancelIcon from "../../../assets/cancel_icon.svg?raw";

    let statusMessage = $state("");
    let mode = $state("view");
    let expandedSubject = $state("")
    let editingSubject = $state("")

    // Add new subject form
    let subject_id = $state("");
    let last_name = $state("");
    let first_name = $state("");
    let sex = $state("");
    let dob = $state("");
    let email = $state("");
    let phone = $state("");
    let notes = $state("");

    // Edit existing subject form
    let edit_last_name = $state(null);
    let edit_first_name = $state(null);
    let edit_sex = $state(null);
    let edit_dob = $state(null);
    let edit_email = $state(null);
    let edit_phone = $state(null);
    let edit_notes = $state(null);

    import { onMount } from "svelte";
    import { formatDate, createSubject, updateSubject, deleteSubject } from "../../../lib/services.js";
    import { appState, ensureSubjectsLoaded } from "../../../lib/stores.svelte.js";

    // INTERFACE FUNCTIONALITY:
    function collapseCard() {
        expandedSubject = null;
        editingSubject = null;
    }

    // BACKEND FUNCTIONALITY:
    //This is fired when the add new subject button is clicked
    function handleAddNewSubject () {
        if (!window.confirm(`Are you sure you want to create this new subject? Go ahead and double check all fields one more time just to be sure :)`)) return;
        createSubject({first_name, last_name, sex, dob, email, phone, notes});
        statusMessage = "test";
    }

    //This is fired when the delete existing subject button is clicked
    function handleDeleteSubject (subject_id) {
        if (!window.confirm(`Are you sure you want to delete subject ${subject_id}? This cannot be undone.`)) return;
        deleteSubject(subject_id)
        statusMessage = "subject deleted";
    }

    //This is fired when the submit edit existing subject button is clicked
    async function handleEditSubject() {
        if (!window.confirm(`Are you sure you want to make these edits? They cannot be undone.`)) return;
        const raw = { first_name: edit_first_name, last_name: edit_last_name, sex: edit_sex, dob: edit_dob, email: edit_email, phone: edit_phone, notes: edit_notes };
        const updates = Object.fromEntries(Object.entries(raw).filter(([, v]) => v !== null && v !== ""));
        try {
            await updateSubject(editingSubject, updates);
            statusMessage = "Subject updated";
        } catch (e) {
            statusMessage = `Update failed: ${e.message}`;
        } finally {
            collapseCard();
        }
    }

    onMount(() => {
        ensureSubjectsLoaded();
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
    <h3 id="viewbox-header">Subject Management</h3>

    {#if mode === "view"}
        <h4>View existing subjects</h4>
        {#if appState.subjects.length === 0}
            <p>No subjects found</p>       
        {/if}
        {#each appState.subjects as s}
            <div class="card" role="button" tabindex='0' onkeydown={(e) => e.stopPropagation()} 
                onclick={() => {
                    if (expandedSubject === s.subject_id) {
                        collapseCard();
                        statusMessage = "card collapsed";
                    } else {
                        collapseCard();
                        expandedSubject = s.subject_id;
                        statusMessage = "card expanded"
                    }
                }}>
                <div class="card-header-container">
                    <div class="card-icon-container">
                        <div class="card-icon">{@html GenericUserIcon}</div>
                    </div>
                    <div class="card-title-container">{s.first_name} {s.last_name}</div>
                </div>
                <div class="card-actions-container">
                    <button class="edit-btn" onclick={(e) => {
                        e.stopPropagation();
                        if (editingSubject === s.subject_id) {
                            collapseCard();
                            statusMessage = "card collapsed";
                        } else {
                            expandedSubject = s.subject_id;
                            editingSubject = s.subject_id;
                            statusMessage = "subject profile edited"
                        }
                    }}> {@html EditIcon}</button>

                    <button class="delete-btn" onclick={(e) => { e.stopPropagation(); handleDeleteSubject(s.subject_id); }}>{@html DeleteIcon}</button>

                </div>
                <div class="card-description-container">Date of Birth: {formatDate(s.dob).slice(0,-12)}, Sex: {s.sex}</div>
                {#if expandedSubject === s.subject_id}
                <div class="card-expanded-container">
                    <div class="subject-profile-container">
                            <p class="subject-profile-row" id="subject-profile-row-header"><strong>Profile</strong></p>
                            <p class="subject-profile-row"><strong>ID:</strong> {s.subject_id}</p>
                            <p class="subject-profile-row"><strong>Email:</strong> {s.email || '—'}</p>
                            <p class="subject-profile-row"><strong>Phone:</strong> {s.phone || '—'}</p>
                            <p class="subject-profile-row"><strong>Notes:</strong> {s.notes || '—'}</p>
                            <p class="subject-profile-row"><strong>Created:</strong> {formatDate(s.created_at)}</p>
                    </div>
                    <div class="subject-datasets-container">
                            <p class="subject-datasets-row" id="subject-datasets-row-header"><strong>Available Data</strong></p>
                            <p class="subject-datasets-row"><strong>Marker1:</strong> 56</p>
                            <p class="subject-datasets-row"><strong>Marker2:</strong> 12</p>
                            <p class="subject-datasets-row"><strong>Marker3:</strong> 94</p>
                    </div>
                </div>    
                {/if}
                {#if editingSubject === s.subject_id}
                <div class="card-edit-container" role="button" tabindex='0' onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                    <p><strong>Edit Subject Profile</strong></p>
                    
                    <form class="inline-form" id="subject-edit-form">                    
                        <div class="form-element" id="edit-last-name-container">
                            <label for="edit-last-name">Last name:</label>
                            <input id="edit-last-name" type="text" bind:value={edit_last_name}>
                        </div>
                        
                        <div class="form-element" id="edit-first-name-container">
                            <label for="edit-first-name">First name:</label>
                            <input id="edit-first-name" type="text" bind:value={edit_first_name}>
                        </div>

                        <div class="form-element" id="edit-sex-container">
                            <label for="edit-sex">Sex:</label>
                            <select id="edit-sex" bind:value={edit_sex}>
                                <option value={null}>--</option>
                                <option value="F">F</option>
                                <option value="M">M</option>
                                <option value="Undeclared">Undeclared</option>
                            </select>
                        </div>
                        
                        <div class="form-element" id="edit-dob-container">
                            <label for="edit-dob">Date of birth:</label>
                            <input type="date" bind:value={edit_dob}>
                        </div>
                        
                        <div class="form-element" id="edit-email-container">
                            <label for="edit-email">Email:</label>
                            <input id="edit-email" type="text" bind:value={edit_email}>
                        </div>
                        
                        <div class="form-element" id="edit-phone-container">
                            <label for="edit-phone">Phone:</label>
                            <input id="edit-phone" type="text" bind:value={edit_phone}>
                        </div>
                        
                        <div class="form-element" id="edit-notes-container">
                            <label for="edit-notes">Notes:</label>
                            <textarea id="edit-notes" rows=5 bind:value={edit_notes}></textarea>
                        </div>
                        
                        <div class="form-element" id="edit-btn-container">
                            <button class="edit-btn" onclick={handleEditSubject}>{@html EditIcon}</button>
                        </div>
                    </form>
                </div>
                {/if}
            </div>
        {/each}
    {/if}

    {#if mode === "add"}
        <h4>Add new subject</h4>
        <form class="new-subject-form">

            <div class="form-element" id="add-last-name-container">
                <label for="add-last-name">Last name:</label>
                <input type="text" class="add-last-name" bind:value={last_name}>
            </div>
            
            <div class="form-element" id="add-first-name-container">
                <label for="add-first-name">First name:</label>
                <input type="text" id="add-first-name" bind:value={first_name}>
            </div>
            
            <div class="form-element" id="add-sex-container">
                <label for="add-sex">Sex:</label>
                <select name="add-sex" id="add-sex" bind:value={sex}>
                    <option value="">-- select --</option>
                    <option value="F">Female</option>
                    <option value="M">Male</option>
                    <option value="Undeclared">Undeclared</option>
                </select>
            </div>
            
            <div class="form-element" id="add-dob-container">
                <label for="add-dob">Date of birth:</label>
                <input type="date" id="add-dob" bind:value={dob}>
            </div>
            
            <div class="form-element" id="add-email-container">
                <label for="add-email">Email address:</label>
                <input type="text" id="add-email" bind:value={email}>
            </div>
            
            <div class="form-element" id="add-phone-container">
                <label for="add-phone">Phone number:</label>
                <input type="text" id="add-phone" bind:value={phone}>
            </div>

            <div class="form-element" id="add-notes-container">
                <label for="add-notes" id="add-notes-container">Notes:</label>
                <textarea id="add-notes" bind:value={notes}></textarea>
            </div>            

            <div class="form-element" id="add-new-subject-btn-container">
                <button type="button" class="add-btn" onclick={handleAddNewSubject}>{@html AddIcon}</button>
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
    
    .subject-profile-container {
        background: rgb(206, 233, 241);
        display: flex;
        flex-direction: column; 
        width: 40%;       
    }

    .subject-datasets-container {
        background: rgb(206, 241, 208);
        width: 60%;
    }

    .subject-profile-row, .subject-datasets-row {
        margin: 0;
        display: flex;
    }

    #subject-profile-row-header, #subject-datasets-row-header {
        justify-content: center;
    }

    #subject-edit-form {
        display: grid;
        grid-template-columns: auto auto auto;
        grid-template-rows: auto auto auto auto;
    }

    #add-notes-container {
        grid-area: 3 / 1 / 4 / 3;
    }

    #add-notes {
        width: 90%;
    }

    #add-new-subject-btn-container {
        grid-area: 3 / 3 / 4 / 4;
        justify-content: flex-end;
    }

    #edit-notes-container {
        grid-area: 3 / 1 / 4 / 3;
    }

    #edit-notes {
        width: 90%;
    }

    #edit-btn-container {
        justify-content: center;
        align-items: center;
    }

</style>
