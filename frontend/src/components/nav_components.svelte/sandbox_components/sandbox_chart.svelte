<script>
    import * as d3 from 'd3';
    import { onMount } from 'svelte';

    let svg;

    const data = [
        { x: 0,  y: 30 },
        { x: 1,  y: 50 },
        { x: 2,  y: 20 },
        { x: 3,  y: 80 },
        { x: 4,  y: 60 },
        { x: 5,  y: 90 },
        { x: 6,  y: 45 },
    ];

    const width  = 600;
    const height = 300;
    const margin = { top: 20, right: 20, bottom: 30, left: 40 };

    onMount(() => {
        const innerWidth  = width  - margin.left - margin.right;
        const innerHeight = height - margin.top  - margin.bottom;

        const chart = d3.select(svg)
            .attr('width',  width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Scales
        const xScale = d3.scaleLinear()
            .domain(d3.extent(data, d => d.x))
            .range([0, innerWidth]);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.y)])
            .range([innerHeight, 0]);

        // Axes
        chart.append('g')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(d3.axisBottom(xScale));

        chart.append('g')
            .call(d3.axisLeft(yScale));

        // Line
        const line = d3.line()
            .x(d => xScale(d.x))
            .y(d => yScale(d.y));

        chart.append('path')
            .datum(data)
            .attr('fill', 'none')
            .attr('stroke', 'steelblue')
            .attr('stroke-width', 2)
            .attr('d', line);
    });
</script>

<svg bind:this={svg}></svg>

<style>
    svg {
        display: block;
    }
</style>
