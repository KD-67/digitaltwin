<script>
    import * as d3 from 'd3';
    import { scaleLinear, scaleTime } from 'd3-scale';
    import { appState, ensureSubjectsLoaded, ensureMeasurementsLoaded } from '../../../../lib/stores.svelte';
    import Xaxis from './xaxis.svelte';
    import Yaxis from './yaxis.svelte';

    let width = 800;
    let height = 400;
    const margin = {top: 20, bottom: 20, left: 10, right:30};
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height -margin.top - margin.bottom;

    const xScale = scaleLinear()
        .domain([0, 15])
        .range([0, innerWidth]);

    let measurements = $derived(                                                                                                                                       
        [...(appState.measurementsBySubject[appState.sandboxSubjectId] ?? [])]
            .sort((a, b) => new Date(a.measured_at) - new Date(b.measured_at))
    );

    let xScaleTime = $derived(
        scaleTime()
            .domain([new Date(measurements[0]?.measured_at), new Date(measurements.at(-1)?.measured_at)])
            .range([0, innerWidth])
    );

    const yScale = scaleLinear()
        .domain([45, 85])
        .range([innerHeight, 0]);


</script>
<svg {width} {height}>
<g transform="translate({margin.left} {margin.top})">

    <Xaxis {xScale} {innerHeight}/>
    <Yaxis {yScale} {innerWidth}/>

    {#each measurements as m}
      <circle cx={xScaleTime(new Date(m.measured_at))} cy={yScale(m.value)} r="5" fill="black"/>
    {/each}


</g> 
</svg>

<style>
    svg {
        border: 1px solid black;
    }
</style>