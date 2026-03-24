<script>
    import { appState, ensureMarkersLoaded } from '../../../lib/stores.svelte';
    import { onMount } from 'svelte';

    let { measurements } = $props();

    onMount(() => ensureMarkersLoaded());

    const markerNameById = $derived(
        Object.fromEntries(appState.markers.map(mk => [mk.marker_id, mk.marker_name]))
    );
</script>

<main>
    <table>
        <thead>
            <tr>
                <th>Marker</th>
                <th>Value</th>
                <th>When</th>
                <th>Normalized value</th>
            </tr>
        </thead>
        <tbody>
            {#each measurements as m}
            <tr>
                <td>{markerNameById[m.marker_id] ?? m.marker_id}</td>
                <td>{m.value}</td>
                <td>{m.measured_at}</td>
            </tr>
            {/each}
        </tbody>
    </table>
</main>
