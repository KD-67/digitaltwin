<script>
    let { data, xScale, yScale } = $props();
</script>

<main>
    <div class="tooltip" style="position: absolute; top: {yScale(data.y)}px; left: {xScale(data.x)}px">{data.title}</div>
</main>

<style>
    .tooltip {
        padding: 4px;
        background-color: white;
        border: 1px solid black;
    }
</style>