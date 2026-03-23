<script>
    let { yScale, innerWidth } = $props();
    import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from '../../../../lib/stores.svelte';

    let yticks = [45, 50, 55, 60, 65, 70, 75, 80, 85]
</script>

<g>
    {#each yticks as tick}
        <line x1="0" x2={innerWidth} y1={yScale(tick)} y2={yScale(tick)} stroke="#cecece"/>
        <text x="0" y={yScale(tick)} >{tick}</text>
    {/each}
</g>