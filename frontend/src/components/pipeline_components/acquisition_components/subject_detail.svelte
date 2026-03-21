<script>
    import { onMount } from 'svelte';
    import AddIcon    from '../../../assets/add_icon.svg?raw';
    import EditIcon   from '../../../assets/edit_icon.svg?raw';
    import DeleteIcon from '../../../assets/delete_icon.svg?raw';
    import CancelIcon from '../../../assets/cancel_icon.svg?raw';
    import GenericUserIcon from '../../../assets/generic_user_icon.svg?raw';
    import LevelsIcon from '../../../assets/levels_icon.svg?raw';

    import { appState, ensureMarkersLoaded, ensureMeasurementsLoaded } from '../../../lib/stores.svelte.js';
    import { formatDate, updateSubject, addMeasurement, deleteMeasurement } from '../../../lib/services.js';

    // ── Navigation ────────────────────────────────────────────────────────────
    function goBack() {
        window.location.hash = 'subjects';
    }

    // ── Reactive derivations ──────────────────────────────────────────────────
    let subject      = $derived(appState.selectedSubject);
    let allMeasurements = $derived(
        subject ? (appState.measurementsBySubject[subject.subject_id] ?? []) : []
    );

    // Unique markers with data for this subject, in first-seen order
    let trackedMarkers = $derived.by(() => {
        const seenIds = new Set();
        const result = [];
        for (const m of allMeasurements) {
            if (!seenIds.has(m.marker_id)) {
                seenIds.add(m.marker_id);
                const meta = appState.markers.find(mk => mk.marker_id === m.marker_id);
                if (meta) result.push(meta);
            }
        }
        return result;
    });

    // Sparse markers not yet tracked by this subject (for "Track new marker" dropdown)
    let untrackedMarkers = $derived.by(() => {
        const trackedIds = new Set(allMeasurements.map(m => m.marker_id));
        return appState.markers.filter(
            m => !trackedIds.has(m.marker_id) && m.storage_type === 'sparse'
        );
    });

    // Sorted readings (newest first) for a given marker
    function readingsForMarker(marker_id) {
        return allMeasurements
            .filter(m => m.marker_id === marker_id)
            .sort((a, b) => b.measured_at.localeCompare(a.measured_at));
    }

    // ── UI state ──────────────────────────────────────────────────────────────
    let statusMessage       = $state('');
    let expandedMarkerId    = $state(null);   // accordion section open
    let showAddFormFor      = $state(null);   // marker_id with inline add form open
    let showAllFor          = $state({});     // { marker_id: true } for sections showing all readings
    let trackNewMarkerOpen  = $state(false);
    let editProfileOpen     = $state(false);

    // "Track new marker" form
    let newMarker_markerId  = $state('');
    let newMarker_value     = $state('');
    let newMarker_measuredAt = $state('');
    let newMarker_quality   = $state('good');
    let newMarker_notes     = $state('');

    // Inline add reading form (shared; reset when a new section's + is clicked)
    let addReading_value     = $state('');
    let addReading_measuredAt = $state('');
    let addReading_quality   = $state('good');
    let addReading_notes     = $state('');

    // Edit profile form
    let edit_first_name = $state(null);
    let edit_last_name  = $state(null);
    let edit_sex        = $state(null);
    let edit_dob        = $state(null);
    let edit_email      = $state(null);
    let edit_phone      = $state(null);
    let edit_notes      = $state(null);

    // ── Helpers ───────────────────────────────────────────────────────────────
    // Converts datetime-local value ("YYYY-MM-DDTHH:mm") to ISO-8601 UTC string
    function toIso(datetimeLocal) {
        return datetimeLocal ? datetimeLocal + ':00Z' : '';
    }

    function clearTrackNewForm() {
        newMarker_markerId  = '';
        newMarker_value     = '';
        newMarker_measuredAt = '';
        newMarker_quality   = 'good';
        newMarker_notes     = '';
    }

    function clearAddReadingForm() {
        addReading_value     = '';
        addReading_measuredAt = '';
        addReading_quality   = 'good';
        addReading_notes     = '';
    }

    // ── Accordion controls ────────────────────────────────────────────────────
    function toggleAccordion(marker_id) {
        if (expandedMarkerId === marker_id) {
            expandedMarkerId = null;
            showAddFormFor = null;
        } else {
            expandedMarkerId = marker_id;
        }
    }

    function openAddForm(marker_id) {
        showAddFormFor = marker_id;
        clearAddReadingForm();
    }

    function closeAddForm() {
        showAddFormFor = null;
    }

    function toggleShowAll(marker_id) {
        const next = { ...showAllFor };
        if (next[marker_id]) delete next[marker_id];
        else next[marker_id] = true;
        showAllFor = next;
    }

    // ── Handlers ──────────────────────────────────────────────────────────────
    async function handleTrackNewMarker() {
        if (!newMarker_markerId)  { statusMessage = 'Please select a marker.'; return; }
        if (!newMarker_value)     { statusMessage = 'Please enter a value.'; return; }
        if (!newMarker_measuredAt){ statusMessage = 'Please enter a date and time.'; return; }
        if (!window.confirm('Add this measurement?')) return;
        try {
            await addMeasurement({
                subject_id:  subject.subject_id,
                marker_id:   newMarker_markerId,
                measured_at: toIso(newMarker_measuredAt),
                value:       newMarker_value,
                quality:     newMarker_quality,
                notes:       newMarker_notes,
            });
            statusMessage = 'Measurement added.';
            trackNewMarkerOpen = false;
            clearTrackNewForm();
            // Auto-expand the newly tracked marker section
            expandedMarkerId = newMarker_markerId;
        } catch (e) {
            statusMessage = `Error: ${e.message}`;
        }
    }

    async function handleAddReading(marker_id) {
        if (!addReading_value)     { statusMessage = 'Please enter a value.'; return; }
        if (!addReading_measuredAt){ statusMessage = 'Please enter a date and time.'; return; }
        if (!window.confirm('Add this reading?')) return;
        try {
            await addMeasurement({
                subject_id:  subject.subject_id,
                marker_id,
                measured_at: toIso(addReading_measuredAt),
                value:       addReading_value,
                quality:     addReading_quality,
                notes:       addReading_notes,
            });
            statusMessage = 'Reading added.';
            showAddFormFor = null;
        } catch (e) {
            statusMessage = `Error: ${e.message}`;
        }
    }

    async function handleDeleteReading(marker_id, measured_at) {
        if (!window.confirm('Delete this reading? This cannot be undone.')) return;
        try {
            await deleteMeasurement(subject.subject_id, marker_id, measured_at);
            statusMessage = 'Reading deleted.';
        } catch (e) {
            statusMessage = `Error: ${e.message}`;
        }
    }

    async function handleEditProfile() {
        if (!window.confirm('Save these profile changes?')) return;
        const raw = {
            first_name: edit_first_name, last_name: edit_last_name, sex: edit_sex,
            dob: edit_dob, email: edit_email, phone: edit_phone, notes: edit_notes,
        };
        const updates = Object.fromEntries(
            Object.entries(raw).filter(([, v]) => v !== null && v !== '')
        );
        try {
            await updateSubject(subject.subject_id, updates);
            // Keep selectedSubject in sync so the profile card updates immediately
            Object.assign(appState.selectedSubject, updates);
            statusMessage = 'Profile updated.';
            editProfileOpen = false;
            edit_first_name = edit_last_name = edit_sex = edit_dob = edit_email = edit_phone = edit_notes = null;
        } catch (e) {
            statusMessage = `Error: ${e.message}`;
        }
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────
    onMount(async () => {
        await ensureMarkersLoaded();
        if (subject) {
            await ensureMeasurementsLoaded(subject.subject_id);
        }
    });
</script>

<main>
<div class="main-container">

    <!-- Top bar: back button + status message -->
    <div id="top-bar">
        <button class="back-btn" onclick={goBack}>← Back to Subjects</button>
        {#if statusMessage}
            <p id="status_msg">{statusMessage}</p>
        {/if}
    </div>

    {#if !subject}
        <div id="viewbox">
            <p>No subject selected. <button class="back-btn" onclick={goBack}>← Go back</button></p>
        </div>
    {:else}
    <div id="viewbox">

        <!-- ── Profile card ─────────────────────────────────────────────── -->
        <div class="profile-card">
            <div class="profile-card-top">
                <div class="profile-identity">
                    <div class="card-icon-container">
                        <div class="card-icon">{@html GenericUserIcon}</div>
                    </div>
                    <div class="profile-name">{subject.first_name} {subject.last_name}</div>
                    <div class="profile-subid">{subject.subject_id}</div>
                </div>
                <button class="edit-btn" title="Edit profile" onclick={() => { editProfileOpen = !editProfileOpen; }}>{@html EditIcon}</button>
            </div>

            <div class="profile-details">
                <span><strong>Sex:</strong> {subject.sex || '—'}</span>
                <span><strong>DOB:</strong> {subject.dob || '—'}</span>
                <span><strong>Email:</strong> {subject.email || '—'}</span>
                <span><strong>Phone:</strong> {subject.phone || '—'}</span>
                {#if subject.notes}<span><strong>Notes:</strong> {subject.notes}</span>{/if}
            </div>

            {#if editProfileOpen}
            <div class="profile-edit-section" role="button" tabindex='0'
                onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                <p><strong>Edit Profile</strong></p>
                <form class="inline-form profile-edit-grid">
                    <div class="form-element">
                        <label>First name:</label>
                        <input type="text" bind:value={edit_first_name} placeholder={subject.first_name ?? ''}>
                    </div>
                    <div class="form-element">
                        <label>Last name:</label>
                        <input type="text" bind:value={edit_last_name} placeholder={subject.last_name ?? ''}>
                    </div>
                    <div class="form-element">
                        <label>Sex:</label>
                        <select bind:value={edit_sex}>
                            <option value={null}>— no change —</option>
                            <option value="F">F</option>
                            <option value="M">M</option>
                            <option value="Undeclared">Undeclared</option>
                        </select>
                    </div>
                    <div class="form-element">
                        <label>DOB:</label>
                        <input type="date" bind:value={edit_dob}>
                    </div>
                    <div class="form-element">
                        <label>Email:</label>
                        <input type="text" bind:value={edit_email} placeholder={subject.email ?? ''}>
                    </div>
                    <div class="form-element">
                        <label>Phone:</label>
                        <input type="text" bind:value={edit_phone} placeholder={subject.phone ?? ''}>
                    </div>
                    <div class="form-element profile-notes-element">
                        <label>Notes:</label>
                        <textarea bind:value={edit_notes} placeholder={subject.notes ?? ''} rows=3></textarea>
                    </div>
                    <div class="form-element profile-edit-actions">
                        <button type="button" class="edit-btn" onclick={handleEditProfile}>{@html EditIcon}</button>
                        <button type="button" class="cancel-btn" onclick={() => { editProfileOpen = false; }}>{@html CancelIcon}</button>
                    </div>
                </form>
            </div>
            {/if}
        </div>

        <!-- ── Track New Marker section ─────────────────────────────────── -->
        <div class="section-control-bar">
            <button class="add-btn track-new-btn" onclick={() => { trackNewMarkerOpen = !trackNewMarkerOpen; }}>
                {trackNewMarkerOpen ? 'Cancel' : '+ Track New Marker'}
            </button>
        </div>

        {#if trackNewMarkerOpen}
        <div class="track-new-form-container">
            <form class="inline-form track-new-grid">
                <div class="form-element">
                    <label>Marker:</label>
                    <select bind:value={newMarker_markerId}>
                        <option value="">— choose marker —</option>
                        {#each untrackedMarkers as m}
                            <option value={m.marker_id}>{m.marker_name} ({m.unit})</option>
                        {/each}
                    </select>
                </div>
                <div class="form-element">
                    <label>Value:</label>
                    <input type="text" bind:value={newMarker_value} placeholder="e.g. 72.5">
                </div>
                <div class="form-element">
                    <label>Date &amp; Time (UTC):</label>
                    <input type="datetime-local" bind:value={newMarker_measuredAt}>
                </div>
                <div class="form-element">
                    <label>Quality:</label>
                    <select bind:value={newMarker_quality}>
                        <option value="good">Good</option>
                        <option value="suspect">Suspect</option>
                        <option value="bad">Bad</option>
                    </select>
                </div>
                <div class="form-element">
                    <label>Notes:</label>
                    <input type="text" bind:value={newMarker_notes}>
                </div>
                <div class="form-element track-new-actions">
                    <button type="button" class="add-btn" onclick={handleTrackNewMarker}>{@html AddIcon}</button>
                    <button type="button" class="cancel-btn" onclick={() => { trackNewMarkerOpen = false; clearTrackNewForm(); }}>{@html CancelIcon}</button>
                </div>
            </form>
        </div>
        {/if}

        <!-- ── Tracked markers accordion ────────────────────────────────── -->
        <div class="tracked-markers-section">
            <h4 class="section-title">Tracked Markers</h4>

            {#if trackedMarkers.length === 0}
                <p class="empty-state">No measurements recorded yet. Use "+ Track New Marker" above to add the first one.</p>
            {/if}

            {#each trackedMarkers as marker}
                {@const readings    = readingsForMarker(marker.marker_id)}
                {@const showAll     = !!showAllFor[marker.marker_id]}
                {@const displayed   = showAll ? readings : readings.slice(0, 5)}

                <div class="marker-accordion">

                    <!-- Accordion header -->
                    <div class="accordion-header" role="button" tabindex="0"
                        onclick={() => toggleAccordion(marker.marker_id)}
                        onkeydown={(e) => e.key === 'Enter' && toggleAccordion(marker.marker_id)}>

                        <div class="accordion-header-left">
                            <span class="accordion-marker-icon">{@html LevelsIcon}</span>
                            <span class="accordion-title">{marker.marker_name}</span>
                            <span class="accordion-meta">({marker.unit}) &mdash; {readings.length} reading{readings.length !== 1 ? 's' : ''}</span>
                        </div>

                        <div class="accordion-header-right">
                            <button class="add-btn accordion-add-btn" title="Add reading" onclick={(e) => {
                                e.stopPropagation();
                                expandedMarkerId = marker.marker_id;
                                if (showAddFormFor === marker.marker_id) {
                                    showAddFormFor = null;
                                } else {
                                    openAddForm(marker.marker_id);
                                }
                            }}>{@html AddIcon}</button>
                            <span class="accordion-chevron">{expandedMarkerId === marker.marker_id ? '▲' : '▼'}</span>
                        </div>
                    </div>

                    {#if expandedMarkerId === marker.marker_id}
                    <div class="accordion-body">

                        <!-- Inline add reading form -->
                        {#if showAddFormFor === marker.marker_id}
                        <div class="inline-add-form-container" role="button" tabindex='0'
                            onclick={(e) => e.stopPropagation()} onkeydown={(e) => e.stopPropagation()}>
                            <form class="inline-form reading-form-grid">
                                <div class="form-element">
                                    <label>Value:</label>
                                    <input type="text" bind:value={addReading_value} placeholder="e.g. 72.5">
                                </div>
                                <div class="form-element">
                                    <label>Date &amp; Time (UTC):</label>
                                    <input type="datetime-local" bind:value={addReading_measuredAt}>
                                </div>
                                <div class="form-element">
                                    <label>Quality:</label>
                                    <select bind:value={addReading_quality}>
                                        <option value="good">Good</option>
                                        <option value="suspect">Suspect</option>
                                        <option value="bad">Bad</option>
                                    </select>
                                </div>
                                <div class="form-element">
                                    <label>Notes:</label>
                                    <input type="text" bind:value={addReading_notes}>
                                </div>
                                <div class="form-element reading-form-actions">
                                    <button type="button" class="add-btn" onclick={() => handleAddReading(marker.marker_id)}>{@html AddIcon}</button>
                                    <button type="button" class="cancel-btn" onclick={closeAddForm}>{@html CancelIcon}</button>
                                </div>
                            </form>
                        </div>
                        {/if}

                        <!-- Readings table -->
                        {#if readings.length === 0}
                            <p class="empty-readings">No readings yet. Click + to add the first one.</p>
                        {:else}
                        <table class="readings-table">
                            <thead>
                                <tr>
                                    <th>Date / Time (UTC)</th>
                                    <th>Value ({marker.unit})</th>
                                    <th>Quality</th>
                                    <th>Notes</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each displayed as reading}
                                <tr>
                                    <td class="reading-date">{reading.measured_at.slice(0, 16).replace('T', ' ')}</td>
                                    <td class="reading-value">{reading.value}</td>
                                    <td class="reading-quality quality-{reading.quality}">{reading.quality}</td>
                                    <td class="reading-notes">{reading.notes || '—'}</td>
                                    <td class="reading-action">
                                        <button class="delete-btn accordion-delete-btn"
                                            onclick={() => handleDeleteReading(marker.marker_id, reading.measured_at)}>
                                            {@html DeleteIcon}
                                        </button>
                                    </td>
                                </tr>
                                {/each}
                            </tbody>
                        </table>

                        {#if readings.length > 5}
                        <button class="show-all-btn" onclick={() => toggleShowAll(marker.marker_id)}>
                            {showAll ? '▲ Show fewer' : `▼ Show all ${readings.length} readings`}
                        </button>
                        {/if}

                        {/if}
                    </div>
                    {/if}

                </div>
            {/each}
        </div>

    </div>
    {/if}

</div>
</main>

<style>
    /* ── Top bar ─────────────────────────────────────────────────────────────── */
    #top-bar {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 0 8px;
    }

    .back-btn {
        width: auto;
        padding: 0.25rem 1rem;
        background-color: var(--view-btn-color);
        color: var(--btn-icon-color);
        font-size: 13px;
    }

    .cancel-btn {
        background-color: var(--delete-btn-color);
    }

    #status_msg {
        color: var(--accent);
        font-size: 14px;
    }

    /* ── Profile card ────────────────────────────────────────────────────────── */
    .profile-card {
        width: 80%;
        border: 2px solid black;
        border-radius: 0.5rem;
        background-color: var(--card-bg);
        box-shadow: 5px 5px 0px var(--shadow);
        padding: 12px 16px;
        margin: 8px 0;
        text-align: left;
    }

    .profile-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .profile-identity {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .profile-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-h);
    }

    .profile-subid {
        font-size: 0.85rem;
        color: var(--text);
    }

    .profile-details {
        display: flex;
        flex-wrap: wrap;
        gap: 12px 24px;
        margin-top: 8px;
        font-size: 0.95rem;
    }

    .profile-edit-section {
        margin-top: 10px;
        border-top: 1px solid var(--border);
        padding-top: 8px;
    }

    .profile-edit-grid {
        grid-template-columns: 1fr 1fr 1fr;
    }

    .profile-notes-element {
        grid-column: 1 / 3;
    }

    .profile-edit-actions {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }

    /* ── Track new marker ────────────────────────────────────────────────────── */
    .section-control-bar {
        width: 80%;
        display: flex;
        justify-content: flex-start;
        margin: 12px 0 4px;
    }

    .track-new-btn {
        width: auto;
        padding: 0.25rem 1rem;
        font-size: 13px;
    }

    .track-new-form-container {
        width: 80%;
        margin-bottom: 8px;
    }

    .track-new-grid {
        grid-template-columns: 1fr 1fr 1fr;
    }

    .track-new-actions {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }

    /* ── Tracked markers accordion ───────────────────────────────────────────── */
    .tracked-markers-section {
        width: 80%;
        margin-top: 8px;
    }

    .section-title {
        text-align: left;
        margin-bottom: 8px;
        color: var(--text-h);
        border-bottom: 1px solid var(--border);
        padding-bottom: 4px;
    }

    .empty-state {
        color: var(--text);
        font-style: italic;
        text-align: left;
        padding: 12px 0;
    }

    .marker-accordion {
        border: 1px solid var(--border);
        border-radius: 0.4rem;
        margin-bottom: 6px;
        background-color: var(--card-bg);
        box-shadow: 3px 3px 0px var(--shadow);
        overflow: hidden;
    }

    .marker-accordion:hover {
        transform: scale(103%);
    }

    .accordion-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        cursor: pointer;
        user-select: none;
        background-color: var(--card-bg);
    }

    .accordion-header-left {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .accordion-marker-icon {
        width: 20px;
        height: 20px;
        display: inline-flex;
        color: var(--accent);
    }

    .accordion-title {
        font-weight: 600;
        color: var(--text-h);
    }

    .accordion-meta {
        font-size: 0.85rem;
        color: var(--text);
    }

    .accordion-header-right {
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .accordion-chevron {
        font-size: 0.75rem;
        color: var(--text);
    }

    .accordion-add-btn, .accordion-delete-btn {
        width: 35px;
        height: 28px;
        margin: 0;
        padding: 0.1rem 0.4rem;
    }

    .accordion-body {
        border-top: 1px solid var(--border);
        padding: 10px 14px;
    }

    /* ── Inline add form ─────────────────────────────────────────────────────── */
    .inline-add-form-container {
        margin-bottom: 10px;
    }

    .reading-form-grid {
        grid-template-columns: 1fr 1fr 1fr;
    }

    .reading-form-actions {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }

    /* ── Readings table ──────────────────────────────────────────────────────── */
    .readings-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
        text-align: left;
        margin-top: 4px;
    }

    .readings-table th {
        border-bottom: 2px solid var(--border);
        padding: 6px 8px;
        color: var(--text);
        font-weight: 600;
        background-color: var(--code-bg);
    }

    .readings-table td {
        padding: 5px 8px;
        border-bottom: 1px solid var(--border);
        vertical-align: middle;
    }

    .readings-table tr:last-child td {
        border-bottom: none;
    }

    .readings-table tr:hover td {
        background-color: var(--accent-bg);
    }

    .reading-date {
        font-family: var(--mono);
        font-size: 0.85rem;
        white-space: nowrap;
    }

    .reading-value {
        font-weight: 500;
        color: var(--text-h);
    }

    .quality-good    { color: #3a7d44; }
    .quality-suspect { color: #b07d00; }
    .quality-bad     { color: #b03030; }

    .empty-readings {
        font-style: italic;
        color: var(--text);
        font-size: 0.9rem;
        padding: 8px 0;
    }

    .show-all-btn {
        width: auto;
        margin-top: 6px;
        padding: 0.15rem 0.75rem;
        font-size: 12px;
        background-color: var(--view-btn-color);
        color: var(--btn-icon-color);
    }
</style>
