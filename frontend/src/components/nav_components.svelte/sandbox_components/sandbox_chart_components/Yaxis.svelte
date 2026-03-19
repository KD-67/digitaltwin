<script>
    let { yScale, innerWidth } = $props();

    let yticks = [0, 2, 4, 6, 8, 10];
</script>

<g>
    {#each yticks as tick}
    <text x="0" y={yScale(tick)} dx="-8" dy="-2">{tick}</text>
    <line x1="0" y1={yScale(tick)} x2={innerWidth} y2={yScale(tick)} stroke="#cecece"/>
    {/each}
</g>