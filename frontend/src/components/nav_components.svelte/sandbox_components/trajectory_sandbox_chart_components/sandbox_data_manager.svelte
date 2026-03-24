<script>
    import { appState } from '../../../../lib/stores.svelte';

    let selected_subject_data = $state(null)
    let selected_subject_data2 = $state(null)
</script>

<main>
    <button type="button" onclick={() => selected_subject_data=appState.measurementsBySubject[appState.sandboxSubjectId]}>Go!</button>

    <div id="selected_datapoints">
        <p>Here ye shall find selected datapoints</p>
    </div>

    <div id="datapoint_selector">
        <p>Here ye shall select desired datapoints:</p>
        <!-- <p>{JSON.stringify(selected_subject_data)}</p> --> 
            {#if selected_subject_data}
            
                <table>
                    <thead>
                        <tr>
                        <th>Marker ID</th>
                        <th>Value</th>
                        <th>Quality</th>
                        </tr>
                    </thead>
                    <tbody>
                    {#each selected_subject_data as s}
                    <tr>
                        <td>{s.marker_id}</td>
                        <td>{s.value}</td>
                        <td>{s.quality}</td>
                    </tr>
                    {/each}
                    </tbody>
                </table>
            {:else}
                <p id="ca_nexist_pas">Ca n'existe pas</p>
            {/if}

        <!-- {#each appState.measurementsBySubject[appState.sandboxSubjectId] as m}
            <p>yo</p>
        {/each} -->
    </div> 
</main>

<style>
#selected_datapoints{
    border: 1px solid black;
    margin: 4px;
}

#datapoint_selector{
    border: 1px solid black;
    margin: 4px;
}

#ca_nexist_pas {
    color: red;
}
</style>