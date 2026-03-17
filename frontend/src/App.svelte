<script>
  import { onMount } from 'svelte';
  let currentPage = window.location.hash.slice(1) || "home";

  // Svelte components:
  import Home from './components/home.svelte';
  import Computation from './components/computation.svelte';
  import Acquisition from './components/acquisition.svelte';
  import Management from './components/management.svelte';
  import Analysis from './components/analysis.svelte';
  import Prediction from './components/prediction.svelte';
  import Interpretation from './components/interpretation.svelte';
  import Sandbox from './components/sandbox.svelte';
  import Architecture from './components/architecture.svelte';
  import Help from './components/help.svelte';
  import Subjects from './components/subjects.svelte';
  import Data from './components/data.svelte';

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

    <div id="titleandlogo-container">
      <img id="logo" src="{LogoIcon}" alt="logo">
      <div id="title-container">
        <p id="title">Human Digital Twin</p>
      </div>
    </div>

    <nav>
      <a class="nav-link" href="#home">Home</a>

      <div class="dropdown">
        <a class="nav-link" id="nav-comp-dropdown" href="#computation">Computation</a>
        <div id="dropdown-menu">
          <a class="dropdown-content" href="#acquisition">Aquisition</a>
          <a class="dropdown-content" href="#management">Management</a>
          <a class="dropdown-content" href="#analysis">Analysis</a>
          <a class="dropdown-content" href="#prediction">Prediction</a>
          <a class="dropdown-content" href="#interpretation">Interpretation</a>
        </div>
      </div>

      <a class="nav-link" href="#sandbox">Sandbox</a>
      <a class="nav-link" href="#architecture">Architecture</a>
      <a class="nav-link" href="#help">Help</a>
    </nav>
  </header>

  <h1>Welcome</h1>
  <p>loading...</p>

  {#if currentPage == "home"}
  <Home />
  {:else if currentPage == "computation"}
  <Computation />
  {:else if currentPage == "acquisition"}
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
  {:else if currentPage == "data"}
  <Data />
  {:else if currentPage == "subjects"}
  <Subjects />
  {/if}
</main>

<style>
  * {
    margin: 0;
    padding: 0;
  }

  main {
    font-family: sans-serif;
    text-align: center;
    padding: 1.5rem;
  }



  #titleandlogo-container {
    display: flex;
  }

  #logo {
    height: 100px;
  }

  #title-container {
    display: flex;
    align-items: center;
  }

  nav {
    display: flex;
    justify-content: space-around;
    align-items: center;
    gap: 8px;
  }

  .nav-link {
    border: 1px solid black;
    background-color: transparent;
    color: black;
    border: none;
    padding: 10px 15px;
    cursor: pointer;
    display: inline-block;
  }

  .nav-link:hover {
    color: blue;
    transform: scale(110%);
  }

  .dropdown {
    position: relative;
  }

  #dropdown-menu {
    position: absolute;
    text-align: left;
    top: calc(100% + .25rem);
    left: 0;
    background-color: white;
    box-shadow: 0 2px 5px rgb(0, 0, 0, 0.1);
    min-width: 100%;
    opacity: 0;
    visibility: hidden;
    transform: translateY(-6px);
    transition: opacity 0.2s ease, transform 0.2s ease, visibility 0.2s;
  }

  .dropdown:hover #dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
  }

  .dropdown-content {
    display: block;
    padding: 8px 15px;
    color: black;
    white-space: nowrap;
  }

  .dropdown-content:hover {
    background-color: #f0f0f0;
  }

</style>
