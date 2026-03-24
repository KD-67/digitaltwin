<script>
    import TrajectorySandboxChart from "./trajectory_sandbox_chart_components/sandbox_chart.svelte";
    import SandboxToolbox from "./sandbox_toolbox.svelte";
    import SandboxDataManager from "./trajectory_sandbox_chart_components/sandbox_data_manager.svelte";

</script>

<main>
    <h2>Trajectory Sandbox</h2>

    <div class="main-container">
        <div class="subcontainer" id="toolbox-container"> toolbox-container
            <div id="toolbox">
                <SandboxToolbox />
            </div>
        </div>
        <div class="subcontainer" id="data-vis-chart-container">
            <div class="data-vis-chart-title-container">Data Vis Chart</div>
            <div id="data-vis-chart">
                <TrajectorySandboxChart />
            </div>    
        </div>
        <div class="subcontainer" id="data-manager-container"> data-manager-container
            <div id="data-manager">
                <SandboxDataManager />
            </div>
        </div>
        <div class="subcontainer" id="data-vis-table-container"> data-vis-table-container 
            <div id="data-vis-table"></div>
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
    grid-template-rows: 9fr 1fr ;
    grid-template-columns: 1fr 5fr 1fr;
    padding: 8px;
    margin-top: 16px;
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
}

#data-vis-table-container {
    grid-area: 2 / 1 / 3 / 4;
}

</style>