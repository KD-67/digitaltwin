<script>
    import * as d3 from 'd3';
    import { scaleLinear } from 'd3-scale';

    let width = 800;
    let height = 400;
</script>

<svg {width} {height}>
<g transform="translate(5 5)">
    <rect x="0" y="0" height={height - 10} width={width - 10} fill="red" />
    <circle cx="400" cy="200" r="25" fill="black"/>
</g> 
</svg>

<style>
    svg {
        border: 1px solid black;
    }
</style>