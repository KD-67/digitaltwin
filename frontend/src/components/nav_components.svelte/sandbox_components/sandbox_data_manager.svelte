<script>
    import { onMount } from 'svelte';
    import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from '../../../lib/stores.svelte';

    onMount(() => {
        ensureSubjectsLoaded();
    });

    let { onSelectionChange } = $props();

    let selectedSubject = $state("");
    let timeFrom = $state('');
    let timeTo   = $state('');
    let checkedKeys = $state(new Set());

    const key = (m) => `${m.marker_id}__${m.measured_at}`;

    let allMeasurements = $derived(
        appState.measurementsBySubject[appState.sandboxSubjectId] ?? []
    );

    let filteredMeasurements = $derived(
        allMeasurements.filter(m => {
            const t = new Date(m.measured_at);
            if (timeFrom && t < new Date(timeFrom)) return false;
            if (timeTo   && t > new Date(timeTo))   return false;
            return true;
        })
    );

    let grouped = $derived(
        filteredMeasurements.reduce((acc, m) => {
            (acc[m.marker_id] ??= []).push(m);
            return acc;
        }, {})
    );

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

    function toggleRow(m) {
        const k = key(m);
        const next = new Set(checkedKeys);
        if (next.has(k)) next.delete(k);
        else next.add(k);
        checkedKeys = next;
        onSelectionChange(filteredMeasurements.filter(x => checkedKeys.has(key(x))));
    }

    function toggleMarker(markerId) {
        const rows = grouped[markerId] ?? [];
        const allChecked = rows.every(m => checkedKeys.has(key(m)));
        const next = new Set(checkedKeys);
        if (allChecked) {
            rows.forEach(m => next.delete(key(m)));
        } else {
            rows.forEach(m => next.add(key(m)));
        }
        checkedKeys = next;
        onSelectionChange(filteredMeasurements.filter(x => checkedKeys.has(key(x))));
    }

    function markerAllChecked(markerId) {
        const rows = grouped[markerId] ?? [];
        return rows.length > 0 && rows.every(m => checkedKeys.has(key(m)));
    }
</script>

<main>
<form id="filter-form" onsubmit={handleSubmit}>
    <div id="subject-filter">
        <label for="select-subject">Subject:</label>
        <select id="select-subject" bind:value={selectedSubject}>
            {#each appState.subjects as s}
                <option value={s.subject_id}>{s.first_name} {s.last_name}</option>
            {/each}
        </select>
    </div>

    <div id="timeframe-filter">
        <label>From: <input type="datetime-local" bind:value={timeFrom} /></label>
        <label>To: <input type="datetime-local" bind:value={timeTo} /></label>
    </div>

    <button type="submit">Go!</button>
    <button type="button" onclick={handleClear}>Clear</button>
</form>

<div id="grouped-measurements">
    {#each Object.entries(grouped) as [markerId, rows]}
        <div class="marker-group">
            <div class="marker-header">
                <input
                    type="checkbox"
                    checked={markerAllChecked(markerId)}
                    onchange={() => toggleMarker(markerId)}
                />
                <strong>
                    {appState.markers.find(mk => mk.marker_id === Number(markerId))?.marker_name ?? `Marker ${markerId}`}
                </strong>
            </div>
            <table>
                <tbody>
                    {#each rows as m}
                        <tr>
                            <td>
                                <input
                                    type="checkbox"
                                    checked={checkedKeys.has(key(m))}
                                    onchange={() => toggleRow(m)}
                                />
                            </td>
                            <td>{m.measured_at}</td>
                            <td>{m.value}</td>
                        </tr>
                    {/each}
                </tbody>
            </table>
        </div>
    {:else}
        <p>Il n'y a pas de mesures</p>
    {/each}
</div>
</main>

<style>
main {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow: hidden;
}

#filter-form {
    display: block;
}

#timeframe-filter {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 4px;
    border-bottom: 1px solid #ccc;
}

#grouped-measurements {
    flex: 1;
    overflow-y: auto;
}

.marker-group {
    margin: 4px;
    border: 1px solid #ccc;
    padding: 4px;
}

.marker-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 4px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85em;
}

td {
    padding: 2px 4px;
}
</style>
