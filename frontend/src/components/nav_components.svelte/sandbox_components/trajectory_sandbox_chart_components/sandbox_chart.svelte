<script>
    import * as d3 from 'd3';
    import { scaleLinear, scaleTime } from 'd3-scale';
    import Xaxis from './xaxis.svelte';
    import Yaxis from './yaxis.svelte';
    import Tooltip from './tooltip.svelte';

    let { measurements = [], normalizedScores = {} } = $props();

    let width = 800;
    let height = 400;
    const margin = {top: 20, bottom: 25, left: 10, right:10};
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height -margin.top - margin.bottom;

    let hoveredData = $state(null)

    const xScale = scaleLinear()
        .domain([0, 15])
        .range([0, innerWidth]);

    let sortedMeasurements = $derived(
        [...measurements].sort((a, b) => new Date(a.measured_at) - new Date(b.measured_at))
    );

    let xScaleTime = $derived(
        scaleTime()
            .domain([new Date(sortedMeasurements[0]?.measured_at), new Date(sortedMeasurements.at(-1)?.measured_at)])
            .range([0, innerWidth])
    );

    const yScale = scaleLinear()
        .domain([-1, 1])
        .range([innerHeight, 0]);

</script>

<main>
<div id="chart-container">
<svg {width} {height}>
<g transform="translate({margin.left} {margin.top})">
    <rect x="0" y="0" width={innerWidth} height={innerHeight/2} fill="#dffcd2"/>
    <rect x="0" y={innerHeight/2} width={innerWidth} height={innerHeight/2} fill="#f5cbcf"/>

    <Xaxis xScale={xScaleTime} {innerHeight}/>
    <Yaxis {yScale} {innerWidth}/>

    {#each sortedMeasurements as m}
      <!-- svelte-ignore a11y_no_static_element_interactions -->
      <circle 
      cx={xScaleTime(new Date(m.measured_at))} 
      cy={yScale(normalizedScores[m.marker_id + '::' + m.measured_at] ?? m.value)}
      r={hoveredData?.created_at ? hoveredData.created_at=== m.created_at ? "7" : "4" : "5"}
      opacity={hoveredData?.created_at ? hoveredData.created_at === m.created_at ? "1" : "0.3" : "1"}
      fill="black"
      onmouseover={() => { hoveredData = m; }}
      onfocus={() => { hoveredData = m; }}
      onmouseleave={() => hoveredData = null}      
      />
    {/each}
</g> 
</svg>

    {#if hoveredData}
        <Tooltip data={hoveredData} {xScale} {yScale} />       
    {/if}

</div>
</main>
