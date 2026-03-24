<script>
    let { xScale, innerHeight } = $props();

    let ticks = $derived(xScale.ticks ? xScale.ticks(6) : []);

    function formatDate(d) {
        return d instanceof Date
            ? d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: '2-digit' })
            : d;
    }
</script>

<g>
    {#each ticks as tick}
        <g transform="translate({xScale(tick)}, {innerHeight})">
            <line y2="6" stroke="black" />
            <text
                y="8"
                dominant-baseline="hanging"
                text-anchor="middle"
                font-size="10"
                transform="rotate(-30)"
            >{formatDate(tick)}</text>
        </g>
    {/each}
</g>
