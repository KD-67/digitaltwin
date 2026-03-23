<script>
    let { xScale, innerHeight } = $props();
    import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from '../../../../lib/stores.svelte';

    let xticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
</script>

<g>
    <circle cx={innerHeight} cy={innerHeight/2} r="5" fill="red" />

    {#each xticks as tick}
        <text x={xScale(tick)} y={innerHeight}>{tick}</text>
    {/each}
</g>