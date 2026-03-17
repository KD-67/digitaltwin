<script>
  import { onMount } from 'svelte';
  let currentPage = window.location.hash.slice(1) || "home";

  // Svelte components:
  import Acquisition from './components/acquisition.svelte';
  import Management from './components/management.svelte';
  import Analysis from './components/analysis.svelte';
  import Prediction from './components/prediction.svelte';
  import Interpretation from './components/interpretation.svelte';
  import Sandbox from './components/sandbox.svelte';
  import Architecture from './components/architecture.svelte';
  import Help from './components/help.svelte';

  // Assets:
  import LogoIcon from '/src/assets/logo_icon.svg';

  // Functions:
    onMount(() => {
      window.addEventListener("hashchange", () => {
        currentPage = window.location.hash.slice(1) || "home";
      });
    });
</script>

<main>
  <header>
    <div id="title_container">
    <img src="{LogoIcon}" alt="logo">
      <p id="title">Human Digital Twin</p>
    </div>
    <nav>
      <a href="#acquisition">Aquisition</a>
      <a href="#management">Management</a>
      <a href="#analysis">Analysis</a>
      <a href="#prediction">Prediction</a>
      <a href="#interpretation">Interpretation</a>
      <a href="#sandbox">Sandbox</a>
      <a href="#architecture">Architecture</a>
      <a href="#help">Help</a>
    </nav>
  </header>

  <h1>Welcome</h1>
  <p>loading...</p>

  {#if currentPage == "acquisition"}
  <Acquisition />
  {:else if currentPage == "management"}
  <Management />
  {:else if currentPage == "analysis"}
  <Analysis />
  {:else if currentPage == "prediction"}
  <Prediction />
  {:else if currentPage == "interpretation"}
  <Interpretation />
  {:else if currentPage == "sandbox"}
  <Sandbox />
  {:else if currentPage == "architecture"}
  <Architecture />
  {:else if currentPage == "help"}
  <Help />
  {/if}
</main>

<style>
  main {
    font-family: sans-serif;
    text-align: center;
    padding: 2rem;
  }

  header {
    display: flex;
    justify-content: space-between;
    border: 1px solid white;
  }

  #title_container {
    display: flex;
    border: 1px solid white;
  }

  #title {
    font-size: 800;
    border: 1px solid rgb(255, 255, 255);
  }

  nav {
    border: 1px solid white;
  }
</style>
