<script>
    let { xScale, innerHeight } = $props();
    import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from '../../../../lib/stores.svelte';
</script>

<g>
    <circle cx={innerHeight} cy={innerHeight/2} r="5" fill="red" />
</g>