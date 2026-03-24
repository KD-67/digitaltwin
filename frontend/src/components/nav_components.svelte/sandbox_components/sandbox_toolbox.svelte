<script>
let isitsubmitted = $state(false)
</script>

<main> 
    <form id="chart-options-form" onsubmit={() => isitsubmitted = true}>
        <label for="chart-type-selector">Type: </label>
        <select name="chart-type-selector" id="chart-type-selector">
            <option value="">--</option>
            <option value="derivative">Derivative</option>
        </select>
    </form> 
    
    <form>
        <div id="chart-meta-container">
        <div id="chart-meta">
            <p>Healthy Min:</p>
            <input type="number">

            <p>Healthy Min:</p>
            <input type="number">

            <p>Vulnerability Margin:</p>
            <input type="number">

            <p>Polynomical Degree:</p>
            <input type="number">

            <button type="submit">Submit</button>
        </div>
    </div>
    </form>
</main>
