<script>
    let {xScale, innerHeight} = $props();

    let xticks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
</script>

<g>
    {#each xticks as tick}
    <text x={xScale(tick)} y={innerHeight} text-anchor="middle" dominant-baseline="hanging" dy="2">{tick}</text>
    {/each}
</g>