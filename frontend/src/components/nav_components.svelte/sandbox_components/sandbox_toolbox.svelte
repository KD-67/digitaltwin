<script>
let { onParamsSubmit } = $props();
let healthy_min = $state(null);
let healthy_max = $state(null);
</script>

<main>
    <form id="chart-meta-container" onsubmit={(e) => { e.preventDefault(); onParamsSubmit({ healthy_min: Number(healthy_min), healthy_max: Number(healthy_max) }); }}>
        <div id="chart-meta">
            <p>Healthy Min:</p>
            <input type="number" bind:value={healthy_min}>

            <p>Healthy Max:</p>
            <input type="number" bind:value={healthy_max}>

            <button type="submit">Submit</button>
        </div>
    </form>
</main>
