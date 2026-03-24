<script>

import { onMount } from "svelte";
import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from "../../../lib/stores.svelte";

let selectedSubject = $state("");

onMount(() => {
    ensureSubjectsLoaded();
});

function handleSubmit(e) {
    e.preventDefault();
    if (!selectedSubject) return;
    appState.sandboxSubjectId = selectedSubject;
    ensureMeasurementsLoaded(selectedSubject);
}

function handleClear(e) {
    e.preventDefault();
    if (selectedSubject != "") {
        appState.sandboxSubjectId = null;
    } else {
        return;
    }
}

</script>

<main>
    <form onsubmit={handleSubmit}>
        <label for="input-subj">Subject:</label>
        <select name="input-subj" id="input-subj" bind:value={selectedSubject}>
            {#each appState.subjects as s}
                <option value={s.subject_id}>{s.first_name} {s.last_name}</option>
            {/each}
        </select>

        <p>You've chosen: {selectedSubject}</p>

        <button type="submit">Submit</button>
        <button type="button" onclick={handleClear} >Clear</button>
    </form>


    
</main>