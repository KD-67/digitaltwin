<script>
    let { yScale, innerWidth } = $props();
    import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from '../../../../lib/stores.svelte';

    let yticks = [-1, 1]
</script>

<g>
    {#each yticks as tick}
        <text x="0" y={yScale(tick)} >{tick}</text>
    {/each}
</g>