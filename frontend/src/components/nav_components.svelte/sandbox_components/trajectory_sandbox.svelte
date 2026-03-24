<script>
    import TrajectorySandboxChart from "./trajectory_sandbox_chart_components/sandbox_chart.svelte";
    import SandboxToolbox from "./sandbox_toolbox.svelte";
    import SandboxDataManager from "./sandbox_data_manager.svelte";
    import DataVisTable from "./data_vis_table.svelte";

    let selectedMeasurements = $state([]);
</script>

<main>
    <h2>Trajectory Sandbox</h2>

    <div class="main-container">
        <div class="subcontainer" id="toolbox-container"> Toolbox
            <div id="toolbox">
                <SandboxToolbox />
            </div>
        </div>
        <div class="subcontainer" id="data-vis-chart-container">
            <div class="data-vis-chart-title-container">Data Vis Chart</div>
            <div id="data-vis-chart">
                <TrajectorySandboxChart measurements={selectedMeasurements} />
            </div>
        </div>
        <div class="subcontainer" id="data-manager-container"> Data Manager
            <div id="data-manager">
                <SandboxDataManager onSelectionChange={(m) => selectedMeasurements = m} />
            </div>
        </div>
        <div class="subcontainer" id="data-vis-table-container"> Data Table
            <div id="data-vis-table">
                <DataVisTable measurements={selectedMeasurements} />
            </div>
        </div>
    </div>
</main>

<style>
* {
    margin: 0;
    padding: 0;
}

.main-container {
    display: grid;
    grid-template-rows: 9fr 1fr;
    grid-template-columns: 1fr 5fr 1fr;
    padding: 8px;
    margin-top: 16px;
    height: calc(80vh - 80px);
}

.subcontainer {
    border: 1px solid black;
}

#toolbox-container {
    grid-area: 1 / 1 / 2 / 2;
}

#data-vis-chart-container {
    grid-area: 1 / 2 / 2 / 3;
    display: flex;
    flex-direction: column;
    align-items: center;
}

#data-manager-container {
    grid-area: 1 / 3 / 2 / 4;
    overflow: hidden;
}

#data-manager {
border: 1px solid black;
margin: 4px;
}

#data-vis-table-container {
    grid-area: 2 / 1 / 3 / 4;
}

</style>
