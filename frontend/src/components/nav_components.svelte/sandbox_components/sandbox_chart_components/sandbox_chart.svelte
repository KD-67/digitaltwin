<script>
    import * as d3 from 'd3';
    import { scaleLinear} from 'd3-scale';
    import Xaxis from './Xaxis.svelte';
    import Yaxis from './Yaxis.svelte';
    import Tooltip from './tooltip.svelte';

    let width = 800;
    let height = 400;
    const margin = {top: 20, right: 40, bottom: 20, left: 40};
    const innerWidth = width - margin.right - margin.left;
    const innerHeight = height -margin.top - margin.bottom;

    const data = [
        {title:"A", x:1, y:5},
        {title:"B", x:2, y:10},
        {title:"C", x:3, y:7},
        {title:"D", x:4, y:3},
        {title:"E", x:5, y:7},
        {title:"F", x:6, y:2},
        {title:"G", x:7, y:9},
    ];

    const xScale = scaleLinear()
        .domain([0, 7])
        .range([0, innerWidth]);

    const yScale = scaleLinear()
        .domain([0, 10])
        .range([innerHeight, 0])

    let hoveredData = $state(null);
</script>

<main>
<div id="container">
<svg {width} {height}>
<g transform="translate({margin.left} {margin.top})">
    <Xaxis {xScale} {innerHeight}/>
    <Yaxis {yScale} {innerWidth}/>
    {#each data as d}
        <circle
        cx={xScale(d.x)}
        cy={yScale(d.y)}
        r={hoveredData?.title  ? hoveredData.title=== d.title ? "12" : "7" : "8"}
        opacity={hoveredData?.title  ? hoveredData.title=== d.title ? "1" : "0.3" : "1"}
        fill="black"
        stroke="black"
        role="img"
        onmouseover={() => { hoveredData = d; }}
        onfocus={() => { hoveredData = d; }}
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

<style>
    #container {
        position: relative;
    }

    svg {
        border: 1px solid black;
        margin: 8px;
    }

    circle {
        transition: all 500ms ease;
        cursor: pointer;
    }

    circle:focus {
        outline: none;
    }
</style>